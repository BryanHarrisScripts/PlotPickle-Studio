#!/usr/bin/env python3
"""Read-only PPF + portable ZIP media byte audit for ChatGPT continuation.
This does not replace the native reader and does not certify Save/Lock or videos.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

HASH = re.compile(r"^(?:sha256:)?([a-fA-F0-9]{64})$")
MAX_ITEMS = 5000
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
CHUNK = 1024 * 1024

class ReopenBlocked(ValueError):
    pass

def digest(data):
    return hashlib.sha256(data).hexdigest()

def safe_path(s):
    return isinstance(s, str) and bool(s) and not s.startswith("/") and "\\\\" not in s and "\\0" not in s and all(x not in ("", ".", "..") for x in s.split("/")) and not PurePosixPath(s).is_absolute()

def inspect(raw, zip_path, expected_id=None, expected_revision=None, expected_sha256=None):
    source_hash = digest(raw)
    if expected_sha256 is not None and expected_sha256.lower().removeprefix("sha256:") != source_hash:
        raise ReopenBlocked("PROJECT_SHA256_CHANGED")
    try:
        p = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ReopenBlocked("INVALID_PPF_JSON") from exc
    if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not p["id"]:
        raise ReopenBlocked("MISSING_PROJECT_ID")
    revision = p.get("revision")
    if type(revision) is not int or revision < 0:
        raise ReopenBlocked("INVALID_REVISION")
    if expected_id is not None and expected_id != p["id"]:
        raise ReopenBlocked("PROJECT_ID_CHANGED")
    if expected_revision is not None and expected_revision != revision:
        raise ReopenBlocked("PROJECT_REVISION_CHANGED")
    registry = p.get("assetRegistry")
    if not isinstance(registry, dict) or not isinstance(registry.get("assets"), list):
        raise ReopenBlocked("MISSING_ASSET_REGISTRY")
    variations = []
    for asset in registry["assets"]:
        if not isinstance(asset, dict) or not isinstance(asset.get("variations"), list):
            raise ReopenBlocked("INVALID_ASSET_VARIATIONS")
        variations.extend(asset["variations"])
        if len(variations) > MAX_ITEMS:
            raise ReopenBlocked("TOO_MANY_MEDIA_VARIATIONS")
    totals = {k: 0 for k in ("recordedVariations", "mediaHashVerified", "mediaVerifiedBytes",
        "missingMedia", "duplicateReferences", "unsafePaths", "invalidDeclaredHash",
        "invalidDeclaredBytes", "bytesMismatch", "hashMismatch",
        "invalidWebpSignature", "archiveMemberRejected")}
    totals["recordedVariations"] = len(variations)
    with zipfile.ZipFile(zip_path) as z:
        members = {}
        for info in z.infolist():
            if info.is_dir():
                continue
            if not safe_path(info.filename):
                raise ReopenBlocked("UNSAFE_ZIP_PATH")
            if info.filename in members:
                raise ReopenBlocked("DUPLICATE_ZIP_MEMBER")
            members[info.filename] = info
        seen = set()
        for v in variations:
            if not isinstance(v, dict):
                raise ReopenBlocked("INVALID_VARIATION")
            path = v.get("portablePath")
            if not safe_path(path):
                totals["unsafePaths"] += 1
                continue
            if path in seen:
                totals["duplicateReferences"] += 1
                continue
            seen.add(path)
            h = v.get("contentHash")
            match = HASH.fullmatch(h) if isinstance(h, str) else None
            if match is None:
                totals["invalidDeclaredHash"] += 1
                continue
            length = v.get("bytes")
            if type(length) is not int or length < 0:
                totals["invalidDeclaredBytes"] += 1
                continue
            info = members.get(path)
            if info is None:
                totals["missingMedia"] += 1
                continue
            mode = (info.external_attr >> 16) & 0o170000
            if mode not in (0, 0o100000) or info.file_size > MAX_FILE_BYTES:
                totals["archiveMemberRejected"] += 1
                continue
            if length != info.file_size:
                totals["bytesMismatch"] += 1
                continue
            if totals["mediaVerifiedBytes"] + info.file_size > MAX_TOTAL_BYTES:
                raise ReopenBlocked("MAX_TOTAL_BYTES_EXCEEDED")
            computed = hashlib.sha256()
            size = 0
            signature = b""
            with z.open(info) as stream:
                while chunk := stream.read(CHUNK):
                    if size == 0:
                        signature = chunk[:12]
                    size += len(chunk)
                    if size > length or size > MAX_FILE_BYTES:
                        break
                    computed.update(chunk)
            if size != length:
                totals["bytesMismatch"] += 1
            elif computed.hexdigest() != match.group(1).lower():
                totals["hashMismatch"] += 1
            elif v.get("mediaType") == "image/webp" and not (
                len(signature) >= 12 and signature[:4] == b"RIFF" and signature[8:12] == b"WEBP"
            ):
                totals["invalidWebpSignature"] += 1
            else:
                totals["mediaHashVerified"] += 1
                totals["mediaVerifiedBytes"] += size
    problems = sum(totals[k] for k in totals if k not in ("recordedVariations","mediaHashVerified","mediaVerifiedBytes"))
    ready = len(variations) > 0 and totals["mediaHashVerified"] == len(variations) and problems == 0
    return {
        "schema": "plotpickle.portable-media-reopen.v1",
        "status": "PORTABLE_MEDIA_VERIFIED_ONLY" if ready else "MEDIA_INCOMPLETE_OR_UNVERIFIABLE",
        "project": {"id": p["id"], "revision": revision, "rawSha256": source_hash},
        "media": totals,
        "safety": {"originalPPFModified": False, "archiveExtracted": False,
                   "canonicalReaderAccepted": False, "pluginHostReopenedProject": False,
                   "savedLockedAndAcceptedVerified": False, "MP4Verified": False,
                   "paidProviderInvoked": False}
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--assets-zip", type=Path, required=True)
    parser.add_argument("--expected-id")
    parser.add_argument("--expected-revision", type=int)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--out", type=Path)
    a = parser.parse_args(argv)
    try:
        result = inspect(a.project.read_bytes(), a.assets_zip,
                         a.expected_id, a.expected_revision, a.expected_sha256)
        data = json.dumps(result, indent=2, sort_keys=True) + "\\n"
        if a.out:
            with a.out.open("x", encoding="utf8") as dest:
                dest.write(data)
        else:
            sys.stdout.write(data)
        return 0 if result["status"] == "PORTABLE_MEDIA_VERIFIED_ONLY" else 1
    except (ValueError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        sys.stderr.write("REOPEN_BLOCKED: " + str(exc) + "\\n")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
