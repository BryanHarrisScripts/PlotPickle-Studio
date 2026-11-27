#!/usr/bin/env python3
"""Native, reversible two-phase Save then Lock of creator-approved design references.

Changes a NEW PPF project snapshot; doesn't edit the original, rewrite a screenplay,
change any storyboard shot/mapping/lock, or install a plugin. Requires real bytes.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

SCHEMA = 'plotpickle.approved-design-references.v1'
HEX = re.compile(r'^[0-9a-f]{64}$')
ID = re.compile(r'^[a-z0-9][a-z0-9-]{1,70}$')

def fail(s): raise ValueError(s)
def digest(b): return hashlib.sha256(b).hexdigest()
def stamp(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def write_new(p,obj):
    if p.exists(): fail('output already exists: '+str(p))
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def read_file(p):
    data=Path(p).read_bytes()
    if not data or len(data)>20*1024*1024:fail('invalid/oversize PPF')
    return json.loads(data),digest(data)
def check_image(p):
    p=Path(p)
    if not p.is_file() or p.is_symlink():fail('missing/unsafe image: '+str(p))
    if p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):fail('unsupported image format')
    data=p.read_bytes()
    if not data or len(data)>50*1024*1024:fail('invalid image size')
    with Image.open(p) as im:
        im.verify()
    with Image.open(p) as im:
        im.load()
        if im.width*im.height>40_000_000:fail('image too large')
        mime=Image.MIME.get(im.format)
        if not mime or p.suffix.lower().lstrip('.') not in mime.split('/')[-1].replace('jpeg','jpg jpeg').split():
            fail('image type mismatch')
        width,height=im.size
    return {'sha256':digest(data),'bytes':len(data),'width':width,'height':height,'mimeType':mime}
def canonical_reader(project,reader):
    if not reader:fail('canonical reader path required for independent verification')
    proc=subprocess.run(['node',str(reader),'--file',str(project),'--operation','identity'],capture_output=True,text=True,timeout=40)
    if proc.returncode:fail('canonical project reader rejected snapshot: '+(proc.stdout or proc.stderr)[:250])
    val=json.loads(proc.stdout)
    if val.get('operation')!='identity' or val.get('project',{}).get('sha256')!=digest(Path(project).read_bytes()):fail('canonical identity mismatch')
    return val['project']

def register(project_path,reader_path,manifest_path,out_dir,expected_id,expected_rev,expected_sha):
    project_path=Path(project_path).resolve(strict=True)
    original,sha=read_file(project_path)
    if (sha,original.get('id'),original.get('revision'))!=(expected_sha,expected_id,expected_rev):fail('STALE_PROJECT')
    if canonical_reader(project_path,reader_path)['id']!=expected_id:fail('canonical source mismatch')
    manifest=json.loads(Path(manifest_path).read_text())
    refs=manifest.get('references')
    if not isinstance(refs,list) or not 1<=len(refs)<=10:fail('1..10 reference images required')
    if manifest.get('creatorApproval')!='explicit-user-approval':fail('explicit user approval required')
    seen=set();prepared=[]
    existing={a.get('id') for a in original.get('assetRegistry',{}).get('assets',[]) if isinstance(a,dict)}
    for x in refs:
        key=x.get('id','');kind=x.get('kind')
        if not ID.fullmatch(key) or key in seen or kind not in ('character','world'):fail('invalid/duplicate design reference ID')
        if 'design-reference-'+key in existing:fail('reference already registered')
        seen.add(key)
        src=Path(x['image']).resolve(strict=True)
        data=check_image(src)
        ext=src.suffix.lower();target=f'assets/design-reference-{key}-{data["sha256"][:16]}{ext}'
        prepared.append((x,src,data,target))
    out_dir=Path(out_dir)
    if out_dir.exists():fail('output directory exists')
    source_assets=project_path.parent/'assets'
    if not source_assets.is_dir():fail('source project portable assets missing')
    provenance={'schema':SCHEMA,'sourceProject':{'id':expected_id,'revision':expected_rev,'sha256':sha},
                'approvalSource':'creator-approved-in-chat','references':[]}
    current=copy.deepcopy(original)
    reg=current['assetRegistry']; design=reg.setdefault('extensions',{}).setdefault('approvedDesignReferences',{'schema':SCHEMA,'records':[]})
    if design.get('schema')!=SCHEMA or not isinstance(design.get('records'),list):fail('invalid existing design reference extension')
    for x,src,data,target in prepared:
        key=x['id']; now=stamp()
        base='design-reference-'+key;vid='variation-'+base
        d={'id':base,'kind':'image','label':x.get('label') or key,'targets':[{'kind':'other','id':x['kind']+':'+key}],
           'variations':[{'id':vid,'source':target,'portablePath':target,'contentHash':'sha256:'+data['sha256'],
                         'mediaType':data['mimeType'],'bytes':data['bytes'],'provider':'ChatGPT author-approved reference',
                         'approval':'approved','provenanceIds':x.get('sourcePassageIds',[]),
                         'extensions':{'designRole':x['kind'],'sourceProjectRevision':expected_rev,'approvalSource':'explicit-user-approval'}}],
           'approvedVariationId':vid,'createdAt':now,'updatedAt':now,
           'extensions':{'designReference':True,'kind':x['kind'],'subjectId':x.get('subjectId',key)}}
        reg['assets'].append(d)
        design['records'].append({'id':key,'kind':x['kind'],'assetId':base,'portablePath':target,'sha256':data['sha256'],
                                  'creatorApproved':True,'savedMarkerPresent':True,'locked':False,'sourcePassageIds':x.get('sourcePassageIds',[]),
                                  'approvalScope':'visual-reference-only-not-storyboard-shot'})
        provenance['references'].append({'id':key,'kind':x['kind'],'imageSha256':data['sha256'],'bytes':data['bytes']})
    current['revision']+=1;current['updatedAt']=stamp()
    with tempfile.TemporaryDirectory(prefix='plotpickle-design-save-lock-') as t:
        stage=Path(t)/'saved';stage.mkdir();shutil.copytree(source_assets,stage/'assets')
        for x,src,data,target in prepared:
            dest=stage/target
            if dest.exists():fail('ref path collision')
            shutil.copyfile(src,dest)
        savep=stage/'project.ppf.json';write_new(savep,current)
        check=canonical_reader(savep,reader_path)
        if check['revision']!=expected_rev+1:fail('save-stage revision mismatch')
        for _,_,data,target in prepared:
            if check_image(stage/target)!=data:fail('save-stage image mismatch')
        got=json.loads(savep.read_text())
        for r in got['assetRegistry']['extensions']['approvedDesignReferences']['records']:
            if r['id'] in seen:
                if not r['savedMarkerPresent'] or r['locked']:fail('invalid Save stage')
                r['locked']=True
        got['revision']+=1;got['updatedAt']=stamp()
        # No changes to existing shot data, screenplay, or build approval ledger.
        for key in ('sourceEvidence','build','production','structure'):
            if got.get(key)!=original.get(key):fail('unrelated '+key+' changed')
        before=original['assetRegistry']['extensions'].get('storyWorkflow')
        after=got['assetRegistry']['extensions'].get('storyWorkflow')
        if before!=after or got['assetRegistry']['assets'][:len(original['assetRegistry']['assets'])]!=original['assetRegistry']['assets']:
            fail('unrelated asset or shot records changed')
        out_dir.mkdir(parents=True)
        try:
            shutil.copytree(stage/'assets',out_dir/'assets')
            final=out_dir/'project.ppf.json';write_new(final,got)
            final_id=canonical_reader(final,reader_path)
            if final_id['revision']!=expected_rev+2:fail('lock-stage revision mismatch')
            reopened=json.loads(final.read_bytes())
            for rec in reopened['assetRegistry']['extensions']['approvedDesignReferences']['records']:
                if rec['id'] in seen:
                    if not rec['savedMarkerPresent'] or not rec['locked']:fail('missing native reference lock')
                    found=check_image(out_dir/rec['portablePath'])
                    if found['sha256']!=rec['sha256']:fail('media SHA changed on reopen')
            provenance['resultProject']=final_id
            provenance['verifiedReferenceCount']=len(prepared)
            provenance['sourceUnchanged']=digest(project_path.read_bytes())==sha
            provenance['unrelatedShotRecordsUnchanged']=True
            provenance['hostLibraryPersistenceVerified']=False
            write_new(out_dir/'design-reference-approval-receipt.json',provenance)
        except:
            shutil.rmtree(out_dir,ignore_errors=True)
            raise
    return provenance

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--reader',required=True)
    ap.add_argument('--manifest',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--project-id',required=True);ap.add_argument('--revision',required=True,type=int);ap.add_argument('--sha256',required=True)
    args=ap.parse_args()
    try:
        result=register(args.project,args.reader,args.manifest,args.out,args.project_id,args.revision,args.sha256)
        print(json.dumps(result,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError,RuntimeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'status':'failed-closed','error':str(e)[:300]}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
