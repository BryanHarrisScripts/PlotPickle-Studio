# PlotPickle Studio v0.8.34: guarded private release staging

## Current outcome — private skills plugin released, sidebar still optional

The original private Plugin Creator plugin was updated to v0.8.34, release `pluginrel_6af102a657b08191b07da5b8d64be07b`. Installed manifests, the private The Third Bell seed and newly installed in-chat continuation files were read back; the owner subsequently reported successful ChatGPT testing. This supersedes earlier statements below that v0.8.33 remains current or that the **conversational skills-only release** is blocked. They are retained as historical preflight notes.

The authenticated hosted MCP Apps global Sidebar App, multi-device source-file persistence, native Save/Lock writes and independently verified MP4s are NOT established by that update and remain separately blocked. An installed skills plugin is not automatically an authenticated hosted Sidebar App.

--- 

This is a release procedure, not a claim that v0.8.34 is deployed, that the MCP sidebar is hosted, or that private media is recoverable. The controlling source is the November 8 engineering discussion and `docs/direction/`.

## Recovered current host state, November 8

- Existing private USER plugin backend ID: `plugins_6aedd4f5ac1481919653cf6110d565ba`.
- Current installed version: `0.8.33`.
- Current release: `pluginrel_6af0b8fb4dec819181b70bcd777f9963`.
- GitHub Studio source baseline: `6a129da9317b9502186627b4956075e2b884ffd2`; PRs #1–#4 merged.
- The Plugin Creator source listing shows the private `skills/plotpickle-editor/windows/the-third-bell-seed.json`, the exact-size native reader, and the previous icon/logo.
- The owner Library contains a named private backup archive, but file listing alone does not verify its bytes, SHA-256, or suitability for a real rollback. No staged source release may consume it until its raw bytes are independently available and checked.
- `get_owned_plugin_archive` returned a current-release download reference. A reference is not a verified, durable backup.
- The published plugin manifest describes a **skills plugin**, not an authenticated deployed MCP Apps transport. Studio `mcp-server.mjs` source intentionally refuses standalone startup absent an authenticated project loader. The global sidebar is not host-accepted.

## New private recovery result (fresh ChatGPT conversation, 2026-11-08)

The authorized Brotherly Love PPF (revision 539) was opened from the user's ChatGPT Library, and its separate WebP archive was independently materialized. All **131 of 131** image assets, totaling **190,630,642 bytes**, matched the source PPF's SHA-256 content hashes and recorded sizes, with no missing images; the original PPF bytes were not changed. This is verified Library PPF/media recovery **outside** the installed plugin host. It is real recovery evidence, but is **not** the outstanding installed-sidebar, mobile, Save/Lock, MP4, rollback, or Plugin Creator archive-checksum acceptance.

## Private staging command (offline, never in public CI)

Obtain the exact approved v0.8.33 archive and keep it in private owner-controlled storage. From a clean checked-out `PlotPickle-Studio` source tree:

```sh
python scripts/stage_plugin_release.py \
  --backup /private/plotpickle-v0.8.33.tar.gz \
  --source . \
  --output /private/plotpickle-v0.8.34-candidate.tar.gz
```

Staging fails closed unless the published archive matches the pinned SHA-256, the 1,364,997-byte native reader is byte-identical in both backup and source, both candidate manifests remain `0.8.34` with the original backend identity, the two new PNGs are present, the private The Third Bell seed survives unchanged, no unexpected private backup file is lost, and the generated archive round-trips identically. It writes no source PPF, makes no paid calls, publishes no plugin, and does not insert private files into GitHub. No staged archive or raw seed should be uploaded as a CI artifact.

The staging output is a **complete private candidate archive** and a JSON receipt marked `STAGED_NOT_PUBLISHED`. Even a passing receipt does not attest to SDK build, authenticated transport, ChatGPT installation, actual storage, media integrity, mobile readability or rollback. Generated assets must be byte-identical to checked-out GitHub source.

## Actual Plugin Creator guarded update (not yet permitted)

When the following preflight acceptance criteria pass, re-read the live plugin's current release ID and use Plugin Creator `update_plugin` with the exact existing backend ID, exact `expected_release_id`, candidate archive and these two explicit `delete_paths`:

```json
["assets/composer-icon.png", "assets/plotpickle-logo.png"]
```

Never delete `skills/plotpickle-editor/windows/the-third-bell-seed.json` as collateral cleanup. The overlay host preserves omitted files, so merely excluding old images from an archive is insufficient to delete them. Keep a separately verified v0.8.33 restore archive and test its recovery route. Never create a duplicate plugin to avoid release validation.

## Required independent host and story acceptance

1. Verify authenticated, existing-plugin MCP Apps transport and global sidebar tool/resource registration under the intended ChatGPT plugin identity. Test SDK tool + UI resource exchange with per-user authenticated project scope. Block and deny a missing identity, missing PPF, wrong project ID, revision/hash mismatch or cross-user read. Confirm no static HTML embeds a user's private story.
2. In ChatGPT desktop and mobile, open Studio through the installed plugin. Verify HOME, REEL and ONCE are navigation views of one source-linked PPF, not a separate story store. Record real host evidence rather than localhost screenshots.
3. Open an authorized saved Brotherly Love PPF in a **fresh conversation**; independently check project ID/revision/hash and 25 first-mini-block positions. Reopen again after a restart. Check that reads do not mutate the project.
4. Recover **actual image, audio or MP4 bytes** from an authorized project/asset package and independently hash them; a fal job URL or metadata entry alone is insufficient. Report missing bytes explicitly.
5. Only after source-pinned edit approval and persistence work exists, separately prove Save, Lock, reopening and review state; no source-only preview may claim these capabilities.
6. Inspect the private v0.8.33 rollback archive's bytes/hash, verify the host's usable recovery path, and retain an independently restorable copy.
7. If all preflight gates are evidenced, perform one compare-and-swap update on the existing plugin. Afterward independently read back installed version, release ID, file inventory, native reader, branding, private seed continuity, authenticated UI and saved-project reopen. If any check fails, stop and use the verified recovery path.

Release gate disposition at the time of this documentation: **BLOCKED**. Source tests and GitHub merges are not host acceptance. No new plugin is installed or published by this staging work.
