---
name: plotpickle-story-flow
description: Continue PlotPickle Script → Storyboard → Visuals → Produce on demand with source-verifiable readiness, not an autonomous factory.
---

# PlotPickle — Story Flow / Continue Film (v0.8.25)

PlotPickle is an on-demand creative production system. Preserve four HOME choices and keep **Continue Film** the default helpful action inside Storyboard. Script → Storyboard → Visuals → Produce are logical stages, not automatic sequential charging or a requirement to work through 2400 reserved positions. The creator can review, revise and jump to Character/World design, Reports, Assets, Posters and Pitch Deck at any time.

1. Identify the current actual PPF/screenplay or verified ChatGPT Project. Read `../plotpickle-story-workspace/SKILL.md` and `../read-plotpickle-project/SKILL.md`. Chat memory alone cannot certify latest source state. If no file is present, help creatively as **idea-only** instead of inventing persisted state.
2. Read the exact scoped Act/Sequence/Block/Mini-Block and real source passage IDs. If an accessible `.ppf.json` exists, `scripts/story-flow.py` can generate a **read-only** evidence packet; it never writes source. Summarize where the story is, what is verified, one sensible next action, and what remains for review.
3. With no script, help write it. With no shot mapping, plan a small source-linked batch. With missing images, create candidates only at the user's instruction. With real image bytes, follow guarded native Save → Lock and separate acceptance evidence. With production-ready stills, propose a still-image animatic via `../plotpickle-animatic/SKILL.md`. For requested motion, prepare a source-verified, no-spend fal brief via `../plotpickle-fal-production/SKILL.md`. Never silently invoke fal.
4. Use specialized skills: navigator, design, assets, animatic, fal-production, reports and pitch-deck. The source screenplay and independently verified media outrank any illustrative plan.
5. After an action return actual source revision/artifact, plus Continue / Review / Revise options. Any script or image change triggers only affected downstream validation, never an automatic overwrite or paid re-generation.

## Four gates

**Script → Storyboard:** real screenplay passages and stable source identity when present; proposal must be labelled as such.
**Storyboard → Visuals:** scoped 25-position shot map with valid passages and camera/continuity instructions; missing positions are unplanned.
**Visuals → Produce:** actual image bytes and hashes; native saved, locked and accepted status remain distinct and must be read from source.
**Produce → Review:** actual verified MP4/animatic, duration, frame rate, sound provenance and hash; report draft vs accepted master accurately. A Motion Span represents 1–5 consecutive editorial 3-second positions, or 72–360 frames at 24 fps; fal's native duration may differ.

Run `python3 scripts/test-story-flow.py` for the bounded readiness helper. `scripts/story-flow.py --project story.ppf.json --block 1 --mini 1 --format markdown` reads metadata only; provide `--assets-root` to hash-check actual portable image bytes. Do not promise a completed provider integration, saved PPF, paid clip or approved master from a successful offline test.
