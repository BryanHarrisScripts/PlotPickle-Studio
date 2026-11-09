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

**v0.8.36** — Plugin Creator release `pluginrel_6af12eac3bfc8191bcf844e1c4719aac`, published 2026-11-09 UTC.

The preceding GitHub source mirror is commit [9f46cfb](https://github.com/BryanHarrisScripts/PlotPickle-Studio/commit/9f46cfb29e3b0bf7d6deccf6b5dd0cdee014029b). This historical commit is retained for recovery. Its exact byte-for-byte equality to the Plugin Creator archive has not been re-audited by this policy change.

See [RELEASES.md](RELEASES.md) for release-to-archive references. Future source snapshots should be appended only after publishing through Plugin Creator.

Licence: GNU Affero General Public License v3 (see LICENSE). Preserve third-party notices.
