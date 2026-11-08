# PlotPickle Studio

The ChatGPT-native PlotPickle creative production plugin. This repository is intentionally separate from [PlotPickle](https://github.com/BryanHarrisScripts/PlotPickle), the original Windows desktop / Story Factory project.

## Migration state: v0.8.33 source candidate

The first import is pinned to the published private ChatGPT plugin `plotpickle-story-reader`, release `pluginrel_6af0b8fb4dec819181b70bcd777f9963` (version 0.8.33, published November 8, 2026).

The imported text source includes the plugin manifests, skills, instructions, workflow schemas, scripts, tests, creative service catalogue, 81-lesson curriculum data, Studio pilot and local editor source. This is **not yet a reproducible, independently verified release**. See [docs/MIGRATION.md](docs/MIGRATION.md) for the five intentionally omitted generated, binary or media-bearing files and the acceptance checklist.

The live ChatGPT plugin is not automatically updated by changes to this repository. Existing private story projects, user media and credentials do not belong in source control.

## Repository boundaries

- **PlotPickle Studio**: ChatGPT plugin UI, Elara guidance, REEL and ONCE, story navigation, connected services, creative and media-production workflow sources.
- **PlotPickle (original)**: legacy desktop app, Windows execution, Software Factory, prior historical development records, and all original PlotPickle logos, images, diagrams and brand assets. None of these visual assets are being migrated to Studio.
- **Interoperability**: use explicit, versioned PPF and media contracts rather than implicit shared directories or duplicate private story stores.

## Release discipline

1. Create and approve Studio-specific icon/logo assets, verify them, and restore the canonical reader bundle. Do not copy original PlotPickle branding.
2. Remove sample private media references and reconcile manifests to this repository.
3. Run skill/script tests and full package build from a clean checkout.
4. Compare the built package with the intended release manifest and verify ChatGPT host acceptance.
5. Explicitly publish a new semantic version to the existing PlotPickle ChatGPT plugin and independently verify its release ID.

Until these steps pass, **the published v0.8.33 plugin remains the deployed source of truth for runtime behaviour**, while GitHub tracks the migration candidate. The new GitHub repository becomes the development source of truth only after the first verified release.

Licence: GNU Affero General Public License v3 (see LICENSE). Preserve third-party notices and comply with dependencies' individual licences.
