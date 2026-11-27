# Conversational swipe storyboard — interaction contract v1

- **Collapsed:** small PlotPickle card inside Elara chat, story title if verified, shot counter `01 / 25`, `Expand storyboard` button; use no private story artwork unless real exact verified bytes are accessible.
- **Expanded:** responsive large in-message view, one chosen shot, horizontal swipe carousel, Previous/Next, page index (`Page 1–5`), 25-position overview, source/approval count. Retain current selected shot when collapsing.
- **Inspector:** in-card / pull-up detail area with six sections: Script, BEAT, Visual, Continuity, Production, Status. Tap `Details` to open; tap Close to return. On iPhone, all functions reachable by touch and keyboard; do not hijack ChatGPT navigation swipe gestures.
- **Saved inactive project:** read-only catalogue badge, no source media loaded, no actions that look as if they update backend. User must explicitly load before real editing. The gallery may show structural slots with verified count badges, but not claim to display 25 original images.
- **Actions:** `Review with Elara` can submit an ordinary new turn requesting grounded review for the selected shot. Save/Approve & Lock/Unlock/Resubmit invoke only exact guarded tool calls after user-specific verification; actions are disabled or omitted until available. A gesture must never spend money or set approval.
- **No invisible host claims:** ChatGPT system level full-screen/side-panel/swipe cannot be controlled by plugin skill. Within-card expand, carousel swipe and inspector are the feature; if host cannot display they fall back to simple buttons.
- **Quality:** no duplicate app/logins, no cross-account project leakage, no source document mutation on viewing, no HTML mass of 2400 shots, readable on 375px-wide phone, exact stored revision for all writes.

Acceptance checklist (verify, do not assert without evidence):
- [ ] In-chat card appears for a real user on iOS.
- [ ] Horizontal swipe changes selected shot without model roundtrip.
- [ ] Expand and inspector work without switching projects.
- [ ] Card collapses with selected shot retained.
- [ ] Actual media and BEAT are loaded only with authorized current source.
- [ ] Save/Lock actions persist and are independently read back.
- [ ] All six timeline tracks can be manipulated and verified or a visible fallback is retained.
