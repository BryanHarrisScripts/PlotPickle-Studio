#!/usr/bin/env python3
"""Source-pinned native PPF initial image default Save -> Lock with portable readback.

This changes *saved exported PPF files*, not a running Windows PlotPickle app or ChatGPT Library.
No network, no provider calls, no implicit final creative sign-off.
"""
import argparse, copy, hashlib, importlib.util, io, json, re, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
SAVE='storyboard-local-save:v1'
IMPORTED='story-workflow-image-import:v1'
LEDGER='plotpickle.initial-image-default-lock.v1'
HEX=re.compile(r'^[a-f0-9]{64}$')

def err(msg): raise ValueError(msg)
def stamp(): return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def digest(data): return hashlib.sha256(data).hexdigest()
def native():
    spec=importlib.util.spec_from_file_location('plotpickle_story_workflow',HERE/'story-workflow.py')
    if not spec or not spec.loader:err('canonical story workflow missing')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def store(p):return p['assetRegistry']['extensions']['storyWorkflow']
def akey(addr):
    if not isinstance(addr,dict):err('invalid image address')
    b,m,s=(addr.get(n) for n in ('blockNumber','miniBlockNumber','shotNumber'))
    if any(type(n)!=int for n in (b,m,s)) or not (1<=b<=24 and 1<=m<=4 and 1<=s<=25):err('invalid shot coordinates')
    if addr.get('actNumber')!=(b-1)//6+1 or addr.get('sequenceNumber')!=(b-1)//2+1:err('inconsistent canonical coordinates')
    return f'{b}:{m}:{s}'
def within(r,block,mini,shot=None):
    a=r['address'];akey(a)
    return (block is None or a['blockNumber']==block) and (mini is None or a['miniBlockNumber']==mini) and (shot is None or a['shotNumber']==shot)

def records(p):
    f=p['build']['foundations'];aa=f['visualArtifacts'];accepted=f['acceptedVisualArtifactIds'];maps=store(p)['imageMappings']
    if not all(isinstance(x,list) for x in (aa,accepted,maps)):err('missing native image records')
    arts={x['id']:x for x in aa}
    if len(arts)!=len(aa) or len(set(accepted))!=len(accepted) or not set(accepted)<=set(arts):err('ambiguous native artifact registry')
    index={}
    for r in maps:
        k=akey(r['address'])
        if k in index:err('duplicate candidate at '+k)
        index[k]=r
    return arts,accepted,index

def ledger(p):
    w=store(p);d=w.setdefault('defaultSaveLock',{'schema':LEDGER,'exceptions':{},'autoAccepted':[],'events':[]})
    if d.get('schema')!=LEDGER or not isinstance(d.get('events'),list) or not isinstance(d.get('exceptions'),dict) or not isinstance(d.get('autoAccepted'),list):err('invalid Save/Lock provenance ledger')
    return d

def event(d,action,k,aid,reason=''):
    if len(d['events'])>10000:err('event ledger full')
    d['events'].append({'action':action,'address':k,'artifactId':aid,'at':stamp(),'reason':str(reason)[:200]})

def planned(p,r):
    a=r['address'];b=a['blockNumber'];m=a['miniBlockNumber'];s=a['shotNumber']
    mini=[x for x in store(p).get('plans',[]) if x.get('address',{}).get('blockNumber')==b and x.get('address',{}).get('miniBlockNumber')==m]
    if len(mini)!=1:return False
    shots=[x for x in mini[0].get('shots',[]) if x.get('shotNumber')==s]
    return len(shots)==1 and shots[0].get('state')=='PLANNED'

def linked(a,r):
    addr=r['address'];b=addr['blockNumber'];m=addr['miniBlockNumber'];s=addr['shotNumber']
    keys=a.get('sourceDecisionKeys',[])
    return (a.get('id')==r.get('artifactId') and a.get('workflow')=='storyboard-frame-webp-v2' and a.get('frameNumber')==s
            and isinstance(keys,list) and IMPORTED in keys
            and f'storyboard-anchor:block:block-{b:02}:mini-{m}' in keys
            and f'storyboard-target:block:block-{b:02}' in keys
            and a.get('assetUrl')=='/api/local-ai/assets/'+Path(r.get('portablePath','')).name)

def check_media(root,r):
    rel=r.get('portablePath')
    if not isinstance(rel,str) or '\\' in rel or '\0' in rel:err('unsafe asset path')
    q=Path(rel)
    if q.is_absolute() or len(q.parts)<2 or q.parts[0]!='assets' or any(x in ('.','..') for x in q.parts) or q.suffix.lower() not in ('.webp','.png','.jpeg','.jpg'):
        err('unsafe asset path')
    root=Path(root).resolve();p=(root/q).resolve()
    if root not in p.parents or not p.is_file():err('asset missing or outside project')
    data=p.read_bytes()
    if not data or len(data)>80*1024*1024 or not HEX.fullmatch(str(r.get('sha256',''))) or digest(data)!=r['sha256']:err('media hash mismatch')
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:im.verify()
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            if im.width*im.height>40_000_000:err('oversized image')
    except ImportError:err('Pillow required for image verification')
    except (ValueError,OSError,TypeError) as e:err('media failed decode: '+str(e)[:80])
    return True

def eligible(p,root,b=None,m=None,s=None,allow_replacement=False):
    arts,accepted,maps=records(p);d=ledger(p);picked=[];rejected=[]
    passages={x['id'] for x in p.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])}
    for k,r in sorted(maps.items(),key=lambda item:tuple(map(int,item[0].split(':')))):
        if not within(r,b,m,s):continue
        a=arts.get(r.get('artifactId'))
        why=None
        if not a or not linked(a,r):why='UNVERIFIED_NATIVE_MAPPING'
        elif k in d['exceptions'] and not (allow_replacement and d['exceptions'][k].get('artifactId')!=a['id']):why='EXPLICITLY_UNLOCKED'
        elif not planned(p,r):why='SHOT_NOT_PLANNED'
        elif r.get('savedMarkerPresent') or r.get('locked') or SAVE in a['sourceDecisionKeys'] or a['id'] in accepted or a.get('reviewState')!='draft':why='PREVIOUS_SAVE_OR_REVIEW_DECISION'
        elif r.get('packageBytesVerified') is not True:why='NOT_VERIFIED_GENERATED_IMAGE'
        elif not r.get('passageIds') or any(x not in passages for x in r['passageIds']):why='SOURCE_EVIDENCE_MISSING'
        else:
            try:check_media(root,r)
            except (ValueError,OSError) as e:why='INVALID_MEDIA: '+str(e)
        if why:rejected.append({'address':k,'reason':why})
        else:picked.append((k,a['id']))
    return picked,rejected

def save_then_lock_source(p,picked):
    arts,_,maps=records(p);d=ledger(p)
    for k,aid in picked:
        a=arts[aid];r=maps[k]
        if SAVE not in a['sourceDecisionKeys']:a['sourceDecisionKeys'].append(SAVE)
        r['savedMarkerPresent']=True;r['locked']=False
        event(d,'SAVE',k,aid,'image bytes hash and decode verified')
    p['revision']+=1;p['updatedAt']=stamp()

def lock_saved_source(p,picked,clear_replaced_exceptions=False):
    arts,accepted,maps=records(p);d=ledger(p)
    for k,aid in picked:
        a=arts[aid];r=maps[k]
        if not r.get('savedMarkerPresent') or SAVE not in a['sourceDecisionKeys'] or a.get('reviewState')!='draft':err('Save must precede Lock')
        if aid not in accepted:accepted.append(aid)
        a['reviewState']='accepted';r['locked']=True
        if aid not in d['autoAccepted']:d['autoAccepted'].append(aid)
        if clear_replaced_exceptions and k in d['exceptions']:
            if d['exceptions'][k].get('artifactId')==aid:err('cannot clear exception for same image')
            d['exceptions'].pop(k)
            event(d,'REPLACEMENT_DEFAULT_LOCK',k,aid,'explicitly requested replacement; final human creative approval not implied')
        else:event(d,'DEFAULT_LOCK',k,aid,'initial workflow default; human final creative approval not implied')
    p['revision']+=1;p['updatedAt']=stamp()

def verify(p,root,picked,locked,require_media=True):
    arts,accepted,maps=records(p)
    for k,aid in picked:
        r=maps.get(k);a=arts.get(aid)
        if not a or not r or not linked(a,r):err('native readback mapping mismatch')
        if require_media:check_media(root,r)
        if not r.get('savedMarkerPresent') or SAVE not in a['sourceDecisionKeys']:err('Save not durable in snapshot')
        if bool(r.get('locked'))!=locked or (aid in accepted)!=locked or (a.get('reviewState')=='accepted')!=locked:err('Lock registry mismatch after reopen')


def canonical_readback(wf,ppf_path,identity,picked,locked):
    """Independently re-read the exported native Save/Lock view through the canonical Node reader."""
    positions={tuple(map(int,k.split(':'))) for k,_ in picked}
    for b,m in sorted({(b,m) for b,m,_ in positions}):
        response=wf.call_node('inspect-project.mjs','--file',str(ppf_path),'--operation','shots',
            '--project-id',identity['id'],'--revision',identity['revision'],
            '--sha256',identity['sha256'],'--block',b,'--mini',m)
        shots=response.get('shots',[])
        for block,mini,shot in sorted(positions):
            if block!=b or mini!=m:continue
            row=next((x for x in shots if x.get('address',{}).get('shotNumber')==shot),None)
            aid=next(a for k,a in picked if k==f'{block}:{mini}:{shot}')
            candidates=(row or {}).get('candidates',[])
            item=next((c for c in candidates if c.get('id')==aid),None)
            if not item or item.get('savedMarkerPresent') is not True or item.get('locked') is not locked:
                err('canonical storyboard reader rejected saved/locked state at '+f'{block}:{mini}:{shot}')

def output_snapshot(wf,source,p,target):
    wf.save_snapshot(SimpleNamespace(project=str(source),out=str(target)),p)
def reopen(wf,out):
    path=Path(out)/'project.ppf.json';identity=wf.identity(str(path))
    if identity['sha256']!=digest(path.read_bytes()):err('project hash not confirmed on reopen')
    return wf.read_json(str(path)),identity,path

def audit(p,root,b=None,m=None):
    arts,accepted,maps=records(p);d=ledger(p);wanted=set();gaps=0
    for x in store(p).get('plans',[]):
        addr=x.get('address',{});pb=addr.get('blockNumber');pm=addr.get('miniBlockNumber')
        if (b is not None and b!=pb) or (m is not None and m!=pm):continue
        if type(pb)!=int or type(pm)!=int:continue
        for sh in x.get('shots',[]):
            n=sh.get('shotNumber')
            if type(n)!=int or not 1<=n<=25:continue
            if sh.get('state')=='PLANNED':wanted.add(f'{pb}:{pm}:{n}')
            else:gaps+=1
    issues=[];ready=[]
    for k in sorted(wanted,key=lambda x:tuple(map(int,x.split(':')))):
        r=maps.get(k);a=arts.get(r.get('artifactId')) if r else None
        if not r or not a or not linked(a,r):reason='MISSING_NATIVE_IMAGE'
        elif k in d['exceptions']:reason='SELECTED_FOR_REVISION'
        elif not (r.get('savedMarkerPresent') and r.get('locked') and SAVE in a['sourceDecisionKeys'] and a['id'] in accepted and a.get('reviewState')=='accepted'):reason='NOT_SAVED_AND_LOCKED'
        else:
            try:check_media(root,r);reason=None
            except (ValueError,OSError):reason='MEDIA_CHANGED_OR_MISSING'
        if reason:issues.append({'address':k,'reason':reason})
        else:ready.append(k)
    return {'plannedPositions':len(wanted),'lockedAndVerified':len(ready),'unresolved':issues,'unplannedGaps':gaps,
            'readyForMotionOrPrevis':bool(wanted) and not issues,
            'scope':{'block':b,'mini':m},'humanFinalApprovalImplied':False,'hostLibraryPersistenceVerified':False}

def bulk(wf,args,replace_unlocked=False):
    p,_=wf.pinned(args);root=Path(args.project).resolve().parent
    selected,skipped=eligible(p,root,args.block,args.mini,args.shot,allow_replacement=replace_unlocked)
    if not selected:return {'status':'no-new-images-to-lock','locked':0,'skipped':skipped,'readiness':audit(p,root,args.block,args.mini)}
    with tempfile.TemporaryDirectory(prefix='plotpickle-image-default-lock-') as temp:
        only_saved=Path(temp)/'saved-stage';phase1=copy.deepcopy(p);save_then_lock_source(phase1,selected)
        output_snapshot(wf,args.project,phase1,only_saved)
        checked,saved_ident,saved_path=reopen(wf,only_saved)
        verify(checked,only_saved,selected,False)
        canonical_readback(wf,saved_path,saved_ident,selected,False)
        phase2=copy.deepcopy(checked);lock_saved_source(phase2,selected,clear_replaced_exceptions=replace_unlocked)
        output_snapshot(wf,saved_path,phase2,args.out)
    checked,identity,path=reopen(wf,args.out)
    verify(checked,args.out,selected,True)
    canonical_readback(wf,path,identity,selected,True)
    return {'status':'saved-then-locked-in-export','locked':len(selected),'positions':[x[0] for x in selected],'skipped':skipped,
            'project':identity,'projectPath':str(path),'readiness':audit(checked,args.out,args.block,args.mini),
            'hostLibraryPersistenceVerified':False,'liveWindowsAppUpdated':False}

def change_one(wf,args):
    p,_=wf.pinned(args);root=Path(args.project).resolve().parent;k=f'{args.block}:{args.mini}:{args.shot}'
    arts,accepted,maps=records(p);r=maps.get(k);a=arts.get(r.get('artifactId')) if r else None
    if not a or not linked(a,r):err('no unambiguous mapped image at position')
    if args.operation=='relock':check_media(root,r)
    d=ledger(p)
    if not r.get('savedMarkerPresent') or SAVE not in a['sourceDecisionKeys']:err('cannot lock or unlock an unsaved image')
    if args.operation=='unlock':
        if a.get('reviewState') not in ('draft','accepted'):err('cannot unlock rejected image')
        a['reviewState']='draft';r['locked']=False;accepted[:]=[x for x in accepted if x!=a['id']]
        d['exceptions'][k]={'artifactId':a['id'],'reason':args.reason or 'User selected for revision','at':stamp()}
        event(d,'UNLOCK',k,a['id'],args.reason or 'User selected for revision')
    else:
        if a.get('reviewState') not in ('draft','accepted'):err('cannot lock rejected image')
        a['reviewState']='accepted';r['locked']=True
        if a['id'] not in accepted:accepted.append(a['id'])
        d['exceptions'].pop(k,None);event(d,'USER_RELOCK',k,a['id'],'explicitly requested')
    p['revision']+=1;p['updatedAt']=stamp();output_snapshot(wf,args.project,p,args.out)
    checked,identity,path=reopen(wf,args.out)
    verify(checked,args.out,[(k,a['id'])],args.operation=='relock',require_media=args.operation=='relock')
    canonical_readback(wf,path,identity,[(k,a['id'])],args.operation=='relock')
    return {'status':args.operation+'-committed','project':identity,'projectPath':str(path),
            'readiness':audit(checked,args.out,args.block,args.mini),'hostLibraryPersistenceVerified':False}

def args_parser(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='operation',required=True)
    for cmd in ('auto','audit','unlock','relock','attach-initial','replace-unlocked'):
        p=sub.add_parser(cmd)
        for k in ('project','project-id','sha256'):p.add_argument('--'+k,required=True)
        p.add_argument('--revision',required=True,type=int)
        if cmd!='audit':p.add_argument('--out',required=True)
        p.add_argument('--block',type=int,required=cmd in ('unlock','relock','attach-initial','replace-unlocked'))
        p.add_argument('--mini',type=int,required=cmd in ('unlock','relock','attach-initial','replace-unlocked'))
        if cmd!='audit':p.add_argument('--shot',type=int,required=cmd in ('unlock','relock','attach-initial','replace-unlocked'))
        if cmd=='unlock':p.add_argument('--reason')
        if cmd in ('attach-initial','replace-unlocked'):p.add_argument('--image',required=True);p.add_argument('--provider',required=True);p.add_argument('--model')
    return ap.parse_args(argv)

def main(argv=None):
    try:
        a=args_parser(argv)
        if a.shot and (a.block is None or a.mini is None):err('shot requires block and mini')
        wf=native()
        if a.operation=='audit':
            p,_=wf.pinned(a);result={'status':'read-only','readiness':audit(p,Path(a.project).resolve().parent,a.block,a.mini)}
        elif a.operation=='auto':result=bulk(wf,a)
        elif a.operation in ('unlock','relock'):result=change_one(wf,a)
        else:
            if a.operation=='replace-unlocked':
                project,_=wf.pinned(a)
                k=f'{a.block}:{a.mini}:{a.shot}'
                _,_,mapped=records(project)
                old=mapped.get(k)
                exception=ledger(project)['exceptions'].get(k)
                if not old or not exception or old.get('artifactId')!=exception.get('artifactId'):
                    err('replacement requires a currently unlocked, explicitly selected image')
            with tempfile.TemporaryDirectory(prefix='plotpickle-new-shot-') as tmp:
                stage=Path(tmp)/'attached'
                wf.attach(SimpleNamespace(**vars(a),out=str(stage),replace=a.operation=='replace-unlocked'))
                old=stage/'project.ppf.json';i=wf.identity(str(old))
                next_a=SimpleNamespace(project=str(old),project_id=i['id'],revision=i['revision'],sha256=i['sha256'],
                     out=a.out,block=a.block,mini=a.mini,shot=a.shot)
                result=bulk(wf,next_a,replace_unlocked=a.operation=='replace-unlocked')
                if result['locked']!=1:err('new image did not pass Save then Lock validation')
        print(json.dumps(result,indent=2,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError,ImportError) as e:
        print(json.dumps({'status':'failed-closed','error':str(e)[:350]}),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
