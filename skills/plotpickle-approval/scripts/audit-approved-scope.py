#!/usr/bin/env python3
"""Independent no-write readback of scoped PlotPickle native PPF Save/Lock and design references.

Never infer native locks from an approved composite page or conversation statement.
"""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,os,re,sys
SAVE='storyboard-local-save:v1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate_file(root,relative,expected):
    if not isinstance(relative,str) or not relative.startswith('assets/') or '..' in Path(relative).parts or '\\' in relative or Path(relative).is_absolute():
        return 'UNSAFE_ASSET_PATH'
    root=Path(root).resolve();file=(root/relative).resolve()
    if not file.is_relative_to(root) or not file.is_file():return 'MEDIA_NOT_PRESENT'
    try:
        if sha(file)!=expected:return 'MEDIA_HASH_MISMATCH'
        with Image.open(file) as im: im.verify()
        with Image.open(file) as im:im.load()
    except Exception:return 'MEDIA_DECODE_FAILED'
    return 'MEDIA_HASH_AND_DECODE_VERIFIED'

def audit(ppf,scopes=((1,1),(2,1))):
    ppf=Path(ppf)
    data=ppf.read_bytes();p=json.loads(data)
    if not p.get('id') or type(p.get('revision')) is not int:raise ValueError('INVALID_PPF')
    assets=p.get('assetRegistry',{})
    w=assets.get('extensions',{}).get('storyWorkflow',{})
    maps=w.get('imageMappings',[]);plans=w.get('plans',[])
    foundation=p.get('build',{}).get('foundations',{})
    arts={x.get('id'):x for x in foundation.get('visualArtifacts',[])}
    accepted=set(foundation.get('acceptedVisualArtifactIds',[]));result=[]
    for b,m in scopes:
        recs={r['address']['shotNumber']:r for r in maps if r.get('address',{}).get('blockNumber')==b and r.get('address',{}).get('miniBlockNumber')==m}
        plan=[x for x in plans if x.get('address',{}).get('blockNumber')==b and x.get('address',{}).get('miniBlockNumber')==m]
        stages=[]
        for shot in range(1,26):
            r=recs.get(shot);a=arts.get(r.get('artifactId')) if r else None
            if not r or not a:status='UNREGISTERED_NATIVE_SHOT'
            elif not r.get('savedMarkerPresent') or not r.get('locked') or SAVE not in a.get('sourceDecisionKeys',[]) or a['id'] not in accepted or a.get('reviewState')!='accepted':
                status='NOT_SAVED_AND_LOCKED'
            else:status=validate_file(ppf.parent,r.get('portablePath'),r.get('sha256'))
            stages.append({'shot':shot,'status':status})
        n=sum(x['status']=='MEDIA_HASH_AND_DECODE_VERIFIED' for x in stages)
        result.append({'block':b,'miniBlock':m,'registeredShotMappings':len(recs),'nativePlanExists':len(plan)==1,
                       'verifiedSavedAndLocked':n,'expected':25,'unresolved':[x for x in stages if x['status']!='MEDIA_HASH_AND_DECODE_VERIFIED']})
    design=assets.get('extensions',{}).get('approvedDesignReferences',{}).get('records',[])
    dr=[]
    for x in design:
        locked=x.get('locked') is True and x.get('savedMarkerPresent') is True and x.get('creatorApproved') is True
        status=validate_file(ppf.parent,x.get('portablePath'),x.get('sha256')) if locked else 'REFERENCE_NOT_SAVED_AND_LOCKED'
        dr.append({'id':x.get('id'),'status':status,'locked':locked})
    n=sum(x['verifiedSavedAndLocked'] for x in result)
    return {'schema':'plotpickle.approval-scope-audit.v1','project':{'id':p['id'],'revision':p['revision'],'sha256':hashlib.sha256(data).hexdigest()},
            'nativeShotTargetCount':25*len(result),'verifiedSavedAndLockedShots':n,
            'scopes':result,'designReferences':dr,'designReferencesVerifiedLocked':sum(x['status']=='MEDIA_HASH_AND_DECODE_VERIFIED' for x in dr),
            'complete':n==25*len(result),'originalProjectWritten':False,
            'warning':'Approved page composites are not native individual shot locks. Host Library persistence must be checked separately.'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--project',required=True);a.add_argument('--out',required=True)
    v=a.parse_args();out=Path(v.out)
    if out.exists():raise SystemExit('Refusing overwrite')
    r=audit(v.project)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'verified':r['verifiedSavedAndLockedShots'],'target':r['nativeShotTargetCount'],
                      'references':r['designReferencesVerifiedLocked'],'complete':r['complete'],'out':str(out)}))
if __name__=='__main__':main()
