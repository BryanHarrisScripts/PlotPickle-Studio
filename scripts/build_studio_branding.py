#!/usr/bin/env python3
"""Render Studio-owned branding; never import original PlotPickle artwork."""
from pathlib import Path
import struct
import hashlib
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZES = {"studio-composer-icon": (512, 512), "studio-logo": (1200, 256)}

def build_assets():
    for stem, expected in SIZES.items():
        source = ASSETS / (stem + ".svg")
        target = ASSETS / (stem + ".png")
        if not source.is_file():
            raise SystemExit("Missing Studio artwork source: " + source.name)
        cairosvg.svg2png(bytestring=source.read_bytes(), write_to=str(target))
        raw = target.read_bytes()
        if raw[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit("Invalid PNG: " + target.name)
        dimensions = struct.unpack(">II", raw[16:24])
        if dimensions != expected:
            raise SystemExit(f"Unexpected size {dimensions} for {target.name}")
        print(f"{target.name}: {dimensions}, {len(raw)} bytes, sha256 {hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    build_assets()
