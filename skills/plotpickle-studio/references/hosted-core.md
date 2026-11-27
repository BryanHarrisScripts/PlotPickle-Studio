# PlotPickle hosted engine — unified in-conversation interactive route (v2.0.38)

**Navigation authority:** `locked-interface-agreement-v1.md` (PP-ENG-UI-001 v1.0, owner-locked). BOTH `Home` and `Studio` display the SAME interactive PlotPickle application **inside the current ChatGPT conversation with Elara**. The prior v2.0.29 "chat-only textual HOME for Studio" route and earlier separate panel launch mapping are SUPERSEDED. The backend and legacy Site remain available infrastructure, not mandatory visible destinations.

## Hydration and evidence, not UI launch

- Home / Studio / Open Studio HOME: the SAME UI route, with the four Skin V1 HOME choices. `open_chat_home` returns only data and `studio_get_core` returns capabilities; successful calls are not proof of an interactive visual render.
- My Stories: `studio_list_projects` for the private Studio catalog, `studio_get_state` for active context, `studio_check_project` before any requested project switch. No arbitrary Library folder scan or silent project load.
- Learn: `studio_list_lessons` and `studio_get_lesson`; preserve the 81 lessons.
- Shot / Editor: `studio_get_state`, `studio_get_image`, `studio_get_beat`, and revisioned `studio_apply_action` for explicit reviewed changes. Six tracks: video, dialogue, action, foley, ambience, music; 24 fps. Do not infer rendering or PPF persistence from view data.
- Explicit legacy visual-editor request ONLY: use appropriate `open_studio_review_editor` or `open_studio_surface` if available, while labeling this a fallback; never auto-launch for Home or Studio.

## Writes, data, security, release truth

Keep ONE existing PlotPickle Studio plugin, MCP host, authenticated account isolation and server-side storage. Original Library PPF/media, Studio sidecar and provider files remain distinct. Use exact source SHA/revision, media SHA and expected Studio revision; read back persisted changes. A creator Studio lock includes approval of that exact media version but is not proof of native PPF writeback. Paid provider jobs need explicit job-specific permission and current prices. Preserve existing projects, approvals, six-track edits and media across updates.

Keep acceptance states distinct: *contract documented*; *plugin version released*; *alias route configured*; *same interactive in-conversation UI visibly rendered*; *phone and desktop tested*; *data read back*; *tool-backed edits verified*; *native PPF writeback verified*; *second account isolated*. Do not claim full interface parity merely from plugin skills, returned MCP data or Site availability.
