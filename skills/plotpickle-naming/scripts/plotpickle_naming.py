#!/usr/bin/env python3
"""PlotPickle Naming V1: canonical names and safe original-byte reconciliation."""
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

EX = {"png":".png", "image/png":".png", "webp":".webp", "image/webp":".webp", "jpg":".jpg", "jpeg":".jpg", "image/jpeg":".jpg", "mp4":".mp4", "video/mp4":".mp4"}

def slug(s):
    result = re.sub(r"_+", "_", re.sub(r"[^A-Z0-9]+", "_", str(s).upper())).strip("_")
    if not result:
        raise ValueError("empty project or subject name")
    return result

def basename(project, block, mini_block, shot, version, extension):
    block, mini_block, shot, version = map(int, (block, mini_block, shot, version))
    if not (1 <= block <= 24 and 1 <= mini_block <= 4 and 1 <= shot <= 25 and 1 <= version <= 999):
        raise ValueError("address/version outside PlotPickle film range")
    ext = EX.get(str(extension).lower().lstrip("."))
    if ext is None:
        raise ValueError("unsupported image/motion extension")
    return f"{slug(project)}_B{block:02d}_MB{mini_block:02d}_S{shot:02d}_V{version:03d}{ext}"

def digest(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest(), path.stat().st_size

def safe_relative(root, rel):
    rel = Path(str(rel))
    if rel.is_absolute() or '..' in rel.parts or any(x == '' for x in rel.parts):
        raise ValueError(f"unsafe relative path: {rel}")
    root = Path(root).resolve()
    p = (root / rel).resolve()
    if root != p and root not in p.parents:
        raise ValueError("path escapes destination")
    return p

def reconcile(manifest, source, dest, apply=False):
    rows = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("manifest must be a list")
    out = []
    names = set()
    for row in rows:
        name = basename(row["project"], row["block"], row["miniBlock"], row["shot"], row.get("version", 1), row.get("extension", "png"))
        result = {"name": name, "source": row.get("source", ""), "state": "UNKNOWN"}
        if name in names:
            result["state"] = "DUPLICATE_DESTINATION"; out.append(result); continue
        names.add(name)
        src = safe_relative(source, row["source"])
        dst = safe_relative(dest, name)
        expected = str(row["sha256"]).lower()
        if not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise ValueError(f"bad sha256 for {name}")
        if not src.is_file():
            result["state"] = "SOURCE_MISSING"
        else:
            actual, bytes_count = digest(src)
            result.update(sourceSha256=actual, bytes=bytes_count)
            if actual != expected or (row.get("bytes") is not None and bytes_count != int(row["bytes"])):
                result["state"] = "SOURCE_HASH_MISMATCH"
            elif dst.is_file():
                h,n = digest(dst)
                result["destinationSha256"] = h
                result["state"] = "COPIED_VERIFIED" if h == expected and n == bytes_count else "DESTINATION_COLLISION"
            elif not apply:
                result["state"] = "COPY_PENDING"
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                fd, temp = tempfile.mkstemp(dir=dst.parent, prefix=".plotpickle-tmp-")
                os.close(fd)
                try:
                    shutil.copyfile(src, temp)
                    verify,_ = digest(Path(temp))
                    if verify != expected:
                        raise IOError("temporary file SHA mismatch")
                    if dst.exists():
                        result["state"] = "DESTINATION_COLLISION"
                    else:
                        os.replace(temp, dst)
                        result["state"] = "COPIED_VERIFIED" if digest(dst)[0] == expected else "READBACK_MISMATCH"
                finally:
                    if os.path.exists(temp): os.unlink(temp)
        out.append(result)
    return {"schema":"plotpickle.naming-reconciliation.v1", "originalsDeleted":False,
            "copiesVerified":sum(x["state"]=="COPIED_VERIFIED" for x in out),
            "records":out, "distinctRemoteStorageVerified":False}

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="command", required=True)
    n=sub.add_parser("name")
    for arg in ("project","block","mini-block","shot","version","ext"):
        n.add_argument("--"+arg, required=True)
    r=sub.add_parser("reconcile")
    for arg in ("manifest","source-root","destination-root"):
        r.add_argument("--"+arg, required=True)
    r.add_argument("--apply", action="store_true")
    args=ap.parse_args()
    if args.command=="name":
        print(basename(args.project,args.block,args.mini_block,args.shot,args.version,args.ext))
    else:
        print(json.dumps(reconcile(args.manifest,args.source_root,args.destination_root,args.apply),indent=2))
if __name__=="__main__": main()
