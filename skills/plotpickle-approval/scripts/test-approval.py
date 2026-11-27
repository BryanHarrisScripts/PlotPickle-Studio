#!/usr/bin/env python3
"""No network, generation or project writes: self-tests for approval scope and image proof."""
import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('approval_audit',root/'audit-approved-scope.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class NativeApprovalAudit(unittest.TestCase):
  def setUp(self):
    self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name)
    (self.base/'assets').mkdir();self.media=self.base/'assets'/'shot.webp'
    Image.new('RGB',(128,72),'navy').save(self.media,'WEBP')
    self.hash=m.sha(self.media)
    art={'id':'a','reviewState':'accepted','sourceDecisionKeys':['storyboard-local-save:v1']}
    self.ppf={'id':'story-test','revision':2,'build':{'foundations':{'visualArtifacts':[art],'acceptedVisualArtifactIds':['a']}},
      'assetRegistry':{'extensions':{'storyWorkflow':{'plans':[{'address':{'blockNumber':1,'miniBlockNumber':1}}],
      'imageMappings':[{'artifactId':'a','address':{'blockNumber':1,'miniBlockNumber':1,'shotNumber':1},'savedMarkerPresent':True,'locked':True,
      'portablePath':'assets/shot.webp','sha256':self.hash}]}}}}
    self.file=self.base/'project.ppf.json';self.write()
  def write(self):self.file.write_text(json.dumps(self.ppf))
  def test_exact_readback_partial(self):
    r=m.audit(self.file)
    self.assertEqual(r['verifiedSavedAndLockedShots'],1)
    self.assertEqual(r['nativeShotTargetCount'],50)
    self.assertEqual(r['scopes'][0]['registeredShotMappings'],1)
    self.assertEqual(r['scopes'][1]['registeredShotMappings'],0)
    self.assertFalse(r['complete'])
  def test_cannot_forge_lock_from_approval(self):
    self.ppf['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]['locked']=False
    self.write()
    self.assertEqual(m.audit(self.file)['verifiedSavedAndLockedShots'],0)
  def test_missing_bytes_fails(self):
    self.media.unlink()
    self.assertEqual(m.audit(self.file)['scopes'][0]['unresolved'][0]['status'],'MEDIA_NOT_PRESENT')
  def test_changed_bytes_fails(self):
    Image.new('RGB',(128,72),'red').save(self.media,'WEBP')
    self.assertEqual(m.audit(self.file)['scopes'][0]['unresolved'][0]['status'],'MEDIA_HASH_MISMATCH')
  def test_unregistered_composite_does_not_count(self):
    self.ppf['assetRegistry']['assets']=[{'id':'approved-page','approval':'approved'}]
    self.write()
    self.assertEqual(m.audit(self.file)['scopes'][1]['verifiedSavedAndLocked'],0)
  def test_reference_must_have_save_and_lock_and_actual_bytes(self):
    x={'id':'mara','creatorApproved':True,'savedMarkerPresent':True,'locked':True,'portablePath':'assets/shot.webp','sha256':self.hash}
    self.ppf['assetRegistry']['extensions']['approvedDesignReferences']={'records':[x]};self.write()
    self.assertEqual(m.audit(self.file)['designReferencesVerifiedLocked'],1)
    x['locked']=False;self.write()
    self.assertEqual(m.audit(self.file)['designReferencesVerifiedLocked'],0)
  def test_unsafe_asset_path(self):
    x=self.ppf['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]
    x['portablePath']='assets/../outside.png';self.write()
    self.assertEqual(m.audit(self.file)['scopes'][0]['unresolved'][0]['status'],'UNSAFE_ASSET_PATH')
if __name__=='__main__':unittest.main(verbosity=2)
