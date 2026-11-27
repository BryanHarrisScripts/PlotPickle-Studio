---
name: plotpickle-approval-truth
description: "MANDATORY for any PlotPickle user approval, approve-all, Save, Lock, resume, recovery, or numbered-shot completion claim. Independently reconcile every requested shot against original bytes and current native PPF/Studio readback; never turn approval, filenames or historical lock markers into verified locks."
---

# Approval Truth — mandatory fail-closed procedure

This is a procedure for **all users**, not a record containing any creator's personal project. It must be applied alongside `../plotpickle-truth-gate/SKILL.md`, `../plotpickle-approval/SKILL.md`, and `../read-plotpickle-project/references/default-save-lock.md` before any project/shot status claim or modification. This skill is a deterministic local audit, not a hosted backend repair or substitute for native Save → Lock.

## Fundamental invariant

**Creator approval is not a lock; a file is not a shot; a filename is not evidence; a prior lock marker is not a current verified native lock.** A user's approval of a full scope is valid authorization covering exactly the named shot positions. Never lose or repeatedly solicit that authorization merely because a file or write is missing. Equally, never count a missing, DRIFTED, or mismapped image as a completed/locked original. Keep authorization and the verified production state separate.

A shot truth record must contain at least `projectId`, `sourcePpfRevision`, `sourcePpfSha256`, `block`, `miniBlock`, `shot`, `creatorAuthorizationSource`, `creatorAuthorized`, `originalAssetIdOrLibraryRef`, `originalSha256`, `originalByteSize`, `sourcePassageIds`, `visualReview`, `nativePpfSaved`, `nativePpfLocked`, `studioImported`, `lastReadbackTime`, and `lastError`. Store per-user records **only** in that user's authorized project; never embed private project material in the distributed plugin.

## Mandatory workflow for every approval and completion request

1. **Scope first.** Enumerate the expected address matrix, e.g., 2 Blocks × 4 Mini-Blocks × 25 = **200 distinct positions**. Capture the creator's exact scoped instruction and apply it to all positions even if some images are still being recovered. Authorizing 200 never means 200 media files or locks were verified.
2. **Source before mutation.** Reopen the current creator-authorized PPF, pin raw project ID, revision and SHA. Read the original screenplay and the approved character/vehicle references. If older Studio has a different source revision, report the mismatch and preserve both; do not choose the older copy by default.
3. **Recover before generating.** Search the user's available Library, current conversation and official project archives, including prior approved originals and receipts. Select per-shot assets by exact source evidence + original SHA, not filename or nearest generated image. Exclude DRIFTED, montages, visual mismatch, unresolved substitutions. Never regenerate merely because a connector cannot find a file.
4. **Verify separate truth dimensions.** Creator-authorized, media located, actual byte-hash+full pixel decode, script/character continuity, mapped PPF candidate, PPF Saved, PPF Locked, Studio imported, render downstream. Only mark a dimension ✅ when its own proof exists. `approved-locked.png`, `lock:true`, Library upload, or a handoff receipt are not sufficient native evidence.
5. **Transactional Save → Lock.** For eligible source-linked original, invoke the supported native writer with source ID/revision/SHA, shot address and expected candidate hash. Independently reopen the saved snapshot **before** locking; independently reopen the locked PPF and image bytes **after** locking. Preserve old source as an immutable fallback, with atomic optimistic concurrency and an idempotent operation key. If the host cannot write an authoritative PPF, stop and record the blocker; do not mutate booleans to simulate success.
6. **Partial failure is recoverable.** On busy storage, absent Library grants, failed import or stale revision, keep user approval, source and image unchanged; mark `LOCK_PENDING`, record exact step/error/idempotency key, and resume from that point after repair without duplicate generation or repeated approval. Do not claim success from the attempted write.
7. **Mandatory readback totals.** After a batch, display approved authorization count, unique originals recovered, originals hash+decode verified in this run, native locks independently verified, Studio imports verified, and precise missing/DRIFTED positions. A 5/5 approval can coexist with 0/5 PPF locks. For 200 shots, do not display `200/200 locked` unless each of those 200 independently passes native readback.
8. **Next user default.** Whenever a new user selects Continue Story, Approve & Lock, or Approved All, initialize a per-story truth ledger; show current saved/locked state and missing dependencies. Never require a second account or hard-coded Library folder. Never reuse another user's approval or project data.

## Executable offline audit

`python3 scripts/reconcile.py --manifest /private/approved-positions.json --ppf /private/project.ppf.json --media-root /private/project-assets --out /private/approval-truth-audit.json --require-complete`

The manifest needs `project.id`, `scope.blocks`, `scope.miniBlocksEach`, `scope.shotsPerMiniBlock`, and one record for **every** address in `positions[]`. Current native lock verification requires all four of: matching source PPF, internally coherent native markers, matching original SHA, and actual valid decoded media on disk. Missing host readback means `UNKNOWN` or `BLOCKED`, **not** success. Audit is read-only; it neither locks media nor imports Studio assets.

Test with `python3 scripts/test_reconcile.py`. No test of this local script proves that the deployed MCP service, per-user Library grants, or Studio persistence is fixed. Backend implementation requirements live in `references/hosted-save-lock-contract.md`.
