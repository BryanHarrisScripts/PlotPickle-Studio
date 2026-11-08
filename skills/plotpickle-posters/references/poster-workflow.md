# PlotPickle Poster Campaign Pack v1 — production workflow

Four formats ship as one linked campaign, not one master with three blind crops:

| Output | Pixels | Ratio | Purpose |
|---|---:|---:|---|
| theatrical | 1620×2400 | 27:40 | standard theatrical key art; digital proof, *not* print-ready |
| square | 1080×1080 | 1:1 | social square feed |
| portrait-feed | 1080×1350 | 4:5 | portrait social feed |
| story-reel | 1080×1920 | 9:16 | story, reel or vertical cover |

A 27×40-inch poster at 300 dpi is **8100×12000 pixels**. The standard 1620×2400 digital proof has the correct ratio but cannot be advertised as print-ready at 300 dpi. For print production confirm final specs (bleed, printer's colour profile, safe area, PDF requirements) with the intended printer. If a separate print-ready derivative is requested, produce and inspect that separately; upscaling without authentic detail does not guarantee print quality.

## Campaign creative flow

1. Open `Home → Storyboard → Production Design → Posters`. Choose project and type: Official/Key Art, Teaser, Character, Ensemble, Scene or World; choose Poster only, Social three, or Full Campaign Pack. Use the same four canonical output definitions for all modes. Full pack is the default.
2. Pin the latest real saved `.ppf.json` when present. Collect actual screenplay title, cited character/location/scene references and approved visual refs. If none exists, label every story fact as proposed and use no invented project revision.
3. Verify the embedded 81-lesson curriculum via `../plotpickle-creative/scripts/curriculum-bridge.py verify`, then retrieve exact lessons in `curriculum-poster-map.json` and their relevant full section text. The key teaching separation is: *logline* describes the story engine; *tagline* invites curiosity, *teaser* withholds deliberately, *poster* conveys a visual promise. No text is silently synced into the locked screenplay.
4. Author an editable marketing brief: audience, genre/tone, poster type, one permitted campaign promise, visual direction, tagline, release text and optional CTA. Draft or propose missing copy; do not invent awards, credits, distribution, release dates, reviews, actor likenesses or endorsements. Ask for rights/credit confirmation where relevant.
5. Prepare a key-art direction and make a candidate with an actual host image-generation tool when the user requests artwork. Apply approved character identity, world consistency, motif, framing and rights. Distinguish an image prompt, a generated candidate, a saved candidate, and an approved campaign asset. Use tool-generated images, not a template, to claim generation.
6. Adapt each target deliberately: preserve subjects and identities but recompose shot/negative space, title hierarchy and credit legibility. Vertical layouts typically shift primary subject and title; square layouts need centred, simplified hierarchy. Never generate by indiscriminate centre crop when it hides faces, titles, trademarks or legal copy.
7. Run `poster-pack.py plan` to create a deterministic plan with all four output sizes and filenames. Plan does not call image generation. Run `inspect` for real local candidate files; inspect checks PNG dimensions and decodes with Pillow when available (otherwise checks PNG header/structure only), hashes files and reports actual evidence. Mark human visual/marketing approval separately. Export a package only with four verified output files; no project save or poster approval is implied by packaging.
8. Use existing Story Reader project asset/Save/Lock APIs only when a real project and supported poster asset operation exist. Poster approvals are not storyboard shot locks: never attach campaign images to arbitrary shot coordinates or mutate screenplay canon. User may revise any of the four outputs independently with campaign revision tracking.

## Output rules

- `Title_Campaign_Type_Format_v01_WxH.png` (sanitized; no inferred project identity).
- Default raster files are PNG. A user may separately convert to WebP/JPG using actual media processing; never rename an unsupported encoding.
- Maintain an auditable campaign-plan JSON with the saved-source SHA, proposed/promotional copy status, provenance, marketing and rights review status, individual output IDs and independently verified file hashes.
- Keep all four planned output records even when the user requests only a subset; unused outputs remain `planned`, not fabricated.
- Treat user-provided social dimensions as configurable future expansion only after testing; the four above are the v1 fixed defaults.
- Preserve `.ppf.json` and bundled curriculum unchanged. A media package is not a live ChatGPT Project save, printed poster, or online campaign publication.

## Acceptance gates

- All four correct dimensions and stable names, no destination overwrite.
- Wrong size or unreadable image fails closed; missing images stay planned.
- Source digest mismatch aborts all planning.
- Script/copy/media rights and final author approvals stay separate.
- Curriculum refs must match actual bundled lessons, not an invented marketing-course title.
