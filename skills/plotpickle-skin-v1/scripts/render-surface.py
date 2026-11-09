#!/usr/bin/env python3
"""Return permanent Skin V1 section and controls specification, no user data/writes."""
import argparse,json
from pathlib import Path

def surface(name):
    d=json.loads((Path(__file__).resolve().parents[1]/'references/skin-v1.json').read_text())
    if name not in d['approvedSurfaces'] and name not in d.get('approvedNestedLayouts',[]):
        raise ValueError(f'unapproved Skin V1 surface: {name}')
    return {'schema':'plotpickle.skin.v1.view-contract','skin':d['skinVersion'],
            'surface':name,'shell':d['shell'],'tokens':{'colors':d['colors'],'spacing':d['spacing'],'typography':d['typography']},
            'layout':d['fixedSurfaceLayouts'][name],
            'nestedApproval':name in d.get('approvedNestedLayouts',[]),
            'readOnlyProjection':True,'sourceData':'MUST be supplied by verified authorized PPF/Library; NOT embedded'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--surface',required=True)
    args=p.parse_args()
    print(json.dumps(surface(args.surface),ensure_ascii=False,indent=2))
