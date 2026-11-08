#!/usr/bin/env python3
"""Read-only evidence binder for PlotPickle creative guidance.

This script binds authored craft findings to exact saved source passages, canonical
lesson IDs, and a pinned project revision. It does not generate conclusions,
certify semantic accuracy, approve proposals, or mutate project truth.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'
ALLOWED = {'supported-observation','interpretation','creative-question','opportunity'}


def verified_lessons():
    path=Path(__file__).with_name('curriculum-bridge.py')
    spec=importlib.util.spec_from_file_location('plotpickle_curriculum_bridge',path)
    bridge=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    records=bridge.verified_library(bridge.load_manifest(),DATA/'learn')
    return {(topic['id'], lesson['id']):lesson for topic,body in records for lesson in body['lessons']}



def digest(data):
    return hashlib.sha256(data).hexdigest()


def evidence_review(project_bytes, review, catalog, inventory):
    project = json.loads(project_bytes)
    ident = {'id': project.get('id'), 'revision': project.get('revision'), 'sha256': digest(project_bytes)}
    provided = review.get('project')
    if not isinstance(provided, dict) or any(provided.get(k) != v for k,v in ident.items()):
        raise ValueError('Project identity/revision/SHA-256 mismatch; reopen the current saved snapshot')
    raw = project.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])
    if not isinstance(raw,list) or not raw:
        raise ValueError('Saved project has no retained screenplay passages')
    passages = {}
    for item in raw:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not isinstance(item.get('text'),str):
            raise ValueError('Malformed screenplay record')
        if item['id'] in passages:
            raise ValueError('Duplicate screenplay passage ID')
        passages[item['id']] = item
    lessons = {(r['topic'],r['id']):r for r in catalog['lessons']}
    topic_meta = {r['id']:r for r in inventory['topics']}
    if len(lessons) != 81 or catalog['lessonCount'] != 81 or len(topic_meta) != 12:
        raise ValueError('Incomplete curriculum catalogue; cannot bind lessons')
    actual_lessons = verified_lessons()
    findings = review.get('findings')
    if not isinstance(findings,list) or not findings or len(findings)>25:
        raise ValueError('Review must contain 1–25 evidence-backed findings')
    out = []
    used_ids = set()
    for f in findings:
        fid = f.get('id')
        if not isinstance(fid,str) or not fid or fid in used_ids:
            raise ValueError('Missing/duplicate finding ID')
        used_ids.add(fid)
        if f.get('classification') not in ALLOWED or not isinstance(f.get('claim'),str) or not f['claim'].strip():
            raise ValueError('Invalid finding type/claim')
        refs = f.get('passageIds')
        if not isinstance(refs,list) or not refs or len(refs)!=len(set(refs)) or any(p not in passages for p in refs):
            raise ValueError(f'Unknown/duplicate/empty passage evidence: {fid}')
        lc = f.get('lessonRefs')
        if not isinstance(lc,list) or not lc:
            raise ValueError(f'Finding lacks actual curriculum references: {fid}')
        bound_lessons=[]
        for link in lc:
            lesson=lessons.get((link.get('topic'),link.get('lessonId')))
            meta=topic_meta.get(link.get('topic'))
            if not lesson or not meta:
                raise ValueError('Unknown curriculum lesson ID')
            if link.get('gitBlobSha1') != meta['gitBlobSha1']:
                raise ValueError('Curriculum topic fingerprint mismatch')
            if not isinstance(link.get('heading'),str) or not link['heading'].strip():
                raise ValueError('Curriculum heading required as review evidence')
            body=actual_lessons.get((lesson['topic'],lesson['id']))
            if not body or body.get('title') != lesson['title'] or body.get('number') != lesson['number']:
                raise ValueError('Lesson source is missing or differs from verified catalogue')
            sections=[sec for sec in body.get('sections',[]) if isinstance(sec,dict) and sec.get('heading') == link['heading']]
            if not sections:
                raise ValueError('Curriculum heading not found in the verified lesson body')
            sec=sections[0]
            sec_bytes=json.dumps(sec,sort_keys=True,ensure_ascii=False).encode('utf-8')
            excerpt=next((v.strip() for v in sec.get('paragraphs',[]) if isinstance(v,str) and v.strip()),'')[:500]
            bound_lessons.append({'topic':lesson['topic'],'lessonId':lesson['id'],'lessonNumber':lesson['number'],
                                  'lessonTitle':lesson['title'],'sectionHeadingReported':link['heading'],
                                  'topicGitBlobSha1':meta['gitBlobSha1'], 'curationStatus':meta['completion'],
                                  'sectionSha256':digest(sec_bytes), 'teachingExcerpt':excerpt,
                                  'lessonBodyVerifiedByBinder':True,'lessonSectionVerifiedByBinder':True})
        out.append({'id':fid,'classification':f['classification'],'claim':f['claim'],
                    'evidence':[{'id':r,'type':passages[r].get('type'),
                                 'text':passages[r]['text'],
                                 'textSha256':digest(passages[r]['text'].encode('utf-8'))} for r in refs],
                    'lessons':bound_lessons,
                    'creativeQuestion':f.get('creativeQuestion'),
                    'editorialSemanticsVerifiedByBinder':False})
    return {'ok':True,'reviewId':review.get('reviewId'),'project':ident,
            'title':project.get('title'),'savedSourcePassageCount':len(passages),
            'mode':'read-only','projectMutated':False,'findings':out,
            'curriculumSourceVerified':True,'canonicalLessonCount':81,'canonicalSourceCount':95,
            'limits':['Verified bytes, section headings and evidence hashes do not prove interpretive correctness.',
                      'The binder does not prove that teaching claims follow from lesson text or that craft judgments are correct.',
                      'No proposal is adopted; no Save, Lock, or human approval is inferred.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',required=True)
    ap.add_argument('--review',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    try:
        path=Path(args.project)
        review=json.loads(Path(args.review).read_text(encoding='utf-8'))
        cat=json.loads((DATA/'lesson-catalog.json').read_text(encoding='utf-8'))
        inv=json.loads((DATA/'curriculum-index.json').read_text(encoding='utf-8'))
        result=evidence_review(path.read_bytes(),review,cat,inv)
        dst=Path(args.out)
        if dst.resolve() == path.resolve():
            raise ValueError('Output must not overwrite the source project')
        if dst.exists():
            raise ValueError('Output exists; refuse accidental overwrite')
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'ok':True,'output':str(dst),'project':result['project'],
                          'findings':len(result['findings']),'projectMutated':False},indent=2))
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        print(json.dumps({'ok':False,'failClosed':True,'error':str(exc)}))
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
