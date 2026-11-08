---
name: plotpickle-pitch-deck
description: Use to prepare PlotPickle film and story pitch decks, presentation packages, graphic novel pitch plans, logline workshops, investor/producer-facing packets and exports anchored to saved project truth.
---

# PlotPickle — Pitch Deck (v0.8.21)

Entry: **Storyboard → Pitch Deck**. Preserve the original desktop PlotPickle's writer-controlled Pitch/Review package (`docs/phase-d-pitch-review.md`) and optional 24-page × 4-panel graphic-novel pitch (`docs/issue-167-ai-comic-pitch.md`) as two clearly different user choices:

1. **Presentation Pitch** — story overview, logline, synopsis, genre, protagonist, stakes, world, visual language, tone, audience, positioning/comps, production approach, rights, team and ask. Default outline of roughly 10–14 slides, adjusted to available verified material. Show missing items as questions or draft proposals; use only approved facts for factual claims.
2. **Graphic Novel Pitch** — optional planning scaffold of exactly 24 canonical Block pages × four Mini-Block panels = 96 panel positions. The 96 reserved spaces are **not 96 authored or generated images**. Source-link any confirmed panel to its actual Block/Mini-Block screenplay evidence; leave absent ones `unmapped`/`not generated`. Preserve dialogue separately as editable text, not AI-drawn words inside images. Offer image generation only upon an explicit request and, for third-party cost-bearing providers, individual approval.

## Truth and approval

Read actual latest `.ppf.json` and `../read-plotpickle-project/SKILL.md`; report project ID/revision/SHA. Use `review.pitchPackage`, current screenplay source, character/world evidence and rights metadata when present. Preserve approved logline verbatim; if only an initial premise exists, present new logline/synopsis as **editable draft**. A pitch deck is a shareable projection, not an automatic edit to `review.pitchPackage` or to screenplay canon. Unsupported audience, comp titles, financing figures, distribution plans, release dates and rights clearance are explicitly `unverified`/`to be supplied` — never fabricated.

For images, reuse actual verified author-approved character/world/poster assets and cite their provenance; otherwise use labelled placeholders or ask for specific creative approval. Keep project script truth and sales copy separate. Source-only `draft` vs `approved` must be visible. Read `../plotpickle-creative/SKILL.md` and targeted archived lessons: the Pitch (#1), Loglines (#15), Mood and Visual Language (#16), Concept Art and Storyboard (#17), Audience/Pitch Language (#42), and Ownership/Rights (#46) as available; curriculum never supersedes the writer.

## Outputs

The helper `scripts/pitch-deck.py` can build source-bound **presentation-outline JSON**, slide-separated **Markdown**, or a **96-panel mapping plan** from an actual project, without external services: `python3 scripts/pitch-deck.py --project story.ppf.json --mode presentation --format markdown --out pitch.md`. The output includes source labels and editable placeholders. When a user asks for an actual `.pptx` or PDF pitch deck, use the host's document/slides authoring tools and provide the created file, with source references and image provenance, after checking the visuals. Do not claim an installable slide designer or render actual slide files from a Markdown outline alone.

## Validation

Run `python3 scripts/test-pitch-deck.py` and a genuine source-project example; verify 96-panel address math, no synthetic approved characters, no image generation, and no file clobbering. A pitch deck remains a draft until author approves its marketing copy, rights statements and visuals. No automatic external sharing, distribution, billing or background generation.
