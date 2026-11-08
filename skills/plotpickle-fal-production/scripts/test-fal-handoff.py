import hashlib, importlib.util, io, json, tempfile, unittest
from PIL import Image
from pathlib import Path
p=Path(__file__).with_name('fal-handoff.py')
spec=importlib.util.spec_from_file_location('fal_handoff',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ADDR={'actNumber':1,'sequenceNumber':1,'blockNumber':1,'miniBlockNumber':1,'shotNumber':1}
def fixture(content=b'frame media'):
 h=hashlib.sha256(content).hexdigest()
 return json.dumps({'id':'story','revision':2,'title':'Test Story','sourceEvidence':{'screenplay':{'passages':[{'id':'source-1','text':'Original scene'}]}},'assetRegistry':{'assets':[{'id':'a1','approvedVariationId':'v1','variations':[{'id':'v1','portablePath':'assets/a.webp','contentHash':'sha256:'+h,'provenanceIds':['source-1'],'extensions':{'storyboardAddress':ADDR}}]}]}}).encode()
CUE='A gentle dolly towards the distant mountains, no changes in subject identity.'
class TestFalHandoff(unittest.TestCase):
 def test_no_media_blocks(self):
  d=m.prepare(fixture(),1,1,1,1,CUE)
  self.assertEqual(d['status'],'blocked-media-unverified');self.assertFalse(d['generationSubmitted']);self.assertFalse(d['costApproved']);self.assertEqual(d['editorial']['framesTotal'],72)
 def test_actual_media_hash_and_no_native_lock(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'assets'/'a.webp';f.parent.mkdir()
   buf=io.BytesIO();Image.new('RGB',(4,4),(32,64,96)).save(buf,format='WEBP')
   raw=buf.getvalue();f.write_bytes(raw)
   d=m.prepare(fixture(raw),1,1,1,1,CUE,t)
   self.assertTrue(d['positions'][0]['media']['bytesVerified'])
   self.assertEqual(d['status'],'blocked-review-save-lock')
   self.assertFalse(d['generationReadiness']['nativeSaveLockVerified'])
 def test_wrong_media_hash_blocks(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'assets'/'a.webp';f.parent.mkdir();f.write_bytes(b'wrong bytes')
   d=m.prepare(fixture(),1,1,1,1,CUE,t)
   self.assertEqual(d['positions'][0]['media']['state'],'hash-mismatch')
 def test_no_six_position_span(self):
  with self.assertRaisesRegex(ValueError,'end-shot'):m.prepare(fixture(),1,1,1,6,CUE)
 def test_missing_shot_keeps_position(self):
  d=m.prepare(fixture(),1,1,1,5,CUE)
  self.assertEqual(d['editorial']['framesTotal'],360)
  self.assertEqual(len(d['positions']),5)
  self.assertEqual(d['positions'][-1]['media']['state'],'not-recorded')
 def test_bad_address(self):
  with self.assertRaisesRegex(ValueError,'block'):m.prepare(fixture(),0,1,1,1,CUE)
 def test_no_fabricated_model_or_price(self):
  d=m.prepare(fixture(),1,1,1,1,CUE)
  self.assertEqual(d['modelSelection'],'pending-connected-model-discovery')
  self.assertFalse(d['generationReadiness']['currentCostQuoted'])
 def test_source_immutable(self):
  b=fixture();m.prepare(b,1,1,1,1,CUE);self.assertEqual(b,fixture())
 def test_invalid_path_blocks(self):
  d=json.loads(fixture());d['assetRegistry']['assets'][0]['variations'][0]['portablePath']='../../secret'
  out=m.prepare(json.dumps(d).encode(),1,1,1,1,CUE)
  self.assertEqual(out['positions'][0]['media']['state'],'unsafe-asset-path')
if __name__=='__main__':unittest.main(verbosity=2)
