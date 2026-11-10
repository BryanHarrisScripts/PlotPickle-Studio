import {createServer as createHttpServer} from 'node:http';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StreamableHTTPServerTransport} from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import {registerAppResource,registerAppTool,RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';
import {RESOURCE_URI,MAX_BYTES,prepareToolResult} from './core.mjs';

const widgetHtml = readFileSync(join(dirname(fileURLToPath(import.meta.url)),'widget.html'),'utf8');

export function makeMcpServer() {
  const mcp = new McpServer({name:'plotpickle-fal-library-acceptance',version:'0.1.0'});
  registerAppResource(mcp,'fal-library-transfer-widget',RESOURCE_URI,{},async()=>({
    contents:[{uri:RESOURCE_URI,mimeType:RESOURCE_MIME_TYPE,text:widgetHtml,
      _meta:{ui:{prefersBorder:true,csp:{connectDomains:['https://v3b.fal.media']}}}}]
  }));
  registerAppTool(mcp,'prepare_fal_library_import',{
    title:'Test fal video to ChatGPT Library transfer',
    description:'Open the native ChatGPT transfer acceptance widget for an existing fal MP4. Does not generate media, save a story, or spend credits.',
    inputSchema:{
      falUrl:z.string().url(),expectedBytes:z.number().int().positive().max(MAX_BYTES),
      storyId:z.string().min(1).max(120),shotId:z.string().min(1).max(120),
      fileName:z.string().max(124).optional()
    },
    annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},
    _meta:{ui:{resourceUri:RESOURCE_URI}}
  },async(args)=>prepareToolResult(args));
  return mcp;
}

export function makeHttpApp() {
  return createHttpServer(async (req,res)=>{
    const u = new URL(req.url||'/',`http://${req.headers.host||'localhost'}`);
    if(req.method==='GET' && u.pathname==='/healthz'){
      res.writeHead(200,{'content-type':'application/json','cache-control':'no-store'});
      res.end(JSON.stringify({ok:true,service:'plotpickle-fal-library-mcp',mode:'acceptance-only'}));return;
    }
    if(u.pathname==='/mcp' && req.method==='OPTIONS'){
      res.writeHead(204,{'access-control-allow-origin':'*',
        'access-control-allow-methods':'GET,POST,DELETE,OPTIONS',
        'access-control-allow-headers':'content-type,mcp-session-id,mcp-protocol-version,authorization',
        'access-control-expose-headers':'Mcp-Session-Id'});res.end();return;
    }
    if(u.pathname==='/mcp' && ['GET','POST','DELETE'].includes(req.method)){
      res.setHeader('access-control-allow-origin','*');
      res.setHeader('access-control-expose-headers','Mcp-Session-Id');
      const mcp=makeMcpServer();
      const transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true});
      res.on('close',()=>{transport.close();mcp.close();});
      try{await mcp.connect(transport); await transport.handleRequest(req,res);}catch(err){
        console.error('MCP request failed:',err?.message);
        if(!res.headersSent){res.writeHead(500).end('Internal error');}
      }
      return;
    }
    res.writeHead(404,{'content-type':'text/plain'}).end('Not found');
  });
}

if(process.argv[1] && fileURLToPath(import.meta.url)===process.argv[1]){
  const port=Number(process.env.PORT||8787);
  makeHttpApp().listen(port,()=>console.log(`PlotPickle MCP acceptance runtime on http://localhost:${port}/mcp`));
}
