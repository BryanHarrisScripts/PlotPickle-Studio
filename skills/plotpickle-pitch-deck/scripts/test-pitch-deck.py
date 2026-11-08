import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).parent/'pitch-deck.py';s=importlib.util.spec_from_file_location('pp_pitch',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Pitch(unittest.TestCase):
 def test_presentation_no_fabrications(self):
  r=m.presentation({'id':'x','revision':1,'title':'Trial'},'abc')
  self.assertEqual(len(r['slides']),12);self.assertIn('placeholder',[x['truth'] for x in r['slides']]);self.assertFalse(r['spend'])
 def test_comic_math(self):
  r=m.comic({'id':'x','revision':1},'abc')
  self.assertEqual(len(r['pages']),24);self.assertEqual(sum(len(p['panels']) for p in r['pages']),96)
  self.assertEqual(r['pages'][23]['panels'][3]['miniBlockNumber'],4)
  self.assertEqual(r['pages'][23]['panels'][3]['status'],'unmapped')
 def test_source_validation(self):
  with self.assertRaises(ValueError):m.source({'id':'x'},'h')
if __name__=='__main__':unittest.main()
