#!/usr/bin/env python3
"""Build a guarded PlotPickle Studio Production Design v0.8.42 overlay."""
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION="0.8.42"
INCLUDE=(
    "plugin.json",
    ".codex-plugin/plugin.json",
    "skills/plotpickle-design/SKILL.md",
    "skills/plotpickle-design/references/layout-sheet.md",
    "skills/plotpickle-design/scripts/design-kit.py",
    "skills/plotpickle-design/scripts/design-review.py",
    "skills/plotpickle-design/scripts/test-design-review.py",
    "skills/plotpickle-studio/SKILL.md",
    "skills/plotpickle-welcome/SKILL.md",
)
for path in ("plugin.json",".codex-plugin/plugin.json"):
    m=json.loads((ROOT/path).read_text(encoding="utf-8"))
    assert m.get("name")=="plotpickle-story-reader","Wrong plugin identity"
    assert m.get("version")==VERSION,"Version mismatch"
for name in INCLUDE:
    assert (ROOT/name).is_file(), f"Missing {name}"
assert "v0.8.42" in (ROOT/"skills/plotpickle-design/SKILL.md").read_text(encoding="utf-8")
out=ROOT/"dist"/f"plotpickle-production-design-v{VERSION}-plugin.zip"
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
    for name in INCLUDE: z.write(ROOT/name,arcname=name)
with zipfile.ZipFile(out) as z:
    assert sorted(z.namelist())==sorted(INCLUDE)
    assert z.testzip() is None
print(json.dumps({"ok":True,"archive":str(out),"version":VERSION,"files":list(INCLUDE)}))
