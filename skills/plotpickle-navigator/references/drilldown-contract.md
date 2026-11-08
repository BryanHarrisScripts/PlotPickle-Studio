# Story Explorer — navigation and evidence contract (v1)

Hierarchy: Story > Act (1..4) > Sequence (local 1..3; global 1..12) > Block (local 1..6; global 1..24) > Mini-Block (1..4) > Shot (1..25). In each Act, sequence 1 owns blocks 1–2, sequence 2 owns 3–4, sequence 3 owns 5–6. Act 2 block 1 is globally Block 7.

Every displayed pane identifies: active story title, project ID/revision/fingerprint if verified; current breadcrumb; source evidence; status (unmapped/unknown/planned/candidate/verified/saved/locked); and a route back to the parent. Do not assume that every scene corresponds to exactly one Beat or Shot. Scene passages, independently authored beats, story responsibility and images are distinct entities with separate verification states.

At Shot level, expose `sourcePassages[]` (IDs + verbatim retained text), `authoredBeat` (record and source, or not authored), `storyboardPrompt` (recorded exact/reconstructed/not authored), `imageCandidates[]` (asset ID, preview only when actually available, visual review, source consistency and file verification), `camera`, `lighting`, `continuity`, `narration`, `motionSpans`, `saved`, `locked`. Never set statuses to green merely because a slot exists, a generated image appears in chat or an image fingerprint matches. Hash match and semantic approval are separate.

Readable states include `Not authored`, `No visual yet`, `Planned`, `Candidate pending review`, `Stored media missing`, `Verified bytes`, `Saved`, `Locked`, `Needs support`, `Blocked by prerequisite`. A legacy `Needs support` status describes a missing mapping or evidence only if the current PPF confirms it. For action buttons, only show enabled operations backed by the current host. Use read-only labels otherwise.

The `story-explorer.py` tool returns normalized JSON from a validated PPF and native reader. It intentionally does not set action button states, infer an authored beat, create a prompt, alter saves, or produce external media. For an individual shot it calls the existing read-only `storyboard-review.py` to report actual image candidates and mapping verification. Current title/scene examples from The Third Bell should be marked illustrative if not saved in a canonical PPF.

For visual design, use the old top Act tabs (screenshot 3), sequence/grouping overview (screenshot 2), and deep shot-details panel (screenshot 1). Improve readability: clear typography, non-colour status words, room for text, a pinned breadcrumb, and progressive disclosure instead of showing all fields at once.

Acceptance scenarios: drill from Act 1 to Shot 07; go back to Act 1 without losing project/revision; show 25 shot slots; source text matches saved passage; missing prompt stays missing; candidate images do not imply saved/locked; a different project or fingerprint blocks stale continuation; file verification stays distinct from image approval; correct Block 7 for Act 2 Block 1; no write operation during drilldown.
