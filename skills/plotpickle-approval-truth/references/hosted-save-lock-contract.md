# Hosted PlotPickle mandatory Save → Lock / recovery contract

This is an acceptance specification for the existing authenticated MCP server, not an assertion that server code has been deployed. Keep the canonical app identity, Site, user storage isolation, six-track editor, original images and existing approval history unchanged.

1. **Authority boundaries:** creator approval intent, original bytes, PPF Saved, PPF Locked, Studio Imported and downstream approvals are independent fields. The display must never infer any other field from a successful previous one. Each persisted record is keyed by account-scoped `(projectId, sourcePpfSha256, block, miniBlock, shot, candidateSha256)` and a stable client idempotency key. No private user records in shared plugin code.
2. **Guarded write:** Authenticate the visitor, validate ownership, request origin and per-user resource access; require current source hash/revision and candidate hash. Persist an append-only approval event, exact image reference and SAVE stage, then independently read back from the authoritative source before LOCK. LOCK only source-linked, fully decoded, explicitly approved, non-DRIFTED originals; then independently read back PPF, original SHA, and lock marker. On any failure, do not return success.
3. **Crash-safe resume:** A busy/interrupted write must yield a durable `PENDING_RECOVERY` event with the step reached and same idempotency key. Retrying same request is read-only reconciliation of the prior transaction until the host establishes whether a write committed, then resumes or reports blocked. Never duplicate images/jobs/charges or overwrite prior revision on uncertain status.
4. **Library sync:** Per-user supported Library grant and exact selected-file bytes are required. No hard-coded folder and no assumption that ChatGPT Library can be browsed by the remote MCP. If Library authorization is unavailable, keep the creator approval event and mark media `PENDING_ACCESS`, not `MISSING_IMAGE` permanently.
5. **Bulk requests:** `Approve all 200` is a single scope-authorized event plus 200 separately tracked candidate transactions. If only 169 unique originals are proven, report `200 authorized / 169 recovered / N native locks verified / 31 unresolved`, not `200 locked`. Do not request approval again after recovery; do ask for adjudication of conflicting identity/shot mapping before production.
6. **Idempotent import:** Resolve latest creator-authorized PPF and source passages, not just Studio's older cached project. If there is an incompatible PPF mapping, preserve the original, make a separately versioned migration candidate and verify source and shot records unchanged before importing; never silently replace production.
7. **Acceptance tests (fictional account, no paid media):** (a) five real single-frame images; (b) 200-scope approval with six missing images; (c) older Studio with 120 historical lock booleans and 0 native mappings; (d) valid image mistakenly labeled DRIFTED; (e) expired Library grant; (f) storage-busy after SAVE but before LOCK; (g) same approval retried twice; (h) two independent authorized user accounts (if available) with no media or approvals crossing users; (i) new conversation resumes exact original hash; (j) native readback checks original bytes and PPF. Pass means verified backend and UI results, never simulated success.

## Human-readable UI states

- `✅ Creator approved` — authorization recorded.
- `✅ Original verified` — exact original bytes, SHA and image decoded.
- `✅ Native locked` — successful SAVE then LOCK and independent authoritative readback.
- `❌ Missing / unresolved` — no usable original, or the source says mismatched/DRIFTED.
- `⚠️ Pending PPF / Library / Studio` — specific unverified technical operation, not missing approval.

A release may label this **TESTED procedure** after offline tests; it must not be labeled live backend enforcement until these host-side acceptance tests pass against a real deployment. Never modify an active user's PPF while testing another user's process.
