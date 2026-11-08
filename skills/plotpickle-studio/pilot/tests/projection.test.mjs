import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import {projectStudio,sha256} from '../src/projection.mjs';
const bytes=readFileSync(new URL('../fixture/synthetic-ppf.json', import.meta.url));
const sample=JSON.parse(bytes.toString());
const identity={id:sample.id,revision:sample.revision,sha256:sha256(bytes)};
test('deterministic source-linked relationships',()=>{
 const p=projectStudio(sample,bytes,identity,{demo:true});
 assert.equal(p.readonly,true);assert.equal(p.scenes.length,2);assert.equal(p.people.length,1);
 assert.equal(p.people[0].sceneIds.length,2);assert.equal(p.shots.length,1);assert.equal(p.shots[0].sceneId,p.scenes[0].id);
 assert.deepEqual(p.shots[0].sourcePassageIds,['p1','p2']);assert.equal(p.shots[0].promptStatus,'recorded-exact');
 assert.equal(p.shots[0].imageStatus,'bytes-not-verified');assert.equal(p.shots[0].saveLockStatus,'not-verified');
});
test('rejects absent or mismatching native identity',()=>{
 assert.throws(()=>projectStudio(sample,bytes,null),/NATIVE_IDENTITY_REQUIRED/);
 assert.throws(()=>projectStudio(sample,bytes,{...identity,sha256:'a'.repeat(64)}),/SOURCE_FINGERPRINT_MISMATCH/);
 assert.throws(()=>projectStudio(sample,bytes,{...identity,revision:2}),/IDENTITY_REVISION_MISMATCH/);
});
test('missing screenplay creates no fabricated scenes, people or shots',()=>{
 const empty={id:'empty-test',revision:0,title:'Empty'};const b=Buffer.from(JSON.stringify(empty));
 const x=projectStudio(empty,b,{id:'empty-test',revision:0,sha256:sha256(b)});
 assert.equal(x.scenes.length,0);assert.equal(x.people.length,0);assert.equal(x.shots.length,0);
});
test('conflicting prompts fail visibly closed',()=>{
 const changed=structuredClone(sample);changed.production.storyboardImagePrompts[0].prompt='conflicting replacement';const b=Buffer.from(JSON.stringify(changed));
 const x=projectStudio(changed,b,{...identity,sha256:sha256(b)});
 assert.equal(x.shots[0].promptStatus,'conflicting-records');assert.equal(x.shots[0].prompt,null);
});
test('no mutating API is exposed in projection',()=>{
 const p=projectStudio(sample,bytes,identity);
 assert.equal(p.readonly,true);assert.equal('write' in p,false);assert.equal('generate' in p,false);
});
test('maps an actual PPF artwork entry without claiming its bytes or native lock verified',()=>{
 const x=structuredClone(sample); x.assetRegistry.extensions.artworkMapping={entries:[{artifactId:'a1',filename:'one.webp',address:{blockNumber:1,miniBlockNumber:1,shotNumber:2},passageIds:['p3'],packageMediaBytesVerified:true,savedMarkerPresent:true,locked:true,mappingStatus:'editorial-match'}]};
 const b=Buffer.from(JSON.stringify(x));const p=projectStudio(x,b,{...identity,sha256:sha256(b)});
 assert.equal(p.shots.length,2);const s=p.shots.find(x=>x.address.shot===2);assert.equal(s.sceneId,p.scenes[0].id);assert.equal(s.candidateRecords[0].mediaBytesVerifiedThisSession,false);
 assert.match(s.saveLockStatus,/not reverified/);assert.equal(s.candidateRecords[0].locked,true);
});
test('linked graph edges cite the source while preserving distinct scene and place IDs',()=>{
 const x=projectStudio(sample,bytes,identity,{demo:true});
 assert.equal(x.schemaVersion,2);
 assert.equal(x.edges.filter(e=>e.kind==='scene-has-heading-place').length,2);
 assert(x.edges.some(e=>e.kind==='scene-has-character-cue' && e.sourcePassageIds.length));
 assert(x.edges.some(e=>e.kind==='shot-mapped-to-scene'));
 assert(x.sourcePassages.some(p=>p.id==='p1' && p.text));
});
test('REEL and ONCE are read-only views of the same identity, not two stores',()=>{
 const x=projectStudio(sample,bytes,identity);
 assert.deepEqual(x.modeChoices,['REEL','ONCE']);
 assert.equal(x.source.projectId,identity.id);
 assert(x.limitations.some(s=>s.includes('never reclassifies')));
});
