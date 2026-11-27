# Asset inventory and stage handoff, v0.8.45

Use one read-only reconciliation view over the existing PPF asset registry, provider IDs, Library identities and editor draft. Do not create competing project canon. Accessible entry points: Storyboard > Assets > Audit Missing Media, Reports > Production > Handoff, and Produce > Check Handoff. Preserve the established HOME and approved review layout.

## Human view

Show the evaluation time and exact scope first, then source assets found, verified Library files, awaiting transfer, unassigned provider assets and shots ready for editor. Never equate all-transferred with all-approved. Each row shows the actual thumbnail when accessible, story/shot or cue, provider, original/version/stem/derivative role, Library location, transfer verification, four independent approval/save/lock/media states, editor usage, blocker and next action. Use real Library file links, not CDN URLs as persistent storage. Do not display credentials or signed transport links.

Thumb through the existing Image Review using Previous / Next, Approve and Lock, Flag for Change, Unlock. These are conversation actions when a live action bridge is unavailable. Approve and Lock invokes the existing source-guarded Save then Lock transaction, persists a new portable project, independently reopens it, and only then reports success. Flag records feedback in a separate persisted, source-pinned sidecar unless an existing verified feedback writer is available; it does not discard the image or unlock unrelated shots. Unlock uses the existing scoped writer and readback. A review preview has no write power. Never fake a completed button operation or implement Save/Lock by changing booleans in a report.

## Synchronization points

After a requested generation completes, register its stable provider/request identity, source image hash, story/shot/cue and output role. Reconcile at that point and before production handoff, after transfer, after an approval transaction, and after a relevant project/media revision. This release executes on demand during a turn; it installs no timer, background task or continuous sync. Existing transfer tools may require a creator click. Never report a completed import from preparation alone; do not regenerate a missing transfer.

Provider snapshots require provider, explicit scope, observedAt, assetIds, paginationComplete and scopeTruncated. Follow every cursor under unchanged filters. An unavailable, partial or truncated listing cannot prove completeness. A null totalCount is unknown; exhausting an untruncated cursor establishes only that query's returned scope. Record failures and unassigned assets, including older generations; don't guess shot membership from titles. No spend or provider mutations are needed for enumeration.

Suno is included in the data contract for future use: preserve song id, version/take, mix/stem role, parent id, selected Library file, content hash and cue association. A Suno song URL or listen page is not an original audio transfer. Do not import an entire personal music account or mark it story-associated automatically. Cue-to-PPF registration and actual Suno byte transport need supported tools and independent verification; absent adapters remain unverified. BUZZ and Modem are on hold for this handoff milestone; preserve their existing optional routes without attempting deployment.

## Portable reconciliation command

`python3 scripts/asset-handoff.py --project PROJECT --manifest INVENTORY --media-root ROOT --out NEW_REPORT`

The manifest is a source-pinned evidence snapshot, not a project writer or authoritative provider database. Fields:

- project: id, revision, sha256 of exact reopened PPF.
- providers: list of provider, scope, observedAt, assetIds, paginationComplete, scopeTruncated, optional error.
- assets: stable inventory id, provider, providerAssetId, kind (image/video/audio), role (original/derivative/mix/stem), optional derivedFrom; exact artifactId when a storyboard shot; original bytes and sha256 from independent source evidence; library {fileId, path, localPath}; submittedImageSha256 for image-to-video; creativeApproval and creativeApprovalEvidenceRef only from actual scoped decisions; continuity list with kind, state, evidenceRef, imageSha256; editorUsage with exact sourceSha256 and draft/clip references when verified.

media-root contains relative portable paths; missing files, traversal, escaping symlinks, changed bytes, stale source pins, incomplete enumeration, wrong source images and missing approvals are explicit issues. The helper independently hashes current local readbacks and registered source images. It never attests full decoding, visual identity, permissions, paid generation, actual provider retrieval or editor import. A different JPEG/WebP hash may be a re-encoding; report a provenance review, never declare it a wrong character or wrong world by hash alone. A documented and visually accepted conversion can later gain its own source-verified lineage evidence; don't silently waive the mismatch.

Audio cue and non-storyboard design-reference adapters are not implemented in this first helper. Their evidence can be inventoried, but missing canonical registration remains blocked rather than borrowing a shot lock. Original media, source images and conformed/editor files remain distinct.

Changed locked images invalidate only dependent readiness: keep the cut, compare its recorded source hash against the new version, mark affected uses needs-review. The helper does not rewrite or replace any timeline media. A full acceptance run requires a real media-linked draft edit, durable saved draft, independent reopen and validated export; a synthetic test is not that acceptance.

Run scripts/test-asset-handoff.py for failed/missing transfers, partial enumeration, unassigned provider assets, stale revisions, source mismatch and path safety. Keep personal manifests, filenames, PPFs and report outputs outside the plugin package.
