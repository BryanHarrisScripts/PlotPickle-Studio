#!/usr/bin/env python3
import copy,hashlib,importlib.util,json,pathlib,tempfile,unittest
spec=importlib.util.spec_from_file_location('story_flow',pathlib.Path(__file__).with_name('story-flow.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def ppf():
    passage={'id':'scene-1','type':'scene-heading','text':'EXT. SHORE - DAWN'}
    return {'id':'story-1','title':'Test Story','revision':2,'sourceEvidence':{'screenplay':{'sourceFileName':'draft.fdx','passages':[passage]}},'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[]}}},'build':{'foundations':{'acceptedVisualArtifactIds':[]}}}
def add_mapping(p,raw,name='assets/frame.webp',save=False,lock=False,accept=False):
    data={'artifactId':'asset-1','address':{'actNumber':1,'sequenceNumber':1,'blockNumber':1,'miniBlockNumber':1,'shotNumber':1},'passageIds':['scene-1'],'portablePath':name,'sha256':hashlib.sha256(raw).hexdigest(),'savedMarkerPresent':save,'locked':lock}
    p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'].append(data)
    if accept:p['build']['foundations']['acceptedVisualArtifactIds'].append('asset-1')
    return data
def audit(p,root=None,block=1,mini=1):return m.inspect(p,json.dumps(p).encode(),root,block,mini)
class TestFlow(unittest.TestCase):
    def test_script_missing(self):
        p=ppf();p['sourceEvidence']['screenplay']['passages']=[];self.assertEqual(audit(p)['nextStage'],'Script')
    def test_no_mappings(self):self.assertEqual(audit(ppf())['nextStage'],'Storyboard')
    def test_ungrounded_source(self):
        p=ppf();v=add_mapping(p,b'frame');v['passageIds']=['missing'];self.assertEqual(audit(p)['nextStage'],'Storyboard')
    def test_invalid_address(self):
        p=ppf();v=add_mapping(p,b'frame');v['address']['sequenceNumber']=12;self.assertEqual(audit(p)['nextStage'],'Storyboard')
    def test_duplicate_address(self):
        p=ppf();v=add_mapping(p,b'frame');p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'].append(copy.deepcopy(v));self.assertGreater(audit(p)['stages'][1]['evidence']['mappingErrors'],0)
    def test_no_root_never_verified(self):
        p=ppf();add_mapping(p,b'frame',save=True,lock=True,accept=True);r=audit(p);self.assertEqual(r['nextStage'],'Visuals');self.assertEqual(r['stages'][2]['evidence']['mediaHashVerified'],0)
    def test_real_bytes_require_save_lock_and_accept(self):
        p=ppf();raw=b'FRAME';add_mapping(p,raw)
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);(root/'assets').mkdir();(root/'assets/frame.webp').write_bytes(raw)
            self.assertEqual(audit(p,root)['stages'][2]['evidence']['mediaHashVerified'],1)
            self.assertEqual(audit(p,root)['nextStage'],'Visuals')
            item=p['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0]
            item['savedMarkerPresent']=True;item['locked']=True;self.assertEqual(audit(p,root)['nextStage'],'Visuals')
            p['build']['foundations']['acceptedVisualArtifactIds'].append('asset-1');self.assertEqual(audit(p,root)['nextStage'],'Produce')
    def test_hash_mismatch_blocks(self):
        p=ppf();add_mapping(p,b'original',save=True,lock=True,accept=True)
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);(root/'assets').mkdir();(root/'assets/frame.webp').write_bytes(b'changed')
            self.assertEqual(audit(p,root)['shots'][0]['media'],'sha256-mismatch');self.assertEqual(audit(p,root)['nextStage'],'Visuals')
    def test_traversal_rejected(self):
        p=ppf();add_mapping(p,b'frame',name='../private/frame.webp')
        with tempfile.TemporaryDirectory() as td:self.assertEqual(audit(p,pathlib.Path(td))['shots'][0]['media'],'unsafe-or-missing-path')
    def test_scope_isolation(self):
        p=ppf();add_mapping(p,b'frame');self.assertEqual(audit(p,block=2,mini=1)['stages'][1]['evidence']['mappedShotCount'],0)
        with self.assertRaises(ValueError):m.inspect(p,json.dumps(p).encode(),None,block=1)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            td=pathlib.Path(td);(td/'story.ppf.json').write_text(json.dumps(ppf()));out=td/'report.json';out.write_text('ORIGINAL')
            with self.assertRaises(FileExistsError):m.main(['--project',str(td/'story.ppf.json'),'--out',str(out)])
            self.assertEqual(out.read_text(),'ORIGINAL')
    def test_no_implicit_authorization(self):
        p=ppf();add_mapping(p,b'frame');r=audit(p)
        self.assertFalse(r['safety']['ppfModified']);self.assertFalse(r['safety']['providerInvoked']);self.assertFalse(r['safety']['creditsSpent'])
        self.assertEqual(r['stages'][3]['evidence']['motionProvider'],'fal')
        self.assertFalse(r['stages'][3]['evidence']['jobSubmitted'])
if __name__=='__main__':unittest.main()
