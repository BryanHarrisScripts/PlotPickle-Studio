import hashlib,importlib.util,json,pathlib,subprocess,tempfile,unittest
P=pathlib.Path(__file__).resolve().parent
class Changes(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=pathlib.Path(self.tmp.name)
  f=self.d/'s.fdx';f.write_text('<FinalDraft><Content>'+''.join('<Paragraph Type="Action"><Text>Beat '+str(i)+'.</Text></Paragraph>' for i in range(1,5))+'</Content></FinalDraft>')
  self.runcli('story-workflow.py','import-fdx','--file',f,'--title','Fixture','--out',self.d/'base');self.project=self.d/'base/project.ppf.json'
 def tearDown(self):self.tmp.cleanup()
 def runcli(self,script,*a,ok=True):
  r=subprocess.run(['python3',str(P/script),*map(str,a)],text=True,capture_output=True)
  if ok:self.assertEqual(r.returncode,0,r.stdout+r.stderr);return json.loads(r.stdout)
  self.assertNotEqual(r.returncode,0);return r.stderr
 def identity(self):
  r=subprocess.run(['node',str(P/'inspect-project.mjs'),'--file',str(self.project),'--operation','identity'],text=True,capture_output=True);return json.loads(r.stdout)['project']
 def pins(self):
  i=self.identity();return ['--project',self.project,'--project-id',i['id'],'--revision',i['revision'],'--sha256',i['sha256']]
 def payload(self):
  groups=[{'actNumber':n,'title':str(n),'reason':'Explicit fixture placement.','placements':[{'passageId':'screenplay-'+str(n),'blockNumber':(n-1)*6+1,'miniBlockNumber':1}]} for n in range(1,5)]
  groups[0]['placements'].append({'passageId':'author-test-new','blockNumber':1,'miniBlockNumber':1})
  return {'id':'test-change','project':self.identity(),'authorship':{'kind':'user','instruction':'Add a beat and revise another.','authorization':'Synthetic test instruction.'},'storyScopePassageIds':['screenplay-'+str(n) for n in range(1,5)],'fourActs':groups,
   'operations':[{'kind':'insert-after','afterPassageId':'screenplay-1','passages':[{'id':'author-test-new','type':'action','text':'New author beat.'}]},{'kind':'replace','passageId':'screenplay-2','expectedText':'Beat 2.','text':'Revised beat 2.'}]}
 def call(self,payload,label='result',ok=True):
  file=self.d/'change.json';file.write_text(json.dumps(payload));return self.runcli('apply-story-change.py',*self.pins(),'--file',file,'--out',self.d/label,ok=ok)
 def test_source_revision_preserves_identity_and_records_author(self):
  before=self.project.read_bytes();self.call(self.payload());p=json.loads((self.d/'result/project.ppf.json').read_text())
  self.assertEqual(p['id'],self.identity()['id']);self.assertEqual(p['revision'],1);self.assertEqual(len(p['sourceEvidence']['screenplay']['passages']),5);self.assertEqual(before,self.project.read_bytes())
  m=p['assetRegistry']['extensions']['projectModel'];self.assertEqual(m['storyChanges'][0]['authorship']['kind'],'user');self.assertEqual(len(m['fourActPlan']['groups']),4)
 def test_expected_text_failure_leaves_no_output(self):
  p=self.payload();p['operations'][1]['expectedText']='Stale text.';self.assertIn('BEFORE_TEXT_CHANGED',self.call(p,ok=False));self.assertFalse((self.d/'result').exists())
 def test_wrong_act_rejected(self):
  p=self.payload();p['fourActs'][3]['placements'][0]['blockNumber']=1;self.assertIn('ACT_ADDRESS_MISMATCH',self.call(p,ok=False))
 def test_image_hash_and_visual_approval_are_separate_from_lock(self):
  from PIL import Image
  image=self.d/'image.png';Image.new('RGB',(32,18),'blue').save(image);p=self.payload()
  p['images']=[{'path':str(image),'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'passageIds':['author-test-new'],'label':'New beat','prompt':'A fixture visual.','promptOrigin':'captured'}]
  self.call(p);out=json.loads((self.d/'result/project.ppf.json').read_text());art=out['build']['foundations']['visualArtifacts'][0]
  self.assertEqual(art['reviewState'],'draft');self.assertNotIn('storyboard-local-save:v1',art['sourceDecisionKeys']);self.assertEqual(out['build']['foundations']['acceptedVisualArtifactIds'],[])
  p['images'][0]['sha256']='0'*64;self.assertIn('IMAGE_BYTES_CHANGED',self.call(p,label='bad',ok=False))
if __name__=='__main__':unittest.main(verbosity=2)
