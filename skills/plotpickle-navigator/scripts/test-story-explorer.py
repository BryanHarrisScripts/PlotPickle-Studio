import argparse, importlib.util, pathlib, unittest
p=pathlib.Path(__file__).with_name('story-explorer.py')
s=importlib.util.spec_from_file_location('nav',p);nav=importlib.util.module_from_spec(s);s.loader.exec_module(nav)

def args(view,act=None,sequence=None,block=None,mini=None,shot=None):
 return argparse.Namespace(view=view,act=act,sequence=sequence,block=block,mini=mini,shot=shot)

class NavigationContracts(unittest.TestCase):
 def test_structure_math(self):
  a=nav.check_address(args('shot',act=2,sequence=1,block=1,mini=1,shot=25))
  self.assertEqual((a['blockGlobal'],a['sequenceGlobal']), (7,4))
 def test_invalid_address_blocks(self):
  for obj in [args('shot',act=1,block=1,mini=1,shot=26), args('mini',act=5,block=1,mini=1),
              args('block',act=1,sequence=1,block=3), args('shot',act=1,block=1,shot=7)]:
   with self.assertRaises(ValueError):nav.check_address(obj)
 def test_source_is_exact_and_scoped(self):
  d={'sourceEvidence':{'screenplay':{'passages':[
   {'id':'p1','type':'action','text':'Source A','blockNumber':1,'miniBlockNumber':1},
   {'id':'p2','type':'action','text':'Source B','blockNumber':1,'miniBlockNumber':2},
   {'id':'p3','type':'dialogue','text':'Source C','blockNumber':7,'miniBlockNumber':1}]}}}
  self.assertEqual([r['text'] for r in nav.passages_in(d,1,1)],['Source A'])
  self.assertEqual([r['text'] for r in nav.passages_in(d,7,1)],['Source C'])
 def test_readonly_native_calls_and_25_slots(self):
  import json, tempfile
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as t:
   f=pathlib.Path(t)/'x.ppf.json'
   f.write_text(json.dumps({'sourceEvidence':{'screenplay':{'passages':[]}}}))
   ins=nav.READERS/'inspect-project.mjs';rev=nav.READERS/'storyboard-review.py'
   # Test with stubbed native reader files, no source alteration.
   files=nav.READERS;files.mkdir(parents=True,exist_ok=True)
   made=[]
   for file in [ins,rev]:
    if not file.exists():file.touch();made.append(file)
   def fake(*cmd):
    if '--operation' in cmd:return {'project':{'id':'abc','revision':2,'sha256':'123'}}
    return {'shots':[{'address':{'shotNumber':i},'shotStatus':'GAP','sourceEvidence':[], 'candidates':[]} for i in range(1,26)],'fileAndRecordCounts':{}}
   a=args('shot',act=1,block=1,mini=1,shot=7)
   a.project=str(f);a.expected_id='abc';a.expected_revision=2;a.expected_sha256='123'
   before=f.read_bytes()
   try:
    with patch.object(nav,'native',side_effect=fake):v=nav.navigate(a)
    self.assertEqual(v['shotDetail']['shot'],7)
    self.assertEqual(v['shotDetail']['storyboardPrompt']['state'],'not authored')
    self.assertEqual(v['shotDetail']['authoredBeat']['state'],'not separately verified')
    self.assertEqual(f.read_bytes(),before)
    a.expected_sha256='wrong'
    with patch.object(nav,'native',side_effect=fake),self.assertRaisesRegex(ValueError,'STALE_PROJECT_FINGERPRINT'):nav.navigate(a)
   finally:
    for file in made:file.unlink()

if __name__=='__main__':unittest.main(verbosity=2)
