---
name: plotpickle-produce
description: "ChatGPT-native PlotPickle Produce and six-track 24fps Timeline Editor, with source-verified media, non-destructive draft edits, original fal transfer handoff and no mandatory Windows application."
---
## Live Review / Editor — v0.8.48

For the live review/editor interface, use `../plotpickle-review/references/live-review-editor.md` before legacy prototype guidance below. The deployed existing PlotPickle Transfer app now serves a real MCP App and signed-in `/studio` page with private per-user workspaces, backed by server-persisted Studio drafts. Do not describe it as a native Library PPF writer. Opening does not approve anything. When the new tools have not refreshed in this chat, link the authenticated workspace and report host tool availability separately.



# PlotPickle Studio — Produce and Timeline Editor (v0.8.44)

Route Storyboard → REEL/ONCE → Produce → Timeline Editor here. The existing PlotPickle HOME, Storyboard, REEL/ONCE, source-authored 24-Block Story Map, Mini-Block shot grid, official graphic-novel reader, approvals, and Skin V1 layouts are unchanged. This release is an on-demand, ChatGPT-native workflow: no mandatory Windows app, local service, GitHub CI, or local tunnel. A standalone runtime for the complete six-track graphical editor is not automatically installed by a skill-only release. Render a live in-chat timeline when the host supports interaction; otherwise use revision-safe JSON patches and file-backed media, never pretend that a displayed preview wrote the project.

## First: recover actual media and approval truth

Read `../read-plotpickle-project/SKILL.md`, `../plotpickle-approval/SKILL.md`, and `references/media-library-inventory.md`. Reopen the latest accessible personal Library project and approval receipts, not conversational memory alone. Folder convention: `ChatGPT Library /PlotPickle/Stories/<Story>/Verified Locked`, `Approved - Registration Pending`, `Review Pending`, `Video Originals - Review Pending`, `Production Drafts`; story-specific folders may vary. Copies of existing sources must not replace originals, overwrite PPF or collapse the four independent statuses Human Approved, PPF Saved, PPF Locked, Media Verified. An approved 25-panel overview is not automatically 25 native-locked shot images. Source associations require exact shot coordinates, project identity, rev/SHA and a true media hash.

A recovered 2026-11-10 inventory currently exists in `Library /PlotPickle/Stories/PlotPickle-Media-Recovery-Inventory-2026-11-10.json`; it is a timestamped evidence snapshot, NOT a standing live catalog. The Third Bell revision010 package verified B01/M01 25 native locked images and four locked design refs; B02/M01 creative board selected but 0/25 native shot registrations verified. The Third Bell has an already-Library-available 8,495,321-byte, 1920x1080, 30fps/90-frame Shot01 original, independently locally hashed and decoded; its newly organized copy has not yet passed independent Library copied-byte readback. The connected fal account exposes three completed Nov 9 Wan motion videos plus one Nov 8 older generation; do not treat their URLs as durable originals in ChatGPT Library. Video approval and native PPF registration are separate. The 9-second hybrid animatic uses only Shot01 original video and still holds for shots 2–3, not three completed transferred originals.

## Transfer of existing fal output — don't regenerate

`mcp__PlotPickle_Transfer__check_transfer_connection` confirms service authentication only. For exact known fal URL, original expected byte count and source-backed story/shot call `mcp__PlotPickle_Transfer__prepare_fal_library_import` and hand off its user-click import widget. It does NOT itself save bytes. Creator must trigger upload; independent Library readback must verify file ID, size and SHA-256 before reporting 'transferred'. Use the existing fal `search_assets` / request-history IDs to locate existing outputs. Never spend credits to replace a completed clip solely because transport is blocked. Native PPF Save/Lock unchanged by transfer. If transfer cannot be verified, mark `remote-original-pending-transfer` and keep the source link and receipt.

## Twenty-four fps media and timeline

Every editorial frame uses 24 fps; one 3-second position occupies 72 frames. A Motion Span may group 1–5 consecutive positions (72–360 frames). Preserve original fal video bytes and distinguish provider fps/duration from conformed media; never claim mere metadata is decoded/verified. Probe, fully decode, conform to exact 24fps/expected frames, fully decode again, hash both originals and derivatives. Use `scripts/produce_editor.py` when the execution runtime has Python 3.11+, FFmpeg and ffprobe. The script supports `conform`, `init`, `validate`, revision-checked `edit` (move/trim/mute/add-cue/undo), and `render` of a draft MP4 with receipt. No external network/provider calls and no native PPF writes. Source media must be present as actual local bytes, supplied from authorized ChatGPT Library materialization; no magic fetch of remote MP4 from Python. The six lanes in fixed order: Video, Dialogue, Action, Foley, Ambience, Music. Action holds editorial markers; Dialogue/Foley/Ambience/Music can bind verified local WAV stems and mix to 48 kHz stereo. Empty audio lanes yield silent reference, not claimed performed audio.

When no live in-chat editor action bridge exists, show a clearly marked in-chat timeline planning surface; edits become a source-pinned, optimistic-revision sidecar and require real Library save/readback. The `editor-project-v1.json` saved earlier is not itself proof of imported video; use actual validated draft. Native PPF/save-lock remain untouched. An approved rough cut requires later explicit film review and native acceptance, not just an FFmpeg success.

## Acceptance and honest status

Report separate statuses for 1) fal generation, 2) original Library transfer plus byte/SHA readback, 3) 24fps full decode, 4) six-track source/patch revision, 5) animatic and rough-cut render, 6) creative approval and PPF Save/Lock. The Third Bell starting gate is 3-shot, 9 seconds, 216 frames; only Shot 01 original currently has verifiable Library bytes in this workspace. Do not describe the entire film, Block 02, Mini-Block 03, Brotherly Love or Afterglow as video-complete based on historic chat requests.

The portable helper is a documented offline tool included to make ChatGPT execution reproducible. It is not a perpetual hosted production service, does not install Windows code, and never takes provider payment. Verify actual host available tools before claiming live authoring, Library upload, UI persistence or provider transport is connected. Keep prior approved creative works and story sources intact.


## Check Handoff before editor use

Read `../plotpickle-assets/references/asset-handoff.md`; use its source-pinned reconciliation report before promoting a clip to ready. Show which source and Library version each timeline clip uses, missing transfers, submitted-image hash discrepancies, unresolved visual reviews and project registration. Preserve the cut when an image changes and flag affected clips instead of silently replacing them. Newer actual saved receipts override the historical recovery snapshot above; never repeat old transfer blockers after verified newer transfers. Revision-checked file edits remain distinct from a live persistent editor UI.


## HOME and conversational intake (v0.8.48)

Open existing projects through HOME → ChatGPT Library, using the current selection and real linked bytes. Do not request manual PPF/WebP uploads in the review/editor surface. A PPF or screenplay dropped directly into chat goes to Elara for inspection and the existing source-backed development workflow. Review offers Approve and Lock, Unlock and Resubmit to Elara. Resubmit is a saved source-pinned revision request, never proof of paid generation. See `../plotpickle-review/references/live-review-editor.md` for host bridge limits.


## v2.0.18 audio integration

For movie dialogue, Foley, ambience and music, use `../plotpickle-editor/references/audio-workflow.md`. Original MP3/PCM WAV candidates can be imported with exact-byte/full-decode evidence, independently reopened, creator-locked (lock includes approval), attached to the four sound tracks and included in a verified 48-kHz mix using the ChatGPT media runtime. Read the actual current Studio state; do not infer candidate approval, Library ingestion or complete film loading from this release. Action remains a marker lane. Native PPF writeback remains separate.
