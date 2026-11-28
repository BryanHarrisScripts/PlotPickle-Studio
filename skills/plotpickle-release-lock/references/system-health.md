# /systemhealth

Show a read-only release and operational health report. Use the coordinated target from the current release brief or ledger. Report the time in America/Toronto. Refresh the evidence on every invocation.

## Production version register

Use one row per surface with columns for live version, candidate version, target, evidence and next action. Use **Unverified** when access or version readback is missing. Record backend, rendered UI, Git revision and deployment state separately. Group the Surface column under **Chat**, **Web**, and **Work/Codex**, in that order.

| Surface | Readback required |
|---|---|
| **Chat** | |
| ChatGPT plugin | Current Plugin Creator release ID and both manifests. Verify the active Chat installation separately. |
| Studio HOME in Chat | Tool response, five-card order and rendered panel version when requested. |
| **Web** | |
| PlotPickle.com | Rendered homepage footer and release link. |
| [Studio HOME on the web](https://plotpickle.com/home) | Verify the rendered release version. |
| [Studio Editor on the web](https://plotpickle.com/studio) | Verify the sign-in redirect, signed-in version and six-track editor. |
| Meet Elara on the web | Public entry link, intended route and shared footer version where applicable. |
| **Work/Codex** | |
| Sites deployment | Live deployment, hosting revision and source commit. |
| GitHub main and README | Both checked-in manifests, documented release and deployed source mapping. |
| GitHub tag and Release | Exact source commit, published status, ZIP manifests and asset checksums. |

Show shared connections and storage in **Connections and diagnostics**. List Studio MCP once and verify its configured endpoint, authenticated initialize version, Studio core version. Label the Studio working-copy storage row **PlotPickle Studio Space** and show its readback and data revision. Keep **ChatGPT Space** as its own connection row. List the two unused development tunnels with their last reported versions in diagnostics.

The hosting revision and Studio, source PPF and editorial revisions are separate identifiers. ChatGPT Space has its own lifecycle. If present, list the Test Tunnel and Factory MCP Tunnel as development connections with independently observed versions and no coordinated production target.

Use `plotpickle.com` for production web checks. The retired `studio.plotpickle.com` hostname is outside the test inventory. The Sites-hosted URL is a diagnostic fallback.

## Studio surface inventory

List each Studio surface under Chat or Web according to its supported entry points. Check the rendered or signed-in surface using its normal entry point. The active release may be shown in a shared shell or footer. Avoid adding individual version constants to these views.

- HOME (Skin V2), Meet Elara, Learn (12 topics and 81 baseline lessons, plus the animation supplement), Storyboard, REEL, ONCE, Library / Your Stories and Connected Services.
- Story Map, Shot Grid, Review, six-track Editor, Pitch Edit, Reports, Pitch Package and System Records.
- Report tool response, data readback and visible release separately when evidence differs.

## Functional health and acceptance

- Verify signed-in connection, project readback and Connected Services. Record independent isolation testing separately.
- Report any completed Save → independent reopen → Lock → readback test and its environment. The Studio working copy is the acceptance target. Report Space file selection, automatic access and native Space PPF writeback as separate capabilities.
- Report editor tracks and render freshness from current evidence. Check Elara’s motion triggers and curriculum supplement separately.
- If authorized, summarize the active project’s registered images, verified originals, confirmed locks and source, Studio and editorial revisions in the private report. Leave approval and media records untouched. No writes, paid provider calls, generation or deployment are part of this command.
- Mark the coordinated release pending whenever a required live surface or acceptance check is unverified. Give the next action for each gap and identify the evidence source.
