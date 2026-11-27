# Source-backed in-chat inspector — v2.0.32

This implements the creator-approved faster ChatGPT UI without a second PlotPickle connection.

## Read-only route (works for inactive saved films)

1. Obtain the real current PPF from an authorized chat attachment/Library file; never from the distributed plugin bundle or memorized story content. Obtain current source revision/SHA from the signed-in private catalogue via `studio_list_projects` and check with `studio_check_project`. Read `studio_get_state` to confirm whether the film is active; DO NOT switch it as a side effect of viewing.
2. Use `scripts/inspect_saved_storyboard.py <ppf.json> --sha256 <expected raw SHA>` to get the selected 25-shot source snapshot. It checks raw bytes and exact PPF identity, 25 planned positions, screenplay passage IDs, asset/shot labels, camera plans, native PPF saved/locked markers, and explicit versus pending visual approval. No media bytes are loaded from this PPF: the package flag is historic verification, not a live image readback. The script has no writes, credentials, network, or provider actions.
3. Bind the produced 25 titles, planning purposes, camera and source statuses to the in-chat swipeable carousel and six-tab inspector. Label source status exactly **PPF source vX**. Client-local page, shot and tab selection must be instantaneous and must not invoke an AI roundtrip.
4. Never claim source `authoredBeats=[]` means there are no Studio BEATs. On an inactive film the Studio BEAT record isn't available through current source-reading tools. Show **Studio BEAT not checked**, and keep the original artwork separate from a contact sheet or preview montage. A Library contact sheet may be shown as a labeled reference only, not 25 original image-byte verifications.
5. Source `locked:true` alongside `visualApproval.state=pending-user-review` is NOT equivalent to an individually explicit creator visual approval. Show both indicators independently, even when all 25 are default saved/locked. The existing creator-lock-includes-approval policy applies to actual creator-triggered Studio locks, not a retroactive claim that every default source lock was individually approved.
6. Source-only snapshots are never the expected current Studio revision for a write. For Save/Lock/Unlock/Resubmit call live `studio_get_state`, verify active project identity, exact revision and image SHA, obtain explicit creator action, use guarded `studio_apply_action` and independent readback. A Save/Lock button that merely looks clickable is prohibited. Native PPF writes are not available through the current Studio MCP bridge.

## Interaction parity

- Inline expanded card, local carousel swipe and Previous/Next, 5 pages, 25 position grid, six tab inspector. No mandatory external tab or separate sign-in.
- Screenplay/BEAT tabs show verified *planning purpose* and source passage IDs, never a fabricated finished BEAT.
- Source badges: native PPF saved, native PPF locked, visual approved/pending; Studio current live review status distinct and unavailable until actually read.
- `Review with Elara` opens a new conversation turn with exact source identity/shot number for fresh read-only inspection. `Load film` is its own separate explicitly authorized user action and triggers a guarded project switch only then.
- No image generation, provider charge, approvals, navigation side effects or change to six-track cut from this path.

## Acceptance gates

A. Plugin skill and source parser installed/tested; B. verified PPF read-only 25-shot snapshot; C. user-tested in-chat navigation; D. actual original WebP images supplied and independently displayed; E. Studio BEAT and reviews read after explicitly loading film; F. creator-triggered Save/Lock readback; G. complete six-track editor parity. Mark each separately; do not claim (D–G) simply because (A–C) passed.
