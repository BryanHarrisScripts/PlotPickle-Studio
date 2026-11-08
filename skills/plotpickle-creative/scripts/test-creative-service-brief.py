import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
p=Path(__file__).with_name('creative-service-brief.py')
s=importlib.util.spec_from_file_location('creative',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
P={'id':'project1','revision':3,'title':'Example','sourceEvidence':{'screenplay':{'passages':[{'id':'a','text':'Original scripted scene.'}]}}}
BYTES=json.dumps(P).encode(); SHA=hashlib.sha256(BYTES).hexdigest()
REG={'services':[{'id':'suno','status':'not-confirmed-connected','mcpServerUrl':'https://api.suno.com/mcp'}]}
REQ={'project':{'id':'project1','revision':3,'sha256':SHA},'service':'suno','action':'create','purpose':'Sketch a motif','brief':'Slow, uneasy instrumental that leaves room for dialogue.','passageIds':['a']}
class Tests(unittest.TestCase):
 def test_preview_no_mutation(self):
  result=m.prepare(BYTES,REQ,REG);self.assertFalse(result['mediaGenerated']);self.assertFalse(result['projectModified']);self.assertFalse(result['creditsAuthorized']);self.assertEqual(result['sourceEvidence'][0]['passageId'],'a')
 def test_bad_project(self):
  with self.assertRaisesRegex(ValueError,'identity'):m.prepare(BYTES,{**REQ,'project':{**REQ['project'],'revision':5}},REG)
 def test_unknown_provider(self):
  with self.assertRaisesRegex(ValueError,'Unknown'):m.prepare(BYTES,{**REQ,'service':'other'},REG)
 def test_missing_passage(self):
  with self.assertRaisesRegex(ValueError,'passage'):m.prepare(BYTES,{**REQ,'passageIds':['wrong']},REG)
 def test_no_fabricated_spend(self):
  with self.assertRaisesRegex(ValueError,'authorization'):m.prepare(BYTES,{**REQ,'creditAuthorization':'granted'},REG)
 def test_extend_needs_source(self):
  with self.assertRaisesRegex(ValueError,'source asset'):m.prepare(BYTES,{**REQ,'action':'extend'},REG)
 def test_external_record_not_verified(self):
  draft=m.prepare(BYTES,REQ,REG);ref=m.record_reference(draft,{'service':'suno','providerAssetId':'a','providerAssetUrl':'https://suno.com/song/123'});self.assertFalse(ref['mediaGeneratedVerified']);self.assertFalse(ref['mediaApproved'])
 def test_foreign_link_rejected(self):
  draft=m.prepare(BYTES,REQ,REG)
  with self.assertRaisesRegex(ValueError,'host'):m.record_reference(draft,{'service':'suno','providerAssetId':'a','providerAssetUrl':'https://malicious.example/123'})
if __name__=='__main__': unittest.main()
