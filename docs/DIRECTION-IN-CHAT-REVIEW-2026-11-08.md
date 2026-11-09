# Direction change — Retire standalone sidebar, use ChatGPT-native Review (2026-11-08)

Owner decision: "scrap the current sidebar" after phone testing and observing that HOME and fal ChatGPT surfaces were much faster and simpler than a separately hosted Studio app. This **supersedes** sidebar hosting / global entrypoint implementation work in earlier Studio direction and acceptance documents; those documents remain historical, not release requirements.

## Supported user path

HOME → Storyboard → REEL or ONCE → Select saved story → Review selected shot.

The selected storyboard shot is displayed inside the current ChatGPT conversation using native response components where supported: one actual image candidate, provenance, shot number/beat, previous/next controls, independent Human Approved / PPF Saved / PPF Locked / Media Verified indicators, and contextual Approve / Regenerate / Save / Lock / Unlock actions. Do not invent or deploy an iframe, standalone webpage, custom global sidebar, cloud-computer service, new user login, or third-party hosting merely to create this presentation.

A native button must send a real follow-up turn and be processed against the current authorized project. Widget-local visual state is not durable story state. There is no guaranteed fixed, shipped component hosted by the plugin's SKILL.md; the ChatGPT response renderer decides how to present controls, with compact text fallback. The existing Story Explorer source reader, inline presentation rules and native PPF operations are sufficient to begin.

## Save/Lock and file truth remain real

- Work from a saved author-owned PPF and portable assets, pinned by project ID, revision, SHA and exact shot/candidate IDs. Distinguish original ZIP crops, independently rendered ChatGPT images, and visual review.
- For actual mutations use existing `skills/read-plotpickle-project/scripts/default-save-lock.py` / `image-operations.py`, independent media verification and canonical readback. The same headless scripts can be invoked from a ChatGPT tool execution environment where source files are accessible.
- Persist versioned resulting PPF + media in the user's authorized ChatGPT Library/Project with actual file tools and compare-and-swap version guard when editing an existing file. Reopen and verify uploaded bytes; otherwise report a review draft and do NOT claim Save/Lock.
- No new project database, no compulsory GitHub for creators, no cloud service to host review buttons, no fal charges merely to open Review.
- Historical The Third Bell revision 0 original source had 25 hash-verified 1280×720 WebP images. Isolated Shot 01 Save→Lock→Unlock→Relock Library roundtrips were verified; this is NOT the same as changing the creator's canonical story without approval.

## Retirement

The unused `skills/plotpickle-studio/pilot/` project, standalone HTML, HTTP/MCP server and global sidebar metadata are removed from the active source and existing private plugin in the next guarded update. Their Git commit history is available for reference; no separate deployed app exists to terminate or migrate. The pure source native PPF scripts, real creative files, project snapshots, HOME and in-chat Story Explorer remain.

## Acceptance

1. GitHub source checks pass after removing pilot-only tests/requirements; Python source review and Save/Lock tests replace them.
2. The guarded update affects the *existing* private plugin only. Both manifests show 0.8.36 and the legacy pilot paths are absent; the private The Third Bell seed and canonical PPF reader remain.
3. Test HOME, Storyboard, The Third Bell shot review in ChatGPT (phone); verify buttons route to real conversational operations or decline with truthful blocker.
4. For a real requested change, independently re-read a fresh authorized PPF and media from Library/Project before reporting durable success. Native in-chat rendering never itself proves a write.

Technical distinction: fal's in-chat UI uses its own MCP tools/server and authenticates its account; PlotPickle can use ChatGPT's own response controls for single-shot review, so no separate custom MCP app is needed. Actual cross-chat persistence still requires an authorized file write and readback.
