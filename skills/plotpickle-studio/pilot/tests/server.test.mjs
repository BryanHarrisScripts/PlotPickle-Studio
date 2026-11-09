import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';

// Preview process is intentionally loopback-only, no secret or remote endpoint.
test('HTTP preview blocks writes and does not imply saved story state',async()=>{
  const child=spawn(process.execPath,['src/server.mjs'],{cwd:new URL('../',import.meta.url),
    env:{...process.env,PORT:'4399',PLOTPICKLE_PROJECT_FILE:'',PLOTPICKLE_INSPECTOR:''},stdio:['ignore','pipe','pipe']});
  try {
    await Promise.race([once(child.stdout,'data'),new Promise((_,reject)=>setTimeout(()=>reject(Error('timeout')),2500))]);
    const root='http://127.0.0.1:4399';
    const view=await fetch(root+'/api/studio');
    assert.equal(view.status,200);
    assert.equal(view.headers.get('cache-control'),'no-store');
    const payload=await view.json();
    assert.equal(payload.status,'unconnected'); assert.equal('data' in payload,false);
    const bad=await fetch(root+'/api/studio',{method:'POST',body:'{"change":"yes"}'});
    assert.equal(bad.status,405);
    const app=await fetch(root+'/');assert.equal(app.status,200);
    const html=await app.text();assert.match(html,/REEL/);assert.match(html,/ONCE/);assert.match(html,/Review/);assert.match(html,/Approve/);assert.match(html,/Regenerate/);assert.match(html,/authenticated project writer/);
    assert.match(html,/https:\/\/fal.ai\/dashboard/);assert.match(html,/https:\/\/suno.com\//);
    assert.equal((await fetch(root+'/etc/passwd')).status,404);
  } finally {child.kill('SIGTERM');await once(child,'exit').catch(()=>{});}
});
