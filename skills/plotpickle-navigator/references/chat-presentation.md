# ChatGPT-native Story Explorer presentation — v0.8.15

## Purpose and availability

When a user wants a graphical interface inside ChatGPT, present a compact, interactive *in-chat* Story Explorer if the current host supports native interactive layout and controls. This is a presentation layer, not a standalone Windows app, installed fixed dashboard, hosted web page, or replacement for project storage. The earlier dark grid and 4 mini-block buttons are visual references, **not** authoritative project state. If native host controls are unavailable, use a compact graphical-like text view with real per-level links or choices; never claim a clickable UI was displayed unless the host actually rendered one.

## Structure: disclosure without clutter

Use the user's matte-black console aesthetic where supported: clear restrained borders, compact labels, green active indicator, neutral/grey unknown state, and intentionally sparse accents. The visual interaction should fit the conversation rather than demand a separate launch or site. Keep the four HOME choices unchanged.

1. Act strip: I / II / III / IV (4 total). An act click selects that act, and resets *only subordinate navigation choices* to its first Sequence and Block, not story identity or canon.
2. Within the selected Act, show three Sequence cards. Each contains the two canonically related Blocks (globally numbered, do not reset global block IDs per Act). Use source-supported names and dramatic shifts only. If no named Sequence exists, use `Sequence 01` and `Name not established`.
3. A selected Block card shows four mini choices 1–4 and their observed evidence status. Do not count accepted visual anchors without actual observations.
4. A selected Mini-Block exposes the 5×5 grid of 25 *planning positions*; click to select one position.
5. Selected shot shows tabs or a tidy stacked detail: Script / Source evidence, Beat, Prompt, Image candidates, Production, Continuity and Save/Lock. For each, show actual stored data and provenance, or `Not recorded` / `Not verified` if absent. A storyboard image is not a screenplay passage. Do not infer Lock or approval from a preview image or chat attachment.
6. Add breadcrumbs: Story > Act > Sequence > Block > Mini > Shot; provide Back and Overview when useful. In-chat controls are session-only selection, not durable writes.

## Data contract and calculations

Use `scripts/story-explorer.py` for source-backed, identity-pinned navigation and the canonical `storyboard-review.py` reader for image observations. Each view must carry project identity, exact revision, source hash, and chosen address. A name, UI card and visual status are *not* evidence of source content. The canonical map is 4 Acts × 3 Sequences each × 2 Blocks each × 4 Mini-Blocks each × 25 planning positions (2,400). Global Block number = `(act - 1) * 6 + (sequenceWithinAct - 1) * 2 + blockWithinSequence`, global Sequence number = `(act - 1) * 3 + sequenceWithinAct`.

Status labels: `DEFINED` only for an actual supported record; `OBSERVED` for independently checked existence; `EMERGING` for proposal/draft; `AVAILABLE` for an action that can actually be performed; `BLOCKED` for a verified unmet requirement; `UNKNOWN` for inaccessible/unverified state. Color never replaces text. Do not apply `NEEDS SUPPORT`, `0/4` or other image-demo statuses to a new story without source evidence.

Preview-only mode when the project has no attached verified PPF: identify it as `INTERACTIVE PREVIEW — NOT CONNECTED TO SAVED PROJECT`. Navigation may work locally in the message, but show empty shot evidence faithfully and avoid implying that the preview is registered with the plugin or the ChatGPT Project. If relevant, use source text and artwork attached in current chat with labels identifying them as unregistered references. Do not fake 25 independently generated images.

## Interactions and writes

On UI selection, keep client-side state for Act/Sequence/Block/Mini/Shot, all relative to the same selected saved source. A drilldown click must not invoke an API call, produce media, update PPF, save or lock anything. If a user chooses an actual editing action, collect the intended change and proceed through existing project write APIs and explicit Save → Lock checks, with snapshot re-read; no fake local success toast. Distinguish passive view from actions. Host-supported previews may lose transient UI state when the conversation rerenders or is reopened. Persistent resumption depends on saved project files, not the rendered card's state.

Do not use a static mockup image when native interactive controls can meet the request. A static screenshot or image can be provided as an optional visual reference but must not impersonate a functioning UI. When rendering many items, show just the selected Act's three sequences and selected Mini's 25 slots to avoid 2,400 buttons. Display titles from saved source where possible, never from the legacy screenshot by default.

## Mobile integration and portable export (v0.8.16)

Reproduce the compact in-chat graphical hierarchy using actual PPF data and host-supported controls. Under ~630 px, use single-column Sequence and Block cards, not fixed 3-column Sequence cards (which caused broken words and overflowing labels on iPhones). The interactive chat element is a presentation projection for the current response; it does not install a permanent ChatGPT screen. A portable `.ppf.json` package can include a regenerated `Story_Explorer.html` and relative asset folder for a functional, standalone offline viewer. The renderer is read-only and verifies SHA-256 of referenced images; it does not change canonical source, Save/Lock or approval. The source PPF must be parsed/validated by the native reader separately before describing it as accepted PlotPickle truth.

## Current source and status routing (v0.8.17)

If the story package is saved in the user's personal Library and current Project files are absent, locate its exact `.ppf.json` there and label the source as Library. Never silently claim that the Library folder is a ChatGPT Project. Render the same evidence panels with the source-backed records rather than a hard-coded example. When the host provides no way to attach the source to a Project, offer the user the verified package and concise manual steps. In responsive in-chat layouts, stack Sequence cards on mobile to prevent letter-by-letter title wrapping.
