import importlib.util,io,pathlib,tempfile,unittest
P=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('review',P/'storyboard-review.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class FileTruth(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.t.name).resolve()
 def tearDown(self):self.t.cleanup()
 def test_valid_missing_changed_and_unsafe_files(self):
  from PIL import Image
  p=self.base/'frame.webp';Image.new('RGB',(32,18),'blue').save(p)
  r={'portablePath':'frame.webp','sha256':m.wf.digest(p.read_bytes())}
  self.assertEqual(m.verify(self.base,r)['state'],'verified')
  r['sha256']='0'*64;self.assertEqual(m.verify(self.base,r)['state'],'hash-mismatch')
  p.unlink();self.assertEqual(m.verify(self.base,r)['state'],'missing')
  r['portablePath']='../outside.webp';self.assertEqual(m.verify(self.base,r)['state'],'unsafe-path')
 def test_matching_hash_is_not_image_decoding(self):
  p=self.base/'bad.webp';p.write_bytes(b'broken image');r={'portablePath':p.name,'sha256':m.wf.digest(p.read_bytes())}
  self.assertEqual(m.verify(self.base,r)['state'],'decode-failed');self.assertFalse(m.verify(self.base,r)['bytesVerified'])
 def test_missing_mapping_is_unknown(self):self.assertEqual(m.verify(self.base,None)['state'],'unmapped')
if __name__=='__main__':unittest.main(verbosity=2)
