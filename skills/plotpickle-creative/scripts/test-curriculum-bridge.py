import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("curriculum_bridge", HERE / "curriculum-bridge.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CurriculumBridgeTests(unittest.TestCase):
    def test_catalog_counts_and_topics(self):
        manifest = mod.load_manifest()
        self.assertEqual(81, manifest["lessonCount"])
        self.assertEqual(95, manifest["sourceCount"])
        self.assertEqual(12, len(manifest["topics"]))
        self.assertEqual(1, sum(x["completion"] == "complete" for x in manifest["topics"]))


    def test_complete_synthetic_global_numbered_archive(self):
        """An exact 12-topic archive with non-contiguous per-topic lesson numbers is valid."""
        manifest = json.loads(json.dumps(mod.load_manifest()))
        next_number = 1
        with tempfile.TemporaryDirectory() as folder:
            for topic in manifest['topics']:
                lessons = []
                for local_idx in range(topic['lessons']):
                    n=next_number
                    next_number += 1
                    src_count=(topic['sources'] if local_idx == 0 else 0)
                    sources=[{'id':f"{topic['id']}-source-{j}", 'content':f"Original source {j}"} for j in range(src_count)]
                    lessons.append({'id':f"{topic['id']}-lesson-{n}", 'title':f"Synthetic lesson {n}",
                                    'topic':topic['id'], 'number':n, 'sources':sources})
                data={'schemaVersion':'2.0','topic':{'id':topic['id']},
                      'lessonCount':len(lessons),'sourceCount':topic['sources'],'lessons':lessons}
                raw=(json.dumps(data,ensure_ascii=False)+'\n').encode('utf-8')
                Path(folder,topic['file']).write_bytes(raw)
                topic['gitBlobSha1']=mod.git_blob_id(raw)
            verified=mod.verified_library(manifest,folder)
            self.assertEqual(12,len(verified))
            self.assertEqual(81,next_number-1)
            # Even if a file is syntactically valid, byte changes must invalidate the identity.
            first=Path(folder,manifest['topics'][0]['file'])
            first.write_bytes(first.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                mod.verified_library(manifest,folder)

    def test_full_offline_catalog_is_navigation_only(self):
        manifest=mod.load_manifest()
        catalogue=mod.embedded_catalog(manifest)
        self.assertFalse(catalogue['lessonTextEmbedded'])
        self.assertEqual(81,len(catalogue['lessons']))
        self.assertEqual(list(range(1,82)), sorted(l['number'] for l in catalogue['lessons']))

    def test_git_blob_known_vector(self):
        self.assertEqual("e69de29bb2d1d6434b8b29ae775ad8c2e48c5391", mod.git_blob_id(b""))

    def test_missing_archive_cannot_fake_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "Missing or unsupported source file"):
                mod.verified_library(mod.load_manifest(), folder)

    def test_changed_archive_fails_closed(self):
        manifest = mod.load_manifest()
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, manifest["topics"][0]["file"]).write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                mod.verified_library(manifest, folder)

    def test_match_reports_real_ids_not_claims(self):
        records = [({"id": "character", "file": "character.json", "gitBlobSha1": "abc", "completion": "source-imported"}, {
            "lessons": [{"id": "character-motivation", "number": 1, "title": "Character Motivation",
                         "overview": "Identify the desire and stakes", "objectives": ["Conflict emerges from desire"],
                         "sections": [{"heading": "Stakes", "paragraphs": ["Pressure turns desire into choices"]}]}]
        })]
        hits = mod.ranked_lessons(records, "character desire", 5)
        self.assertEqual("character-motivation", hits[0]["lessonId"])
        self.assertEqual("abc", hits[0]["verifiedGitBlobSha1"])


if __name__ == "__main__":
    unittest.main()
