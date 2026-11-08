#!/usr/bin/env python3
"""Privately stage and audit a PlotPickle Studio release; never publish a plugin.

Inputs: exact pre-update Plugin Creator archive and checked-out PlotPickle-Studio
source. Private material is allowed only from the backup archive and is never
written to GitHub. Safe to run locally/offline. No provider calls or writes to PPF.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import subprocess
from pathlib import Path, PurePosixPath
import tarfile
import zipfile

PINNED_BACKUP_SHA256 = "5838a10ec530959635c787d6dd0391c7aabcf740e0e6870950cff103dc4c7dc3"
PINNED_READER_SHA256 = "6c9c239f4484d2cd624bfd1c761fa8645203cc8e78be1d58b11ec2500a5f498f"
PINNED_READER_SIZE = 1_364_997
PLUGIN_NAME = "plotpickle-story-reader"
VERSION = "0.8.34"
READER = "skills/read-plotpickle-project/scripts/inspect-project.mjs"
PRIVATE_SEED = "skills/plotpickle-editor/windows/the-third-bell-seed.json"
OLD_BRANDING = frozenset({"assets/composer-icon.png", "assets/plotpickle-logo.png"})
BRANDING = ("assets/studio-composer-icon.png", "assets/studio-logo.png")
MANIFESTS = ("plugin.json", ".codex-plugin/plugin.json")
LIMIT_PER_FILE = 16 * 1024 * 1024
LIMIT_TOTAL = 150 * 1024 * 1024

class ReleaseBlocked(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_path(value: str) -> str:
    if not isinstance(value, str) or "\\" in value or "\x00" in value:
        raise ReleaseBlocked("unsafe archive path")
    p = PurePosixPath(value)
    if not value or value.startswith("/") or any(c in ("", ".", "..") for c in value.split("/")) or p.is_absolute():
        raise ReleaseBlocked("unsafe archive path")
    return value


def read_archive(path: Path) -> dict[str, bytes]:
    if not path.is_file():
        raise ReleaseBlocked(f"archive absent: {path.name}")
    result: dict[str, bytes] = {}
    size = 0

    def add(name: str, data: bytes) -> None:
        nonlocal size
        name = check_path(name)
        if name in result:
            raise ReleaseBlocked(f"duplicate archive member: {name}")
        size += len(data)
        if len(data) > LIMIT_PER_FILE or size > LIMIT_TOTAL:
            raise ReleaseBlocked("archive exceeds safe size budget")
        result[name] = data

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                # UNIX mode symlinks or special types must not enter a plugin ZIP.
                mode = (member.external_attr >> 16) & 0o170000
                if mode not in (0, 0o100000):
                    raise ReleaseBlocked("archive contains a link or special file")
                if member.file_size > LIMIT_PER_FILE:
                    raise ReleaseBlocked("archive member too large")
                add(member.filename, archive.read(member))
    else:
        try:
            with tarfile.open(path, mode="r:gz") as archive:
                for member in archive.getmembers():
                    if member.isdir():
                        continue
                    if not member.isfile():
                        raise ReleaseBlocked("archive contains a link or special file")
                    if member.size > LIMIT_PER_FILE:
                        raise ReleaseBlocked("archive member too large")
                    handle = archive.extractfile(member)
                    if handle is None:
                        raise ReleaseBlocked("unreadable archive member")
                    add(member.name, handle.read())
        except tarfile.TarError as exc:
            raise ReleaseBlocked("not a valid gzip tar or ZIP archive") from exc
    return result


def source_files(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        raise ReleaseBlocked("checked-out Studio source directory absent")
    result: dict[str, bytes] = {}
    for base in ("skills", "assets"):
        folder = root / base
        if not folder.is_dir():
            raise ReleaseBlocked(f"source missing {base}/")
        for entry in folder.rglob("*"):
            if entry.is_symlink():
                raise ReleaseBlocked("source contains symbolic link")
            if not entry.is_file():
                continue
            name = entry.relative_to(root).as_posix()
            if "__pycache__" in entry.parts or entry.suffix == ".pyc":
                continue
            if name == PRIVATE_SEED or name in OLD_BRANDING:
                raise ReleaseBlocked("private creator data or legacy branding in public source")
            result[check_path(name)] = entry.read_bytes()
    for name in (*MANIFESTS, "LICENSE"):
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ReleaseBlocked(f"source missing {name}")
        result[name] = path.read_bytes()
    return result


def verify_clean_checkout(root: Path, packaged_paths: set[str]) -> None:
    """The public input must be clean and exactly versioned in Git."""
    if not (root / ".git").exists():
        raise ReleaseBlocked("release source must be a checked-out Git repository")
    opts = {"capture_output": True, "check": False}
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all",
         "--", "skills", "assets", "plugin.json", ".codex-plugin/plugin.json", "LICENSE"],
        **opts,
    )
    if status.returncode or status.stdout.strip():
        raise ReleaseBlocked("release source contains modified or untracked plugin files")
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--",
         "skills", "assets", "plugin.json", ".codex-plugin/plugin.json", "LICENSE"],
        **opts,
    )
    if tracked.returncode:
        raise ReleaseBlocked("could not audit tracked public plugin inputs")
    actual = {p.decode("utf-8") for p in tracked.stdout.split(b"\x00") if p}
    if packaged_paths.difference(actual):
        raise ReleaseBlocked("release input contains files not tracked in Git")


def parse_manifest(blob: bytes, label: str, version: str) -> dict:
    try:
        doc = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseBlocked(f"{label}: invalid UTF-8 JSON") from exc
    if doc.get("name") != PLUGIN_NAME or doc.get("version") != version:
        raise ReleaseBlocked(f"{label}: plugin identity/version differs from pinned release")
    return doc


def verify_reader(files: dict[str, bytes], label: str, sha: str, size: int) -> None:
    reader = files.get(READER)
    if reader is None or len(reader) != size or digest(reader) != sha:
        raise ReleaseBlocked(f"{label}: canonical reader bytes differ from pinned original")


def stage(backup_path: Path, source_root: Path, output_path: Path,
          *, expected_backup_sha: str = PINNED_BACKUP_SHA256,
          reader_sha: str = PINNED_READER_SHA256,
          reader_size: int = PINNED_READER_SIZE,
          require_clean_git: bool = False) -> dict:
    if backup_path.resolve() == output_path.resolve():
        raise ReleaseBlocked("candidate output must not overwrite backup")
    initial_sha = digest(backup_path.read_bytes())
    if initial_sha != expected_backup_sha:
        raise ReleaseBlocked("private backup SHA-256 is not the pinned v0.8.33 archive")
    backup = read_archive(backup_path)
    source = source_files(source_root)
    if require_clean_git:
        verify_clean_checkout(source_root, set(source))
    for manifest in MANIFESTS:
        parse_manifest(backup.get(manifest, b""), f"backup {manifest}", "0.8.33")
        parsed = parse_manifest(source[manifest], f"source {manifest}", VERSION)
        if parsed.get("repository") != "https://github.com/BryanHarrisScripts/PlotPickle-Studio":
            raise ReleaseBlocked(f"source {manifest}: wrong Studio source URL")
    for name in BRANDING:
        if not source.get(name) or not source[name].startswith(b"\x89PNG\r\n\x1a\n"):
            raise ReleaseBlocked(f"missing or invalid Studio PNG: {name}")
    verify_reader(backup, "backup", reader_sha, reader_size)
    verify_reader(source, "source", reader_sha, reader_size)
    if PRIVATE_SEED not in backup or not backup[PRIVATE_SEED]:
        raise ReleaseBlocked("private The Third Bell project seed absent in backup")
    for old in OLD_BRANDING:
        if old not in backup:
            raise ReleaseBlocked(f"published baseline missing expected legacy branding: {old}")
    # Do not silently discard backup-only material; it may be a private project.
    permitted_omissions = {PRIVATE_SEED, *OLD_BRANDING}
    permitted_omissions |= {n for n in backup if n.endswith(".pyc") and "__pycache__" in n}
    unexpected = set(backup).difference(source).difference(permitted_omissions)
    if unexpected:
        raise ReleaseBlocked("unreviewed private/legacy backup files would be lost: " + ", ".join(sorted(unexpected)))
    candidate = dict(source)
    candidate[PRIVATE_SEED] = backup[PRIVATE_SEED]
    # The Plugin Creator overlay update MUST explicitly delete old branding.
    if set(candidate).intersection(OLD_BRANDING):
        raise ReleaseBlocked("candidate contains legacy branding")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as file:
        with gzip.GzipFile(filename="", fileobj=file, mode="wb", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as archive:
                for name, data in sorted(candidate.items()):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mode = 0o644
                    info.uid = info.gid = 0
                    info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
    actual = read_archive(output_path)
    if actual != candidate or actual[PRIVATE_SEED] != backup[PRIVATE_SEED]:
        raise ReleaseBlocked("candidate archive round-trip or private seed preservation failed")
    if digest(backup_path.read_bytes()) != initial_sha:
        raise ReleaseBlocked("backup mutated during staging")
    for name in (*MANIFESTS, *BRANDING, READER):
        if actual[name] != source[name]:
            raise ReleaseBlocked(f"candidate differs from source at {name}")
    return {
        "status": "STAGED_NOT_PUBLISHED",
        "candidate_file": output_path.name,
        "candidate_sha256": digest(output_path.read_bytes()),
        "backup_sha256_verified": initial_sha,
        "reader_sha256_verified": reader_sha,
        "source_file_count": len(source),
        "candidate_file_count": len(actual),
        "private_seed_preserved": True,
        "legacy_branding_in_candidate": False,
        "required_plugin_creator_delete_paths": sorted(OLD_BRANDING),
        "host_authentication_verified": False,
        "fresh_chat_reopen_verified": False,
        "media_bytes_verified": False,
        "rollback_test_verified": False,
        "publish_authorized_by_this_report": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", type=Path, required=True,
                        help="private current v0.8.33 Plugin Creator archive (never commit)")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = stage(args.backup, args.source, args.output, require_clean_git=True)
    except (ReleaseBlocked, FileNotFoundError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
