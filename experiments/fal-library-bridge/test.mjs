import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import { makeFalAssetHandler, validateFalUrl } from "./proxy.mjs";
import { saveFalAssetToLibrary } from "./widget.mjs";

const GOOD_URL = "https://v3b.fal.media/files/b/abc123/example.mp4";
const payload = Buffer.from("TEST-VIDEO-BYTES", "utf8");

test("fal media URL validation blocks SSRF and other hosts", () => {
  assert.equal(validateFalUrl(GOOD_URL), GOOD_URL);
  for (const url of [
    "http://v3b.fal.media/files/b/abc123/example.mp4",
    "https://v3b.fal.media.evil.test/files/b/abc123/example.mp4",
    "https://127.0.0.1/files/b/abc123/example.mp4",
    "https://v3b.fal.media@127.0.0.1/files/b/abc123/example.mp4",
    "https://v3b.fal.media/admin",
    "https://v3b.fal.media/files/b/abc123/example.mp4#fragment"
  ]) assert.throws(() => validateFalUrl(url));
});

test("proxy rejects handler without authentication", () => {
  assert.throws(() => makeFalAssetHandler(), /authorization/);
});

test("proxy transports bytes, widget calls library:true, returns upload receipt", async () => {
  const upstreamResponse = new Response(payload, {
    headers: { "content-type": "video/mp4", "content-length": String(payload.length) }
  });
  const handler = makeFalAssetHandler({
    authorize: async (req) => req.headers["x-test-auth"] === "trusted-for-test-only",
    fetchImpl: async () => upstreamResponse
  });
  const server = createServer(handler);
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  try {
    const url = "http://127.0.0.1:" + server.address().port + "/api/fetch-fal-asset";
    const unauthorized = await fetch(url, {method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify({falUrl:GOOD_URL})});
    assert.equal(unauthorized.status,401);
    const receipt = await saveFalAssetToLibrary({
      falUrl:GOOD_URL,
      proxyUrl:url,
      fileName:"shot01-original.mp4",
      expectedBytes:payload.length,
      fetchImpl: (input, options) => fetch(input, {...options,
        headers:{...options.headers,"x-test-auth":"trusted-for-test-only"}}),
      openai:{uploadFile:async (file, opts)=>{
        assert.deepEqual(opts, {library:true});
        assert.equal(file.name,"shot01-original.mp4");
        assert.deepEqual(Buffer.from(await file.arrayBuffer()),payload);
        return {fileId:"test-file-id"};
      }}
    });
    assert.equal(receipt.fileId, "test-file-id");
    assert.equal(receipt.status, "upload-reported");
    assert.equal(receipt.libraryReadbackVerified,false);
  } finally {
    server.close();
    await once(server,"close");
  }
});

test("proxy rejects a declared oversized media response", async () => {
  const handler=makeFalAssetHandler({
    authorize:async()=>true,
    maxBytes:5,
    fetchImpl:async()=>new Response(payload,{headers:{"content-type":"video/mp4","content-length":String(payload.length)}})
  });
  const server=createServer(handler);
  server.listen(0,"127.0.0.1");
  await once(server,"listening");
  try{
    const resp=await fetch("http://127.0.0.1:"+server.address().port+"/",{
      method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({falUrl:GOOD_URL})
    });
    assert.equal(resp.status,413);
  }finally{server.close(); await once(server,"close");}
});
