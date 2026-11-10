# PlotPickle fal → ChatGPT Library: direct-first proof of concept

This is experimental source code, **not a deployed PlotPickle Studio widget**.

## Simplest candidate: no additional server or storage

1. Inside an actual PlotPickle MCP Apps widget, retrieve the original public `v3b.fal.media` MP4 using a browser `fetch` (cross-origin access must be allowed by the fal CDN and host CSP).
2. Wrap the returned Blob as a File.
3. Call `window.openai.uploadFile(file, { library: true })`.
4. Obtain `fileId`, then independently read back the Library asset and compare full byte count and SHA-256 to establish persistence.

The widget implementation in `widget.mjs` **attempts direct fetch first**. It does not need or create a proxy by default. An explicitly configured and authenticated proxy can be used as a fallback if cross-origin restrictions prevent direct access. `proxy.mjs` is only that optional, unhosted alternative, not a requirement.

## Tests

Run `node --test experiments/fal-library-bridge/*.test.mjs` with Node 22+. Local synthetic tests verify direct-first routing, expected errors when CORS/network access fails, explicit proxy fallback, authentication checks, URL allowlisting, media types, byte count, and that mocked `uploadFile` receives `{ library: true }`.

Tests are not a live ChatGPT widget or fal CDN transfer. A mock upload receipt is not proof of a persisted Library file.

## Acceptance criteria for The Third Bell, Shot 01

- The original fal provider job reports a 1920×1080, 3-second, 30-fps MP4 of 8,495,321 bytes. Never substitute the 910×512 user-supplied ChatGPT copy.
- A real PlotPickle widget downloads the actual original bytes in the host, using no new storage provider.
- The host's real uploadFile helper returns a file ID and adds the original media to ChatGPT Library.
- Reopen the Library record, compare byte size + SHA-256 and verify correct story/shot association separately.
- Do not write native PPF Save/Lock or claim creative approval without a separate guarded transaction.
- If the browser/CDN blocks CORS or the OpenAI widget rejects programmatically built Files, stop at transport blocked; the optional authenticated proxy is a fallback, not a completed solution.

The installed private PlotPickle Studio 0.8.40 is currently a skills/scripts package without an embedded live widget to run this code. No server, new account, media generation, or external storage has been provisioned.

Docs: https://developers.openai.com/plugins/reference
