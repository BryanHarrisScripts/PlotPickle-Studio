---
name: plotpickle-release-lock
description: PlotPickle Studio version-linked engineering release locks, surface and pattern IDs, inventor/invention reference tracking, test and deployment gates, minimal storage, and owner approval. Use before changes to a protected surface, plugin version or release.
---

# PlotPickle Studio — Compact Engineering Release Lock v1.0 (plugin 2.0.41)

This is a **version-linked release ledger and a local release gate**, not a backup service, hosted deployment controller, or new application. Read `references/release-index.v1.json`; run `python3 scripts/release_lock.py validate` before preparing a release. Run `python3 scripts/release_lock.py check --version VERSION` to determine if the release is **eligible to be called locked and ready to deploy**. Never call a TESTED/CANDIDATE record LOCKED or RELEASED.

## One version; one small record

- Plugin semver identifies the package (`2.0.41`); the single append-only `references/release-index.v1.json` links that version to existing **surface locks, pattern/engineering specifications, invention reference IDs**, source fingerprint/commit, test and creator-approval evidence, and a verified rollback pointer. Use references to files already in the plugin or source-control history, not copies of the files themselves.
- Before every release, append exactly **one new version record**, and never change any previous locked record. The helper rejects duplicate versions and validates SHA-256 of canonical record content to catch accidental corruption. Its checksum is not a cryptographic signature or proof against a malicious rewrite. Version-control history provides the independent audit trail if connected and verified.
- **No per-version ZIP, screenshot bundle, build folder, user story, media, PPF, source dump, legal case file, or database** is created by this workflow. Use existing source-control / hosted-plugin release history and pointers. Keep only a minimal current/last-good rollback *reference*, not self-generated backup archives. Never automatically delete original creative assets, historical deployed releases, legal-hold material, or platform-managed backups.
- Internal invention/patent-tracking entries contain **IDs and statuses only**. `internal-invention-record` does not mean patent applied for, registered, granted, or legally protected. Only record verified external filing/grant references, and keep confidential disclosure details outside a distributable plugin.
- Do not add a duplicate UI engineering database. The Surface Library `references/registry.v1.json` and the existing locked interface agreements remain authoritative for surfaces and their acceptance states.

## Mandatory stage distinction

**DESIGN → BUILD → TEST → REGISTER → LOCK → RELEASE.** DESIGN/BUILD/TEST may run while creators use LIVE, but this separation is a *deployment requirement*, not proof isolation already exists. A release is eligible to be called LOCKED only when exact tested source, surface/pattern approvals, owner release authorization, preservation checks and rollback evidence are confirmed. RELEASE requires independent actual deployment / device validation. An update to packaged skills alone does **not** deploy Site code, change the MCP server or prove that a ChatGPT app surface works.

Do not use a skill version bump as authorization to override the already owner-locked Skin V2 HOME. If a lock changes, obtain a new explicit owner design approval. Preserve private PPF/storyboard approvals, images, BEATs, six-track media, and source integrity.

**Operation:** `python3 scripts/release_lock.py validate`, `... check --version 2.0.41`, or `... append --record /path/to/proposed-record.json`. The last command inserts a unique draft/tested record; it never marks the version locked automatically. Run `python3 scripts/test_release_lock.py` for offline tests. For actual release publishing, release engineers must run the gate; the plugin host does not currently enforce this script at deployment time.
