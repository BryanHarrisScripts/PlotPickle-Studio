# PlotPickle Studio v0.8.34 — release acceptance

Source authority: November 8, 2026 Studio engineering briefs in `docs/direction/`. The original desktop PlotPickle remains separate. The live ChatGPT plugin v0.8.33 remains published until Plugin Creator accepts a verified replacement.

## Actual saved creator story: private ChatGPT Library acceptance (2026-11-08)

- Exact published v0.8.33 canonical reader has SHA-256 `6c9c239f4484d2cd624bfd1c761fa8645203cc8e78be1d58b11ec2500a5f498f`.
- A real saved PPF from the author's ChatGPT Library was materialized in an isolated ChatGPT execution workspace (not committed).
- Reader identity accepted the actual PPF, revision 539, source file hash pinned and independently rehashed.
- Reader summary reported 383 retained screenplay passages and the established 4 Act / 12 Sequence / 24 Block / 96 Mini-Block planning structure.
- The first Mini-Block returned 25 read-only storyboard observations. Source paging also succeeded.
- Wrong SHA and stale revision both failed closed with `FILE_IDENTITY_OR_REVISION_CHANGED`.
- The source bytes before and after reads were identical. `canonMutated` was false.
- Reader explicitly reported `mediaBytesVerified=false` and `liveVaultReadVerified=false`; those are not success claims. Actual images, video assets and Saved/Locked media were not independently reverified.
- A different library PPF failed `RAW_STRUCTURE_UNVERIFIABLE`; do not silently repair/relax the canonical reader for that source.
- No private story project, real screenplay passages, asset URLs, or project hashes are recorded in this public repository.

This acceptance proves native reader execution inside a ChatGPT tool environment against one real saved project. It does NOT establish ChatGPT sidebar/plugin host execution, account-authorized durable reopen across devices, native PPF persistence, or real media-byte recovery. A synthetic end-to-end import -> reader -> Studio projection test is included for source integration; it cannot substitute for real host acceptance.

## Studio identity

- New, independently authored Studio composer icon and wordmark in `assets/studio-composer-icon.svg` and `assets/studio-logo.svg`, rendered to PNG using pinned CairoSVG.
- Both plugin manifests point to `assets/studio-composer-icon.png` and `assets/studio-logo.png`, not the original desktop artwork.
- User-visible name becomes PlotPickle Studio; backend identity stays `plotpickle-story-reader` to preserve plugin continuity.

## Release blocks

- [x] Source merged to Studio GitHub and exact canonical reader hash verified (PR #3).
- [x] Real private ChatGPT Library PPF read, fail-closed identity, source paging, 25 shots and nonmutation verified.
- [x] Public test story synthetic; private creator The Third Bell seed not published to GitHub.
- [ ] Studio branding PNGs built, committed and CI verified.
- [ ] Exact updated plugin full archive prepared from GitHub source/owned original release with all needed assets.
- [ ] Validate 0.8.34's plug-in packaging against real Plugin Creator host acceptance.
- [ ] Confirm real ChatGPT plugin UI integration including real read-only PPF reopen and private media provenance.
- [ ] Recheck privately retained 0.8.33 archive checksum and confirm safe rollback is possible.
- [ ] Publish guarded 0.8.34 update only after independent acceptance; verify returned release ID and current version.

Passing source tests or rendering assets is NOT deployment; never claim this is a release-ready user experience until the actual Plugin Creator install/verification succeeds.
