#!/usr/bin/env python3
"""Source-pinned fal motion brief builder. Offline, no provider/network/credits/project edits."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = 'plotpickle.fal-motion-brief.v1'

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def checked_int(val, lo, hi, name):
    if type(val) is not int or not lo <= val <= hi:
        raise ValueError(f'{name} must be {lo}..{hi}')
    return val

def address(block, mini, shot):
    return {'actNumber': (block - 1) // 6 + 1,
            'sequenceNumber': (block - 1) // 2 + 1,
            'blockNumber': block, 'miniBlockNumber': mini, 'shotNumber': shot}

def media_check(variation, root):
    path = variation.get('portablePath')
    expected = variation.get('contentHash')
    if not isinstance(path, str) or not path or not isinstance(expected, str) or not expected.startswith('sha256:'):
        return {'state': 'metadata-incomplete', 'bytesVerified': False}
    norm = Path(path)
    if norm.is_absolute() or '..' in norm.parts or norm.parts[0] != 'assets':
        return {'state': 'unsafe-asset-path', 'bytesVerified': False}
    if root is None:
        return {'state': 'media-not-supplied', 'portablePath': path, 'expectedSha256': expected, 'bytesVerified': False}
    real_root = Path(root).resolve()
    target = (real_root / norm).resolve()
    if not target.is_relative_to(real_root):
        return {'state': 'unsafe-asset-path', 'bytesVerified': False}
    if not target.is_file():
        return {'state': 'media-missing', 'portablePath': path, 'bytesVerified': False}
    blob = target.read_bytes()
    if 'sha256:' + digest(blob) != expected:
        return {'state': 'hash-mismatch', 'portablePath': path, 'bytesVerified': False}
    try:
        from PIL import Image
        with Image.open(target) as im:
            im.verify()
        decode = 'verified-by-pillow'
    except ImportError:
        decode = 'not-verified-no-decoder'
    except Exception:
        return {'state': 'image-decode-failed', 'portablePath': path, 'bytesVerified': False}
    return {'state':'bytes-hash-verified', 'portablePath':path,'sha256':digest(blob), 'sizeBytes':len(blob), 'imageDecode':decode,'bytesVerified':True}

def prepare(project_bytes, block, mini, start_shot, end_shot, motion_cue, assets_root=None):
    block=checked_int(block,1,24,'block')
    mini=checked_int(mini,1,4,'mini')
    start_shot=checked_int(start_shot,1,25,'start-shot')
    end_shot=checked_int(end_shot,start_shot,min(25,start_shot+4),'end-shot')
    if not isinstance(motion_cue,str) or len(motion_cue.strip())<12 or len(motion_cue)>3000:
        raise ValueError('Provide a bounded director motion cue (12–3000 characters)')
    project = json.loads(project_bytes)
    ident = {'id':project.get('id'), 'revision':project.get('revision'),'sha256':digest(project_bytes), 'title':project.get('title')}
    if not isinstance(ident['id'],str) or not ident['id'] or type(ident['revision']) is not int:
        raise ValueError('Missing project ID or numeric revision')
    assets=project.get('assetRegistry',{}).get('assets',[])
    if not isinstance(assets,list):
        raise ValueError('Invalid asset registry')
    pass_map={p.get('id'):p for p in project.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[]) if isinstance(p,dict)}
    positions=[]
    for sn in range(start_shot,end_shot+1):
        addr=address(block,mini,sn)
        options=[]
        for a in assets:
            if not isinstance(a,dict):continue
            for var in a.get('variations',[]):
                if isinstance(var,dict) and var.get('extensions',{}).get('storyboardAddress')==addr:
                    options.append((a,var))
        if len(options)>1: raise ValueError(f'Ambiguous candidate for shot {sn}; resolve project mapping first')
        row={'address':addr,'storyboardPosition':sn,'media':{'state':'not-recorded','bytesVerified':False},'saved':False,'locked':False,'visuallyApproved':False,'passageIds':[]}
        if options:
            a,v=options[0]
            row['assetId']=a.get('id')
            row['variationId']=v.get('id')
            row['passageIds']=v.get('provenanceIds') or []
            # The asset registry's approval only reflects a variation choice; no automatic Save/Lock.
            row['visuallyApproved']=bool(a.get('approvedVariationId') and a.get('approvedVariationId')==v.get('id'))
            row['media']=media_check(v,assets_root)
            row['promptProvenance']='reconstructed' if v.get('extensions',{}).get('promptOrigin')=='reconstructed' else 'source-recorded'
            row['passageEvidenceVerified']=bool(row['passageIds']) and all(pid in pass_map for pid in row['passageIds'])
        positions.append(row)
    media_valid=all(row['media']['bytesVerified'] for row in positions)
    approval=all(row['visuallyApproved'] for row in positions)
    screenplay_valid=all(row.get('passageEvidenceVerified') is True for row in positions)
    # Native Save/Lock is NOT proven from asset-variation metadata.
    # This helper cannot certify native Save/Lock. Even approved variations remain blocked.
    status=('blocked-media-unverified' if not media_valid else
            'blocked-source-evidence' if not screenplay_valid else
            'blocked-review-save-lock')
    return {'schema':SCHEMA,'status':status,'project':ident,'provider':'fal','modelSelection':'pending-connected-model-discovery',
            'requestedOutput':'image-to-video','editorial':{'fps':24,'framesPerPosition':72,'positionCount':len(positions),'framesTotal':72*len(positions),'secondsTotal':3*len(positions)},
            'motionCue':motion_cue.strip(),'positions':positions,
            'generationReadiness':{'allMediaHashesVerified':media_valid,'allSourcePassagesVerified':screenplay_valid,'allVisualChoicesApproved':approval,'nativeSaveLockVerified':False,
                                   'providerModelDurationSupported':False,'connectedAccountVerified':False,'currentCostQuoted':False,'jobApprovalObtained':False},
            'generationSubmitted':False,'costApproved':False,'providerAccountVerified':False,'videoBytesVerified':False,'mediaImported':False,'projectModified':False,
            'nextAction':'Review source images and Save/Lock, then inspect connected fal model capabilities and actual per-job quote; generation requires explicit approval.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--block',type=int,required=True)
    p.add_argument('--mini',type=int,required=True)
    p.add_argument('--start-shot',type=int,required=True)
    p.add_argument('--end-shot',type=int,required=True)
    p.add_argument('--motion-cue',required=True)
    p.add_argument('--assets-root',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.out.exists():raise ValueError('Refuse overwrite')
        before=a.project.read_bytes()
        out=prepare(before,a.block,a.mini,a.start_shot,a.end_shot,a.motion_cue,a.assets_root)
        if a.project.read_bytes()!=before:raise ValueError('Source project changed during plan')
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        print(json.dumps({'status':out['status'],'output':str(a.out),'submitted':False,'creditsSpent':False}))
        return 0
    except (ValueError,TypeError,KeyError,OSError,json.JSONDecodeError) as e:
        print(json.dumps({'status':'fail-closed','error':str(e)}))
        return 2
if __name__=='__main__':raise SystemExit(main())
