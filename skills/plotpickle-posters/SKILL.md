---
name: plotpickle-posters
description: Create source-aware theatrical and three-format social poster campaign packs for stories and film projects, using PlotPickle's verified 81-lesson curriculum for marketing copy, visual language and rights. Use when the user requests a poster, key art, teaser campaign, character poster or social promotional graphics.
---

# PlotPickle — Posters / Campaign Pack (v0.8.11)

ChatGPT remains the creative workspace; this is a **Storyboard → Production Design → Posters** capability, not a fifth Home tab. Home choices remain Meet Elara, Learn, Storyboard, and Connected Services. In Storyboard offer Character Builder, World Builder, Layout Sheets, Posters, and Produce. User can start Posters without completing the other paths.

Read `references/poster-workflow.md` and the specific mapped lessons in `references/curriculum-poster-map.json`. Before citing or using archived teaching, run `python3 ../plotpickle-creative/scripts/curriculum-bridge.py verify` and confirm `completeSnapshotVerified: true`; retrieve full lesson sections via `curriculum-bridge.py lesson`. The 81 lessons contain relevant marketing language, not a separately verified "marketing skills course." Keep historical sources, proposals and actual user decisions distinct. Recommended lenses: The Pitch (#1), Loglines (#15), Mood and Visual Language (#16), Concept Art and Storyboard (#17), Pitch/Audience Language (#42), and Ownership/Rights (#46).

## User experience

Show **Create Poster**, **Generate Social Set**, **Create Campaign Pack** as actions. Guide selection of actual project (when available), poster type (official/key art, teaser, character, ensemble, scene, world), audience and approved creative identity. Offer title, tagline, optional logline, release text and CTA; fill unknowns with editable proposals rather than inventing facts. Always specify whether copy is draft or approved. Distinguish a tagline from a screenplay logline; do not write marketing copy into screenplay scenes. Encourage factual, non-spoiler, audience-focused copy and rights checks before publication.

Full Campaign Pack has **four native compositions**, not indiscriminate crops: theatrical 1620×2400 PNG (27×40 ratio, digital proof); social square 1080×1080 PNG; portrait social 1080×1350 PNG; story/reel vertical 1080×1920 PNG. This is one marketing creative brief with four different creative layouts. When users choose Poster only or Social only, keep other formats planned/not generated. For physical printing, discuss actual 27×40 inch 300-dpi requirement (8100×12000), bleed, printer settings and proofing; do not falsely label the default proof print-ready.

If the user asks to generate actual art, use available host image tools and preserve actual, author-approved image references and character/world continuity. Render each format deliberately: recompose subjects, keep faces safe, adapt headline and copy sizes/placement, reserve vertical social UI overlay zones. Do not claim a poster exists because the data/plan does. Verify generated image bytes and exact dimensions; if not available, keep status as `planned` and explain what remains. Posters are marketing assets, **not automatic storyboard shot Save/Lock**. A native project record can be updated only by real supported project asset operations, without inventing shot assignments or ChatGPT Project persistence.

## Deterministic offline helper

From this skill's directory:

    python3 scripts/poster-pack.py formats
    python3 scripts/poster-pack.py plan --brief campaign-brief.json --out campaign-plan.json
    python3 scripts/poster-pack.py inspect --plan campaign-plan.json --assets-dir ./images
    python3 scripts/poster-pack.py package --plan campaign-plan.json --assets-dir ./images --out campaign-pack.zip

Use `schemas/poster-campaign.v1.schema.json` for campaign brief input and `schemas/poster-pack.v1.schema.json` for output. A source-backed brief must provide the real saved `.ppf.json` path, SHA-256, project ID, revision, and optional passage IDs. The tool checks the file SHA and checks exposed project ID/revision fields when present; source claims and passage meanings remain reviewable rather than automatically true. Without a project, it explicitly returns `unbound-proposal`. The helper never generates media, spends provider credits, uploads to social platforms or edits project canon. Inspect verifies dimensions and full image decoding when Pillow is installed; without Pillow it reports decode as unverified and refuses packaging. Packaging requires four actual decoded images but is **not** equivalent to author marketing approval, rights clearance or print-readiness.

## Acceptance

Run `python3 scripts/test-poster-pack.py`. Confirm four stable dimensions and filenames, immutable plan outputs, explicit `planned` states, failure on missing/wrong-size/corrupt assets, source SHA mismatch failure, and no overwrites. Verify curriculum reference IDs/sections against the actual embedded lesson text and run its independent verification. A passing local helper test is not evidence that images were generated, approved, uploaded, or retained in a project.
