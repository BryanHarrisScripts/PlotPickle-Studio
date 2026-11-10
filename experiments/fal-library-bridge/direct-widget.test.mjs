import test from 'node:test';
import assert from 'node:assert/strict';
import {saveFalAssetToLibrary} from './widget.mjs';

const url = 'https://v3b.fal.media/files/b/abc123/example.mp4';
const bytes = Buffer.from('dummy-video');
const response = () => new Response(bytes, {headers:{'content-type':'video/mp4','content-length':String(bytes.length)}});
const host = {uploadFile:async (file, options)=> {
  assert.deepEqual(options, {library:true});
  assert.deepEqual(Buffer.from(await file.arrayBuffer()), bytes);
  return {fileId:'receipt123'};
}};

test('direct fal fetch is preferred, without a proxy', async()=>{
  const result=await saveFalAssetToLibrary({falUrl:url, expectedBytes: bytes.length, openai:host,
    fetchImpl: async (input, options)=> {assert.equal(input,url);assert.equal(options.method,'GET');return response();}});
  assert.equal(result.sourceRoute,'direct'); assert.equal(result.fileId,'receipt123');
});

test('failed direct browser fetch makes no false upload claim', async()=>{
  let uploaded=false;
  await assert.rejects(saveFalAssetToLibrary({
    falUrl:url, openai:{uploadFile:()=>{uploaded=true;}},
    fetchImpl:async()=>{throw new TypeError('CORS');}
  }), /Direct fal download unavailable/);
  assert.equal(uploaded, false);
});

test('existing approved proxy is optional fallback only', async()=>{
  let n=0;
  const result=await saveFalAssetToLibrary({
    falUrl:url,proxyUrl:'/api/fetch-fal-asset',expectedBytes:bytes.length,openai:host,
    fetchImpl: async (input, options)=>{
      n++;
      if(n===1){assert.equal(input,url);throw new TypeError('blocked');}
      assert.equal(input,'/api/fetch-fal-asset'); assert.equal(options.method,'POST');
      return response();
    }
  });
  assert.equal(result.sourceRoute,'proxy');assert.equal(n,2);
});

test('reject unknown domains and bad MIME', async()=>{
  await assert.rejects(saveFalAssetToLibrary({
    falUrl:'https://localhost/files/b/abc123/example.mp4',openai:host
  }), /allowlisted/);
  await assert.rejects(saveFalAssetToLibrary({
    falUrl:url,openai:host,fetchImpl:async()=>new Response(bytes,{headers:{'content-type':'text/html'}})
  }), /MIME/);
});
