# REVIEW — inherited Skin V1 IMAGE_REVIEW and MOBILE_STORYBOARD_REVIEW

Breadcrumb HOME / STORYBOARD / [verified story] / Block / Mini / Shot / Review. On desktop, selected exact image + provenance/variants and independent status panel; on mobile stack. Never use a generic web image as private source art. If image bytes inaccessible, say `Media not verified` and show a clearly labeled placeholder.

Four **independent** statuses in order: Human Approved / PPF Saved / PPF Locked / Media Verified. The existing creator-lock-includes-human-approval policy applies to exact saved candidate, while separate explicit creator-message evidence must not be invented. Source locks, Studio sidecar locks, native PPF writes and media hash readbacks are distinct. Tabs in image review: Script / Prompt / Continuity / Audit. Mini-block inspector additionally: Script / Beat / Prompt / Image / Continuity / Save/Lock. Navigation Previous/Next and local tabs are view-only.

Save, Approve & Lock, Unlock, Undo/Resubmit or Request regeneration buttons only submit a **normal explicit turn** containing selected project/shot/version. Elara then checks source hash, candidate hash, expected Studio revision and current permissions, applies real tool-backed change and rereads. Request regeneration NEVER spends by itself. Approval is of exact media only. Template: `../../templates/REVIEW.dil.md`.
