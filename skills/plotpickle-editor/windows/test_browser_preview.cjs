/* Dependency-free browser state regression for verified fal clip previews. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
class Element {
  constructor(tag,id='') {this.tagName=tag;this.id=id;this.children=[];this.style={};this.dataset={};this.listeners={};this.textContent='';this.value='';this.disabled=false;this.currentTime=0;this.src='';this.parentElement=null;}
  addEventListener(name,callback){this.listeners[name]=callback;}
  replaceChildren(...nodes){this.children=nodes;for(const n of nodes){if(n instanceof Element)n.parentElement=this;}}
  append(...nodes){for(const n of nodes){this.children.push(n);if(n instanceof Element)n.parentElement=this;}}
  removeAttribute(name){if(name==='src')this.src='';}
  pause(){}
  load(){}
  setPointerCapture(){}
}
const ids=['storyTitle','revision','badge','rulerInfo','scriptScroll','timelineGrid','video','missing','playerStatus','transfer','render','undo','selectedTrack','inspectorBody','notice','timecode','downloadDraft'];
const nodes=Object.fromEntries(ids.map(x=>[x,new Element('div',x)]));
const pending={schema:'plotpickle.editor-draft.v1',title:'The Third Bell',revision:0,source:{nativePpfModified:false},script:[{id:'screenplay-4',text:'Dawn',shot:1}],tracks:{video:[{id:'video-1',label:'Shot 01',mediaId:'shot01',startFrame:0,durationFrames:72,sourceShot:1}],dialogue:[],action:[],foley:[],ambience:[],music:[]},media:{shot01:{id:'shot01',status:'pending-transfer'}},job:{state:'idle'}};
const verified=JSON.parse(JSON.stringify(pending));
verified.media.shot01={id:'shot01',status:'verified-draft',previewAvailable:true,previewUrl:'/media/shot01-24fps.mp4',fps:24,frames:72};
verified.job={state:'complete',mediaId:'shot01'};
async function runCase(state,expected){
  for(const node of Object.values(nodes)){node.textContent='';node.disabled=false;node.children=[];node.dataset={};node.src='';node.style={};}
  const errors=[];
  const context={document:{getElementById:(id)=>nodes[id],createElement:(tag)=>new Element(tag),querySelectorAll:()=>[]},fetch:async()=>({ok:true,json:async()=>state}),setInterval:()=>0,clearInterval:()=>{},console:{error:(e)=>errors.push(e)}};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'app.js'),'utf8'),context);
  await new Promise(resolve=>setTimeout(resolve,0));
  assert.equal(nodes.playerStatus.textContent,expected.status);
  assert.equal(nodes.transfer.disabled,expected.transferDisabled);
  assert.equal(nodes.render.disabled,expected.renderDisabled);
  assert.equal(nodes.video.src,expected.src);
  assert.ok(!String(nodes.notice.textContent).includes('Local bridge error'),String(nodes.notice.textContent));
  assert.equal(errors.length,0);
  if(expected.src){
    vm.runInContext("select('video','video-1')",context);
    assert.equal(nodes.selectedTrack.textContent,'video');
    assert.equal(nodes['field_durationFrames'],undefined); // dynamically created elements are not registered in mock
  }
}
(async()=>{
  await runCase(pending,{status:'Source media not yet transferred',transferDisabled:false,renderDisabled:true,src:''});
  await runCase(verified,{status:'Verified picture · original conform',transferDisabled:true,renderDisabled:false,src:'/media/shot01-24fps.mp4'});
  const rendered=JSON.parse(JSON.stringify(verified));rendered.job={state:'render-complete',previewUrl:'/render/draft-revision-0000.mp4',previewAvailable:true};
  await runCase(rendered,{status:'Picture + audio mix · verified',transferDisabled:true,renderDisabled:false,src:'/render/draft-revision-0000.mp4'});
  const bad=JSON.parse(JSON.stringify(verified));delete bad.media.shot01.previewUrl;bad.media.shot01.previewAvailable=false;
  await runCase(bad,{status:'Local media missing — check vault',transferDisabled:true,renderDisabled:true,src:''});
  console.log('Browser preview state regression PASS: pending, imported, mixed render, missing files');
})().catch(e=>{console.error(e);process.exitCode=1});
