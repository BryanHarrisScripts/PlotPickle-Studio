"""Offline screenplay/idea -> canonical project -> evidence-bound storyboard workflow.

No network or model calls. Agent-authored story decisions are validated as proposals,
not proved by arithmetic. Output directories must not exist (atomic snapshots).
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
MAX_BYTES = 20 * 1024 * 1024
MAX_PASSAGES = 2500


def fail(code):
    raise ValueError(code)


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    p = Path(path)
    if p.stat().st_size > MAX_BYTES:
        fail('INPUT_TOO_LARGE')
    return p.read_bytes()


def read_json(path):
    return json.loads(read_bytes(path))


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def nonblank(value, limit=8000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        fail('INVALID_TEXT_FIELD')
    return value.strip()


def call_node(script, *args):
    result = subprocess.run(['node', str(HERE / script), *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        fail('CANONICAL_READER_REJECTED: ' + (result.stdout or result.stderr).strip()[:500])
    return json.loads(result.stdout)


def identity(path):
    return call_node('inspect-project.mjs', '--file', path, '--operation', 'identity')['project']


def pinned(args):
    data = read_bytes(args.project)
    ident = identity(args.project)
    if digest(data) != ident['sha256'] or (args.project_id, args.revision, args.sha256) != (ident['id'], ident['revision'], ident['sha256']):
        fail('STALE_PROJECT_SNAPSHOT')
    raw = json.loads(data)
    if raw.get('format') == 'plotpickle-explicit-project-export':
        raw = raw['project']
    return raw, ident


def workflow(project):
    ext = project.setdefault('assetRegistry', {'version': '1.0.0', 'assets': [], 'extensions': {}}).setdefault('extensions', {})
    return ext.setdefault('storyWorkflow', {'version': 1, 'plans': [], 'imageMappings': [], 'truths': []})


def address(block, mini, shot=None):
    if type(block) is not int or type(mini) is not int or not 1 <= block <= 24 or not 1 <= mini <= 4:
        fail('INVALID_ADDRESS')
    a = dict(actNumber=(block - 1) // 6 + 1, sequenceNumber=(block - 1) // 2 + 1, blockNumber=block, miniBlockNumber=mini)
    if shot is not None:
        if type(shot) is not int or not 1 <= shot <= 25:
            fail('INVALID_SHOT')
        a['shotNumber'] = shot
    return a


def anchor(block, mini):
    return f'storyboard-anchor:block:block-{block:02}:mini-{mini}'


def source(project):
    s = project.get('sourceEvidence', {}).get('screenplay')
    if not s or not s.get('passages'):
        fail('SCREENPLAY_REQUIRED_BEFORE_SHOTS')
    if s.get('passagesTruncated'):
        fail('TRUNCATED_SOURCE_REQUIRES_REVIEW')
    return s


def parse_fdx(path):
    data = read_bytes(path)
    markup_probe = data.replace(b'\x00', b'').upper()
    if b'<!DOCTYPE' in markup_probe or b'<!ENTITY' in markup_probe:
        fail('XML_ENTITIES_NOT_SUPPORTED')
    root = ET.fromstring(data)
    local = lambda e: e.tag.split('}')[-1]
    if local(root) != 'FinalDraft':
        fail('NOT_FINAL_DRAFT_XML')
    contents = [e for e in root if local(e) == 'Content']
    if len(contents) != 1:
        fail('SCREENPLAY_CONTENT_UNVERIFIABLE')
    types = {'Scene Heading': 'scene-heading', 'Character': 'character', 'Dialogue': 'dialogue',
             'Action': 'action', 'Parenthetical': 'parenthetical', 'Transition': 'transition'}
    originals, segments = [], []
    scene = 0
    # Only screenplay body paragraphs, including dual-dialogue containers; not title pages or notes.
    def paragraphs(e):
        for child in e:
            if local(child) == 'Paragraph':
                yield child
            elif local(child) in ('DualDialogue', 'Content'):
                yield from paragraphs(child)
    for paragraph in paragraphs(contents[0]):
        text = ''.join(''.join(e.itertext()) for e in paragraph if local(e) == 'Text')
        if not text.strip():
            continue
        kind = types.get(paragraph.get('Type', ''), 'note')
        if kind == 'scene-heading':
            scene += 1
        original_id = f'fdx-paragraph-{len(originals) + 1}'
        originals.append({'id': original_id, 'type': kind, 'fdxType': paragraph.get('Type', ''), 'text': text, 'sceneNumber': scene})
        remaining = clean(text)
        # Canonical PPF passage limit is 800 characters. Preserve original text above,
        # split without dropping characters, and verify the normalization round trip.
        part = 0
        while remaining:
            cut = len(remaining) if len(remaining) <= 780 else remaining.rfind(' ', 0, 781)
            if cut < 1:
                cut = 780
            part += 1
            fragment, remaining = remaining[:cut], remaining[cut:].lstrip()
            segments.append({'id': f'screenplay-{len(segments) + 1}', 'type': kind, 'text': fragment,
                             'sceneNumber': scene, 'sceneId': f'scene-{scene:04}' if scene else None,
                             'originalParagraphId': original_id, 'part': part})
    if not segments:
        fail('EMPTY_SCREENPLAY')
    if len(segments) > MAX_PASSAGES:
        fail('SOURCE_EXCEEDS_CANONICAL_CAPACITY_NO_TRUNCATION_WRITTEN')
    return data, originals, segments


def copy_portable_assets(project, project_path, staging):
    missing = []
    base = Path(project_path).resolve().parent
    for asset in project.get('assetRegistry', {}).get('assets', []):
        for variation in asset.get('variations', []):
            rel = variation.get('portablePath', '')
            if not rel:
                continue
            path = Path(rel)
            if path.is_absolute() or '..' in path.parts:
                fail('UNSAFE_PORTABLE_PATH')
            candidate = (base / path).resolve()
            if not candidate.is_relative_to(base):
                fail('UNSAFE_PORTABLE_PATH')
            if candidate.is_file():
                target = staging / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(candidate, target)
            else:
                missing.append(rel)
    return sorted(set(missing))


def save_snapshot(args, project, extras=None, create=False):
    dest = Path(args.out).resolve()
    if dest.exists():
        fail('OUTPUT_DIRECTORY_EXISTS')
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.story-workflow-', dir=dest.parent))
    try:
        extras = extras or {}
        missing = copy_portable_assets(project, args.project, temporary) if getattr(args, 'project', None) else []
        for relative, data in extras.items():
            path = temporary / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))
        seed = temporary / '.seed.json'
        seed.write_text(json.dumps(project, ensure_ascii=False))
        target = temporary / 'project.ppf.json'
        call_node('project-bridge.mjs', '--file', seed, '--out', target, '--operation', 'create' if create else 'validate')
        seed.unlink()
        normalized = read_json(target)
        for key in ('sourceEvidence',):
            before = project.get(key, {}).get('screenplay')
            after = normalized.get(key, {}).get('screenplay')
            if before and (len(before['passages']) != len(after['passages']) or
                           [(p['id'], clean(p['text'])) for p in before['passages']] != [(p['id'], p['text']) for p in after['passages']]):
                fail('CANONICAL_SOURCE_LOSS_BLOCKED')
        before_prompts = project.get('production', {}).get('storyboardImagePrompts', [])
        after_prompts = normalized.get('production', {}).get('storyboardImagePrompts', [])
        if len(before_prompts) != len(after_prompts):
            fail('CANONICAL_PROMPT_LOSS_BLOCKED')
        before_images = project.get('build', {}).get('foundations', {}).get('visualArtifacts', [])
        after_images = normalized.get('build', {}).get('foundations', {}).get('visualArtifacts', [])
        if {x['id'] for x in before_images} != {x['id'] for x in after_images}:
            fail('CANONICAL_IMAGE_LOSS_BLOCKED')
        if not create:
            # Validate through the canonical parser, but preserve the existing export's
            # unrelated fields verbatim. Normalizer whitespace cleanup is not an edit
            # the user requested merely by planning another Mini-Block.
            target.write_text(json.dumps(project, ensure_ascii=False, indent=2) + '\n')
        ident = identity(target)
        receipt = {'version': 1, 'project': ident, 'liveApplicationUpdated': False,
                   'missingPortableAssets': missing, 'runtimeMeasured': False,
                   'plannedStructure': {'acts': 4, 'sequences': 12, 'blocks': 24, 'miniBlocks': 96, 'shotsPerMiniBlock': 25},
                   'canonicalBaselineShotSeconds': 3, 'canonicalBaselineMiniBlockSeconds': 75,
                   'projectRuntimePlan': normalized.get('assetRegistry', {}).get('extensions', {}).get('projectModel', {}).get('runtimePlan'),
                   'persistenceConfirmed': False, 'note': 'Local snapshot only. Confirm durable file-service write separately.'}
        (temporary / 'resume.json').write_text(json.dumps(receipt, indent=2) + '\n')
        os.rename(temporary, dest)
        return {'status': 'created', 'directory': str(dest), **receipt}
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def new_project(title):
    t = stamp()
    return {'id': str(uuid.uuid4()), 'title': nonblank(title, 500), 'revision': 0, 'createdAt': t, 'updatedAt': t}


def import_fdx(args):
    data, originals, segments = parse_fdx(args.file)
    project = new_project(args.title)
    if args.project:
        project, _ = pinned(args)
        if project.get('sourceEvidence', {}).get('screenplay'):
            fail('EXISTING_SCRIPT_REQUIRES_EXPLICIT_REVISION_WORKFLOW')
        project['revision'] += 1
        project['updatedAt'] = stamp()
    w = workflow(project)
    w['stage'] = 'screenplay-proposal' if args.project else 'imported-screenplay'
    w['sourceDocument'] = {'name': Path(args.file).name, 'sha256': digest(data), 'format': 'final-draft', 'paragraphs': originals}
    w['allocation'] = {'state': 'provisional', 'method': 'chronological-word-share',
                       'note': 'Mechanical source allocation, not proof of dramatic structure. Review semantic boundaries before shot planning.'}
    total = sum(max(1, len(p['text'].split())) for p in segments)
    consumed = 0
    mapped = []
    for p in segments:
        position = min(95, consumed * 96 // total)
        mapped.append({k: v for k, v in p.items() if k not in ('originalParagraphId', 'part')} |
                      {'blockNumber': position // 4 + 1, 'miniBlockNumber': position % 4 + 1})
        consumed += max(1, len(p['text'].split()))
    w['paragraphMapping'] = [{'passageId': p['id'], 'originalParagraphId': p['originalParagraphId'], 'part': p['part']} for p in segments]
    project.setdefault('sourceEvidence', {})['screenplay'] = {'sourceFileName': Path(args.file).name,
        'sourceFormat': 'final-draft', 'importedAt': stamp(), 'analysisStatus': 'suggested',
        'totalPassageCount': len(mapped), 'storedPassageCount': len(mapped), 'passagesTruncated': False,
        'passages': mapped, 'sectionMarkers': [], 'projectionReviews': []}
    return save_snapshot(args, project, {'source.fdx': data}, create=not bool(args.project))


def idea(args):
    data = read_bytes(args.file)
    text = nonblank(data.decode('utf-8'), 100000)
    project = new_project(args.title)
    workflow(project).update({'stage': 'idea-awaiting-screenplay', 'idea': {'text': text, 'sha256': digest(data)},
                              'allocation': {'state': 'not-started'}})
    return save_snapshot(args, project, {'idea.txt': data}, create=True)


def remap(args):
    project, ident = pinned(args)
    mapping = read_json(args.mapping)
    if mapping.get('project') != ident:
        fail('MAPPING_SNAPSHOT_MISMATCH')
    if project.get('build', {}).get('foundations', {}).get('visualArtifacts') or project.get('production', {}).get('storyboardImagePrompts'):
        fail('SOURCE_REMAP_WITH_EXISTING_MEDIA_OR_PROMPTS_REQUIRES_MIGRATION')
    s = source(project)
    existing = {p['id'] for p in s['passages']}
    assignments = mapping.get('assignments', [])
    ids = [x.get('passageId') for x in assignments]
    if set(ids) != existing or len(ids) != len(existing):
        fail('MAPPING_MUST_COVER_EVERY_PASSAGE_EXACTLY_ONCE')
    lookup = {}
    for row in assignments:
        address(row['blockNumber'], row['miniBlockNumber'])
        nonblank(row.get('reason'), 1200)
        lookup[row['passageId']] = row
    for p in s['passages']:
        p.update({k: lookup[p['id']][k] for k in ('blockNumber', 'miniBlockNumber')})
    workflow(project)['allocation'] = {'state': 'editorial-proposal', 'method': 'explicit-passage-map',
                                        'baseProject': ident, 'assignments': assignments}
    project['revision'] += 1
    project['updatedAt'] = stamp()
    return save_snapshot(args, project)


def prepare(args):
    project, ident = pinned(args)
    a = address(args.block, args.mini)
    passages = [p for p in source(project)['passages'] if p['blockNumber'] == args.block and p['miniBlockNumber'] == args.mini]
    if not passages:
        fail('NO_SOURCE_FOR_MINI_BLOCK')
    packet = {'version': 1, 'project': ident, 'address': a, 'status': 'UNPLANNED',
              'allocation': workflow(project).get('allocation', {'state': 'existing-export-placement-unreviewed'}),
              'sourcePassages': passages, 'truths': [], 'shots': [
                  {'shotNumber': n, 'state': 'GAP', 'passageIds': [], 'reason': 'Awaiting evidence-bound shot design.'} for n in range(1, 26)]}
    out = Path(args.out)
    with out.open('x') as f:
        json.dump(packet, f, ensure_ascii=False, indent=2)
    return {'status': 'prepared', 'file': str(out.resolve()), 'plannedShotSlots': 25, 'promptsAuthored': 0}


def plan(args):
    project, ident = pinned(args)
    proposal = read_json(args.plan)
    if proposal.get('project') != ident:
        fail('PLAN_SNAPSHOT_MISMATCH')
    a = proposal.get('address', {})
    b, m = a.get('blockNumber'), a.get('miniBlockNumber')
    if a != address(b, m):
        fail('INVALID_ADDRESS')
    all_source_ids = {p['id'] for p in source(project)['passages']}
    allowed = {p['id'] for p in source(project)['passages'] if p['blockNumber'] == b and p['miniBlockNumber'] == m}
    if not allowed:
        fail('NO_SOURCE_FOR_MINI_BLOCK')
    nonblank(proposal.get('allocationReview'), 2000)
    truths = proposal.get('truths', [])
    truth_ids = set()
    for truth in truths:
        tid = nonblank(truth.get('id'), 160)
        if tid in truth_ids or truth.get('origin') not in ('source', 'visual-proposal'):
            fail('INVALID_TRUTH_RECORD')
        truth_ids.add(tid)
        nonblank(truth.get('text'), 2000)
        refs = truth.get('passageIds', [])
        if not isinstance(refs, list) or not set(refs) <= all_source_ids or (truth['origin'] == 'source' and not refs):
            fail('TRUTH_EVIDENCE_OUTSIDE_PROJECT')
    shots = proposal.get('shots', [])
    if len(shots) != 25 or sorted(x.get('shotNumber', 0) for x in shots) != list(range(1, 26)):
        fail('EXACTLY_25_UNIQUE_SHOT_SLOTS_REQUIRED')
    seen, prompts = set(), []
    for shot in shots:
        if type(shot.get('shotNumber')) is not int:
            fail('INTEGER_SHOT_NUMBER_REQUIRED')
        if shot.get('state') == 'GAP':
            nonblank(shot.get('reason'), 2000)
            continue
        if shot.get('state') != 'PLANNED':
            fail('INVALID_SHOT_STATE')
        refs = shot.get('passageIds')
        if not isinstance(refs, list) or not refs or not set(refs) <= allowed:
            fail('SHOT_EVIDENCE_OUTSIDE_MINI')
        if shot.get('coverageType') not in ('story-beat', 'alternative-view', 'detail'):
            fail('INVALID_COVERAGE_TYPE')
        purpose = nonblank(shot.get('narrativePurpose'), 1000)
        composition = nonblank(shot.get('composition'), 2000)
        if not isinstance(shot.get('truthIds', []), list) or not set(shot.get('truthIds', [])) <= truth_ids:
            fail('UNKNOWN_TRUTH_REFERENCE')
        prompt = nonblank(shot.get('prompt'), 8000)
        # Compare content, not shot labels, to reject twenty-five copies of one prompt.
        signature = re.sub(r'\b(?:shot|frame|position)\s*\d+\b', '', clean(prompt).lower())
        if signature in seen:
            fail('DUPLICATE_IMAGE_PROMPT')
        seen.add(signature)
        prompts.append({'anchorRef': anchor(b, m), 'position': shot['shotNumber'], 'prompt': prompt, 'createdAt': stamp()})
        duration = shot.get('durationTargetSeconds', 3)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 < duration <= 10000000:
            fail('INVALID_SHOT_DURATION_TARGET')
        shot.update({'narrativePurpose': purpose, 'composition': composition, 'durationTargetSeconds': duration,
                     'semanticGrounding': 'agent-authored-not-independently-proved', 'imageState': 'MISSING'})
    # No automatic generation or approval; source claims remain auditable proposals.
    w = workflow(project)
    known_truths = {x['id']: x for x in w.get('truths', [])}
    for truth in truths:
        if truth['id'] in known_truths and truth != known_truths[truth['id']]:
            fail('CONTINUITY_TRUTH_CHANGED_REQUIRES_EXPLICIT_REVISION')
        known_truths[truth['id']] = truth
    w['truths'] = list(known_truths.values())
    if any(x['address'] == a for x in w.get('plans', [])):
        fail('MINI_ALREADY_PLANNED_USE_EXPLICIT_REVISION')
    proposal.update({'status': 'SHOT_PLAN_PROPOSAL', 'createdAt': stamp(), 'semanticGroundingVerified': False})
    w.setdefault('plans', []).append(proposal)
    existing = project.setdefault('production', {}).setdefault('storyboardImagePrompts', [])
    if any(x['anchorRef'] == anchor(b, m) for x in existing):
        fail('EXISTING_MINI_PROMPTS_REQUIRE_EXPLICIT_REPLACEMENT')
    existing.extend(prompts)
    project['revision'] += 1
    project['updatedAt'] = stamp()
    return save_snapshot(args, project, {'shot-plan.json': json.dumps(proposal, ensure_ascii=False, indent=2)})


def attach(args):
    project, ident = pinned(args)
    a = address(args.block, args.mini, args.shot)
    w = workflow(project)
    plans = [p for p in w.get('plans', []) if p['address'] == address(args.block, args.mini)]
    if len(plans) != 1:
        fail('SHOT_PLAN_REQUIRED_BEFORE_IMAGE')
    shot = next(s for s in plans[0]['shots'] if s['shotNumber'] == args.shot)
    if shot.get('state') != 'PLANNED':
        fail('GAP_SHOT_CANNOT_RECEIVE_IMAGE')
    try:
        from PIL import Image
    except ImportError:
        fail('IMAGE_DECODER_UNAVAILABLE')
    # Decode the source, then store a lossless WebP with an address and content hash.
    data = read_bytes(args.image)
    import io
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.format not in ('PNG', 'JPEG', 'WEBP'):
            fail('UNSUPPORTED_IMAGE_FORMAT')
        if image.width * image.height > 40000000:
            fail('IMAGE_DIMENSIONS_TOO_LARGE')
        mode = 'RGBA' if 'A' in image.getbands() else 'RGB'
        buffer = io.BytesIO()
        image.convert(mode).save(buffer, format='WEBP', lossless=True)
        webp = buffer.getvalue()
        width, height = image.size
    h = digest(webp)
    name = f'story-b{args.block:02}-m{args.mini}-s{args.shot:02}-{h[:16]}.webp'
    url = '/api/local-ai/assets/' + name
    artifacts = project['build']['foundations']['visualArtifacts']
    old = [x for x in artifacts if x.get('workflow') == 'storyboard-frame-webp-v2' and x.get('frameNumber') == args.shot and anchor(args.block, args.mini) in x.get('sourceDecisionKeys', [])]
    if old and not args.replace:
        fail('SHOT_ALREADY_HAS_IMAGE_USE_REPLACE')
    old_ids = {x['id'] for x in old}
    if old_ids:
        artifacts[:] = [x for x in artifacts if x['id'] not in old_ids]
        accepted = project['build']['foundations']['acceptedVisualArtifactIds']
        accepted[:] = [x for x in accepted if x not in old_ids]
        # Remove registry records only when explicitly bound to the replaced storyboard frame.
        old_urls = {x['assetUrl'] for x in old}
        legacy_entries = project['assetRegistry']['extensions'].get('artworkMapping', {}).get('entries', [])
        old_asset_ids = {x.get('assetId') for x in legacy_entries if x.get('address') == a}
        project['assetRegistry']['assets'][:] = [x for x in project['assetRegistry']['assets'] if
            x['id'] not in old_asset_ids and not any(t.get('kind') == 'storyboard-frame' and t.get('id') in old_ids for t in x.get('targets', []))
            and not any(v.get('source') in old_urls for v in x.get('variations', []))]
        if legacy_entries:
            project['assetRegistry']['extensions']['artworkMapping']['entries'] = [x for x in legacy_entries if x.get('address') != a]
    art_id = str(uuid.uuid4())
    keys = [f'storyboard-target:block:block-{args.block:02}', anchor(args.block, args.mini), f'storyboard-position:{args.shot}',
            'story-workflow-image-import:v1'] + ['source-passage:' + x for x in shot['passageIds']]
    artifacts.append({'id': art_id, 'assetUrl': url, 'prompt': shot['prompt'], 'createdAt': stamp(),
        'provider': nonblank(args.provider, 200), 'model': args.model or '', 'frameNumber': args.shot,
        'sourceDecisionKeys': keys, 'workflow': 'storyboard-frame-webp-v2', 'reviewState': 'draft', 'parentArtifactId': None})
    record = {'artifactId': art_id, 'address': a, 'passageIds': shot['passageIds'], 'prompt': shot['prompt'],
              'portablePath': 'assets/' + name, 'sha256': h, 'sourceSha256': digest(data), 'width': width, 'height': height,
              'packageBytesVerified': True, 'liveMediaBytesVerified': False, 'savedMarkerPresent': False, 'locked': False}
    w['imageMappings'] = [x for x in w.get('imageMappings', []) if x['address'] != a] + [record]
    shot['imageState'] = 'CANDIDATE'
    project['assetRegistry']['assets'].append({'id': 'asset-' + art_id, 'kind': 'image', 'label': f'Block {args.block} Mini {args.mini} Shot {args.shot}',
        'targets': [{'kind': 'storyboard-frame', 'id': art_id}], 'variations': [{'id': 'variation-' + art_id,
        'source': url, 'portablePath': record['portablePath'], 'contentHash': 'sha256:' + h, 'mediaType': 'image/webp',
        'bytes': len(webp), 'prompt': shot['prompt'], 'provider': args.provider, 'model': args.model or '',
        'approval': 'unreviewed', 'provenanceIds': shot['passageIds'], 'extensions': {'storyboardAddress': a}}],
        'approvedVariationId': '', 'createdAt': stamp(), 'updatedAt': stamp(), 'extensions': {}})
    project['revision'] += 1
    project['updatedAt'] = stamp()
    return save_snapshot(args, project, {'assets/' + name: webp})


def resume(args):
    project, ident = pinned(args)
    w = workflow(project)
    verified, missing, changed = [], [], []
    base = Path(args.project).resolve().parent
    mappings = w.get('imageMappings', [])
    # Also accept the explicit mapping from the prior artwork-import workflow.
    mappings = mappings + project.get('assetRegistry', {}).get('extensions', {}).get('artworkMapping', {}).get('entries', [])
    for e in mappings:
        rel = Path(e['portablePath'])
        if rel.is_absolute() or '..' in rel.parts:
            fail('UNSAFE_PORTABLE_PATH')
        path = (base / rel).resolve()
        if not path.is_relative_to(base):
            fail('UNSAFE_PORTABLE_PATH')
        if not path.is_file():
            missing.append(str(rel))
        elif digest(path.read_bytes()) != e['sha256']:
            changed.append(str(rel))
        else:
            verified.append(str(rel))
    return {'status': 'observed', 'project': ident, 'stage': w.get('stage', 'existing-export'),
            'sourcePassages': len(project.get('sourceEvidence', {}).get('screenplay', {}).get('passages', [])) if project.get('sourceEvidence', {}).get('screenplay') else 0,
            'miniPlans': len(w.get('plans', [])), 'verifiedImages': len(verified), 'missingImages': missing,
            'changedImages': changed, 'liveApplicationUpdated': False, 'newConversationHostAcceptanceVerified': False}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='operation', required=True)
    for name in ('import-fdx', 'idea', 'map', 'prepare-mini', 'plan-mini', 'attach-image', 'resume'):
        s = commands.add_parser(name)
        if name in ('import-fdx', 'idea'):
            s.add_argument('--file', required=True)
            s.add_argument('--title', required=True)
        if name != 'idea':
            s.add_argument('--project', required=name != 'import-fdx')
            s.add_argument('--project-id')
            s.add_argument('--revision', type=int)
            s.add_argument('--sha256')
        if name not in ('resume',):
            s.add_argument('--out', required=True)
        if name == 'map':
            s.add_argument('--mapping', required=True)
        if name in ('prepare-mini', 'attach-image'):
            s.add_argument('--block', required=True, type=int)
            s.add_argument('--mini', required=True, type=int)
        if name == 'plan-mini':
            s.add_argument('--plan', required=True)
        if name == 'attach-image':
            s.add_argument('--shot', required=True, type=int)
            s.add_argument('--image', required=True)
            s.add_argument('--provider', required=True)
            s.add_argument('--model')
            s.add_argument('--replace', action='store_true')
    return p


if __name__ == '__main__':
    try:
        args = parser().parse_args()
        handlers = {'import-fdx': import_fdx, 'idea': idea, 'map': remap, 'prepare-mini': prepare,
                    'plan-mini': plan, 'attach-image': attach, 'resume': resume}
        print(json.dumps(handlers[args.operation](args), ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError, json.JSONDecodeError) as e:
        print(json.dumps({'status': 'blocked', 'code': str(e)[:600], 'sourceFileMutated': False}), file=sys.stderr)
        sys.exit(1)
