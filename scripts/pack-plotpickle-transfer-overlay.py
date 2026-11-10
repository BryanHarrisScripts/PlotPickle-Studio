#!/usr/bin/env python3
"""Build a minimal PlotPickle Studio 0.8.41 overlay for Plugin Creator."""
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.8.41"
INCLUDE = (
    "plugin.json",
    ".codex-plugin/plugin.json",
    "skills/plotpickle-creative/data/creative-services.json",
    "skills/plotpickle-creative/scripts/service-catalog.py",
    "skills/plotpickle-creative/scripts/test-service-catalog.py",
    "skills/plotpickle-creative/references/connected-services.md",
    "skills/plotpickle-creative/references/plotpickle-transfer-site.md",
    "skills/plotpickle-welcome/SKILL.md",
)
for name in ("plugin.json", ".codex-plugin/plugin.json"):
    data = json.loads((ROOT / name).read_text(encoding="utf-8"))
    assert data["name"] == "plotpickle-story-reader", "Cannot overwrite a different plugin"
    assert data["version"] == VERSION, "Manifest version mismatch"
services = json.loads((ROOT / INCLUDE[2]).read_text(encoding="utf-8"))["services"]
assert [s["id"] for s in services] == ["suno", "fal", "plotpickle-transfer", "buzz", "modem"]
transfer = services[2]
assert transfer["status"] == "not-confirmed-connected"
assert transfer["siteVisibility"] == "private-by-default"
assert transfer["credentialsStoredByPlotPickle"] is False
assert transfer["setupGuide"] in INCLUDE
assert all((ROOT / name).is_file() for name in INCLUDE), "Missing overlay source"

out = ROOT / "dist" / f"plotpickle-transfer-v{VERSION}-plugin.zip"
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for name in INCLUDE:
        zf.write(ROOT / name, arcname=name)
with zipfile.ZipFile(out) as zf:
    assert sorted(zf.namelist()) == sorted(INCLUDE)
    assert zf.testzip() is None
print(f"Built {out} with {len(INCLUDE)} files")
