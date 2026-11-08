from pathlib import Path
import copy, importlib.util, tempfile, json, unittest
f=Path(__file__).with_name('service-catalog.py');spec=importlib.util.spec_from_file_location('creative_catalog',f)
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
class TestDirectLinks(unittest.TestCase):
 def setUp(self):self.cat=app.load_registry()
 def test_direct_fal(self):
  v=app.intent(self.cat,'fal','open-fal')
  self.assertEqual(v['openUrl'],'https://fal.ai/dashboard');self.assertFalse(v['conversationRequired']);self.assertFalse(v['creditsSpent'])
 def test_direct_suno(self):
  v=app.intent(self.cat,'suno','open-suno')
  self.assertEqual(v['openUrl'],'https://suno.com/');self.assertFalse(v['conversationRequired'])
 def test_paid_generation_still_requires_approval(self):
  v=app.intent(self.cat,'fal','generate-fal-clip')
  self.assertTrue(v['requiresExplicitCreditApproval']);self.assertFalse(v['providerInvoked'])
 def test_reject_redirect(self):
  v=copy.deepcopy(self.cat)
  next(s for s in v['services'] if s['id']=='fal')['actions'][1]['url']='https://example.com'
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'r.json';p.write_text(json.dumps(v))
   with self.assertRaises(AssertionError):app.load_registry(p)
if __name__=='__main__':unittest.main()
