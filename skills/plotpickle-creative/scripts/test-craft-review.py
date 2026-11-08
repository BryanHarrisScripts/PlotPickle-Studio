import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('craft_review',BASE/'scripts'/'craft-review.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CraftReviewTests(unittest.TestCase):
    def setUp(self):
        self.cat=json.loads((BASE/'data'/'lesson-catalog.json').read_text())
        self.inv=json.loads((BASE/'data'/'curriculum-index.json').read_text())
        self.data=json.dumps({'id':'fictional-test','revision':2,'title':'Synthetic Test',
            'sourceEvidence':{'screenplay':{'passages':[{'id':'screenplay-1','type':'action','text':'The door closes.'}]}}}).encode()
        self.identity={'id':'fictional-test','revision':2,'sha256':mod.digest(self.data)}
        lesson=next(x for x in self.cat['lessons'] if x['topic']=='structure' and x['id']=='24b-dynamic-scenes')
        blob=next(x for x in self.inv['topics'] if x['id']=='structure')['gitBlobSha1']
        self.review={'project':self.identity,'reviewId':'synthetic','findings':[
            {'id':'finding1','classification':'creative-question','claim':'What changed?',
             'passageIds':['screenplay-1'],
             'lessonRefs':[{'topic':'structure','lessonId':lesson['id'],'gitBlobSha1':blob,'heading':'The dynamic scene chain'}]}]}

    def test_binds_real_passages_to_real_lesson_ids(self):
        result=mod.evidence_review(self.data,self.review,self.cat,self.inv)
        self.assertFalse(result['projectMutated'])
        self.assertEqual('screenplay-1',result['findings'][0]['evidence'][0]['id'])
        self.assertTrue(result['findings'][0]['lessons'][0]['lessonBodyVerifiedByBinder'])

    def test_unknown_heading_blocked(self):
        self.review['findings'][0]['lessonRefs'][0]['heading']='Unsupported fabrication'
        with self.assertRaisesRegex(ValueError,'heading'):mod.evidence_review(self.data,self.review,self.cat,self.inv)

    def test_wrong_snapshot_blocked(self):
        self.review['project']['revision']=3
        with self.assertRaisesRegex(ValueError,'identity'):mod.evidence_review(self.data,self.review,self.cat,self.inv)

    def test_unknown_passage_blocked(self):
        self.review['findings'][0]['passageIds']=['screenplay-999']
        with self.assertRaisesRegex(ValueError,'passage'):mod.evidence_review(self.data,self.review,self.cat,self.inv)

    def test_fabricated_lesson_blocked(self):
        self.review['findings'][0]['lessonRefs'][0]['lessonId']='fake'
        with self.assertRaisesRegex(ValueError,'Unknown curriculum'):mod.evidence_review(self.data,self.review,self.cat,self.inv)

    def test_changed_blob_blocked(self):
        self.review['findings'][0]['lessonRefs'][0]['gitBlobSha1']='0'*40
        with self.assertRaisesRegex(ValueError,'fingerprint'):mod.evidence_review(self.data,self.review,self.cat,self.inv)

if __name__=='__main__':unittest.main()
