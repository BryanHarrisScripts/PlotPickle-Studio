# PlotPickle Transfer — creator-owned private Site setup (v0.8.41)

This guidance does not create, publish, host or connect a Site. Complete live connection verification before calling transfers available.

Purpose: one creator-owned, narrowly scoped transfer Site. This Site is NOT PlotPickle Studio itself. It performs existing fal.ai media -> user's ChatGPT Library transfers through a Site-hosted MCP plugin. No extra video archive, no local Windows dependency and no automatic paid generation.

Status: **DESIGN/BOOTSTRAP TEMPLATE ONLY**. Live Site deployment, CORS/egress, the ChatGPT widget's acceptance of programmatically constructed files, Library persistence, and shot registration are not verified. Do not market this as one-click or production-ready.

## User experience

1. The user connects their own fal.ai account in ChatGPT for generation and source discovery.
2. PlotPickle Studio offers **Set up Transfers**. Explain that ChatGPT Sites requires an eligible account (currently Plus/Pro/Business/Enterprise) and that Site creation/editing consumes included Work/Codex usage; running Sites has separate usage/storage limits.
3. A copyable setup request below starts ChatGPT Work on web/desktop to build a PRIVATE Site named **PlotPickle Transfer** from the versioned OSS MCP source. Avoid claiming to open Work programmatically or auto-deploy an account-owned Site from a generic plugin. A built-in Site clone/template API has not been verified.
4. The owner reviews the preview, publishes the Site, installs its associated MCP plugin, and completes any connection/authorization steps. Publishing the Site alone does not install or connect its plugin.
5. PlotPickle performs a one-time **Transfer check** against an existing small authorized fal video. If the test passes it stores the site-connection identifier (not credentials) on the user's side and marks transfers available. If it fails it reports the exact stage and leaves the project unchanged.
6. In Produce, the creator clicks **Save to Library**; the widget reads the original video from an allowlisted fal CDN URL, calls `window.openai.uploadFile(file,{library:true})`, then independently verifies Library readback. It returns the file ID, SHA-256, byte count, associated story and shot. No screenshot, preview derivative or proxy-transcoded substitute can count as the original.
7. Only a separately guarded asset-registration step may update a canonical PPF story document. Never silently change Save/Lock.

## Copyable Work / @Sites build request (for an eligible account)

Build a PRIVATE ChatGPT Site called "PlotPickle Transfer" to host a minimal MCP Apps server for transferring existing authorized fal.ai videos into my own ChatGPT Library. Use the open-source implementation and acceptance tests from the PlotPickle-Studio GitHub repository under `integrations/fal-library-mcp/` on the owner-approved branch/release. Keep the user interface to a connection check, source summary, Save Original button and verified receipt. Implement the documented `prepare_fal_library_import` tool and `ui://plotpickle/fal-library-import/v1.html` widget resource, with explicit CSP allowlisting for fal's media endpoint.

Important: Do not create videos or invoke paid fal models. Do not store media or API passwords in the Site. Avoid server-side media fetching if direct browser transfer works. Reject arbitrary URLs. Require explicit creator action for transfers. Verify downloaded bytes, MIME, MP4 header, size, SHA-256 and host Library upload result; perform independent readback where allowed. If that readback isn't available, state "upload reported, verification pending" and do not claim success. Keep the Site private to me; use platform authorizations. Do not alter any PlotPickle PPF Save/Lock fields.

First run the bundled Node CI tests (including HTTP MCP tool discovery/resource test) using the pinned package-lock. Inspect whether this Sites runtime can host the MCP server and whether the widget's direct browser fetch and OpenAI uploadFile API are available. Do not publish or mark operational unless the live tests succeed. Give me an accurate blocker report if Sites does not support this runtime or fal CDN CORS.

## Architecture and protections

- Creator-owned Site and Site-hosted plugin. The common display name does **not** imply a shared URL or shared credentials; each Site has its own address, owner and permissions.
- No credentials in public GitHub, URL query strings, widget HTML, tool outputs or telemetry. Use separately connected fal tool/account where authorized; public outputs can be transferred using a signed provider URL subject to expiry.
- Default Site and plugin access PRIVATE. Owner reviews every permission and publication. Separate Site access from plugin installation/authorization.
- Strict host and path allowlists; no SSRF/open proxy, prevent redirects; enforce content types, file size caps, timeouts, rate limits and per-user authorization if any server fetch is added.
- Audit receipt with provider request ID, expected filename, story/shot, source URL identity, byte count and SHA-256, upload file ID, readback status. Keep provider payment and Save/Lock entirely separate.
- Do not state a per-transfer Work/Codex charge; ordinary file transfer is not necessarily a Work task. Site runtime/traffic quotas, user Library upload rate/storage caps and fal provider charges remain separate.
- Sites currently only available to eligible account/workspace tiers; Free/Go users would need a different supported solution. Not all API methods or web origin rules are guaranteed in Sites.
- Personal account Site-hosted plugins aren't directly shareable as plugins to other personal accounts. Independent per-user creation may avoid that restriction, but each creator must still complete a permitted setup.

## Acceptance for The Third Bell Shot 01

Original fal output: 1920x1080 MP4, 3 seconds, 30 fps, 8,495,321 bytes. A 910x512 copy (1,931,139 bytes) exists in ChatGPT Library but is not an acceptable original.

PASS only if a user-owned, private Site actually hosts its MCP plugin; ChatGPT invokes the real tool + widget; original bytes transfer from fal to the user's Library via the real helper; Library listing and readback verify byte count and SHA-256; and the PPF remains unchanged until separately authorized. NO new paid generation or other media hosting should occur.

## Product UI states

`not-configured` → `site-draft` → `site-published` → `plugin-connected` → `transfer-tested` → `ready`.

An upload may have `transfer-requested`, `download-blocked`, `upload-reported`, `readback-verified`, `registration-pending`. Only `readback-verified` means the original media reached Library; only a separate guarded PPF action may set `registered`.

## Sources

- https://help.openai.com/en/articles/20001339-creating-and-using-chatgpt-sites
- https://help.openai.com/en/articles/20001547-hosting-a-plugin-with-chatgpt-sites
- https://developers.openai.com/plugins/reference
- https://developers.openai.com/plugins/build/chatgpt-ui
- https://help.openai.com/en/articles/8555545-uploading-files-and-audio-to-chatgpt
