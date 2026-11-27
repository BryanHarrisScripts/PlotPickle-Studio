#!/usr/bin/env python3
"""Compact, version-linked, non-archiving PlotPickle release ledger validation.

The live Site/MCP publisher must invoke the gate separately; this tool cannot
alter deployed Sites or override a host-side release action.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / 'references' / 'release-index.v1.json'
VERSION = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
STATES = ('DRAFT', 'TESTED', 'LOCKED', 'RELEASED')


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def stamp(record):
    data = {k: v for k, v in record.items() if k != 'recordDigest'}
    return hashlib.sha256(canonical(data)).hexdigest()


def version_key(version):
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise ValueError(f'Invalid semver: {version!r}')
    return tuple(map(int, version.split('.')))


def load(path=INDEX):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate(index):
    if index.get('schema') != 'plotpickle.engineering.release-index.v1':
        raise ValueError('wrong release index schema')
    if index.get('storagePolicy', {}).get('customArchivesPerRelease') != 0:
        raise ValueError('cannot create redundant release archives')
    if index.get('storagePolicy', {}).get('bundlePrivateProjectAssets') is not False:
        raise ValueError('private story data may not enter release index')
    records = index.get('releases')
    if not isinstance(records, list) or not records:
        raise ValueError('releases must be a nonempty list')
    previous = None
    for rec in records:
        version = rec.get('version')
        current = version_key(version)
        if previous is not None and current <= previous:
            raise ValueError('duplicate or unordered release version')
        previous = current
        if rec.get('state') not in STATES:
            raise ValueError(f'invalid state for {version}')
        if rec.get('recordDigest') != stamp(rec):
            raise ValueError(f'ledger checksum mismatch at {version}')
        if not isinstance(rec.get('surfaceLockRefs'), list) or not isinstance(rec.get('patternRefs'), list):
            raise ValueError(f'missing engineering references for {version}')
        if not isinstance(rec.get('inventionRefs'), list) or not isinstance(rec.get('patentFilingRefs'), list):
            raise ValueError(f'missing invention/patent refs for {version}')
        for ref in rec['patentFilingRefs']:
            if not isinstance(ref, dict) or not ref.get('verifiedFilingReference'):
                raise ValueError('patent filings require external verification reference')
        if rec['state'] in ('LOCKED', 'RELEASED'):
            check_lock(rec)
        if rec['state'] == 'RELEASED' and rec.get('deploymentVerified') is not True:
            raise ValueError('released state requires independent deployment evidence')
    if index.get('currentVersion') != records[-1]['version']:
        raise ValueError('current version must match final record')
    return True


def check_lock(rec):
    version = rec['version']
    checks = rec.get('checks') or {}
    missing = [f for f in ('unit', 'integration', 'preservation') if checks.get(f) is not True]
    for field in ('sourceFingerprint', 'ownerReleaseApproval', 'rollbackRef'):
        if not rec.get(field):
            missing.append(field)
    if not rec.get('surfaceLockRefs') or not rec.get('patternRefs'):
        missing.append('engineering references')
    if missing:
        raise ValueError(f'{version} release lock blocked: '+', '.join(missing))
    return True


def append(index, rec):
    validate(index)
    existing = {x['version'] for x in index['releases']}
    if rec['version'] in existing:
        raise ValueError('append only: version already exists')
    if version_key(rec['version']) <= version_key(index['currentVersion']):
        raise ValueError('new version must increase semver')
    if rec.get('state') in ('LOCKED', 'RELEASED'):
        raise ValueError('append accepts draft/tested only; do not auto-lock or release')
    copy = json.loads(json.dumps(index))
    rec = {k: v for k, v in rec.items() if k != 'recordDigest'}
    rec['recordDigest'] = stamp(rec)
    copy['releases'].append(rec)
    copy['currentVersion'] = rec['version']
    validate(copy)
    return copy


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['validate', 'check', 'append'])
    p.add_argument('--version')
    p.add_argument('--record', type=Path)
    p.add_argument('--index', type=Path, default=INDEX)
    args = p.parse_args()
    try:
        index = load(args.index)
        validate(index)
        if args.command == 'check':
            record = next((x for x in index['releases'] if x['version'] == args.version), None)
            if record is None:
                raise ValueError('unknown release version')
            if record['state'] not in ('LOCKED', 'RELEASED'):
                raise ValueError('candidate is not creator-locked; release blocked')
            check_lock(record)
        elif args.command == 'append':
            if not args.record:
                raise ValueError('--record required')
            record = json.loads(args.record.read_text(encoding='utf-8'))
            output = append(index, record)
            # A tiny single-file ledger; no per-release archive or duplicate DB.
            args.index.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('PASS:', args.command)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print('BLOCKED:', e, file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
