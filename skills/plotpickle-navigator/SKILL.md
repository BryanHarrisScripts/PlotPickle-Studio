---
name: plotpickle-navigator
description: Navigate an existing PlotPickle story from story to Act, Sequence, Block, Mini-Block and 25 shot positions, down to screenplay evidence, authored beats, stored prompts, image candidates, continuity and Save/Lock. Read-only source-pinned drilldown; no fabricated authored content or native application UI claims.
---

# PlotPickle — Story Explorer / progressive drilldown (v0.8.15)

This skill adds a Storyboard navigation pathway, not a fifth HOME choice. In ChatGPT hosts that support native controls, prefer the visual, interactive in-chat presentation described in `references/chat-presentation.md` when a user requests a graphical drilldown. Preview navigation does not imply a persistent hosted UI or project write. It combines the user's three legacy designs:

1. **Top rail**: four Acts. Only the selected Act is highlighted. Use explicit active-story title and saved revision; when unverified, say so. Act I–IV each has six Blocks.
2. **Act map**: three Sequences grouped into two Blocks each; display Block 01–06 as selectable cards with four Mini-Block choices. The sequence grouping is 01–02, 03–04, 05–06 (within an Act). The names, thematic shifts and statuses come from saved story evidence, never assumed based on the example screenshot.
3. **Block workspace**: four Mini-Block cards with real image/status previews; opening one shows source scenes and separately authored beats, with a 5×5 grid of 25 storyboard positions. Clicking a shot reveals the detail panel.
4. **Shot evidence panel**: exact scene/paragraph ID and retained text, independently authored beat if one exists, narrative purpose or allocation proposal, canonical shot address, exact stored image-generation prompt with provenance, candidate images, visual approvals, file/hash verification, Save/Lock, style/lighting/camera and continuity/handoff, narration and motion-span linkages when actually recorded. Label an absent item `Not authored` or `Not verified`, not a fabricated value.

Navigation model: `Story > Act 1 > Sequence 1 > Block 1 > Mini-Block 1 > Shot 07`. Provide breadcrumb Back and a compact `Overview` link in the same turn. Selection never resets active story or saved revision. Deep links must carry stable project ID + revision + source fingerprint + canonical address, not mutable titles alone. When a save changes the source fingerprint, refresh rather than using stale observations. One physical production clip may cover 1–5 consecutive planning positions; never change the canonical number of positions.

## Live source and honest boundaries

Read `../read-plotpickle-project/SKILL.md`, its references `storyboard-review.md`, `story-workflow.md` and `limits.md`. For an existing `.ppf.json` file use the supplied or accessible saved source, never an imagined project. Pin identity with the bundled `inspect-project.mjs --operation identity` before any drilldown, and use `storyboard-review.py` for the real shot candidates and file observations. The packaged `scripts/story-explorer.py` wraps these readers in read-only JSON navigation: run `python3 scripts/story-explorer.py --project /path/to/project.ppf.json --view act --act 1` (or view `story|sequence|block|mini|shot`; see `--help`). This produces a data contract, **not** a hosted dashboard or clickable application. Render native in-chat cards and working selection controls from this data where the host supports them, following `references/chat-presentation.md`. Otherwise use clear compact text navigation. Never render inert controls masquerading as buttons or imply a persistent custom host UI. If the only source is a PDF screenplay or concept art, offer a *proposal preview* only: no saved PPF project, stored Beat or Lock is implied.

Use screenshot visual style as inspiration, not as authority for current records. The old screenshots are examples of unpopulated states: `No visual yet`, `Needs support`, `Not authored` are not story truths. Avoid using a red missing badge just because a view is empty, and avoid treating 25 planned positions as 25 generated assets.

## Conversation actions

A user may say `Show story map`, `Act 2`, `Sequence 3`, `Block 1`, `Mini 1`, `Shot 07`, `Show script`, `Show beat`, `Show prompt`, `Show image`, `What is locked?`, or `Back to Act`. Maintain the current validated breadcrumb and display the requested real detail in place. On an unnamed or unattached source, identify the candidate story from current project context without claiming it has been loaded, then give a grounded outline or request a saved `.ppf.json` to inspect status.

For draft editing, redirect to the existing source/shot change operations. Clicking Save/Lock or generating a prompt is not a side effect of opening a drilldown. Editing is an explicit new operation, with audit and source-pinning, and must preserve `Save -> Lock`, separate image approvals, portable media hashes, affected dependencies and restart readback. Proposals must never silently become canon. The Story Explorer is compatible with the separate `../plotpickle-story-workspace/SKILL.md` ChatGPT Project folder guidance; it cannot move a conversation to a Project itself.

## Canonical shape

4 Acts × 3 Sequences per Act × 2 Blocks per Sequence × 4 Mini-Blocks per Block × 25 planning shot positions = 2,400 positions total; global Blocks 1–24 and Sequences 1–12. A Mini-Block uses 25 positions with a baseline 3 seconds each, not a guarantee of rendered runtime. Distinguish actual shots/clips and alternative candidates from planning positions. See `references/drilldown-contract.md` for displayed states and explicit actions.

## Responsive source-backed presentation (v0.8.16)

When the current ChatGPT host supports interactive message controls, present a compact dark Story Explorer driven by the actual saved `.ppf.json` evidence (not a simulated project title). Use the native reader and the `story-explorer.py` read-only contract for current IDs/revision/fingerprint before rendering; the presentation is a projection, never a second source of truth. Do not embed one user's project or media in the distributed plugin.

On narrow mobile screens, place three Sequence cards and two Block cards in one column. Never force a three-column layout that splits a word like "Awakening" character-by-character. Keep the four Act selectors across, Mini-Block selectors 1–4 inside the corresponding Block, and a 5×5 grid of 25 planning positions below the selected Mini-Block. Use a horizontally scrollable Shot inspector tab strip; show *Script / Beat / Prompt / Image / Continuity / Save-Lock*. In the in-chat host, opening those tabs must be read-only; Save/Lock writes are explicit, separately authorized operations, with pinned snapshot readback.

For a user who wants a self-contained, portable browser demonstration alongside a saved PPF, generate `Story_Explorer.html` with:

    python3 scripts/render-story-explorer.py --project /path/to/project.ppf.json --out /path/to/Story_Explorer.html

The offline renderer is a read-only projection of source passages, sequence and block names, exact stored project prompts, 25 positions, and hash-checked portable image candidates. It escapes screenplay text to prevent HTML injection, declines unsafe or missing/mismatched image paths, and works without a server or network. It can use named Story Navigator metadata when present or show neutral generic labels when absent. The generated HTML must be packaged alongside relative `assets/` files; an HTML file alone cannot display relative images if separated from its folder. Regenerate after each project revision. It is not a native ChatGPT Project, a live plugin dashboard, a media generation engine, or verification that PlotPickle's canonical reader accepted a newly constructed PPF.

## Persisted source lookup and mobile in-chat rendering (v0.8.17)

When a user approves an update or returns to a story, prefer an actual saved PPF export over memory or demonstration data. If a file service is available, search the current ChatGPT Project first and the personal Library by exact story name or PPF filename second; verify the file identity, revision, hash and source before displaying a status. A personal Library folder is not a ChatGPT Project and is never evidence that chats or attachments have moved. Use the saved project to render actual sequence/block labels and per-shot source. Do not bundle private story assets or PPF snapshots into the distributable plugin.

Mobile in-chat navigation should use a single vertical list of Sequence cards on narrow viewports, with long labels wrapping at natural word boundaries. Sequence choice preserves the active project ID and resets only subordinate selection. Use a compact four-Act rail, four Mini buttons for the selected Block and a five-by-five shot grid; show detail under the selected shot rather than a horizontally-scrolling miniature dashboard.

The offline renderer now discovers any authored Mini-Block shot plan, not only Block 1 / Mini 1. For each selected shot, show the exact stored passage text, shot purpose, stored prompt and provenance, available image and verified hash, visual approval, recorded Save/Lock and continuity. Omitted media and unplanned slots must remain explicitly unavailable. Passive navigation must be read-only. Only actual authorized project-write operations may set Save or Lock, followed by re-read verification.

A user's approval to proceed with the pipeline is not proof of approval for every image candidate or of a successful native Save/Lock transition. Continue to report independent package integrity checks separately from native-reader acceptance and ChatGPT Project attachment.
