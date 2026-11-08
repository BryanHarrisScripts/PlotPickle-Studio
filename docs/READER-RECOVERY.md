# Exact canonical reader recovery — v0.8.33

Source: privately published PlotPickle ChatGPT plugin v0.8.33
Release: `pluginrel_6af0b8fb4dec819181b70bcd777f9963`
Archive: `current.tar.gz`, supplied by the project owner in a ChatGPT conversation. The private archive must NEVER be committed into a public repository.

- Plugin archive SHA-256: `5838a10ec530959635c787d6dd0391c7aabcf740e0e6870950cff103dc4c7dc3`
- Canonical reader archive member: `skills/read-plotpickle-project/scripts/inspect-project.mjs`
- Exact member size: 1,364,997 bytes
- Exact reader SHA-256: `6c9c239f4484d2cd624bfd1c761fa8645203cc8e78be1d58b11ec2500a5f498f`
- Reader extracted safely from owner-supplied archive; no executable tar extensions followed.
- Node 22 and Python 3.13 acceptance run in the conversation's tool environment: 7 story-workflow, 16 Save/Lock, 4 image, 8 project-model, 4 story-change and 3 storyboard-review tests passed individually. Reader identity succeeded on a **synthetic canonical project** generated from FDX.
- The Studio pilot's lightweight `fixture/synthetic-ppf.json` is not a canonical PPF and native reader correctly rejects it with `RAW_STRUCTURE_UNVERIFIABLE`. Do not call this a real-story reader acceptance or suppress the failure.

Recovery attempt: GitHub Actions checks out the pinned public original source in an isolated CI workspace, bundles with a pinned esbuild version and only commits the generated reader into Studio when BOTH the exact SHA-256 and byte length match the owner-supplied archive. A matching build does not prove a current real creator project or its media can reopen. Any compiler mismatch fails closed without claiming source equivalence.

Keep the original PlotPickle desktop repository unchanged. Do not commit the source private archive, logos, user stories, fal media URLs or any original project files.

Even after recovering this reader in GitHub, preserve the current Plugin Creator v0.8.33 release until new Studio branding, current-project host/reader integration, durable private archive backup and full ChatGPT acceptance have been independently verified.
