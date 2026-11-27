import copy, hashlib, importlib.util, pathlib, tempfile, unittest
spec=importlib.util.spec_from_file_location('handoff',pathlib.Path(__file__).with_name('asset-handoff.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class Reconciliation(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);(self.root/'image').write_bytes(b'image');(self.root/'clip').write_bytes(b'clip')
  self.ih=h.digest(self.root/'image');self.vh=h.digest(self.root/'clip');self.ps='a'*64
  self.project={'id':'p','revision':1,'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[{'artifactId':'a','address':{'shotNumber':1},'passageIds':['p1'],'portablePath':'image','sha256':self.ih,'visualApproval':{'state':'approved','approvedCandidateSha256':self.ih},'savedMarkerPresent':True,'locked':True}]}}}}
  self.manifest={'project':{'id':'p','revision':1,'sha256':self.ps},'providers':[{'provider':'fal','scope':'explicit-test-scope','assetIds':['v'],'observedAt':'2026-11-10T22:00:00Z','paginationComplete':True,'scopeTruncated':False}], 'assets':[{'id':'v','provider':'fal','providerAssetId':'v','artifactId':'a','kind':'video','bytes':4,'sha256':self.vh,'submittedImageSha256':self.ih,'creativeApproval':'approved','creativeApprovalEvidenceRef':'explicit-test-fixture-approval','continuity':[{'kind':'world','state':'passed','evidenceRef':'r','imageSha256':self.ih}],'library':{'fileId':'libfile-test','localPath':'clip'}}]}
 def tearDown(self):self.tmp.cleanup()
 def run_audit(self):return h.audit(self.project,self.ps,self.manifest,self.root)
 def test_complete(self):
  r=self.run_audit();self.assertEqual(r['summary']['readyForEditor'],1);self.assertTrue(r['providers'][0]['allTransferredForEnumeratedScope'])
 def test_missing_bytes(self):
  (self.root/'clip').unlink();r=self.run_audit();self.assertFalse(r['assets'][0]['readyForEditor']);self.assertFalse(r['providers'][0]['allTransferredForEnumeratedScope'])
 def test_tampered_copy(self):
  (self.root/'clip').write_bytes(b'fake');self.assertEqual(self.run_audit()['assets'][0]['transfer'],'byte-or-hash-mismatch')
 def test_unknown_provider_asset(self):
  self.manifest['providers'][0]['assetIds'].append('older');r=self.run_audit();self.assertEqual(r['providers'][0]['unassignedAssetIds'],['older']);self.assertFalse(r['providers'][0]['allTransferredForEnumeratedScope'])
 def test_partial_listing(self):
  self.manifest['providers'][0]['scopeTruncated']=True;self.assertFalse(self.run_audit()['providers'][0]['allTransferredForEnumeratedScope'])
 def test_stale_project(self):
  self.manifest['project']['revision']=0;self.assertIn('project-version-mismatch',self.run_audit()['assets'][0]['issues'])
 def test_source_mismatch(self):
  self.manifest['assets'][0]['submittedImageSha256']='f'*64;self.assertIn('video-source-image-differs',self.run_audit()['assets'][0]['issues'])
 def test_path_escape(self):
  self.manifest['assets'][0]['library']['localPath']='../secret';self.assertEqual(self.run_audit()['assets'][0]['transfer'],'library-listed-unsafe-path')
 def test_symlink_escape(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'secret';p.write_text('secret');(self.root/'link').symlink_to(p);self.manifest['assets'][0]['library']['localPath']='link';self.assertEqual(self.run_audit()['assets'][0]['transfer'],'library-listed-unsafe-path')
 def test_changed_continuity(self):
  self.manifest['assets'][0]['continuity'][0]['imageSha256']='b'*64;self.assertIn('world-review-needed',self.run_audit()['assets'][0]['issues'])
 def test_no_silent_approval(self):
  del self.manifest['assets'][0]['creativeApproval'];self.assertIn('media-review-pending',self.run_audit()['assets'][0]['issues'])
 def test_duplicate_id(self):
  self.manifest['assets'].append(copy.deepcopy(self.manifest['assets'][0]));self.assertRaises(ValueError,self.run_audit)
if __name__=='__main__':unittest.main()
