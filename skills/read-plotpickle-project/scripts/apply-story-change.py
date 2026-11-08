"""Apply one explicitly authorized author-directed revision as an atomic snapshot.
Inputs pin identity, before-text, image hashes and explicit placement. No generation.
"""
import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
wf = load('workflow', 'story-workflow.py')
pm = load('project_model', 'project-model.py')


def apply(args):
    project, ident = wf.pinned(args)
    payload = wf.read_json(args.file)
    pm.require_snapshot(payload, ident)
    change_id = wf.nonblank(payload.get('id'), 120)
    if not all(c.isalnum() or c in '-_' for c in change_id):wf.fail('INVALID_CHANGE_ID')
    authority = payload.get('authorship', {})
    if authority.get('kind') != 'user':wf.fail('AUTHOR_DIRECTED_ORIGIN_REQUIRED')
    wf.nonblank(authority.get('instruction'), 16000)
    wf.nonblank(authority.get('authorization'), 4000)
    m = pm.model(project)
    if any(x['id'] == change_id for x in m.get('storyChanges', [])):wf.fail('CHANGE_ALREADY_APPLIED')
    before = copy.deepcopy(project['sourceEvidence']['screenplay'])
    passages = copy.deepcopy(wf.source(project)['passages'])
    by_id = {p['id']: p for p in passages}
    operations = payload.get('operations', [])
    if not operations:wf.fail('SOURCE_OPERATIONS_REQUIRED')
    touched, new_ids = set(), set()
    for op in operations:
        if op.get('kind') == 'replace':
            pid = op.get('passageId')
            if pid not in by_id or pid in touched:wf.fail('REPLACE_TARGET_INVALID')
            if by_id[pid]['text'] != op.get('expectedText'):wf.fail('BEFORE_TEXT_CHANGED')
            text = wf.nonblank(op.get('text'), 780)
            by_id[pid]['text'] = wf.clean(text);touched.add(pid)
        elif op.get('kind') == 'insert-after':
            anchor = op.get('afterPassageId')
            if anchor not in by_id:wf.fail('INSERT_ANCHOR_UNRESOLVED')
            insert = []
            for fragment in op.get('passages', []):
                pid = wf.nonblank(fragment.get('id'), 240)
                if pid in by_id or not pid.startswith('author-'):wf.fail('AUTHOR_PASSAGE_ID_INVALID')
                if fragment.get('type') not in pm.KINDS:wf.fail('INVALID_PASSAGE_TYPE')
                text = wf.nonblank(fragment.get('text'), 780)
                p = {**by_id[anchor], 'id':pid, 'type':fragment['type'], 'text':wf.clean(text)}
                by_id[pid] = p;new_ids.add(pid);insert.append(p)
            if not insert:wf.fail('EMPTY_INSERT')
            index = next(i for i,p in enumerate(passages) if p['id']==anchor)
            passages[index+1:index+1] = insert
        else:wf.fail('UNSUPPORTED_SOURCE_OPERATION')
    if len(passages)>wf.MAX_PASSAGES:wf.fail('SOURCE_EXCEEDS_CANONICAL_CAPACITY')
    # Optional four-Act migration includes every explicitly scoped story passage.
    groups = payload.get('fourActs', [])
    scope = set(payload.get('storyScopePassageIds', [])) | new_ids
    pm.check_ids(list(scope), set(by_id), True)
    if groups:
        if len(groups)!=4 or any(type(g.get('actNumber')) is not int or not g.get('placements') for g in groups) or {g.get('actNumber') for g in groups}!={1,2,3,4}:wf.fail('FOUR_UNIQUE_NONEMPTY_ACTS_REQUIRED')
        assigned = set()
        for group in groups:
            wf.nonblank(group.get('title'), 500);wf.nonblank(group.get('reason'), 4000)
            for placement in group.get('placements', []):
                pid = placement.get('passageId')
                if pid not in scope or pid in assigned:wf.fail('INVALID_ACT_ASSIGNMENT')
                a = wf.address(placement.get('blockNumber'), placement.get('miniBlockNumber'))
                if a['actNumber'] != group['actNumber']:wf.fail('ACT_ADDRESS_MISMATCH')
                by_id[pid].update(blockNumber=a['blockNumber'], miniBlockNumber=a['miniBlockNumber'])
                assigned.add(pid)
        if assigned!=scope:wf.fail('ACT_MAP_MUST_COVER_STORY_SCOPE')
        ordered_acts=[(by_id[p['id']]['blockNumber']-1)//6+1 for p in passages if p['id'] in scope]
        if ordered_acts!=sorted(ordered_acts):wf.fail('ACTS_MUST_FOLLOW_SCREENPLAY_ORDER')
    for p in passages:p.update(by_id[p['id']])
    source=project['sourceEvidence']['screenplay'];source['passages']=passages
    source.update(storedPassageCount=len(passages),totalPassageCount=len(passages),analysisStatus='suggested',sourceFormat='imported-source+author-directed-revision')
    artifacts=project['build']['foundations']['visualArtifacts']
    before_media=copy.deepcopy(project['build']['foundations'])
    before_plans=copy.deepcopy(wf.workflow(project).get('plans',[]))
    before_prompts=copy.deepcopy(project['production'].get('storyboardImagePrompts',[]))
    artifacts_by_id={a['id']:a for a in artifacts}
    supersede=payload.get('supersedeArtifactIds', [])
    pm.check_ids(supersede,set(artifacts_by_id))
    pm.check_ids(payload.get('reviewArtifactIds',[]),set(artifacts_by_id))
    for aid in supersede:artifacts_by_id[aid]['reviewState']='rejected'
    accepted=project['build']['foundations']['acceptedVisualArtifactIds']
    accepted[:]=[aid for aid in accepted if aid not in supersede]
    for asset in project['assetRegistry']['assets']:
        if any(v.get('source') in {artifacts_by_id[x]['assetUrl'] for x in supersede} for v in asset.get('variations', [])):
            for v in asset['variations']:v['approval']='rejected'
            asset['approvedVariationId']=''
    extra={};image_records=[]
    for image in payload.get('images', []):
        from PIL import Image
        pm.check_ids(image.get('passageIds', []),scope,True)
        raw=wf.read_bytes(image['path'])
        if wf.digest(raw)!=image.get('sha256'):wf.fail('IMAGE_BYTES_CHANGED')
        prompt=wf.nonblank(image.get('prompt'),8000)
        if image.get('promptOrigin') not in {'captured','reconstructed'}:wf.fail('PROMPT_ORIGIN_REQUIRED')
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            if im.width*im.height>40000000:wf.fail('IMAGE_TOO_LARGE')
            if im.format not in {'PNG','JPEG','WEBP'}:wf.fail('IMAGE_FORMAT_UNSUPPORTED')
            buffer=io.BytesIO();im.convert('RGBA' if 'A' in im.getbands() else 'RGB').save(buffer,format='WEBP',lossless=True)
            data=buffer.getvalue()
        h=wf.digest(data);name='story-'+change_id+'-'+h[:16]+'.webp';aid=str(uuid.uuid4());url='/api/local-ai/assets/'+name
        artifacts.append({'id':aid,'assetUrl':url,'prompt':prompt,'createdAt':wf.stamp(),'provider':'ChatGPT host image generation','model':'','frameNumber':1,
            'sourceDecisionKeys':['source-passage:'+p for p in image['passageIds']], 'workflow':'storyboard-frame-webp-v2','reviewState':'draft','parentArtifactId':None})
        extra['assets/'+name]=data
        record={'artifactId':aid,'passageIds':image['passageIds'],'portablePath':'assets/'+name,'sha256':h,'sourceSha256':wf.digest(raw),'prompt':prompt,'promptOrigin':image['promptOrigin'],
                'visualApproval':{'state':'approved','authority':authority['authorization']},'savedMarkerPresent':False,'locked':False,'packageBytesVerified':True,'liveMediaBytesVerified':False}
        image_records.append(record)
        project['assetRegistry']['assets'].append({'id':'asset-'+aid,'kind':'image','label':image['label'],'targets':[{'kind':'storyboard-frame','id':aid}],
            'variations':[{'id':'variation-'+aid,'source':url,'portablePath':record['portablePath'],'contentHash':'sha256:'+h,'mediaType':'image/webp','bytes':len(data),
                          'prompt':prompt,'provider':'ChatGPT host image generation','approval':'unreviewed','provenanceIds':image['passageIds'],'extensions':{'visualApproval':record['visualApproval']}}],
            'approvedVariationId':'','createdAt':wf.stamp(),'updatedAt':wf.stamp(),'extensions':{'authorChangeId':change_id}})
    # Rebuild the active source-to-shot mapping in screenplay order. Rejected media is audit history.
    legacy=project['assetRegistry']['extensions'].get('artworkMapping',{}).get('entries',[])
    legacy_by_id={e['artifactId']:e for e in legacy}
    old_maps=wf.workflow(project).get('imageMappings',[])
    mapping_by_id={e['artifactId']:e for e in old_maps+image_records}
    source_index={p['id']:i for i,p in enumerate(passages)}
    grouped={}
    for seq,art in enumerate(artifacts):
        if art.get('workflow')!='storyboard-frame-webp-v2' or art.get('reviewState')=='rejected':continue
        refs=[k.removeprefix('source-passage:') for k in art.get('sourceDecisionKeys',[]) if k.startswith('source-passage:')]
        if not refs:refs=legacy_by_id.get(art['id'],{}).get('passageIds',[])
        override=payload.get('imagePassageOverrides',{}).get(art['id'])
        if override:
            wf.nonblank(override.get('reason'),4000)
            pm.check_ids(override.get('passageIds',[]),scope,True)
            refs=override['passageIds']
            art['sourceDecisionKeys']=[k for k in art.get('sourceDecisionKeys',[]) if not k.startswith('source-passage:')]+['source-passage:'+r for r in refs]
            if art['id'] in legacy_by_id:legacy_by_id[art['id']]['passageIds']=refs
        if not refs or any(r not in scope for r in refs):wf.fail('ACTIVE_IMAGE_EVIDENCE_REQUIRES_EXPLICIT_MIGRATION')
        locations={(by_id[r]['blockNumber'],by_id[r]['miniBlockNumber']) for r in refs}
        if len(locations)!=1:wf.fail('IMAGE_CROSSES_MINI_BOUNDARY_REVIEW_REQUIRED')
        primary=payload.get('primaryPassageOverrides',{}).get(art['id'])
        if primary is not None and primary not in refs:wf.fail('PRIMARY_PASSAGE_NOT_IN_IMAGE_EVIDENCE')
        order=source_index[primary] if primary else min(source_index[r] for r in refs)
        b,mini=next(iter(locations));grouped.setdefault((b,mini),[]).append((order,seq,art,refs))
    for (b,mini),rows in grouped.items():
        if len(rows)>25:wf.fail('MINI_IMAGE_CAPACITY_EXCEEDED')
        for slot,(_,_,art,refs) in enumerate(sorted(rows,key=lambda r:(r[0],r[1])),1):
            a=wf.address(b,mini,slot);art['frameNumber']=slot
            old=legacy_by_id.get(art['id'],mapping_by_id.get(art['id'],{})).get('address')
            if old!=a or any(r in touched or r in new_ids for r in refs):
                art['sourceDecisionKeys']=[k for k in art.get('sourceDecisionKeys',[]) if k!='storyboard-local-save:v1']
                accepted[:]=[x for x in accepted if x!=art['id']]
                art['reviewState']='draft'
            art['sourceDecisionKeys']=[k for k in art.get('sourceDecisionKeys',[]) if not k.startswith(('storyboard-target:','storyboard-anchor:','storyboard-position:'))]+[f'storyboard-target:block:block-{b:02}',wf.anchor(b,mini),f'storyboard-position:{slot}']
            if art['id'] in legacy_by_id:legacy_by_id[art['id']]['address']=a
            if art['id'] in mapping_by_id:mapping_by_id[art['id']]['address']=a
    for entry in legacy:
        if entry['artifactId'] in supersede:entry['status']='superseded'
    wf.workflow(project)['imageMappings']=list(mapping_by_id.values())
    # Plan prompts and previous continuity interpretations must not silently follow new addresses.
    m['reviewRequired'].append({'authorChangeId':change_id,'atRevision':project['revision']+1,'areas':['shot-plans','continuity','runtime','existing-derived-writing'],
        'artifactIds':payload.get('reviewArtifactIds',[]),'reason':'Author-directed revision; earlier plans, prompts and artwork need review against the new source.'})
    if groups:
        wf.workflow(project)['plans']=[]
        project['production']['storyboardImagePrompts']=[]
        m['fourActPlan']={'status':'author-directed-structure','groups':groups,'storyScopePassageIds':list(scope),'excludedRetainedPassageIds':[p['id'] for p in passages if p['id'] not in scope]}
        for block in project['structure']['blocks']:
            for mini in block['miniBlocks']:
                selected=[p['text'] for p in passages if p['id'] in scope and p['blockNumber']==block['number'] and p['miniBlockNumber']==mini['ordinal']]
                mini['note']=('Author-directed story coverage: '+' '.join(selected))[:800] if selected else 'No story coverage assigned here; canonical planning position retained.'
    changes=m.setdefault('storyChanges',[])
    changes.append({'id':change_id,'at':wf.stamp(),'baseProject':ident,'authorship':authority,'operations':operations,
                    'beforeSource':before,'sourceFingerprintAfter':pm.fingerprint(project),'newImageRecords':image_records,'supersededArtifactIds':supersede,
                    'beforeMediaState':before_media,'beforeShotPlans':before_plans,'beforeShotPrompts':before_prompts,
                    'propContinuity':payload.get('propContinuity',[]),'learning':payload.get('learning',{}),'semanticContinuityIndependentlyVerified':False})
    changes[-1]['imagePassageOverrides']=payload.get('imagePassageOverrides',{})
    project['revision']+=1;project['updatedAt']=wf.stamp()
    return wf.save_snapshot(args,project,extra)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('project','project-id','sha256','file','out'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--revision',type=int,required=True)
    try:print(json.dumps(apply(parser.parse_args()),ensure_ascii=False))
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(json.dumps({'status':'blocked','code':str(e)[:600],'inputFileMutated':False}),file=sys.stderr);sys.exit(1)
