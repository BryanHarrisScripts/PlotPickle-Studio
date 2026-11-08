import importlib.util, pathlib, unittest
p=pathlib.Path(__file__).parent/'reports.py'
s=importlib.util.spec_from_file_location('pp_reports',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Reports(unittest.TestCase):
 def test_eight_sections(self):
  r=m.report({'id':'a','revision':1,'sourceEvidence':{'screenplay':{'passages':[{'id':'p1','type':'scene-heading','text':'EXT. BEACH - DAY'},{'id':'p2','type':'character','text':'MARA'},{'id':'p3','type':'dialogue','text':'Hello world'}]}}},'a.ppf.json','abc')
  self.assertEqual(set(r['sections']),set(m.SECTIONS));self.assertEqual(r['sections']['dialogue']['recordedDialogueWords'],2)
  self.assertEqual(r['sections']['story']['canonicalPlannedShotPositions'],2400)
  self.assertIsNone(r['sections']['production']['verifiedMediaBytes'])
 def test_no_invented_connections(self):
  self.assertEqual(m.report({'id':'x','revision':0})['sections']['connections']['status'],'not checked')
 def test_project_identity_fail(self):
  import json,tempfile
  with tempfile.TemporaryDirectory() as tmp:
   f=pathlib.Path(tmp)/'a.json';f.write_text(json.dumps({'id':'a'}))
   with self.assertRaises(ValueError):m.load(f)
if __name__=='__main__':unittest.main()
