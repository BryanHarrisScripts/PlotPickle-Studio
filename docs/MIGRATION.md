# PlotPickle Studio v0.8.33 migration record

- Source: existing published ChatGPT private plugin `plugins_6aedd4f5ac1481919653cf6110d565ba`
- Exact source release ID: `pluginrel_6af0b8fb4dec819181b70bcd777f9963`
- Version: `0.8.33`
- Destination: `BryanHarrisScripts/PlotPickle-Studio` (public GitHub repository)
- Original `BryanHarrisScripts/PlotPickle` desktop repository: **unchanged** by this import
- Source enumeration: **145 paths** in the published release; **140 source paths** imported to this candidate tree.

## Paths intentionally NOT copied into the public GitHub source candidate

1. `assets/composer-icon.png` — original 17,731-byte binary image; exact bytes still required for a reproducible package.
2. `assets/plotpickle-logo.png` — original 175,017-byte binary image; exact bytes still required.
3. `skills/read-plotpickle-project/scripts/inspect-project.mjs` — original 1,364,997-byte generated native reader bundle; single-file text-read API is limited to 1 MiB. Recover exact release bytes or rebuild from the pinned canonical parser source and independently verify.
4. `skills/plotpickle-editor/windows/the-third-bell-seed.json` — sample editor seed includes a specific fal media URL. Deliberately omitted to avoid publishing creator media references. Replace with a synthetic fixture without user-specific URLs before packaging.
5. `skills/plotpickle-creative/scripts/__pycache__/service-catalog.cpython-313.pyc` — generated Python bytecode cache, correctly omitted from source control; do not include in release.

The public GitHub tree is not a byte-for-byte copy of the published plugin until the first four missing release inputs are recovered or replaced through an authorized, reviewed build. Do not claim the next release is ready while these gaps remain.

## Code and release authority

- The first import commit preserved the published v0.8.33 manifests verbatim. A second, separate candidate commit sets both manifest versions to **0.8.34** and changes their repository URL to **PlotPickle-Studio**; this 0.8.34 candidate has **not** been published to ChatGPT. The historical source state is preserved by the earlier commit.
- Existing open PRs #3412, #3413 and #3414 in the original repo are **historical source/evidence candidates**, not additional files silently merged into this repository.
- Do not merge or close original desktop PRs or issues merely because Studio imports some code.
- Keep original Windows-only Factory, Windows launcher and unrelated app code in the original repository.
- Do not commit user-supplied `.ppf.json` story exports, private screenplay drafts, provider tokens, original fal videos or authenticated job URLs.
- License at this repository root is AGPL v3. Inspect imported dependencies and ownership before redistribution.

## Release-ready acceptance checklist

- [ ] Exact binary icon and logo imported, hashes checked against the published release
- [ ] Bundled project inspector restored and test-built from a traceable source
- [ ] Editor seed replaced with sanitized synthetic media data, or the code updated to require a creator-provided seed
- [x] Both plugin manifests' repository references changed to the new repository in unpublished v0.8.34 candidate
- [ ] Full test suite and package/archive comparison pass in a clean environment
- [ ] ChatGPT host smoke test and source-linked persisted-project read test pass
- [ ] GitHub commit / tagged release -> Plugin Creator update -> deployed release ID independently verified
- [ ] Public-source privacy and dependency licence audit completed

A source-only GitHub Actions check now runs the standalone Studio pilot syntax/tests and source-manifest audit. Passing this is NOT proof of a complete plugin build, media integrity, authenticated ChatGPT host install or published release. GitHub alone does not automatically synchronize ChatGPT conversations, private projects, user-generated images, cloud-provider assets or plugin publications.
