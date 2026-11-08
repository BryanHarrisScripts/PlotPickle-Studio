// Local acceptance preview only. This is not a deployed ChatGPT sidebar entrypoint.
import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createProjectLoader } from './loader.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const port=Number(process.env.PORT||4318);
const load=createProjectLoader({
  projectFile:process.env.PLOTPICKLE_PROJECT_FILE,
  inspector:process.env.PLOTPICKLE_INSPECTOR
});
const server=http.createServer(async(req,res)=>{
  try {
    const path=new URL(req.url,'http://localhost').pathname;
    res.setHeader('Cache-Control','no-store');
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
    if(req.method!=='GET') {res.writeHead(405);return res.end('Read-only service');}
    if(path==='/api/studio') {res.setHeader('Content-Type','application/json; charset=utf-8');return res.end(JSON.stringify(await load()));}
    if(path==='/') {res.setHeader('Content-Type','text/html; charset=utf-8');return res.end(await readFile(resolve(root,'studio.html'),'utf-8'));}
    res.writeHead(404);res.end('Not found');
  } catch(e){res.writeHead(503,{'Content-Type':'application/json'});res.end(JSON.stringify({status:'blocked',reason:String(e.message).slice(0,250)}));}
});
server.listen(port,'127.0.0.1',()=>console.log(`Read-only PlotPickle Studio acceptance preview: http://127.0.0.1:${port}`));
