#!/usr/bin/env python3
"""Portable media reopen verification: synthetic source and ZIP only."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

path = Path(__file__).with_name("verify-portable-package.py")
spec = importlib.util.spec_from_file_location("ppf_portable_media", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FRAME = b"RIFF" + (4).to_bytes(4, "little") + b"WEBP" + b"VP8 " + b"fake-webp-payload"
PATH = "assets/shot-01.webp"


def source(frame=FRAME, media_type="image/webp"):
    return {
        "id": "synthetic-project",
        "revision": 4,
        "assetRegistry": {
            "assets": [{
                "id": "synthetic-asset",
                "variations": [{
                    "id": "synthetic-variation",
                    "portablePath": PATH,
                    "contentHash": "sha256:" + hashlib.sha256(frame).hexdigest(),
                    "bytes": len(frame),
                    "mediaType": media_type
                }]
            }]
        }
    }


def archive(path, records=None):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as f:
        for name, data in records if records is not None else [(PATH, FRAME)]:
            f.writestr(name, data)


class TestPortableMediaReopen(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.zip = Path(self.workspace.name) / "media.zip"
        archive(self.zip)
        self.ppf = source()

    def run_check(self, ppf=None, **kw):
        payload = json.dumps(self.ppf if ppf is None else ppf).encode()
        return m.inspect(payload, self.zip, **kw)

    def test_verified_only_not_plugin_or_save_lock(self):
        r = self.run_check()
        self.assertEqual(r["status"], "PORTABLE_MEDIA_VERIFIED_ONLY")
        self.assertEqual(r["media"]["mediaHashVerified"], 1)
        self.assertEqual(r["media"]["mediaVerifiedBytes"], len(FRAME))
        self.assertFalse(r["safety"]["canonicalReaderAccepted"])
        self.assertFalse(r["safety"]["pluginHostReopenedProject"])
        self.assertFalse(r["safety"]["savedLockedAndAcceptedVerified"])

    def test_missing_archive_asset_fails_closed(self):
        archive(self.zip, [("assets/not-the-shot.webp", FRAME)])
        r = self.run_check()
        self.assertEqual(r["status"], "MEDIA_INCOMPLETE_OR_UNVERIFIABLE")
        self.assertEqual(r["media"]["missingMedia"], 1)

    def test_tampered_asset_hash_fails_closed(self):
        archive(self.zip, [(PATH, FRAME[:-1] + b"?")])
        r = self.run_check()
        self.assertEqual(r["media"]["hashMismatch"], 1)

    def test_incorrect_declared_size_fails_closed(self):
        self.ppf["assetRegistry"]["assets"][0]["variations"][0]["bytes"] += 1
        self.assertEqual(self.run_check()["media"]["bytesMismatch"], 1)

    def test_invalid_webp_header_fails_closed(self):
        altered = b"not-a-webp" + b"x" * (len(FRAME) - len("not-a-webp"))
        archive(self.zip, [(PATH, altered)])
        self.ppf = source(altered)
        self.assertEqual(self.run_check()["media"]["invalidWebpSignature"], 1)

    def test_stale_revision_fails_closed(self):
        with self.assertRaisesRegex(m.ReopenBlocked, "PROJECT_REVISION_CHANGED"):
            self.run_check(expected_revision=3)

    def test_changed_sha_fails_closed(self):
        with self.assertRaisesRegex(m.ReopenBlocked, "PROJECT_SHA256_CHANGED"):
            self.run_check(expected_sha256="0" * 64)

    def test_wrong_project_id_fails_closed(self):
        with self.assertRaisesRegex(m.ReopenBlocked, "PROJECT_ID_CHANGED"):
            self.run_check(expected_id="another-project")

    def test_zip_traversal_rejected_without_extraction(self):
        archive(self.zip, [("../outside.webp", FRAME)])
        with self.assertRaisesRegex(m.ReopenBlocked, "UNSAFE_ZIP_PATH"):
            self.run_check()

    def test_duplicate_zip_member_rejected(self):
        archive(self.zip, [(PATH, FRAME), (PATH, FRAME)])
        with self.assertRaisesRegex(m.ReopenBlocked, "DUPLICATE_ZIP_MEMBER"):
            self.run_check()

    def test_duplicate_variation_path_not_double_counted(self):
        first = self.ppf["assetRegistry"]["assets"][0]["variations"][0]
        self.ppf["assetRegistry"]["assets"][0]["variations"].append(copy.deepcopy(first))
        result = self.run_check()
        self.assertEqual(result["media"]["duplicateReferences"], 1)
        self.assertEqual(result["media"]["mediaHashVerified"], 1)
        self.assertEqual(result["status"], "MEDIA_INCOMPLETE_OR_UNVERIFIABLE")

    def test_no_registry_fails_closed(self):
        self.ppf.pop("assetRegistry")
        with self.assertRaisesRegex(m.ReopenBlocked, "MISSING_ASSET_REGISTRY"):
            self.run_check()

    def test_file_count_requires_actual_media(self):
        self.ppf["assetRegistry"]["assets"] = []
        r = self.run_check()
        self.assertEqual(r["status"], "MEDIA_INCOMPLETE_OR_UNVERIFIABLE")
        self.assertEqual(r["media"]["recordedVariations"], 0)

    def test_read_only_no_output_mutation(self):
        original = json.dumps(self.ppf).encode()
        ppf_file = Path(self.workspace.name) / "story.ppf.json"
        ppf_file.write_bytes(original)
        report_file = Path(self.workspace.name) / "receipt.json"
        result = m.main(["--project", str(ppf_file), "--assets-zip", str(self.zip),
                         "--expected-revision", "4", "--out", str(report_file)])
        self.assertEqual(result, 0)
        self.assertEqual(ppf_file.read_bytes(), original)
        self.assertTrue(json.loads(report_file.read_text())["safety"]["originalPPFModified"] is False)
        with self.assertRaises(FileExistsError):
            report_file.open("x")

    def test_actual_cli_disallows_overwrite_of_prior_receipt(self):
        report_file = Path(self.workspace.name) / "receipt.json"
        report_file.write_text("ORIGINAL", encoding="utf-8")
        ppf_file = Path(self.workspace.name) / "story.ppf.json"
        ppf_file.write_text(json.dumps(self.ppf), encoding="utf-8")
        self.assertEqual(m.main(["--project", str(ppf_file), "--assets-zip", str(self.zip),
                                 "--out", str(report_file)]), 1)
        self.assertEqual(report_file.read_text(), "ORIGINAL")


if __name__ == "__main__":
    unittest.main()
