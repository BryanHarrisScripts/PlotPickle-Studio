#!/usr/bin/env python3
"""Read-only, source-fingerprinted PlotPickle reports. Does not open service connections."""
import argparse, collections, hashlib, json, pathlib, re, sys
SECTIONS=('project','story','characters','scenes','dialogue','production','feedback','connections')

def load(path):
    raw=path.read_bytes(); p=json.loads(raw)
    if not isinstance(p,dict) or not isinstance(p.get('id'),str) or not isinstance(p.get('revision'),int):
        raise ValueError('PPF identity/revision missing')
    return p,hashlib.sha256(raw).hexdigest()

def group(p):
    source=p.get('sourceEvidence') or {}; screenplay=source.get('screenplay') or {}
    return [x for x in screenplay.get('passages',[]) if isinstance(x,dict)]

def report(project,source_name='project.ppf.json',sha=''):
    p=project; passages=group(p); wf=((p.get('assetRegistry') or {}).get('extensions') or {}).get('storyWorkflow') or {}
    nav=((p.get('assetRegistry') or {}).get('extensions') or {}).get('storyNavigator') or {}
    mapped=[v for v in wf.get('imageMappings',[]) if isinstance(v,dict)]
    acts=nav.get('acts',[]) or []; sequences=nav.get('sequences',[]) or []; blocks=nav.get('blocks',[]) or []
    scenes=[]; speakers=collections.defaultdict(lambda:{'cues':0,'words':0,'passageIds':[]})
    last_id=None
    for i,x in enumerate(passages):
        t=str(x.get('type','')).lower(); text=str(x.get('text') or '')
        if t in ('scene-heading','scene_heading','scene heading'):
            scenes.append({'id':x.get('sceneId') or x.get('id'), 'heading':text, 'passageId':x.get('id'), 'blockNumber':x.get('blockNumber')})
        if t in ('character','character-cue','character cue'):
            who=text.strip().upper();last_id=who or None
        elif t in ('dialogue','parenthetical') and last_id and t=='dialogue':
            d=speakers[last_id];d['cues']+=1;d['words']+=len(re.findall(r"\b[\w'-]+\b",text));d['passageIds'].append(x.get('id'))
        elif t not in ('parenthetical',):last_id=None
    assets=(p.get('assetRegistry') or {}).get('assets',[]) or []
    raw_feedback=((p.get('review') or {}).get('threads') or [])
    if not isinstance(raw_feedback,list):raw_feedback=[]
    locked=sum(bool(x.get('locked')) for x in mapped)
    saved=sum(bool(x.get('savedMarkerPresent')) for x in mapped)
    accepted=(p.get('build') or {}).get('foundations',{}).get('acceptedVisualArtifactIds') or []
    info={'projectId':p['id'],'revision':p['revision'],'sha256':sha,'sourceFile':source_name,
          'status':'source-pinned-read-only-report','unverifiedFieldsAreNotZero':True}
    sections={
      'project':{'title':p.get('title') or (p.get('metadata') or {}).get('title') or 'Untitled',
                 'screenplaySource':(p.get('sourceEvidence') or {}).get('screenplay',{}).get('sourceFileName'),
                 'recordedPassages':len(passages),'recordedScenes':len(scenes),'recordedAssetEntries':len(assets),'revision':p['revision']},
      'story':{'recordedActs':len(acts),'recordedSequences':len(sequences),'recordedBlocks':len(blocks),
               'canonicalPlannedActs':4,'canonicalPlannedSequences':12,'canonicalPlannedBlocks':24,
               'canonicalPlannedMiniBlocks':96,'canonicalPlannedShotPositions':2400,
               'mappedImagePositions':len(mapped),'planningVsActual':'Planning capacity does not prove authored or verified coverage.'},
      'characters':{'sourceDialogueCues':{k:v for k,v in sorted(speakers.items())},
                    'note':'Cue counting from source; absent character metadata and estimated speaking duration are not inferred.'},
      'scenes':{'items':scenes,'count':len(scenes)},
      'dialogue':{'recordedDialogueCues':sum(v['cues'] for v in speakers.values()),
                  'recordedDialogueWords':sum(v['words'] for v in speakers.values()),
                  'note':'Counts are approximate text tokenization; no spoken seconds inferred.'},
      'production':{'mappedImagePositions':len(mapped),'declaredSaved':saved,'declaredLocked':locked,
                    'declaredAcceptedVisualArtifactIds':len(accepted),'verifiedMediaBytes':None,
                    'shootingSchedule':'not verified','note':'Save, Lock, accepted and actual media bytes are separate truths.'},
      'feedback':{'recordedReviewThreads':len(raw_feedback),'note':'No threads recorded does not mean approval.'},
      'connections':{'status':'not checked','note':'Requires fresh authorized reads for every service; static project metadata is not evidence of connectivity.'}
    }
    return {'schema':'plotpickle.reports.snapshot.v1','source':info,'sections':sections}

def markdown(r,section):
    out=['# PlotPickle Reports',f"Source: {r['source']['sourceFile']} | ID: {r['source']['projectId']} | revision: {r['source']['revision']}",f"SHA-256: {r['source']['sha256']}", 'Status: read-only draft report; no application Save/Lock or media verification.']
    for name,val in r['sections'].items():
        if section!='all' and name!=section:continue
        out.extend(['',f'## {name.title()}'])
        for k,v in val.items():
            out.append(f'- {k}: '+(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v)))
    return '\n'.join(out)+'\n'

def main():
    a=argparse.ArgumentParser();a.add_argument('--project',required=True,type=pathlib.Path);a.add_argument('--section',choices=('all',)+SECTIONS,default='all');a.add_argument('--format',choices=('json','markdown'),default='json');a.add_argument('--out',type=pathlib.Path);v=a.parse_args()
    p,sha=load(v.project);r=report(p,v.project.name,sha)
    if v.section!='all':r['sections']={v.section:r['sections'][v.section]}
    out=json.dumps(r,indent=2,ensure_ascii=False)+'\n' if v.format=='json' else markdown(r,v.section)
    if v.out:
        with v.out.open('x',encoding='utf-8') as f:f.write(out)
    else:sys.stdout.write(out)
if __name__=='__main__':main()
