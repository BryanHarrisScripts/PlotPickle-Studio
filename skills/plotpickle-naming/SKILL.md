---
name: plotpickle-naming
description: Mandatory canonical filename assignment for every newly generated or imported PlotPickle storyboard image, video, approved character/world reference, Pitch Edit and manifest; existing-shot non-destructive V1 migration, per-asset original SHA-256 matching across ChatGPT Space and PlotPickle Studio, and lossless renaming with versioned provenance.
---

# PlotPickle Studio — Naming Standard V1

**Creator approved 2026-11-23.** This policy applies to all PlotPickle projects and all future image generation, redo, import, export and backup/reconciliation. Naming is assigned **automatically**, as part of a new asset's completion workflow; never ask the creator to invent a filename. The real project/source/asset identity and content hash remain authoritative, not the human-readable basename.

## Canonical names

- Storyboard image (original or approved revision): `PROJECT_B##_MB##_S##_V###.ext`, e.g. `AFTERGLOW_B03_MB04_S02_V001.png`.
- Motion for the same shot: same stem, actual extension `.mp4` (media kind must remain distinct in the registry).
- Character reference: `PROJECT_REF_CHAR_SUBJECT_V###.ext`; vehicle `PROJECT_REF_VEHICLE_SUBJECT_V###.ext`; world `PROJECT_REF_WORLD_SUBJECT_V###.ext`. Normalize project and subject slugs to uppercase ASCII alphanumerics and underscores, avoiding empty/ambiguous slugs. Retain stable IDs in the PPF.
- Pitch Edit: `PROJECT_PITCH_EDIT_V###.mp4`.
- Manifest: `PROJECT_MANIFEST_V###.json`.
- B (Block) and MB (Mini-Block) are two digits (01–24 and 01–04 for the current film engine); S is two digits (01–25), V is three digits (001–999). Full original MIME determines the extension; `.png` is never forced onto WebP or JPEG bytes. The filename is informational, not proof of the file format; validate the actual signature.

## Automatic assignment at creation

1. After selecting exact project ID, production address, role and source revision (but before registering the generated image), compute the canonical stem using `scripts/plotpickle_naming.py name --project ... --block ... --mini-block ... --shot ... --version ... --ext ...` when local execution is available. Where local execution is unavailable, format the same canonical stem deterministically in the active creation workflow.
2. For a first accepted original at a new shot, use `V001`. A replacement for the *same* shot must receive the next unoccupied version after examining real prior variations; do not reuse or overwrite a historical filename. Never infer historical version numbers from old filenames alone. For the legacy 225-shot Afterglow Studio inventory, the creator-approved canonical alias is V001 for the 225 currently registered candidates, with historical alternates preserved separately until reconciliation.
3. Save newly generated **original bytes** under that canonical filename, calculate SHA-256 and byte size from the exact bytes and pin source/shot/variant IDs. Verify full decode, source continuity and creator approval independently. A displayed filename is not Save, Lock, import or two-copy verification.
4. For ChatGPT Space and PlotPickle Studio copies, require actual original-byte readback at each distinct storage destination. Record destination file/asset ID, original bytes, digest, variant, source revision and timing separately. Two filenames or two database entries without both sets of bytes **do not** count as two copies. After readback, both SHA-256 values must equal the approved original digest.
5. For migration, map every existing ID and SHA to a canonical filename. **Never destructively rename, delete, re-encode or overwrite** a creator original or any referenced PPF/Studio working file without a fully supported, source-pinned atomic migration and readback. Prefer a new alias/copy plus manifest while legacy references are in use. If the host lacks a supported rename/copy/Space media connector, report `RENAME_PENDING` / `SPACE_COPY_PENDING` and preserve everything. Never fake completion.
6. Do not put `approved`, `locked`, `final`, `drifted` or status words in canonical names. Keep approval, saved, locked, source match and media verification as distinct project fields. Rejected/DRIFTED images and their original bytes stay preserved with separate stable IDs and must not consume the approved filename without evidence.

## Offline verifier and migration helper

`scripts/plotpickle_naming.py` provides deterministic `name` and non-destructive `reconcile` actions against a private, creator-supplied manifest and existing **actual file bytes**. `reconcile` reports matched versus missing/mismatch, supports `--apply` to make independently hashed canonical copies in a destination folder, and never removes the originals or mutates PPF/Studio/Space host records. It does not establish independent remote storage even if two local folders exist. `scripts/test_plotpickle_naming.py` checks naming, original preservation, hash comparisons, collisions and version safety.

This packaged skill is a client-side workflow contract. It does **not** by itself alter a hosted Sites MCP server, add ChatGPT Space upload capability, rename already-saved Studio keys, or complete an unavailable remote byte transport. Current active host must verify these capabilities separately.
