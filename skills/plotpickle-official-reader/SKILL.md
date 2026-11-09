---
name: plotpickle-official-reader
description: Open the creator-approved The Third Bell official graphic novel, read the complete ten-page fifty-panel edition from the private ChatGPT Library, with source-aware page navigation, edition continuity, and no PPF Save/Lock side effects.
---

# PlotPickle Studio — Official graphic-novel reading (v0.8.39)

This skill implements the creator's November 9, 2026 approval of the **official illustrated reading edition** for *The Third Bell*. The edition comprises the **first Mini-Block of Block 01** and **first Mini-Block of Block 02**, 25 planned shot positions each, as **10 pages × 5 illustrated panels = 50 panels**. It does **not** certify that all four Mini-Blocks in either Block are illustrated. It does **not** mean 50 independent full-resolution PPF production images were created, visually approved or locked.

## Read-only entry in Studio

Route: **HOME → Storyboard → REEL → Your Stories → The Third Bell → Read Graphic Novel → Official Blocks 01–02**. This is a child action within the approved REEL/Storyboard hierarchy, not a new HOME choice, a hosted sidebar or a separate database. Also accept `Open The Third Bell official graphic novel`, `Read the 10-page edition`, `Page 7`, `Next page`, and `Back to Storyboard` in natural language. Do not require a Windows app, GitHub login, new Plugin Creator installation or remote media generation.

## Authoritative private Library sources — locate afresh each session

The creator's authorized Library location at publication:

`/The Third Bell/Graphic Novel/Official Blocks 01-02/`

Expected filenames there:

- `The_Third_Bell_Official_Edition_Manifest.json` — edition index, per-page expected file hashes, shot mapping and captions
- `The_Third_Bell_Page_01.png` through `The_Third_Bell_Page_10.png` — the actual illustrated pages
- `The_Third_Bell_Graphic_Novel_Blocks_01_02_10_Pages.pdf` — continuous ten-page document
- `The_Third_Bell_Interactive_Reader.html` — offline/standalone original page reader
- `The_Third_Bell_Blocks_01_02_Official_Complete.zip` — portable edition bundle

These are **pointers to private, user-authorized storage, not bundled assets or public URLs**. Ask the current host's accessible Project/Library file service to list and read them. In a different user's account, a missing folder does not mean The Third Bell exists. No special private file IDs, user IDs, credentials, signed media links or content hashes are stored in the plugin. Never invent an attachment, file URL, sandbox path or Library permission. Do not claim that the plugin's installed files contain these images.

On reopening, prefer a current authorized personal Library source; verify the exact folder and filenames; use actual file bytes to check all ten images are readable and each is a portrait page with five clearly identifiable illustrated panels. Check the original manifest's stated hashes/byte lengths against the actual pages when a supported byte-reading tool is available, then show an accurate verified count. The edition manifest may not match every separately exported PDF byte-for-byte (PDF recompression/alternate export). Verify PDFs independently (ten readable pages, actual bytes/hashes), do not wrongly reject unchanged ten PNGs because one PDF differs, and do not silently overwrite the manifest or an official edition. A ZIP can contain a previous PDF export; distinguish the ZIP's contained edition from the current standalone PDF. If a file is unavailable, report that specific file as missing/unverified; do not substitute stock art or image-generation results.

## Consistent reading presentation

Use the owner's established illustrated-page aesthetic: navy and parchment/gold decorative top banner; title THE THIRD BELL; `Block {01|02} · Page {01..10} · Shots {NN}–{NN}`; five **wide, vertically stacked** cinematic illustrations, small shot number badges, short legible caption plaques on each image, warm sunrise/island/coastal lighting and consistent characters. Preserve the **saved exact artwork** rather than regenerating it at reopen. Page 01–05 = Block 01 Mini 01, numbered 01–25; Page 06–10 = Block 02 Mini 01, numbered 01–25. Read the actual caption text from the verified manifest or page — do not manufacture dialogue or fill missing panels.

For ChatGPT hosts supporting interactive controls, show the actual saved ten images in one swipe/arrow page reader with an active page indicator, page title, block and shot range, and a page selector. Controls must really change local page state; no inactive fake buttons. On hosts without a working interactive image viewer, show individual actual verified images in reading order with plain navigation text. Offer links to the verified **original** reader, PDF and complete ZIP as secondary ways to read. Links must be returned by the currently accessible file host or established current container; do not reuse stale sandbox paths from past conversations. Open pages without spending credits or uploading their images to a third-party provider.

## Truth, approval and revisions

The creator approved and saved this **official visual reading edition** as a finished ten-page graphic-novel artifact. Keep this `OFFICIAL_READING_EDITION` state distinct from (a) the storyboard's selected source sheets; (b) a screenwriter's authoritative scenes/dialogue; (c) individual candidate image acceptance; and (d) PPF Saved / PPF Locked / Media Verified. The source PPF was previously observed at revision 003; do not assert it remains current without a fresh independent read. A saved graphic-novel illustration or official-edition designation is NOT a native PPF update. At this publication, the Block 02 illustrated adaptation may diverge from the saved council-hall screenplay scene; explicitly label screenplay/source reconciliation as pending rather than silently rewriting either. Refer back to `../read-plotpickle-project/SKILL.md` before any real screenplay or shot mutation.

Treat the creator-selected 10-page edition as the preserved baseline for future pages. Do not regenerate, restyle, reorder, or replace any of the original ten pages by default. New editions, editorial changes, further Blocks, alternative captioning or continuity corrections need a distinct, explicit creator request. Never mark source panels individually Save/Locked based on the edition's approval. Never trigger fal, Suno or paid image/video generation from a reading action.

Read `references/official-edition-layout.md` for the expected page ranges and recovery checklist; use `../plotpickle-graphic-novel/SKILL.md` for generic Mini-Block creation or other stories and `../plotpickle-skin-v1/SKILL.md` for the existing Studio shell.
