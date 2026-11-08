# Canonical PlotPickle OSS Radar source map (read-only)

Identity (owner and repository are fixed; never switch to public OSSRadar platforms):
- Repository: https://github.com/BryanHarrisScripts/PlotPickle
- Radar source: https://github.com/BryanHarrisScripts/PlotPickle/tree/main/lib/verification/oss-radar
- Discovery contract: https://github.com/BryanHarrisScripts/PlotPickle/blob/main/config/oss-radar/discovery-contract.json
- Creative Focus: https://github.com/BryanHarrisScripts/PlotPickle/blob/main/config/oss-radar/creative-focus.json
- Learning & Evolution proposals: https://github.com/BryanHarrisScripts/PlotPickle/blob/main/lib/verification/oss-radar/learning-evolution/review-proposals.mjs
- GitHub Actions schedule: https://github.com/BryanHarrisScripts/PlotPickle/blob/main/.github/workflows/oss-radar.yml
- Human-readable report issue search: https://github.com/BryanHarrisScripts/PlotPickle/issues?q=%22%5BOSS+RADAR%5D%22
- November 2026 archive example: https://github.com/BryanHarrisScripts/PlotPickle/issues/3364

As of verification on 2026-11-07, a dated 2026-11-06 report existed in the November issue; this is a HISTORICAL observation, not live state for future chats.

Discovery: inspect report issue comments bearing `<!-- PLOTPICKLE-OSS-RADAR-DAY:YYYY-MM-DD -->`; the matching header is `## OSS Radar — YYYY-MM-DD`. Reports are dated in UTC; compare by report date. If the latest comment is missing or inaccessible, return `unavailable`, not a guessed shortlist. The issue body is a charter, not the day's discovery. Archive comments can be large; inspect focused portions without silently discarding evidence or pretending all content was reviewed.

Typical report sections describe GitHub discovery, enrichment, ranked findings, Creative Focus Top 3 and learning/teaching handoff. If the actual report lacks one of these sections, report it as absent. Do not treat counts as evidence of a successful nightly run without checking workflow run status when asked. The report can include unavailable/partial states; preserve them.

No credentials needed for public viewing. User-installed GitHub tools can read the source; a read-only standard-library helper is available for supported plugin script runtimes. Never configure other services under the similar name OSS Radar. Approval flow: DISCOVER -> VERIFY -> REVIEW -> EXPERIMENT -> ACCEPTED CHANGE, with the final phase requiring separate verified implementation. No runtime mutation or skill auto-update in this release.
