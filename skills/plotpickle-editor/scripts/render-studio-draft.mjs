// Offline ChatGPT media-runtime adapter. Reads a prepared plan and explicit local
// input paths from stdin. No downloads, provider calls or native PPF mutations.
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';

const request=JSON.parse(fs.readFileSync(0,'utf8'));
const {plan,fingerprint}=request.prepared,inputs=request.inputs;
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
if(plan.schema!=='plotpickle.render-plan.v1'||digest(JSON.stringify(plan))!==fingerprint||plan.fps!==24)throw new Error('Invalid or changed render plan');
if(!path.isAbsolute(request.output)||!Array.isArray(inputs))throw new Error('Explicit local inputs and absolute output required');
if(plan.width*plan.height>1920*1080||plan.totalFrames>14400)throw new Error('Render exceeds bounded runtime limits');
const run=(command,args)=>{const r=spawnSync(command,args,{encoding:'utf8',maxBuffer:8*1024*1024});if(r.error||r.status!==0)throw new Error(command+' failed: '+(r.error?.message||r.stderr));return r.stdout;};
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_streams','-of','json',file]));
const decode=file=>run('ffmpeg',['-v','error','-xerror','-i',file,'-f','null','-']);
if(!['silent-reference; unbound cues are markers','verified-audio-mix-48k'].includes(plan.audio))throw new Error('Unsupported audio plan');
const clips=plan.tracks.video.filter(c=>c.enabled!==false).toSorted((a,b)=>a.startFrame-b.startFrame),sourceEvidence=[];
if(!clips.length)throw new Error('No video');
const args=['-v','error','-xerror','-y'],filters=[],parts=[];let end=0;
for(let i=0;i<clips.length;i++){
 const c=clips[i],input=inputs.find(x=>x.clipId===c.id);if(!input||!path.isAbsolute(input.path))throw new Error('Missing local bytes for '+c.id);
 if(digest(fs.readFileSync(input.path))!==c.sha256)throw new Error('Input hash mismatch: '+c.id);
 const meta=probe(input.path),v=meta.streams.find(s=>s.codec_type==='video');
 if(!v||v.r_frame_rate!=='24/1'||v.avg_frame_rate!=='24/1'||Number(v.nb_read_frames)<c.sourceInFrame+c.durationFrames||c.startFrame<end)throw new Error('Input timing mismatch or overlap: '+c.id);
 decode(input.path);sourceEvidence.push({clipId:c.id,sha256:c.sha256,frames:Number(v.nb_read_frames),fullDecode:true});args.push('-i',input.path);
 if(c.startFrame>end){filters.push('color=c=black:s='+plan.width+'x'+plan.height+':r=24,trim=end_frame='+(c.startFrame-end)+',setpts=PTS-STARTPTS[gap'+i+']');parts.push('[gap'+i+']');}
 filters.push('['+i+':v]trim=start_frame='+c.sourceInFrame+':end_frame='+(c.sourceInFrame+c.durationFrames)+',setpts=PTS-STARTPTS,scale='+plan.width+':'+plan.height+':force_original_aspect_ratio=decrease,pad='+plan.width+':'+plan.height+':(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v'+i+']');parts.push('[v'+i+']');end=c.startFrame+c.durationFrames;
}
if(end<plan.totalFrames){filters.push('color=c=black:s='+plan.width+'x'+plan.height+':r=24,trim=end_frame='+(plan.totalFrames-end)+',setpts=PTS-STARTPTS[tail]');parts.push('[tail]');}
if(end>plan.totalFrames)throw new Error('Picture exceeds frame extent');
filters.push(parts.join('')+'concat=n='+parts.length+':v=1:a=0[out]');
const audioSources=[],audioLabels=[],audioClips=['dialogue','foley','ambience','music'].flatMap(l=>plan.tracks[l].filter(c=>c.audioAssetId&&!c.muted));
for(let i=0;i<audioClips.length;i++){
 const c=audioClips[i],asset=plan.audioAssets?.find(a=>a.id===c.audioAssetId),input=(request.audioInputs||[]).find(a=>a.audioAssetId===c.audioAssetId);
 if(!asset||!input||!path.isAbsolute(input.path)||digest(fs.readFileSync(input.path))!==c.sha256||asset.sha256!==c.sha256)throw new Error('Audio input hash mismatch or missing: '+c.id);
 if(!Number.isInteger(c.sourceInFrame)||c.sourceInFrame<0||(c.sourceInFrame+c.durationFrames)*asset.sampleRate>asset.samples*24||!Number.isFinite(c.gainDb)||c.gainDb< -60||c.gainDb>12)throw new Error('Invalid audio trim or gain');
 const a=probe(input.path).streams.find(s=>s.codec_type==='audio');if(!a||Number(a.sample_rate)!==asset.sampleRate||a.channels!==asset.channels)throw new Error('Audio source format changed');
 decode(input.path);audioSources.push({audioAssetId:asset.id,sha256:asset.sha256,fullDecode:true});args.push('-i',input.path);
 filters.push('['+(clips.length+i)+':a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=start_sample='+(c.sourceInFrame*2000)+':end_sample='+((c.sourceInFrame+c.durationFrames)*2000)+',asetpts=PTS-STARTPTS,volume='+c.gainDb+'dB,adelay='+(c.startFrame*2000)+'S:all=1[a'+i+']');audioLabels.push('[a'+i+']');
}
if(audioLabels.length)filters.push(audioLabels.join('')+'amix=inputs='+audioLabels.length+':normalize=0:dropout_transition=0,alimiter=limit=0.95:level=0:latency=1,apad,atrim=end_sample='+(plan.totalFrames*2000)+'[audioout]');
fs.mkdirSync(path.dirname(request.output),{recursive:true});
if(!audioLabels.length)args.push('-f','lavfi','-i','anullsrc=r=48000:cl=stereo');
args.push('-filter_complex_threads','1','-filter_complex',filters.join(';'),'-map','[out]','-map',audioLabels.length?'[audioout]':clips.length+':a','-c:v','libx264','-threads','2','-preset','fast','-crf','22','-r','24','-frames:v',String(plan.totalFrames),'-c:a','aac','-t',String(plan.totalFrames/24),'-movflags','+faststart',request.output);
run('ffmpeg',args);decode(request.output);
const result=probe(request.output),v=result.streams.find(s=>s.codec_type==='video'),a=result.streams.find(s=>s.codec_type==='audio');
if(Number(v?.nb_read_frames)!==plan.totalFrames||v?.r_frame_rate!=='24/1'||v?.avg_frame_rate!=='24/1'||v?.width!==plan.width||v?.height!==plan.height||Number(a?.sample_rate)!==48000)throw new Error('Output verification failed');
const bytes=fs.readFileSync(request.output),sha256=digest(bytes),decodeEvidence={fullDecode:true,decoder:'ffmpeg',mediaSha256:sha256,frames:plan.totalFrames,fingerprint,...(plan.audio==='verified-audio-mix-48k'?{mixedAudio:true,audioSources}:{})};
const receipt={schema:'plotpickle.studio-render-receipt.v1',fingerprint,plan,sha256,bytes:bytes.length,sourceEvidence,decodeEvidence,output:request.output,nativePpfModified:false,providerJobSubmitted:false,approval:'editorial-draft-only'};
fs.writeFileSync(request.output+'.receipt.json',JSON.stringify(receipt,null,2));
process.stdout.write(JSON.stringify(receipt)+'\n');
