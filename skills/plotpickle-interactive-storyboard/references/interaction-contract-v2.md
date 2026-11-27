# Interactive review contract v2.0.31 — chat-first, no extra panel

## Layout
Collapsed card shows verified saved title (otherwise generic), mini-block when known, current shot 01–25 and Expand. It is not a screenshot or a source image. Expanded view is one in-chat carousel with 25 positions, swipe/arrow access, five page buttons and a five-by-five selection grid; selected shot remains selected through Expand/Collapse. Inspector is a collapsible local surface with Script / BEAT / Visual / Continuity / Production / Status tabs. All are in the current ChatGPT message, not an OS drawer or a separate Studio tab.

## Latency
Local controls change locally without a new Elara response. New turns are reserved for: inspecting fresh verified source, image read, discussing changes, or an explicitly authorized guarded write. Do not send model requests from a swipe/shot selection/page switch; do not perform MCP writes or paid provider actions as a gesture side effect.

## Source boundary
A saved inactive project can be displayed as a navigation-only preview. Actual original story image bytes, screenplay excerpts, narrative BEATs and source Save/Lock states appear only after authenticated source inspection. `25 images verified in catalogue` is not `25 images loaded in this view`. The current Studio workspace can be empty without deleting the saved catalogue. Source PPF writes are distinct from Studio sidecar actions.

## Handoff
The read-only `Review this shot with Elara` control issues a new chat message containing story title, active/inactive status, Mini-Block address if known and shot number, asks Elara to recheck current source and *not* switch projects. Opening a saved project requires a separate explicit user selection. An approval request is not a persistent lock. A regeneration request is not a paid job authorization.

## Test matrix
- Read-only saved film: 25 slots navigable, no accidental import/switch/write.
- Expand/Collapse: stable selected shot; drawer can independently open/close.
- Swipe and arrow: same selected shot and page; first/last controls safely bounded.
- Page buttons: page k selects shot 5(k−1)+1; still 1–25 globally.
- Inspector: six tabs share shot selection; unknown fields reported as Not loaded/Not checked.
- 'Review with Elara': explicitly creates a normal new turn, with source readback before any action.
- iPhone: single-column, tap-friendly, swipe does not hijack OS gesture; keyboard arrows/buttons fallback.
- Data invariants: no source PPF or Studio revision changes from preview; no paid jobs, no new login, old editor remains.
- Separate acceptance: real original media, save/lock readback, regeneration cost authorizations, six-track operations and hosted app UI require additional implementation; never mark those complete from skill update alone.
