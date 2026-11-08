import importlib.util, pathlib, json, tempfile, unittest, hashlib
BASE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('render',BASE/'render-story-explorer.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RenderTests(unittest.TestCase):
 def setup_case(self):
  tmp=tempfile.TemporaryDirectory();root=pathlib.Path(tmp.name)
  p={'title':'Synthetic Story','revision':0,'sourceEvidence':{'screenplay':{'passages':[
        {'id':'screenplay-1','type':'action','text':'<script>alert(1)</script>','blockNumber':1,'miniBlockNumber':1}]}},
    'assetRegistry':{'extensions':{'storyWorkflow':{'plans':[],'imageMappings':[],'truths':[]}}}}
  path=root/'project.ppf.json';path.write_text(json.dumps(p));return tmp,root,path
 def test_vanilla_project_no_images(self):
  t,root,path=self.setup_case()
  try:
   before=path.read_bytes();result=r.render(path,root/'out.html')
   self.assertEqual(result['shots'],0);self.assertEqual(result['images'],0)
   self.assertEqual(path.read_bytes(),before)
   self.assertNotIn('<script>alert(1)</script>',(root/'out.html').read_text())
  finally:t.cleanup()
 def test_image_integrity_rejects_changed_bytes(self):
  t,root,path=self.setup_case()
  try:
   (root/'assets').mkdir();(root/'assets'/'a.webp').write_bytes(b'bad')
   p=json.loads(path.read_text());p['assetRegistry']['extensions']['storyWorkflow']={
     'plans':[{'address':{'blockNumber':1,'miniBlockNumber':1},'shots':[
       {'shotNumber':7,'state':'PLANNED','narrativePurpose':'Test shot: Some action','prompt':'prompt',
        'passageIds':['screenplay-1'],'truthIds':[]}]}],
     'imageMappings':[{'address':{'blockNumber':1,'miniBlockNumber':1,'shotNumber':7},'portablePath':'assets/a.webp','sha256':'0'*64}],
     'truths':[]}
   path.write_text(json.dumps(p))
   with self.assertRaisesRegex(ValueError,'INVALID_MEDIA_HASH'):r.render(path,root/'out.html')
  finally:t.cleanup()
 def test_other_mini_block_source_and_lock_records(self):
  t,root,path=self.setup_case()
  try:
   (root/'assets').mkdir()
   raw=b'portable-asset-test'; (root/'assets'/'b.webp').write_bytes(raw)
   p=json.loads(path.read_text())
   p['sourceEvidence']['screenplay']['passages'].append({'id':'screenplay-2','type':'action','text':'A second act beat.','blockNumber':2,'miniBlockNumber':3})
   p['assetRegistry']['extensions']['storyWorkflow']={
       'plans':[{'address':{'blockNumber':2,'miniBlockNumber':3},'shots':[
          {'shotNumber':9,'state':'PLANNED','narrativePurpose':'New beat: Camera tilt',
           'prompt':'Exact stored prompt','passageIds':['screenplay-2'],'truthIds':[]}]}],
       'imageMappings':[{'address':{'blockNumber':2,'miniBlockNumber':3,'shotNumber':9},
           'portablePath':'assets/b.webp','sha256':hashlib.sha256(raw).hexdigest(),
           'promptOrigin':'captured','visualApproval':{'state':'accepted'},
           'savedMarkerPresent':True,'locked':True}], 'truths':[]}
   path.write_text(json.dumps(p))
   result=r.render(path,root/'out.html')
   html=(root/'out.html').read_text()
   self.assertEqual(result['shots'],1)
   self.assertEqual(result['images'],1)
   self.assertIn('"2.3"',html)
   self.assertIn('Exact stored prompt',html)
   self.assertIn('"saved": true',html)
   self.assertIn('"locked": true',html)
  finally:t.cleanup()
 def test_mapping_without_planned_slot_fails_closed(self):
  t,root,path=self.setup_case()
  try:
   p=json.loads(path.read_text())
   p['assetRegistry']['extensions']['storyWorkflow']['imageMappings']=[
       {'address':{'blockNumber':3,'miniBlockNumber':4,'shotNumber':9},
        'portablePath':'assets/absent.webp','sha256':'0'*64}]
   path.write_text(json.dumps(p))
   with self.assertRaisesRegex(ValueError,'IMAGE_MAPPING_WITHOUT_PLANNED_SHOT'):
    r.render(path,root/'out.html')
  finally:t.cleanup()
if __name__=='__main__':unittest.main(verbosity=2)
