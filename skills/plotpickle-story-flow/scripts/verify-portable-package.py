#!/usr/bin/env python3
"""Verify a saved PPF's portable media archive for ChatGPT story reopening.

Read-only utility. The PPF is the authority, ZIP is an untrusted collection of
candidate bytes. This does NOT replace the canonical native reader, establish
native Save/Lock, validate MP4 provenance or claim ChatGPT plugin persistence.
No files are extracted, no network or provider calls are made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

HEX = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")
MAX_REFERENCES = 5000
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
CHUNK = 1024 * 1024


class InvalidPackage(ValueError):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def safe_path(path: object) -> bool:
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or "\x00" in path:
        return False
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    return not PurePosixPath(path).is_absolute()


def refs(project: dict) -> list[dict]:
    registry = project.get("assetRegistry")
    if not isinstance(registry, dict) or not isinstance(registry.get("assets"), list):
        raise InvalidPackage("ASSET_REGISTRY_MISSING_OR_INVALID")
    found = []
    for asset in registry["assets"]:
        if not isinstance(asset, dict):
            raise InvalidPackage("INVALID_ASSET_RECORD")
        variations = asset.get("variations")
        if not isinstance(variations, list):
            raise InvalidPackage("INVALID_VARIATION_COLLECTION")
        for variation in variations:
            if not isinstance(variation, dict):
                raise InvalidPackage("INVALID_VARIATION_RECORD")
            found.append(variation)
            if len(found) > MAX_REFERENCES:
                raise InvalidPackage("TOO_MANY_MEDIA_REFERENCES")
    return found


def audit(project_bytes: bytes, archive: Path,
          expected_id: str | None = None,
          expected_revision: int | None = None,
          expected_sha256: str | None = None) -> dict:
    raw_hash = sha256(project_bytes)
    if expected_sha256 and expected_sha256.lower().removeprefix("sha256:") != raw_hash:
        raise InvalidPackage("PROJECT_SHA256_CHANGED")
    try:
        project = json.loads(project_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidPackage("INVALID_PROJECT_JSON") from exc
    if not isinstance(project, dict) or not isinstance(project.get("id"), str) or not project["id"]:
        raise InvalidPackage("MISSING_PROJECT_ID")
    rev = project.get("revision")
    if type(rev) is not int or rev < 0:
        raise InvalidPackage("INVALID_PROJECT_REVISION")
    if expected_id is not None and expected_id != project["id"]:
        raise InvalidPackage("PROJECT_ID_CHANGED")
    if expected_revision is not None and expected_revision != rev:
        raise InvalidPackage("PROJECT_REVISION_CHANGED")
    entries = refs(project)
    totals = {
        "recordedVariations": len(entries),
        "mediaHashVerified": 0,
        "mediaVerifiedBytes": 0,
        "missingMedia": 0,
        "unsafePaths": 0,
        "missingOrInvalidDeclaredHash": 0,
        "missingOrInvalidDeclaredBytes": 0,
        "bytesMismatch": 0,
        "sha256Mismatch": 0,
        "invalidWebpSignature": 0,
        "archiveMemberRejected": 0,
        "duplicateReferences": 0,
    }
    if not archive.is_file():
        raise InvalidPackage("ARCHIVE_NOT_ACCESSIBLE")
    seen_paths = set()
    try:
        with zipfile.ZipFile(archive, "r") as z:
            index = {}
            duplicate_members = set()
            for info in z.infolist():
                if info.is_dir():
                    continue
                if not safe_path(info.filename):
                    raise InvalidPackage("UNSAFE_ZIP_MEMBER_PATH")
                if info.filename in index:
                    duplicate_members.add(info.filename)
                index[info.filename] = info
            if duplicate_members:
                raise InvalidPackage("DUPLICATE_ZIP_MEMBERS")

            for item in entries:
                path = item.get("portablePath")
                if not safe_path(path):
                    totals["unsafePaths"] += 1
                    continue
                if path in seen_paths:
                    totals["duplicateReferences"] += 1
                    continue
                seen_paths.add(path)
                expected = item.get("contentHash")
                matcher = HEX.fullmatch(expected) if isinstance(expected, str) else None
                if not matcher:
                    totals["missingOrInvalidDeclaredHash"] += 1
                    continue
                declared_bytes = item.get("bytes")
                if type(declared_bytes) is not int or declared_bytes < 0:
                    totals["missingOrInvalidDeclaredBytes"] += 1
                    continue
                info = index.get(path)
                if info is None:
                    totals["missingMedia"] += 1
                    continue
                # Unix ZIP member type: regular file or unspecified only.
                file_type = (info.external_attr >> 16) & 0o170000
                if file_type not in (0, 0o100000) or info.file_size > MAX_FILE_BYTES:
                    totals["archiveMemberRejected"] += 1
                    continue
                if info.file_size != declared_bytes:
                    totals["bytesMismatch"] += 1
                    continue
                if totals["mediaVerifiedBytes"] + info.file_size > MAX_TOTAL_BYTES:
                    raise InvalidPackage("PACKAGE_SIZE_LIMIT")
                h = hashlib.sha256()
                size = 0
                header = b""
                with z.open(info) as stream:
                    while True:
                        chunk = stream.read(CHUNK)
                        if not chunk:
                            break
                        if size == 0:
                            header = chunk[:12]
                        size += len(chunk)
                        if size > MAX_FILE_BYTES or size > declared_bytes:
                            break
                        h.update(chunk)
                if size != declared_bytes:
                    totals["bytesMismatch"] += 1
                    continue
                if h.hexdigest() != matcher.group(1).lower():
                    totals["sha256Mismatch"] += 1
                    continue
                if item.get("mediaType") == "image/webp" and not (
                    len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
                ):
                    totals["invalidWebpSignature"] += 1
                    continue
                totals["mediaHashVerified"] += 1
                totals["mediaVerifiedBytes"] += size
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise InvalidPackage("UNREADABLE_OR_CORRUPT_ARCHIVE") from exc

    errors = sum(totals[k] for k in (
        "missingMedia", "unsafePaths", "missingOrInvalidDeclaredHash",
        "missingOrInvalidDeclaredBytes", "bytesMismatch", "sha256Mismatch",
        "invalidWebpSignature", "archiveMemberRejected", "duplicateReferences"
    ))
    verified = bool(entries) and totals["mediaHashVerified"] == len(entries) and errors == 0
    return {
        "schema": "plotpickle.portable-media-reopen.v1",
        "status": "PORTABLE_MEDIA_VERIFIED_ONLY" if verified else "MEDIA_INCOMPLETE_OR_UNVERIFIABLE",
        "project": {"id": project["id"], "revision": rev, "rawSha256": raw_hash},
        "media": totals,
        "safety": {
            "originalPPFModified": False,
            "archiveExtracted": False,
            "providerInvoked": False,
            "canonicalReaderAccepted": False,
            "chatgptInstalledPluginReopenedProject": False,
            "savedLockedAndAcceptedStatesVerified": False,
            "videoProvenanceVerified": False,
            "mediaVerifiedDoesNotImplyProductionReadiness": True
        }
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--assets-zip", type=Path, required=True)
    p.add_argument("--expected-id")
    p.add_argument("--expected-revision", type=int)
    p.add_argument("--expected-sha256")
    p.add_argument("--out", type=Path, help="private output; must not already exist")
    a = p.parse_args(argv)
    try:
        report = audit(a.project.read_bytes(), a.assets_zip,
                       a.expected_id, a.expected_revision, a.expected_sha256)
        output = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if a.out:
            with a.out.open("x", encoding="utf-8") as dest:
                dest.write(output)
        else:
            sys.stdout.write(output)
        return 0 if report["status"] == "PORTABLE_MEDIA_VERIFIED_ONLY" else 1
    except (InvalidPackage, OSError) as exc:
        sys.stderr.write("REOPEN_BLOCKED: " + str(exc) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
