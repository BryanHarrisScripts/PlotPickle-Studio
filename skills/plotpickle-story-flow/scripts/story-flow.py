#!/usr/bin/env python3
"""Read-only source-pinned PlotPickle Script → Storyboard → Visuals → Produce preflight."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, sys
from collections import Counter
SCHEMA='plotpickle.story-flow.v1'
HEX64=re.compile(r'^[0-9a-f]{64}$')
def _hash(raw):return hashlib.sha256(raw).hexdigest()
def _safe_media(root,path,expected):
    if root is None:return 'not-checked-no-assets-root'
    if not isinstance(path,str) or not path or path.startswith('/') or '\\' in path:return 'unsafe-or-missing-path'
    pp=pathlib.PurePosixPath(path)
    if pp.is_absolute() or any(v in ('','..') for v in pp.parts):return 'unsafe-or-missing-path'
    root=root.resolve();target=(root/path).resolve()
    if not target.is_relative_to(root):return 'unsafe-or-missing-path'
    if not target.is_file():return 'media-not-present'
    if not isinstance(expected,str):return 'no-valid-declared-sha256'
    expected=expected.lower().removeprefix('sha256:')
    if not HEX64.fullmatch(expected):return 'no-valid-declared-sha256'
    h=hashlib.sha256()
    with target.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return 'hash-verified' if h.hexdigest()==expected else 'sha256-mismatch'
def _address(item):
    a=item.get('address')
    if not isinstance(a,dict):return None
    fields=('actNumber','sequenceNumber','blockNumber','miniBlockNumber','shotNumber')
    vals=tuple(a.get(k) for k in fields)
    if any(type(v) is not int for v in vals):return None
    act,seq,block,mini,shot=vals
    if not (1<=act<=4 and 1<=seq<=12 and 1<=block<=24 and 1<=mini<=4 and 1<=shot<=25):return None
    if not (3*(act-1)<seq<=3*act and 2*(seq-1)<block<=2*seq):return None
    return vals
def inspect(project,project_bytes,assets_root=None,block=None,mini=None):
    if not isinstance(project,dict) or not isinstance(project.get('id'),str) or not project['id']:raise ValueError('PROJECT_ID_REQUIRED')
    if type(project.get('revision')) is not int or project['revision']<0:raise ValueError('PROJECT_REVISION_REQUIRED')
    if (block is None)!=(mini is None):raise ValueError('BLOCK_AND_MINI_MUST_BE_SUPPLIED_TOGETHER')
    if block is not None and not (1<=block<=24 and 1<=mini<=4):raise ValueError('INVALID_SCOPE')
    p=((project.get('sourceEvidence') or {}).get('screenplay') or {})
    passages=p.get('passages') or []
    if not isinstance(passages,list):raise ValueError('SCREENPLAY_PASSAGES_MUST_BE_LIST')
    ids={x.get('id') for x in passages if isinstance(x,dict) and isinstance(x.get('id'),str)}
    has_text=any(isinstance(x,dict) and isinstance(x.get('text'),str) and x['text'].strip() for x in passages)
    wf=(((project.get('assetRegistry') or {}).get('extensions') or {}).get('storyWorkflow') or {})
    mappings=wf.get('imageMappings') or []
    if not isinstance(mappings,list):raise ValueError('STORYBOARD_IMAGE_MAPPINGS_MUST_BE_LIST')
    selected=[]
    for item in mappings:
        if not isinstance(item,dict):continue
        a=item.get('address') or {}
        if block is not None and (a.get('blockNumber')!=block or a.get('miniBlockNumber')!=mini):continue
        selected.append(item)
    accepted=set(((project.get('build') or {}).get('foundations') or {}).get('acceptedVisualArtifactIds') or [])
    pos=Counter();shots=[]
    for item in selected:
        a=_address(item)
        if a:pos[a]+=1
        source=item.get('passageIds') or []
        sourced=isinstance(source,list) and bool(source) and all(isinstance(x,str) and x in ids for x in source)
        asset=item.get('artifactId');saved=item.get('savedMarkerPresent') is True;locked=item.get('locked') is True
        approved=isinstance(asset,str) and asset in accepted
        media=_safe_media(assets_root,item.get('portablePath'),item.get('sha256'))
        shots.append({'address':dict(zip(('act','sequence','block','mini','shot'),a)) if a else None,
                      'artifactId':asset,'sourcePassageIds':source if isinstance(source,list) else [],
                      'sourcePassagesValid':bool(sourced),'promptOrigin':item.get('promptOrigin','unknown'),
                      'candidateRecorded':bool(item.get('portablePath') and item.get('sha256')),
                      'media':media,'savedMarkerPresent':saved,'locked':locked,
                      'acceptedArtifactIdRecorded':approved,
                      'eligibleForSourcePinnedProduction':bool(a and sourced and media=='hash-verified' and saved and locked and approved)})
    duplicates=[list(k) for k,v in pos.items() if v>1]
    errors=sum(not bool(s['address']) or not s['sourcePassagesValid'] for s in shots)+len(duplicates)
    verified=sum(s['media']=='hash-verified' for s in shots)
    eligible=sum(s['eligibleForSourcePinnedProduction'] for s in shots)
    candidates=sum(s['candidateRecorded'] for s in shots)
    script_ready=bool(has_text and ids)
    board_ready=script_ready and bool(shots) and not errors
    visuals_ready=board_ready and candidates==len(shots) and verified==len(shots) and eligible==len(shots)
    if not script_ready:next_stage,next_action='Script','Import or write a real screenplay; approve the source before storyboarding.'
    elif not shots:next_stage,next_action='Storyboard','Plan a first 25-shot Mini-Block from screenplay evidence; do not invent completed shots.'
    elif errors:next_stage,next_action='Storyboard','Repair duplicate, invalid or ungrounded shot mappings.'
    elif candidates<len(shots):next_stage,next_action='Visuals','Create and review missing image candidates.'
    elif verified<len(shots):next_stage,next_action='Visuals','Supply the actual image files and verify selected SHA-256 hashes.'
    elif eligible<len(shots):next_stage,next_action='Visuals','Complete guarded Save-then-Lock/acceptance readback.'
    else:next_stage,next_action='Produce','Prepare an animatic or a no-spend fal Motion Span brief from verified source media.'
    return {'schema':SCHEMA,
      'source':{'projectId':project['id'],'title':project.get('title'),'revision':project['revision'],
                'rawSha256':_hash(project_bytes),'screenplaySource':p.get('sourceFileName')},
      'scope':{'block':block,'mini':mini,'allMappedShots':block is None},
      'stages':[
       {'name':'Script','status':'source-present' if script_ready else 'source-missing','evidence':{'passageCount':len(passages),'passageIds':len(ids)}},
       {'name':'Storyboard','status':'mapped-for-review' if board_ready else 'needs-source-or-mapping',
        'evidence':{'mappedShotCount':len(shots),'mappingErrors':errors,'duplicateAddresses':duplicates}},
       {'name':'Visuals','status':'source-ready' if visuals_ready else 'unverified-or-needs-review',
        'evidence':{'recordedCandidates':candidates,'mediaHashVerified':verified,'savedLockedAndAcceptedWithVerifiedBytes':eligible}},
       {'name':'Produce','status':'draft-assembly-preflight-only' if visuals_ready else 'not-source-ready',
        'evidence':{'sourceEligibleShots':eligible,'sourceSelectedShots':len(shots),
                    'videoClipsVerified':None,'assemblyExecuted':False,'motionProvider':'fal','jobSubmitted':False}}],
      'nextStage':next_stage,'nextAction':next_action,'shots':shots,
      'safety':{'ppfModified':False,'providerInvoked':False,'creditsSpent':False,
                'mediaBytesVerifiedOnlyWhenAssetsRootSupplied':True,
                'canonicalPlanningPositionsNotAssumedAuthored':2400,
                'productionHandoffRequiresExplicitUserDecision':True,
                'recordedAcceptanceDoesNotImplyCreativeApproval':True}}
def to_markdown(d):
    s=d['source'];lines=['# PlotPickle Story Flow — read-only handoff','',f"Story: {s['title'] or '(untitled)'}",
    f"Project ID: {s['projectId']}",f"Revision: {s['revision']}",f"SHA-256: {s['rawSha256']}",'']
    for stage in d['stages']:
        lines.append(f"{stage['name']}: {stage['status']}")
        lines.append('  '+'; '.join(f'{k}={v}' for k,v in stage['evidence'].items()))
    lines.extend(['',f"Next: {d['nextStage']} — {d['nextAction']}",'',
      'Read-only preflight. No story edits, generation, Save/Lock or paid provider spend.'])
    return '\n'.join(lines)+'\n'
def main(argv=None):
    parser=argparse.ArgumentParser(description='Read-only PlotPickle four-stage story preflight')
    parser.add_argument('--project',type=pathlib.Path,required=True)
    parser.add_argument('--assets-root',type=pathlib.Path)
    parser.add_argument('--block',type=int);parser.add_argument('--mini',type=int)
    parser.add_argument('--format',choices=('json','markdown'),default='markdown')
    parser.add_argument('--out',type=pathlib.Path)
    a=parser.parse_args(argv);data=a.project.read_bytes()
    report=inspect(json.loads(data),data,a.assets_root,a.block,a.mini)
    output=json.dumps(report,ensure_ascii=False,indent=2)+'\n' if a.format=='json' else to_markdown(report)
    if a.out:
        with a.out.open('x',encoding='utf8') as f:f.write(output)
    else:sys.stdout.write(output)
    return 0
if __name__=='__main__':raise SystemExit(main())
