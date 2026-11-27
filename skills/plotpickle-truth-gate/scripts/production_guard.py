#!/usr/bin/env python3
"""Offline, fail-closed PlotPickle image-context preflight and candidate verification.

No provider calls, no PPF writes, no Studio mutations, no approval creation.
The caller must reopen the actual image pixels and conduct a human/visual semantic
comparison; a SHA, dimension check, or claimed semantic PASS does not do that.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = 'plotpickle.image-production-context.v1'
REVIEW_SCHEMA = 'plotpickle.image-production-review.v1'
STATES = {'PASS', 'DRIFTED', 'REVIEW_REQUIRED', 'UNKNOWN'}
HEX64 = re.compile(r'^[0-9a-f]{64}$')
BAD_PROMPT = re.compile(r'\b(collage|montage|contact sheet|storyboard sheet|storyboard grid|split[- ]screen|five[- ]shot|five[- ]frame|multi[- ]panel|five[- ]panel|panel grid|2x2 grid|3x2 grid)\b', re.I)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def issue(issues, location, message):
    issues.append({'at': location, 'problem': message})


def sha_valid(value):
    return isinstance(value, str) and bool(HEX64.fullmatch(value))


def text_valid(value):
    return isinstance(value, str) and bool(value.strip())


def resolve_file(root, relative):
    if not text_valid(relative):
        raise ValueError('missing local media path')
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or p.parts[0] in ('.', ''):
        raise ValueError('media path must be relative and confined to authorized root')
    root = Path(root).resolve(strict=True)
    p = (root / p).resolve(strict=True)
    if not p.is_relative_to(root) or not p.is_file():
        raise ValueError('media escapes authorized root or is not a file')
    return p


def verify_media(root, descriptor, at, issues, require_landscape=False):
    if not isinstance(descriptor, dict):
        issue(issues, at, 'expected media object'); return None
    if not sha_valid(descriptor.get('sha256')):
        issue(issues, at, 'expected real 64-hex media SHA-256')
    try:
        path = resolve_file(root, descriptor.get('path'))
        raw = path.read_bytes()
        actual = digest(raw)
        if actual != descriptor.get('sha256'):
            issue(issues, at, 'original media bytes SHA-256 mismatch')
        try:
            from PIL import Image
        except ImportError:
            issue(issues, at, 'Pillow decoder unavailable: fail closed'); return None
        with Image.open(path) as im:
            im.load()
            width, height = im.size
            if im.format not in ('PNG', 'WEBP', 'JPEG'):
                issue(issues, at, 'unsupported decoded image format')
            if require_landscape and (width < 640 or height < 320 or abs(width / height - 16/9) > 0.075):
                issue(issues, at, 'candidate is not a sufficiently sized 16:9 frame')
        if descriptor.get('bytes') is not None and descriptor['bytes'] != len(raw):
            issue(issues, at, 'media byte count mismatch')
        return {'path': str(path), 'sha256': actual, 'bytes': len(raw), 'width': width, 'height': height}
    except (OSError, ValueError, TypeError) as ex:
        issue(issues, at, 'missing/unsafe/unreadable original image: '+str(ex))
        return None


def address(sh):
    if not isinstance(sh, dict): return None
    a = sh.get('productionAddress')
    if not isinstance(a, dict): return None
    values = (a.get('block'), a.get('miniBlock'), a.get('shot'))
    if any(type(n) is not int for n in values): return None
    if not (1 <= values[0] <= 24 and 1 <= values[1] <= 4 and 1 <= values[2] <= 25): return None
    return values


def preflight(packet, root):
    errors = []
    if not isinstance(packet, dict) or packet.get('schema') != SCHEMA:
        return {'gate': 'BLOCKED', 'errors': [{'at':'schema','problem':'wrong packet schema'}]}
    for key in ('projectId', 'sourceTitle', 'sourceFormat'):
        if not text_valid(packet.get(key)):
            issue(errors, key, 'must be pinned to an actual authorized source')
    if type(packet.get('sourceRevision')) is not int or packet['sourceRevision'] < 0:
        issue(errors, 'sourceRevision', 'invalid source revision')
    if not sha_valid(packet.get('sourceSha256')):
        issue(errors, 'sourceSha256', 'missing exact source hash')
    # Verify actual creator-authorized screenplay/PPF bytes, not just a copied checksum.
    try:
        src = resolve_file(root, packet.get('sourceFile'))
        if digest(src.read_bytes()) != packet.get('sourceSha256'):
            issue(errors, 'sourceFile', 'actual source-file bytes do not match pinned screenplay SHA-256')
    except (OSError, ValueError, TypeError) as ex:
        issue(errors, 'sourceFile', 'canonical screenplay/PPF original is unavailable: '+str(ex))
    passages = packet.get('passages')
    if not isinstance(passages, list) or not passages:
        issue(errors, 'passages', 'actual screenplay passages with scene and source text are required')
        passages = []
    ids = set()
    scenes = set()
    for i, p in enumerate(passages):
        if not isinstance(p, dict) or not all(text_valid(p.get(k)) for k in ('id','text','scene')):
            issue(errors, f'passages[{i}]', 'passage id, exact source text and scene required')
            continue
        if p['id'] in ids: issue(errors, f'passages[{i}]', 'duplicate source passage id')
        ids.add(p['id']); scenes.add(p['scene'])

    refs = packet.get('approvedReferences')
    if not isinstance(refs, list) or not refs:
        issue(errors, 'approvedReferences', 'approved original character/vehicle/world image required; use design review if none approved')
        refs = []
    ref_ids, attachment_paths = set(), []
    for i, ref in enumerate(refs):
        at = f'approvedReferences[{i}]'
        if not isinstance(ref, dict) or not text_valid(ref.get('id')) or not text_valid(ref.get('role')):
            issue(errors, at, 'reference id and role required'); continue
        if ref['id'] in ref_ids: issue(errors, at, 'duplicate approved reference id')
        ref_ids.add(ref['id'])
        if ref.get('approval') != 'CREATOR_APPROVED':
            issue(errors, at, 'image has no separate creator-approved identity proof')
        m = verify_media(root, ref, at, errors)
        if m: attachment_paths.append(m['path'])
    anchor = packet.get('continuityAnchor')
    if isinstance(anchor, dict) and anchor.get('type') == 'NONE_FIRST_SHOT':
        if not text_valid(anchor.get('reason')): issue(errors, 'continuityAnchor', 'first-shot reason required')
    elif isinstance(anchor, dict) and anchor.get('type') == 'PREVIOUS_SHOT':
        if not text_valid(anchor.get('shotId')):
            issue(errors, 'continuityAnchor', 'previous shot id missing')
        m = verify_media(root, anchor, 'continuityAnchor', errors)
        if m: attachment_paths.append(m['path'])
    else:
        issue(errors, 'continuityAnchor', 'verified previous image or genuine first-shot explanation required')
    shots = packet.get('shots')
    if not isinstance(shots, list) or not 1 <= len(shots) <= 5:
        issue(errors, 'shots', 'batch must contain 1–5 distinct intended shots'); shots = []
    addresses, prompts = [], set()
    for i, shot in enumerate(shots):
        at = f'shots[{i}]'
        if not isinstance(shot, dict):
            issue(errors, at, 'shot must be object'); continue
        a=address(shot)
        if not a: issue(errors, at, 'invalid production address (24×4×25)')
        else: addresses.append(a)
        if not isinstance(shot.get('scriptPassageIds'), list) or not shot['scriptPassageIds']:
            issue(errors, at, 'source passage references missing')
        elif any(pid not in ids for pid in shot['scriptPassageIds']):
            issue(errors, at, 'shot uses passage outside pinned screenplay source')
        for key in ('scene', 'action', 'camera', 'imagePrompt'):
            if not text_valid(shot.get(key)):
                issue(errors, at+'.'+key, 'required scene-specific element missing')
        if text_valid(shot.get('scene')) and shot['scene'] not in scenes:
            issue(errors, at+'.scene', 'scene is not in pinned screenplay passages')
        if not isinstance(shot.get('subjects'), list) or not shot['subjects'] or not all(text_valid(s) for s in shot['subjects']):
            issue(errors, at+'.subjects', 'script-backed subject list missing; use explicit NONE for no visible character')
        if not isinstance(shot.get('mustShow'), list) or not shot['mustShow'] or not all(text_valid(s) for s in shot['mustShow']):
            issue(errors, at+'.mustShow', 'required visible action not specified')
        if not isinstance(shot.get('mustNotShow'), list) or not shot['mustNotShow']:
            issue(errors, at+'.mustNotShow', 'forbidden continuity drift missing')
        used=shot.get('referenceIds')
        if not isinstance(used, list) or not used or any(ref not in ref_ids for ref in used):
            issue(errors, at+'.referenceIds', 'unapproved/unresolved visual reference(s)')
        prompt=shot.get('imagePrompt')
        if text_valid(prompt):
            if BAD_PROMPT.search(prompt):
                issue(errors, at+'.imagePrompt', 'image prompt requests a collage/grid/panels instead of one frame')
            if prompt in prompts:
                issue(errors, at+'.imagePrompt', 'duplicate prompt: shots need distinct narrative actions')
            prompts.add(prompt)
    if addresses and len(addresses) == len(shots):
        first = addresses[0]
        if len(set(addresses)) != len(addresses): issue(errors, 'shots', 'duplicate production address')
        if any(a[:2] != first[:2] for a in addresses):
            issue(errors, 'shots', 'batch crosses Mini-Blocks; separate into source-scoped batches')
        if [a[2] for a in addresses] != list(range(first[2], first[2]+len(shots))):
            issue(errors, 'shots', 'shots out of sequence or have a gap')
        continuation = packet.get('continuation')
        if not isinstance(continuation, dict) or address({'productionAddress':continuation}) != first:
            issue(errors, 'continuation', 'continuation does not match first exact production address')
    response = {'schema':'plotpickle.image-production-preflight.v1', 'gate': 'PASS' if not errors else 'BLOCKED',
         'packetSha256':digest(canonical(packet)), 'projectId':packet.get('projectId'),
         'sourceSha256':packet.get('sourceSha256'), 'shotAddresses':addresses,
         'requiredHostImageAttachments':sorted(set(attachment_paths)),
         'hostMustActuallySupplyVisualBytes':True,
         'warning':'Offline checks do not prove that images were attached to the host image model or that generated pixels match the screenplay',
         'errors':errors}
    return response


def review(packet, results, root):
    pf=preflight(packet, root)
    errors=list(pf.get('errors', []))
    if results.get('schema') != REVIEW_SCHEMA:
        issue(errors, 'schema', 'wrong review schema')
    if results.get('packetSha256') != pf.get('packetSha256'):
        issue(errors, 'packetSha256', 'stale source packet or mismatched review')
    if results.get('projectId') != packet.get('projectId') or results.get('sourceSha256') != packet.get('sourceSha256'):
        issue(errors, 'project', 'wrong project or screenplay version')
    incoming=results.get('shots')
    if not isinstance(incoming, list): incoming=[];issue(errors,'shots','missing results')
    expected=pf.get('shotAddresses',[])
    if len(incoming)!=len(expected): issue(errors,'shots','every requested address needs independent result or UNKNOWN')
    seen_hashes=set()
    output=[]
    for i,s in enumerate(incoming):
        at=f'shots[{i}]'
        if not isinstance(s,dict):issue(errors,at,'result must be object');continue
        a=address(s)
        if i>=len(expected) or a!=expected[i]: issue(errors,at,'wrong candidate-to-shot address')
        status=s.get('semanticState', 'UNKNOWN')
        if status not in STATES:
            issue(errors,at,'invalid semantic state');status='UNKNOWN'
        if status=='DRIFTED' and not text_valid(s.get('reason')):
            issue(errors,at,'DRIFTED needs explicit visible contradiction and evidence')
        if s.get('visualInspectionPerformed') is not True or not text_valid(s.get('inspector')):
            issue(errors,at,'real pixel inspection with inspector attribution not verified')
        if s.get('referenceImagesProvidedToModel') is not True:
            issue(errors,at,'actual reference image bytes not provided to generation host')
        fileinfo=None
        if status!='UNKNOWN' or isinstance(s.get('image'),dict):
            fileinfo=verify_media(root, s.get('image'), at+'.image', errors, require_landscape=True)
        if fileinfo:
            if fileinfo['sha256'] in seen_hashes:
                issue(errors,at,'duplicate image bytes within five-shot batch')
            seen_hashes.add(fileinfo['sha256'])
            if fileinfo['sha256'] in {r.get('sha256') for r in packet.get('approvedReferences',[])}:
                issue(errors,at,'generated frame duplicates design reference original')
            if fileinfo['sha256']==packet.get('continuityAnchor',{}).get('sha256'):
                issue(errors,at,'generated frame repeats previous shot unchanged')
        def strict_true(key):return s.get(key) is True
        # Self-asserted approval / lock booleans never certify a native PPF write.
        # A separate guarded Save -> Lock -> reopen with the canonical reader is required.
        if s.get('usableForProduction') is True:
            issue(errors,at,'cannot claim production-ready from review JSON: native PPF Save/Lock and independent reader receipts are separate')
        output.append({'address':a,'semanticState':status,'mediaSha256':fileinfo['sha256'] if fileinfo else None,
                       'candidateInspectable':bool(fileinfo) and status=='PASS' and not any(e['at'].startswith(at) for e in errors),
                       'productionReady':False, 'nativePpfLockState':'UNVERIFIED_BY_THIS_TOOL'})
    return {'schema':'plotpickle.image-production-postflight.v1', 'gate':'PASS' if not errors else 'BLOCKED',
            'packetSha256':pf.get('packetSha256'),'shots':output,'errors':errors,
            'requiresHumanSemanticReview':True,'nativePpfWritten':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest='command',required=True)
    for name in ('preflight','review'):
        cmd=subs.add_parser(name)
        cmd.add_argument('--packet',required=True)
        cmd.add_argument('--assets-root',required=True)
        cmd.add_argument('--out')
        if name=='review':cmd.add_argument('--results',required=True)
    args=parser.parse_args()
    try:
        packet=json.loads(Path(args.packet).read_text(encoding='utf-8'))
        if args.command=='preflight':report=preflight(packet,args.assets_root)
        else:report=review(packet,json.loads(Path(args.results).read_text(encoding='utf-8')),args.assets_root)
        if args.out:
            target=Path(args.out)
            if target.exists():raise ValueError('refusing to overwrite existing evidence report')
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False))
        return 0 if report['gate']=='PASS' else 2
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as ex:
        print('BLOCKED: '+str(ex),file=sys.stderr)
        return 2


if __name__=='__main__':sys.exit(main())
