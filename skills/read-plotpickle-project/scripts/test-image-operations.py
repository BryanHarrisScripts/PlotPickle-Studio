import hashlib, importlib.util, json, pathlib, subprocess, tempfile, unittest
from types import SimpleNamespace
from PIL import Image
P=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('images',P/'image-operations.py'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Images(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=pathlib.Path(self.tmp.name)
  f=self.d/'s.fdx';f.write_text('<FinalDraft><Content><Paragraph Type="Action"><Text>A closing beat.</Text></Paragraph></Content></FinalDraft>')
  subprocess.run(['python3',str(P/'story-workflow.py'),'import-fdx','--file',str(f),'--title','Test','--out',str(self.d/'base')],check=True,capture_output=True)
  self.project=self.d/'base/project.ppf.json';im=self.d/'i.png';Image.new('RGB',(48,32),'blue').save(im)
  self.image={'path':str(im),'sha256':hashlib.sha256(im.read_bytes()).hexdigest(),'prompt':'Fixture.','promptOrigin':'captured','label':'Frame'};self.n=0
 def tearDown(self):self.tmp.cleanup()
 def runop(self,kind,**data):
  self.n+=1;i=m.wf.identity(self.project);f=self.d/'op.json';f.write_text(json.dumps({'project':i,'kind':kind,'id':'event-'+str(self.n),'reason':'Test change.','authorization':'Fixture delegated instruction.',**data}))
  args=SimpleNamespace(project=str(self.project),project_id=i['id'],revision=i['revision'],sha256=i['sha256'],file=str(f),out=str(self.d/('out'+str(self.n))))
  out=m.apply(args);self.project=pathlib.Path(out['directory'])/'project.ppf.json';return out
 def add(self,shot=1):return self.runop('add',address=m.wf.address(1,1,shot),passageIds=['screenplay-1'],image=self.image)['imageChange']['newArtifactId']
 def test_pending_bad_bytes_then_replacement_preserves_beat(self):
  aid=self.add();before=json.loads(self.project.read_text())['sourceEvidence'];self.runop('begin-replacement',artifactId=aid)
  ref=self.project;bad={**self.image,'sha256':'0'*64}
  with self.assertRaisesRegex(ValueError,'IMAGE_BYTES_CHANGED'):self.runop('complete-replacement',artifactId=aid,pendingId='event-2',image=bad)
  self.assertEqual(len(m.active(json.loads(ref.read_text()))),1);self.assertFalse((self.d/'out3').exists())
  out=self.runop('complete-replacement',artifactId=aid,pendingId='event-2',image=self.image)
  self.assertEqual(out['activeImages'],1);self.assertEqual(out['pendingReplacements'],0)
  p=json.loads(self.project.read_text());self.assertEqual(p['sourceEvidence'],before)
  a=m.active(p)[0];self.assertEqual(a['reviewState'],'draft');self.assertNotIn('storyboard-local-save:v1',a['sourceDecisionKeys']);self.assertEqual(p['build']['foundations']['acceptedVisualArtifactIds'],[])
 def test_add_move_remove_and_collision(self):
  a=self.add();b=self.add(2)
  with self.assertRaisesRegex(ValueError,'SLOT_OCCUPIED'):self.runop('move',artifactId=b,address=m.wf.address(1,1,1))
  self.assertEqual(self.runop('move',artifactId=b,address=m.wf.address(1,1,3))['imageChange']['activeDelta'],0)
  self.assertEqual(self.runop('remove',artifactId=a)['activeImages'],1)
  self.assertEqual(len(json.loads(self.project.read_text())['sourceEvidence']['screenplay']['passages']),1)
 def test_restoration_is_separate_from_replacement_arithmetic(self):
  a=self.add();self.runop('remove',artifactId=a)
  with self.assertRaisesRegex(ValueError,'EXPLICIT_RESTORE'):self.runop('begin-replacement',artifactId=a)
  out=self.runop('begin-replacement',artifactId=a,restoreReference=True,address=m.wf.address(1,1,1))
  self.assertEqual(out['imageChange']['referenceRestorations'],1);self.assertEqual(out['activeImages'],1)
  out=self.runop('cancel-replacement',artifactId=a,pendingId=out['imageChange']['id']);self.assertEqual(out['activeImages'],1)
 def test_pending_stale_source_and_pin_blocked(self):
  a=self.add();self.runop('begin-replacement',artifactId=a)
  p=json.loads(self.project.read_text());p['sourceEvidence']['screenplay']['passages'][0]['text']='Changed beat.';self.project.write_text(json.dumps(p))
  with self.assertRaisesRegex(ValueError,'PENDING_REPLACEMENT_STALE'):self.runop('complete-replacement',artifactId=a,pendingId='event-2',image=self.image)
  i=m.wf.identity(self.project);args=SimpleNamespace(project=str(self.project),project_id=i['id'],revision=i['revision']-1,sha256=i['sha256'])
  with self.assertRaisesRegex(ValueError,'STALE_PROJECT'):m.wf.pinned(args)
if __name__=='__main__':unittest.main(verbosity=2)
