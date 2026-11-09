# v0.8.35 — in-chat Review controls and portable workspace

Owner accepted the dark Shot Review design and authorized implementation on November 8, 2026.

## Proven private project recovery

A real Library-owned The Third Bell `project.ppf.json` and versioned full project ZIP were retrieved by authorized tools. The PPF inside the ZIP is byte-identical to the separate saved file; its 25 original source WebP assets were each individually read from the ZIP, SHA-256 checked against their PPF shot mapping and portable asset registry, decoded with Pillow and verified at 1280×720. No mismatches were observed. The original PPF revision is 0 with no saved or locked images. This establishes authentic portable source byte recovery, not official hosted MCP Apps storage or native PPF Save/Lock write acceptance. The real PPF and images are private and are **not** included in public GitHub.

A mobile-friendly standalone HTML Review workspace was generated from the source and tested with real images using Chromium/Playwright. It displays all 25 original images and eight separate newer conversation-side concept candidate thumbnails. Shot selection, local draft approval, regeneration request, queued Save→Lock intent and JSON draft export were exercised in browser tests. It NEVER modifies native PPF or runs a provider. Its source-pinned review records are explicitly uncommitted drafts. The portable UI and source verification JSON were saved to the owner's Library at `/The Third Bell/Review/`.

## Release scope

v0.8.35 adds `skills/plotpickle-review/SKILL.md` to the **existing private conversational plugin** and surfaces a new direct Review entry prompt. It does not replace HOME/REEL/ONCE or force a Windows app, new GitHub storage, or separate provider account.

A true hosted ChatGPT native sidebar requires deployment of official MCP Apps UI registration, authenticated per-user project transport, current-project read/write loader, verified media address resolution, compare-and-swap owner-owned project persistence and independent readback. Plugin Creator skills overlay alone cannot turn that source-only MCP registration seam into a hosted sidebar. Keep all four graphic controls disabled there until those conditions are satisfied. A document/HTML viewer does not establish the host.

Real native Save/Lock in the Project/Library requires running the canonical native reader and image workflows with current source identity, making an authorized durable write and reading back actual bytes. If that is unavailable, the assistant can still collect a review-draft event and write it to private Library as a separate artifact, but must not mark the PPF locked. Never convert conversational approvals into old PPF selection flags without exact candidate choice.

## Acceptance matrix

- Source/manifest integrity: two manifests version 0.8.35, existing plugin identity, same Studio branding and retained 21 previous default prompts plus one new Review prompt.
- Source CI: must pass before any guarded release.
- Human mobile acceptance: previously confirmed v0.8.34 HOME, REEL and ONCE remain unchanged; v0.8.35 still requires an independent user check.
- Private data: source PPF, images, review choices and private The Third Bell seed never checked into public GitHub.
- Native hosted sidebar: NOT YET DEPLOYED.
- Portable Review: FUNCTIONAL LOCAL DRAFT AND EXPORT, not native Save/Lock.
- Native durable Save/Lock for Third Bell: NOT YET EXECUTED.
