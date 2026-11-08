# v0.8.34 release focus — ChatGPT-first continuity (owner clarification, 2026-11-08)

This document records the owner's later direction after testing PlotPickle on a phone. It supplements the November 8 engineering discussion, preserving the existing source authority. Do not rewrite or pretend the original sidebar pilot was deployed.

## What stays primary

The existing private ChatGPT plugin, HOME, Meet Elara, Learn, Storyboard, REEL, ONCE, Connected Services, in-chat Story Explorer, Script → Storyboard → Visuals → Produce and specialist skills. These surfaces have been exercised by the owner on mobile. That reported usability is meaningful but is not a substitute for specific persisted-media or native Save/Lock acceptance.

The mobile conversational workflow requires no special UI host, Windows app, new storage provider, GitHub account or service deployment. A genuine future MCP Apps global sidebar is **optional**, not a prerequisite for the v0.8.34 ChatGPT plugin skills/branding update. Do not delete or claim completion of the source-only sidebar pilot. Keep the pilot visibly unhosted and separate from shipped skills.

## Small demonstrable improvement

The primary "Continue my saved story" path:

1. Locate an actual authorized PPF in ChatGPT Project files or personal Library, not model memory. Pin project identity/revision/hash using the unchanged canonical reader when available; retain one authoritative source.
2. If an accompanying ZIP is present, verify each declared media variation by portable path, recorded byte count, SHA-256 and supported file signature **without extracting the ZIP**. The new `skills/plotpickle-story-flow/scripts/verify-portable-package.py` provides this read-only media test. No creator installation is needed; the host's available execution environment runs it.
3. Inspect requested Mini-Block and its actual passage IDs/mapped shot records through the existing `story-flow.py`, native reader and Story Explorer. Media variation recovery and production-mapped shots are separate facts. Never turn an image's existence into an inferred Save/Lock or accepted shot.
4. Return story + revision, verified count/unknowns, stage and one suggested next action. Generate images or call fal only on an explicit authorized request, with separate provider cost approval. Keep The Third Bell's existing private project/Shot 01 seed intact as the next pilot.

The media ZIP check is not a new PPF parser/engine, host service, auto-sync daemon or duplicate story store. If the native reader is unavailable, the output explicitly says its acceptance remains unverified. Only the checked source may be authoritative. A private ChatGPT Library asset package is not automatically proof of plugin-level or mobile-vault storage.

## v0.8.34 plugin acceptance (skills-only path)

- The current **same existing** private USER plugin and current release ID are independently inspected through Plugin Creator before update.
- Complete v0.8.33 archive backup is downloadable, privately retained, SHA-256 verified and has a usable restoration strategy. Current rollback verification status must be stated, not presumed from release history.
- Reconcile v0.8.34 candidate from exact v0.8.33 private archive and Studio MAIN, including two manifests, distinct Studio PNG bytes, same canonical reader checksum and preserved The Third Bell private seed. No private media goes to public GitHub.
- Verify source and synthetic suite including story flow and portable media recovery. Test real authorized saved PPF/ZIP read-only on ChatGPT execution before treating new claims as functional. The previously recorded Brotherly Love ZIP recovery is real Library evidence, not live plugin certification.
- Verify actual Plugin Creator installation and ordinary ChatGPT plugin conversations using HOME, Storyboard, REEL, ONCE and Continue Film; at least one phone acceptance session should be reported by an authorized user when available.
- Update only the original plugin using `expected_release_id` guard. Explicitly remove obsolete legacy branding paths only when candidate bytes are correct; retain private seed. Read back exact new release version and ID and inspect preserved files.
- Unverified hosted sidebar, new media write APIs, native Save→Lock on a different storage host and independently recovered video MP4s remain **feature-specific future gates**. Do not claim those features exist in v0.8.34; they do not, by themselves, prevent a clearly labelled skills-only release.
- No deployment before verified backup/candidate and Plugin Creator readiness. No surprise provider spending.

## Current release boundary

GitHub source tests and phone UI observations cannot update an installed plugin. Plugin Creator still reports published v0.8.33 at the last verified check. New source changes are unreleased until a guarded update returns a new release ID. All old Windows code is historical/optional; the original PlotPickle desktop repository stays untouched.
