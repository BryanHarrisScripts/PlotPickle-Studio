#!/usr/bin/env python3
"""Public canonical PlotPickle surface skeleton resolver. No private data or network calls."""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'references/registry.v1.json'
def resolve(surface):
    data=json.loads(R.read_text(encoding='utf-8'))
    sid=data['aliases'].get(surface,surface.upper())
    if sid not in data['surfaces']:
        raise KeyError(f'Unknown surface: {surface}')
    s=data['surfaces'][sid]
    return {'surfaceId':sid,'libraryVersion':data['libraryVersion'],'pluginRelease':data['pluginRelease'],'route':s['route'],'approval':s['approval'],'authority':s['authority'],'order':data['lockedHomeOrder'] if sid=='HOME' else s['children'],'dataSources':s['dataSources'],'template':s['template'],'readOnlyEntry':s['readOnlyEntry'],'privateStoryDataBundled':False}
if __name__=='__main__':
    try:print(json.dumps(resolve(sys.argv[1] if len(sys.argv)>1 else 'HOME'),indent=2))
    except KeyError as e:print(str(e),file=sys.stderr);sys.exit(2)
