import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createProjectLoader } from '../src/loader.mjs';
import { sha256 } from '../src/projection.mjs';

const bytes=readFileSync(new URL('../fixture/synthetic-ppf.json',import.meta.url));
const ppf=JSON.parse(bytes.toString());
const identity={id:ppf.id,revision:ppf.revision,sha256:sha256(bytes)};
const fakeReader=async()=>({stdout:JSON.stringify({project:identity})});
const fakeRead=async()=>bytes;

test('never reveals a PPF without native reader configuration',async()=>{
 const r=await createProjectLoader({projectFile:'/private/source.json'})();
 assert.equal(r.status,'unconnected'); assert.equal(r.readonly,true);
 assert.equal('data' in r,false);
});
test('reader identity yields read-only source-linked view',async()=>{
 const r=await createProjectLoader({projectFile:'/private/source.json',inspector:'/reader',execute:fakeReader,read:fakeRead})();
 assert.equal(r.status,'source-backed'); assert.equal(r.data.source.projectId,ppf.id);
 assert.equal(r.data.readonly,true);assert.equal(r.data.edges.some(x=>x.kind==='scene-has-character-cue'),true);
});
test('native hash mismatch fails closed without leaking filesystem paths',async()=>{
 const execute=async()=>({stdout:JSON.stringify({project:{...identity,sha256:'a'.repeat(64)}})});
 const r=await createProjectLoader({projectFile:'/sensitive/private.json',inspector:'/private/reader',execute,read:fakeRead})();
 assert.equal(r.status,'blocked');assert.equal(r.reason,'SOURCE_FINGERPRINT_MISMATCH');
 assert.equal('data' in r,false);assert.doesNotMatch(JSON.stringify(r),/sensitive\/private|private\/reader/);
});
test('native reader execution errors never leak source text',async()=>{
 const execute=async()=>{throw Error('Secret screenplay text from /sensitive/private.json')};
 const r=await createProjectLoader({projectFile:'/sensitive/private.json',inspector:'/reader',execute,read:fakeRead})();
 assert.equal(r.status,'blocked');assert.equal(r.reason,'NATIVE_PROJECT_READER_UNAVAILABLE');
 assert.doesNotMatch(JSON.stringify(r),/Secret screenplay text|sensitive/);
});
