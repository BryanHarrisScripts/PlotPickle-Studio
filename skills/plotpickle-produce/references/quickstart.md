# Produce quickstart, 24 fps

Use only actual source bytes and an exact PPF. For an original completed fal 3-second MP4 available in an authorized runtime:

    python3 scripts/produce_editor.py conform --source original.mp4 --out shot01-24fps.mp4 --frames 72

To build a source-bound sidecar without changing PPF:

    python3 scripts/produce_editor.py init --project project.ppf.json --project-id PROJECT_ID --title 'Film draft' --out timeline.json

For video entries set kind `video`, path to the actual conformed MP4, SHA-256, startFrame, durationFrames. For still holds set kind `image`, actual image path, SHA-256 and exact frame duration. Supply contiguous positive video segments and exactly six track arrays in timeline. Then:

    python3 scripts/produce_editor.py validate --timeline timeline.json --media-root media/ --project project.ppf.json
    python3 scripts/produce_editor.py render --timeline timeline.json --media-root media/ --project project.ppf.json --out rough-cut.mp4

Every render emits an independent receipt. Final acceptance requires source hash, full decode, exact frame count/fps/resolution, and creator review. No GitHub CI or Windows app is mandatory.
