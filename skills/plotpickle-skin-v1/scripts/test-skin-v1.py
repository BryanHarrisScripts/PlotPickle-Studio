#!/usr/bin/env python3
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from importlib.machinery import SourceFileLoader
view=SourceFileLoader('skin_render',str(Path(__file__).resolve().parent/'render-surface.py')).load_module()
d=json.loads((Path(__file__).resolve().parents[1]/'references/skin-v1.json').read_text())
assert d['approvedSurfaces']==['HOME','STORYBOARD','STORY_MAP','MINI_BLOCK_SHOT_GRID','IMAGE_REVIEW']
assert [c['title'] for c in d['fixedSurfaceLayouts']['HOME']['primaryCards']]==['Meet Elara','Learn','Storyboard','Connected Services']
assert [p['id'] for p in d['fixedSurfaceLayouts']['STORYBOARD']['paths']]==['REEL','ONCE']
assert d['fixedSurfaceLayouts']['STORY_MAP']['acts']==4
assert d['fixedSurfaceLayouts']['STORY_MAP']['blocksTotal']==24
assert d['fixedSurfaceLayouts']['MINI_BLOCK_SHOT_GRID']['shotGrid']=={'rows':5,'columns':5}
assert d['fixedSurfaceLayouts']['IMAGE_REVIEW']['statusRows']==['Human Approved','PPF Saved','PPF Locked','Media Verified']
assert 'PRODUCTION_HANDOFF' not in d['approvedSurfaces']
assert d['pluginRelease']=='0.8.38'
assert d['approvedNestedLayouts']==['REEL_WORKSPACE_ENTRY','MOBILE_STORYBOARD_REVIEW']
reel=d['fixedSurfaceLayouts']['REEL_WORKSPACE_ENTRY']
assert [c['title'] for c in reel['startingOptions']]==['New Idea','Import Script','Continue Film','Explore Tools']
mobile=d['fixedSurfaceLayouts']['MOBILE_STORYBOARD_REVIEW']
assert mobile['shotGrid']['rows']*mobile['shotGrid']['columns']==25 and mobile['miniBlockSelectors']==4
assert mobile['statusRows']==['Human Approved','PPF Saved','PPF Locked','Media Verified']
assert mobile['persistentHostedSidebar'] is False
assert d['graphicNovelReadingFormat']['positionCoverage']==[[1,5],[6,10],[11,15],[16,20],[21,25]]
assert d['graphicNovelReadingFormat']['plannedPagesForFullScaffold']==480
for n in d['approvedNestedLayouts']:
    view.surface(n)
for n in d['approvedSurfaces']:
 a=view.surface(n); b=view.surface(n); assert a==b and a['readOnlyProjection']
try: view.surface('PRODUCTION_HANDOFF')
except ValueError: pass
else: raise AssertionError('unapproved surface must be refused')
print('PASS: 5 primary + 2 nested approved view contracts; six original surface statuses retained; mobile 25 shot grid; five-page reading; unapproved gated')
