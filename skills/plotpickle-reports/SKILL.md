---
name: plotpickle-reports
description: Use for PlotPickle Reports: project, story, characters, scenes, dialogue, production, feedback, connections, project-readiness, or printable/exportable story reports sourced from actual PPF records.
---

# PlotPickle — Reports (v0.8.21)

Entry: **Storyboard → Reports**. Preserve existing four HOME categories: Meet Elara, Learn, Storyboard, Connected Services. Under Reports show **Project, Story, Characters, Scenes, Dialogue, Production, Feedback, Connections**, matching original desktop PlotPickle `docs/issue-118-consolidated-reports.md`; Production further includes Overview, Locations, Shot Types, Shoot Groups, Actor Schedule, Shooting Timeline, Production Requirements and AI Systems per `docs/issue-119-production-reports.md`.

## Source and truth

Read `../read-plotpickle-project/SKILL.md` and locate the latest actually available saved `.ppf.json`, screenplay/scene records and relevant supplied media. Each report must identify project ID, revision, raw-file SHA-256, source filename, and data/evaluation time if applicable. Do not infer active project from a previous chat, forge source refs or count the full canonical 24 blocks / 96 Mini-Blocks / 2,400 slots as populated. Return `unknown` or `not recorded` where sources are missing; do not transform estimates into measured production facts. Read-only by default: no database, changes to screenplay, native Save/Lock, approvals, media, revision history or provider connections.

For users without a PPF, offer a *clearly labelled draft report template*, not invented populated metrics. Use documented assumptions for estimates and cite the associated source passage IDs or source fields. Report credentials/connection statuses only from a current authorized provider probe; static service catalogues never mean Connected. Reports may embed approved artwork if actually supplied and accessible, otherwise show missing/review-required.

## Functional outputs

- **Project**: identity, source revision, element counts, declared plan and image-map coverage, saved/locked states verified from current records.
- **Story**: Act/Sequence/Block/Mini-Block progress based on actual saved records; pacing, threads and payoffs are marked interpretive when not measured.
- **Characters**: screenplay cue counts, dialogue by speaker, source references, world/visual continuity gaps.
- **Scenes**: scene heading/order, screenplay passages, Block associations, linked cast/locations when recorded.
- **Dialogue**: count and word statistics from source cue records; never fabricate speech duration.
- **Production**: shot/media state, needs, breakdown and schedule from project; absent schedule means no schedule.
- **Feedback**: only stored project feedback/review threads, with unresolved status; never assume no notes means approval.
- **Connections**: current *verified* provider operations only; unavailable/unchecked remains unverified.

Use standard ChatGPT document, spreadsheet or PDF creation tools if the user asks for a finished exported artifact. The portable CLI `scripts/reports.py` produces an evidence-bound JSON or Markdown readout without external packages. Example: `python3 scripts/reports.py --project story.ppf.json --format markdown --section all --out reports.md`. For source-specific layouts supplement the CLI with screenplay/asset evidence and candid uncertainty. The helper cannot attest media bytes without supplied assets, has no provider authentication and does not create a live dashboard.

## Validation

Run `python3 scripts/test-reports.py` for structural and safety coverage; also check a real current PPF sample. A successful generated report is a **draft analytical projection**, not project canon, a saved report database or a completed production. Existing desktop Windows reports are references, not a live synchronized source.
