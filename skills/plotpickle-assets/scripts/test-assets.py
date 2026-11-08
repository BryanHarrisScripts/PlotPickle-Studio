import importlib.util, pathlib, unittest, tempfile, hashlib
p=pathlib.Path(__file__).parent/'assets.py';s=importlib.util.spec_from_file_location('pp_assets',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Assets(unittest.TestCase):
 def test_empty_groups(self):
  r=m.inventory({'id':'x','revision':1,'assetRegistry':{'assets':[]}},'abc',None)
  self.assertEqual(set(r['categories']),set(m.CATEGORIES));self.assertEqual(r['summary']['recordedAssetCount'],0)
 def test_verification(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);(root/'a.webp').write_bytes(b'image')
   self.assertEqual(m.verify_path(root,'a.webp',hashlib.sha256(b'image').hexdigest()),'hash-verified')
   self.assertEqual(m.verify_path(root,'a.webp','0'*64),'hash-mismatch')
   self.assertEqual(m.verify_path(root,'../outside','0'*64),'unsafe-path')
   self.assertEqual(m.verify_path(None,'a.webp','0'*64),'not-supplied')
 def test_classify(self):
  self.assertEqual(m.classify({'kind':'image','targets':[{'kind':'storyboard-frame'}]}),'Storyboard Images')
if __name__=='__main__':unittest.main()
