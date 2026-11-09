---
name: plotpickle-review
version: 0.8.35
summary: Review and source-pin individual PlotPickle storyboard images in ChatGPT, with honest separation of human approval, Save, Lock, Unlock and regeneration.
---

# PlotPickle Studio — Storyboard Review

When the creator asks to open Review or approve, regenerate, lock or unlock a storyboard image, preserve HOME/REEL/ONCE and use the current ChatGPT conversation as the primary entry. The optional hosted MCP Apps sidebar is NOT automatically available merely because this skill is installed. Never claim a local HTML preview is the official ChatGPT sidebar.

## Source-backed loading

Locate the latest authorized saved PPF in current ChatGPT Project files or personal Library, plus any accompanying native portable ZIP/images. Pin the exact project ID, revision and raw SHA-256; check it against the canonical inspector when available. Inspect stored shot addresses and exact image-to-passage mappings. Read actual image bytes and verify SHA-256, file size, dimensions, and decoded image; do not use a contact sheet as proof that a particular source image exists. Keep image originality, full-resolution quality, candidate selection, native Save/Lock and human approval separate.

Display the 25-position Mini-Block with source-linked candidate previews where possible and clearly distinguish the actual 25 original portable images from newer ChatGPT-generated images that have not yet been imported. Offer one active shot's Approve, Regenerate, Lock and Unlock decisions with their actual conditions. A disabled/blocked operation must say why. Show any pending action as a review draft until committed.

## User actions

- Approve: require the author's explicit selection of a specific image candidate; record the exact shot address, source passage references, candidate ID (if known), media SHA-256, project ID, revision and PPF SHA-256. The human visual review is not automatically a native Save or Lock.
- Regenerate: preserve the selected source and prompt and record a revision reason. Request or perform image creation only when explicitly requested by the creator; never overwrite the locked image, generate on a stale source, or spend fal/Suno credits without separate authorization. The replacement remains a new candidate requiring its own review.
- Save: verify the actual selected media and source relationship before updating an exported project. Use the installed/native `read-plotpickle-project/scripts/default-save-lock.py` or source-governed workflow where present, with current project revision/hash guard; reopen and verify the saved marker. A queued request or browser-only change is not Save.
- Lock: only after a successful Save, native readback, and current decoded media verification; use the native source project operation, persist a new owner-scoped project snapshot, then independently reopen PPF and media. Never claim native Lock from a chat approval, sidecar event or disabled preview button.
- Unlock: require a currently saved and locked source candidate plus a human reason; source-guard and commit a new revision, then reopen to confirm. This retains prior candidates and audit history. Regeneration of a locked shot requires Unlock first.

For a true commit, all mutations need an owner-authorized durable file writer and compare-and-swap against the current project version. If current tools cannot perform native file-level Save/Lock and independent post-write readback, prepare a private structured `plotpickle.review-draft.v1` event instead, explicitly marked `REVIEW_DRAFT_NOT_PPF_COMMITTED`. Put it in the creator's authorized Project/Library only with an actual successful file operation; never change the original PPF on speculative authority. Do not invent missing reader, write, upload, or image-generation connections.

Do not assume earlier conversational approvals selected a specific existing PPF image. Older PPF concept crops and newer ChatGPT renders are different candidates. Present the selection to the author.

## Current reviewed reference milestone

A privately authorized The Third Bell project ZIP can be read in ChatGPT Library. A verified recovery pass found 25 original 1280×720 WebP shots matching the source PPF revision 0 and image hashes. This establishes byte recovery only; the initial PPF saved/locked flags are false, and the package's original concept crops are distinct from later ChatGPT image candidates. Use the actual latest files rather than treating this historical receipt as always current. The portable review HTML can collect local approval and regeneration requests for export, but it is not a native write endpoint, authenticated MCP Apps sidebar, or a file-service synchronization mechanism.

If author asks where to find the sidebar, state that the official hosted entrypoint needs deployment and authenticated owner-scoped project loading. The in-chat review workflow can operate today; do not introduce a mandatory Windows installation or second storage database.
