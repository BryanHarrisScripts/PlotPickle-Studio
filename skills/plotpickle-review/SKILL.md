---
name: plotpickle-review
version: 0.8.36
summary: ChatGPT-native, source-checked storyboard review. Select and inspect actual images; approve, regenerate, Save, Lock and Unlock via explicit conversational turns and verified PPF readback, with no separate sidebar or MCP Apps host.
---

# PlotPickle Studio — in-chat Storyboard Review

The user explicitly retired the standalone Studio sidebar on November 8, 2026. HOME remains four fast conversational choices. From Storyboard > REEL or ONCE > saved story > Review, present one small **native ChatGPT conversation panel** showing one selected shot, its actual candidate image (only if accessible), provenance, source evidence and separate human approval / saved / locked / media verification states. A compact previous/next shot selector may be interactive in the message if the ChatGPT host supports it. Avoid a separate sidebar, iframe, locally hosted HTML, app server, API-login wizard, Windows install or developer-mode configuration.

Use the host's native visual and interaction components when supported; plain conversational commands are the fallback. UI selection is ephemeral. An action control **must issue an explicit new conversational turn** or execute a real accessible supported tool action; never merely change a local badge to “Saved” or “Locked.” Native controls are chosen by the ChatGPT response renderer, not shipped JavaScript from this skill. If the host cannot present them, show concise actionable text choices.

## Read the real project first

Prefer current authorized ChatGPT Project file(s), otherwise the creator's Library. Find the exact latest saved PPF and portable assets, not just a previous chat claim. Pin project ID, revision, SHA-256 and canonical shot coordinates with the bundled `../read-plotpickle-project/scripts/inspect-project.mjs` when available. Use `storyboard-review.py` and actual ZIP/image bytes to confirm content hash, size and decoded dimensions. A contact sheet, fal URL, prior generation or prior verbal “approved” does NOT establish that a specific PPF image is selected or saved. Keep newer ChatGPT-generated candidate images distinct from PPF concept renders. Never expose private story bytes in public plugin source.

For each shot, show one image, its exact candidate identity and where it came from, the relevant screenplay action, and four independent statuses: **Human review**, **PPF Saved**, **PPF Locked**, **Media verified**. If no image can be read, say so. For 25-shot navigation, maintain the source pin in any follow-up, and refresh it immediately after a successful write.

## Actions and real persistence

- **Approve**: author selects the exact candidate; record an explicit human review decision with artifact ID/media SHA and pinned PPF source. It is not proof of Save or Lock until the durable source snapshot is written and read back. Where an authorized native Save->Lock path exists and the creator has chosen initial auto-lock, perform that workflow on that selected image, with separate receipts.
- **Regenerate**: require an exact shot and reason, preserve the current candidate and prompt, and ask ChatGPT image generation for a new distinct candidate only when requested. Regeneration never overwrites a locked image: unlock first. No automatic paid fal/Suno action.
- **Save**: use the existing `../read-plotpickle-project/scripts/default-save-lock.py` / `image-operations.py` guarded PPF workflow after current identity and media validation. Write a new version, independently reopen, and confirm Save marker. Save precedes Lock.
- **Lock**: only on a verified, saved and selected image. Commit a new revision with the native operation, then reopen and confirm both PPF flags and image bytes. Never call an approval, HTML change, a draft sidecar or a display state a Lock.
- **Unlock**: require an explicitly selected currently locked candidate and review reason. Commit its new PPF revision, retain old candidate/history, and independently reopen to confirm Unlock. A new replacement is another candidate and must be saved/locked separately.
- **Retain across conversations**: use actual authorized Library / ChatGPT Project backing files and available file upload/write tools. Avoid a second story database. If updating an existing Library file, use its actual stable file ID and expected version for compare-and-swap; do not overwrite the source on guesses. When such a write cannot be performed, output a plainly labelled `REVIEW_DRAFT_NOT_PPF_COMMITTED` and do not claim persistence.

For every successful write, show the new project revision and source SHA; observed saved/locked values; image integrity status; where the new private project snapshot was stored; and whether the Library/Project copy was re-fetched and checked. Avoid automatic creative approval based on image hashes alone.

## The Third Bell acceptance

The creator's private Library previously contained a real The Third Bell PPF revision 0 with 25 individually hash-verified 1280×720 images and original concept crops. There was also a separate test of Shot 01 Save→Lock→Unlock→Relock in **isolated project copies** stored in a private Library folder. Neither test implies that the canonical project was silently updated or that newly generated ChatGPT images were imported. Reopen actual current files and let the creator select between distinct candidates. Preserve all original story material; no optional graphical sidebar is required.

Only claim a native in-chat review display when one was actually rendered. The old `plotpickle-studio/pilot` standalone sidebar was retired, not secretly deployed. Never request a separate hosted MCP app simply to show review images.
