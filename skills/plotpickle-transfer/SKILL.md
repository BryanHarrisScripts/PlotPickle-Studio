---
name: plotpickle-transfer
description: Handle secure transfer of existing original PlotPickle media to ChatGPT Library inside the single PlotPickle application; report independently verified bytes and never generate media merely to transfer it.
---
# PlotPickle — Built-in Original Media Transfer

This is an INTERNAL workflow of the ONE user-facing PlotPickle plugin. Never tell a creator to install a separate PlotPickle Relay, PlotPickle Transfer plugin, or developer Site companion. Elara handles the workflow from PlotPickle HOME, Storyboard, or Produce. Keep the working authenticated Site-backed MCP App as infrastructure, not a second application. Preserve the approved Skin V1 layout and all saved creator data.

Transfer success requires original bytes, an authenticated ChatGPT Library upload, matching SHA-256/size, and independently reread persistent Library bytes. A hosted preview, fal URL, source record, download link, rendered proxy or `uploadFile` receipt is not proof of a completed transfer. Never silently change native PPF Save/Lock, Studio review sidecars, original videos, timeline clips or provider billing.

1. Resolve exact authorized PPF project/shot and existing fal asset ID, job status and original download URL. Reject unexpected source hosts, redirects and unverified shot mappings. Do not expose private user records to others or package them in the plugin.
2. First use actual source bytes already available from authorized conversation, project or Library files; verify expected size, MP4 `ftyp` signature and SHA-256. If a supported Files Library upload can access those actual bytes, use it and independently re-read. Do not confuse developer API file IDs with ChatGPT Library IDs.
3. If original bytes are only on fal, the connected MCP App may use a creator-click browser transport if this host supports CORS, `window.openai.uploadFile(file,{library:true})` and readback. `scripts/relay-client.mjs` is a PORTED, source-only reference from the former standalone Relay v0.1.1. It is NOT deployed by including it in a skill. Its filename helper is specifically for the existing Third Bell pilot; before serving to other accounts, adapt it to user-specific safe naming and test authentication and isolation.
4. Record source URL identity, provider request, shot, expected/actual bytes, source SHA-256, ChatGPT Library file ID and independent reread bytes/hash. Use states `source-verified`, `bytes-unavailable`, `bytes-fetched`, `library-uploaded-unverified`, `verified-in-library`, `blocked`. Only `verified-in-library` means verified transfer success.
5. Preserve the original provider frame rate. Conform to 24 fps and bind to the six-track editor only in the separate approved Produce workflow; retain canonical source approval and revision guards.

If the browser host, CDN CORS, authenticated Library permission or independent readback is missing, report the blocker. No false 'transfer complete', no new paid fal jobs, no external media-storage requirement, no Windows dependency. Use `../plotpickle-unified-application/SKILL.md`, `../plotpickle-creative/references/plotpickle-transfer-site.md`, and the actual Site MCP tools for live operation. The original Relay prototype passed synthetic contract tests only; the current Site service connection alone does not prove that a transfer is verified.
