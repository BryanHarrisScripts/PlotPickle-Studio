# PlotPickle — Locked Engineering Agreement: One In-Conversation Interactive Application

**Agreement ID:** PP-ENG-UI-001  
**Version:** 1.0, owner-approved decision baseline  
**Decision date:** 2026-11-13  
**Plugin documentation release:** 2.0.38  
**Status:** LOCKED — normative engineering contract; implementation still subject to acceptance testing  
**Owner authority:** PlotPickle creator. This agreement can be revised only after explicit owner approval of a new numbered revision.

## 1. Decision / immutable product meaning

**Home and Studio are two aliases for the SAME interactive PlotPickle application embedded within the CURRENT ChatGPT conversation, with Elara.** There are not two user experiences or competing launch modes. The application is navigated and used in the conversation, using ChatGPT-supported interactive controls; Elara remains available in that same conversation. The normal user must not be sent to a separate right-hand application panel, browser tab, external website, separate chat, additional sign-in, or ChatGPT Work mode just to use either command.

| User command | Required behavior |
| --- | --- |
| `Home` | Open/display the interactive PlotPickle HOME **inside the current ChatGPT conversation with Elara**. |
| `Studio` | Open/display the **same** interactive PlotPickle HOME **inside the current ChatGPT conversation with Elara**. |
| `Open Studio`, `Open Studio HOME`, `/home` | Resolve to the same unified entry; do not silently switch renderers or launch targets. |

There is ONE user-facing connection, ONE Elara, ONE active ChatGPT conversation, ONE shared authenticated PlotPickle MCP engine and ONE canonical source of project truth. No parallel application, database or conversation bot may be introduced to implement this agreement. Entry by either command is read-only and MUST NOT change the active project, approve/lock assets, mutate the timeline or spend credits.

## 2. The interactive HOME is not a text-only menu

The first view presents the fixed Skin V1 HOME structure, **in this order**:

1. Meet Elara
2. Learn
3. Storyboard
4. Connected Services

A genuine interactive in-conversation view uses host-supported controls to navigate/select, expand or collapse panels, page through shots and open inspectors where supported. Pressing a selectable control performs its advertised local operation or submits an explicit user-intent turn to a real PlotPickle tool. A static text answer, four labels, or a successful MCP `open_chat_home` data response **is not equivalent to passing interactive UI acceptance**. Native widgets are host-dependent; never claim a fully embedded app was displayed when only source data was returned. If controls cannot render, explain the unsupported operation and provide an honest in-conversation fallback without changing the agreed target architecture.

Storyboard retains REEL and ONCE as two paths through the SAME PPF engine. Preserve 81 lessons, 4 acts / 12 sequences / 24 blocks / 96 mini-blocks, 25 planned shot positions per mini-block, the approved source-backed storyboard, review/BEAT inspection, six-track 24-fps editor, images, motion, sound and production pathways. The 25-slot grid and client-local swiping/expansion must not imply persisted data or committed approvals.

## 3. Launch / engineering routing

- `Home` and `Studio`: run the **same** canonical in-conversation HOME route/component. No routing distinction and no command-specific screen.
- `open_chat_home` and `studio_get_core` are permitted as read-only **data** hydration; neither is proof of an interactive render.
- Use authenticated `studio_list_projects` / `studio_get_state` before project-specific work; do not auto-open a remembered project.
- Use real connected MCP tools and source-backed data for Learn, project selection, story shots, BEATs, review, production and Connected Services. The user never has to choose a separate connection.
- Keep legacy `open_studio_home`, `open_studio_surface`, `open_studio_review_editor` and the hosted Site/visual editor available for optional, **explicitly requested** legacy operations or parity testing. They MUST NOT automatically execute for `Home` or `Studio` and are NOT a required main interface.
- The Sites-hosted MCP backend is infrastructure, not a second mandatory user-facing web app. Do not disable its binding, authentication, account isolation or storage.
- A native ChatGPT app view/third-panel launch, external URL, website login, separate conversation, iframe or Work redirect is NOT a substitute for the contracted in-conversation view.

## 4. Data ownership and safety

The original user-owned PPF and media remain authoritative. Studio-side review/cut records remain distinct from native Library PPF writes. Read exact project ID, PPF revision and SHA-256, shot/asset hashes and Studio revision before guarded changes; independently read back afterward. Creator approval/lock applies only to the exact selected version. A command to display HOME is never consent to save, lock, switch, delete or pay. Paid image/video/music jobs require current price/model information and explicit per-job authorization. No new mandatory local app, tunnel, GitHub flow, credential entry, storage account, independent web chat, or duplicate project service.

## 5. Acceptance test contract (required before claiming complete)

**A1 — Alias parity:** In the *same* ChatGPT conversation, `Home`, `Studio` and `Open Studio HOME` yield the same interactive HOME navigation and project state. No mode differences.

**A2 — In-place operation:** The interactive controls render *inside the conversation*. They work on desktop and phone with tap/click, accessible keyboard where supported, and appropriate touch navigation. No side-panel launch or tab/new-window/Work/login transition is required.

**A3 — Genuine interaction:** HOME cards navigate; Storyboard presents REEL/ONCE; shot/page controls and inspector operate without fake results. Client-local changes are labeled local. `open_chat_home` returning success alone fails this test.

**A4 — Backend truth:** When authenticated, lessons and actual project/shot/BEAT/visual data are read from the same connected tools. Errors, inactive projects and unavailable media are disclosed. No project switch on HOME.

**A5 — Guarded edits:** With explicit owner authorization, a selected shot Save/Approve & Lock/Unlock or timeline change is revision/hash-guarded and independently read back; no false native-PPF write claim. All six tracks, existing approvals and history survive navigation/reopen.

**A6 — Parity and non-regression:** No extra plugin/account is needed; second-account isolation is verified separately; existing project storage, source media, learning materials, production services and legacy editor are not damaged. Older versions may be restored from retained releases.

**A7 — Honest release reporting:** Report separately: documentation lock; plugin release installed; same-command routing configured; in-conversation UI actually rendered; device acceptance; backend correctness; and editing parity. None proves the next automatically.

## 6. Ownership, precedence and change control

This agreement supersedes contrary **navigation** directions in earlier `plotpickle-welcome`, `plotpickle-studio`, `plotpickle-unified-application`, v2.0.29 chat-only guidance, v2.0.28 Studio-panel guidance, and the historical 2026-11-08 sidebar brief. It does NOT supersede those documents' safety, privacy, preservation, media provenance or editorial contracts.

**Locked engineering rule:** NEVER reinterpret `Home` and `Studio` as different entry points or downgrade their target to a static menu, a separate side panel or a website without a new numbered agreement explicitly approved by the creator. No automatic release, coding assistant, plugin update or backend fallback may silently amend this decision. Preserve this document in each subsequent release and include alias-parity tests in review. Mark any temporary host limitation as a *gap against the agreement*, not an approved product redesign.

## 7. Implementation status at documentation lock

The release containing this agreement documents the contract and corrects the plugin's entry instructions; it does **not** by itself deploy a new ChatGPT rendering runtime, change the Site application, prove on-device interactions, or grant native PPF writeback. The existing backend may report a different server version from the plugin package. Claim the interface fully implemented only after A1–A7 are independently exercised with the real ChatGPT host.
