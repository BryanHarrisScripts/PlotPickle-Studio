# PlotPickle Studio — Backend acceptance contract for the Image Truth Gate

**Status:** packaged design/test contract, **NOT** an implemented Site/MCP deploy. The ChatGPT Studio MCP and locked Skin V2 are separate. No change to the App identity, project database, authentication, user-owned assets or HOME design is authorized by inclusion of this file alone.

## Required Studio implementation in existing Site project (no second database)

1. **Source lock:** before preparing/submitting a storyboard image job, resolve current account-scoped story, real source PPF, SHA/revision, exact production address, separately preserved source passage IDs and the latest Library/stored scene allocation. If actual Library original bytes are inaccessible, fail closed. Do not call `studio_get_state`'s scoped 25 shots the complete story.
2. **Reference readback & generation envelope:** reopen approved character/vehicle/world and preceding image originals by hash. Include their *actual image bytes* (or verified provider upload receipts) in every one-image request. One distinct request/immutable idempotency key per intended shot; do not combine five shot prompts into one or ask for a montage. Verify expected scene, subjects, action, camera and explicit exclusions.
3. **Provider risk:** per-job current price and creator authorization for a paid model. No automatic expense, duplicate submission on uncertain provider response, or reliance on the creator's Plus subscription as API payment. Return honest errors/host limitations.
4. **Postflight classification:** decode actual returned pixels, compare against script/reference images through a real visual inspector (model or human), keep a specific reason and original SHA for DRIFTED; do not equate a pixel-decoder/hash PASS with semantic alignment. Failed/unknown frames cannot advance the continuation pointer.
5. **Save and readback:** separate creator approval, original Library hash, PPF SAVE stage, PPF LOCK stage, Studio workspace import and export readiness. Require independent canonical PPF reader validation and scoped optimistic concurrency before any `NATIVE_LOCKED` badge. Preserve unrelated blocks/mini-blocks, prior approved versions and six-track records.
6. **DRIFTED enforcement:** store semantic state per exact candidate hash. Display a visible DRIFTED review overlay only on flagged derivatives, preserve unmarked masters, block flagged/unknown assets from editor selection, Pitch Edit, motion, preview and export until source-backed correction. Do not retroactively overwrite approved originals.
7. **Resume:** store the exact last accepted shot and failed/pending shot in account-scoped project state. On fresh conversations load actual continuation, not chat recaps. Keep production address separate from source block address. Conflicts trigger review, not automatic source selection.
8. **Account isolation:** test with two **real authorized accounts**, independent source and media sets. Never use one user's approved references in another user's image prompt, preview or project. Use fictional test assets. Second-account success cannot be inferred from mocked identities.

## Development/TEST acceptance — mandatory before production deployment

- One authorized fictional screenplay with two distinct characters, two ages, two vehicles, 25+ shot positions in two Mini-Blocks, duplicate/skipped/mismatched shot requests.
- Batches of five return five **separate** original images with different hashes; no tiled collage or repeated previous frame. Intentional wrong actor, scene, vehicle and panel grid are caught and marked on review derivative only.
- Run source-change conflict, stale revision, valid/invalid Library SHA, remote image bytes unavailable, wrong author session, duplicate retry, native Save then Lock with PPF readback, Studio import preserving multi-mini-block approvals, six-track render exclusion for DRIFTED and UNKNOWN.
- Verify actual MCP tool and active ChatGPT UI behavior. Preserve owner-locked HOME/Skin V2. Do not deploy Site without the existing release lock, owner sign-off and verified rollback.

**Current known limitation:** the existing Studio MCP tools expose separate import/review workflows, but their active account state can lag the user's ChatGPT Library; the skill-only release cannot repair the Site or make server-side rules live. This contract must be implemented in the Site's owning source under a separate guarded deployment.
