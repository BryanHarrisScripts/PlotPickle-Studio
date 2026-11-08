#!/usr/bin/env python3
"""Verify the exact previously published canonical PlotPickle v0.8.33 reader."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = Path("skills/read-plotpickle-project/scripts/inspect-project.mjs")
EXPECTED_SIZE = 1364997
EXPECTED_SHA256 = "6c9c239f4484d2cd624bfd1c761fa8645203cc8e78be1d58b11ec2500a5f498f"

def main() -> int:
    path = ROOT / RELATIVE
    if not path.is_file():
        print(f"BLOCKED: exact published reader not yet present: {RELATIVE}")
        return 1
    content = path.read_bytes()
    actual_sha = hashlib.sha256(content).hexdigest()
    print(f"Reader size: {len(content)}; SHA-256: {actual_sha}")
    if len(content) != EXPECTED_SIZE or actual_sha != EXPECTED_SHA256:
        print("BLOCKED: not the exact owner-supplied published v0.8.33 reader.")
        return 1
    print("PASS: exact published reader bytes recovered and hash checked.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
