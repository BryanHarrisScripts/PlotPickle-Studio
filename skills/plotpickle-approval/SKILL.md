---
name: plotpickle-approval
description: "Apply creator-approved PlotPickle design references and storyboard Save/Lock with independently reopened PPF and actual media proof. Show 25/50 truth and isolate unrelated shots."
---

# PlotPickle Studio v0.8.43 — Approval means verify → Save → Lock → independently read back

When the creator explicitly approves an image or image set, treat that approval as an instruction to **perform** the available Save→Lock transaction on those exact assets, never as evidence a transaction has already happened. State the precise difference between user approval, image bytes and hash, portable PPF saved marker, portable PPF lock marker, and ChatGPT Library persistence. Any failed or incomplete step must remain visibly unverified. The current PlotPickle plugin is a packaged skill, not a persistent media host or always-running database.

## Storyboard image Save/Lock

Use `../read-plotpickle-project/SKILL.md` and `../read-plotpickle-project/references/default-save-lock.md`. Open the real latest saved PPF plus its matching portable image files. Pin project id, revision and SHA. For eligible *already registered and source-linked* individual images, use the native `default-save-lock.py auto` command, which performs separate SAVE and LOCK snapshots, validates media with Pillow, independently reopens both, and checks the canonical Node storyboard reader. Never directly toggle JSON booleans instead of running the transaction. Preserve explicit unlock exceptions and image review decisions; don't mutate unrelated shots. When an old PPF lacks required canonical structural metadata, do not falsify successful validation. A separately versioned migration snapshot may add the minimum canonical scaffold, with all existing source and shot records verified unchanged, before any lock transaction. Preserve the original in Library and include a migration receipt.

For a set of 25 images per Mini-Block and five images per illustrated page, enumerate the canonical addresses explicitly. Two distinct Block 01 / Mini 01 and Block 02 / Mini 01 selections mean 50 individual *shot positions*. A page PNG or 25-panel collage is NOT itself 25 original byte-verified shot images and cannot be treated as 25 native saved/locked mappings. If a selected visual sequence conflicts with the actual screenplay or approved character identity, report the conflict and keep it staged for reconciliation. Do not silently rewrite the screenplay to match a visual collage. Do not assign wrong character labels merely to meet a count. Report actual locked X/50, not the desired total.

## Creator-approved character and world design references

Use `scripts/register-design-references.py` ONLY with an explicit manifest containing the current creator-approved images, approved subject identities, real local image paths, and cited source passages. This creates a **NEW**, nonoverwriting portable PPF snapshot; the original file and existing screenplay, structure, storyboard shots/mappings and artifact approvals remain unchanged. It adds a typed image asset + an `assetRegistry.extensions.approvedDesignReferences` record per design reference, saves the image bytes, reopens and verifies SHA and full pixel decode, then marks the reference locked in a second version and reopens again. These reference locks are NOT storyboard shot Save/Lock and must never be counted toward the 50 shot positions. On re-run, reject duplicates; do not put the user's private artwork or screenplay inside the published plugin.

Example (arguments must use actual current source values):

    python3 scripts/register-design-references.py --project project.ppf.json --reader ../read-plotpickle-project/scripts/inspect-project.mjs --manifest approved-refs.json --project-id ID --revision N --sha256 HASH --out design-references-locked

The reference manifest must include `creatorApproval: "explicit-user-approval"` and `references: [{id,kind:"character"|"world",subjectId,label,image,sourcePassageIds}]`.

## Independently audit all positions and references

    python3 scripts/audit-approved-scope.py --project project.ppf.json --out approved-scope-audit.json

The audit returns a 50-shot target (Block 01/Mini 01 and Block 02/Mini 01), byte/decoder verified native locked counts, missing/unsafe/changed media, and independently verified design-reference locks. It does not make a write or claim that a local snapshot has been persisted to ChatGPT Library. Persist a new versioned portable package in the creator's authorized Library project only after independent readback; do not overwrite the source project unless the user explicitly requests that replacement and stale-write guards pass. Never claim background process execution, provider spend or GitHub CI usage.

## Visual continuity / next page

The Third Bell: Mara is the mature gray-bearded keeper wearing a navy knit cap; Elara is the young engineer. Treat their identities as different and preserve the creator-approved cinematic cartoon-pixel style. The North Head lighthouse, station, bell with three wave marks, mug with three waves, dangerous channel, ferry dock and dawn lighting are the approved world baseline, while camera geometry beyond the actual screenplay remains proposed. Use the user's existing approved images as visual references for new world continuity layouts and five-shot pages. All newly generated pages remain **draft candidates** until separately approved, registered and verified; generation cannot assert "Saved", "Locked" or "Approved" badges. A page should show exactly five shots with explicit Mini-Block addresses; don't reuse existing shot numbers or invent source approval. If next Mini-Block 03 screenplay allocation is unresolved, produce a proposed, clearly labeled storyboard plan rather than a native locked page.

Run local offline tests: `python3 scripts/test-approval.py`, and the existing `../read-plotpickle-project/scripts/test-default-save-lock.py`. GitHub CI is not part of this release workflow. Plugin Creator updates the private plugin code; creator private PPFs/assets stay outside the plugin archive.


## Simple sequential review and handoff refresh

Use Previous / Next to review exact real individual images in the existing approved Image Review. Offer Approve and Lock, Flag for Change and Unlock as supported conversation actions. Approve and Lock performs the existing guarded transaction and persistence/readback on that exact asset; no success badge from intent alone. Reconcile its downstream uses using `../plotpickle-assets/references/asset-handoff.md` after a successful write. Changes flag dependent media for review without overwriting a cut or spending credits. Flagged feedback needs an actual saved sidecar or supported writer, not transient UI state.
