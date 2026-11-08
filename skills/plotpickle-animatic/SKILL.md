---
name: plotpickle-animatic
description: Build, validate and render source-pinned PlotPickle 24-fps still-image animatic draft MP4s from portable PPF and actual image bytes with ffmpeg.
---

# PlotPickle — Draft Animatic Bridge (v0.8.25)

This is the existing read-only PPF-to-manifest and optional FFmpeg/ffprobe 24-fps draft renderer. It never alters screenplay revision, story approvals or Save/Lock. The input is the current actual saved `.ppf.json` and separately available portable `assets/`; the plugin does not bundle private story files. Read `../read-plotpickle-project/SKILL.md` before use.

## Source and timing

The `assetRegistry.extensions.projectModel.runtimePlan.physicalShots` records supply the 4-Act address and whole-frame edit duration. Current image assignments combine source artwork with `storyWorkflow.imageMappings`, accounting for superseded or rejected candidates. Missing mappings are draft gaps, never automatically accepted art. A valid draft records project SHA-256, source revision and each image hash. Variable editorial duration never changes the original position scaffold.

## Commands

    python3 scripts/animatic-bridge.py manifest --project story.ppf.json --out animatic-manifest.json
    python3 scripts/animatic-bridge.py validate --project story.ppf.json --manifest animatic-manifest.json --assets-root /path/to/story-package
    python3 scripts/animatic-bridge.py render --project story.ppf.json --manifest animatic-manifest.json --assets-root /path/to/story-package --out draft-animatic.mp4

`assets-root` contains the nested `assets/` directory. Use `--allow-gaps` only for explicitly labelled incomplete previews. Output never overwrites existing media. Manifest can use a separate cue file of schema `plotpickle.animatic-cues.v1` with captions bound to actual dialogue passages and before/after cards; see `references/animatic-workflow.md` and `references/editorial-cues-example.json`.

Validate actual bytes, hashes, safe paths, project identity and plan revision; no asset metadata alone proves media availability. FFmpeg and ffprobe must actually be available to render. Draft output includes H.264 MP4 picture with silent AAC unless separately approved source-linked sound is supplied. Verify exact frame count, dimensions, duration, complete decode and SHA-256; report provenance and gaps. A draft is not an approved master, performed dialogue or a recorded provider billing action.

## fal image-to-video complement

For AI motion across 1–5 consecutive 3-second positions use `../plotpickle-fal-production/SKILL.md` and its `references/motion-spans-v1.md`. fal creates source-linked draft motion only after verified source images, a live account/model/cost check and explicit one-job approval. Its output duration can differ from the source's exact 72–360 editorial frames; downloaded, validated clips can later be aligned without rewriting PPF. The existing animatic manifest is still the authority for editorial timing; don't put one paid generation into every position by default.

## Save/Lock and tests

The initial-image default Save → Lock workflow is `../read-plotpickle-project/references/default-save-lock.md`; always rebuild source-pinned manifests when source revision changes. Run `python3 scripts/test-animatic-bridge.py`. Earlier Brotherly Love historical draft/timing figures may be used as context but do not represent currently accessible/verified personal media. No local application, hosted export or external billing is implied by this package.
