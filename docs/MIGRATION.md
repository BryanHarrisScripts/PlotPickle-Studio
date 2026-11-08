# PlotPickle Studio v0.8.33 migration record

- Source: existing published ChatGPT private plugin `plugins_6aedd4f5ac1481919653cf6110d565ba`
- Exact source release ID: `pluginrel_6af0b8fb4dec819181b70bcd777f9963`
- Version: `0.8.33`
- Destination: `BryanHarrisScripts/PlotPickle-Studio` (public GitHub repository)
- Original `BryanHarrisScripts/PlotPickle` desktop repository: **unchanged** by this import
- Source enumeration: **145 paths** in the published release; **140 source paths** imported to this candidate tree.

## Paths intentionally NOT copied into the public GitHub source candidate

1. `assets/composer-icon.png` — 17,731-byte image packaged in the historical v0.8.33 ChatGPT plugin. This is original PlotPickle branding and MUST stay with the original PlotPickle project. Do not migrate it into Studio; create a distinct PlotPickle Studio composer icon for the next release.
2. `assets/plotpickle-logo.png` — 175,017-byte image packaged in the historical v0.8.33 plugin. This is original PlotPickle branding and MUST stay with the original PlotPickle project. Do not migrate it into Studio; create a distinct Studio logo, and update both manifests to refer only to new Studio-owned asset paths.
3. `skills/read-plotpickle-project/scripts/inspect-project.mjs` — original 1,364,997-byte generated native reader bundle; single-file text-read API is limited to 1 MiB. Recover exact release bytes or rebuild from the pinned canonical parser source and independently verify.
4. `skills/plotpickle-editor/windows/the-third-bell-seed.json` — sample editor seed includes a specific fal media URL. Deliberately omitted to avoid publishing creator media references. Replace with a synthetic fixture without user-specific URLs before packaging.
5. `skills/plotpickle-creative/scripts/__pycache__/service-catalog.cpython-313.pyc` — generated Python bytecode cache, correctly omitted from source control; do not include in release.

The public GitHub tree is intentionally NOT a byte-for-byte copy of the published plugin: the original PlotPickle logo and icon are excluded by owner direction and must NOT be copied. A new Studio-branded release requires distinct Studio assets, manifest path updates, a restored and tested project inspector, and a sanitized editor seed. Do not call the next release ready while these gaps remain.

## Code and release authority

- The first import commit preserved the published v0.8.33 manifests verbatim. A second, separate candidate commit sets both manifest versions to **0.8.34** and changes their repository URL to **PlotPickle-Studio**; this 0.8.34 candidate has **not** been published to ChatGPT. The historical source state is preserved by the earlier commit.
- Existing open PRs #3412, #3413 and #3414 in the original repo are **historical source/evidence candidates**, not additional files silently merged into this repository.
- Do not merge or close original desktop PRs or issues merely because Studio imports some code.
- Keep original Windows-only Factory, Windows launcher, original PlotPickle logos, images, diagrams, brand assets and unrelated app code in the original repository. The two historical image references in the v0.8.33 manifests are migration placeholders only; no original graphic is to be copied to Studio.
- Do not commit user-supplied `.ppf.json` story exports, private screenplay drafts, provider tokens, original fal videos or authenticated job URLs.
- License at this repository root is AGPL v3. Inspect imported dependencies and ownership before redistribution.

## Release-ready acceptance checklist

- [ ] Design/approve NEW PlotPickle Studio-specific composer icon and logo (no original PlotPickle graphic imports); add their bytes to Studio and update both manifests to new Studio asset paths
- [ ] Bundled project inspector restored and test-built from a traceable source
- [ ] Editor seed replaced with sanitized synthetic media data, or the code updated to require a creator-provided seed
- [x] Both plugin manifests' repository references changed to the new repository in unpublished v0.8.34 candidate
- [ ] Full test suite and package/archive comparison pass in a clean environment
- [ ] ChatGPT host smoke test and source-linked persisted-project read test pass
- [ ] GitHub commit / tagged release -> Plugin Creator update -> deployed release ID independently verified
- [ ] Public-source privacy and dependency licence audit completed

A source-only GitHub Actions check now runs the standalone Studio pilot syntax/tests and source-manifest audit. Passing this is NOT proof of a complete plugin build, media integrity, authenticated ChatGPT host install or published release. GitHub alone does not automatically synchronize ChatGPT conversations, private projects, user-generated images, cloud-provider assets or plugin publications.

## Owner-confirmed execution priority (November 8, 2026)

1. **Restore and verify the native story reader first.** The published ChatGPT v0.8.33 plugin still contains the generated inspector bundle, but the public GitHub Studio source does not. It is not valid to claim native PPF read/Save/Lock verification until the exact reader is restored or reproducibly rebuilt and tested against canonical project fixtures.
2. **Preserve The Third Bell and cleanly separate test fixtures.** The real `the-third-bell-seed.json` in the published ChatGPT v0.8.33 plugin includes screenplay shot links and a concrete fal Shot 01 media URL/request ID. It is not disposable test data and must remain intact as creator project evidence. Public Studio tests use `skills/plotpickle-editor/windows/fixtures/editor-seed.synthetic.json` instead; the public fixture contains no real story, provider URL, request ID or media bytes. Never remove the original from the live plugin as part of source cleanup; first migrate actual user project data into authenticated private story storage with verified reopen.
3. **Create independent Studio branding last.** New Studio-specific logo and composer icon; original PlotPickle logos, illustrations and diagrams stay in the desktop PlotPickle project. No new logo or icon has been approved yet.

## ChatGPT build, backup and integration gate

The owner specifies that the **full plugin build and update are done within ChatGPT using the Plugin Creator workflow**, not by claiming that a GitHub source test publishes or installs a plugin. GitHub stores auditable source, history, fixtures and source-only CI tests. Before publishing any new version:

- Pin the current ChatGPT plugin ID and release ID; verify the current published version still matches the intended backup (v0.8.33 as of this record).
- Retrieve the complete current-release Plugin Creator archive and create a **durable, private, checksum-verified backup** outside the public source repository. A successful archive-URL lookup or retained historical release ID alone does **not** establish durable backup verification.
- Keep The Third Bell project seed and generated fal media references in appropriate private storage. Preserve historical release access; never expose media URLs/creator assets in public source.
- Build and publish the next plugin archive through ChatGPT Plugin Creator with its expected-release guard. Check asset inclusion, native reader integrity and ChatGPT interface from the actual returned deployed release, not simply from GitHub tests.
- Read back exact installed version and release ID, verify critical files and real PPF/project reopen and editor handoffs. Verify rollback from the privately retained pre-update archive and documented history.
- Do not call GitHub and ChatGPT auto-synchronized until an actual secure publish workflow is wired and tested. A PR merge only updates GitHub.

As of this record, ChatGPT Plugin Creator listed v0.8.33 as current (`pluginrel_6af0b8fb4dec819181b70bcd777f9963`) and its archive retrieval endpoint was available. **A private downloaded backup and restore test have not yet been completed.** A full v0.8.34 ChatGPT build, publication and integration test have not been completed.
