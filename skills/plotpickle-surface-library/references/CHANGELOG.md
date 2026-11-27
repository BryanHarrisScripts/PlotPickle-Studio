# Surface Library changelog

## 1.0.0 — Plugin 2.0.40 — 2026-11-13

- Created one versioned registry and five reusable in-chat surface contracts/templates: HOME, STORYBOARD, LIBRARY_YOUR_STORIES, REVIEW, EDITOR.
- Locked HOME order unchanged: Meet Elara / Learn / Storyboard / Library / Your Stories / Connected Services, with Library fourth.
- Preserved Skin V2 owner approval unchanged, Skin V1 approved Storyboard and Image Review, and Editor in nonlocked draft state.
- Added versioned route resolution, test suite, and action/privacy boundary documentation.
- No new MCP connection, site deployment, private story copies, media generation or Source PPF changes.

**Version policy:** bump Surface Library minor for backwards-compatible new surfaces, patch for fixes that do not alter locked layout; bump major and obtain explicit owner approval for locked navigation/visual changes. Plugin releases have separate semver and keep their identity/bindings. Retain previous registry versions when changing schema.
