---
name: plotpickle-assets
description: Use for PlotPickle Assets: character, world, collectible, poster, Foley, narration and music libraries; asset inventory, media verification, creative requests, provenance and portable exports.
---

# PlotPickle — Assets (v0.8.21)

Entry: **Storyboard → Assets**. Inspired by the original desktop **ASSETS** menu. Show the following internal catalogue in the project's human workflow: **Characters**, **World**, **Collectibles**, **Posters**, and **Sounds** with **Foley**, **Narration**, **Music**. Also expose associated storyboard frames and motion clips as project-linked media views, not a new competing registry. Posters route to `../plotpickle-posters/SKILL.md`; Character/World creation and Layout Sheets route to `../plotpickle-design/SKILL.md`; soundtrack briefs route to `../plotpickle-creative/SKILL.md` and current authorized music provider when requested.

## Asset identity and media boundaries

Use `../read-plotpickle-project/SKILL.md` and existing `assetRegistry`, `build.foundations.visualArtifacts`, and saved workflow image mappings. The PPF is the project record, not a proof that external media bytes exist. Keep stable asset and variation IDs, approved/accepted evidence, project revision and source passages. Avoid a second asset database, never infer approval from matching a title or working filename. For asset files supplied alongside the PPF, independently check path containment, presence, bytes, and SHA-256 before saying **verified bytes**. If the user only provides references, show **metadata only / media unavailable**. An `acceptedVisualArtifactIds` record is distinct from `locked` and `savedMarkerPresent`; report all separately. Do not infer a story shot ID from numeric filenames.

Character and location catalogues may be derived from actual screenplay cues/headings as *names only*. A generated visual design is a proposal until the user reviews it, the bytes are verified, and any native Save/Lock operation succeeds in a new separately saved PPF. Collectibles and Sounds retain their destination names even if empty. Posters remain marketing assets and do not become storyboards automatically. For Foley, Narration and Music, do not claim a playable file, license, speaker identity, audio measurement or provider credit balance without actual media and authorization.

## User actions

Show **Browse Assets**, **Build Character**, **Build World**, **Create Poster**, **Create Collectible**, **Prepare Foley**, **Prepare Narration**, **Prepare Music**, **Audit Missing Media**, **Export Asset Inventory**. Each action produces real source-linked proposals or artifacts in ChatGPT, not a fake desktop navigation route. Generate images using the image tool when explicitly requested; preserve approved reference continuity and show drafts for review. Use available audio provider only when actually connected and user authorizes any spend. A change to asset records requires the guarded native project mutation workflow and a durable new version; browsing is read-only.

Portable command: `python3 scripts/assets.py --project story.ppf.json [--assets-root path] --format json --out inventory.json`. It inventories recorded assets and verifies matching local media where supplied. A report of `missing` or `not-supplied` is not a deletion instruction. It does not upload, move, link, approve, generate or save media.

## Validation

Run `python3 scripts/test-assets.py` and inspect a source-backed sample. Asset presentation can be provided as clickable in-chat cards, but these are transient UI, not a permanent host-installed library. Do not imply synchronization with the original Windows desktop application.
