#!/usr/bin/env python3
"""Gate PlotPickle Studio source-candidate metadata, without pretending release readiness."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/BryanHarrisScripts/PlotPickle-Studio"
MANIFESTS = ("plugin.json", ".codex-plugin/plugin.json")
SOURCE_REQUIRED = (
    "skills/plotpickle-welcome/SKILL.md",
    "skills/plotpickle-studio/pilot/src/projection.mjs",
    "skills/plotpickle-studio/pilot/tests/projection.test.mjs",
    "skills/plotpickle-fal-production/scripts/fal-handoff.py",
    "skills/plotpickle-creative/data/lesson-catalog.json",
    "skills/plotpickle-editor/windows/editor_server.py",
    "skills/plotpickle-animatic/scripts/animatic-bridge.py",
    "docs/MIGRATION.md",
)
RELEASE_REQUIRED = (
    "assets/composer-icon.png",
    "assets/plotpickle-logo.png",
    "skills/read-plotpickle-project/scripts/inspect-project.mjs",
    "skills/plotpickle-editor/windows/the-third-bell-seed.example.json",
)

def verify(phase: str) -> None:
    errors = []
    for name in MANIFESTS:
        try:
            manifest = json.loads((ROOT / name).read_text(encoding="utf-8"))
            if manifest.get("version") != "0.8.34":
                errors.append(f"{name}: expected unpublished candidate version 0.8.34")
            if manifest.get("repository") != REPOSITORY:
                errors.append(f"{name}: wrong repository")
            if manifest.get("license") != "AGPL-3.0-or-later":
                errors.append(f"{name}: wrong licence identifier")
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            errors.append(f"{name}: {exc}")
    for name in SOURCE_REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f"missing source: {name}")
    if (ROOT / "skills/plotpickle-editor/windows/the-third-bell-seed.json").exists():
        errors.append("creator-specific editor seed is not permitted in public source")
    if phase == "release":
        for name in RELEASE_REQUIRED:
            if not (ROOT / name).is_file():
                errors.append(f"release input not yet recovered: {name}")
        # A passing file-presence gate is not a complete release audit: hashes,
        # tests, third-party licences, host acceptance and approved publishing are separate.
    for message in errors:
        print("BLOCKED:", message)
    if errors:
        raise SystemExit(1)
    print("SOURCE CANDIDATE CHECK PASSED" if phase == "source"
          else "RELEASE INPUTS PRESENT; human approval and independent verification still required")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("source", "release"), default="source")
    verify(parser.parse_args().phase)
