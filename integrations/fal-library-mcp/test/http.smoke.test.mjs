import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import {makeHttpApp} from '../server.mjs';
import {RESOURCE_URI} from '../core.mjs';

const example = {
  falUrl: 'https://v3b.fal.media/files/b/0ab1d25b/test-original.mp4',
  expectedBytes: 8495321,
  storyId: 'The Third Bell',
  shotId: 'Shot 01',
  fileName: 'third-bell-shot01-1080p.mp4'
};

test('real Streamable HTTP MCP: initialize, discover tool, load widget, prepare verified input', async () => {
  const app=makeHttpApp();
  app.listen(0,'127.0.0.1');
  await once(app,'listening');
  const base='http://127.0.0.1:'+app.address().port;
  const client=new Client({name:'plotpickle-http-test',version:'0.1.0'});
  try {
    const health=await fetch(base+'/healthz');
    assert.equal(health.status,200);
    assert.equal((await health.json()).mode,'acceptance-only');
    await client.connect(new StreamableHTTPClientTransport(new URL(base+'/mcp')));
    const tools=await client.listTools();
    const tool=tools.tools.find(x=>x.name==='prepare_fal_library_import');
    assert.ok(tool, 'MCP tool not discoverable over HTTP');
    assert.equal(tool._meta?.ui?.resourceUri,RESOURCE_URI);
    const widget=await client.readResource({uri:RESOURCE_URI});
    const body=widget.contents.find(x=>x.uri===RESOURCE_URI);
    assert.ok(body?.text?.includes('window.openai.uploadFile'));
    assert.match(body.mimeType,/text\/html/);
    const result=await client.callTool({name:'prepare_fal_library_import',arguments:example});
    assert.equal(result.isError,undefined);
    assert.equal(result.structuredContent.expectedBytes,8495321);
    assert.equal(result.structuredContent.storyId,'The Third Bell');
    assert.equal(result.structuredContent.registration,'pending');
    assert.equal(result.structuredContent.libraryReadbackVerified,false);
  } finally {
    await client.close().catch(()=>{});
    await new Promise(resolve=>app.close(resolve));
  }
});
