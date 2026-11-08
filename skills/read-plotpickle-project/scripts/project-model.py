"""Truth, mathematics and learning records for an explicitly pinned PlotPickle file.

No model/network calls. Schema checks validate relationships, not artistic truth.
Only adopt-proposal changes screenplay content, on an explicit adoption instruction.
"""
import argparse
import copy
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('story_workflow', HERE / 'story-workflow.py')
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)
CATEGORIES = {'known', 'inferred', 'unknown', 'proposed', 'adopted'}
KINDS = {'transition', 'scene-heading', 'action', 'character', 'dialogue', 'parenthetical', 'note'}


def model(project):
    ext = project['assetRegistry'].setdefault('extensions', {})
    return ext.setdefault('projectModel', {'version': 1, 'principles': ['truth', 'mathematics', 'learning'],
        'truths': [], 'assessments': [], 'proposals': [], 'decisions': [], 'feedback': [],
        'runtimePlan': None, 'reviewRequired': []})


def fingerprint(project):
    s = project.get('sourceEvidence', {}).get('screenplay')
    return wf.digest(json.dumps(s, ensure_ascii=False, sort_keys=True).encode())


def ids_for(project):
    s = project.get('sourceEvidence', {}).get('screenplay')
    return {p['id'] for p in s['passages']} if s else set()


def check_ids(values, allowed, required=False):
    if not isinstance(values, list) or any(not isinstance(x, str) for x in values) or len(values) != len(set(values)):
        wf.fail('INVALID_REFERENCE_LIST')
    if (required and not values) or not set(values) <= allowed:
        wf.fail('SOURCE_REFERENCE_UNRESOLVED')


def require_snapshot(payload, ident):
    if payload.get('project') != ident:
        wf.fail('PAYLOAD_SNAPSHOT_MISMATCH')


def validate_truth(t, source_ids):
    wf.nonblank(t.get('id'), 160)
    wf.nonblank(t.get('text'), 4000)
    if t.get('category') not in CATEGORIES - {'adopted'}:
        wf.fail('ADOPTED_TRUTH_REQUIRES_ADOPTION_EVENT')
    if t.get('scope') not in {'source-observation', 'story-world', 'character-belief', 'editorial-judgment', 'production'}:
        wf.fail('INVALID_TRUTH_SCOPE')
    if t.get('category') == 'known' and t['scope'] not in {'source-observation', 'production'}:
        wf.fail('WORLD_FACT_REQUIRES_REVIEW_NOT_AUTOMATIC_CERTAINTY')
    if t.get('origin') not in {'supplied-source', 'interpretation', 'synthetic', 'unresolved'}:
        wf.fail('INVALID_TRUTH_ORIGIN')
    if t['category'] == 'known' and t['origin'] != 'supplied-source':
        wf.fail('KNOWN_REQUIRES_SUPPLIED_SOURCE')
    if t['category'] == 'proposed' and t['origin'] != 'synthetic':
        wf.fail('PROPOSAL_REQUIRES_SYNTHETIC_ORIGIN')
    if t['category'] == 'unknown' and t['origin'] != 'unresolved':
        wf.fail('UNKNOWN_REQUIRES_UNRESOLVED_ORIGIN')
    if t['category'] == 'inferred' and t['origin'] != 'interpretation':
        wf.fail('INFERENCE_REQUIRES_INTERPRETATION_ORIGIN')
    check_ids(t.get('passageIds', []), source_ids, t['category'] in {'known', 'inferred'})
    if t['origin'] == 'supplied-source' and any(x.startswith('synthetic-') for x in t.get('passageIds', [])):
        wf.fail('SYNTHETIC_SOURCE_CANNOT_BECOME_ORIGINAL_EVIDENCE')
    wf.nonblank(t.get('reason'), 4000)
    if t.get('independentlyVerified', False) is not False:
        wf.fail('INDEPENDENT_VERIFICATION_NOT_ESTABLISHED_BY_THIS_COMMAND')
    t['independentlyVerified'] = False
    t['createdAt'] = wf.stamp()
    t['originalCategory'] = t['category']
    t['relations'] = t.get('relations', [])
    if not isinstance(t['relations'], list):
        wf.fail('INVALID_TRUTH_RELATION')
    for r in t['relations']:
        if r.get('kind') not in {'supports', 'contradicts', 'depends-on'}:
            wf.fail('INVALID_TRUTH_RELATION')
        wf.nonblank(r.get('truthId'), 160)
        wf.nonblank(r.get('reason'), 2000)
    return t


def assessment(args):
    project, ident = wf.pinned(args)
    payload = wf.read_json(args.file)
    require_snapshot(payload, ident)
    source_ids = ids_for(project)
    if not source_ids:
        wf.fail('SCREENPLAY_REQUIRED_FOR_ASSESSMENT')
    scope_ids = payload.get('scopePassageIds', sorted(source_ids))
    check_ids(scope_ids, source_ids, True)
    source_ids = set(scope_ids)
    supporting = payload.get('supportingSource')
    if supporting is not None:
        import re
        wf.nonblank(supporting.get('fileName'), 500)
        if not re.fullmatch(r'[a-f0-9]{64}', supporting.get('sha256', '')):
            wf.fail('INVALID_SUPPORTING_SOURCE_HASH')
        wf.nonblank(supporting.get('comparisonNote'), 5000)
    m = model(project)
    new_truths = [validate_truth(copy.deepcopy(t), source_ids) for t in payload.get('truths', [])]
    known = {t['id']: t for t in m['truths']}
    for t in new_truths:
        if t['id'] in known:
            wf.fail('TRUTH_ID_ALREADY_EXISTS')
        known[t['id']] = t
    for t in new_truths:
        for r in t['relations']:
            if r['truthId'] not in known or r['truthId'] == t['id']:
                wf.fail('TRUTH_RELATION_UNRESOLVED')
    summary = payload.get('storySummary', {})
    for part in ('beginning', 'middle', 'ending'):
        entry = summary.get(part, {})
        wf.nonblank(entry.get('text'), 5000)
        check_ids(entry.get('passageIds', []), source_ids, True)
    findings = payload.get('findings', [])
    finding_ids = set()
    for f in findings:
        fid = wf.nonblank(f.get('id'), 160)
        if fid in finding_ids or f.get('classification') not in {'supported', 'deliberate-ambiguity', 'candidate-gap', 'opportunity'}:
            wf.fail('INVALID_FINDING')
        finding_ids.add(fid)
        wf.nonblank(f.get('claim'), 5000)
        wf.nonblank(f.get('reason'), 5000)
        check_ids(f.get('passageIds', []), source_ids, True)
        # Deliberate ambiguity is an editorial reading, not certified author intent.
        f['status'] = 'editorial-assessment-not-independently-proved'
    proposal_ids = {p['id'] for p in m['proposals']}
    proposed = []
    for p in payload.get('proposals', []):
        pid = wf.nonblank(p.get('id'), 160)
        if pid in proposal_ids:
            wf.fail('PROPOSAL_ID_ALREADY_EXISTS')
        proposal_ids.add(pid)
        for field in ('title', 'diagnosis', 'rationale'):
            wf.nonblank(p.get(field), 6000)
        if p.get('findingId') not in finding_ids:
            wf.fail('PROPOSAL_FINDING_UNRESOLVED')
        check_ids(p.get('passageIds', []), source_ids, True)
        check_ids(p.get('truthIds', []), set(known))
        learning = p.get('learning', {})
        for field in ('principle', 'explanation', 'studentQuestion'):
            wf.nonblank(learning.get(field), 6000)
        if not isinstance(p.get('impacts'), list) or not p['impacts']:
            wf.fail('PROPOSAL_IMPACT_REQUIRED')
        for impact in p['impacts']:
            wf.nonblank(impact.get('area'), 160)
            wf.nonblank(impact.get('reason'), 3000)
        if p.get('recommendation') not in {'insert', 'retain'}:
            wf.fail('INVALID_RECOMMENDATION')
        if p['recommendation'] == 'insert':
            change = p.get('change', {})
            if change.get('afterPassageId') not in source_ids:
                wf.fail('INSERT_ANCHOR_UNRESOLVED')
            wf.address(change.get('blockNumber'), change.get('miniBlockNumber'))
            fragments = change.get('passages', [])
            if not isinstance(fragments, list) or not fragments:
                wf.fail('SYNTHETIC_PASSAGES_REQUIRED')
            for f in fragments:
                if f.get('type') not in KINDS:
                    wf.fail('INVALID_PASSAGE_TYPE')
                wf.nonblank(f.get('text'), 780)
        elif p.get('change'):
            wf.fail('RETAIN_RECOMMENDATION_CANNOT_INSERT')
        p.update({'status': 'proposed', 'origin': 'synthetic' if p['recommendation'] == 'insert' else 'editorial',
                  'createdAt': wf.stamp(), 'baseProject': ident, 'sourceFingerprint': fingerprint(project)})
        proposed.append(p)
    m['truths'].extend(new_truths)
    m['proposals'].extend(proposed)
    record = {'id': 'assessment-' + str(len(m['assessments']) + 1), 'at': wf.stamp(), 'baseProject': ident,
              'sourceFingerprint': fingerprint(project), 'storySummary': summary, 'findings': findings,
              'scopePassageIds': scope_ids, 'supportingSource': supporting,
              'proposalIds': [p['id'] for p in proposed], 'truthIds': [t['id'] for t in new_truths],
              'semanticVerification': 'editorial-review-required'}
    m['assessments'].append(record)
    project['revision'] += 1
    project['updatedAt'] = wf.stamp()
    return wf.save_snapshot(args, project, {'assessment.json': json.dumps(record, ensure_ascii=False, indent=2),
                                          'proposals.json': json.dumps(proposed, ensure_ascii=False, indent=2)})


def decision(args):
    project, ident = wf.pinned(args)
    payload = wf.read_json(args.file)
    require_snapshot(payload, ident)
    m = model(project)
    proposal = next((p for p in m['proposals'] if p['id'] == args.proposal), None)
    if not proposal or proposal['status'] != 'proposed':
        wf.fail('PENDING_PROPOSAL_REQUIRED')
    authority = wf.nonblank(payload.get('authority'), 3000)
    reason = wf.nonblank(payload.get('reason'), 6000)
    action = 'adopted' if args.operation == 'adopt-proposal' else 'rejected'
    if action == 'adopted' and proposal['sourceFingerprint'] != fingerprint(project):
        wf.fail('SOURCE_CHANGED_REASSESS_PROPOSAL')
    inserted = []
    if action == 'adopted' and proposal['recommendation'] == 'insert':
        source = wf.source(project)
        change = proposal['change']
        passages = source['passages']
        idx = next(i for i, p in enumerate(passages) if p['id'] == change['afterPassageId'])
        base = passages[idx]
        if len(passages) + len(change['passages']) > wf.MAX_PASSAGES:
            wf.fail('SOURCE_EXCEEDS_CANONICAL_CAPACITY')
        for number, fragment in enumerate(change['passages'], 1):
            pid = 'synthetic-' + proposal['id'] + '-' + str(number)
            if len(pid) > 240 or pid in ids_for(project):
                wf.fail('SYNTHETIC_PASSAGE_ID_COLLISION')
            inserted.append({'id': pid, 'type': fragment['type'], 'text': wf.clean(fragment['text']),
                             'blockNumber': change['blockNumber'], 'miniBlockNumber': change['miniBlockNumber'],
                             'sceneNumber': base['sceneNumber'], 'sceneId': base['sceneId']})
        # Retain every original passage, original ID and original source document.
        source['passages'] = passages[:idx + 1] + inserted + passages[idx + 1:]
        source['storedPassageCount'] = len(source['passages'])
        source['totalPassageCount'] = len(source['passages'])
        source['sourceFormat'] = 'imported-source+adopted-synthetic-revision'
        source['analysisStatus'] = 'suggested'
        m['reviewRequired'].append({'proposalId': proposal['id'], 'atRevision': project['revision'] + 1,
                                   'blockNumber': change['blockNumber'], 'miniBlockNumber': change['miniBlockNumber'],
                                   'areas': ['source-allocation', 'continuity', 'shot-plan', 'images', 'runtime'],
                                   'reason': 'Adopted story addition changes the source. Existing media approval is not approval of this revision.'})
    event = {'id': 'decision-' + str(len(m['decisions']) + 1), 'proposalId': proposal['id'],
             'action': action, 'authority': authority, 'reason': reason, 'at': wf.stamp(),
             'atRevision': project['revision'] + 1, 'insertedPassageIds': [x['id'] for x in inserted],
             'authorityIndependentlyVerified': False}
    proposal['status'] = action
    proposal['decisionId'] = event['id']
    m['decisions'].append(event)
    if action == 'adopted':
        for tid in proposal.get('truthIds', []):
            t = next(t for t in m['truths'] if t['id'] == tid)
            if t['category'] == 'proposed':
                t['category'] = 'adopted'
                t['adoptionDecisionId'] = event['id']
                t['adoptedAtRevision'] = project['revision'] + 1
    project['revision'] += 1
    project['updatedAt'] = wf.stamp()
    return wf.save_snapshot(args, project)


def decimal(value, allow_zero=False):
    if isinstance(value, bool):
        wf.fail('INVALID_DURATION')
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        wf.fail('INVALID_DURATION')
    if not result.is_finite() or result < 0 or (not allow_zero and result == 0) or result > Decimal('10000000'):
        wf.fail('INVALID_DURATION')
    return result


def number(d):
    return int(d) if d == d.to_integral_value() else float(d)


def runtime(args):
    project, ident = wf.pinned(args)
    payload = wf.read_json(args.file)
    require_snapshot(payload, ident)
    if payload.get('intendedFormat') not in {'short', 'feature', 'episode', 'other', 'undecided'}:
        wf.fail('INVALID_PROJECT_FORMAT')
    target = payload.get('targetRuntimeSeconds')
    if target is not None:
        target = decimal(target)
        wf.nonblank(payload.get('targetBasis'), 3000)
    fps = payload.get('framesPerSecond', 24)
    if type(fps) is not int or not 1 <= fps <= 120:
        wf.fail('INTEGER_PLANNING_FPS_REQUIRED')
    shots = payload.get('physicalShots', [])
    if not isinstance(shots, list):
        wf.fail('INVALID_PHYSICAL_SHOTS')
    seen, covered, total = set(), set(), Decimal(0)
    for shot in shots:
        sid = wf.nonblank(shot.get('id'), 160)
        if sid in seen:
            wf.fail('DUPLICATE_PHYSICAL_SHOT')
        seen.add(sid)
        duration = decimal(shot.get('durationSeconds'))
        total += duration
        refs = shot.get('slotRefs', [])
        if not isinstance(refs, list) or not refs:
            wf.fail('CANONICAL_SLOT_REFERENCE_REQUIRED')
        local = set()
        for ref in refs:
            valid = wf.address(ref.get('blockNumber'), ref.get('miniBlockNumber'), ref.get('shotNumber'))
            if ref != valid:
                wf.fail('INVALID_CANONICAL_SLOT')
            key = (valid['blockNumber'], valid['miniBlockNumber'], valid['shotNumber'])
            if key in covered or key in local:
                wf.fail('SLOT_ASSIGNED_TO_MULTIPLE_PHYSICAL_SHOTS')
            local.add(key)
        covered.update(local)
        wf.nonblank(shot.get('coverageReason'), 3000)
    frames = total * fps
    result = {'physicalShotCount': len(shots), 'plannedRuntimeSeconds': number(total),
              'targetRuntimeSeconds': number(target) if target is not None else None,
              'differenceFromTargetSeconds': number(total - target) if target is not None else None,
              'coveredCanonicalSlots': len(covered), 'totalCanonicalSlots': 2400,
              'unassignedCanonicalSlots': 2400 - len(covered), 'framesPerSecond': fps,
              'plannedFramesExact': str(frames), 'integerFrameCount': frames == frames.to_integral_value(),
              'nearestFrameCount': int(frames.to_integral_value(rounding=ROUND_HALF_UP)),
              'actualMediaRuntimeVerified': False, 'structuralCoverageProved': False,
              'note': 'Assigned planning addresses are not proof of dramatic completeness or rendered duration.'}
    payload.update({'status': 'production-plan-proposal', 'computed': result, 'at': wf.stamp(),
                    'sourceFingerprint': fingerprint(project)})
    m = model(project)
    if m['runtimePlan']:
        m.setdefault('runtimePlanHistory', []).append(m['runtimePlan'])
    m['runtimePlan'] = payload
    project['revision'] += 1
    project['updatedAt'] = wf.stamp()
    return wf.save_snapshot(args, project, {'runtime-plan.json': json.dumps(payload, ensure_ascii=False, indent=2)})


def feedback(args):
    project, ident = wf.pinned(args)
    payload = wf.read_json(args.file)
    require_snapshot(payload, ident)
    m = model(project)
    if payload.get('proposalId') not in {p['id'] for p in m['proposals']}:
        wf.fail('FEEDBACK_PROPOSAL_UNRESOLVED')
    for field in ('observation', 'evidence', 'lesson', 'nextExperiment'):
        wf.nonblank(payload.get(field), 6000)
    if payload.get('reportedBy') not in {'user', 'agent'}:
        wf.fail('FEEDBACK_ORIGIN_REQUIRED')
    payload.update({'id': 'feedback-' + str(len(m['feedback']) + 1), 'at': wf.stamp(),
                    'independentlyVerified': False, 'modelWeightsUpdated': False})
    m['feedback'].append(payload)
    project['revision'] += 1
    project['updatedAt'] = wf.stamp()
    return wf.save_snapshot(args, project)


def inspect(args):
    project, ident = wf.pinned(args)
    m = model(project)
    contradictions = [{'truthId': t['id'], **r} for t in m['truths'] for r in t.get('relations', []) if r['kind'] == 'contradicts']
    return {'status': 'observed', 'project': ident, 'sourceFingerprint': fingerprint(project),
            'projectModel': m, 'declaredContradictions': contradictions,
            'runtimePlanMatchesCurrentSource': m['runtimePlan'] is None or m['runtimePlan']['sourceFingerprint'] == fingerprint(project),
            'contradictionsAutomaticallyDetected': False, 'sourceMutated': False,
            'mathematicsVerifiedBy': 'explicit computation', 'semanticTruthIndependentlyVerified': False}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    for name in ('assess', 'adopt-proposal', 'reject-proposal', 'runtime-plan', 'record-feedback', 'inspect'):
        s = sub.add_parser(name)
        s.add_argument('--project', required=True)
        s.add_argument('--project-id', required=True)
        s.add_argument('--revision', required=True, type=int)
        s.add_argument('--sha256', required=True)
        if name != 'inspect':
            s.add_argument('--file', required=True)
            s.add_argument('--out', required=True)
        if name in {'adopt-proposal', 'reject-proposal'}:
            s.add_argument('--proposal', required=True)
    return p


if __name__ == '__main__':
    try:
        args = parser().parse_args()
        handler = {'assess': assessment, 'adopt-proposal': decision, 'reject-proposal': decision,
                   'runtime-plan': runtime, 'record-feedback': feedback, 'inspect': inspect}[args.operation]
        print(json.dumps(handler(args), ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError) as e:
        print(json.dumps({'status': 'blocked', 'code': str(e)[:600], 'inputFileMutated': False}), file=sys.stderr)
        sys.exit(1)
