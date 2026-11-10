# PlotPickle fal → ChatGPT Library bridge: proof of concept

This is source-only experimental code, not an installed or deployed PlotPickle Studio feature.

Run `node --test experiments/fal-library-bridge/test.mjs` (Node 22+). Four offline tests cover strict URL validation, authentication gating, media byte transport into a mock `uploadFile(..., { library: true })` call, and oversize refusal. The tests do not call the real fal network or live ChatGPT widget API.

## Proposed mechanism

1. In a real PlotPickle MCP Apps widget, the creator chooses to preserve a verified fal output.
2. The authenticated service verifies the creator's project ownership and resolves the exact fal URL. Only a restricted media domain is permitted. Server fetching must occur on a host with fal CDN network egress.
3. The proxy streams original bytes into the widget, which creates a `File` and calls `window.openai.uploadFile(file, { library: true })`.
4. Treat the returned `fileId` as an upload receipt, NOT as independent proof of Library persistence. Verify Library listing, saved file size and SHA-256 via a separate authorized readback. Folder placement and guarded PPF asset registration are subsequent operations.

## Important limitations

- No hosting or new storage has been provisioned. The published PlotPickle package is currently skills/scripts and does not have this custom backend or UI widget.
- `authorize(req)` is deliberately mandatory. Production must connect it to existing authenticated sessions/OAuth scoped to project ownership. Do not make a public unauthenticated URL proxy. Add per-user quotas, rate limits, audit logs, security review and replay safeguards.
- A real ChatGPT host test is required to establish whether the widget accepts a programmatically constructed `File` from a fetched `Blob` and actually adds it to Library.
- The tested uploader uses the library flag explicitly; merely returning `video/mp4` from a proxy does not save anything in ChatGPT.
- The original fal The Third Bell Shot 01 job reported 1920×1080, 3 sec, 30 fps and 8,495,321 bytes. The user-supplied ChatGPT copy is lower resolution and must not be substituted for the master.
- Never put private source videos, story data or auth receipts in this public GitHub repository.
- This prototype makes no native PPF writes, no provider generation calls and no external storage writes.

Docs: https://developers.openai.com/plugins/reference
