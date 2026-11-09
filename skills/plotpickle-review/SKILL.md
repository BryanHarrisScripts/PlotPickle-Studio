---
name: plotpickle-review
version: 0.8.35
summary: Source-backed storyboard image approval, regeneration, Save, Lock and Unlock in ChatGPT.
---

# PlotPickle Studio — Review

This is the primary ChatGPT conversational review path for REEL or ONCE. Preserve the existing HOME, REEL, ONCE and mobile interactions. The optional MCP Apps graphical sidebar is not deployed just because this skill is installed. A standalone HTML preview or locally retained review draft is not native project persistence.

## Locate and verify the correct source

For Review, Approve, Regenerate, Lock or Unlock, locate the latest owner-authorized PPF in ChatGPT Project files or the personal Library and any accompanying portable ZIP or image files. Do not infer saved source from memory, a screenshot, a project title or a stale UI card. Pin the PPF project ID, revision and exact raw SHA-256; independently validate it with the canonical native reader when available. Read real shot-to-screenplay mapping records, exact candidate IDs and prompt provenance. Check actual image bytes, recorded SHA-256 and decoder, not just a URL or a concept contact sheet. Distinguish a historical PPF concept crop from a separately generated ChatGPT candidate. A verified portable ZIP is not proof of a saved or locked shot.

Present an easy source-linked 25-shot review selector and the selected image, with four independent properties: exact visual candidate and human review decision; native Save marker; native Lock marker; independently verified media bytes. Unavailable state must say “not verified,” never “complete.”

## Action rules

- **Approve:** the author must explicitly choose a specific candidate. Record shot coordinates, project ID/revision/raw SHA-256, artwork hash and identifier, source passage IDs and explicit human choice. Approval alone is not a native PPF Save/Lock. Never infer which PPF artwork was approved from earlier general “approved” messages.
- **Regenerate:** record a reason, preserve prior candidate and prompt, and prepare a new image proposal. If the image is locked, require Unlock first. Generate new ChatGPT imagery only on the creator's request; chargeable fal/Suno jobs require separate exact-job approval. A replacement starts unlocked and requires its own review.
- **Save:** verify exact image bytes and source mapping, use the existing native project Save operation, persist a new owner-scoped snapshot with a compare-and-swap source guard, and reopen the saved artifact. The user must never be told Save succeeded on a queued intent or browser-only draft.
- **Lock:** requires an independently verified prior Save, author approval, correct current decoded image, exact pinned PPF and successful new revision/readback. The existing `read-plotpickle-project/scripts/default-save-lock.py` can perform exported native Save→Lock operations when the canonical inspector and files are available; it is not itself an authenticated ChatGPT Library writer.
- **Unlock:** requires a saved+locked source candidate and an explicit review reason. Use a guarded native Unlock revision and readback. Do not overwrite or silently revive a retired candidate.

Never report a durable project edit until its actual owner-authorized file write succeeded and the new PPF and portable media were reopened and verified. When host-side native write or readback is unavailable, create a private `plotpickle.review-draft.v1` intent explicitly marked `REVIEW_DRAFT_NOT_PPF_COMMITTED`, with all current source/media pins. Save that draft to Library only if an actual file write returns success. Offer to copy/export decisions from the portable HTML Review workspace.

An existing privately owned The Third Bell ZIP was recovered with 25 original 1280×720 WebP shots and matching SHA-256 records at PPF revision 0; in that snapshot none was saved or locked. This is historic source verification, not a current cross-chat or hosted UI guarantee. Do not place user-owned PPFs, source passages, media, IDs or SHA-256 in public GitHub.

If the creator requests a genuine sidebar, say that official hosted MCP Apps entrypoint and owner-scoped storage connection remain separate unverified deployment gates. The in-chat review workflow can work now without a compulsory Windows app, extra database or GitHub story account.
