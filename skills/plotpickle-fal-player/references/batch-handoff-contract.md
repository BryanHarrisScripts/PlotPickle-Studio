# PlotPickle fal Player — private batch handoff contract v1 (v0.8.40)

The private source manifest is authoritative only as a job/source **reference**. It is not a media receipt until actual MP4 bytes are fully decoded and hashed. The connected fal player renders provider-completed results, while the local batch assembler consumes real files and produces independent verified 24fps drafts.

Required JSON shape (synthetic filenames and IDs only; no actual creator data in public source):

```json
{
  "schema": "plotpickle.fal-shot-batch.v1",
  "projectId": "synthetic-project-id",
  "revision": 3,
  "rawSha256": "REPLACE_WITH_ACTUAL_SOURCE_SHA256",
  "block": 1,
  "miniBlock": 1,
  "shots": [
    {
      "shot": 1,
      "status": "completed-provider-video",
      "endpointId": "alibaba/wan-3.0-prime/image-to-video",
      "requestId": "ORIGINAL_REQUEST_ID",
      "url": "https://v3b.fal.media/files/example/shot-01.mp4",
      "file": "shot-01.mp4",
      "reportedBytes": 1234567
    }
  ]
}
```

The helper accepts 1–5 **consecutive** shots within one Mini-Block; the real manifest should include one row per original provider MP4 with the exact named local input file and provider-reported byte length. Source images, PPF, prompts and job identifiers should be sourced through authorized private project files and fal tools, never guessed. Do not include private account-receipt fragments, status URLs or CDN authorization fragments in a shared manifest. Do not treat an externally hosted MP4 URL alone as downloaded bytes. Do not upload this private source manifest into the public plugin or GitHub.

Acceptance states: `fal-submitted`, `completed-provider-video`, `fal-library-saved`, `pending-intake`, `verified-draft-sidecar`, `editor-imported-verified`, `native-imported-draft`, and `creative-approved`. These do not imply one another. Single-shot PPF still Save/Lock and the creative review of generated video remain separate. One completed shot cannot silently approve its neighbor. For a 3-shot group, 72/144/216-frame boundaries and SHA-256 hashes must be measured on actual bytes; only claim a 216-frame nine-second 24fps draft when the helper prints success and files/receipt exist.

The current Windows editor prototype's verified ingest and render cover one clip, not a true three-shot editable timeline. The combined output is an independently rendered draft sidecar until a supported editor import and readback are implemented. Never describe fal's excellent in-chat player as an owned/embedded custom PlotPickle player implementation; PlotPickle delegates playback through the connected fal app's actual display tools.
