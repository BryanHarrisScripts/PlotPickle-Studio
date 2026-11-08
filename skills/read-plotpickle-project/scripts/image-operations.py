"""Pinned, atomic image changes. Pending replacements keep their reference visible."""
import argparse, copy, importlib.util, io, json, sys, uuid
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('workflow', HERE / 'story-workflow.py')
wf = importlib.util.module_from_spec(spec); spec.loader.exec_module(wf)

def records(p):
    ext = p['assetRegistry']['extensions']
    return ext.get('artworkMapping', {}).get('entries', []) + wf.workflow(p)['imageMappings']

def artifacts(p):
    return p['build']['foundations']['visualArtifacts']

def active(p):
    return [a for a in artifacts(p) if a.get('workflow') == 'storyboard-frame-webp-v2' and a.get('reviewState') != 'rejected']

def ledger(p):
    return p['assetRegistry']['extensions'].setdefault('imageChanges', {'version':1, 'events':[], 'pending':[]})

def find(p, aid):
    a = next((a for a in artifacts(p) if a['id'] == aid), None)
    r = next((r for r in records(p) if r['artifactId'] == aid), None)
    if not a or not r: wf.fail('IMAGE_RECORD_REQUIRED')
    return a, r

def address(value):
    a = wf.address(value['blockNumber'], value['miniBlockNumber'], value['shotNumber'])
    if value != a: wf.fail('ADDRESS_MUST_BE_CANONICAL')
    return a

def place(p, art, rec, a):
    a = address(a)
    for other in active(p):
        if other['id'] != art['id'] and find(p, other['id'])[1]['address'] == a: wf.fail('SLOT_OCCUPIED_PLAN_EXPANSION_REQUIRED')
    art['frameNumber'] = a['shotNumber']
    art['sourceDecisionKeys'] = [k for k in art.get('sourceDecisionKeys', []) if not k.startswith(('storyboard-target:', 'storyboard-anchor:', 'storyboard-position:'))] + [f"storyboard-target:block:block-{a['blockNumber']:02}", wf.anchor(a['blockNumber'],a['miniBlockNumber']), f"storyboard-position:{a['shotNumber']}"]
    rec['address'] = a

def unlock(p, art, rec):
    art['reviewState'] = 'draft'
    art['sourceDecisionKeys'] = [k for k in art.get('sourceDecisionKeys', []) if k != 'storyboard-local-save:v1']
    f = p['build']['foundations']; f['acceptedVisualArtifactIds'] = [x for x in f['acceptedVisualArtifactIds'] if x != art['id']]
    rec.update(savedMarkerPresent=False, locked=False)
    for asset in p['assetRegistry']['assets']:
        for v in asset.get('variations', []):
            if v.get('source') == art['assetUrl']:
                v['approval'] = 'unreviewed'; asset['approvedVariationId'] = ''

def retire(p, art, rec):
    unlock(p, art, rec); art['reviewState'] = 'rejected'; rec['status'] = 'superseded'
    for asset in p['assetRegistry']['assets']:
        for v in asset.get('variations', []):
            if v.get('source') == art['assetUrl']: v['approval'] = 'rejected'

def verify_reference(args, rec):
    rel = Path(rec['portablePath']); base = Path(args.project).resolve().parent
    if rel.is_absolute() or '..' in rel.parts or not (base/rel).resolve().is_relative_to(base): wf.fail('UNSAFE_PORTABLE_PATH')
    if wf.digest(wf.read_bytes(base/rel)) != rec['sha256']: wf.fail('REFERENCE_BYTES_CHANGED')
    from PIL import Image
    with Image.open(base/rel) as im: im.load()

def import_image(p, image, a, refs, extras, parent=None):
    from PIL import Image
    raw = wf.read_bytes(image['path'])
    if wf.digest(raw) != image['sha256']: wf.fail('IMAGE_BYTES_CHANGED')
    prompt = wf.nonblank(image['prompt'])
    if image.get('promptOrigin') not in ('captured', 'reconstructed'): wf.fail('PROMPT_ORIGIN_REQUIRED')
    with Image.open(io.BytesIO(raw)) as im:
        if im.width*im.height > 40000000: wf.fail('IMAGE_TOO_LARGE')
        im.load()
        if im.format not in ('PNG', 'JPEG', 'WEBP'): wf.fail('IMAGE_FORMAT_UNSUPPORTED')
        b = io.BytesIO(); im.convert('RGB').save(b, format='WEBP', lossless=True); data = b.getvalue()
        width, height = im.size
    h = wf.digest(data); aid = str(uuid.uuid4()); name = 'image-change-'+aid+'.webp'; rel = 'assets/'+name; url = '/api/local-ai/assets/'+name
    art = {'id':aid,'assetUrl':url,'prompt':prompt,'createdAt':wf.stamp(),'provider':'supplied or host-generated artwork','model':'','frameNumber':a['shotNumber'], 'sourceDecisionKeys':['source-passage:'+r for r in refs],'workflow':'storyboard-frame-webp-v2','reviewState':'draft','parentArtifactId':parent}
    rec = {'artifactId':aid,'address':a,'passageIds':refs,'portablePath':rel,'sha256':h,'sourceSha256':wf.digest(raw),'width':width,'height':height,'prompt':prompt,'promptOrigin':image['promptOrigin'],'visualApproval':{'state':'pending-user-review'},'savedMarkerPresent':False,'locked':False,'status':'current'}
    artifacts(p).append(art); wf.workflow(p)['imageMappings'].append(rec)
    p['assetRegistry']['assets'].append({'id':'asset-'+aid,'kind':'image','label':wf.nonblank(image['label'],500),'targets':[{'kind':'storyboard-frame','id':aid}], 'variations':[{'id':'variation-'+aid,'source':url,'portablePath':rel,'contentHash':'sha256:'+h,'mediaType':'image/webp','bytes':len(data),'prompt':prompt,'approval':'unreviewed','provenanceIds':refs}], 'approvedVariationId':'','createdAt':wf.stamp(),'updatedAt':wf.stamp()})
    extras[rel] = data; place(p,art,rec,a)
    return art,rec

def apply(args):
    p, ident = wf.pinned(args); payload = wf.read_json(args.file)
    if payload.get('project') != ident: wf.fail('STALE_PAYLOAD_SNAPSHOT')
    kind = payload['kind']; reason = wf.nonblank(payload['reason']); authority = wf.nonblank(payload['authorization'])
    log = ledger(p); event_id = wf.nonblank(payload['id'],240)
    if any(e['id'] == event_id for e in log['events']): wf.fail('DUPLICATE_CHANGE_ID')
    before = len(active(p)); extras = {}; source_hash = wf.digest(json.dumps(wf.source(p),sort_keys=True).encode())
    event = {'id':event_id,'kind':kind,'reason':reason,'authorization':authority,'baseProject':ident,'at':wf.stamp(),'sourceFingerprint':source_hash,'activeBefore':before,'referenceRestorations':0}
    pending = log['pending']; target = payload.get('artifactId')
    if kind != 'add':
        art,rec = find(p,target); event['artifactId'] = target; event['beforeArtifact'] = copy.deepcopy(art); event['beforeMapping'] = copy.deepcopy(rec)
    if kind == 'begin-replacement':
        if any(x['artifactId'] == target for x in pending): wf.fail('REPLACEMENT_ALREADY_PENDING')
        verify_reference(args,rec)
        if art['reviewState'] == 'rejected':
            if payload.get('restoreReference') is not True: wf.fail('INACTIVE_TARGET_REQUIRES_EXPLICIT_RESTORE')
            unlock(p,art,rec); place(p,art,rec,payload['address']); rec['status'] = 'current-reference'; event['referenceRestorations'] = 1
        pending.append({'id':event_id,'artifactId':target,'address':copy.deepcopy(rec['address']),'sourceFingerprint':source_hash,'state':'awaiting-verified-replacement'})
    elif kind == 'complete-replacement':
        item = next((x for x in pending if x['id'] == payload['pendingId'] and x['artifactId'] == target),None)
        if not item or item['sourceFingerprint'] != source_hash or item['address'] != rec['address'] or art['reviewState'] == 'rejected': wf.fail('PENDING_REPLACEMENT_STALE')
        verify_reference(args,rec)
        # Input is validated before output is committed; failure leaves the reference snapshot intact.
        retire(p,art,rec)
        new,newrec = import_image(p,payload['image'],item['address'],rec['passageIds'],extras,target)
        rec['replacedBy'] = new['id']; newrec['replaces'] = target; event['newArtifactId'] = new['id']; event['pendingId'] = item['id']; pending.remove(item)
    elif kind == 'add':
        refs = payload['passageIds']; valid = {r['id'] for r in wf.source(p)['passages']}
        if not refs or len(set(refs)) != len(refs) or any(r not in valid for r in refs): wf.fail('SOURCE_EVIDENCE_REQUIRED')
        a = address(payload['address'])
        new,_ = import_image(p,payload['image'],a,refs,extras); event['newArtifactId'] = new['id']
    elif kind in ('remove','move'):
        if art['reviewState'] == 'rejected': wf.fail('TARGET_NOT_ACTIVE')
        if any(x['artifactId'] == target for x in pending): wf.fail('FINISH_OR_CANCEL_PENDING_REPLACEMENT_FIRST')
        if kind == 'remove':
            retire(p,art,rec); event['coverageReview'] = {'passageIds':rec['passageIds'],'note':'Image removed; source beat retained. Review remaining visual coverage.'}
        else:
            unlock(p,art,rec); place(p,art,rec,payload['address']); event['continuityReviewRequired'] = True
    elif kind == 'cancel-replacement':
        item = next((x for x in pending if x['id'] == payload['pendingId'] and x['artifactId'] == target),None)
        if not item: wf.fail('PENDING_REPLACEMENT_NOT_FOUND')
        pending.remove(item)
    else: wf.fail('UNKNOWN_IMAGE_OPERATION')
    event['activeAfter'] = len(active(p)); event['activeDelta'] = event['activeAfter']-before
    expected = {'add':1,'remove':-1,'move':0,'complete-replacement':0,'begin-replacement':event['referenceRestorations'],'cancel-replacement':0}[kind]
    if event['activeDelta'] != expected: wf.fail('IMAGE_COUNT_INVARIANT_FAILED')
    if source_hash != wf.digest(json.dumps(wf.source(p),sort_keys=True).encode()): wf.fail('UNREQUESTED_SOURCE_CHANGE')
    log['events'].append(event); p['revision'] += 1; p['updatedAt'] = wf.stamp()
    return {**wf.save_snapshot(args,p,extras),'imageChange':event,'activeImages':len(active(p)),'pendingReplacements':len(pending)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('project','project-id','sha256','file','out'): parser.add_argument('--'+name,required=True)
    parser.add_argument('--revision',type=int,required=True)
    try: print(json.dumps(apply(parser.parse_args()),ensure_ascii=False))
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(json.dumps({'status':'blocked','code':str(e)[:600],'inputFileMutated':False}),file=sys.stderr); sys.exit(1)
