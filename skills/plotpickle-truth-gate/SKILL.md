---
name: plotpickle-truth-gate
description: Mandatory source-and-image truth gate for PlotPickle. Trigger before generating, continuing, redoing or approving individual cinematic shots or batches, and before editor imports, locks, motion and Pitch Edit. Check screenplay, approved character and vehicle images, exact Block/Mini/Shot, prompt format and actual media; label ONLY proven drifted review copies DRIFTED.
---

# PlotPickle Truth Gate — enforced preflight contract, v2

**Every screenplay-backed new image, redo, batch, review, source/PPF import, Save/Lock, motion, Storyboard, REEL or Pitch Edit must pass through this gate.** Do not infer that this policy alone changes the hosted Studio MCP server. Read `../read-plotpickle-project/SKILL.md`, `../plotpickle-approval/SKILL.md` and `../plotpickle-image-production/SKILL.md` as appropriate. Store user project records in their authorized Library/PPF, never the distributed plugin.

## Authority order

1. Reopen the latest **creator-authorized original screenplay or PPF** by actual file bytes; pin project identity, revision, source hash, specific source passage IDs and verbatim scene/action/dialogue text. Conversation memory, UI cards and previous chat recaps are clues, not source.
2. Reopen the **actual approved visual reference image bytes** (characters, age variants, vehicle, wardrobe, world), independently decode them and SHA-check. A reference filename or a textual description is insufficient. A design proposal cannot override a prior approved visual.
3. Reopen the **approved preceding and following storyboard image originals** where available, check source binding and hash. Do not confuse prior creator approval with new project Save/Lock.
4. Keep `productionAddress` (24 Blocks × 4 Mini-Blocks × 25 slots) distinct from the screenplay's mechanical `sourceBlockNumber` and `sourceMiniBlockNumber`. A shot can reference source passages in a different mechanical block. Never fill missing numbered positions by guessing.
5. Carry separate dimensions: current image semantic state, actual original-byte SHA/readback, explicit creator approval, verified native PPF Save, verified native PPF Lock, Studio import and downstream usage status. Filename suffixes are not receipts.

## Hard gate before any generation — executable

Each shot must have a persisted **Shot Truth Card**: actual project/source file and raw SHA; exact production address; exact screenplay source passages and scene; subjects/age, story action, camera, location/time, approved references (role, file ID/path, original SHA) plus preceding shot anchor; `mustShow`, `mustNotShow`; a unique **single-frame** 16:9 prompt and expected image-gate status. Create a small packet of 1–5 distinct sequential shots; five requests are five independent full cinematic frames, not one collage. The host must actually provide the verified visual references to the image provider, not merely mention names in the prompt. If host cannot pass images, report that limitation and do not call the result reference-anchored.

When actual source/reference originals are accessible, prepare a private `plotpickle.image-production-context.v1` packet and run:

`python3 scripts/production_guard.py preflight --packet shot-packet.json --assets-root /authorized/project/files --out new-preflight-report.json`

Read `references/image-production-gate.v1.md` for the packet contract and the distinction between source hash, model reference delivery and semantic review. **BLOCKED means do not generate or spend provider credits.** The script verifies actual source bytes, approved reference image bytes and prior image, passages, duplicate/gap addresses, single-frame prompt wording and 16:9 image requirements. It does not semantically understand a screenplay and does not itself attach bytes to the model. When the execution tool is unavailable, perform the same exact-source preflight manually, show its unverifiable parts, and fail closed instead of asserting PASS.

**Never** generate a five-panel storyboard, tiled sheet, multiple shots in one image, unrelated flashback, different actor, new vehicle, altered age or new location to satisfy an image slot. For a direct `next five` request, sequential shot numbers, scene source and the latest verified continuation location MUST be respected. A collage cannot be cut into five images and claimed as independent originals.

## Postflight after each actual image

Independently inspect the returned image pixels beside the exact screenplay text and real approved visual references. Verify protagonist/age/wardrobe, vehicle/cabin silhouette, time/location, required action, readable critical UI text, camera geography, frame format and whether it repeats the previous shot. Compare original hashes, decoder result and dimensions. Status values:

- `PASS`: the visual visibly matches the pinned source and approved references. **Not** an approval or PPF lock.
- `DRIFTED`: clearly wrong identity, vehicle, scene, action, five-panel image, invented event, or unacceptable repeated frame. Record a specific source-backed contradiction.
- `REVIEW_REQUIRED`: ambiguous visual/mapping/identity, or possibly incorrect event; do not stamp DRIFTED without proof.
- `UNKNOWN`: inaccessible pixels/source/references or no image. Cannot be used.

For exact-byte candidates, validate a private `plotpickle.image-production-review.v1` report:

`python3 scripts/production_guard.py review --packet shot-packet.json --results review.json --assets-root /authorized/project/files --out new-review-report.json`

The postflight rejects missing/duplicate/mismatched image bytes and claims of production readiness based merely on booleans. It cannot perform the human/visual semantic inspection itself, verify remote reference attachments, write PPF, or mark any media **PRODUCTION_READY**. Review states must remain separately persisted by exact project/shot/candidate hash.

## Mark only confirmed DRIFTED images, without destroying originals

When visual inspection establishes `DRIFTED`, create a stamped **review derivative** with the prominent exact word `DRIFTED` using:

`python3 scripts/drift_review.py stamp --image RAW.png --out DRIFTED-REVIEW.png --status DRIFTED --reason 'specific source contradiction'`

This refuses stamping any other state, preserves the original bytes and emits an SHA receipt. Never stamp PASS, REVIEW_REQUIRED, UNKNOWN or unrelated creator-approved originals. Show visible DRIFTED overlays in the future Studio backend and block flagged frames from storyboard production, motion, animatic, editor, Pitch Edit and exports. The current packaged script is **not** enforcement in the hosted Studio backend; see `references/backend-enforcement-contract.v1.md`.

## Generation/retry and continuation

After one definite drift, correct the **same shot card and reference delivery** before retrying; do not keep replaying an old collage prompt. After repeated drift, stop and expose the source/host mismatch instead of generating beyond the missing position. Never silently increment continuation because an image file was created. Corrected images require independent inspection and creator approval on the exact replacement hash. If one of five fails, report actual counts and addresses, not five green badges.

## Save/Lock & Studio boundaries

Creator approval is an instruction to attempt a guarded Save → Lock transaction, not evidence it succeeded. For registered source-linked images use `../plotpickle-approval/SKILL.md` and `../read-plotpickle-project/references/default-save-lock.md`; independently reopen native PPF with the canonical Node reader and original media. Studio review, Library upload or `approved-locked` file naming do not prove native PPF Save/Lock. Preserve old image, other mini-blocks, BEATs and six tracks. Never accept a status truthy string (`"true"`/`"false"`) as a boolean or forge readback receipts.

The live `studio_get_state` can be older than creator Library; use project-catalog and verified current source to detect version mismatches. `studio_import_project` is a separate Studio workspace action and **does not write the native Library PPF**. No provider spend without explicit current job-specific approval. Never package a private screenplay, character sheet or photograph into this plugin.

Run `python3 scripts/test_production_guard.py`, `python3 scripts/test_drift_review.py`. Synthetic/offline checks do not certify the deployed MCP, remote reference attachments, pixel semantics, active Studio importer or public-account isolation. Never call a private plugin update an approved live Studio deployment.
