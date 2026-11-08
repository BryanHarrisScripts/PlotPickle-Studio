# PlotPickle Fal Clip Intake — version 1

Single source-linked output: one completed fal video provider receipt, one current saved PPF revision, one shot address. The output is an immutable verified draft sidecar, not a native PPF mutation. No cost-bearing provider invocation.

Statuses:
- `completed-provider-video`: fal returned a URL and video metadata, but host video bytes have not yet been accessed and independently inspected.
- `pending-intake`: no direct media download/attachment/FFmpeg channel is available. May display provider video in ChatGPT. Never claim a converted file exists.
- `verified-draft-sidecar`: actual provider MP4 verified by full decode and byte checksum, exact 72-frame 24fps MP4 verified by full decode and SHA256, both linked to one raw PPF SHA and shot identity. Remains pending human creative review and native project import.
- `native-imported-draft`: only after a supported native PPF writer performs guarded save and readback and confirms media bytes, revisions and registration. Not provided by this intake script; don't infer it.
- `approved`: only when explicit separate author acceptance and native Save/Lock are verified. No generation or intake action alone promotes a draft.

Do not store fal account fragment tokens or private submission-status URLs in exported sidecars. Retain public provider media URL, model endpoint, request ID, source shot, raw PPF SHA, original video hash, converted video hash, codec, dimensions, frame count, fps, and decode checks. The native mapped image and first-frame still must be checked independently; a derived contact-sheet crop cannot be claimed identical to the PPF image mapping.

For native motion-span groups of 2–5 shots, a separate group-level conform is required; the single-shot intake script targets one 3-second/72-frame editorial position. Do not silently multiply it to cover an entire mini-block.
