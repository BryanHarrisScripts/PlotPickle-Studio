"""Public synthetic fixture must never substitute for The Third Bell or claim real video."""
import json
from pathlib import Path
import unittest

import editor_core as editor

FIXTURE = Path(__file__).with_name("fixtures") / "editor-seed.synthetic.json"

class TestSyntheticEditorFixture(unittest.TestCase):
    def test_import_is_source_linked_but_unverified(self):
        seed = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(seed["schema"], "plotpickle.editor-seed.v1")
        self.assertEqual(seed["source"]["projectId"], "synthetic-local-test-only")
        self.assertEqual(seed["media"], [])
        self.assertNotIn("The Third Bell", str(seed))
        self.assertNotIn("v3b.fal.media/files/", str(seed))
        self.assertNotIn("requestId", str(seed))
        draft = editor.initial(seed)
        self.assertEqual(draft["source"]["nativePpfModified"], False)
        self.assertEqual(draft["media"], {})
        self.assertEqual(draft["tracks"]["video"][0]["mediaId"], None)
        self.assertEqual(draft["tracks"]["ambience"][0]["durationFrames"], 72)
        self.assertEqual(draft["tracks"]["foley"][0]["startFrame"], 24)
        self.assertEqual(draft["revision"], 0)
        self.assertFalse(draft["draftApproved"])

    def test_edit_and_undo_source_immutability(self):
        seed = json.loads(FIXTURE.read_text(encoding="utf-8"))
        original = editor.initial(seed)
        changed = editor.apply_edit(original, {
            "expectedRevision": 0,
            "track": "ambience",
            "operation": "change",
            "id": "demo-ambience-cue-01",
            "startFrame": 3,
        })
        self.assertEqual(original["revision"], 0)
        self.assertEqual(changed["revision"], 1)
        self.assertEqual(changed["tracks"]["ambience"][0]["startFrame"], 3)
        self.assertFalse(changed["source"]["nativePpfModified"])

if __name__ == "__main__":
    unittest.main()
