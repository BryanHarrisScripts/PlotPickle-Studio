import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
bridge_path=ROOT/'scripts'/'curriculum-bridge.py'
spec=importlib.util.spec_from_file_location('pp_bridge',bridge_path)
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
class EmbeddedCurriculumAcceptance(unittest.TestCase):
    def setUp(self):
        self.index=bridge.load_manifest()
        self.base=ROOT/'data'/'learn'
    def test_all_81_lessons_and_95_sources_have_real_content(self):
        rec=bridge.verified_library(self.index,self.base)
        self.assertEqual(len(rec),12)
        self.assertEqual(sum(len(b['lessons']) for _,b in rec),81)
        self.assertEqual(sum(len(l['sources']) for _,b in rec for l in b['lessons']),95)
    def test_all_twelve_files_match_recorded_sha256(self):
        manifest=json.loads((ROOT/'data'/'curriculum-package-manifest.json').read_text())
        for topic,item in manifest['sourceFiles'].items():
            blob=(self.base/item['file']).read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(),item['sha256'],topic)
            self.assertEqual(bridge.git_blob_id(blob),item['gitBlobSha1'],topic)
    def test_retrieve_real_lessons_and_sections(self):
        rec=bridge.verified_library(self.index,self.base)
        lookup={(topic['id'],l['id']):l for topic,b in rec for l in b['lessons']}
        for key,head in [(('structure','24b-dynamic-scenes'),'The dynamic scene chain'),
                         (('character','characters-choice-proof'),'Build the evidence chain'),
                         (('dialogue','dialogue-subtext'),'The pressure system')]:
            lesson=lookup[key]
            self.assertTrue(any(s['heading']==head and len(' '.join(s.get('paragraphs',[])))>50 for s in lesson['sections']))
    def test_search_returns_canonical_lesson(self):
        rec=bridge.verified_library(self.index,self.base)
        hits=bridge.ranked_lessons(rec,'character pressure choice agency',10)
        self.assertIn(('character','characters-choice-proof'), {(r['topic'],r['lessonId']) for r in hits})
    def test_partial_library_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            shutil.copy2(self.base/'character.json',d/'character.json')
            with self.assertRaisesRegex(ValueError,'Missing'):
                bridge.verified_library(self.index,d)
    def test_mutated_file_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            for f in self.base.glob('*.json'):shutil.copy2(f,d/f.name)
            with (d/'character.json').open('ab') as f:f.write(b' ')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                bridge.verified_library(self.index,d)
if __name__=='__main__':unittest.main()
