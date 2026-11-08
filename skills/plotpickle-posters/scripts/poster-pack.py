#!/usr/bin/env python3
"""Plan and verify PlotPickle poster campaign packs; never generates image pixels."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LESSON_MAP = ROOT / 'references' / 'curriculum-poster-map.json'
FORMATS = (
    ('theatrical', 1620, 2400, '27:40', 'Key-art focal point with ample top/bottom title/credits space. This is a digital poster proof, not 300-dpi print-ready art.', {'left': 0.08, 'right': 0.08, 'top': 0.08, 'bottom': 0.12}),
    ('square', 1080, 1080, '1:1', 'Recompose into a balanced square. Protect faces and keep one readable focal point, restrained copy and strong title hierarchy.', {'left': 0.08, 'right': 0.08, 'top': 0.08, 'bottom': 0.10}),
    ('portrait-feed', 1080, 1350, '4:5', 'Use vertical negative space and mobile-legible title. Place faces and key props inside safe central composition; do not blind crop.', {'left': 0.07, 'right': 0.07, 'top': 0.08, 'bottom': 0.11}),
    ('story-reel', 1080, 1920, '9:16', 'Reframe subject for vertical viewing. Keep titles, CTA and faces clear of platform-specific top/bottom interactive overlays.', {'left': 0.10, 'right': 0.10, 'top': 0.15, 'bottom': 0.20}),
)
ALLOWED_TYPES = {'official', 'teaser', 'character', 'ensemble', 'scene', 'world'}
REQUIRED_KEYS = {'title'}
ALLOWED_BRIEF_KEYS = {
    'title','campaign','posterType','tagline','logline','audience','genre','tone','visualDirection',
    'subjects','callToAction','releaseText','credits','source','referenceAssets','copyApproval'
}

class CampaignError(ValueError):
    pass


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        raise CampaignError(f'Invalid JSON input: {e}') from e
    if not isinstance(data, dict):
        raise CampaignError('Expected a JSON object')
    return data


def canonical_file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def slug(text: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9]+', '-', text.strip()).strip('-')[:70]
    return cleaned or 'Untitled'


def safe_filename(title: str, campaign: str, poster_type: str, fmt: str, width: int, height: int) -> str:
    return f'{slug(title)}_{slug(campaign)}_{slug(poster_type)}_{fmt}_v01_{width}x{height}.png'


def checked_source(brief: dict, brief_path: Path) -> dict:
    source = brief.get('source')
    if source is None:
        return {'status': 'unbound-proposal', 'message': 'No saved project supplied; story facts and visual directions are proposals.'}
    if not isinstance(source, dict) or not {'file', 'sha256', 'projectId', 'revision'} <= set(source):
        raise CampaignError('source requires file, sha256, projectId and revision')
    file_path = Path(source['file'])
    if not file_path.is_absolute():
        file_path = (brief_path.parent / file_path).resolve()
    if not file_path.is_file():
        raise CampaignError('Pinned project file does not exist')
    expected = str(source['sha256']).lower()
    if not re.fullmatch(r'[0-9a-f]{64}', expected):
        raise CampaignError('source.sha256 must contain exactly 64 hex characters')
    actual = canonical_file_hash(file_path)
    if actual != expected:
        raise CampaignError('Project source SHA-256 mismatch (fail closed)')
    saved = read_json(file_path)
    id_seen = saved.get('projectId', saved.get('id'))
    rev_seen = saved.get('revision')
    if id_seen is not None and str(id_seen) != str(source['projectId']):
        raise CampaignError('Project ID does not match pinned file')
    if rev_seen is not None and str(rev_seen) != str(source['revision']):
        raise CampaignError('Project revision does not match pinned file')
    return {
        'status': 'source-bytes-verified', 'file': str(file_path), 'sha256': actual,
        'declaredProjectId': source['projectId'], 'declaredRevision': source['revision'],
        'projectIdChecked': id_seen is not None, 'projectRevisionChecked': rev_seen is not None,
        'passageIds': source.get('passageIds', []),
        'message': 'Project file bytes pinned. Story assertions and referenced passages still need independent review.'
    }


def validate_brief(brief: dict) -> None:
    extras = set(brief) - ALLOWED_BRIEF_KEYS
    if extras:
        raise CampaignError(f'Unsupported brief keys: {sorted(extras)}')
    if not isinstance(brief.get('title'), str) or not brief['title'].strip():
        raise CampaignError('A real, nonempty title is required')
    if len(brief['title']) > 200:
        raise CampaignError('Title is too long')
    if brief.get('posterType', 'official') not in ALLOWED_TYPES:
        raise CampaignError('Invalid posterType')
    if brief.get('copyApproval', 'draft') not in ('draft', 'approved'):
        raise CampaignError('copyApproval must be draft or approved')
    for field in ('campaign','tagline','logline','audience','genre','tone','visualDirection','callToAction','releaseText'):
        if field in brief and not isinstance(brief[field], str):
            raise CampaignError(f'{field} must be text')
    if 'subjects' in brief and (not isinstance(brief['subjects'], list) or not all(isinstance(v, str) for v in brief['subjects'])):
        raise CampaignError('subjects must be a list of strings')
    if 'credits' in brief and (not isinstance(brief['credits'], list) or not all(isinstance(v, str) for v in brief['credits'])):
        raise CampaignError('credits must be a list of strings')
    if 'referenceAssets' in brief:
        if not isinstance(brief['referenceAssets'], list):
            raise CampaignError('referenceAssets must be a list')
        for asset in brief['referenceAssets']:
            if not isinstance(asset, dict) or asset.get('approval') not in ('approved', 'proposed', 'unverified') or not asset.get('id'):
                raise CampaignError('Reference assets require an id and explicit approval status')


def lesson_refs() -> list:
    records = read_json(LESSON_MAP).get('references')
    if not isinstance(records, list) or len(records) < 5:
        raise CampaignError('Bundled poster lesson map is incomplete')
    for record in records:
        if not {'topic', 'lessonId', 'number', 'title', 'section'} <= set(record):
            raise CampaignError('Bundled lesson map is malformed')
    return records


def plan(brief: dict, brief_path: Path) -> dict:
    validate_brief(brief)
    source = checked_source(brief, brief_path)
    campaign = brief.get('campaign') or 'Key Art'
    poster_type = brief.get('posterType') or 'official'
    outputs = []
    for fmt, width, height, ratio, direction, safe in FORMATS:
        outputs.append({
            'id': fmt, 'width': width, 'height': height, 'ratio': ratio,
            'filename': safe_filename(brief['title'], campaign, poster_type, fmt, width, height),
            'status': 'planned', 'printReady': False,
            'compositionNotes': direction, 'copySafeArea': safe,
        })
    return {
        'schemaVersion': '1.0', 'status': 'planned',
        'campaignId': f'{slug(brief["title"])}-{slug(campaign)}-{slug(poster_type)}-v01',
        'brief': brief, 'source': source,
        'curriculumReferences': lesson_refs(), 'curriculumVerification': 'required-before-creative-use',
        'rightsReview': 'pending', 'marketingReview': 'pending',
        'exportsArePrintReady': False,
        'outputs': outputs,
    }


def save_new_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def inspect_png(path: Path) -> tuple[int,int,str]:
    if path.stat().st_size > 128*1024*1024:
        raise CampaignError('Image exceeds 128-MiB verification limit')
    with path.open('rb') as inp:
        head = inp.read(24)
    if len(head) < 24 or head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR':
        raise CampaignError('Not a recognizable PNG')
    width = int.from_bytes(head[16:20], 'big')
    height = int.from_bytes(head[20:24], 'big')
    if width < 1 or height < 1:
        raise CampaignError('Invalid PNG dimensions')
    try:
        from PIL import Image
    except ImportError:
        return width, height, 'header-only-unverified-decode'
    try:
        with Image.open(path) as im:
            if im.format != 'PNG':
                raise CampaignError('Image encoding does not match PNG suffix')
            im.verify()
        with Image.open(path) as im:
            im.load()
            if im.size != (width,height):
                raise CampaignError('Image size changed between header and full decode')
        return width, height, 'fully-decoded'
    except (OSError, ValueError) as e:
        raise CampaignError(f'Image failed full decode: {e}') from e


def inspect(plan_data: dict, assets_dir: Path) -> dict:
    outputs = plan_data.get('outputs')
    if not isinstance(outputs, list) or [x.get('id') for x in outputs] != [f[0] for f in FORMATS]:
        raise CampaignError('Plan has missing or reordered output definitions')
    expected_files = [x['filename'] for x in outputs]
    if len(set(expected_files)) != len(expected_files):
        raise CampaignError('Duplicate planned output filenames')
    results = []
    for item, fmt in zip(outputs,FORMATS):
        if (item['width'],item['height']) != (fmt[1],fmt[2]) or item['filename'] != safe_filename(plan_data['brief']['title'],plan_data['brief'].get('campaign') or 'Key Art',plan_data['brief'].get('posterType') or 'official',fmt[0],fmt[1],fmt[2]):
            raise CampaignError(f'Plan output {item["id"]} differs from canonical dimensions or filename')
        path = assets_dir / item['filename']
        if not path.is_file():
            results.append({'id':item['id'],'status':'missing','filename':item['filename']})
            continue
        try:
            width,height,check = inspect_png(path)
            if (width,height) != (item['width'],item['height']):
                raise CampaignError(f'Expected {item["width"]}x{item["height"]}, found {width}x{height}')
            results.append({'id':item['id'], 'status':'bytes-verified' if check=='fully-decoded' else 'unverified-decode',
                            'decode':check,'filename':item['filename'],'sha256':canonical_file_hash(path)})
        except (OSError,CampaignError) as e:
            results.append({'id':item['id'],'status':'invalid','reason':str(e),'filename':item['filename']})
    return {'campaignId': plan_data['campaignId'], 'outputs':results,
            'allBytesVerified': len(results)==4 and all(x['status']=='bytes-verified' for x in results),
            'marketingApproval':plan_data.get('marketingReview','pending'),
            'rightsApproval':plan_data.get('rightsReview','pending')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command',required=True)
    commands.add_parser('formats')
    create = commands.add_parser('plan')
    create.add_argument('--brief', required=True, type=Path)
    create.add_argument('--out', required=True, type=Path)
    check = commands.add_parser('inspect')
    check.add_argument('--plan', required=True, type=Path)
    check.add_argument('--assets-dir', required=True, type=Path)
    pack = commands.add_parser('package')
    pack.add_argument('--plan', required=True, type=Path)
    pack.add_argument('--assets-dir', required=True, type=Path)
    pack.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'formats':
            payload = [{'id':f[0],'width':f[1],'height':f[2],'ratio':f[3]} for f in FORMATS]
        elif args.command == 'plan':
            payload = plan(read_json(args.brief),args.brief)
            save_new_json(args.out,payload)
        else:
            p = read_json(args.plan)
            payload = inspect(p,args.assets_dir)
            if args.command == 'package':
                if not payload['allBytesVerified']:
                    raise CampaignError('Package blocked: all four actual PNG files must be fully decoded and dimension-verified')
                args.out.parent.mkdir(parents=True,exist_ok=True)
                with args.out.open('xb') as output:
                    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
                        z.write(args.plan,'campaign-plan.json')
                        z.writestr('verification.json',json.dumps(payload,indent=2))
                        for item in payload['outputs']:
                            z.write(args.assets_dir/item['filename'],'art/'+item['filename'])
                payload['archive'] = str(args.out)
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        return 0
    except (CampaignError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'ok':False,'error':str(e)}),file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
