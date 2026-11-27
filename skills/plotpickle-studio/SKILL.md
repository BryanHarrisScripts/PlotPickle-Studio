---
name: plotpickle-studio
description: Owner-locked unified interactive PlotPickle HOME in the current ChatGPT conversation with Elara; Skin V2 five-choice layout, permanent versioned Surface Library, and authenticated MCP engine underneath.
---

# PlotPickle Studio — unified in-chat application (plugin v2.0.41)

## Owner locks — mandatory

Read `references/locked-interface-agreement-v1.1.md` and `../plotpickle-skin-v2/SKILL.md` before responding to `Home`, `Studio`, `Open Studio`, `Open Studio HOME`, or `/home`. All aliases open the SAME in-conversation interactive HOME. One plugin, one Elara, one account-bound backend. No mandatory panel, browser tab, website, Work mode, extra login or separate ChatGPT conversation.

**Permanent fast-reference Surface Library:** read `../plotpickle-surface-library/SKILL.md` and its `references/registry.v1.json`, then the requested surface spec/template. Library version 1.0.0 covers `HOME`, `STORYBOARD`, `LIBRARY_YOUR_STORIES`, `REVIEW` and `EDITOR`; reusable specs/templates do not independently deploy UI or authorize actions. Do not regenerate a conflicting layout.

**Skin V2 HOME has exactly five selectable cards, in order:** 1 Meet Elara; 2 Learn; 3 Storyboard; 4 **Library / Your Stories**; 5 Connected Services. Approved and locked 2026-11-13 under `PP-SKIN-V2-HOME-LOCK-2026-11-13-01`. Skin V1 child Storyboard/Image Review rules survive; Editor layout is documented draft, not visually locked.

Use host-supported real in-chat controls and local selections; project/review/edit actions require exact authorized tool calls, version/hash guards and readback. A successful tool response by itself does not verify a rendered UI. HOME entry is read-only.

For routine HOME requests in ChatGPT, use the branded chat HOME template in `../plotpickle-surface-library/templates/HOME.dil.md` and accept a reply by number or name. The hosted Studio link is optional. Call `open_chat_home` only when the user explicitly requests interactive cards or the inline panel. Reserve `open_studio_home` for an explicitly requested sidebar. If the requested panel fails or its render is unconfirmed, keep the branded HOME available and describe the panel status accurately.

## Intent → real authenticated source

| Intent | Tool | Boundary |
| --- | --- | --- |
| HOME / Studio / aliases | Show the branded chat HOME; use `open_chat_home` on explicit request for embedded controls | No project switch or write |
| Library / Your Stories | `studio_list_projects` + `studio_get_state` | Saved catalogue vs unverified references; no live Library-wide scan |
| Explicit Open Film | `studio_check_project`, `studio_get_state`, guarded `studio_open_project` and readback | Selection must be explicit; exact source/revision |
| Learn | `studio_list_lessons`, `studio_get_lesson` | Real 81 lessons / 12 topics, no invented progress |
| Storyboard / Review | `studio_get_state`, `studio_get_image`, `studio_get_beat` | Exact image + BEAT provenance; no fabricated media |
| Approve / Lock / Undo | revision-guarded `studio_apply_action`, independent readback | Native Library PPF never silently changed |
| Editor / Render | `studio_get_state`, `studio_prepare_render`, `studio_get_render` | 6 lanes, 24 fps, real draft evidence only |
| Image / motion / music | authorized provider calls only after current prices and explicit job consent | No spend from view navigation |
| Connected Services | `studio_get_core`, actual provider status if connected | Backend listing ≠ provider credit verification |

## Guardrails

Before any project-specific mutation read current project ID, source revision/SHA-256, media SHA and Studio expected revision. Do not infer active project from memory. Keep all existing story copies, media, BEATs, approvals and six-lane edits. No new provider charges or private files in plugin. Missing in-chat gestures/playback, automatic Library access and native PPF writeback are separate acceptance gaps. Read `references/chat-first-acceptance.md`, `../plotpickle-skin-v2/references/surface-sitemap.md` and the existing specialist reader/review/editor skills.

## Engineering releases and storage (v2.0.41)

Before design changes, developer work, version bumps or publication, use `../plotpickle-release-lock/SKILL.md`. The one version-linked `../plotpickle-release-lock/references/release-index.v1.json` tracks affected surface lock IDs, patterns, invention identifiers, verified tests, authorizations and rollback references. Validate and check the release gate before calling a version LOCKED or suitable for live deployment. **No per-version private archives, user-story media copies or parallel engineering DB.** Continue to distinguish a working release package from actual Site/MCP deployment and user acceptance. Internal patent/invention records are not legal patent filings or registrations. Never silently change the approved HOME layout or overwrite creator story data.
