# Image additions, replacements, removals and moves

Use scripts/image-operations.py for explicit artwork edits. Keep read-only requests
read-only. Do not silently treat a new image as a replacement, or an image removal
as deletion of the story beat. Infer a clear instruction from context; ask only when
the operation or target is materially ambiguous. A matching filename is not proof.

All commands take --project, --project-id, --revision, --sha256, --file and --out.
The JSON file contains id (unique event ID), project (exact identity result), kind,
reason, authorization (the user's instruction or delegated authority) and the fields
below. Output is a new atomic local snapshot; confirm durable saving separately.

| kind | Required fields | Active count |
| --- | --- | --- |
| add | address, passageIds, image | +1 |
| begin-replacement | artifactId | unchanged; old reference stays visible |
| complete-replacement | artifactId, pendingId, image | unchanged |
| cancel-replacement | artifactId, pendingId | unchanged; reference stays |
| remove | artifactId | -1; source beat retained, coverage review recorded |
| move | artifactId, address | unchanged; Save/Lock cleared for changed address |

address contains actNumber, sequenceNumber, blockNumber, miniBlockNumber and
shotNumber, exactly consistent with the canonical map. An occupied target blocks
the operation. More images are allowed; plan free positions or expand coverage
across Mini-Blocks explicitly rather than silently replacing or dropping images.
The canonical scaffold does not determine the short's duration or image count.

image contains path, sha256 (input bytes), label, prompt and promptOrigin
(captured or reconstructed). Capture generation prompts before invoking generation.
Bytes must decode as PNG/JPEG/WebP; output is a verified portable WebP. Record both
input and output hashes. A new image remains a draft pending user visual review;
neither generation nor review implies native application Save or Lock.

begin-replacement verifies the reference file and records a pending operation with
the source fingerprint and current address. complete-replacement rejects stale
source/address and verifies the new bytes before committing a snapshot that retires
the reference and inserts the replacement at the same position with the same source
passages. A failed generation/import leaves the prior snapshot usable and visible.
The old image is audit history after successful completion, omitted from the current
storyboard viewer. The new image has no inherited Save/Lock.

For a known prior mistaken removal only, begin-replacement may include explicit
restoreReference:true and address. This records referenceRestorations:1, separate
from replacement arithmetic. Require user authority for that repair, verify the
reference bytes, and explain the +1 as restoration, not replacement growth.

Events and pending work are retained in assetRegistry.extensions.imageChanges.
Report activeBefore, activeAfter, activeDelta, referenceRestorations, pending state,
affected artifacts and source coverage. Read the ledger and canonical reader without
rewriting for inspection. Verify portable bytes using story-workflow.py resume;
its file count includes historical media, so also report active artwork separately.
File verification proves byte identity/decoding, not perfect semantic continuity.

Before resuming elsewhere, save the current project export together with its assets,
source evidence, mapping and ledger in one portable ZIP, then reopen and verify pins
and hashes. Conversation memory or a generated thumbnail alone cannot restore files.
