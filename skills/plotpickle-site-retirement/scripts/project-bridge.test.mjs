import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeProjects,fileKind,prepareBatchPreview,persistReviewDraft,canonicalStoryFolder} from './project-bridge.mjs';
const source={projectId:'test-id',revision:10,ppfSha256:'a'.repeat(64)};
const candidate=(shot,opts={})=>({shot,kind:'image',candidateId:`c${shot}`,mediaSha256:'b'.repeat(64),
   verified:true,sourceMappingVerified:true,ppfLocked:false,humanApproved:false,...opts});
const choice=(shot,action,opts={})=>({shot,kind:'image',candidateId:`c${shot}`,mediaSha256:'b'.repeat(64),action,...opts});
class FakeStore {
 constructor(){this.map=new Map()}
 key(user,id){return `${user}/${id}`}
 async read(u,id){return this.map.get(this.key(u,id))||null}
 async compareAndSwap(u,id,revision,value){let key=this.key(u,id),prev=this.map.get(key);if((prev?.revision??0)!==revision)throw Error('CAS conflict');let next={revision:revision+1,value:structuredClone(value)};this.map.set(key,next);return next}
}
test('classified media includes audio and excludes metadata',()=>{
 assert.equal(fileKind('master.WAV'),'audio');assert.equal(fileKind('opening.mp4'),'video');assert.equal(fileKind('still.webp'),'image');assert.equal(fileKind('story.ppf.json'),'ppf');
});
test('unprefixed legacy folder is displayed with one PP prefix',()=>{
 const result=summarizeProjects([{kind:'file',name:'image.webp',path:'/PlotPickle/Stories/The Third Bell/Review Pending/image.webp',size_bytes:123}]);
 assert.equal(result[0].displayName,'PP - The Third Bell');assert.equal(result[0].folder,'/PlotPickle/Stories/The Third Bell');
 assert.equal(result[0].discovered,1);assert.equal(result[0].verified,0);assert.equal(result[0].unassigned,1);
});
test('folder traversal rejected',()=>{
 assert.throws(()=>summarizeProjects([{kind:'file',name:'x',path:'/PlotPickle/Stories/../private/x'}]),/outside authorized/)
});
test('Keep is not Lock and is preview only',()=>{
 const res=prepareBatchPreview({source,candidates:[candidate(1)],decisions:[choice(1,'keep')]});
 assert.equal(res.blocked,0);assert.equal(res.nativePpfWritten,false);assert.equal(res.providerJobSubmitted,false);
});
test('Redo of locked media blocked; no implicit unlock',()=>{
 const res=prepareBatchPreview({source,candidates:[candidate(1,{ppfLocked:true})],decisions:[choice(1,'redo')]});
 assert.equal(res.blocked,1);assert.match(res.items[0].issues.join(),/locked-source-requires-unlock/);
});
test('source link and exact media SHA required',()=>{
 const res=prepareBatchPreview({source,candidates:[candidate(1,{sourceMappingVerified:false})],decisions:[choice(1,'keep',{mediaSha256:'b'.repeat(64)})]});
 assert.equal(res.blocked,1);
});
test('duplicate decisions blocked',()=>{
 assert.throws(()=>prepareBatchPreview({source,candidates:[candidate(1)],decisions:[choice(1,'keep'),choice(1,'redo')]}),/Duplicate decision/)
});
test('Request Lock requires specific image approval',()=>{
 const a=prepareBatchPreview({source,candidates:[candidate(1)],decisions:[choice(1,'keep',{requestLock:true})]});assert.equal(a.blocked,1)
});
test('persist draft + readback, revision CAS, user isolation',async()=>{
 const store=new FakeStore(), args={store,source,candidates:[candidate(1)],decisions:[choice(1,'keep')],expectedStudioRevision:0};
 const result=await persistReviewDraft({...args,authenticatedActor:'userA'});
 assert.equal(result.saved,true);assert.equal(result.studioRevision,1);
 assert.equal(await store.read('userB',source.projectId),null);
 await assert.rejects(persistReviewDraft({...args,authenticatedActor:'userA'}),/Stale Studio revision/);
});
test('blocked execution proposal persists safely but does not modify originals',async()=>{
 const store=new FakeStore();const res=await persistReviewDraft({authenticatedActor:'userA',store,source,candidates:[candidate(1,{ppfLocked:true})],decisions:[choice(1,'discard')],expectedStudioRevision:0});
 assert.equal(res.saved,true);assert.equal(res.blockedItems,1);
 const draft=await store.read('userA',source.projectId);
 assert.equal(draft.value.reviewBatch.items[0].blocked,true);assert.equal(res.nativePpfWritten,false);
});
test('no authenticated actor => no persistence',async()=>{
 const store=new FakeStore();await assert.rejects(persistReviewDraft({authenticatedActor:null,store,source,candidates:[candidate(1)],decisions:[choice(1,'keep')],expectedStudioRevision:0}),/Not authenticated/);
});

test('real prefixed Library folders do not become PP - PP - names',()=>{
 const list=summarizeProjects([
  {kind:'folder',name:'PP - Afterglow',path:'/PlotPickle/Stories/PP - Afterglow'},
  {kind:'file',name:'summary.md',path:'/PlotPickle/Stories/PP - Afterglow/Review Pending/summary.md'},
  {kind:'file',name:'a.webp',path:'/PlotPickle/Stories/PP - Brotherly Love/Review Pending/a.webp'},
  {kind:'file',name:'a.mp4',path:'/PlotPickle/Stories/PP - The Third Bell/Production Drafts/a.mp4'},
 ]);
 assert.equal(list.length,3);
 assert.ok(list.every(x=>x.displayName.startsWith('PP - ')&&!x.displayName.startsWith('PP - PP - ')));
 assert.equal(list.find(x=>x.story==='Afterglow').folder,'/PlotPickle/Stories/PP - Afterglow');
 assert.equal(canonicalStoryFolder('PP - PP - The Third Bell'),'PP - The Third Bell');
});

test('review sidecar update preserves existing timeline, clips and other draft fields',async()=>{
 const store=new FakeStore();await store.compareAndSwap('u',source.projectId,0,{source, timeline:{revision:7,clips:['s1','s2']},notes:'protected'});
 const res=await persistReviewDraft({authenticatedActor:'u',store,source,candidates:[candidate(1)],decisions:[choice(1,'keep')],expectedStudioRevision:1});
 const saved=await store.read('u',source.projectId);
 assert.equal(res.studioRevision,2);
 assert.deepEqual(saved.value.timeline.clips,['s1','s2']);
 assert.equal(saved.value.notes,'protected');
});

test('batch proposal never locks anything implicitly',()=>{
 const res=prepareBatchPreview({source,candidates:[candidate(1,{humanApproved:true,ppfLocked:true})],decisions:[choice(1,'keep')]});
 assert.equal(res.items[0].requestLock,false);
 assert.equal(res.execution,false);
});

import {createHash} from 'node:crypto';
import {loadProjectFromLibrary} from './project-bridge.mjs';
test('authenticated project load verifies current media bytes without inventing shot placements',async()=>{
 const b=new TextEncoder().encode('test media');
 const registry={schema:'plotpickle.library-project-registry.v1',projects:[{key:'pp-test',displayName:'PP - Test',
    libraryPath:'/PlotPickle/Stories/PP - Test',source:{path:'/PlotPickle/Stories/PP - Test/master.ppf.json',sha256:null}}]};
 const calls=[];
 const library={async listFilesForActor(args){calls.push(args);return [{kind:'file',name:'shot.webp',path:'/PlotPickle/Stories/PP - Test/Images/shot.webp',library_file_id:'libfile-1',size_bytes:b.length}]},
 async readFileForActor(args){calls.push(args);return b;}};
 const res=await loadProjectFromLibrary({authenticatedActor:'server-session-user',registry,projectKey:'pp-test',library});
 assert.equal(res.counts.image,1);assert.equal(res.counts.mediaHashVerified,1);
 assert.equal(res.counts.unassigned,1);assert.equal(res.editorLoaded,false);
 assert.equal(res.items[0].sha256,createHash('sha256').update(b).digest('hex'));
 assert.ok(calls.every(x=>x.actor==='server-session-user'));
});
test('no authenticated Library connection fails closed',async()=>{
 const registry={schema:'plotpickle.library-project-registry.v1',projects:[{key:'pp-test',displayName:'PP - Test',libraryPath:'/PlotPickle/Stories/PP - Test'}]};
 await assert.rejects(loadProjectFromLibrary({authenticatedActor:'user',registry,projectKey:'pp-test',library:null}),/LIBRARY_CONNECTOR_UNAVAILABLE/);
 await assert.rejects(loadProjectFromLibrary({authenticatedActor:null,registry,projectKey:'pp-test',library:{}}),/Not authenticated/);
});
test('cross-project file injection rejected',async()=>{
 const registry={schema:'plotpickle.library-project-registry.v1',projects:[{key:'pp-a',displayName:'PP - A',libraryPath:'/PlotPickle/Stories/PP - A'}]};
 const library={async listFilesForActor(){return [{kind:'file',name:'bad.webp',path:'/PlotPickle/Stories/PP - B/x.webp',library_file_id:'wrong'}]},
 async readFileForActor(){throw Error('should not read')}};
 await assert.rejects(loadProjectFromLibrary({authenticatedActor:'user',registry,projectKey:'pp-a',library}),/Invalid or repeated Library file/);
});
test('PPF hash conflicts fail closed',async()=>{
 const registry={schema:'plotpickle.library-project-registry.v1',projects:[{key:'pp-test',displayName:'PP - Test',libraryPath:'/PlotPickle/Stories/PP - Test',source:{path:'/PlotPickle/Stories/PP - Test/x.ppf.json',sha256:'a'.repeat(64)}}]};
 const library={async listFilesForActor(){return [{kind:'file',name:'x.ppf.json',path:'/PlotPickle/Stories/PP - Test/x.ppf.json',library_file_id:'source-id',size_bytes:4}]},
 async readFileForActor(){return new Uint8Array([1,2,3,4])}};
 await assert.rejects(loadProjectFromLibrary({authenticatedActor:'user',registry,projectKey:'pp-test',library}),/PPF_SOURCE_HASH_CONFLICT/);
});
