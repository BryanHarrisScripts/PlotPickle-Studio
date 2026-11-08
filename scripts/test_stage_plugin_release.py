#!/usr/bin/env python3
"""Synthetic tests only: no private PPF, creator seed, media URL or provider call."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from stage_plugin_release import OLD_BRANDING, PRIVATE_SEED, READER, ReleaseBlocked, digest, read_archive, stage

PNG = b"\x89PNG\r\n\x1a\nsynthetic-asset"
READER_BYTES = b"synthetic-reader-only-for-automated-tests"


def manifest(version):
    return json.dumps({"name": "plotpickle-story-reader", "version": version,
                       "repository": "https://github.com/BryanHarrisScripts/PlotPickle-Studio"}).encode()


def make_tar(path, contents):
    with gzip.open(path, "wb") as out:
        with tarfile.open(fileobj=out, mode="w") as tf:
            for name, content in contents.items():
                member = tarfile.TarInfo(name)
                member.size = len(content)
                tf.addfile(member, io.BytesIO(content))


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.backup = self.root / "backup.tar.gz"
        self.output = self.root / "candidate.tar.gz"
        self.original = {
            "plugin.json": manifest("0.8.33"),
            ".codex-plugin/plugin.json": manifest("0.8.33"),
            "LICENSE": b"synthetic",
            READER: READER_BYTES,
            PRIVATE_SEED: b"private synthetic, not an actual creator seed",
            "assets/composer-icon.png": b"old icon",
            "assets/plotpickle-logo.png": b"old logo",
            "skills/plotpickle-welcome/SKILL.md": b"welcome",
        }
        make_tar(self.backup, self.original)
        files = {
            "plugin.json": manifest("0.8.34"),
            ".codex-plugin/plugin.json": manifest("0.8.34"),
            "LICENSE": b"synthetic",
            READER: READER_BYTES,
            "assets/studio-composer-icon.png": PNG,
            "assets/studio-logo.png": PNG,
            "skills/plotpickle-welcome/SKILL.md": b"welcome",
        }
        for name, value in files.items():
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(value)

    def build(self, **kwargs):
        return stage(self.backup, self.source, self.output,
                     expected_backup_sha=kwargs.get("expected_backup_sha", digest(self.backup.read_bytes())),
                     reader_sha=hashlib.sha256(READER_BYTES).hexdigest(),
                     reader_size=len(READER_BYTES))

    def test_stages_source_and_preserves_private_seed_without_old_branding(self):
        report = self.build()
        files = read_archive(self.output)
        self.assertEqual(report["status"], "STAGED_NOT_PUBLISHED")
        self.assertEqual(files[PRIVATE_SEED], self.original[PRIVATE_SEED])
        self.assertFalse(set(files) & OLD_BRANDING)
        self.assertFalse(report["host_authentication_verified"])
        self.assertEqual(set(report["required_plugin_creator_delete_paths"]), OLD_BRANDING)

    def test_output_deterministic(self):
        self.build()
        expected = digest(self.output.read_bytes())
        self.output.unlink()
        self.build()
        self.assertEqual(digest(self.output.read_bytes()), expected)

    def test_rejects_changed_archive_checksum(self):
        with self.assertRaisesRegex(ReleaseBlocked, "backup SHA-256"):
            self.build(expected_backup_sha="0" * 64)

    def test_rejects_missing_creator_seed(self):
        del self.original[PRIVATE_SEED]
        make_tar(self.backup, self.original)
        with self.assertRaisesRegex(ReleaseBlocked, "private The Third Bell"):
            self.build()

    def test_rejects_unreviewed_private_material(self):
        self.original["skills/creator/new-private-file.json"] = b"secret"
        make_tar(self.backup, self.original)
        with self.assertRaisesRegex(ReleaseBlocked, "unreviewed private"):
            self.build()

    def test_rejects_mismatched_reader(self):
        (self.source / READER).write_bytes(b"different")
        with self.assertRaisesRegex(ReleaseBlocked, "canonical reader"):
            self.build()

    def test_rejects_old_brand_in_source(self):
        (self.source / "assets/composer-icon.png").write_bytes(b"old")
        with self.assertRaisesRegex(ReleaseBlocked, "legacy branding"):
            self.build()

    def test_rejects_duplicate_tar_member(self):
        with gzip.open(self.backup, "wb") as out:
            with tarfile.open(fileobj=out, mode="w") as tf:
                for _ in range(2):
                    b = b"hi"
                    ti = tarfile.TarInfo("duplicate.txt")
                    ti.size = len(b)
                    tf.addfile(ti, io.BytesIO(b))
        with self.assertRaisesRegex(ReleaseBlocked, "duplicate"):
            read_archive(self.backup)

    def test_rejects_path_traversal(self):
        make_tar(self.backup, {"../private-secret": b"hi"})
        with self.assertRaisesRegex(ReleaseBlocked, "unsafe archive path"):
            read_archive(self.backup)

    def test_never_overwrites_backup(self):
        with self.assertRaisesRegex(ReleaseBlocked, "not overwrite"):
            stage(self.backup, self.source, self.backup, expected_backup_sha="not used")


if __name__ == "__main__":
    unittest.main()
