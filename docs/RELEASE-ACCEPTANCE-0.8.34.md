# PlotPickle Studio v0.8.34 — release acceptance

## Installed conversational plugin acceptance — verified after publication, 2026-11-08

This section is the current release record. The remainder of this document records earlier pre-release investigation and MUST NOT be interpreted as today's plugin version.

- Released the existing private USER plugin **v0.8.34**, same backend identity `plugins_6aedd4f5ac1481919653cf6110d565ba`. Verified release ID: `pluginrel_6af102a657b08191b07da5b8d64be07b`. Not a second or replacement plugin.
- Retrieved Plugin Creator's live plugin manifests after publication. Both report `0.8.34`, display name `PlotPickle Studio`. The new in-chat continuation skill and read-only portable ZIP media verifier are present, and the existing private The Third Bell seed is still readable. Older v0.8.33 remains in release history.
- The owner reported **"tested and good"** after ChatGPT testing. This is affirmative user-reported acceptance of the working conversational plugin experience, NOT independent proof that the graphical sidebar has an authenticated host, that mobile media recovery and native Save/Lock work, or that a finished MP4 is stored.
- Source and release have a focused difference: the published overlay included the new `skills/plotpickle-chat-first/SKILL.md` and a smaller installed portable-media verifier. This sync change records those **exact installed text bytes** and aligns synthetic test calls; `plugin.json` in GitHub was already byte-identical to its installed counterpart. It does not add private story media.
- Initial private media acceptance (131/131 images from a real saved Brotherly Love PPF + portable ZIP) was verified in ChatGPT execution outside the installed plugin host; it does not certify plugin-host media loading. No provider spend is implied.
- Sidebar hosting, cross-device persistent reopening, native Save→Lock writes and MP4 provenance remain **separate feature-specific acceptance gates**. The optional sidebar is not a release gate for a working conversational plugin.
- Prior v0.8.33 history and source backup should remain available. A listed historical release is a recovery option, but rollback was not exercised during this successful update.

### Release disposition

**Conversational plugin v0.8.34: PUBLISHED AND USER-TESTED. Optional hosted sidebar: NOT VERIFIED. Native storage/media/Save-Lock features: ONLY as separately demonstrated.**

---

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

The real saved project was ALSO processed through the actual Studio `createProjectLoader` and read-only `projectStudio` adapter using the exact native reader in the ChatGPT execution environment. It returned `status=source-backed`, correct source identity/hash and revision 539, 383 passages, 16 source scenes, 10 people cues, 16 distinct places, 125 storyboard positions, 300 evidence relationships, and `readonly=true`. The source hash stayed unchanged. This establishes source-level Studio loader integration with a real saved PPF, **not** official ChatGPT sidebar/plugin-host execution, account-authorized durable reopen across devices, native PPF persistence, or real media-byte recovery. A synthetic end-to-end import -> reader -> Studio projection test is included for source integration; it cannot substitute for real host acceptance.

## Independent Library media recovery in a fresh conversation (2026-11-08)

This is **new evidence beyond the earlier native reader / source projection tests**. In a fresh ChatGPT conversation, the owner-authorized `brotherly-love.ppf.json` and its separately stored `Brotherly-Love-New-Artwork-Storyboard.zip` were materialized from the user's private ChatGPT Library into an isolated execution environment, without modifying their originals or publishing them to GitHub. The saved PPF parsed at revision 539 (1,468,305 bytes). Its asset registry identified 131 WebP image variations with portable paths, recorded byte lengths and SHA-256 content hashes.

All 131 corresponding WebP files were independently located in the owner archive and read byte-for-byte. Each file matched its recorded byte length and SHA-256 hash, and its RIFF/WEBP signature was checked. The total validated image payload was **190,630,642 bytes**; there were **zero missing or mismatched files**. The source PPF remained byte-identical after verification. A detailed machine-readable verification receipt was returned privately to the owner, not committed.

**Scope limitation:** this proves cross-conversation Library file retrieval and authentic image-byte correspondence to one real PPF/portable asset package. It does **not** prove that the published v0.8.33 plugin itself reopened the project, that the v0.8.34 Studio sidebar is installed, that mobile host transport works, that native Save/Lock has persisted, that fal MP4s are recovered, or that the Plugin Creator backup/archive and rollback have been independently validated. Those release gates remain open.

## Studio identity

- New, independently authored Studio composer icon and wordmark in `assets/studio-composer-icon.svg` and `assets/studio-logo.svg`, rendered to PNG using pinned CairoSVG.
- Both plugin manifests point to `assets/studio-composer-icon.png` and `assets/studio-logo.png`, not the original desktop artwork.
- User-visible name becomes PlotPickle Studio; backend identity stays `plotpickle-story-reader` to preserve plugin continuity.

## Release blocks

- [x] Source merged to Studio GitHub and exact canonical reader hash verified (PR #3).
- [x] Real private ChatGPT Library PPF read, fail-closed identity, source paging, 25 shots and nonmutation verified.
- [x] Public test story synthetic; private creator The Third Bell seed not published to GitHub.
- [x] Studio branding PNGs built, committed to the release branch and CI verified (reproducible SVG sources retained).
- [x] A **private, unpublished** v0.8.34 candidate archive assembled in the ChatGPT tool environment by overlaying release manifests and new Studio assets on the owner-supplied v0.8.33 backup, retaining the original private The Third Bell seed and exact reader. The original logo/icon are excluded from the candidate.
- [ ] Validate 0.8.34's plug-in packaging against real Plugin Creator host acceptance.
- [ ] Confirm real ChatGPT plugin UI integration including real read-only PPF reopen and private media provenance.
- [ ] Original private v0.8.33 archive checksum rechecked (SHA-256 `5838a10ec530959635c787d6dd0391c7aabcf740e0e6870950cff103dc4c7dc3`); rollback under the actual Plugin Creator host is **not** yet verified.
- [ ] Publish guarded 0.8.34 update only after independent acceptance; verify returned release ID and current version.

Local private candidate passed all 13 existing Studio pilot tests and syntax checks. Synthetic native importer → canonical reader → Studio projection integration also passed the GitHub Actions source workflow. The private candidate must be reconciled against the final GitHub-generated branding PNG bytes before publication. When calling Plugin Creator's overlay update, explicitly list the original `assets/composer-icon.png` and `assets/plotpickle-logo.png` in `delete_paths`, since omission from an overlay archive does not delete old plugin files. **Do not** delete the private `the-third-bell-seed.json` as part of public source cleanup.

Passing source tests or rendering assets is NOT deployment; never claim this is a release-ready user experience until the actual Plugin Creator install/verification succeeds.
