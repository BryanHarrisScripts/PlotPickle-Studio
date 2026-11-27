#!/usr/bin/env python3
"""PlotPickle Studio portable, fail-closed 24fps six-lane editorial sidecar.
No provider calls or native .ppf.json writes. Python 3.11+ and FFmpeg/ffprobe for renders.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

TRACKS = ('video', 'dialogue', 'action', 'foley', 'ambience', 'music')
AUDIO_TRACKS = ('dialogue', 'foley', 'ambience', 'music')
FPS = 24


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def run(cmd):
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if result.returncode:raise RuntimeError(f'{cmd[0]} failed: {result.stderr[-1300:]}')
    return result.stdout


def probe(path):
    j=json.loads(run(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_type,width,height,avg_frame_rate,nb_read_frames,sample_rate:format=duration,size','-of','json',str(path)]))
    vids=[s for s in j.get('streams',[]) if s.get('codec_type')=='video']
    if len(vids)!=1:raise ValueError('Exactly one video stream required')
    s=vids[0]
    frac=s.get('avg_frame_rate','0/1').split('/')
    fps=float(frac[0])/float(frac[1]) if len(frac)==2 and float(frac[1]) else float(frac[0])
    return {'frames':int(s.get('nb_read_frames') or 0),'fps':fps,'width':s.get('width'),'height':s.get('height'),'duration':float(j.get('format',{}).get('duration',0)),'size':int(j.get('format',{}).get('size',0))}


def decode(path):
    run(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:v:0','-f','null','-'])


def write_new(path, data):
    path=Path(path)
    if path.exists():raise FileExistsError(str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    t=path.with_name(path.name+'.partial')
    if t.exists():raise FileExistsError(str(t))
    try:
        with open(t,'x',encoding='utf8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(t,path)
    finally:
        t.unlink(missing_ok=True)


def atomic_replace(path,data):
    path=Path(path)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.plotpickle-timeline-',suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf8') as f:
            json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def load(path):
    d=json.loads(Path(path).read_text(encoding='utf8'))
    if d.get('schema')!='plotpickle.timeline.v1' or d.get('fps')!=24 or sorted(d.get('tracks',{}))!=sorted(TRACKS):raise ValueError('Invalid timeline schema/fps/tracks')
    if not isinstance(d.get('revision'),int):raise ValueError('Missing timeline revision')
    return d


def media_path(root, rel):
    if not isinstance(rel,str) or not rel or '\\' in rel:raise ValueError('Unsafe media path')
    p=Path(rel)
    if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe relative media path')
    r=Path(root).resolve()
    full=(r/p).resolve()
    if not full.is_relative_to(r) or not full.is_file():raise FileNotFoundError(f'Media unavailable: {rel}')
    return full


def ensure_source(d, ppf):
    if sha(ppf)!=d['ppfSha256']:raise ValueError('PPF source SHA mismatch; do not edit stale timeline')


def conform(source,output,frames,width,height):
    source=Path(source);out=Path(output)
    if out.exists():raise FileExistsError(str(out))
    if frames<1 or frames>72000:raise ValueError('Frame count out of range')
    if source.stat().st_size<1000:raise ValueError('Media too small')
    original=probe(source)
    decode(source)
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_name(out.stem+'.partial.mp4')
    if tmp.exists():raise FileExistsError('Existing partial conformance')
    try:
        run(['ffmpeg','-v','error','-xerror','-i',str(source),'-an','-vf',f'fps=24,scale={width}:{height}:flags=lanczos,setsar=1', '-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)])
        x=probe(tmp)
        decode(tmp)
        if x['frames']!=frames or abs(x['fps']-24)>0.001 or (x['width'],x['height'])!=(width,height):raise ValueError('24fps output verification failed')
        os.replace(tmp,out)
        return {'original':{'bytes':source.stat().st_size,'sha256':sha(source),**original},'conformed':{'bytes':out.stat().st_size,'sha256':sha(out),**x}}
    finally:tmp.unlink(missing_ok=True)


def validate(d, root, ppf=None, only_range=None):
    if ppf:ensure_source(d,ppf)
    width,height=d['width'],d['height']
    v=sorted([c for c in d['tracks']['video'] if c.get('enabled',True)],key=lambda x:x['startFrame'])
    if not v:raise ValueError('No enabled video clips')
    cursor=0; receipts=[]
    for c in v:
        start=c.get('startFrame');length=c.get('durationFrames');kind=c.get('kind','video')
        if not isinstance(start,int) or not isinstance(length,int) or length<1 or start!=cursor:raise ValueError('Enabled video must be positive, contiguous and non-overlapping')
        cursor+=length
        if only_range and start>=only_range:break
        if kind not in ('video','image'):raise ValueError('Unsupported picture kind')
        if not c.get('path') or not c.get('sha256'):raise ValueError('Missing picture path or hash')
        path=media_path(root,c['path'])
        h=sha(path)
        if h!=c['sha256']:raise ValueError('Media hash mismatch: '+str(c['path']))
        if kind=='video':
            x=probe(path);decode(path)
            if x['fps']!=24 or x['frames']<length+c.get('sourceInFrame',0) or (x['width'],x['height'])!=(width,height):raise ValueError('Video requires verified 24fps frames and target resolution')
        receipts.append({'id':c['id'],'kind':kind,'path':c['path'],'sha256':h,'startFrame':start,'durationFrames':length})
    if cursor!=d['totalFrames']:raise ValueError('Declared totalFrames mismatches clips')
    for lane in AUDIO_TRACKS:
        for cue in d['tracks'][lane]:
            if cue.get('muted') or not cue.get('path'):continue
            if not isinstance(cue.get('startFrame'),int) or cue['startFrame']<0 or not isinstance(cue.get('durationFrames'),int) or cue['durationFrames']<1 or cue['startFrame']+cue['durationFrames']>cursor:raise ValueError('Audio cue outside duration')
            src=media_path(root,cue['path'])
            if sha(src)!=cue.get('sha256'):raise ValueError('Audio hash mismatch')
            if src.suffix.lower()!='.wav':raise ValueError('Bound sound must be WAV')
    return {'schema':'plotpickle.timeline-validation.v1','revision':d['revision'],'ppfSha256':d['ppfSha256'],'verifiedClips':receipts,'totalFrames':cursor,'fps':24,'status':'source-and-media-verified'}


def apply_edit(d,op,lane,clip_id,expected,**kw):
    if d['revision']!=expected:raise ValueError('Stale revision; re-open timeline')
    before={k:copy.deepcopy(d[k]) for k in ('tracks','totalFrames')}
    if op=='undo':
        hist=d.get('history',[])
        if not hist:raise ValueError('Nothing to undo')
        snap=hist[-1]['before'];d['tracks']=snap['tracks'];d['totalFrames']=snap['totalFrames'];d['history']=hist[:-1]
    else:
        if lane not in TRACKS:raise ValueError('Unknown lane')
        clips=d['tracks'][lane]
        if op=='add-cue':
            if lane=='video':raise ValueError('Use verified source-linked picture registration for video')
            if not kw.get('id') or any(c.get('id')==kw['id'] for c in clips):raise ValueError('Duplicate/empty cue ID')
            if kw.get('startFrame',-1)<0 or kw.get('durationFrames',0)<1:raise ValueError('Bad cue timing')
            clips.append({'id':kw['id'],'label':kw.get('label','Cue'),'startFrame':kw['startFrame'],'durationFrames':kw['durationFrames'],'muted':False})
        else:
            clip=next((x for x in clips if x.get('id')==clip_id),None)
            if not clip:raise ValueError('Cue not found')
            if op in ('move','trim'):
                field='startFrame' if op=='move' else 'durationFrames'
                if not isinstance(kw.get('value'),int) or kw['value'] < (0 if op=='move' else 1):raise ValueError('Invalid frame value')
                clip[field]=kw['value']
            elif op=='mute':
                if lane in ('video','action'):raise ValueError('Cannot mute this lane')
                clip['muted']=not clip.get('muted',False)
            else:raise ValueError('Unsupported edit')
        if len(d.get('history',[]))>=100:d['history']=d['history'][-99:]
        d.setdefault('history',[]).append({'revision':d['revision'],'operation':op,'lane':lane,'clipId':clip_id,'before':before})
    d['revision']+=1;d['renderStatus']='stale'
    return d


def render(d, root, ppf, target):
    verified=validate(d,root,ppf)
    target=Path(target)
    if target.exists():raise FileExistsError(str(target))
    width,height=d['width'],d['height'];frames=d['totalFrames'];duration=frames/24
    if frames>24*60*30:raise ValueError('Render above 30m limit')
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pp-produce-') as work:
        work=Path(work);segments=[]
        for n,c in enumerate(sorted(d['tracks']['video'],key=lambda c:c['startFrame'])):
            if not c.get('enabled',True):continue
            source=media_path(root,c['path']);seg=work/f'seg-{n:04d}.mp4';kind=c.get('kind','video')
            if kind=='video':
                cmd=['ffmpeg','-v','error','-xerror','-i',str(source),'-an','-vf',f'trim=start_frame={c.get("sourceInFrame",0)}:end_frame={c.get("sourceInFrame",0)+c["durationFrames"]},setpts=PTS-STARTPTS,setsar=1','-frames:v',str(c['durationFrames'])]
            else:
                cmd=['ffmpeg','-v','error','-xerror','-loop','1','-framerate','24','-i',str(source),'-frames:v',str(c['durationFrames'])]
            cmd+=(['-r','24','-vf',f'scale={width}:{height},setsar=1'] if kind=='image' else ['-r','24'])+['-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','20',str(seg)]
            run(cmd)
            q=probe(seg);decode(seg)
            if q['frames']!=c['durationFrames'] or abs(q['fps']-24)>0.001:raise ValueError('Segment verification failed')
            segments.append(seg)
        listfile=work/'list.txt';listfile.write_text(''.join(f"file '{s.as_posix()}'\n" for s in segments))
        picture=work/'picture.mp4';run(['ffmpeg','-v','error','-xerror','-f','concat','-safe','0','-i',str(listfile),'-c','copy',str(picture)])
        if probe(picture)['frames']!=frames:raise ValueError('Concatenation frame count mismatch')
        out=target.with_name(target.stem+'.partial.mp4')
        if out.exists():raise FileExistsError('Existing partial render')
        try:
            audio=[]
            for lane in AUDIO_TRACKS:
                for c in d['tracks'][lane]:
                    if c.get('muted') or not c.get('path'):continue
                    audio.append(c)
            cmd=['ffmpeg','-v','error','-xerror','-i',str(picture)]
            for c in audio:cmd+=['-i',str(media_path(root,c['path']))]
            if audio:
                filters=[]
                for i,c in enumerate(audio,1):
                    vol=math.pow(10,max(-60,min(12,float(c.get('gainDb',0))))/20)
                    filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={c["durationFrames"]/24:.6f},asetpts=PTS-STARTPTS,volume={vol:.7f},adelay={c["startFrame"]*2000}S|{c["startFrame"]*2000}S[a{i}]')
                filters.append(''.join(f'[a{i}]' for i in range(1,len(audio)+1))+f'amix=inputs={len(audio)}:duration=longest:normalize=0,apad,atrim=duration={duration:.6f}[mix]')
                cmd+=['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[mix]']
            else:
                cmd+=['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-map','0:v:0','-map','1:a:0']
            cmd+=['-c:v','copy','-c:a','aac','-ar','48000','-t',f'{duration:.6f}','-movflags','+faststart','-shortest',str(out)]
            run(cmd)
            q=probe(out);decode(out)
            if q['frames']!=frames or abs(q['fps']-24)>0.001 or (q['width'],q['height'])!=(width,height):raise ValueError('Final frame/fps/resolution mismatch')
            os.replace(out,target)
        finally:out.unlink(missing_ok=True)
    receipt={'schema':'plotpickle.editor-render-receipt.v1','status':'verified-draft-not-approved-master','sourcePPFSha256':d['ppfSha256'],'timelineRevision':d['revision'],'tracks':list(TRACKS),'frames':frames,'fps':24,'durationSeconds':duration,'mediaSha256':sha(target),'mediaBytes':target.stat().st_size,'media':'draft rough cut / animatic','validation':verified,'nativePpfModified':False,'saveLockModified':False}
    write_new(str(target)+'.receipt.json',receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='action',required=True)
    c=sp.add_parser('conform');c.add_argument('--source',required=True);c.add_argument('--out',required=True);c.add_argument('--frames',type=int,default=72);c.add_argument('--width',type=int,default=1920);c.add_argument('--height',type=int,default=1080)
    init=sp.add_parser('init');init.add_argument('--project',required=True);init.add_argument('--project-id',required=True);init.add_argument('--title',required=True);init.add_argument('--width',type=int,default=1920);init.add_argument('--height',type=int,default=1080);init.add_argument('--out',required=True)
    check=sp.add_parser('validate');check.add_argument('--timeline',required=True);check.add_argument('--media-root',required=True);check.add_argument('--project')
    edit=sp.add_parser('edit');edit.add_argument('--timeline',required=True);edit.add_argument('--expected-revision',type=int,required=True);edit.add_argument('--op',choices=['move','trim','mute','add-cue','undo'],required=True);edit.add_argument('--lane',choices=TRACKS,default='action');edit.add_argument('--clip-id');edit.add_argument('--id');edit.add_argument('--start-frame',type=int);edit.add_argument('--duration-frames',type=int);edit.add_argument('--label');edit.add_argument('--value',type=int)
    rend=sp.add_parser('render');rend.add_argument('--timeline',required=True);rend.add_argument('--media-root',required=True);rend.add_argument('--project',required=True);rend.add_argument('--out',required=True)
    a=p.parse_args()
    if a.action=='conform':ans=conform(a.source,a.out,a.frames,a.width,a.height)
    elif a.action=='init':
        d={'schema':'plotpickle.timeline.v1','projectId':a.project_id,'title':a.title,'ppfSha256':sha(a.project),'fps':24,'width':a.width,'height':a.height,'totalFrames':0,'revision':0,'tracks':{t:[] for t in TRACKS},'history':[],'renderStatus':'not-rendered','nativePpfModified':False};write_new(a.out,d);ans={'timeline':a.out,'revision':0,'ppfSha256':d['ppfSha256']}
    elif a.action=='validate':ans=validate(load(a.timeline),a.media_root,a.project)
    elif a.action=='edit':
        d=load(a.timeline);apply_edit(d,a.op,a.lane,a.clip_id,a.expected_revision,id=a.id,startFrame=a.start_frame,durationFrames=a.duration_frames,label=a.label,value=a.value);atomic_replace(a.timeline,d);ans={'revision':d['revision'],'renderStatus':d['renderStatus']}
    else:ans=render(load(a.timeline),a.media_root,a.project,a.out)
    print(json.dumps(ans,indent=2))
if __name__=='__main__':main()
