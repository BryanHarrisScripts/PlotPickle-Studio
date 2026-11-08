#!/usr/bin/env python3
"""Read-only native-reader-backed PlotPickle story drilldown. Emits JSON, never changes files."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
READERS = HERE.parents[1] / 'read-plotpickle-project' / 'scripts'


def native(*args):
    proc = subprocess.run(list(map(str, args)), text=True, capture_output=True, check=False)
    if proc.returncode:
        raise ValueError('NATIVE_READER_FAILED: ' + (proc.stderr or proc.stdout).strip()[:500])
    return json.loads(proc.stdout)


def check_address(args):
    a, q, b, m, s = args.act, args.sequence, args.block, args.mini, args.shot
    # All address arguments are local within the immediate parent (except global values emitted by output).
    for name, val, hi in [('act',a,4),('sequence',q,3),('block',b,6),('mini',m,4),('shot',s,25)]:
        if val is not None and not 1 <= val <= hi:
            raise ValueError(f'INVALID_{name.upper()}')
    required = {'act':['act'],'sequence':['act','sequence'],'block':['act','block'],
                'mini':['act','block','mini'],'shot':['act','block','mini','shot']}
    for name in required.get(args.view,[]):
        if getattr(args,name) is None: raise ValueError('MISSING_' + name.upper())
    if q is not None and b is not None and (b-1)//2+1 != q:
        raise ValueError('BLOCK_OUTSIDE_SEQUENCE')
    if s is not None and m is None: raise ValueError('SHOT_REQUIRES_MINI')
    if m is not None and b is None: raise ValueError('MINI_REQUIRES_BLOCK')
    return {'act':a,'sequenceLocal':q,'blockLocal':b,'miniBlock':m,'shot':s,
            'sequenceGlobal':(a-1)*3+q if a and q else None,
            'blockGlobal':(a-1)*6+b if a and b else None}


def passages_in(p, block=None, mini=None):
    src=p.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])
    return [{'id':s.get('id'),'type':s.get('type'),'text':s.get('text'),
             'blockNumber':s.get('blockNumber'),'miniBlockNumber':s.get('miniBlockNumber')}
            for s in src if (block is None or s.get('blockNumber')==block)
            and (mini is None or s.get('miniBlockNumber')==mini)]


def navigate(args):
    addr=check_address(args)
    path=Path(args.project).expanduser().resolve()
    if not path.is_file(): raise ValueError('PROJECT_NOT_FOUND')
    inspector=READERS/'inspect-project.mjs'
    if not inspector.is_file(): raise ValueError('BUNDLED_INSPECTOR_NOT_AVAILABLE')
    identity=native('node', inspector,'--file',path,'--operation','identity').get('project',{})
    if not all(k in identity for k in ('id','revision','sha256')):
        raise ValueError('PROJECT_IDENTITY_INCOMPLETE')
    if args.expected_id is not None and args.expected_id!=identity['id']:raise ValueError('WRONG_ACTIVE_PROJECT')
    if args.expected_revision is not None and args.expected_revision!=identity['revision']:raise ValueError('STALE_PROJECT_REVISION')
    if args.expected_sha256 is not None and args.expected_sha256!=identity['sha256']:raise ValueError('STALE_PROJECT_FINGERPRINT')
    p=json.loads(path.read_text(encoding='utf-8'))
    if args.view != 'story' and not p.get('sourceEvidence'):
        # The reader may accept an intentionally empty scaffold; do not invent source details.
        pass
    out={'version':1,'view':args.view,'project':identity,'address':addr,
         'mutation':'none','chatGPTProjectCreation':'not attempted','nativeAppUpdated':False,
         'breadcrumbs':['Story'] + ([f'Act {args.act}'] if args.act else [])
         + ([f'Sequence {args.sequence}'] if args.sequence else [])
         + ([f'Block {args.block}'] if args.block else [])
         + ([f'Mini-Block {args.mini}'] if args.mini else [])
         + ([f'Shot {args.shot:02}'] if args.shot else [])}
    if args.view=='story':
        out['acts']=[{'act':a,'sequences':3,'blocks':6,'miniBlocks':24,'planningPositions':600} for a in range(1,5)]
        out['sourcePassageCount']=len(passages_in(p));return out
    base=(args.act-1)*6
    if args.view=='act':
        out['sequences']=[{'local':q,'global':(args.act-1)*3+q,
          'blocks':[{'local':b,'global':base+b,'sourcePassageCount':len(passages_in(p,base+b))}
                    for b in (q*2-1,q*2)]} for q in range(1,4)]
        return out
    if args.view=='sequence':
        out['blocks']=[{'local':b,'global':base+b,'miniBlocks':4,
                        'sourcePassageCount':len(passages_in(p,base+b))}
                       for b in (args.sequence*2-1,args.sequence*2)]
        return out
    global_block=addr['blockGlobal']
    if args.view=='block':
        out['miniBlocks']=[{'mini':m,'sourcePassages':len(passages_in(p,global_block,m)),
                            'planningPositions':25} for m in range(1,5)]
        return out
    selected=passages_in(p,global_block,args.mini)
    reviewer=READERS/'storyboard-review.py'
    if not reviewer.is_file():raise ValueError('BUNDLED_STORYBOARD_REVIEW_NOT_AVAILABLE')
    review=native(sys.executable, reviewer,'--project',path,'--project-id',identity['id'],
                  '--revision',identity['revision'],'--sha256',identity['sha256'],
                  '--block',global_block,'--mini',args.mini)
    slots=review.get('shots',[])
    if len(slots)!=25:raise ValueError('INVALID_NATIVE_SHOT_COUNT')
    out.update({'sourcePassages':selected, 'slotCount':25,
                'verifiedReader':True,'reviewFileCounts':review.get('fileAndRecordCounts',{})})
    if args.view=='mini':
        out['shots']=[{'shot':i,'address':slot.get('address'),
                       'status':slot.get('shotStatus'), 'candidateCount':len(slot.get('candidates',[])),
                       'savedCandidates':sum(bool(c.get('savedMarkerPresent')) for c in slot.get('candidates',[])),
                       'lockedCandidates':sum(bool(c.get('locked')) for c in slot.get('candidates',[]))}
                      for i,slot in enumerate(slots,1)]
        return out
    slot=slots[args.shot-1]
    ext=p.get('assetRegistry',{}).get('extensions',{}).get('storyWorkflow',{})
    address_plan={'actNumber':args.act,'sequenceNumber':(global_block-1)//2+1,
                  'blockNumber':global_block,'miniBlockNumber':args.mini}
    matching_plans=[x for x in ext.get('plans',[]) if x.get('address')==address_plan]
    plan=matching_plans[0] if len(matching_plans)==1 else None
    planned=[x for x in (plan or {}).get('shots',[]) if x.get('shotNumber')==args.shot]
    shot_plan=planned[0] if len(planned)==1 and planned[0].get('state')=='PLANNED' else None
    anchor=f'storyboard-anchor:block:block-{global_block:02}:mini-{args.mini}'
    recorded_prompts=[x for x in p.get('production',{}).get('storyboardImagePrompts',[])
                      if x.get('anchorRef')==anchor and x.get('position')==args.shot]
    if len(recorded_prompts)>1:raise ValueError('CONFLICTING_STORED_PROMPTS')
    rp=recorded_prompts[0] if recorded_prompts else None
    if shot_plan and rp and shot_plan.get('prompt')!=rp.get('prompt'):
        raise ValueError('PLAN_AND_STORED_PROMPT_MISMATCH')
    beat_candidates=[x for x in ext.get('authoredBeats',[]) if isinstance(x,dict)
                     and x.get('address')=={**address_plan,'shotNumber':args.shot}]
    # An authored shot-plan coverage type called 'story-beat' does not prove an independent authored beat.
    beat=beat_candidates[0] if len(beat_candidates)==1 else None
    shot_refs=set(shot_plan.get('passageIds',[])) if shot_plan else set()
    relevant=[x for x in selected if x.get('id') in shot_refs] if shot_plan else []
    all_truths={x.get('id'):x for x in ext.get('truths',[]) if isinstance(x,dict)}
    continuity=[all_truths[t] for t in shot_plan.get('truthIds',[]) if t in all_truths] if shot_plan else []
    out['shotDetail']={
        'shot':args.shot,'address':slot.get('address'),'shotStatus':slot.get('shotStatus'),
        'sourcePassages':relevant, 'miniBlockEvidence':slot.get('miniBlockEvidence'),
        'shotPlan':{k:shot_plan.get(k) for k in ('state','coverageType','narrativePurpose','composition','durationTargetSeconds','semanticGrounding','passageIds')} if shot_plan else {'state':'not authored'},
        'authoredBeat':{'state':'recorded','data':beat} if beat else {'state':'not separately verified'},
        'storyboardPrompt':{'state':'recorded-exact','text':rp.get('prompt'),'createdAt':rp.get('createdAt')} if rp else {'state':'not authored','text':None},
        'candidates':slot.get('candidates',[]),'continuity':{'records':continuity,'state':'recorded' if continuity else 'not authored'},
        'camera':{'composition':shot_plan.get('composition'),'status':'shot-plan-proposal'} if shot_plan else {'state':'not authored'},'lighting':{'state':'not separately authored'},
        'narration':{'state':'not verified'},'motionSpans':{'state':'not verified'},
        'statusNote':'Opening this panel is read-only. Candidate records do not imply author approval.'}
    return out


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--project',required=True)
    a.add_argument('--view',required=True,choices=['story','act','sequence','block','mini','shot'])
    for arg in ('act','sequence','block','mini','shot'):a.add_argument('--'+arg,type=int)
    a.add_argument('--expected-id');a.add_argument('--expected-revision',type=int);a.add_argument('--expected-sha256')
    args=a.parse_args()
    try: print(json.dumps(navigate(args),ensure_ascii=False))
    except (ValueError,OSError,TypeError,KeyError,json.JSONDecodeError) as ex:
        print(json.dumps({'status':'blocked','reason':str(ex),'mutation':'none'}),file=sys.stderr);sys.exit(1)

if __name__=='__main__':main()
