---
name: plotpickle-image-production
description: Produce individual PlotPickle film images reliably when the user says next five shots, generate images, continue storyboarding, redo drifted images, approve or lock shots. Mandatory screenplay and approved-asset context preflight, one actual 16:9 cinematic image per shot, independent visual truth review and honest Save/Lock/Studio handoff; prevent generic montage prompts and lost context.
---

# PlotPickle Image Production — single-frame continuity workflow

This routes ALL visual production requests through `../plotpickle-truth-gate/SKILL.md` before any image generation. Read `../plotpickle-chat-first/SKILL.md`, `../read-plotpickle-project/SKILL.md` and `../plotpickle-approval/SKILL.md` when resuming/reviewing existing work. In the current user's selected story, continue from **verified persistent project state**, not the last conversational estimate. Do not create another app, Site, database or compulsory login.

**Naming Standard V1 (2026-11-23):** Read and apply `../plotpickle-naming/SKILL.md` automatically to EVERY new or redone storyboard image and motion asset, including single-image and batches. Assign a canonical basename using the source-pinned Block/Mini-Block/Shot and actual MIME **before saving or presenting the new asset**. Never ask creators to supply filenames; never overwrite prior revisions or infer approved/locked from the name. Report `REMOTE_NAMING_PENDING` if the hosted backend cannot persist the generated filename.

## Normal user flow: Continue five

1. Identify the exact saved story and source revision/hash; reconcile current private Library, source PPF, Studio registry and any pending review receipts. A Studio active 25-shot window does not necessarily include later Library images. Display conflicting versions instead of silently overwriting them. Never reset the selected story.
2. Read the screenplay *at the requested narrative moment* and authored shot mapping. Verify the 24×4×25 production address and separate mechanical source-block address. Verify the latest finished **accepted** frame, rejected variants and last attempted but pending frame. Do not skip a hole.
3. Reopen bytes for the approved main character(s), their correct age variant, vehicles, world/location and preceding one or two image originals. For new projects without approved references, first stage a proposed design for creator selection. Preserve old approved references.
4. Build one distinct Shot Truth Card for each of the 1–5 addresses with verbatim source passage IDs, specific visible action, camera, scene/time, expected people and exclusions. Build/execute the `production_guard.py preflight` packet. Resolve and deliver the verified original inputs using the workflow below before generating.
5. Generate **one full 16:9 cinematic image per shot**, independently. Never ask the image generator for a storyboard, gallery, panel grid, montage or contact sheet; those words can themselves cause drift. Use only the target shot's action as the positive prompt; do not paste narrative paragraphs for all five shots into one prompt. Distinct camera/action requirements prevent near-duplicates. Preserve actual image bytes/hash for each return. **Automatically assign the V1 filename as specified in `../plotpickle-naming/SKILL.md` and carry it with the exact media and source ID throughout Save, Lock, Library and Studio handoffs.**
6. Inspect the actual image pixels against approved references and source **immediately**, then run `production_guard.py review`. If `DRIFTED`, preserve original, stamp only a review derivative with `drift_review.py`, exclude it and correct before attempting that position again. A failed retry must not silently advance the production address. `REVIEW_REQUIRED` or `UNKNOWN` are not usable. Status PASS alone is **awaiting creator approval**.
7. Present image(s) for creator review. For explicit approval/lock, retain exact candidate ID+SHA, then attempt the **real native PPF Save/Lock** using available guarded writer and independent readback. If writer lacks authenticated PPF/Library access, store only an approval receipt/independently verified bytes in the creator's private Library and report `NATIVE_PPF_LOCK_PENDING`, not success. Studio import is another independently verified step; never claim it because the files are in Library.
8. Show concise shot checklist and *exact next missing address*. Five requested frames are not complete until five separately created, verified and reviewed candidates exist. No public publication or paid provider calls without existing release/spend gates.

## Shot continuity preflight

For a continuity-configured PPF, call `studio_get_shot_continuity` with the current registered Studio shot number and exact `ppfSha256`. Use the returned address, source revision, screenplay links and entity IDs in the shot brief. Stop before generation when continuity is unresolved or any required reference is missing. Keep legacy projects on their existing source and reference checks when the receipt reports `configured: false`.

A verified reference in the receipt has been reopened from Studio. Pass the exact approved original to the image host and retain evidence of actual delivery. Keep visual review, creator approval, Save and Lock separate. Continuity resolution alone grants none of those states.

## Send approved originals to ChatGPT Images

1. Resolve the required visual roles from the shot card. Use the creator-authorized source revision to pin each approved asset/variation and SHA-256. For a matching Studio project, reopen `studio_get_reference_approvals` and check the project, source hash, approval scope, and saved/locked status. If Studio has only part of the reference set, use the matching canonical approval records from the selected source for the remaining roles.
2. In ChatGPT Work, materialize the original image files from the user's authorized Library or verified PPF media into the current workspace. Decode each file and match its SHA-256 to the pinned approval. Filenames alone are insufficient. Keep originals private and unchanged.
3. After preflight passes, invoke the built-in ChatGPT Images tool with the verified absolute paths in its `referenced_image_paths` input when the host exposes it. List only the images relevant to the shot and identify each role in the same order in the prompt. Use this route even if Studio approval readback already reports verified bytes. A successful readback is a source check. Record explicit input delivery only when the image request includes every required verified file and succeeds.
4. In a host that cannot pass file paths, use the exact originals attached in the current conversation only when the image tool can accept them explicitly and their identity matches the approved records. If that route is unavailable, stop at the same shot and identify the missing file or host capability. The creator can use the conversation composer's **Add from library** for an available original. A tool preview, link, contact sheet, filename, or description cannot substitute for the original inputs.
5. Check the output against those same originals and the screenplay. Successful input delivery does not guarantee visual continuity. Keep the output at review until the independent visual check and creator decision are complete.

## Delivery without distortion

- **Candidate status:** PASS/DRIFTED/REVIEW_REQUIRED/UNKNOWN, media byte/hash verification, creator approval, native PPF save, native PPF lock and Studio import are independent fields.
- **Resume:** persist Shot Truth Cards, original hash and source/visual reference pins in the user's existing Library/PPF; on the next conversation reopen them. Never bundle one user's story assets in this shared plugin.
- **No counterfeit completion:** an edited screenshot, contact-sheet crop, generic reference prompt or source citation cannot substitute for independently generated and inspected media.
- **No hidden automation:** complete the current authorized batch now or report the actual blocker. Do not promise background generation.

## Test / integration boundary

Offline Python `../plotpickle-truth-gate/scripts/test_production_guard.py` verifies preflight, wrong project/shot, missing source/ref bytes, montage prompts, duplicates, image decoding and false green states. Live Studio must separately add server-side checks defined in `../plotpickle-truth-gate/references/backend-enforcement-contract.v1.md`. Changing packaged skills does not update the deployed Studio MCP, Site UI or public plugin publication state.
