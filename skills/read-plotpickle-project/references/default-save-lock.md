# Initial storyboard images: Save first, Lock by default (v0.8.25)

The portable native PPF workflow keeps `visualArtifacts` IDs, `sourceDecisionKeys` marker `storyboard-local-save:v1`, `reviewState=accepted`, and `build.foundations.acceptedVisualArtifactIds`. Historical `packageBytesVerified` is not sufficient; SHA-256 of the actual portable file plus image decoding must be checked at each Save/Lock step. This is a project-file workflow, not a claim about a running Windows app.

Initial image → verify actual source-bound bytes → SAVE new source snapshot → independently reopen and inspect Save marker → LOCK new snapshot → independently reopen and verify artifact, accepted/locked record and real bytes. An initial auto-accepted image means default production acceptance, not separate final human creative approval. Authors can `unlock` exceptions for revision without revoking unrelated images. A new replacement for the unlocked address is verified, saved and locked as a new candidate; the old asset isn't silently revived. `relock` requires a true prior Save and current verified bytes. Any missing/corrupt asset, ambiguous mapping, stale project or unsafe path blocks the transition.

Commands use exact canonical `--project FILE --project-id ID --revision N --sha256 HASH` and produce new, non-overwriting output directories containing a project snapshot and assets:

    python3 scripts/default-save-lock.py attach-initial --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1 --shot 1 --image first.png --provider 'actual-provider' --out first-locked
    python3 scripts/default-save-lock.py auto --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1 --out mini-locked
    python3 scripts/default-save-lock.py audit --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1
    python3 scripts/default-save-lock.py unlock --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1 --shot 8 --reason 'Replace the expression' --out revision-needed
    python3 scripts/default-save-lock.py replace-unlocked --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1 --shot 8 --image corrected.png --provider 'actual-provider' --out corrected-locked
    python3 scripts/default-save-lock.py relock --project story.ppf.json --project-id ID --revision N --sha256 HASH --block 1 --mini 1 --shot 8 --out revised-locked

`readyForMotionOrPrevis=true` means scoped planned positions have verified saved-and-locked images without unresolved unlocks, not that all 25 reserved positions are authored or that any video has been generated. For fal motion follow `../plotpickle-fal-production/SKILL.md`; for 24fps still draft assembly use `../plotpickle-animatic/SKILL.md`. Run `python3 scripts/test-default-save-lock.py` and `python3 ../plotpickle-fal-production/scripts/test-fal-handoff.py` in their corresponding skill directories. Only report durable saved state after independently re-opening an actual user project and verifying real media.
