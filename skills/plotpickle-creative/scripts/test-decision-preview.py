import importlib.util
import copy
import hashlib
import json
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('pp_decision_preview',Path(__file__).with_name('decision-preview.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class ReviewToDecisionTests(unittest.TestCase):
    def setUp(self):
        self.project=json.dumps({'id':'example','revision':4,'title':'Synthetic Source',
            'sourceEvidence':{'screenplay':{'passages':[{'id':'s1','type':'action','text':'A door closes.'}]}}}).encode()
        self.ident={'id':'example','revision':4,'sha256':hashlib.sha256(self.project).hexdigest()}
        catalog=json.loads((Path(__file__).resolve().parents[1]/'data'/'lesson-catalog.json').read_text())
        inventory=json.loads((Path(__file__).resolve().parents[1]/'data'/'curriculum-index.json').read_text())
        lesson=next(x for x in catalog['lessons'] if x['topic']=='character')
        topic=next(x for x in inventory['topics'] if x['id']=='character')
        body=json.loads((Path(__file__).resolve().parents[1]/'data'/'learn'/'character.json').read_text())
        canonical=next(l for l in body['lessons'] if l['id']==lesson['id'])
        section=canonical['sections'][0]
        section_sha=hashlib.sha256(json.dumps(section,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
        self.review={'ok':True,'project':self.ident,'projectMutated':False,'reviewId':'test',
                     'findings':[{'id':'f1','classification':'interpretation','evidence':[{'id':'s1','type':'action','text':'A door closes.','textSha256':hashlib.sha256(b'A door closes.').hexdigest()}],
                                  'lessons':[{'topic':'character','lessonId':lesson['id'],'lessonTitle':lesson['title'],'lessonNumber':lesson['number'],
                                              'topicGitBlobSha1':topic['gitBlobSha1'],'lessonBodyVerifiedByBinder':True,'lessonSectionVerifiedByBinder':True,'sectionHeadingReported':section['heading'],'sectionSha256':section_sha}],
                                  'creativeQuestion':'Why?'}]}
        self.choices={'project':self.ident,'choices':[{'findingId':'f1','recommendation':'visual-test',
                                                     'rationale':'Check a visible choice','potentialImpacts':['storyboard','learning']} ]}
    def test_preserves_creative_authority(self):
        r=mod.build_preview(self.project,self.review,self.choices)
        self.assertFalse(r['projectMutated']);self.assertIsNone(r['recommendations'][0]['authorDecision'])
        self.assertEqual('proposed-for-author-review',r['recommendations'][0]['status'])
        self.assertTrue(r['curriculumProof']['fullSourceBodiesEmbeddedInPlugin'])
    def test_stale_project_blocked(self):
        self.choices['project']=dict(self.ident,revision=5)
        with self.assertRaisesRegex(ValueError,'identity'):mod.build_preview(self.project,self.review,self.choices)
    def test_fake_finding_blocked(self):
        self.choices['choices'][0]['findingId']='imaginary'
        with self.assertRaisesRegex(ValueError,'Unknown'):mod.build_preview(self.project,self.review,self.choices)
    def test_tampered_evidence_blocked(self):
        self.review['findings'][0]['evidence'][0]['text']='Rewritten without project approval.'
        with self.assertRaisesRegex(ValueError,'evidence'):mod.build_preview(self.project,self.review,self.choices)

    def test_fabricated_lesson_number_blocked(self):
        self.review['findings'][0]['lessons'][0]['lessonNumber']=1000
        with self.assertRaisesRegex(ValueError,'metadata'):mod.build_preview(self.project,self.review,self.choices)

    def test_missing_disposition_blocked(self):
        self.choices['choices']=[]
        with self.assertRaisesRegex(ValueError,'All'):mod.build_preview(self.project,self.review,self.choices)
    def test_unverified_lesson_blocked(self):
        self.review['findings'][0]['lessons'][0]['lessonBodyVerifiedByBinder']=False
        with self.assertRaisesRegex(ValueError,'independently verified'):mod.build_preview(self.project,self.review,self.choices)

    def test_changed_section_blocked(self):
        self.review['findings'][0]['lessons'][0]['sectionSha256']='0'*64
        with self.assertRaisesRegex(ValueError,'section evidence'):mod.build_preview(self.project,self.review,self.choices)

if __name__=='__main__': unittest.main()
