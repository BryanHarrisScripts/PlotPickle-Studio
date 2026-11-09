# PlotPickle Studio — Release Archive

PlotPickle Studio is the ChatGPT-native creative production plugin for REEL, ONCE, Storyboard, the 81-lesson curriculum and creative services.

**Plugin Creator is the authoritative development, package and release manager.** GitHub is a read-only-in-practice historical version archive. The private published ChatGPT plugin, not the `main` branch, determines what creators use.

## Operating policy (owner approved 2026-11-09)

- Design and edit the plugin using ChatGPT and **Plugin Creator**. Publish updates using Plugin Creator's guarded update function and verify the published release metadata and relevant feature behaviour there.
- After a successful publication, copy the approved release source into this repository as an archival snapshot; record the version, Plugin Creator release ID, archive commit and any known archive limitations. GitHub archival must **follow**, not precede, publication.
- Do **not** use GitHub Actions, CI, automated GitHub tests, PR-based release gates, software-factory workers or branch-based deployment to produce or approve releases.
- Do not execute stored tests in GitHub. A small creator-facing manual readback/check within ChatGPT remains an option when validating a release. Plugin Creator itself is not a comprehensive functional test runner.
- Keep project PPFs, screenplay files, media, credentials and provider tokens out of this source archive. Personal story data belongs in authorized ChatGPT Project/Library records.
- Keep the current release recoverable and preserve historical commits. Never silently overwrite the published release based on this repository.

## Current published release

**v0.8.40** — Plugin Creator release `pluginrel_6af23bf39cac8191bff7ea118b147b40`, published 2026-11-09 UTC. The exact authorized six-file text-source overlay was archived to [GitHub commit ec7a1b6](https://github.com/BryanHarrisScripts/PlotPickle-Studio/commit/ec7a1b64245ae7bb09453351e2dcb834eb5a7860) only after publication. The original plugin identity and PRIVATE sharing audience are retained; both manifests and the added fal Player skill were read back from the installed release.

v0.8.40 adds native fal in-chat viewer routing (using the separately connected fal app rather than a new embedded player), safe approved multi-shot generation/recovery, saved fal media readback and a no-spend 1–5-shot local H.264/24fps editorial conform helper. The helper passed a synthetic three-shot, 216-frame, nine-second integrity test with stale-source and overwrite rejection. The actual three-shot fal provider generation and fal-library readbacks were completed separately; **their MP4 bytes were not independently downloaded into the ChatGPT runtime or imported into the connected editor**, so live 24fps video/export acceptance remains pending. The personal The Third Bell source PPF, media and private job receipts are not in GitHub.

The earlier [v0.8.39 cumulative text-source archive](https://github.com/BryanHarrisScripts/PlotPickle-Studio/commit/dcba2d5a74f76b580d53a9304da329c77f6115f4) remains preserved. Its specific 142-file comparison applies to v0.8.39, not a full new byte-by-byte v0.8.40 package audit. Historical private plugin archives remain available from Plugin Creator and binary/source exclusions remain documented in [the v0.8.37–v0.8.39 reconciliation](docs/archive/2026-11-09-v0.8.37-v0.8.39.md). No CI, GitHub release gate or separate hosted sidebar was introduced.

See [RELEASES.md](RELEASES.md) for release-to-archive references. Future source snapshots should be appended only after publishing through Plugin Creator.

Licence: GNU Affero General Public License v3 (see LICENSE). Preserve third-party notices.
