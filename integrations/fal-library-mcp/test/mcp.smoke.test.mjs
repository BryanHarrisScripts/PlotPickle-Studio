import test from 'node:test';
import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {InMemoryTransport} from '@modelcontextprotocol/sdk/inMemory.js';
import {makeMcpServer} from '../server.mjs';
import {RESOURCE_URI} from '../core.mjs';

test('MCP Apps tool registers resource and returns structured original fal payload',async()=>{
 const mcp=makeMcpServer();
 const client=new Client({name:'plotpickle-acceptance-client',version:'0.1.0'});
 const [clientTransport,serverTransport]=InMemoryTransport.createLinkedPair();
 try {
   await mcp.connect(serverTransport);
   await client.connect(clientTransport);
   const tools=await client.listTools();
   const t=tools.tools.find(x=>x.name==='prepare_fal_library_import');
   assert.ok(t,'Transfer tool missing');
   assert.equal(t._meta?.ui?.resourceUri,RESOURCE_URI);
   const res=await client.readResource({uri:RESOURCE_URI});
   const html=res.contents.find(x=>x.uri===RESOURCE_URI);
   assert.ok(html,'Widget resource missing');
   assert.match(html.mimeType,/text\/html/);
   assert.match(html.text,/uploadFile/);
   const result=await client.callTool({name:'prepare_fal_library_import',arguments:{
     falUrl:'https://v3b.fal.media/files/b/0ab1d25b/test-original.mp4',expectedBytes:8495321,
     storyId:'The Third Bell',shotId:'Shot 01',fileName:'third-bell-shot01-1080p.mp4'
   }});
   assert.equal(result.isError,undefined);
   assert.equal(result.structuredContent.storyId,'The Third Bell');
   assert.equal(result.structuredContent.libraryReadbackVerified,false);
 } finally {await client.close();await mcp.close();}
});
