# PP-ENG-UI-001 v1.1 — Skin V2 in-chat acceptance test contract (plugin v2.0.39)

Design lock `PP-SKIN-V2-HOME-LOCK-2026-11-13-01`. Verify host behavior separately from documents, releases, backend data and tool output.

1. Home, Studio, Open Studio and /home render the SAME interactive HOME in the same ChatGPT conversation; same authenticated account and no silent project switch.
2. HOME shows five **operable** cards, **in exact order**: Meet Elara / Learn / Storyboard / Library / Your Stories / Connected Services; Library is card 4 and the total is 5. No sixth REEL/ONCE card.
3. Library / Your Stories visibly distinguishes saved private Studio projects from unverified source-only references using `studio_list_projects`; opening, approval and import are not implied by selection.
4. On desktop and phone, each card is selectable inside conversation without requiring third panel, external website, tab, new chat, extra login or Work. Keyboard/touch accessibility where supported.
5. Storyboard REEL/ONCE, local shot/page/inspector navigation, lesson opening and services checks perform advertised read-only or tool-backed actions; `open_chat_home` data-only output does not count as UI success.
6. HOME and Library entry do not change current source, PPF locks, Studio approvals, timeline or billing; verify readback.
7. Source-linked images/BEATs and six 24-fps audio/video tracks are genuine and exact-hash checked where available; distinguish Studio locks from native PPF, and reference-only records from verified projects.
8. Owner-authorized edits require exact revisions/media SHA, explicit intent and independent persistence readback; no claim of native PPF Library writeback.
9. Provider spending, regeneration, uploads and deletions are opt-in only; privacy and second-account isolation separately verified.
10. Report independently: documentation lock, plugin release update, backend version, actual in-chat rendered controls, phone and desktop tests, functional edit parity, and second-account verification. An untested item remains pending; preserve previous release for rollback.
