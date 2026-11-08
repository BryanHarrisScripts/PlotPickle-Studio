# PlotPickle Studio — read-only Sidebar App integration pilot

Status: implementation candidate, November 8, 2026. The source is built and unit/HTTP-tested; the global ChatGPT sidebar entry is **not yet installed or hosted**. This directory is intentionally separate from the optional legacy Windows app. The November 8 engineering brief in `docs/plotpickle-engineering-brief-2026-11-08.md` is the working product direction; November 6 is background only.

## What is implemented

- REEL and ONCE are two navigation experiences over one PPF project and one source identity, not separate stores. Choosing ONCE does **not** turn an existing screenplay into an autobiographical memory.
- The responsive `studio.html` is a read-only visual story workspace with Story, Characters/People, Worlds/Places, Scenes/Memories, Storyboards/Illustrations, Produce/Preserve, Learn, Review and Share. Source-backed scenes, character cues, individual unmerged scene-heading places, shot addresses, original prompt records and derived evidence edges can be inspected. Unverified media remains visibly unverified. No source content is inserted via `innerHTML`.
- `src/projection.mjs` reads real PPF records without changing them. It checks the project ID, revision, and raw SHA-256 that an independently executed native PlotPickle reader returns. Legacy artwork mapping is represented without inventing an authored shot plan.
- `src/loader.mjs` requires a configured PPF and native inspector. Missing source/reader, mismatched hash, failed reader or bad PPF is blocked without exposing private file paths or source text.
- `src/server.mjs` is a loopback-only developer preview. GET `/api/studio` and `/` exist; no write endpoint or authenticated multi-user service is implemented. The preview starts with `No project loaded` unless a file and native inspector are explicitly provided.
- `src/mcp-registration.mjs` declares `open_plotpickle_studio` with official MCP Apps `ui://` resource and OpenAI global/sidebar entrypoint metadata. The standard MCP Apps tool-result bridge supplies data to the UI. The reusable app resource does **not** embed private story content; it starts unconnected and receives the authorized tool result.
- `src/mcp-server.mjs` creates an SDK server for integration into the existing authenticated PlotPickle plugin host. It intentionally does not start a new, unsecured public MCP process. Transport, authentication, per-user project resolution, deployment and plugin host linkage are pending.
- Direct provider links open `https://suno.com/` and `https://fal.ai/dashboard`; PlotPickle does not collect credentials or automatically consume credits.

## Build and test

Node 22 or later is recommended.

```sh
npm test          # no external dependencies needed, includes HTTP preview smoke
npm run check     # parses the five core source modules
npm run preview   # loopback-only developer view: http://127.0.0.1:4318
```

To test against a genuinely native-verified project source on a host that has the unchanged canonical PlotPickle inspector:

```sh
PLOTPICKLE_PROJECT_FILE=/authorized/path/story.ppf.json \
PLOTPICKLE_INSPECTOR=/path/to/read-plotpickle-project/scripts/inspect-project.mjs \
npm run preview
```

Never configure private user PPFs in a public server or share a generated HTML page that embeds their contents. For actual ChatGPT installation, the existing authenticated plugin host must resolve each authorized user's current project, execute the canonical inspector, register the app resource/tool, install the official SDK dependencies, and expose a vetted TLS MCP endpoint. The current environment has no available Sites MCP backend and npm registry access is blocked. Do not treat `node --check` as an SDK integration test.

## Acceptance evidence

Thirteen automated tests pass (projection, loader fail-closed, local HTTP no-write). A read-only projection from a privately retrieved Brotherly Love PPF export, revision 539, found 383 retained passages, 16 source scenes, 10 cue-derived characters, 16 distinct scene-heading places, 125 storyboard addresses, 131 recorded artwork associations, and 300 derived relation edges. This is **source projection only**: it was not independently accepted by the canonical native inspector in this environment, and associated image/video bytes were not fetched and verified. The real export and private preview are deliberately excluded from this source package.

Headless browser acceptance could not be completed here because the browser environment blocked local file and loopback navigation; this remains an independent UI gate, not a passing test.

## Gates to ChatGPT sidebar availability

1. Use the November 8 engineering brief as the controlling product direction.
2. Connect an existing authenticated PlotPickle MCP host; no second story repository or provider credentials.
3. Install SDK dependencies and run the MCP Apps bridge/entrypoint under an official host, including mobile and desktop UI checks.
4. Prove native PPF identity and durable reopen for a real authorized project and separately verify portable media bytes.
5. Only then introduce guarded Save → Lock, edits, provider job submission, import, render and sharing. All mutation APIs remain absent in this milestone.

Never describe the read-only Studio prototype as a published ChatGPT Sidebar App or an editor.
