---
name: plotpickle-chat-first
description: Resume an existing PlotPickle REEL or ONCE story inside ChatGPT, verify a real saved PPF and portable media files, and show one practical next step without imposing a new sidebar, app, storage account, or paid action.
---

# PlotPickle Studio — Continue My Story (v0.8.34)

The creator's existing ChatGPT conversation and phone-tested HOME / Elara / Learn / Storyboard / Connected Services navigation are the primary interface. REEL and ONCE are entrances to the SAME existing PPF story engine. Do not introduce a mandatory graphical sidebar, new app, install, login, GitHub repository, or provider setup to continue a story. Preserve all existing 81 learning lessons, Character and World Builder, visual assets, motion, Suno, fal, editor, posters and share pathways.

On Continue Film, Reopen, Your Stories, or "what's next":

1. Prefer the actual authorized latest saved PPF in the current ChatGPT Project, attached conversation files or creator Library. Do not treat memory, a project title, an old rendering or a UI card as proof of current saved state. If no source is accessible, say "No saved project loaded" and continue helping with the idea or request a file when essential.
2. Pin source identity / revision / raw SHA-256 using `../read-plotpickle-project/scripts/inspect-project.mjs`, when it is executable. A raw JSON preview or ZIP audit is NOT a substitute for a native reader acceptance. Wrong project ID, stale revision or changed SHA fails closed.
3. When the matching portable asset ZIP is available, independently check image variations against `assetRegistry.assets[*].variations[*].portablePath`, `bytes`, `contentHash` and signatures with `../plotpickle-story-flow/scripts/verify-portable-package.py`. The verifier streams ZIP members without extracting files or modifying project media. Verified ZIP image bytes do not prove a shot's Save / Lock / accepted or that an MP4 is recovered. Keep the source PPF and ZIP private.
4. For a named Act/Block/Mini-Block use `../plotpickle-story-flow/scripts/story-flow.py` and existing Story Explorer to read real screenplay passages and all 25 positions. Verify their exact source relationships, stored prompt, image candidacy, Save/Lock and approval separately. Absence of a position does not imply it was authored. Do not infer an asset-to-shot mapping solely from asset file numbers.
5. Return a compact response: exact story title and revision, whether screenplay/shot source was verified, count of byte-verified assets (or "not checked"), current Script → Storyboard → Visuals → Produce stage, and ONE sensible next action. Use the creator's language and let them select Continue, Review or Revise. Preserve review decisions and continuity across the discussion; do not overwrite or alter any source during a read.
6. Media production remains on demand. Generating a fresh image needs the creator's instruction; submitting a paid fal/Suno job requires current model/cost review and explicit job-specific approval. No auto-generation, no surprise charges, no duplicate retries.

Output terms must be precise: Source loaded vs native reader verified; portable media hashes verified vs hosted Plugin Creator media available; image saved vs locked vs accepted vs final creative approval; provider URL vs actual downloaded MP4; script planned vs completed shot.

The supported in-chat Studio remains the normal experience. The source-only MCP sidebar pilot is optional and must NEVER be represented as hosted, installed, account-authenticated, or fully operational just because a skill or preview is present.

For The Third Bell, resume the private screenplay and first Mini-Block's 25 shot positions when actual authorized files are available; do not publish the story's private seed as part of this skill. For Brotherly Love, a past 131/131 media verification is historical context; rerun the check on current authorized files before claiming their current readiness.

This skill orchestrates existing PlotPickle skills. It does not create a second story database, independently persist files across chats, write native Save/Lock or grant provider billing permission.
