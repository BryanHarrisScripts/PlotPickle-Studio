import copy, hashlib, importlib.util, json, shutil, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from PIL import Image

S=Path(__file__).with_name('default-save-lock.py')
spec=importlib.util.spec_from_file_location('default_save_lock',S)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FakeWF:
    def call_node(self, script, *args):
        if script!='inspect-project.mjs' or '--operation' not in args or args[args.index('--operation')+1]!='shots':
            raise ValueError('unexpected fake canonical reader request')
        p=self.read_json(args[args.index('--file')+1])
        b=int(args[args.index('--block')+1]);mm=int(args[args.index('--mini')+1])
        art,accepted,maps=m.records(p)
        shots=[]
        for n in range(1,26):
            row={'address':{'shotNumber':n},'candidates':[]}
            r=maps.get(f'{b}:{mm}:{n}')
            if r:
                x=art[r['artifactId']]
                saved=m.SAVE in x['sourceDecisionKeys']
                row['candidates']=[{'id':x['id'],'savedMarkerPresent':saved,'locked':saved and x['id'] in accepted and x['reviewState']=='accepted'}]
            shots.append(row)
        return {'shots':shots}
    """Isolated project snapshot adapter; native Node PPF validation remains a separately required integration test."""
    def identity(self,path):
        p=Path(path);j=json.loads(p.read_text());return {'id':j['id'],'revision':j['revision'],'sha256':m.digest(p.read_bytes())}
    def read_json(self,path):return json.loads(Path(path).read_text())
    def pinned(self,args):
        j=self.read_json(args.project);ident=self.identity(args.project)
        if (args.project_id,args.revision,args.sha256)!=(ident['id'],ident['revision'],ident['sha256']):raise ValueError('STALE_PROJECT')
        return j,ident
    def save_snapshot(self,args,project):
        dest=Path(args.out)
        if dest.exists():raise ValueError('OUTPUT_EXISTS')
        dest.mkdir(parents=True)
        source=Path(args.project).parent/'assets'
        if source.is_dir():shutil.copytree(source,dest/'assets')
        (dest/'project.ppf.json').write_text(json.dumps(project))

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.wf=FakeWF()
        (self.root/'assets').mkdir()
        self.a={"actNumber":1,"sequenceNumber":1,"blockNumber":1,"miniBlockNumber":1,"shotNumber":1}
        self.p=self.make_project()
        self.project_path=self.root/'project.ppf.json'
        self.write()
    def make_project(self):
        image=self.root/'assets'/'first.webp'
        Image.new('RGB',(32,20),color=(120,20,70)).save(image,'WEBP')
        record={'artifactId':'candidate-1','address':self.a,'passageIds':['screenplay-1'],'prompt':'A quiet opening shot','portablePath':'assets/first.webp','sha256':m.digest(image.read_bytes()),'packageBytesVerified':True,'savedMarkerPresent':False,'locked':False}
        artifact={'id':'candidate-1','workflow':'storyboard-frame-webp-v2','frameNumber':1,'assetUrl':'/api/local-ai/assets/first.webp','reviewState':'draft',
                  'sourceDecisionKeys':['story-workflow-image-import:v1','storyboard-anchor:block:block-01:mini-1','storyboard-target:block:block-01']}
        return {'id':'film-A','revision':2,'updatedAt':m.stamp(),'sourceEvidence':{'screenplay':{'passages':[{'id':'screenplay-1','text':'A quiet scene','type':'action'}]}},
                'build':{'foundations':{'visualArtifacts':[artifact],'acceptedVisualArtifactIds':[]}},
                'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[record],'plans':[{'address':{'blockNumber':1,'miniBlockNumber':1},'shots':[{'shotNumber':1,'state':'PLANNED'}]}]}}}}
    def write(self):self.project_path.write_text(json.dumps(self.p))
    def args(self,operation='auto',out='out',project_path=None):
        project_path=project_path or self.project_path
        ident=self.wf.identity(project_path)
        return SimpleNamespace(operation=operation,project=str(project_path),project_id=ident['id'],revision=ident['revision'],sha256=ident['sha256'],out=str(self.root/out),block=1,mini=1,shot=1,reason='Fix continuity')
    def test_default_saves_then_locks_with_readback(self):
        args=self.args();result=m.bulk(self.wf,args)
        self.assertEqual(result['locked'],1)
        self.assertTrue(result['readiness']['readyForMotionOrPrevis'])
        latest=self.wf.read_json(self.root/'out'/'project.ppf.json')
        self.assertEqual(latest['revision'],4)
        self.assertEqual(self.wf.read_json(self.project_path)['revision'],2)
        a,accept,maps=m.records(latest)
        self.assertIn(m.SAVE,a['candidate-1']['sourceDecisionKeys'])
        self.assertTrue(maps['1:1:1']['savedMarkerPresent'])
        self.assertTrue(maps['1:1:1']['locked'])
        self.assertEqual(accept,['candidate-1'])
        self.assertEqual([x['action'] for x in m.ledger(latest)['events']],['SAVE','DEFAULT_LOCK'])
    def test_explicit_replacement_can_default_relock_only_new_image(self):
        m.bulk(self.wf,self.args())
        m.change_one(self.wf,self.args('unlock','unlocked',self.root/'out'/'project.ppf.json'))
        p=self.wf.read_json(self.root/'unlocked'/'project.ppf.json')
        rr=p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]
        aa=p['build']['foundations']['visualArtifacts'][0]
        second=self.root/'unlocked'/'assets'/'second.webp'
        Image.new('RGB',(32,20),color=(12,203,41)).save(second,'WEBP')
        rr.update({'artifactId':'candidate-2','portablePath':'assets/second.webp','sha256':m.digest(second.read_bytes()),'savedMarkerPresent':False,'locked':False})
        aa.update({'id':'candidate-2','assetUrl':'/api/local-ai/assets/second.webp','reviewState':'draft'})
        aa['sourceDecisionKeys']=[x for x in aa['sourceDecisionKeys'] if x!=m.SAVE]
        p['revision']+=1
        stage=self.root/'unlocked'/'replaced.ppf.json';stage.write_text(json.dumps(p))
        rargs=self.args('auto','replacement-ready',stage)
        self.assertEqual(m.bulk(self.wf,rargs)['locked'],0)
        done=m.bulk(self.wf,rargs,replace_unlocked=True)
        self.assertEqual(done['locked'],1)
        self.assertTrue(done['readiness']['readyForMotionOrPrevis'])
        final=self.wf.read_json(self.root/'replacement-ready'/'project.ppf.json')
        self.assertEqual(m.ledger(final)['exceptions'],{})
        self.assertIn('REPLACEMENT_DEFAULT_LOCK',[e['action'] for e in m.ledger(final)['events']])

    def test_replacement_bypass_never_relocks_old_candidate(self):
        m.ledger(self.p)['exceptions']['1:1:1']={'artifactId':'candidate-1','reason':'user unlocked'}
        self.write()
        r=m.bulk(self.wf,self.args(),replace_unlocked=True)
        self.assertEqual(r['locked'],0)

    def test_no_eligible_image_does_not_create_output(self):
        first=self.args();m.bulk(self.wf,first)
        after=self.args(project_path=self.root/'out'/'project.ppf.json',out='second')
        r=m.bulk(self.wf,after)
        self.assertEqual(r['locked'],0)
        self.assertFalse((self.root/'second').exists())
    def test_unlock_only_selected_then_relock(self):
        m.bulk(self.wf,self.args())
        unlocked=m.change_one(self.wf,self.args('unlock','unlocked',self.root/'out'/'project.ppf.json'))
        self.assertFalse(unlocked['readiness']['readyForMotionOrPrevis'])
        after=self.wf.read_json(self.root/'unlocked'/'project.ppf.json')
        self.assertEqual(m.records(after)[2]['1:1:1']['savedMarkerPresent'],True)
        self.assertNotIn('candidate-1',m.records(after)[1])
        self.assertEqual(m.eligible(after,self.root/'unlocked',1,1,1)[0],[])
        locked=m.change_one(self.wf,self.args('relock','relocked',self.root/'unlocked'/'project.ppf.json'))
        self.assertTrue(locked['readiness']['readyForMotionOrPrevis'])
    def test_locked_missing_media_audit_fails(self):
        m.bulk(self.wf,self.args())
        (self.root/'out'/'assets'/'first.webp').unlink()
        latest=self.wf.read_json(self.root/'out'/'project.ppf.json')
        self.assertFalse(m.audit(latest,self.root/'out',1,1)['readyForMotionOrPrevis'])
    def test_unlock_missing_media_still_possible(self):
        m.bulk(self.wf,self.args())
        (self.root/'out'/'assets'/'first.webp').unlink()
        res=m.change_one(self.wf,self.args('unlock','bad',self.root/'out'/'project.ppf.json'))
        self.assertFalse(res['readiness']['readyForMotionOrPrevis'])
    def test_missing_image_rejected_and_no_fake_lock(self):
        (self.root/'assets'/'first.webp').unlink()
        r=m.bulk(self.wf,self.args())
        self.assertEqual(r['locked'],0)
        self.assertFalse(r['readiness']['readyForMotionOrPrevis'])
    def test_sha_tamper_rejected(self):
        self.p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]['sha256']='a'*64;self.write()
        r=m.bulk(self.wf,self.args())
        self.assertEqual(r['locked'],0)
        self.assertEqual(len(r['skipped']),1)
    def test_not_planned_or_draft_does_not_autolock(self):
        self.p['assetRegistry']['extensions']['storyWorkflow']['plans'][0]['shots'][0]['state']='GAP';self.write()
        self.assertEqual(m.bulk(self.wf,self.args())['locked'],0)
    def test_rejects_malformed_canonical_address(self):
        self.p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]['address']['sequenceNumber']=3;self.write()
        with self.assertRaisesRegex(ValueError,'inconsistent'):m.bulk(self.wf,self.args())
    def test_save_precedes_lock(self):
        with self.assertRaisesRegex(ValueError,'Save must precede Lock'):m.lock_saved_source(copy.deepcopy(self.p),[('1:1:1','candidate-1')])
    def test_source_pinned(self):
        args=self.args()
        self.p['revision']=3;self.write()
        with self.assertRaisesRegex(ValueError,'STALE'):m.bulk(self.wf,args)
    def test_does_not_auto_relock_exception(self):
        m.ledger(self.p)['exceptions']['1:1:1']={'reason':'user requested'}
        self.write()
        self.assertEqual(m.bulk(self.wf,self.args())['locked'],0)
    def test_rejects_duplicate_current_mappings(self):
        r=copy.deepcopy(self.p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]);self.p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'].append(r);self.write()
        with self.assertRaisesRegex(ValueError,'duplicate'):m.bulk(self.wf,self.args())
    def test_cannot_relock_unsaved(self):
        with self.assertRaisesRegex(ValueError,'unsaved'):m.change_one(self.wf,self.args('relock'))

if __name__=='__main__':unittest.main(verbosity=2)
