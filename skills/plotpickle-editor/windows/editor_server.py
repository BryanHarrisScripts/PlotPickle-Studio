#!/usr/bin/env python3
"""Local-only PlotPickle draft editor/FFmpeg media receiver (Python 3.11+).

A deliberately LOCAL service: it does not create ChatGPT/MCP connectivity, publicly
expose the computer or change source PPFs. No third-party Python dependencies.
"""
from __future__ import annotations
import argparse, copy, hashlib, http.server, io, json, math, os, pathlib, re, shutil, subprocess, sys, threading, time, urllib.request, webbrowser
from urllib.parse import urlsplit
import editor_core as ec
import editor_audio as ea

HERE=pathlib.Path(__file__).resolve().parent

def default_media_root():
    """Select user-writable media storage; never assume Videos is physical/not redirected."""
    override=os.environ.get('PLOTPICKLE_EDITOR_ROOT')
    if override:
        return pathlib.Path(override).expanduser()
    legacy=pathlib.Path.home()/'Videos'/'PlotPickle'/'The Third Bell'/'Editor'
    if (legacy/'editor-draft.json').is_file():
        return legacy
    local=os.environ.get('LOCALAPPDATA')
    if local:
        return pathlib.Path(local)/'PlotPickle'/'Projects'/'The Third Bell'/'Editor'
    return pathlib.Path.home()/'PlotPickle'/'Projects'/'The Third Bell'/'Editor'
MAX_UPLOAD=32*1024*1024
MAX_VIDEO=1024*1024*1024
MEDIA_ID=re.compile(r'^[a-zA-Z0-9_-]{1,64}$')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ec.EditError('CDN redirected; blocked')

def run(cmd,timeout=180):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
    if p.returncode:raise ec.EditError((p.stderr or p.stdout).decode('utf-8','replace')[-650:])
    return p.stdout.decode('utf-8','replace')

def probe(path):
    out=run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],45)
    d=json.loads(out);v=next((x for x in d.get('streams',[]) if x.get('codec_type')=='video'),None)
    if not v:raise ec.EditError('File contains no video stream')
    if v.get('width',0)>8192 or v.get('height',0)>8192:raise ec.EditError('Video dimensions beyond draft limits')
    return d,v

def framecheck(path,frames):
    d,v=probe(path)
    fraction=v.get('avg_frame_rate','0/1')
    if fraction!='24/1':raise ec.EditError(f'Output is not exactly 24 fps: {fraction}')
    count=int(run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames','-of','default=noprint_wrappers=1:nokey=1',str(path)],120).strip())
    if count!=frames:raise ec.EditError(f'Expected {frames} frames, saw {count}')
    run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],120)
    return {'width':v['width'],'height':v['height'],'fps':24,'frames':count,'durationSeconds':frames/24,'sha256':ec.sha(path),'sizeBytes':path.stat().st_size,'fullDecodeVerified':True}

def conform(src,dst,frames):
    if not isinstance(frames,int) or frames<1 or frames>24*300:raise ec.EditError('Invalid shot duration')
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(src),'-vf','fps=24', '-frames:v',str(frames),'-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','veryfast','-movflags','+faststart',str(dst)],240)
    return framecheck(dst,frames)

class Editor:
    def __init__(self,root,seed=None):
        self.root=pathlib.Path(root).expanduser().resolve()
        try:
            self.root.mkdir(parents=True,exist_ok=True)
        except OSError as ex:
            raise ec.EditError('Cannot create PlotPickle media folder %s: %s. Choose a writable path with PLOTPICKLE_EDITOR_ROOT.' % (self.root, ex)) from ex
        self.media=self.root/'media';self.media.mkdir(exist_ok=True)
        self.renders=self.root/'renders';self.renders.mkdir(exist_ok=True)
        self.history=self.root/'history';self.history.mkdir(exist_ok=True)
        self.audio=self.root/'audio';self.audio.mkdir(exist_ok=True)
        self.lock=threading.RLock();self.project_path=self.root/'editor-draft.json'
        if self.project_path.exists():
            self.p=json.loads(self.project_path.read_text(encoding='utf-8'))
            if self.p.get('schema')!='plotpickle.editor-draft.v1':raise ec.EditError('Unsupported project schema')
        else:
            initial_seed=json.loads(pathlib.Path(seed).read_text(encoding='utf-8')) if seed else None
            self.p=ec.initial(initial_seed);self._save()
        self.busy=False
        self._ensure_audio_assets()
    def _ensure_audio_assets(self):
        """Add original local demo audio to the *draft*, not the locked source PPF.
        Existing edits are left untouched: no removed cue is recreated.
        """
        changed=False
        assets=self.p.setdefault('audioAssets',{})
        for kind,ident in (('ocean','demo-ocean'),('gulls','demo-gulls')):
            target=self.audio/f'{ident}.wav'
            ea.create_demo_wav(target,kind)
            entry={'id':ident,'kind':'generated-demo','label':f'{kind.title()} (synthetic demonstration)',
                   'path':str(target.relative_to(self.root)),'sha256':ec.sha(target),
                   'sampleRate':ea.SAMPLE_RATE,'demo':True}
            if ident not in assets:
                assets[ident]=entry;changed=True
            elif assets[ident].get('sha256')!=ec.sha(target):
                raise ec.EditError('Demo audio integrity changed: '+ident)
        if self.p.get('audioDefaultsVersion') is None:
            for track,cid,aid in (('ambience','ambience-01','demo-ocean'),('foley','foley-01','demo-gulls')):
                for c in self.p['tracks'][track]:
                    if c['id']==cid and c.get('audioId') is None:
                        c['audioId']=aid;c.setdefault('muted',False)
                        if self.p['revision']==0 and c.get('gainDb',0)==0:c['gainDb']=(-7 if track=='ambience' else -10)
                        changed=True
            self.p['audioDefaultsVersion']=1;changed=True
        if changed:self._save()
    def _audio_path(self,aid):
        asset=self.p.get('audioAssets',{}).get(aid)
        if not asset:raise ec.EditError('Missing audio asset: '+str(aid))
        file=(self.root/asset['path']).resolve()
        if not file.is_relative_to(self.audio.resolve()) or file.suffix!='.wav' or not file.is_file():raise ec.EditError('Audio file not available')
        if ec.sha(file)!=asset['sha256']:raise ec.EditError('Audio file checksum mismatch')
        return file
    def attach_audio(self,track,clip_id,expected_revision,data):
        """Save caller-supplied WAV, normalize to 48 kHz PCM and attach to cue.
        Localhost only. No arbitrary filesystem path accepted from browser.
        """
        if track not in ('dialogue','foley','ambience','music'):raise ec.EditError('Invalid audio track')
        if not MEDIA_ID.fullmatch(clip_id):raise ec.EditError('Invalid clip ID')
        if not isinstance(data,bytes) or not 44<=len(data)<=MAX_UPLOAD or data[:4]!=b'RIFF' or data[8:12]!=b'WAVE':raise ec.EditError('Upload must be WAV (max 32 MB)')
        with self.lock:
            if self.busy:raise ec.EditError('Processing already active')
            if type(expected_revision)!=int or self.p['revision']!=expected_revision:raise ec.EditError('Revision conflict')
            if not any(c['id']==clip_id for c in self.p['tracks'][track]):raise ec.EditError('Clip missing')
            digest=hashlib.sha256(data).hexdigest()[:20]
            raw=self.audio/f'upload-{digest}.wav';normalized=self.audio/f'user-{digest}.wav'
            tmp=self.audio/f'user-{digest}.tmp.wav'
            if not raw.exists():raw.write_bytes(data)
            try:
                meta=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(raw)],40))
                streams=meta.get('streams',[])
                if not any(c.get('codec_type')=='audio' for c in streams) or any(c.get('codec_type')=='video' for c in streams):raise ec.EditError('WAV must contain audio only')
                duration=float(meta.get('format',{}).get('duration',0))
                if not .05<=duration<=300:raise ec.EditError('WAV duration out of range')
                if not normalized.exists():
                    run(['ffmpeg','-y','-v','error','-i',str(raw),'-vn','-ar','48000','-ac','2','-c:a','pcm_s16le',str(tmp)],90)
                    os.replace(tmp,normalized)
                aid='user-'+digest
                self.p.setdefault('audioAssets',{})[aid]={
                    'id':aid,'kind':'uploaded-wav','label':'Imported WAV audio','path':str(normalized.relative_to(self.root)),
                    'sha256':ec.sha(normalized),'sampleRate':48000,'demo':False,'sourceSha256':hashlib.sha256(data).hexdigest()}
                # Apply to cloned draft; preserve edit history and optimistic concurrency.
                result=self.edit({'operation':'change','expectedRevision':expected_revision,'track':track,'id':clip_id,'audioId':aid,'muted':False})
                return result
            finally:
                tmp.unlink(missing_ok=True)
    def _save(self):
        tmp=self.project_path.with_suffix('.json.tmp');tmp.write_text(json.dumps(self.p,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');os.replace(tmp,self.project_path)
    def state(self):
        """Return display-safe state with opaque, same-origin preview links.

        Filesystem paths are private server state and must never be consumed by
        browser JS. Reconcile an already verified media reference on restart
        without re-importing, re-rendering, or changing the revision counter.
        """
        with self.lock:
            state=ec.public_state(self.p)
            for mid, media in self.p['media'].items():
                if media.get('status') != 'verified-draft':
                    continue
                # Only the receiver's exact media filename is a previewable file.
                rel=media.get('path')
                allowed_name=f'{mid}-24fps.mp4'
                displayed=state['media'][mid]
                displayed['previewAvailable']=False
                if not isinstance(rel,str) or not MEDIA_ID.fullmatch(mid):
                    continue
                target=(self.root/rel).resolve()
                if (target.name == allowed_name and target.is_relative_to(self.media.resolve())
                        and target.is_file()):
                    displayed['previewUrl']='/media/'+allowed_name
                    displayed['previewAvailable']=True
            resultPath=self.p.get('job',{}).get('resultPath')
            if self.p.get('job',{}).get('state')=='render-complete' and isinstance(resultPath,str):
                candidate=(self.root/resultPath).resolve()
                if candidate.is_relative_to(self.renders.resolve()) and candidate.is_file() and re.fullmatch(r'draft-revision-\d{4}\.mp4',candidate.name):
                    state['job']['previewUrl']='/render/'+candidate.name
                    state['job']['previewAvailable']=True
            return state
    def edit(self,event):
        with self.lock:
            if self.busy:raise ec.EditError('Editing paused while a media job is running')
            before=copy.deepcopy(self.p);after=ec.apply_edit(before,event)
            (self.history/f'{before["revision"]:08d}.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
            self.p=after;self._save();return self.state()
    def undo(self,revision):
        with self.lock:
            if self.busy:raise ec.EditError('Undo paused while media job is running')
            if type(revision)!=int or revision!=self.p['revision']:raise ec.EditError('Revision conflict')
            prior=self.history/f'{revision-1:08d}.json'
            if not prior.exists():raise ec.EditError('No earlier edit to undo')
            before=copy.deepcopy(self.p);recovered=json.loads(prior.read_text(encoding='utf-8'))
            (self.history/f'{revision:08d}.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
            recovered['revision']=revision+1;recovered['job']={'state':'draft-edited'}
            self.p=recovered;self._save();return self.state()
    def transfer(self,media_id):
        if not MEDIA_ID.fullmatch(media_id):raise ec.EditError('Unsafe media ID')
        with self.lock:
            if self.busy:raise ec.EditError('Processing is already in progress')
            m=self.p['media'].get(media_id)
            if not m or m['status'] not in ('pending-transfer','failed'):
                raise ec.EditError('No pending source media to transfer')
            self.busy=True;self.p['job']={'state':'transferring','mediaId':media_id};self._save()
        threading.Thread(target=self._do_transfer,args=(media_id,),daemon=True).start()
        return {'state':'transferring','mediaId':media_id}
    def _do_transfer(self,media_id):
        orig=self.media/f'{media_id}-original.mp4';temp=self.media/f'{media_id}-download.tmp'
        dst=self.media/f'{media_id}-24fps.mp4';tmpdst=self.media/f'{media_id}-24fps.tmp.mp4'
        try:
            with self.lock:
                m=self.p['media'][media_id];url=ec.fal_media_url(m['originUrl'],resolve=True)
                clips=[c for c in self.p['tracks']['video'] if c.get('mediaId')==media_id]
                if not clips: raise ec.EditError('Media not referenced by the draft timeline')
                frames=clips[0]['durationFrames']
                if frames>24*300:raise ec.EditError('Media clip too long')
            opener=urllib.request.build_opener(NoRedirect(),urllib.request.ProxyHandler({}))
            request=urllib.request.Request(url,headers={'User-Agent':'PlotPickleLocalReceiver/0.1','Accept':'video/mp4'})
            with opener.open(request,timeout=30) as reply, temp.open('wb') as out:
                if reply.status!=200:raise ec.EditError(f'Download returned {reply.status}')
                n=0
                while True:
                    block=reply.read(1024*1024)
                    if not block:break
                    n+=len(block)
                    if n>MAX_VIDEO:raise ec.EditError('Video file exceeds configured size limit')
                    out.write(block)
            if temp.stat().st_size<256:raise ec.EditError('Incomplete MP4')
            source_md,source_video=probe(temp)
            run(['ffmpeg','-v','error','-xerror','-i',str(temp),'-f','null','-'],120)
            with self.lock:self.p['job']={'state':'conforming','mediaId':media_id};self._save()
            detail=conform(temp,tmpdst,frames)
            if orig.exists() or dst.exists():raise ec.EditError('Existing media would be overwritten')
            os.replace(temp,orig);os.replace(tmpdst,dst)
            with self.lock:
                self.p['media'][media_id].update({'status':'verified-draft','path':str(dst.relative_to(self.root)),'originalPath':str(orig.relative_to(self.root)), 'sha256':detail['sha256'], 'fps':24, 'frames':frames, 'verification':detail, 'sourceProbe':{'width':source_video['width'],'height':source_video['height'],'avgFrameRate':source_video.get('avg_frame_rate')}, 'sourceSha256':ec.sha(orig)})
                self.p['job']={'state':'complete','mediaId':media_id,'verified':True};self._save()
        except Exception as ex:
            with self.lock:
                self.p['media'][media_id]['status']='failed';self.p['job']={'state':'failed','mediaId':media_id,'error':str(ex)[:1000]};self._save()
        finally:
            for path in (temp,tmpdst):
                try:path.unlink(missing_ok=True)
                except OSError:pass
            with self.lock:self.busy=False
    def render(self,expected_revision):
        with self.lock:
            if self.busy:raise ec.EditError('Processing already active')
            if type(expected_revision)!=int or expected_revision!=self.p['revision']:raise ec.EditError('Revision conflict')
            movie=list(self.p['tracks']['video'])
            if len(movie)!=1 or movie[0]['startFrame']!=0:raise ec.EditError('MVP renders one continuous video clip starting at frame zero')
            clip=movie[0];frames=clip['durationFrames'];m=self.p['media'].get(clip.get('mediaId'))
            if not m or m['status']!='verified-draft':raise ec.EditError('Transfer and verify video first')
            source=(self.root/m['path']).resolve()
            if not source.is_relative_to(self.media.resolve()) or not source.is_file():raise ec.EditError('Missing verified media')
            if ec.sha(source)!=m['sha256']:raise ec.EditError('Media checksum changed')
            cues=[];skipped=[]
            for track in ('dialogue','foley','ambience','music'):
                for cue in self.p['tracks'][track]:
                    if cue.get('muted') or cue['startFrame']>=frames:continue
                    if not cue.get('audioId'):
                        skipped.append(cue['id']);continue
                    path=self._audio_path(cue['audioId'])
                    end=min(cue['durationFrames'],frames-cue['startFrame'])
                    cues.append({'track':track,'id':cue['id'],'file':str(path),'startFrame':cue['startFrame'],
                        'durationFrames':end,'gainDb':cue.get('gainDb',0)})
            if len(cues)>24:raise ec.EditError('Maximum 24 simultaneous audio cues in MVP')
            target=self.renders/f'draft-revision-{expected_revision:04d}.mp4'
            if target.exists():raise ec.EditError('Draft export exists; no overwrite')
            self.busy=True;self.p['job']={'state':'rendering','revision':expected_revision};self._save()
        threading.Thread(target=self._do_render,args=(source,target,frames,expected_revision,cues,skipped),daemon=True).start()
        return {'state':'rendering','revision':expected_revision}
    def _do_render(self,source,target,frames,revision,cues,skipped):
        temp=target.with_suffix('.tmp.mp4')
        try:
            cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(source)]
            for cue in cues:cmd+=['-i',cue['file']]
            for i,cue in enumerate(cues,start=1):cue['input_index']=i
            if cues:
                spec=ea.audio_filter_spec(cues,frames)
                cmd+=['-filter_complex',spec,'-map','0:v:0','-map','[mix]']
            else:
                cmd+=['-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=48000','-map','0:v:0','-map',f'{len(cues)+1}:a:0']
            cmd+=['-frames:v',str(frames),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
                '-c:a','aac','-b:a','192k','-ar','48000','-t',str(frames/24),'-movflags','+faststart',str(temp)]
            run(cmd,240)
            detail=framecheck(temp,frames)
            streams,_=probe(temp)
            audio=next((x for x in streams.get('streams',[]) if x.get('codec_type')=='audio'),None)
            if not audio or audio.get('sample_rate')!='48000':raise ec.EditError('Output missing 48 kHz audio')
            detail['audio']={'sampleRate':48000,'channels':audio.get('channels'),'mixedCueCount':len(cues),
                             'mixedCueIds':[c['id'] for c in cues],'unboundCueIds':skipped,'demoAudio':any(c['id'] in ('ambience-01','foley-01') for c in cues)}
            os.replace(temp,target)
            with self.lock:
                self.p['job']={'state':'render-complete','revision':revision,'verified':True,
                    'resultPath':str(target.relative_to(self.root)),'verification':detail,
                    'audioNote':f'{len(cues)} cue(s) mixed at 48 kHz; {len(skipped)} unbound cue(s) omitted. Sample sounds are synthetic demos.'};self._save()
        except Exception as ex:
            with self.lock:self.p['job']={'state':'failed','revision':revision,'error':str(ex)[:1000]};self._save()
        finally:
            temp.unlink(missing_ok=True)
            with self.lock:self.busy=False

class Handler(http.server.BaseHTTPRequestHandler):
    server_version='PlotPickleLocalEditor/0.1'
    def log_message(self,fmt,*args):return
    @property
    def ed(self):return self.server.editor
    def _security(self,write=False):
        if self.headers.get('Host') not in ('127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port)):
            raise ec.EditError('Invalid host')
        if self.client_address[0] not in ('127.0.0.1','::1'):raise ec.EditError('Remote access forbidden')
        if write:
            origin=self.headers.get('Origin')
            if origin not in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port)):
                raise ec.EditError('Invalid origin')
            if self.headers.get('X-PlotPickle-Local')!='editor-v1':raise ec.EditError('Missing local action header')
    def send(self,code,body,ctype='application/json'):
        data=json.dumps(body,ensure_ascii=False).encode('utf-8') if isinstance(body,(dict,list)) else body
        self.send_response(code);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
    def do_GET(self):
        try:
            self._security();path=urlsplit(self.path).path
            if path=='/api/project':return self.send(200,self.ed.state())
            if path=='/api/health':return self.send(200,{'status':'local-only','fps':24,'ffmpeg':shutil.which('ffmpeg') is not None,'mediaRoot':str(self.ed.root),'chatgptBridge':'not-connected'})
            if path in ('/','/app.js','/style.css'):
                f=HERE/({'/':'index.html'}.get(path,path.lstrip('/')))
                return self.send(200,f.read_bytes(),{'/':'text/html; charset=utf-8','/app.js':'application/javascript; charset=utf-8','/style.css':'text/css; charset=utf-8'}[path])
            if path.startswith('/media/') or path.startswith('/render/'):
                relative=path.rsplit('/',1)[-1]
                if not MEDIA_ID.fullmatch(relative.replace('.mp4','')) and not re.fullmatch(r'draft-revision-\d{4}\.mp4',relative):raise ec.EditError('Unknown file')
                with self.ed.lock:
                    p=self.ed.p
                    candidates=[m.get('path') for m in p['media'].values() if m.get('status')=='verified-draft']+[p.get('job',{}).get('resultPath')]
                matches=[self.ed.root/x for x in candidates if x and pathlib.Path(x).name==relative]
                if len(matches)!=1:raise ec.EditError('No verified media by this name')
                f=matches[0].resolve();allowed=(self.ed.media.resolve(),self.ed.renders.resolve())
                if not any(f.is_relative_to(root) for root in allowed):raise ec.EditError('Out-of-root media')
                content=f.read_bytes() # MVP bounded files only
                if len(content)>MAX_VIDEO:raise ec.EditError('File too large')
                return self.send(200,content,'video/mp4')
            return self.send(404,{'error':'Not found'})
        except Exception as ex:return self.send(400,{'error':str(ex)})
    def do_POST(self):
        try:
            self._security(write=True)
            n=int(self.headers.get('Content-Length','0'))
            path=urlsplit(self.path).path
            if path=='/api/audio-upload':
                if not 0<n<=MAX_UPLOAD:raise ec.EditError('Audio upload too large or empty')
                track=self.headers.get('X-PlotPickle-Track','')
                clip_id=self.headers.get('X-PlotPickle-Clip','')
                try:revision=int(self.headers.get('X-PlotPickle-Revision',''))
                except (ValueError,TypeError):raise ec.EditError('Missing expected revision')
                return self.send(200,self.ed.attach_audio(track,clip_id,revision,self.rfile.read(n)))
            if not 0<n<128*1024:raise ec.EditError('Body must be a small JSON document')
            data=json.loads(self.rfile.read(n));path=urlsplit(self.path).path
            if path=='/api/edit':result=self.ed.edit(data)
            elif path=='/api/undo':result=self.ed.undo(data.get('expectedRevision'))
            elif path=='/api/transfer':result=self.ed.transfer(data.get('mediaId',''))
            elif path=='/api/render':result=self.ed.render(data.get('expectedRevision'))
            else:return self.send(404,{'error':'Unknown operation'})
            return self.send(200,result)
        except Exception as ex:return self.send(400,{'error':str(ex)})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(default_media_root()));ap.add_argument('--seed');ap.add_argument('--port',type=int,default=8765);ap.add_argument('--no-browser',action='store_true');args=ap.parse_args()
    if sys.version_info < (3,11):ap.error('Python 3.11 or newer is required. You are using %s. Use the updated Windows launcher.' % sys.version.split()[0])
    if not 1025<=args.port<=65535:ap.error('Port out of range')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):ap.error('FFmpeg and ffprobe are required on PATH')
    app=Editor(args.root,args.seed)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler);server.editor=app
    url=f'http://127.0.0.1:{args.port}'
    print('PlotPickle local-only draft editor:',url,'\nMedia root:',app.root,'\nPress Ctrl+C to stop. No inbound internet access.',flush=True)
    if not args.no_browser:threading.Timer(.75,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
