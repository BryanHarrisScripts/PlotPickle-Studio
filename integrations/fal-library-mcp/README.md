# PlotPickle fal-to-ChatGPT Library MCP Apps acceptance runtime

This integration provides a standalone MCP Apps test server, not a replacement for the currently installed skills-only PlotPickle Studio plugin. It does not add a storage vendor, generate new media, register story assets, or change PPF Save/Lock.

## How to run

Install Node 22+ and then:

    npm install
    npm test
    npm start

The MCP Streamable HTTP endpoint is `http://localhost:8787/mcp`, with a `GET /healthz` health check. Only connect it to ChatGPT after an approved HTTPS deployment/tunnel and the required authentication/security hardening. Local Node/browser tests by themselves do not establish host acceptance.

Connect as a new private development MCP plugin; do not modify the existing PlotPickle Studio release. The tool `prepare_fal_library_import` exposes a `ui://plotpickle/fal-library-import/v1.html` resource with `text/html;profile=mcp-app` MIME, and the CSP allows direct connections to `https://v3b.fal.media`. The tool requires an explicit pre-existing MP4 URL, byte size, story ID, shot ID and optional safe filename. It performs no server-side downloads or writes.

For The Third Bell Shot 01, use the existing fal request (not a new generation) and its expected size of 8,495,321 bytes. Do not bundle that private URL, source media or project manifest into public source code.

The widget is direct-first: it downloads the actual MP4 on a user click, checks MIME/size/file signature, hashes the bytes and invokes `window.openai.uploadFile(file,{library:true})`. When supported, it then calls `getFileDownloadUrl` and hashes the readback. Only a readback with matching byte count and SHA-256 is labeled verified. A file ID without readback remains upload-acknowledged, not an accepted story asset.

The widget does not promise that creating a programmatic `File` will be accepted by the host. This must be verified in real ChatGPT. CORS/CSP can block the direct fal CDN fetch even when the server is healthy. No proxy or extra hosting/storage is provisioned by these files; for a real ChatGPT plugin, the MCP server itself still needs an accessible HTTPS runtime.

## Testing

`npm test` runs pure validation tests. `python test/browser_acceptance.py` is a Chromium fixture using a real user-supplied 910×512 MP4 and mocks for both the fal CDN HTTP response and the ChatGPT host upload/readback. It cannot establish a real transfer, and it uses a mock SHA digest because the test page's about:blank origin is not a secure context.

The **release acceptance** is only satisfied when an actual MCP Apps-connected ChatGPT widget can retrieve the original 8,495,321-byte MP4 from fal, upload it to ChatGPT Library, recover its Library record, compare full bytes/SHA-256, and then perform a separately authorized, guarded PlotPickle shot registration transaction.

Before deploying publicly: implement host-bound authentication, rate-limiting and audit logs, review CSP and permitted origins, and pin SDK dependencies with a lockfile. This proof-of-concept accepts a user-supplied fal URL only and has no privileged server-side access. The unauthed dev server must not be advertised as a production ingestion service.

Documentation: https://developers.openai.com/plugins/build/app-quickstart , https://developers.openai.com/plugins/build/chatgpt-ui .
