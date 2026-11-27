#!/usr/bin/env python3
"""Non-destructive creator approval / image / native PPF lock truth gate.

It inventories planned positions and evidence. It NEVER modifies a PPF or grants a lock.
Native lock claims require an independently loaded matching native PPF and original
image bytes. A filename, creator blanket approval, or historical record does not count.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter

HEX = set('0123456789abcdef')
SAVE = 'storyboard-local-save:v1'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1024 * 1024), b''):
            h.update(c)
    return h.hexdigest()


def is_hex(v):
    return isinstance(v, str) and len(v) == 64 and set(v) <= HEX


def addr(row):
    return int(row['block']), int(row['miniBlock']), int(row['shot'])


def expect_slots(scope):
    blocks = scope.get('blocks') or list(range(1, int(scope['blockCount']) + 1))
    return [(b, m, s) for b in blocks
            for m in range(1, int(scope['miniBlocksEach']) + 1)
            for s in range(1, int(scope['shotsPerMiniBlock']) + 1)]


def native_index(ppf):
    f = ppf.get('build', {}).get('foundations', {})
    arts = {x.get('id'): x for x in f.get('visualArtifacts', []) if isinstance(x, dict)}
    accepted = set(f.get('acceptedVisualArtifactIds', []))
    maps = ppf.get('assetRegistry', {}).get('extensions', {}).get('storyWorkflow', {}).get('imageMappings', [])
    results = {}
    for entry in maps:
        a = entry.get('address', {})
        try:
            key = int(a['blockNumber']), int(a['miniBlockNumber']), int(a['shotNumber'])
        except (ValueError, KeyError, TypeError):
            continue
        if key in results:
            raise ValueError(f'duplicate native PPF mapping: {key}')
        art = arts.get(entry.get('artifactId'))
        coherent = (isinstance(art, dict) and entry.get('savedMarkerPresent') is True
            and entry.get('locked') is True and SAVE in art.get('sourceDecisionKeys', [])
            and art.get('reviewState') == 'accepted' and art.get('id') in accepted
            and art.get('id') == entry.get('artifactId'))
        results[key] = {'coherent':bool(coherent), 'entry':entry,'artifact':art}
    return results


def decode_media(path):
    try:
        from PIL import Image
        with Image.open(path) as im: im.verify()
        with Image.open(path) as im:
            im.load()
            return im.width, im.height
    except (OSError, ValueError, ImportError):
        return None


def validate(manifest, ppf_path=None, media_root=None):
    scope = manifest['scope']
    expected = expect_slots(scope)
    if len(expected) != len(set(expected)):
        raise ValueError('duplicate scope coordinates')
    rows = manifest['positions']
    if len(rows) != len(expected):
        raise ValueError(f'{len(rows)} rows for {len(expected)} expected positions')
    keyed = {}
    for item in rows:
        key = addr(item)
        if key in keyed:
            raise ValueError(f'duplicate position: {key}')
        keyed[key] = item
    if set(keyed) != set(expected):
        raise ValueError('manifest has missing / out-of-scope positions')
    ppf = None; ppfdigest = None; mapped = {}
    if ppf_path:
        ppfdigest = sha256(ppf_path)
        ppf = json.loads(Path(ppf_path).read_text(encoding='utf-8'))
        mapped = native_index(ppf)
        project_id = manifest.get('project', {}).get('id')
        if project_id and ppf.get('id') != project_id:
            raise ValueError('project ID conflict with original PPF')
    # No guessed native locks when PPF absent, or image bytes inaccessible.
    results = []
    counts = Counter()
    for key in expected:
        item = keyed[key]
        original_hash = item.get('originalSha256')
        history = item.get('originalStatus', 'UNKNOWN')
        human = item.get('creatorApproval', 'unknown')
        authorization = bool(human and human not in ('unknown', 'not_approved', 'rejected'))
        # Set requested approval separately: does not create a usable media candidate.
        user_authorizes = bool(manifest.get('creatorInstruction')) or authorization
        rejected = ('DRIFTED' in str(history).upper() or 'REJECTED' in str(history).upper()
                    or item.get('visualStatus') in ('DRIFTED', 'REJECTED'))
        has_historical_media = is_hex(original_hash) and not rejected and 'missing' not in str(history).lower()
        media_now = False
        actual_hash = None
        media_file = None
        if media_root and has_historical_media:
            candidate = (Path(media_root) / (item.get('originalFilename') or '')).resolve()
            root = Path(media_root).resolve()
            if root == candidate or root not in candidate.parents:
                raise ValueError(f'unsafe media path for {key}')
            if candidate.is_file():
                actual_hash = sha256(candidate)
                media_now = actual_hash == original_hash and decode_media(candidate) is not None
                media_file = str(candidate.relative_to(root))
        native = mapped.get(key)
        ppf_locked_marker = bool(native and native['coherent'])
        # Proof of actual byte-matched original required for native lock verification.
        native_verified = bool(ppf_locked_marker and media_now and
            native['entry'].get('sha256') == actual_hash)
        # Historical approval/marker fields never count as actual native locked.
        issue = ('DRIFTED_OR_REJECTED' if rejected else
                 'NO_RECOVERED_USABLE_ORIGINAL' if not has_historical_media else
                 'NOT_VERIFIED_NATIVE_LOCK' if not native_verified else 'NONE')
        r = {'block':key[0],'miniBlock':key[1],'shot':key[2],
             'creatorApprovalAuthorized':user_authorizes,'originalEvidenceFromHistory':has_historical_media,
             'originalSha256':original_hash if has_historical_media else None,
             'originalVerifiedThisRun':media_now,'nativePpfLockMarkerCoherent':ppf_locked_marker,
             'nativePpfLockByteVerified':native_verified,'issue':issue,
             'historicalOriginalStatus':history}
        if media_file: r['localMediaFile'] = media_file
        results.append(r)
        counts[issue] += 1
    groups=[]
    for b in scope['blocks']:
        for m in range(1,int(scope['miniBlocksEach'])+1):
            selected=[r for r in results if r['block']==b and r['miniBlock']==m]
            groups.append({'block':b,'miniBlock':m,'total':len(selected),
                           'recoveredEvidence':sum(bool(r['originalEvidenceFromHistory']) for r in selected),
                           'verifiedNativeLocks':sum(bool(r['nativePpfLockByteVerified']) for r in selected),
                           'unresolved':[r['shot'] for r in selected if r['issue'] != 'NONE']})
    return {'schema':'plotpickle.approval-truth-audit.v1',
            'project':manifest.get('project'),'sourcePpfSha256Actual':ppfdigest,
            'scope':scope, 'status':'COMPLETE' if counts.get('NONE',0)==len(expected) else 'BLOCKED',
            'counts':{'target':len(expected),'creatorAuthorized':sum(r['creatorApprovalAuthorized'] for r in results),
                      'historicalImageEvidence':sum(r['originalEvidenceFromHistory'] for r in results),
                      'verifiedImagesThisRun':sum(r['originalVerifiedThisRun'] for r in results),
                      'nativeLocksFullyVerified':sum(r['nativePpfLockByteVerified'] for r in results),
                      'issues':dict(counts)},
            'groups':groups,'positions':results,
            'limitations':['Read-only: does not apply approvals or native Save/Lock.',
                           'Historical file markers are not native locks.',
                           'Live Studio status and Library persistence require independent readback from their hosts.',
                           'Missing originals or previously rejected images cannot be made valid through blanket approval.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--ppf')
    ap.add_argument('--media-root')
    ap.add_argument('--out',required=True)
    ap.add_argument('--require-complete',action='store_true')
    args=ap.parse_args()
    try:
        v=validate(json.loads(Path(args.manifest).read_text(encoding='utf-8')),args.ppf,args.media_root)
        target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'status':v['status'],'counts':v['counts'],'out':str(target)},ensure_ascii=False))
        return 2 if args.require_complete and v['status']!='COMPLETE' else 0
    except (OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'status':'INVALID_EVIDENCE','error':str(e)}))
        return 3

if __name__=='__main__':
    raise SystemExit(main())
