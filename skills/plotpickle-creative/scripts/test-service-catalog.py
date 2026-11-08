import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
p=Path(__file__).with_name('service-catalog.py');spec=importlib.util.spec_from_file_location('catalog_module',p)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TestServiceCatalog(unittest.TestCase):
 def setUp(self):self.registry=mod.load_registry()
 def test_four_services(self):
  self.assertEqual([x['name'] for x in mod.catalog(self.registry)['services']],['Suno','fal','BUZZ','Modem'])
  self.assertFalse(mod.catalog(self.registry)['liveConnectionChecked'])
 def test_fal_not_connected_in_static_catalogue(self):
  s=next(x for x in self.registry['services'] if x['id']=='fal')
  self.assertEqual(s['status'],'not-confirmed-connected');self.assertFalse(s['credentialsStoredByPlotPickle']);self.assertNotIn('mcpServerUrl',s)
 def test_fal_brief_free(self):
  a=mod.intent(self.registry,'fal','prepare-fal-motion')
  self.assertFalse(a['providerInvoked']);self.assertFalse(a['creditsSpent']);self.assertFalse(a['hostConnectionVerificationRequired']);self.assertFalse(a['requiresExplicitCreditApproval'])
 def test_fal_payment_guard(self):
  a=mod.intent(self.registry,'fal','generate-fal-clip')
  self.assertTrue(a['hostConnectionVerificationRequired']);self.assertTrue(a['requiresExplicitCreditApproval']);self.assertFalse(a['creditsAuthorized']);self.assertFalse(a['providerInvoked'])
 def test_fal_connection_read_only(self):
  a=mod.intent(self.registry,'fal','check-fal')
  self.assertTrue(a['hostConnectionVerificationRequired']);self.assertFalse(a['requiresExplicitCreditApproval'])
 def test_suno_guard(self):
  a=mod.intent(self.registry,'suno','create-music');self.assertFalse(a['creditsSpent']);self.assertTrue(a['requiresExplicitCreditApproval'])
 def test_buzz_modem_planned(self):
  self.assertEqual([x['status'] for x in mod.catalog(self.registry)['services']][2:],['Planned · unavailable','Planned · unavailable'])
 def test_connected_forgery_fails(self):
  bad=copy.deepcopy(self.registry);bad['services'][1]['status']='connected'
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'r.json';f.write_text(json.dumps(bad))
   with self.assertRaisesRegex(AssertionError,'static registry'):mod.load_registry(f)
 def test_only_four_catalogue_entries(self):
  self.assertEqual([s['id'] for s in self.registry['services']],['suno','fal','buzz','modem'])
 def test_unknown_action_fails(self):
  with self.assertRaisesRegex(ValueError,'Unknown action'):mod.intent(self.registry,'fal','login-with-password')
if __name__=='__main__':unittest.main(verbosity=2)
