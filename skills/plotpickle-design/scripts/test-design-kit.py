import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

path=Path(__file__).with_name('design-kit.py')
spec=importlib.util.spec_from_file_location('design_kit',path)
kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
PROJECT={
  'id':'test-plotpickle','title':'Test story','revision':4,
  'sourceEvidence':{'screenplay':{'passages':[
    {'id':'p1','type':'scene-heading','text':'EXT. GARDEN - DAY'},
    {'id':'p2','type':'action','text':'MARA runs to the locked gate.'},
    {'id':'p3','type':'character','text':'Mara'},
    {'id':'p4','type':'dialogue','text':'Let me through.'},
    {'id':'p5','type':'scene-heading','text':'INT. CABIN - NIGHT'},
    {'id':'p6','type':'character','text':'MARA (CONT\'D)'},
    {'id':'p7','type':'dialogue','text':'I remember.'},
  ]}}
}
BYTES=json.dumps(PROJECT).encode();IDENT={'id':PROJECT['id'],'revision':4,'sha256':hashlib.sha256(BYTES).hexdigest()}

class DesignKitTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory();self.path=Path(self.td.name)/'story.ppf.json';self.path.write_bytes(BYTES)
        self.project,self.ident,self.passages=kit.read_project(self.path,IDENT)
    def tearDown(self):self.td.cleanup()
    def test_catalogue_deduplicates_cue_variants(self):
        c=kit.catalogue(self.project,self.ident,self.passages)
        self.assertEqual(len(c['characters']),1)
        self.assertEqual(c['characters'][0]['cueCount'],2)
        self.assertEqual(len(c['worlds']),2)
        self.assertFalse(c['projectModified'])
    def test_character_evidence_and_9_panels(self):
        d=kit.character_design(self.project,self.ident,self.passages,'mara')
        l=kit.layout(d)
        self.assertEqual([p['id'] for p in l['panels']][:3],['front','three-quarter-left','profile'])
        self.assertEqual(len(l['panels']),9)
        self.assertEqual(l['cellAspectRatio'],'1:1')
        self.assertTrue(all(p['image'] is None and not p['imageVerified'] for p in l['panels']))
        self.assertIn('p2',[e['passageId'] for e in d['sourceEvidence']])
        self.assertIn('p4',[e['passageId'] for e in d['sourceEvidence']])
    def test_world_contains_only_that_scene(self):
        d=kit.world_design(self.project,self.ident,self.passages,'EXT. GARDEN - DAY')
        self.assertEqual([e['passageId'] for e in d['sourceEvidence']],['p1','p2','p4'])
        l=kit.layout(d)
        self.assertEqual(len(l['panels']),6)
        self.assertEqual(l['cellAspectRatio'],'16:9')
    def test_missing_subject_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Subject not found'):
            kit.character_design(self.project,self.ident,self.passages,'invented')
    def test_stale_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'identity/revision/SHA'):
            kit.read_project(self.path,{**IDENT,'revision':5})
    def test_source_mutation_changes_sha(self):
        original=self.path.read_bytes()
        changed=json.loads(original);changed['sourceEvidence']['screenplay']['passages'][1]['text']='Other event'
        self.path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError,'identity'):
            kit.read_project(self.path,IDENT)
    def test_sheet_is_placeholder_not_fake_media(self):
        d=kit.character_design(self.project,self.ident,self.passages,'Mara')
        s=kit.render_html(kit.layout(d))
        self.assertEqual(s.count('IMAGE PENDING'),9)
        self.assertIn('No artwork generated or approved',s)
    def test_no_overwrite(self):
        out=Path(self.td.name)/'sheet.json';kit.output(out,{'a':1})
        with self.assertRaisesRegex(ValueError,'refusing to overwrite'):
            kit.output(out,{'a':2})
    def test_reject_bad_layout_and_generated(self):
        d=kit.character_design(self.project,self.ident,self.passages,'mara')
        d['mediaGenerated']=True
        with self.assertRaisesRegex(ValueError,'ungenerated'):
            kit.layout(d)

if __name__=='__main__':unittest.main()
