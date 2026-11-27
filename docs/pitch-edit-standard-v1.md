# PlotPickle Pitch Edit — Standard v1

Owner direction: Bryan Harris, 20 November 2026.

Pitch Edit is the single name for PlotPickle's cinematic story presentation cut. The target is a compelling full-story pitch package, using the approved collection for The Boy Who Collected Tomorrow as the creative precedent. Its current deployed media and render must be independently verified before reuse.

## Output and assembly

- Cinematic landscape MP4, H.264, 1920×1080, 24 fps; preserve original composition with fitting, never destructive stretching.
- Assemble in the existing six-track editor: Video, Dialogue, Action, Foley, Ambience, Music.
- Approved, saved and locked images supply picture; approved motion may replace or supplement the corresponding still positions. No requirement to generate motion for every image.
- Use editorial timing appropriate to each story beat, saved in whole frames. No fixed total runtime is inferred from image count.
- Add approved source-linked dialogue, sound and music when available. Empty lanes remain honestly empty; captions or cue markers are not performed audio.
- A pitch package contains the viewing MP4, a shot/timing manifest, exact media provenance and a clearly stated coverage report. Additional pitch materials can accompany it when requested.

## Governance

- Preserve exact original bytes, project identity, source passage links, 24-block/4-mini-block/25-shot addresses, approvals and locks.
- Creator lock includes human approval. Reference locks do not automatically approve storyboard frames; a Pitch Edit render is separately reviewed.
- Rejected and superseded images do not enter the current cut.
- Work in progress may be rendered as a clearly labelled partial Pitch Edit. Full-story status requires complete intended story coverage.
- Validate source identity, image and motion hashes, frame count, dimensions, duration, audio and full MP4 decode before marking a render current. Any timeline change makes the previous render stale.
- The ongoing movie image workflow remains 24 blocks × 4 mini-blocks × 25 shots. Continue in batches of five from the saved position.

## Implementation

PNG and WebP storyboard originals use exact byte hashes and imported creator lock records. Pitch Edit sources retain all mini-blocks in one project, with staged uploads. Provisional three-second image holds are editable and clearly labelled as draft timing. Incomplete coverage remains a partial story.
