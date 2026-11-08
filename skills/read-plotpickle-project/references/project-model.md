# Truth, mathematics and learning commands

Use Python 3 and the bundled Node bridge. No model, network or provider calls are
made by these scripts. Author the creative assessment using the host model and
actual source; the validator cannot supply or prove that reasoning.

Every command pins the current snapshot using the reader's exact identity:

    --project FILE --project-id ID --revision REV --sha256 HASH

Run identity first. The file/revision arguments change after each write. Writer
commands require --file PAYLOAD.json and --out NEW_DIRECTORY; inspect is read-only.
Save a current snapshot through the host's durable file service separately, preserving
an existing file identity for a replacement. Never put user records into this plugin.
The ledger lives in assetRegistry.extensions.projectModel.

## Assess a story without changing its script

    python3 scripts/project-model.py assess <identity-args> --file assessment.json --out assessed

The payload has:

    {
      "project": {"id":"...","title":"...","revision":0,"sha256":"..."},
      "scopePassageIds": ["screenplay-1","screenplay-2"],
      "storySummary": {
        "beginning":{"text":"...","passageIds":["screenplay-1"]},
        "middle":{"text":"...","passageIds":["screenplay-2"]},
        "ending":{"text":"...","passageIds":["screenplay-2"]}
      },
      "truths": [], "findings": [], "proposals": []
    }

scopePassageIds is optional; default is all retained screenplay passages. Scope an
assessment explicitly when an old export includes unrelated imported notes. Optional
supportingSource records fileName, sha256 and comparisonNote for a source independently
inspected by the host. It is corroboration, not permission to invent or rewrite text.

Truth records require id, category, scope, origin, text, passageIds and reason.

Category     Origin              Meaning
known        supplied-source     Direct source observation, not automatic world certainty
inferred     interpretation      Reasoned reading, with source evidence
unknown      unresolved          Open question without an invented answer
proposed     synthetic           Suggested new story fact, not yet canon
adopted      retained origin     Created only through an adoption event

Use scope source-observation, story-world, character-belief, editorial-judgment or
production. Known records are restricted to source-observation or production with
cited evidence; they cannot certify a disputed character claim as world truth.
An adopted synthetic record retains originalCategory=proposed and origin=synthetic.
The command never asserts independentlyVerified=true.

Example:

    {"id":"parent-message","category":"known","scope":"source-observation",
     "origin":"supplied-source","text":"A parent says the child should return.",
     "passageIds":["screenplay-2"],"reason":"Direct observation of this dialogue."}

Optional relations are objects with kind (supports, contradicts, depends-on), truthId
and reason. Referenced IDs must exist in the ledger/batch. Conflicting records remain
visible; the script does not search natural language for every possible contradiction.

Findings require id, classification, claim, reason and passageIds. Classification is
supported, deliberate-ambiguity, candidate-gap or opportunity. Deliberate ambiguity is
an editorial reading unless the author explicitly establishes intention. Do not treat
every unanswered question as missing material or promise a mathematically perfect story.

Each proposal requires id, title, diagnosis, rationale, findingId, passageIds, truthIds,
recommendation, learning and impacts. Evidence must be inside the assessment scope.
learning requires principle, explanation and studentQuestion. impacts is a nonempty
list of area/reason objects identifying consequences for script, continuity, shots,
assets or runtime. recommendation is insert or retain.

For an optional insertion:

    "change": {
      "afterPassageId":"screenplay-2","blockNumber":1,"miniBlockNumber":1,
      "passages":[{"type":"action","text":"The courier pauses before knocking."}]
    }

Passage types are transition, scene-heading, action, character, dialogue,
parenthetical or note. Text is limited to 780 characters per proposed passage.
Use multiple passages for longer additions. A retain recommendation has no change
object: it records why preserving an existing ambiguity or compression can help.

Assess stores the summary, findings, truth records and proposals. It preserves script,
artwork and existing approvals. It reports editorial review, not semantic proof.

## Adopt or reject explicitly

    python3 scripts/project-model.py adopt-proposal <identity-args> --proposal ID --file decision.json --out adopted
    python3 scripts/project-model.py reject-proposal <identity-args> --proposal ID --file decision.json --out rejected

The decision payload contains the exact current project identity, authority and
reason. Only perform adoption when the user explicitly asks or has delegated that
creative decision. A string in the payload is not independent authentication.

Adoption rejects proposals when the underlying source fingerprint has changed.
Insertion preserves original passages/IDs, adds unique synthetic-PROPOSAL-N IDs,
records the decision, retains provenance and flags source allocation, continuity,
shot plans, images and runtime for review. It does not regenerate images, reset or
fabricate Save/Lock receipts. Existing approvals still describe earlier media;
reviewRequired makes the source change visible before downstream production.
Synthetic scene-heading insertions inherit the anchor's scene metadata in this
prototype; a full scene renumbering/migration is a separate editing operation.

Rejecting changes only the proposal/decision records. Accepted inference, ambiguity,
and source facts must not be silently promoted into certainty. Revisions or rewritten
existing passages are separate workflows; the insertion command does not implement
arbitrary rewriting. Original source archives remain original after adoption.

## Plan physical runtime independently of the canonical map

    python3 scripts/project-model.py runtime-plan <identity-args> --file runtime.json --out timed

Example payload:

    {
      "project":{"id":"...","title":"...","revision":0,"sha256":"..."},
      "intendedFormat":"short", "targetRuntimeSeconds":null, "framesPerSecond":24,
      "physicalShots":[
        {"id":"physical-1","durationSeconds":2.5,
         "slotRefs":[{"actNumber":1,"sequenceNumber":1,"blockNumber":1,
                      "miniBlockNumber":1,"shotNumber":1}],
         "coverageReason":"The opening view covers this dramatic position."}
      ]
    }

Formats are short, feature, episode, other or undecided. Leave targetRuntimeSeconds
null when unspecified. A supplied target requires targetBasis describing its origin.
Never infer the film's duration from page/asset count or impose the baseline two hours.

Physical shots require unique IDs, positive durations, nonempty valid slotRefs and a
coverageReason. One physical shot can refer to several planning positions when the
editorial proposal explains that compression. A planning position cannot be assigned
to multiple physical shots in this representation. Use a separate alternative plan
for alternate coverage, rather than double-counting final runtime.

The canonical framework remains 4 Acts / 12 Sequences / 24 Blocks / 96 Mini-Blocks /
25 shot positions per Mini-Block. A 3-second-per-position feature baseline is not a
requirement to render 2,400 shots for every story. Compute physical shot count, summed
durations, difference from the supplied target, represented slots and missing slots.
Neither slot assignments nor a full grid prove that the story is dramatically complete.

Integer planning frame rates from 1–120 are supported. Decimal seconds are summed
without binary floating-point accumulation. Fractional frame totals are exposed with
an explicit nearest-frame count; no actual render duration is certified. Fractional
rates such as 23.976 require a future rational-rate extension, not silent rounding.
Prior runtime plans remain in history. Source changes flag the stored plan as stale.

## Record learning and inspect recovery

    python3 scripts/project-model.py record-feedback <identity-args> --file feedback.json --out learned

The payload has project, proposalId, reportedBy (user or agent), observation,
evidence, lesson and nextExperiment. Distinguish reported review from independently
verified outcomes. Retain both the lesson and what to test next. This is persistent
project feedback; no model weights are trained and improvement is not assumed.

    python3 scripts/project-model.py inspect <identity-args>

Inspect recovers truth categories, declared contradictions, assessments, proposals,
decisions, learning and runtime calculations from the pinned file in a new process.
It reports runtimePlanMatchesCurrentSource separately from measured runtime. Use the
original reader for actual image candidate/Save/Lock state and story-workflow resume
for available image hashes. A fresh process is not proof of a fresh ChatGPT chat.
