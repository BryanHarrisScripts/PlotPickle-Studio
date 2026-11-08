#!/usr/bin/env python3
"""Read-only inventory with optional SHA-256 validation of supplied media."""
import argparse,hashlib,json,pathlib,re,sys
CATEGORIES=('Characters','World','Collectibles','Posters','Sounds / Foley','Sounds / Narration','Sounds / Music','Storyboard Images','Motion Clips','Unclassified')
def classify(asset):
    label=str(asset.get('label','')).lower();kind=str(asset.get('kind','')).lower(); targets=asset.get('targets') or []
    if any(isinstance(t,dict) and t.get('kind')=='storyboard-frame' for t in targets):return 'Storyboard Images'
    for word,cat in [('poster','Posters'),('character','Characters'),('world','World'),('location','World'),('collectible','Collectibles'),('foley','Sounds / Foley'),('narration','Sounds / Narration'),('music','Sounds / Music')]:
        if word in kind or word in label:return cat
    if kind in ('video','motion','clip'):return 'Motion Clips'
    return 'Unclassified'
def verify_path(root,path,declared):
    if root is None:return 'not-supplied'
    if not isinstance(path,str) or not path:return 'no-path'
    rel=pathlib.PurePosixPath(path)
    if rel.is_absolute() or '..' in rel.parts or '\\' in path:return 'unsafe-path'
    root=root.resolve();location=(root/path).resolve()
    if not location.is_relative_to(root):return 'unsafe-path'
    if not location.is_file():return 'missing'
    if not isinstance(declared,str) or not re.fullmatch(r'(sha256:)?[0-9a-fA-F]{64}',declared):return 'bytes-present-hash-unrecorded'
    actual=hashlib.sha256(location.read_bytes()).hexdigest()
    return 'hash-verified' if actual==declared.lower().removeprefix('sha256:') else 'hash-mismatch'
def inventory(p,sha,root):
    if not isinstance(p,dict) or not p.get('id') or not isinstance(p.get('revision'),int):raise ValueError('PPF identity missing')
    ar=p.get('assetRegistry') or {}; accepted=set(((p.get('build') or {}).get('foundations') or {}).get('acceptedVisualArtifactIds') or [])
    mappings=((ar.get('extensions') or {}).get('storyWorkflow') or {}).get('imageMappings') or []
    byartifact={x.get('artifactId'):x for x in mappings if isinstance(x,dict)}
    grouped={name:[] for name in CATEGORIES}
    for a in ar.get('assets',[]) or []:
        if not isinstance(a,dict):continue
        variants=[]
        for v in a.get('variations',[]) or []:
            if not isinstance(v,dict):continue
            artifact=str(v.get('id') or '').removeprefix('variation-')
            m=byartifact.get(artifact) or {}
            variants.append({'id':v.get('id'),'path':v.get('portablePath'),'source':v.get('source'),
              'mediaVerification':verify_path(root,v.get('portablePath'),v.get('contentHash') or v.get('sha256')),
              'declaredSaved':m.get('savedMarkerPresent') if m else None,
              'declaredLocked':m.get('locked') if m else None,
              'acceptedArtifactIdRecorded':artifact in accepted,
              'approval':v.get('approval','unknown'),'sourcePassageIds':v.get('provenanceIds') or []})
        key=classify(a);grouped[key].append({'id':a.get('id'),'label':a.get('label'),'kind':a.get('kind'),'variations':variants})
    return {'schema':'plotpickle.assets.inventory.v1','project':{'id':p['id'],'revision':p['revision'],'sha256':sha},
       'categories':grouped,'summary':{'recordedAssetCount':sum(len(a) for a in grouped.values()),'suppliedAssetsRoot':bool(root)},
       'notice':'Empty groups are valid. Recorded media paths and approvals are not file bytes, Save/Lock, or live integrations.'}
def main():
    a=argparse.ArgumentParser();a.add_argument('--project',type=pathlib.Path,required=True);a.add_argument('--assets-root',type=pathlib.Path);a.add_argument('--format',choices=['json','markdown'],default='json');a.add_argument('--out',type=pathlib.Path);v=a.parse_args()
    raw=v.project.read_bytes();p=json.loads(raw);data=inventory(p,hashlib.sha256(raw).hexdigest(),v.assets_root)
    if v.format=='json':out=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
    else:
        out='# PlotPickle Assets\nSource SHA-256: '+data['project']['sha256']+'\n'
        for cat,items in data['categories'].items():
            out+=f'\n## {cat} ({len(items)})\n'
            for item in items:out+=f"- {item['label'] or item['id']}: "+', '.join(str(x['mediaVerification']) for x in item['variations'])+'\n'
    if v.out:
        with v.out.open('x',encoding='utf-8') as f:f.write(out)
    else:sys.stdout.write(out)
if __name__=='__main__':main()
