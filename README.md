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

**v0.8.39** — Plugin Creator release `pluginrel_6af22335cf948191a60264f0b542c4c9`, published 2026-11-09 19:47 UTC. The current public text-source archive is [dcba2d5](https://github.com/BryanHarrisScripts/PlotPickle-Studio/commit/dcba2d5a74f76b580d53a9304da329c77f6115f4), created only *after* Plugin Creator publication. It includes the cumulative source changes introduced by published v0.8.37–v0.8.39.

A source audit compared 142 readable installed UTF-8 text files with GitHub MAIN: 124 were already identical and 18 were mirrored exactly in the archive commit. This is a **public text-source mirror**, not a complete byte-for-byte copy of the private plugin archive. The private creator story seed, original nonpublic artwork, generated assets and a Python bytecode cache remain outside GitHub. The installed Studio logo PNG differs from the historical GitHub logo PNG and is not declared reconciled; the 1.36 MB canonical inspector was not re-read through the 1 MiB Plugin Creator text API during this audit. Original Plugin Creator archives retain release-specific binary data. See [the reconciliation record](docs/archive/2026-11-09-v0.8.37-v0.8.39.md).

Historical v0.8.37 and v0.8.38 release IDs are recorded in [RELEASES.md](RELEASES.md), with exact release timestamps and an explicit distinction between their retained private archives and this cumulative v0.8.39 GitHub source snapshot. The preceding [v0.8.36 archive](https://github.com/BryanHarrisScripts/PlotPickle-Studio/commit/9f46cfb29e3b0bf7d6deccf6b5dd0cdee014029b) remains in Git history.

See [RELEASES.md](RELEASES.md) for release-to-archive references. Future source snapshots should be appended only after publishing through Plugin Creator.

Licence: GNU Affero General Public License v3 (see LICENSE). Preserve third-party notices.
