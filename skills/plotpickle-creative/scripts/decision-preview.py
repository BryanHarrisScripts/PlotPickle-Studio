#!/usr/bin/env python3
"""Create a read-only, source-anchored creative decision packet from a verified craft review.

Suggestions are never canon or approvals. Does not modify a screenplay, image, or
project; rejects stale identities and unanchored or unknown review findings.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ALLOWED = {'retain-as-written', 'visual-test', 'consider-revision', 'study-further'}
DATA = Path(__file__).resolve().parents[1] / 'data'


def build_preview(project_bytes, review, choices, catalog=None, inventory=None):
    project = json.loads(project_bytes)
    ident = {'id': project.get('id'), 'revision': project.get('revision'),
             'sha256': hashlib.sha256(project_bytes).hexdigest()}
    bridge_path=Path(__file__).with_name('curriculum-bridge.py')
    spec=importlib.util.spec_from_file_location('pp_curriculum_bridge_v08',bridge_path)
    bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
    records=bridge.verified_library(bridge.load_manifest(),DATA/'learn')
    full_lessons={(t['id'],l['id']):l for t,b in records for l in b['lessons']}
    if choices.get('project') != ident or review.get('project') != ident:
        raise ValueError('Stale project or review identity; reopen authoritative source')
    if review.get('ok') is not True or review.get('projectMutated') is not False:
        raise ValueError('Review must be a successful read-only evidence packet')
    if catalog is None:
        catalog = json.loads((DATA / 'lesson-catalog.json').read_text(encoding='utf-8'))
    if inventory is None:
        inventory = json.loads((DATA / 'curriculum-index.json').read_text(encoding='utf-8'))
    topic_map={t['id']:t for t in inventory['topics']}
    lesson_map={(l['topic'],l['id']):l for l in catalog['lessons']}
    if len(topic_map) != 12 or len(lesson_map) != 81:
        raise ValueError('Incomplete canonical curriculum catalog')
    passages=project.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])
    source_map={p.get('id'):p for p in passages}
    if not passages or len(source_map) != len(passages):
        raise ValueError('Missing or duplicate saved screenplay source')
    findings = review.get('findings', [])
    by_id = {f.get('id'):f for f in findings}
    if not findings or len(by_id) != len(findings):
        raise ValueError('Missing or duplicate review findings')
    ids = set()
    decisions = []
    for choice in choices.get('choices', []):
        fid = choice.get('findingId')
        if fid not in by_id or fid in ids:
            raise ValueError('Unknown/duplicate finding ID in decision packet')
        ids.add(fid)
        action = choice.get('recommendation')
        if action not in ALLOWED:
            raise ValueError('Invalid non-authoritative recommendation')
        notes = choice.get('rationale')
        if not isinstance(notes, str) or not notes.strip():
            raise ValueError('Missing craft rationale')
        evidence = by_id[fid]['evidence']
        lessons = by_id[fid]['lessons']
        if not evidence or not lessons or any(not e.get('textSha256') for e in evidence):
            raise ValueError('Incomplete screenplay/lesson binding')
        if any(l.get('lessonBodyVerifiedByBinder') is not True or l.get('lessonSectionVerifiedByBinder') is not True for l in lessons):
            raise ValueError('Lesson body/section must be independently verified before a craft decision')
        for item in evidence:
            source = source_map.get(item['id'])
            if not source or source.get('text') != item.get('text') or source.get('type') != item.get('type') or hashlib.sha256(source['text'].encode('utf-8')).hexdigest() != item['textSha256']:
                raise ValueError('Screenplay evidence no longer matches the pinned saved project')
        for lesson in lessons:
            canon=lesson_map.get((lesson.get('topic'),lesson.get('lessonId')))
            topic=topic_map.get(lesson.get('topic'))
            if not canon or not topic or lesson.get('lessonNumber') != canon.get('number') or lesson.get('lessonTitle') != canon.get('title') or lesson.get('topicGitBlobSha1') != topic.get('gitBlobSha1'):
                raise ValueError('Curriculum lesson metadata is not canonical')
            real=full_lessons.get((lesson['topic'],lesson['lessonId']))
            sections=[sec for sec in real.get('sections',[]) if sec.get('heading')==lesson.get('sectionHeadingReported')] if isinstance(real,dict) else []
            if len(sections)!=1:
                raise ValueError('Verified lesson section is missing or ambiguous')
            raw=json.dumps(sections[0],sort_keys=True,ensure_ascii=False).encode('utf8')
            if lesson.get('sectionSha256')!=hashlib.sha256(raw).hexdigest():
                raise ValueError('Curriculum section evidence no longer matches the verified archive')
        effects = choice.get('potentialImpacts', [])
        if not isinstance(effects, list) or not effects or any(x not in ('script', 'continuity', 'images', 'storyboard', 'runtime', 'learning') for x in effects):
            raise ValueError('Explicit potential impacts are required')
        decisions.append({
            'findingId': fid, 'reviewClassification': by_id[fid]['classification'],
            'recommendation': action, 'status': 'proposed-for-author-review',
            'rationale': notes.strip(),
            'whyNotAutomatic': choice.get('uncertainty') or 'Creative judgment belongs to the author',
            'creativeQuestion': by_id[fid].get('creativeQuestion'),
            'scriptPassageIds': [e['id'] for e in evidence],
            'craftLessonRefs': [{'topic':l['topic'],'lessonId':l['lessonId'], 'number':l['lessonNumber'],
                                 'fingerprint':l['topicGitBlobSha1']} for l in lessons],
            'potentialImpacts': list(dict.fromkeys(effects)),
            'nextExperiment': choice.get('nextExperiment') or 'Discuss in ChatGPT before any project write',
            'authorDecision': None,
        })
    if len(decisions) != len(findings):
        raise ValueError('All evidence findings require explicit disposition')
    return {
        'ok': True, 'project': ident, 'title':project.get('title'),
        'reviewId':review.get('reviewId'), 'readOnly':True, 'scriptModified':False,
        'imagesModified':False, 'projectMutated':False,
        'approvalState':'not-requested-or-recorded', 'recommendations':decisions,
        'curriculumProof':{
            'lessonMetadataAndGitBlobPins':True,
            'fullSourceBodiesEmbeddedInPlugin':True,
            'lessonBodiesVerifiedByThisDecisionTool':True,
            'verifiedLessonAndSectionReferences':True,
            'teachingLimits': 'Verified source and section evidence; creative interpretations remain subject to human review'
        },
        'nextStep':'Author reviews proposals; approved choices require a separate guarded story change and durable save.'
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',required=True,type=Path)
    p.add_argument('--review',required=True,type=Path)
    p.add_argument('--choices',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    try:
        if a.out.exists() or a.out.resolve() in (a.project.resolve(), a.review.resolve(), a.choices.resolve()):
            raise ValueError('Output exists or targets source file; refusing write')
        original=a.project.read_bytes()
        result=build_preview(original,json.loads(a.review.read_text()),json.loads(a.choices.read_text()))
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        if a.project.read_bytes()!=original:
            raise RuntimeError('Project unexpectedly changed during read-only process')
        print(json.dumps({'ok':True,'output':str(a.out),'decisions':len(result['recommendations']),
                          'projectMutated':False,'approvalState':result['approvalState']},indent=2))
    except (ValueError,OSError,TypeError,KeyError,json.JSONDecodeError,RuntimeError) as exc:
        print(json.dumps({'ok':False,'failClosed':True,'error':str(exc)}))
        return 2
    return 0

if __name__=='__main__':sys.exit(main())
