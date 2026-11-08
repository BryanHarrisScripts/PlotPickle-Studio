# PlotPickle — Engineering Direction and Studio Sidebar Brief

Date: 8 November 2026  
Primary decision source: https://chatgpt.com/share/6af0af4f-2990-83e9-9401-878f047f1764  
Status: owner-directed working brief; source-reconciled from the November 8 conversation context, not a verbatim transcript verification.

## Executive decision

PlotPickle is an on-demand, ChatGPT-native creative production system. ChatGPT is the primary creative workspace on a phone or desktop. PlotPickle's skills, portable project record, source-linked media, guarded operations, and Elara's guidance provide continuity from an idea or memory through visual narrative and production. The PlotPickle Studio Sidebar App will be an optional visual entrance to this SAME engine, not a second app, second story store, local desktop replica, or software factory.

The product must have no creator-side requirement to install Windows software, run a tunnel, administer a server, use Google/Apple storage, create a separate storage account, connect GitHub, or understand technical process topology. Hosted infrastructure may be required to make an official MCP App run, but provisioning, secrets and authentication are engineering responsibilities; they must not become creator setup steps. An interactive view is not evidence that durable data already exists.

## Navigation and human experience

The existing HOME choices remain Meet Elara, Learn, Storyboard, and Connected Services. The Sidebar App adds a discoverable **PlotPickle Studio** workspace when ChatGPT supports and verifies its registration. It opens with two clear entries above the creator's stories:

- **REEL:** Turn an idea or screenplay into a visual story and movie.
- **ONCE:** Tell your life story, bring memories to life and preserve them for family.

REEL and ONCE are human-facing entry modes over the same project engine. REEL presents Characters, Worlds, Scenes, Visuals and Produce; ONCE presents People, Places, Memories, Illustrations and Preserve, with accessible one-memory-at-a-time guidance. Real persons, recollections and AI reenactments are distinct. Ask permission before inventing biography, depicting identifiable real people, or sharing family material. Neither mode imposes a setup wizard.

Within the selected story, connect Story, People, Places, Moments, Visuals, Produce, Learn, Review, and Share. These are views of actual source-linked project data, not disconnected asset buckets. Preserve discoverable Props, Styles, Storyboards, Films and Audio as relationships or context-specific tools, alongside posters, reports, pitch decks, collectibles, Foley, narration, music, and the eventual archive.

## One connected story graph

The creator can move along real relationships:

project (ID + revision + source hash)
→ idea, script passage, or recorded memory
→ scene / moment / dramatic beat
→ character or real person, place/world, prop, visual style
→ storyboard position, composition and continuity
→ exact versioned image prompt and references
→ actual candidate image and review decision
→ saved, locked and accepted states (distinct)
→ motion span or animatic, narration, Foley, music
→ editing timeline, review export, film, poster, report or private family archive.

Each relation must identify its evidence and source address; missing links remain unknown, never synthetic. Use the existing project, evidence, continuity and asset contracts instead of introducing a parallel database. Human and agent interfaces must read the same project truth and apply identical authorization and validation.

## Learn, Elara, and the creative loop

Retain the complete 81-lesson curriculum across 12 topics and its full browsing path. Offer context-grounded teaching when a specific creative decision benefits from it: character choice, structure, dialogue, visual language, collaboration, ownership, revision, responsible AI. Lessons help writers understand decisions, not silently write into canon. Elara is the shared conversation/coordination role, not an unverified persistent daemon. Preserve Learning & Evolution research and review, without confusing recorded feedback with model retraining.

Workflows are on demand: assess → propose → decide → create → review. A user can jump into character design, worlds, sound, posters, editing or Learn when useful. Script → Storyboard → Visuals → Produce represents governed handoffs, not an automatic paid pipeline.

## Story authority, mathematics, and storage

The user-owned PPF and its portable, verifiable files are the source of truth. Preserve project ID, revision, raw SHA-256, screenplay passages, approved decisions, proposals, continuity, exact prompts, shot mappings, asset identity, review state, media provenance, and change impacts. Verified bytes and hashes are required before claiming an image, audio file or MP4 is recoverable. Do not interpret a fal URL, saved record or chat response as a committed file. Visual selection, Save, Lock, acceptance and final approval are separate evidence states. A revised screenplay invalidates only affected downstream assumptions.

The canonical 4 Acts / 12 Sequences / 24 Blocks / 96 Mini-Blocks / 25 planning positions per Mini-Block remains available. Its nominal 3-second positions and 24-fps timing are planning tools, not a forced physical-shot count or runtime. ONCE hides cinematic mathematics until needed. Prove current saved project and media recovery across chat sessions and devices rather than assuming ChatGPT memory is persistent storage. Prefer the built-in ChatGPT project/file experience where verified. Plan a portable project-and-assets ZIP; do not add a mandatory Google Drive, iCloud or GitHub story repository.

## Story Continuity and Pi Durable reference

Preserve one inspectable story-state checkpoint per meaningful adopted revision and production handoff, with project/source identity, authorized action, results, retries and pending reviews. A repeated submission must not duplicate spending or overwrite approved work. Restart/reopen must recover current intent without constructing fictional source state. Study the open-source Pi Durable design as a REFERENCE for checkpoints, recovery, idempotency and shared state. It is not a product dependency, Windows service, mandatory account, or commission of an always-on worker fleet.

## Editor and production

The editor should become a coherent part of the ChatGPT-native story experience, usable from phone and desktop, but its capabilities must be earned by actual host integration. Preserve useful timeline, trim, cut, dialogue, Foley/music/narration, asset inventory, review, and reproducible export contracts. The old Windows editor remains reference software, with no parity/synchronization obligation. Do not claim a hosted editor, audio mix, retained video or Save/Lock when only a demo/view has been built.

For media services, retain Prepare Music Brief + direct Open Suno, and Prepare Motion Brief + direct Open fal (https://fal.ai/dashboard). Provider sign-in, model catalogue, pricing and credit management belong to the provider. No credentials enter PlotPickle. Paid generation requires actual source imagery, supported provider model/duration, up-front current cost, explicit one-job authorization, receipts, and independently verified returned bytes. 3–15-second Motion Spans are editorial groupings, not universal provider duration guarantees. BUZZ remains a community pilot, Modem planned, until deployment truth is verified.

## Source-backed first implementation and acceptance

1. Establish this November 8 decision brief as the working authority; retain November 6 materials only for historical preservation context. Preserve the existing PlotPickle plugin identity and skill surface.
2. Build a read-only, mobile-responsive Studio shell and pure PPF relationship projection. Unit-test source binding, unknown states, malformed/conflicting prompts, and prohibition of mutation.
3. Verify a REAL saved PPF via the existing native reader against project ID/revision/hash, traverse actual links and verify separately supplied media bytes. Use Brotherly Love as a source-rich reader acceptance case; The Third Bell is the intended creative pilot for the next production slice when its actual current source is accessible.
4. Attach the official MCP Apps resource and OpenAI sidebar entrypoint to the EXISTING authenticated PlotPickle plugin host. Verify actual registration, authenticated transport and mobile/desktop presentation. Do not create an unnecessary second plugin or claim that a localhost preview is an installed sidebar app.
5. Prove durable reopen, source-version stability, privacy, media integrity and no false or duplicate writes across ChatGPT conversations/devices. Only then implement guarded project edits, Save→Lock readback, source-aware media intake and editor actions.
6. Deliver one end-to-end, user-reviewed The Third Bell scene/mini-block through screenplay evidence, visual continuity, generated image, verified persistence, motion/animatic, sound and reviewable output. Package a portable archive only once constituent media are actually present and verified.

## Current evidence boundary — November 8, 2026

A standalone read-only Studio shell, a PPF relationship projection, and six passing Node unit tests have been built in a local source pilot. A separate real PPF export was inspected with a native reader, but that does not independently prove host-delivered media bytes or full story recovery. The sidebar metadata remains source-only, not hosted, connected, or independently tested inside ChatGPT. The editor, retained media, multi-device synchronization/recovery, guarded editing and paid production do not become operational merely because this brief names them. No provider generation, expenditure, repository merge or user-facing sidebar installation is claimed by this checkpoint.

## Non-negotiable engineering rules

No duplicate project authority, no fabricated story state, no credential collection, no unexplained external provider charges, no forced local software, no permanent extra account, no silent rewriting of user source, no unverified media-availability claim, and no retirement of legacy code or contracts before an evidenced replacement. Prefer one small working, recoverable creative journey over a broad menu of unconnected screens.

## Implementation checkpoint — November 8, version 0.2.0

A source-only read-only MCP Apps sidebar registration and standard host tool-result bridge have been authored. The local Studio shell and PPF projection now include evidence-linked scene/people/place/shot edges and source excerpts. Thirteen tests pass: six baseline relationship/identity tests, two additional graph/mode tests, four guarded source-loader tests, and one HTTP preview no-write test. A source-only Brotherly Love PPF read measured 383 passages, 16 scenes, 10 character cues, 16 separate heading-derived places, 125 shot addresses, 131 recorded artwork associations and 300 derived edges. This does not independently verify any attached media or current native Save/Lock. Browser/host integration could not run in the available environment. The official MCP server SDK was not installed (network unavailable), and no authenticated public endpoint or Explore-sidebar installation was created. Next implementation gate is to attach the registration to the existing authenticated PlotPickle host and complete native reader + ChatGPT mobile/desktop acceptance.
