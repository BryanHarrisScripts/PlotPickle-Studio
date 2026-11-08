'use strict';
const FPS=24,TRACKS=['video','dialogue','action','foley','ambience','music'];
let project=null,selected=null,interval=null,totalFrames=360,dragging=null;
const el=id=>document.getElementById(id);
function tc(frame){frame=Math.max(0,Math.round(frame));let f=frame%24,s=Math.floor(frame/24)%60,m=Math.floor(frame/1440)%60,h=Math.floor(frame/86400);return [h,m,s,f].map(n=>('0'+n).slice(-2)).join(':')}
function notify(msg){el('notice').textContent=msg}
async function api(route,body){const r=await fetch('/api/'+route,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json','X-PlotPickle-Local':'editor-v1'}:{},body:body?JSON.stringify(body):undefined});let j=await r.json();if(!r.ok)throw new Error(j.error||'Local request failed');return j}
async function load(){try{project=await api('project');render();}catch(e){notify('Local bridge error: '+e.message)}}
function make(tag,cls,text){let n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n}
function render(){if(!project)return;
 el('storyTitle').textContent=project.title;el('revision').textContent='rev '+project.revision;
 el('badge').textContent='Local draft · source PPF untouched';
 el('rulerInfo').textContent='24 FPS · '+project.revision+' edits · draft only';
 totalFrames=Math.max(360,...Object.values(project.tracks).flat().map(c=>c.startFrame+c.durationFrames));totalFrames=Math.ceil(totalFrames/72)*72;
 let script=el('scriptScroll');script.replaceChildren();(project.script.length?project.script:[{id:'none',text:'No source script entries in this editor draft.',shot:1}]).forEach(p=>{let n=make('div','script-entry'+(selected&&selected.sourceShot===p.shot?' active':''));n.append(make('span','source',`Shot ${p.shot} · ${p.id}`),make('div','',p.text));n.addEventListener('click',()=>{let c=project.tracks.video.find(c=>c.sourceShot===p.shot);if(c){select('video',c.id);el('video').currentTime=c.startFrame/24}});script.append(n)});
 let grid=el('timelineGrid');grid.replaceChildren();const ruler=make('div','ruler');ruler.append(make('div','rowname','Timecode'));const bar=make('div','rulerbar');for(let f=0;f<=totalFrames;f+=72){let n=make('span','tick',tc(f).slice(3));n.style.left=`${f/totalFrames*100}%`;bar.append(n)}ruler.append(bar);grid.append(ruler);
 TRACKS.forEach(t=>{let row=make('div','rowtrack');row.append(make('div','rowname',t[0].toUpperCase()+t.slice(1)));let lane=make('div','lane');project.tracks[t].forEach(c=>{let node=make('div','clip '+t+(selected?.id===c.id?' selected':''),c.label||c.id);node.style.left=`${c.startFrame/totalFrames*100}%`;node.style.width=`${c.durationFrames/totalFrames*100}%`;node.title=`${c.label}\nStart: ${tc(c.startFrame)}\nDuration: ${c.durationFrames} frames${c.audioId?' · audio attached':' · no audio linked'}${c.muted?' · muted':''}`;if(t!=='video'&&t!=='action'){if(c.muted)node.classList.add('muted');if(!c.audioId)node.classList.add('unbound')}node.addEventListener('click',()=>select(t,c.id));node.addEventListener('pointerdown',e=>startDrag(e,t,c));lane.append(node)});row.append(lane);grid.append(row)});
 const ph=make('div','playhead');ph.id='playhead';ph.style.left='102px';ph.style.display='none';grid.style.position='relative';grid.append(ph);
 // Local file paths are intentionally never delivered by /api/project.
 // Use the server-issued same-origin preview URL only; do not reconstruct a path.
 const media=project.media||{};
 const shot=project.tracks.video.find(c=>{
   const m=media[c.mediaId];
   return m?.status==='verified-draft' && m.previewAvailable===true &&
     typeof m.previewUrl==='string' && /^\/media\/[a-zA-Z0-9_-]+-24fps\.mp4$/.test(m.previewUrl);
 });
 const video=el('video'),missing=el('missing');
 const renderPreview=project.job?.state==='render-complete' && project.job?.previewAvailable===true && /^\/render\/draft-revision-\d{4}\.mp4$/.test(project.job?.previewUrl||'');
 if(shot){
   const src=renderPreview?project.job.previewUrl:media[shot.mediaId].previewUrl;
   if(video.dataset.src!==src){video.pause();video.src=src;video.dataset.src=src}
   video.style.display='block';missing.style.display='none';
   el('playerStatus').textContent=renderPreview?'Picture + audio mix · verified':'Verified picture · original conform';
 }else{
   video.pause();video.removeAttribute('src');delete video.dataset.src;video.load();
   video.style.display='none';missing.style.display='flex';
   el('playerStatus').textContent=project.tracks.video.some(c=>media[c.mediaId]?.status==='verified-draft')
     ? 'Local media missing — check vault' : 'Source media not yet transferred';
 }
 const job=project.job||{};el('transfer').disabled=!Object.values(media).some(m=>m.status==='pending-transfer'||m.status==='failed')||['transferring','conforming','rendering'].includes(job.state);
 el('render').disabled=!shot||['transferring','conforming','rendering'].includes(job.state);
 el('undo').disabled=project.revision===0;
 const dl=el('downloadDraft');dl.style.display=renderPreview?'inline-flex':'none';if(renderPreview){dl.href=project.job.previewUrl;dl.download=`PlotPickle-TheThirdBell-shot01-rev${project.revision}.mp4`}
 if(selected){const c=project.tracks[selected.track]?.find(c=>c.id===selected.id);if(c)showInspector(selected.track,c);else selected=null}
 if(job.state==='failed')notify('Processing failed: '+job.error);
 else if(job.state==='complete' && !shot)notify('Media is marked verified but the MP4 is missing from the local vault. Restore the file; no re-generation is needed.');
 else if(job.state==='complete')notify('Verified 24 fps media ready. Click Render Draft to export.');
 else if(job.state==='render-complete')notify('Picture + sound draft verified. '+(job.audioNote||'')+' Click Play or Download Mix.');
 else if(['transferring','conforming','rendering'].includes(job.state))notify('Local job: '+job.state+'. Original and source project are unchanged.');
 else notify('Source-linked draft. Audio is mixed when a cue has a WAV source. Demo ocean/gulls sounds are synthetic placeholders.');
}
function select(track,id){const c=project.tracks[track].find(x=>x.id===id);selected={track,id,sourceShot:c.sourceShot};render()}
function showInspector(track,c){let panel=el('inspectorBody');panel.replaceChildren();el('selectedTrack').textContent=track;
 panel.append(make('div','kicker',`Clip ${c.id} · ${track}`));
 function field(label,key,type='text'){let wrapper=make('label','',label),input=make(type==='textarea'?'textarea':'input');if(type!=='textarea')input.type=type;input.id='field_'+key;input.value=String(c[key]??'');wrapper.append(input);return wrapper}
 panel.append(field('Label','label'));let row=make('div','formrow');row.append(field('Start frame (24 fps)','startFrame','number'),field('Duration in frames','durationFrames','number'));panel.append(row);
 if(!['video','action'].includes(track)){
  panel.append(field('Gain (dB) · applied to mix','gainDb','number'));
  const mute=make('label','mute-label','Mute this cue');const cb=make('input');cb.type='checkbox';cb.id='field_muted';cb.checked=c.muted===true;mute.append(cb);panel.append(mute);
  const asset=project.audioAssets?.[c.audioId];
  panel.append(make('div','kicker',asset?`Audio: ${asset.label}`:'Unbound cue: no sound will be mixed'));
  const upload=make('label','','Replace with local WAV (up to 32 MB)');const file=make('input');file.type='file';file.accept='.wav,audio/wav,audio/x-wav';file.id='audioFile';upload.append(file);panel.append(upload);
  const btn=make('button','','Attach WAV to cue');btn.addEventListener('click',async()=>{const f=file.files?.[0];if(!f){notify('Select a WAV file first.');return}if(f.size>32*1024*1024){notify('WAV exceeds 32 MB.');return}
    try{btn.disabled=true;const response=await fetch('/api/audio-upload',{method:'POST',headers:{'Content-Type':'audio/wav','X-PlotPickle-Local':'editor-v1','X-PlotPickle-Track':track,'X-PlotPickle-Clip':c.id,'X-PlotPickle-Revision':String(project.revision)},body:f});const j=await response.json();if(!response.ok)throw new Error(j.error||'Upload failed');project=j;render();notify('Imported WAV, normalized to 48 kHz and linked to cue. Render Draft to audition.')}catch(e){notify('Audio import failed: '+e.message);btn.disabled=false}});panel.append(btn);
 }
 panel.append(field('Notes / speech / Foley intent','note','textarea'));
 panel.append(make('div','kicker',`Starts ${tc(c.startFrame)} · Ends ${tc(c.startFrame+c.durationFrames)}`));
 let save=make('button','primary','Save Edit');save.addEventListener('click',async()=>{const ev={expectedRevision:project.revision,operation:'change',track,id:c.id,label:el('field_label').value,startFrame:Number(el('field_startFrame').value),durationFrames:Number(el('field_durationFrames').value),note:el('field_note').value};if(el('field_gainDb')){ev.gainDb=Number(el('field_gainDb').value);ev.muted=el('field_muted').checked;}try{project=await api('edit',ev);render()}catch(e){notify(e.message)}});panel.append(save);
 if(track!=='video'){let remove=make('button','remove','Remove Cue');remove.addEventListener('click',async()=>{try{project=await api('edit',{operation:'remove',expectedRevision:project.revision,track,id:c.id});selected=null;panel.replaceChildren(make('div','placeholder','Select a clip to edit.'));render()}catch(e){notify(e.message)}});panel.append(remove)}
}
function startDrag(e,track,c){if(e.button!==0)return;dragging={startX:e.clientX,track,id:c.id,original:c.startFrame,moved:false};e.currentTarget.setPointerCapture(e.pointerId);e.currentTarget.addEventListener('pointermove',onDrag);e.currentTarget.addEventListener('pointerup',onDrop,{once:true})}
function onDrag(e){if(!dragging)return;let lane=e.currentTarget.parentElement;let width=lane.getBoundingClientRect().width;let dx=(e.clientX-dragging.startX)/width*totalFrames;let newStart=Math.max(0,Math.round((dragging.original+dx)/3)*3);e.currentTarget.style.left=(newStart/totalFrames*100)+'%';dragging.moved=newStart!==dragging.original;dragging.newStart=newStart}
async function onDrop(e){e.currentTarget.removeEventListener('pointermove',onDrag);let d=dragging;dragging=null;if(!d||!d.moved)return;try{project=await api('edit',{operation:'change',expectedRevision:project.revision,track:d.track,id:d.id,startFrame:d.newStart});selected={track:d.track,id:d.id};render()}catch(x){notify(x.message);render()}}
function bind(){el('transfer').addEventListener('click',async()=>{const m=Object.values(project.media).find(m=>m.status==='pending-transfer'||m.status==='failed');if(!m)return;try{await api('transfer',{mediaId:m.id});await load()}catch(e){notify(e.message)}});
 el('render').addEventListener('click',async()=>{try{await api('render',{expectedRevision:project.revision});await load()}catch(e){notify(e.message)}});
 el('undo').addEventListener('click',async()=>{try{project=await api('undo',{expectedRevision:project.revision});selected=null;render()}catch(e){notify(e.message)}});
 document.querySelectorAll('[data-track]').forEach(b=>b.addEventListener('click',async()=>{let t=b.dataset.track,id=t+'-'+Date.now().toString(36);let c={id,label:t+' cue',startFrame:0,durationFrames:72,gainDb:0,note:'',mediaId:null,audioId:null,muted:false,sourceShot:null};try{project=await api('edit',{expectedRevision:project.revision,operation:'add',track:t,clip:c});select(t,id)}catch(e){notify(e.message)}}));
 el('video').addEventListener('timeupdate',()=>{let frame=Math.floor(el('video').currentTime*FPS);el('timecode').textContent=tc(frame);let ph=el('playhead');ph.style.display='block';ph.style.left=`calc(102px + (100% - 102px) * ${frame/totalFrames})`});
 interval=setInterval(async()=>{if(project && ['transferring','conforming','rendering'].includes(project.job?.state))await load()},1200);
}
bind();load();
