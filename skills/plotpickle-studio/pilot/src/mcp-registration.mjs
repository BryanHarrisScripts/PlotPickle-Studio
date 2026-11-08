// Sidebar registration seam. Requires the official MCP Apps + OpenAI extensions SDKs.
// Not used by the standalone acceptance preview. Hosting/transport/auth remain pending.
import { registerAppTool, registerAppResource, RESOURCE_MIME_TYPE } from '@modelcontextprotocol/ext-apps/server';
import { z } from 'zod';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const STUDIO_URI='ui://plotpickle/studio.html';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const escapeJson=obj=>JSON.stringify(obj).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
// loadProjection must return {status:'source-backed', data} or a blocked/unconnected response.
// It MUST verify current PPF bytes through the existing native PlotPickle reader.
export function registerPlotPickleStudio(server,loadProjection) {
  registerAppTool(server,'open_plotpickle_studio',{
    title:'PlotPickle Studio',
    description:'Open the source-linked, read-only PlotPickle Studio workspace. No writes, provider calls or charges.',
    inputSchema:z.object({}),
    _meta:{ui:{resourceUri:STUDIO_URI},'openai/ui':{entrypoints:[{type:'global'}]}}
  },async()=>{
    const payload=await loadProjection();
    return {content:[{type:'text',text:payload.status==='source-backed'?`Read-only PlotPickle Studio: ${payload.data.source.title}, revision ${payload.data.source.revision}`:'PlotPickle Studio: no independently verified project loaded.'}],structuredContent:payload};
  });
  registerAppResource(server,'PlotPickle Studio',STUDIO_URI,{mimeType:RESOURCE_MIME_TYPE},async()=>{
    const template=await readFile(resolve(root,'studio.html'),'utf8');
    const html=template.replace('__STUDIO_JSON__',escapeJson({status:'unconnected',message:'Open the app through the verified PlotPickle Studio tool.'}));
    return {contents:[{uri:STUDIO_URI,mimeType:RESOURCE_MIME_TYPE,text:html}]};
  });
  return server;
}
export {STUDIO_URI};
