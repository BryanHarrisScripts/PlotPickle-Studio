---
name: plotpickle-editor
summary: Source-linked, non-destructive PlotPickle film timeline editing in ChatGPT with an optional local Windows FFmpeg media worker. Supports interactive timeline planning, verified video intake, and honest local-connection states.
description: Use for Open Editor, timeline, cut, trim, dialogue/foley/music cues, preview, undo and render requests. Do not infer Windows connection or claim unsupported audio mixing.
---

# PlotPickle Creative Editor — Phase 1 + Audio Tracks (v0.8.31)

This is **one on-demand creative interface**, not a new factory. Route **HOME → Storyboard → Editor** or **Storyboard → Produce → Edit** here. Keep SCRIPT/PLAYBACK/INSPECTOR layout and a six-lane timeline (Video, Dialogue, Action, Foley, Ambience, Music), inspired by the approved editing reference. Natural language commands such as "move Shot 01 six frames earlier", "insert an ocean ambience cue", "inspect dialogue" and "undo" translate into a typed draft edit; do not claim a local file was changed unless a confirmed write/readback exists.

## Truth and connection states

- **ChatGPT in-chat editing:** when host UI supports native interactive controls, show a timeline representation grounded in the current project and preview assets; if no host binding can persist edit actions, keep it as *interactive preview only*, offer a source-bound patch for authorized import, and say that the local connection is not configured. The plugin bundle contains no persistent hosted editor App, remote HTML deployment or privileged localhost access just because these files exist.
- **Local editor prototype:** `windows/editor_server.py` (Python 3.11+, FFmpeg on PATH) serves a working browser UI at `http://127.0.0.1:8765/` and its verified on-demand local media receiver. This runs only after a user installs/runs the Windows starter; never silently install or execute on the user's PC from chat. Code is included in the plugin and in the separate owner Windows starter ZIP. No public listener, tunnel or cloud file storage is part of Phase 1.
- **Fal:** use the existing `../plotpickle-fal-production/SKILL.md` for approval, one generation, result URL and receipt. A separate local intake is no new paid video generation. A CDN result can be transferred to Windows by the local receiver, without needing ChatGPT's code sandbox to fetch it, once the Windows receiver is launched and seed/reference is present.
- **Windows connection not yet verified:** the legacy Factory tunnel cannot accept arbitrary clip payloads. A dedicated authenticated outbound editor-action bridge is still required for direct commands from ChatGPT to a local Windows process. Do not mark it operational or promise in-chat preview can stream the Windows-local MP4.

## Supported local Phase 1 operations

1. Read a user-provided current screenplay/PPF and map selected passage and shot coordinates; do not rely on memory for the latest revision. The owner test seed for The Third Bell was exported separately without native changes.
2. Start the local editor *on Windows* with the `Start-PlotPickle-Editor.cmd` file from the owner starter ZIP. Default data location is under `%LOCALAPPDATA%\PlotPickle\Projects\The Third Bell\Editor` (or `PLOTPICKLE_EDITOR_ROOT` when explicitly configured); reuse an old Videos-based editor draft only if a real `editor-draft.json` exists there and the app opens a localhost browser. It does not require GitHub, Cloudflare, or credential entry.
3. **Import fal Shot 01**: only a previously recorded completed `https://v3b.fal.media/files/...mp4` source from the seed is eligible. The receiver downloads, verifies original bytes and full decode, makes a 24 fps 72-frame conform, checks the final full decode/SHA, and retains original + conformed files. If fal URL is expired or unavailable, report blocked; do not regenerate or substitute media.
4. 
4. Select a clip or script cue, drag its start position in three-frame increments, edit labels/start/duration, add and remove dialogue/Foley/ambience/music cues, attach WAV stems, adjust gain/mute, and undo. An audio cue can also attach a vetted local WAV, be moved or trimmed, muted, and mixed at 48 kHz. The local draft writes revisions with optimistic concurrency and keeps native PPF unchanged. Clip drag and inspector Save require a real local browser UI.
5. **Render Draft** (phase 1): renders one verified video clip from 0:00 to a draft MP4 with a silent 48 kHz audio reference track, 24 fps, exact frame count, and a verification receipt/status. In v0.8.31 the local editor DOES mix bounded WAV sources on the Dialogue, Foley, Ambience and Music lanes into a verified 48 kHz audio stream. The two pre-seeded Shot 01 ocean/gull sounds are clearly labeled synthetic sound-design demo clips (not real environmental recordings); clip selection supports frame start/duration, gain in dB, mute, local WAV replacement, revisioned Save and Undo. The renderer builds one picture + sound MP4, previews that verified render and offers download. It does *not* yet perform dialogue generation, lip-sync, render multi-shot concatenations or mark an approved master. Present those as subsequent, separately gated milestones.

## Next engineering handoff

The bounded editor MCP bridge should expose `status`, `getTimeline`, `applyPatch`, `ingestCompletedFalClip` and `exportDraft` via a secure, outbound local agent. The editor is then usable within a real ChatGPT UI and can stream previews by authorized host media delivery. No browser CORS workaround or direct ChatGPT-to-localhost access is valid. See `references/editor-contract.md` for gate rules and security. Test local core with `python -m unittest test_editor.py`, and verify Windows + real fal CDN intake + hosted ChatGPT editor separately before calling the workflow end to end.

## Windows launcher repair (v0.8.30)

The v0.8.28 Windows CMD selected `py -3`, which could resolve to Python 3.8 even though Python 3.11+ is required. It also assumed `%USERPROFILE%\Videos` exists; on redirected Windows profiles it may not. The corrected launcher selects a verified Python 3.11-3.14 interpreter, prefers `%LOCALAPPDATA%\PlotPickle\Projects\The Third Bell\Editor`, preserves an existing legacy draft if found, supports `PLOTPICKLE_EDITOR_ROOT` for alternate storage, and fails with an actionable message rather than a Python traceback. Do not claim installation, startup or host acceptance until actually observed on the Windows machine.

## Video preview repair (v0.8.30)

The v0.8.29 `public_state` intentionally concealed Windows media path values,
while `app.js` erroneously read `project.media[id].path.split('/')`, interrupting
all toolbar UI after the first verified 24-fps media import. The local API now
provides `previewAvailable` and a same-origin `previewUrl` ONLY for a real verified
media file inside the approved media vault. The browser must use this returned
URL, never invent Windows paths or ask to regenerate an existing fal result.
Existing imported Shot 01 and draft revisions remain intact. If media is missing,
show its status without crashing. Close the previous Python server before copying
updated files, and hard-refresh the browser if an old script is cached. The
standalone Windows browser has not yet been replaced with a fully bridged ChatGPT
editor. Audio cues still contain no synthesized/mixed sound.


## Audio acceptance (v0.8.31)

The existing local Windows starter is updated in place. No duplicate desktop service or new port is required. Startup migration adds two demo audio WAVs (deterministically synthesized ocean hiss and stylized gull calls) to the existing *local editor draft* under `<editor root>/audio/`. It does not overwrite the user's previous Shot 01 conformed video, earlier rendered MP4s, source screenplay, revision history, or locked PPF. Existing custom audio bindings and edited gains are preserved. No remote model or credit spend.

For one approved clip, audio clips reference local `audioAssets` records by stable ID; sample-based placements are exactly 2,000 samples per frame at 48 kHz / 24 fps. Unbound cue markers never silently acquire sound or count toward the number of mixed clips. WAV attachment is limited to a bounded 32 MiB, independently probed and normalized to 48k stereo PCM locally. Local POSTs require the exact loopback Origin and existing action header; the browser never receives raw filesystem paths. All assets are hashed on retrieval; missing or changed media blocks rendering. The renderer mixes and limits audio into AAC+MP4, checks 24 fps, 72-frame output where requested, decodes the result and records a mix receipt and noncanonical preview URL. A subsequent timeline edit invalidates the render-current status without deleting the original output. A muted or empty audio lane retains a silent 48k reference for compatibility. No lip-sync, AI voice generation or professional Foley library is claimed.

Windows user flow: close editor → replace starter files → relaunch → select Ocean hush / Distant gulls → adjust gain and mute → Render Picture + Sound → play the result → Download Mix. Use Attach WAV on a selected cue to replace the demo sound without changing the PPF. If no WAV is available, cues are visible markers but produce no sound. A fully embedded hosted ChatGPT timeline and secure live chat-to-Windows edits remain a separate integration gate; localhost is not reachable from ChatGPT by assumption.

Tests: `python -m unittest test_editor.py test_audio.py` and `node test_browser_preview.cjs` run locally; separately verify on the owner's Windows host and with the actual existing fal video before claiming end-to-end acceptance.
