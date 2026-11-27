---
name: plotpickle-surface-library
description: Reuse versioned in-chat PlotPickle Studio surfaces (HOME, Storyboard, Library / Your Stories, Review, Editor) with locked Skin V2 navigation, verified tool data, and safe interactive controls.
---

# PlotPickle Studio — Surface Library v1.0.0 (plugin 2.0.40)

**Purpose:** Permanent, versioned, portable source-of-truth package for in-conversation surface assembly. This is **not a hosted website, browser panel, new MCP server, or a compiled UI runtime**. It is a reusable spec and set of host-supported interaction templates; ChatGPT still renders them per turn. Loading this skill alone is not proof of host acceptance.

## Fast reference (always use this route)

1. Read `references/registry.v1.json` for exact surface IDs, order, authority, source tools, and approval states.
2. Read only the requested `references/surfaces/<ID>.md`, then `templates/<ID>.dil.md`; do not reinvent layout/order.
3. Before presenting private story contents, query real authenticated PlotPickle Studio tools as documented. Never render invented project names, counts, images, source hashes, locks, video or waveform data.
4. Show responsive in-conversation controls where supported. **Local selection** changes only the card preview; actions requiring storage must issue a **normal explicit user-intent turn** for version-guarded tools and independent readback. A click is not proof of a saved change.
5. For HOME (`Home`, `Studio`, `Open Studio`, `Open Studio HOME`, `/home`) always show the **same exact five-card Skin V2 HOME**. Library / Your Stories is card 4, Connected Services card 5. Never split aliases into chat-vs-panel modes or open Work, a tab, or second login by default.

## Status and scope

- HOME / Library: **creator-locked Skin V2**; original approval `PP-SKIN-V2-HOME-LOCK-2026-11-13-01` remains unchanged.
- Storyboard / Review: **inherited previously approved Skin V1**. Preserve 4 Acts / 12 sequences / 24 blocks / 96 mini-blocks, 25 *positions* per mini-block, 5×5 grid and four independent review statuses; these are plans, not proof of media.
- Editor: **registered draft view**, not an owner-approved visual lock. Its underlying six-lane 24 fps engine and guardrails remain preserved.
- Existing `plotpickle-skin-v2`, `plotpickle-skin-v1`, `plotpickle-interactive-storyboard`, `plotpickle-review`, `plotpickle-editor`, `read-plotpickle-project` remain canonical for their specialist behavior. Conflicts resolve in favor of Skin V2 for HOME and Skin V1 for its approved child layouts.
- Store **no user PPF, project ID, screenplay, WebP/MP4/MP3, private session data, tokens or credentials** in this library. The logo stays at its existing approved locked asset path and is not duplicated.

## Safety gates

Opening Home, Storyboard, Library, Review, or Editor is read-only. Use actual project ID, source revision/raw SHA, selected asset hash, and Studio expected revision before mutations. Selection is not approval. Studio sidecar edits do not write native Library PPF. Review image provenance independently; display `Unknown` when unavailable. Request-generation never means credit spend. Renderer-dependent gestures, audio/video playback, or per-device UI support require independent tests.

`python3 scripts/resolve_surface.py HOME` produces a deterministic *public layout skeleton* for inspection, not a private-state render. `python3 scripts/test_surface_library.py` checks structure, routing, immutability, approvals and template coverage. See `references/interaction-contract.md` and `references/CHANGELOG.md`.
