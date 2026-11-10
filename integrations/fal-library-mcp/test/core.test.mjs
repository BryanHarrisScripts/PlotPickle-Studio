import test from 'node:test';
import assert from 'node:assert/strict';
import {validateRequest,prepareToolResult,RESOURCE_URI,MAX_BYTES} from '../core.mjs';
const base={falUrl:'https://v3b.fal.media/files/b/0ab1d25b/example.mp4',expectedBytes:8495321,
 storyId:'The Third Bell',shotId:'Shot 01',fileName:'third-bell-shot01-1080p.mp4'};
test('source verification gives narrow safe acceptance shape',()=>{
 const result=validateRequest(base);
 assert.equal(result.url,base.falUrl);
 assert.equal(result.registration,'pending');
 assert.equal(result.libraryReadbackVerified,false);
 assert.equal(result.savedLockedUnchanged,true);
 assert.equal(RESOURCE_URI,'ui://plotpickle/fal-library-import/v1.html');
});
test('reject network SSRF, credentials, fragments, wrong paths, protocols and oversized video',()=>{
 const invalid=[
  'https://localhost/files/b/0ab1d25b/example.mp4',
  'https://v3b.fal.media.evil.test/files/b/0ab1d25b/example.mp4',
  'https://evil@v3b.fal.media/files/b/0ab1d25b/example.mp4',
  'https://v3b.fal.media/files/b/0ab1d25b/example.mp4#x',
  'http://v3b.fal.media/files/b/0ab1d25b/example.mp4',
  'https://v3b.fal.media/internal/status'];
 for(const url of invalid)assert.throws(()=>validateRequest({...base,falUrl:url}));
 assert.throws(()=>validateRequest({...base,expectedBytes:MAX_BYTES+1}));
 assert.throws(()=>validateRequest({...base,fileName:'../../sneaky.mp4'}));
});
test('refuse missing story identity, never claim project write',()=>{
 assert.throws(()=>validateRequest({...base,storyId:''}));
 const result=prepareToolResult(base);
 assert.equal(result.structuredContent.storyId,'The Third Bell');
 assert.match(result.content[0].text,/No generation or project edits/);
 assert.equal(result.structuredContent.savedLockedUnchanged,true);
});
