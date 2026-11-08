# Project-backed storyboard review

Use scripts/storyboard-review.py --project PATH --project-id ID --revision N
--sha256 HASH --block B --mini M. It returns all 25 positions from the bundled
canonical reader and joins recorded image-to-passage mappings, exact retained text,
prompt provenance, visual approval, pending replacements and available file checks.
Read-only: it never generates, approves, saves, locks, retires or revises anything.

Keep four facts separate: native Save/Lock records; user visual review; portable file
hash/decoding; semantic image-to-script consistency. A stored asset URL is not a
file check. Mini-Block evidence is not an exact per-shot mapping. Unmapped, missing,
changed, invalid and verified files must have distinct visible states. A matching
hash with no decoder is hash-only verification, not a decoded image. A reconstructed
prompt must not be labelled captured. Display conflicting addresses or missing
passages rather than silently assigning another image or source passage.

An interface may consume this view data for shot selection, source, prompts and
review status. This script does not provide hosted UI, authentication or durable
button actions. A preview must say so. Do not describe a clicked preview control as
a saved project change. Genuine changes still use the pinned image/source operation
scripts followed by an explicit successful file-service write and reopen check.

The intended primary workspace is a ChatGPT Project. GitHub integration is deferred.
Current project state must be read from saved files, not inferred from chat memory.
Do not embed a user's screenplay, IDs or images into the distributed plugin package.
For live UI persistence, first verify authorized host/file-service access and its
supported write path; do not deploy a service with copied private source data as a
substitute for an authenticated connection to the current project.
