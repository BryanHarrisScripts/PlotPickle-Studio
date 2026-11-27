# Live Review / Editor

Release 0.8.47 uses the existing authenticated app, now named PlotPickle Studio, preserving its app/plugin ID and original transfer tools. Studio workspace: https://plotpickle-studio.avairis.chatgpt.site/studio . This is a genuine deployed server-backed workspace, not a screenshot or a browser-local draft. It can also render as an MCP App through `open_studio_review_editor`. The connected service may need a new chat to expose refreshed tools; never claim in-chat host acceptance from deployment alone.

## Scope and source

The existing creator's private workspace is The Third Bell source revision 10, Block 01 / Mini-Block 01: 25 exact byte/hash-verified storyboard WebPs, source-linked passages and three existing motion originals. Source PPF SHA is pinned in the view. Keep later Mini-Blocks and unrelated stories out of this bounded first implementation. Access is keyed server-side by the authenticated Site-scoped user ID; never package personal story data inside this distributed skills plugin.

## Human and headless parity

- `open_studio_review_editor`: opens the real review/editor app without writing.
- `studio_get_state`: returns source, shots, saved reviews, six-lane timeline and handoff issues.
- `studio_get_image`: exact registered WebP bytes and hash for one shot.
- `studio_apply_action`: exact-hash approve-lock, flag, unlock, edit-clip, add-cue or undo. Supply expected Studio revision and source PPF SHA. Review actions also require exact shot, media kind and media SHA. Unlock needs a reason.

The UI provides Previous/Next, 25-shot selector, still versus existing motion preview, Script/Prompt/Continuity/Audit evidence, four separate source statuses, Studio review status, timeline clip inspector, saved frame trim/move, cue markers, undo, saved-draft export and asset destination report with Library links. No drag feature is claimed.

## Persistence boundary

Writes use server object-store conditional ETag updates and independent object readback. A stale expected revision or competing save fails. No success status before a verified saved revision. Studio records approve and lock as one atomic review action anchored to actual media hash and passage IDs; these are Studio sidecar records, not native PPF Save/Lock changes. The source PPF's separately shown Saved/Locked statuses come from verified source revision 10. A review change marks matching editor clips for review, retaining the cut and originals. Audit entries survive undo; undo writes a new monotonically increasing revision.

Library PPF writeback, continuous provider synchronization, fresh frame-verified server renders are not implemented by this interface release. Exported Studio JSON is an editorial draft, not an approved PPF master. Route later rendering through the existing verified Produce workflow using actual Library media.

## Report truth

Three original Library transfers have verified byte/hash evidence in the 2026-11-10 handoff package. Existing provider-original video playback is a preview; it is not the conformed 24fps derivative. Source image lineage differs from the registered still hashes and character/world continuity remains unresolved. Approval does not automatically clear provenance. The report stays blocked and preserves already edited clips. One older fal clip remains unassigned; completeness covers only the dated saved-video catalogue snapshot. BUZZ and Modem remain on hold; Suno integration remains pending.

## Verification

Source tests cover per-user authorization, exact media/hash matching, source and revision guards, concurrent writes, independent save readback, trim boundaries, overlap rejection, six lanes, undo and retained cut. Report deployment, automated acceptance, browser UI checks and ChatGPT MCP App acceptance separately. An owner sign-in page is proof of protection, not proof of authenticated live persistence.

## Public access and personal workspace isolation (v0.8.47)

Public landing: https://plotpickle-studio.avairis.chatgpt.site/ . Every user can access the web surface with ChatGPT sign-in, without installing the private plugin. Web accessibility does not imply public ChatGPT plugin publication. Preserve plugin sharing; public directory installation requires its own supported publication workflow. The same Site, App, plugin and storage binding identities are retained across the URL rename.

The Third Bell seed is available ONLY to its original creator account. Every other signed-in user starts with an empty private workspace; the image endpoint must read that user's current state and must never fall back to creator seed media. Server storage keys derive exclusively from the authenticated user ID, never request-supplied user IDs or project owners.

The web import panel and `studio_import_project` accept an actual extracted portable PPF JSON (at most 1 MiB) and 1–25 corresponding original WebPs (at most 6 MiB in the browser). Optional Block/Mini-Block selection defaults to the first source mapping. The server computes the source hash, checks registered media hashes and WebP container integrity, requires screenplay passage links, saves only user-scoped media, revision-guards the current workspace replacement and independently reopens it. Previous workspace state is archived, and PPF source bytes remain unchanged. Imported PPF lock statuses are Unknown until separately audited; do not infer them from initial registration. The browser decodes imported images, but the server's import receipt certifies hashes and container checks, not an independent full image decode.

New imports open image review and an empty six-lane timeline for cue markers. Generic video import/binding is not added by this release; the creator's existing three-shot motion draft is preserved. Do not claim other users received those videos or a ready-to-render movie. The current web import works on one active Mini-Block per private workspace.

Tests include independent user fixtures: a second user can import, reopen and review their own source while a third user cannot read its images or reviews. Neither receives the original creator's seed. Anonymous landing contains no personal project data; workspace and APIs require sign-in. Live second-account browser acceptance is separate from fixture isolation tests.

## HOME, Library and resubmission — v0.8.48 supersedes the browser import panel

Manual PPF/WebP file inputs have been removed from the hosted review/editor. HOME (https://plotpickle-studio.avairis.chatgpt.site/home) contains the sole project-opening link, Open ChatGPT Library. A creator can also drop a PPF or script directly into chat with Elara. Four approved HOME cards are retained; conversational actions are active only with a real host message bridge. Standalone users can open the Library and the existing PlotPickle chat entry.

`open_studio_home` is a read-only HOME tool and global/thread MCP App entrypoint. HOME navigation and Continue Review/Editor preserve the active source, selected shot and saved cut. `studio_import_project` remains an agent-side byte-validated adapter, not an instruction to ask users for manual browser file imports. It still loads one scoped Mini-Block; do not claim it reconciles an entire story or all provider files.

`studio_apply_action(operation='resubmit')` requires current Studio revision, source PPF SHA, exact shot/kind/media SHA and a reason. It saves an awaiting-Elara-review request with screenplay links, retains source PPF and the cut, marks affected clips for review, records generationSubmitted=false and rejects an identical pending request. A Studio-locked review must first be unlocked with a reason. Undo restores the previous pending-request list while retaining audit history.

In a supported MCP App host, the user-click Resubmit to Elara action uses the real host message bridge to request Elara's review. In a standalone browser it saves the request and asks the creator to continue in PlotPickle chat; it does not fabricate a sent message, a generation job or a new image. Elara reads the saved request and proposes a correction before separately authorized provider submission.

The Library link is navigation only. Native chat-side Library tools can resolve a user-selected project and verify its linked files, but this Site has no verified authorized Library picker/connector bridge in the available tool surface. Automatic selection → all project files loaded remains pending. Loaded counts in HOME describe the current bounded draft, not complete Library synchronization.


## v2.0.18 — audio candidate locking and sound-track attachment

Supersedes earlier unsupported-audio statements above. Use `../../plotpickle-editor/references/audio-workflow.md`. Hosted Studio now imports exact MP3/PCM WAV candidates with source/shot/passage/BEAT links, verifies saved hashes, records creator lock as human approval, and attaches locked versions to Dialogue, Foley, Ambience or Music. Playback, gain/mute/trim, detach and undo use authenticated revision-guarded state. Render plans include exact audio hashes/settings, and the bundled media-runtime adapter mixes at 48 kHz with full-decode receipts. Server render attachment checks a bound mix has the expected AAC audio stream; server execution of ffmpeg is not claimed. Library loading remains a chat-side handoff. No audio candidate is approved by deployment.
