#!/usr/bin/env python3
"""Read-only source-PFF-to-chat-inspector adapter. Never modifies a source or Studio.

Produces one 25-shot mini-block snapshot with independently pinned JSON bytes.
Does not fetch media, perform GUI actions, request generation, or approve locks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path


class ReviewSourceError(ValueError):
    pass


def extract_source_snapshot(data: bytes, *, expected_sha256: str, block: int = 1, mini: int = 1) -> dict:
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ReviewSourceError('PPF SHA-256 mismatch; no snapshot produced')
    try:
        ppf = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReviewSourceError('Invalid PPF JSON') from error

    if not (isinstance(ppf, dict) and isinstance(ppf.get('assetRegistry'), dict)):
        raise ReviewSourceError('Missing PPF asset registry')
    workflow = ppf['assetRegistry'].get('extensions', {}).get('storyWorkflow', {})
    plans = workflow.get('plans', [])
    target = [p for p in plans if p.get('address', {}).get('blockNumber') == block and p.get('address', {}).get('miniBlockNumber') == mini]
    if len(target) != 1:
        raise ReviewSourceError('Exactly one source-backed mini-block plan required')
    plan = target[0]
    mappings = [m for m in workflow.get('imageMappings', []) if m.get('address', {}).get('blockNumber') == block and m.get('address', {}).get('miniBlockNumber') == mini]
    by_number = {}
    for m in mappings:
        num = m.get('address', {}).get('shotNumber')
        if not isinstance(num, int) or not 1 <= num <= 25 or num in by_number:
            raise ReviewSourceError('Invalid or duplicate shot mapping')
        by_number[num] = m
    planned = {}
    for shot in plan.get('shots', []):
        num = shot.get('shotNumber')
        if not isinstance(num, int) or not 1 <= num <= 25 or num in planned:
            raise ReviewSourceError('Invalid or duplicate planned shot')
        planned[num] = shot
    labels = {}
    for asset in ppf['assetRegistry'].get('assets', []):
        if asset.get('kind') == 'image' and asset.get('id', '').startswith('asset-'):
            labels[asset.get('id')[6:]] = asset.get('label', '')
    authored_beats = workflow.get('authoredBeats', [])
    rows = []
    for num in range(1, 26):
        shot = planned.get(num, {})
        mapped = by_number.get(num, {})
        label = labels.get(mapped.get('artifactId'), '')
        title = label.split(': ', 1)[-1] if ': ' in label else f'Shot {num:02d}'
        visual_approval = mapped.get('visualApproval') or {}
        rows.append({
            'shot': num,
            'page': ((num-1)//5)+1,
            'title': title,
            'planPurpose': shot.get('narrativePurpose') or None,
            'cameraPlan': shot.get('composition') or None,
            'passageIds': mapped.get('passageIds') or shot.get('passageIds') or [],
            'nativePpfSavedMarker': bool(mapped.get('savedMarkerPresent')),
            'nativePpfLocked': bool(mapped.get('locked')),
            'visualApproval': visual_approval.get('state', 'not-recorded'),
            'packageBytesVerifiedFlag': bool(mapped.get('packageBytesVerified')),
            'liveMediaBytesVerifiedFlag': bool(mapped.get('liveMediaBytesVerified')),
            'mediaSha256': mapped.get('sha256'),
            'promptOrigin': shot.get('prompt', '').split('. ', 1)[0] if shot.get('prompt', '').startswith('RECONSTRUCTED') else 'not-specified',
            # Do not infer Studio BEATs from PPF: those are separate saved records.
            'nativePpfAuthoredBeatKnown': any(isinstance(b, dict) and (b.get('shotNumber') == num or b.get('address', {}).get('shotNumber') == num) for b in authored_beats),
        })
    summary = {
        'registeredMappings': len(by_number),
        'plannedSlots': len(planned),
        'sourcePpfSaved': sum(x['nativePpfSavedMarker'] for x in rows),
        'sourcePpfLocked': sum(x['nativePpfLocked'] for x in rows),
        'explicitHumanVisualApproval': sum(x['visualApproval'] == 'approved' for x in rows),
        'pendingVisualReview': sum(x['visualApproval'] == 'pending-user-review' for x in rows),
        'sourceNativeAuthoredBeats': sum(x['nativePpfAuthoredBeatKnown'] for x in rows),
    }
    return {
        'schema':'plotpickle.chat-inspector.source-snapshot.v1',
        'readOnly':True,
        'source':{'title':ppf.get('title'),'projectId':ppf.get('id'),'revision':ppf.get('revision'),'sha256':actual_sha256},
        'address':{'block':block,'miniBlock':mini},
        'summary':summary,
        'shots':rows,
        'truthBoundary': 'PPF source fields only; not a live Studio-sidecar BEAT, hosted image readback, or approved native write',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ppf', type=Path)
    parser.add_argument('--sha256', required=True, help='Exact expected hash of source PPF JSON bytes')
    parser.add_argument('--block', type=int, default=1)
    parser.add_argument('--mini', type=int, default=1)
    args = parser.parse_args()
    result = extract_source_snapshot(args.ppf.read_bytes(),expected_sha256=args.sha256, block=args.block, mini=args.mini)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
