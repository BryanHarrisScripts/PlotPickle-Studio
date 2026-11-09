# Shot Review Sidebar — first truthful milestone (2026-11-08)

Owner request: an optional ChatGPT Studio sidebar specifically for approving, regenerating, locking and unlocking images, to replace repeated uncontrolled conversational approvals. Preserve phone-tested conversational HOME/REEL/ONCE. This is **not** a replacement editor and does not mean the MCP Apps host is already connected.

## One source of truth, one selected shot

Review tray shows exactly one canonical shot address (Act, Sequence, Block, Mini-Block, Shot), screenplay evidence, exact retained prompt provenance, original/source candidate and variations, native saved marker, native lock flag, independently observed image SHA-256/decode, an independent human visual-approval mark, and the current project revision. The tray must never present a generated contact sheet crop as a full-resolution locked source image.

Primary controls:

- **Approve** — record an explicit human image selection for an exact candidate. Approval alone is **not** Save or Lock. To advance a newly approved image, the source write adapter must verify image bytes, then run Save -> reopen/readback -> Lock -> reopen/readback. This must obey existing default-save-lock v1 rules; no automatic silent lock claims.
- **Regenerate** — capture a revision request, preserve the existing image and old prompt, and prepare a new candidate. Locked selections must first be explicitly unlocked. This control **never** directly spends fal or other credits. ChatGPT Image generation remains user-directed; any provider job requires separate review/cost approval.
- **Lock** — requires prior saved state, explicit author approval, current verified image bytes, exact project identity/revision/hash, source evidence and a successful native Lock readback.
- **Unlock** — requires currently saved+locked image and a user reason; permits replacement even if original media has since gone missing. Unlock is a separately committed project revision, not a flag hidden in browser state.
- Optional "Approve verified set" convenience may be added after native write acceptance. It must show all affected shots and exceptions before committing; operations must remain individually auditable.

## Technical gates

Current source includes `pilot/src/review-intents.mjs` as a pure, fail-closed intent preparer. It validates identity, revision, image content hash, exact candidate, shot source and idempotency key. It never writes to a PPF. The existing `read-plotpickle-project/scripts/default-save-lock.py` has native Save->Lock, Unlock, Relock and Replacement commands with canonical readback. The missing middle layer is an authenticated, owner-scoped host file writer with compare-and-swap revision checking and readback. **Do not permit a UI field or browser flag to self-assert that storage is connected**. Only the authenticated server establishes write capability.

State should be displayed as four independent axes: 
1. Visual approval in the actual persisted project or explicit pending review intent.
2. PPF Save marker.
3. PPF Lock marker.
4. Image bytes/hash/decoder verification and pending replacement.

The graphical sidebar's `Review` view exposes a shot-by-shot candidate list and four control labels, but all action buttons stay disabled in this initial source-only milestone. No fake success, no localStorage approval, no unauthenticated HTTP writes, no extra story database and no provider invocation. Once a verified host service is available, the same intent contract can be invoked headlessly by the agent and interactively through the sidebar.

## The Third Bell, first concrete review truth

The authorized ChatGPT conversation contains the 25-shot plan and selected generated PNG concepts. A private exported register named `The-Third-Bell-25-Shot-Review-Register.json` inventories **eight** candidate PNGs whose local bytes can be decoded and hashed (Shots 01, 02, 07, 08, 09, 10, 11, 12). Past conversational approvals were reported for 01, 02, 07, 08 and 09; that is **not** canonical PPF Save/Lock or a proven final approval record. Images 07–12 are derived concept crops, not independent full-resolution renders. Shot 10's actual arrival is tightly cropped; Shot 12's 1920x443 crop requires a full production reframe. The remaining 17 positions do not have individually verified original source images in the current local register. The actual Third Bell PPF is not available for live reopen here; its old ID/revision/hash from a motion brief are not a verified current source pin.

Never upload the private register or images into the public Studio code repo. The owner may keep that register in their ChatGPT Project and use it to recover review context, but not as a substitute for a canonical PPF mutation and readback.

## Acceptance for a functioning ChatGPT sidebar

- Proven official MCP Apps UI host + authenticated account-scoped project loader, never a public path or static single-user PPF.
- Correct image bytes and source-linked thumbnail available for each candidate; demonstrate review on real authorized PPF with verified media.
- Clicking each control returns a structured receipt that records request ID, expected source revision/hash, new committed revision/hash (when applicable), readback status and unresolved conflicts. Do not mark success until verified native PPF bytes and accessible portable assets are reopened.
- Reopen in a fresh ChatGPT conversation and on phone/desktop. State persists without relying on browser local state. Back/forward and stale concurrent clicks cannot resurrect a retired asset.
- Provider cost approval stays outside visual review.
- Existing conversational plugin v0.8.34 remains intact until a separately guarded plugin release with verified host acceptance. A GitHub source merge does **not** install a sidebar.
