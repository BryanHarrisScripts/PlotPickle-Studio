#!/usr/bin/env python3
"""Read-only reconciliation of source-pinned PPF, provider enumeration and Library bytes.
This never calls providers, transfers files, accepts artwork or writes project/editor state.
"""
import argparse, collections, datetime, hashlib, json, pathlib, re


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def sha(value):
    return value.lower().removeprefix('sha256:') if isinstance(value, str) and re.fullmatch(r'(sha256:)?[0-9a-fA-F]{64}', value) else None


def local(root, relative):
    if root is None or not relative: return None, 'not-supplied'
    if not isinstance(relative, str): return None, 'unsafe-path'
    p = pathlib.PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts or '\\' in relative or re.match(r'^[A-Za-z]:', relative): return None, 'unsafe-path'
    root = pathlib.Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root): return None, 'unsafe-path'
    if not target.is_file(): return None, 'missing'
    if not target.stat().st_size: return None, 'empty-file'
    return target, 'present'


def audit(project, project_sha, manifest, root=None):
    if not project.get('id') or type(project.get('revision')) is not int: raise ValueError('Project identity unavailable')
    expected = manifest.get('project', {})
    pinned = expected.get('id') == project['id'] and expected.get('revision') == project['revision'] and sha(expected.get('sha256')) == project_sha
    ar = project.get('assetRegistry') or {}
    mappings = ((ar.get('extensions') or {}).get('storyWorkflow') or {}).get('imageMappings') or []
    by_id = collections.defaultdict(list)
    for m in mappings: by_id[m.get('artifactId')].append(m)
    rows, seen = [], set()
    for a in manifest.get('assets', []):
        aid = a.get('id')
        if not isinstance(aid, str) or not aid or aid in seen: raise ValueError('Missing or duplicate inventory asset id')
        seen.add(aid)
        issues = []
        if not pinned: issues.append('project-version-mismatch')
        lib = a.get('library') or {}
        path, state = local(root, lib.get('localPath'))
        actual_hash = digest(path) if path else None
        actual_size = path.stat().st_size if path else None
        content_hash = sha(a.get('sha256'))
        if not lib.get('fileId'): transfer = 'not-transferred'
        elif state != 'present': transfer = 'library-listed-' + state
        elif not content_hash or type(a.get('bytes')) is not int: transfer = 'source-proof-missing'
        elif actual_hash != content_hash or actual_size != a['bytes']: transfer = 'byte-or-hash-mismatch'
        else: transfer = 'verified-library-bytes'
        if transfer != 'verified-library-bytes': issues.append(transfer)
        mm = by_id.get(a.get('artifactId'), [])
        m = mm[0] if len(mm) == 1 else {}
        if len(mm) > 1: issues.append('ambiguous-shot-registration')
        address = m.get('address')
        if not m: issues.append('shot-registration-missing')
        if m and not m.get('passageIds'): issues.append('screenplay-link-missing')
        still_path, still_state = local(root, m.get('portablePath'))
        still_hash = digest(still_path) if still_path else None
        if m and (still_state != 'present' or not sha(m.get('sha256')) or still_hash != sha(m.get('sha256'))): issues.append('registered-image-unverified')
        approved = m.get('visualApproval') or {}
        human_approved = approved.get('state') == 'approved' and sha(approved.get('approvedCandidateSha256')) is not None and sha(approved.get('approvedCandidateSha256')) == still_hash
        if not human_approved: issues.append('image-approval-evidence-missing')
        if m.get('savedMarkerPresent') is not True: issues.append('project-save-pending')
        if m.get('locked') is not True: issues.append('project-lock-pending')
        submitted = sha(a.get('submittedImageSha256'))
        source_match = submitted == still_hash if submitted and still_hash else None
        if a.get('kind') == 'video' and source_match is not True: issues.append('video-source-image-differs' if source_match is False else 'video-source-image-unknown')
        if a.get('kind') in ('video', 'audio') and (a.get('creativeApproval') != 'approved' or not a.get('creativeApprovalEvidenceRef')): issues.append('media-review-pending')
        if a.get('kind') == 'image' and content_hash != still_hash: issues.append('image-version-differs-from-registered')
        continuity = a.get('continuity', [])
        for c in continuity:
            if c.get('state') not in ('passed', 'not-applicable') or not c.get('evidenceRef') or sha(c.get('imageSha256')) != still_hash:
                issues.append(str(c.get('kind', 'continuity')) + '-review-needed')
        if not continuity: issues.append('continuity-review-unknown')
        # Report the recorded usage only. A path/receipt is not live editor import proof.
        usage = a.get('editorUsage') or {}
        if usage.get('sourceSha256') and sha(usage['sourceSha256']) != content_hash: issues.append('editor-media-version-changed')
        rows.append({'id': aid, 'provider': a.get('provider'), 'providerAssetId': a.get('providerAssetId'),
                     'role': a.get('role', 'original'), 'derivedFrom': a.get('derivedFrom'), 'artifactId': a.get('artifactId'),
                     'address': address, 'library': lib, 'actualBytes': actual_size, 'actualSha256': actual_hash,
                     'transfer': transfer, 'imageApproved': True if human_approved else None, 'ppfSaved': m.get('savedMarkerPresent'),
                     'ppfLocked': m.get('locked'), 'submittedImageMatchesRegistered': source_match,
                     'editorUsage': usage, 'issues': list(dict.fromkeys(issues)), 'readyForEditor': not issues})
    provider_reports = []
    for p in manifest.get('providers', []):
        provider = p.get('provider')
        # Provider ids are namespaced; never match a filename, URL prefix or numeric shot.
        bound = {a.get('providerAssetId') for a in manifest.get('assets', []) if a.get('provider') == provider and a.get('providerAssetId')}
        listed = set(p.get('assetIds', []))
        unassigned = sorted(listed - bound)
        absent = sorted(bound - listed)
        complete = p.get('paginationComplete') is True and p.get('scopeTruncated') is False and bool(p.get('observedAt')) and bool(p.get('scope')) and not p.get('error')
        selected = [r for r in rows if r['provider'] == provider]
        # An empty or failed enumeration must never produce an all-transferred badge.
        all_transferred = complete and bool(selected) and not unassigned and not absent and all(r['transfer'] == 'verified-library-bytes' for r in selected)
        provider_reports.append({'provider': provider, 'scope': p.get('scope'), 'observedAt': p.get('observedAt'),
                                 'enumerationComplete': complete, 'unassignedAssetIds': unassigned,
                                 'registeredButNotEnumerated': absent, 'allTransferredForEnumeratedScope': all_transferred})
    hashes = collections.defaultdict(list)
    for r in rows:
        if r['actualSha256']: hashes[r['actualSha256']].append(r['id'])
    return {'schema': 'plotpickle.asset-handoff-report.v1', 'evaluatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'project': {'id': project['id'], 'revision': project['revision'], 'sha256': project_sha, 'pinMatched': pinned},
            'summary': {'assets': len(rows), 'verifiedLibraryFiles': sum(r['transfer'] == 'verified-library-bytes' for r in rows),
                        'readyForEditor': sum(r['readyForEditor'] for r in rows)}, 'providers': provider_reports, 'assets': rows,
            'identicalContentGroups': [ids for ids in hashes.values() if len(ids) > 1],
            'limits': ['Snapshot, not continuous synchronization.', 'Byte/hash verification is separate from media decoding and visual approval.',
                       'Provider listing coverage is limited to the stated scope and observation time.',
                       'No project, timeline, approval, provider or Library mutations performed.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=pathlib.Path, required=True)
    parser.add_argument('--manifest', type=pathlib.Path, required=True)
    parser.add_argument('--media-root', type=pathlib.Path)
    parser.add_argument('--out', type=pathlib.Path, required=True)
    args = parser.parse_args()
    p = json.loads(args.project.read_text())
    m = json.loads(args.manifest.read_text())
    result = audit(p, digest(args.project), m, args.media_root)
    with args.out.open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, ensure_ascii=False); f.write('\n')

if __name__ == '__main__': main()
