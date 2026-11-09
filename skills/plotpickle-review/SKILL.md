---
name: plotpickle-review
version: 0.8.36
description: Review real source-backed PlotPickle storyboard images in ChatGPT and route explicit approval, Save, Lock, Unlock and regeneration through verified project operations.
---

# PlotPickle Studio — ChatGPT-native Storyboard Review

The owner retired the standalone sidebar. When asked to Review or approve, regenerate, lock or unlock an image, keep HOME, REEL and ONCE as the fast entry points. Display a compact Review panel inside a normal ChatGPT reply where native response controls are supported; otherwise offer concise conversational actions. Do not open an external app, iframe or hosted sidebar, and do not require credentials, a Windows installation or a new project store. ChatGPT response controls are rendered by the host, not shipped from this skill as a fixed JavaScript app.

## Source and evidence

Use current authorized saved PPF from the user's ChatGPT Project or Library and its corresponding portable media. Pin project ID, revision, SHA-256, canonical shot address and exact candidate. Run the existing canonical inspector when available; independently verify each image's actual bytes, content hash, dimensions and decoded content, not merely filenames or contact sheets. Identify original PPF concept crops separately from later ChatGPT-generated candidate images. Show the selected image and screenplay source if available, and clearly separate four values: Human Approved, PPF Saved, PPF Locked and Media Verified. Unknown is not true.

## Native in-chat actions

A native button may select another shot locally, but Approve, Regenerate, Save, Lock and Unlock MUST initiate an explicit conversational tool-backed action, not change a badge in UI state and falsely claim a PPF write. If a control cannot perform the real operation, use a follow-up turn explaining the blocked step. No fake buttons or claims that widget state is persistent.

Approve requires an explicit choice of one exact image variation, recorded with source passage references and media SHA. An author's visual approval is not proof of native PPF Save/Lock. If initial auto Save→Lock is enabled, run the real source workflow and show separate readback confirmations. Regenerate requires a source-bound shot and revision reason, preserves prior candidates, and requires Unlock first for a locked image. ChatGPT image creation happens only on explicit instruction; fal/Suno credits require their own per-job permission.

Save requires a current source pin and verified image bytes. Invoke the installed read-plotpickle-project default-save-lock or image-operations source workflow, produce a new PPF snapshot, reopen it and confirm saved markers. Lock only after Save readback and actual media validation, with new revision and independent readback. Unlock requires a previously saved and locked specific candidate plus reason; write a new revision, preserve audit history, reopen it and verify the new state. Never overwrite a creator's canonical PPF or newest Library file using an unverified expected version. Use actual available Library/Project file tools with version guards; when no secure write is possible return REVIEW_DRAFT_NOT_PPF_COMMITTED, not a success badge.

Show resulting project revision and hash, saved/locked states and output location only after independently checking written bytes. Keep source truth and image approval independent.

## The Third Bell

The original private PPF rev 0 had 25 individually hash-verified images; this is not proof the later generated variants are imported or final-approved. Prior Shot 01 Save→Lock→Unlock→Relock tests in isolated Library snapshots do not update the canonical project. Reopen current project and let the author choose the exact candidate before committing.

The standalone plotpickle-studio/pilot sidebar was retired and is not installed. Native Review requires no separate hosted MCP App, although persistent file writes still require the real authenticated ChatGPT file service and readback. Never claim otherwise.
