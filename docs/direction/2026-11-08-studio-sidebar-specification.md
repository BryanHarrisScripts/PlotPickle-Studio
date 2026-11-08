# PlotPickle — Studio Sidebar App and Connected Story Workspace

Owner decision recorded November 8, 2026. This is the implementation specification for the November 8 engineering conversation (https://chatgpt.com/share/6af0af4f-2990-83e9-9401-878f047f1764) and companion to `plotpickle-engineering-brief-2026-11-08.md`. The November 6 migration and operating documents are historical context, not the controlling brief for this build. Preserve existing truth, governance, capability and retirement protections.

## One shared creative system

ChatGPT is the primary creative workspace; PlotPickle remains the on-demand creative production system, not an always-on coding factory. Elara guides conversation and decisions, not an invisible background agent. The original Windows local UI is optional reference software; there is no synchronization/parity requirement with it. GitHub remains for source code and collaborative development, not mandatory story storage. Preserve all existing reusable engines, the 81-lesson/12-topic curriculum, screenplay, truth ledger, narrator, character and world design, asset catalogue, Save→Lock, reviewer, motion, animatic, editor, posters, reports, pitch deck, community and game intentions. A future replacement may retire an old surface only after proof that its responsibilities are covered.

## Interface hierarchy

Home retains Meet Elara, Learn, Storyboard, Connected Services. The optional ChatGPT native PlotPickle Studio sidebar entry opens a full-screen or side panel to the SAME creative system. Its first screen places REEL and ONCE prominently above the creator's stories. The first working surface is a connected read-only Story Workspace rather than a generic asset library.

REEL: turn an idea or screenplay into a visual story and movie; labels Characters, Worlds, Scenes, Visuals, Produce.

ONCE: tell your life story, bring memories to life and preserve them for family; labels People, Places, Memories, Illustrations, Preserve. Start one real memory at a time and protect narrator truth and personal privacy. Reenactments remain labelled illustrative and require permission to invent connective scenes or portray real people.

Under both: Story, People, Places, Moments, Visuals, Produce, Learn, Review, Share are connected VIEWS of the selected story, not independently editable baskets or two story engines. The author can follow passage → scene/memory → cue/person → location → shot/illustration → exact prompt → image candidate → motion/animatic → film/audio/poster/report, with each relation explained by project evidence. Prompts are versioned outputs of creative decisions, not floating canonical instructions. Details and data for known entities are never silently imagined.

## Data authority

There is ONE owned story project/PPF and its portable assets. The UI is a projection, not a storage or canonical ledger. Stable identifiers, project revision and SHA-256 guard every read and write. Extracted character cues and place headings are merely observations until author-reviewed; a generated image and an external fal URL are not proof of asset byte recovery; saved, locked, accepted and final approved are independent. Every source revision invalidates only affected downstream assumptions. No auto-generated 2,400-shot film claim: 4 acts, 12 sequences, 24 blocks, 96 mini-blocks, 25 planned slots each are optional editorial scaffold whose physical runtime can compress.

## Learning in context

Keep full curriculum browsing. Additionally surface source-grounded lessons at a decision point: structure 19 (Why 24 Blocks Work), character 58 (Prove Character Through Choice), theme 16 (Mood, Colour and Visual Language). A lesson suggestion must cite an actual source passage and relevant full lesson before diagnosing the user's work. Learning never silently rewrites project truth or trains a model.

## Providers and production

For Connected Services, keep Prepare Music Brief/Open Suno and Prepare Motion Brief/Open fal. Open fal is a direct external link to https://fal.ai/dashboard for independent account sign-in, models, prices, usage and credits; Open Suno is a direct link to its official account. The plugin never collects passwords or stores provider keys. A specific fal job is Prepare → price review → explicit individual approval → Submit → verified provider result → source-pinned intake. 3–15 seconds is an editorial Motion Span, not provider duration guarantee. BUZZ pilot and Modem remain labelled not operational until verified.

## Engineering sequence and acceptance

A. Preserve source/release identity and add this brief to the plugin/repo development record. Do not duplicate an installed PlotPickle plugin or create a second engine.
B. Build a small read-only Studio shell and pure PPF relationship projection. The source adapter must use the existing native reader and fail closed on missing/mismatched project id, revision or SHA, no invented scene/item counts, no provider credits or writes. Test actual links from scene/memory to character cue, heading, authored shot and prompt, with explicit unknown media.
C. Integrate the MCP Apps UI resource and OpenAI global sidebar entrypoint into the existing authenticated plugin host; implement required hosted transport/security. Use the same headless data operations for ChatGPT and the interface. Verify in actual ChatGPT; a local HTML preview is NOT sidebar deployment.
D. Prove reopen/restart and mobile/readability against one real authorized saved PPF and asset package. Read-only must not mutate; no false Save/Lock, no phantom files and no unexplained identities.
E. Only after C–D pass, introduce source-guarded writes, media verification/import, shared editor progress and delivery. Keep repo implementation and current installed plugin decoupled until releases pass real host checks.

## Status on November 8

A read-only projection and standalone local preview source were created with six automated tests. Global sidebar metadata is scaffolded but has not been deployed to ChatGPT, and no actual private story was loaded. This is a cautious implementation start, not a production release or acceptance of source/asset persistence.

## Version 0.2.0 source checkpoint

Thirteen automated source/loader/HTTP tests pass. MCP Apps global-entrypoint source metadata and host tool-result bridge are present; no actual ChatGPT sidebar installation, current host SDK build, multi-user auth, or independent visual acceptance is claimed. The pilot remains read-only and does not expose private story data in reusable UI resources. The source-only Brotherly Love fixture acceptance reports actual recorded relationships; media and native reader acceptance are still separately required.
