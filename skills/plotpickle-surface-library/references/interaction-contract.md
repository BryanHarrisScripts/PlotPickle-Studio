# Shared interactive contract — in-chat surfaces

## Rendering and route ownership

- Top-level aliases: `Home`, `Studio`, `Open Studio`, `Open Studio HOME`, `/home` → `HOME`. Never open a distinct app frame, tab or Website to fulfill them.
- All HOME cards are `pressable` surfaces or equivalent real in-chat selection controls; selected card expands *below* the cards in the same conversation. Two columns on wide screens; single column on phone; card five may span wide row.
- In a live response, `{@body ...}` state may hold local `selected`, `page`, `shot`, `tab`, `expanded`, `path`. Local UI operations require no MCP write. Any **external** action uses a button with `GenUI.issueNewTurn` carrying clear exact user intent, followed by tool-mediated confirmation. Never mark persisted success on click alone.
- Do not implement buttons that claim a tool write before a real action and readback. If an interactive host control is not supported, keep the same order and offer in-chat conversational navigation.

## Data and presentation

| Surface | Read before display | Never imply |
| --- | --- | --- |
| HOME | optionally `studio_get_core`, `open_chat_home` and `studio_get_state` for source context | loaded current story without state evidence |
| STORYBOARD | current source and `studio_get_state` where relevant | planned slot = authored/verified image |
| LIBRARY_YOUR_STORIES | `studio_list_projects` / `studio_get_state` | auto enumeration of ChatGPT Library, reference = imported project |
| REVIEW | `studio_get_state`, selected `studio_get_image`, `studio_get_beat` and current source provenance | image lock = native Library PPF modification |
| EDITOR | `studio_get_state`, optionally `studio_prepare_render` | a rendered MP4, active audio lane, approved master |

Footer must distinguish actual project loaded vs no active project, and verified data vs unknown. No optimistic approval badges based on design samples.

## Source-backed write protocol

1. User chooses an exact project/shot/media version or typed timeline operation.
2. Elara rereads current project ID, source revision + SHA, asset SHA and Studio expected revision.
3. Validate action eligibility, permissions and any applicable cost/consent.
4. Submit real `studio_apply_action` / supported operation, if eligible.
5. Reread current state and report confirmed new revision or an error. Studio sidecar is not native PPF writeback.
6. Paid image/motion/music requests require verified per-job model/price and explicit authorization. Regeneration discussion is not submission.

## Visual tokens

Use locked brand asset `assets/branding-locked/studio-logo-approved.png` only when host supports displaying real plugin assets. Otherwise textual `PLOTPICKLE / STUDIO` branding is a fallback, not a replacement approved logo. Matte black + off-white + restrained purple, compact 4px rhythm. Breadcrumb and Back must preserve current source pin; no invented story title on an anonymous page.
