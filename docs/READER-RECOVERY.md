# Exact canonical reader source recovery — owner-provided bytes

The owner provided the full current plugin v0.8.33 archive directly to the ChatGPT session. This is a private-source backup that must NOT be uploaded to public GitHub.

Reader included in archive:
- Path: `skills/read-plotpickle-project/scripts/inspect-project.mjs`
- Exact size: `1,364,997` bytes
- SHA-256: `6c9c239f4484d2cd624bfd1c761fa8645203cc8e78be1d58b11ec2500a5f498f`
- Original v0.8.33 archive SHA-256: `5838a10ec530959635c787d6dd0391c7aabcf740e0e6870950cff103dc4c7dc3`

Reader-only ZIP and standalone MJS files were prepared in the private ChatGPT execution environment. They contain no original branding or The Third Bell seed. The repository's available GitHub connector accepts UTF-8 inline source, not a local file upload. The attempted public-source rebuild in the previous commit produced a different SHA-256 and was correctly refused before commit.

The next step is to upload ONLY the verified single `inspect-project.mjs` file into the already-existing `skills/read-plotpickle-project/scripts/` folder of this PR branch. Do not upload or extract the entire private plugin archive to the public repository. GitHub Actions then verifies exact SHA and runs six synthetic canonical-reader test suites. The Studio user-facing PPF reopen/integration test remains a separate acceptance gate.

Private archive source release: `pluginrel_6af0b8fb4dec819181b70bcd777f9963`.
Original PlotPickle desktop repository is not modified.
