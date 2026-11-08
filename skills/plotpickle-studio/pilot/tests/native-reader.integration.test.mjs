import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { createProjectLoader } from '../src/loader.mjs';
import { sha256 } from '../src/projection.mjs';
const exec=promisify(execFile);
const dirname=path.dirname(fileURLToPath(import.meta.url));
const reader=path.resolve(dirname,'../../../read-plotpickle-project/scripts/inspect-project.mjs');
const importer=path.resolve(dirname,'../../../read-plotpickle-project/scripts/story-workflow.py');

test('actual canonical reader verifies an imported, source-linked PPF in Studio',async()=>{
 const dir=await mkdtemp(path.join(os.tmpdir(),'pp-studio-reader-'));
 try {
  const fdx=path.join(dir,'fixture.fdx');
  await writeFile(fdx,'<FinalDraft><Content><Paragraph Type="Scene Heading"><Text>EXT. DOCK - DAY</Text></Paragraph><Paragraph Type="Action"><Text>A character waits beside a lantern.</Text></Paragraph><Paragraph Type="Character"><Text>RIVER</Text></Paragraph><Paragraph Type="Dialogue"><Text>We should begin.</Text></Paragraph></Content></FinalDraft>');
  const out=path.join(dir,'project');
  await exec('python3',[importer,'import-fdx','--file',fdx,'--title','Synthetic integration source','--out',out],{timeout:15000});
  const projectFile=path.join(out,'project.ppf.json');
  const before=await readFile(projectFile);
  const result=await createProjectLoader({projectFile,inspector:reader})();
  assert.equal(result.status,'source-backed',JSON.stringify(result));
  assert.equal(result.readonly,true);
  assert.equal(result.data.readonly,true);
  assert.equal(result.data.source.projectId.length>0,true);
  assert.equal(result.data.source.sha256,sha256(before));
  assert.equal(result.data.scenes.length>=1,true);
  assert.equal('write' in result.data,false);
  assert.equal(sha256(await readFile(projectFile)),sha256(before));
 } finally {await rm(dir,{recursive:true,force:true});}
});
