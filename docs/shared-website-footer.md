# Shared website footer — deployment specification

Status: requested, not deployed. This file documents the intended hosted website change; it does not trigger a deployment.

## Scope

Use one shared footer component on these three routes:
- https://plotpickle.avairis.chatgpt.site/
- https://plotpickle.avairis.chatgpt.site/studio
- https://plotpickle.avairis.chatgpt.site/home

## Visible footer

**PlotPickle Studio**

Your story. Your decisions. Your cut.

[Website](https://plotpickle.com) · [Open Studio](https://plotpickle.avairis.chatgpt.site/studio) · [Home](https://plotpickle.avairis.chatgpt.site/home) · [Download](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases) · [GitHub](https://github.com/BryanHarrisScripts/PlotPickle-Studio)

[Support](https://plotpickle.com/support/) · [Privacy](https://plotpickle.com/privacy/) · [Terms](https://plotpickle.com/terms/) · [Licence](https://plotpickle.com/legal/)

© 2026 PlotPickle · Independent creative project

v2.0.55 · [Release information](https://github.com/BryanHarrisScripts/PlotPickle-Studio/releases/tag/v2.0.55)

## Implementation requirements

- Preserve page content, existing layout/branding and workspace data; change only the shared footer.
- Replace old duplicated technical links and version strings with one release line. Populate that line from the actual verified deployed release manifest; v2.0.55 is the latest GitHub release as checked on 2026-11-27, not a verified synchronized website/MCP deployment. If versions differ, do not misrepresent them; retain accurate component details in release information and indicate synchronization pending until reconciled.
- Website remains the public marketing domain; Open Studio and Home use the explicitly supplied hosted routes. Home is included so all requested surfaces are navigable. Remove tracking query parameters.
- Verify all link destinations and render the same footer at all three routes on desktop and mobile before marking deployed. The hosted /studio and /home and public support/privacy/terms URLs could not be independently fetched in the current session; this is not proof they are broken.
- Do not change or republish the existing plugin package merely to make a footer version label match. No project or media changes.
