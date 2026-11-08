# Carry an author-directed change through a project

Run `python3 scripts/apply-story-change.py` only after the user directs/adopts the
story changes. This operation is distinct from generating or approving an image.
Pin the current project ID, revision and SHA-256 using the original reader.

    python3 scripts/apply-story-change.py --project FILE --project-id ID --revision REV --sha256 HASH --file change.json --out NEW_DIRECTORY

The input payload is an editorial plan authored from the user's actual request:

    {"project":{"id":"...","title":"...","revision":0,"sha256":"..."},
     "id":"author-change-1",
     "authorship":{"kind":"user","instruction":"Actual user direction.",
                   "authorization":"Actual adoption instruction or delegated authority."},
     "storyScopePassageIds":["screenplay-1"],
     "operations":[
       {"kind":"replace","passageId":"screenplay-1",
        "expectedText":"Exact current text.","text":"Authorized new text."},
       {"kind":"insert-after","afterPassageId":"screenplay-1",
        "passages":[{"id":"author-new-beat","type":"action","text":"New action."}]}
     ],
     "images":[], "supersedeArtifactIds":[], "reviewArtifactIds":[],
     "propContinuity":[], "learning":{}
    }

Retain the raw owner direction and distinguish it from the agent's wording and
placement decisions. The command records the claimed authority; it does not
independently authenticate a human. Never manufacture an approval event from an
unrelated acknowledgement. Insertion IDs begin author-, remain unique, and text
is limited to 780 characters per passage. Replacement keeps the original ID
and rejects a mismatching expectedText. The input project is never overwritten;
only a fully validated new output snapshot is installed. Durable replacement is
performed separately by the host file service with its version guard.

Optional fourActs contains four objects: actNumber (1–4), title, reason and
placements. Each placement has passageId, blockNumber and miniBlockNumber. Cover
every scoped story passage and new passage exactly once. Act numbers must agree
with the canonical block address. Historical retained notes outside the declared
scope are preserved and listed as excluded, rather than treated as story beats.
The four-Act plan is an explicit editorial plan, not a word-count proof.

Images require local path, sha256 of the input bytes, label, passageIds, prompt
and promptOrigin (captured or reconstructed). Before invoking native imagegen,
record its exact prompt and reference identities, then associate the output file
and hash immediately. If an older prompt can only be reconstructed, label that
fact. Do not mislabel an import description as the exact generation prompt.
The writer decodes and converts PNG/JPEG/WebP to lossless WebP and retains source
and output hashes. Image registration does not generate new images or call an API.

Map images by actual story evidence, not numeric filenames. Active images are
ordered within each Mini-Block by source order and stable existing artifact order,
and assigned at most 25 positions. Cross-Mini-Block evidence blocks the migration
until an explicit imagePassageOverrides entry provides passageIds and reason for
that artifact ID. primaryPassageOverrides can choose one already cited passage
as an ordering anchor when a broad source citation includes a time card or heading.
Review that editorial choice; the schema cannot prove it is narratively correct.

Superseding is explicit by artifact ID. It rejects conflicting candidates and
removes their accepted linkage. They remain in audit/media history, while the
current storyboard excludes them. Other possibly affected frames appear in
reviewRequired; do not treat that flag as proof of replacement or review completion.
Moved or source-changed image records do not inherit Save/Lock. Visual approval is
recorded separately from application Save, acceptance and Lock.

A four-Act remap archives the old shot plans/prompts in the change record and clears
their active projection so stale addresses cannot be used as if current. Rebuild
shot plans from revised source before further generation. Original source/media
state, operations, author direction, prop history and learning rationale remain
recorded in projectModel.storyChanges. Existing runtime/assessments are not silently
re-certified: source fingerprints and reviewRequired expose their stale state.

This prototype supports insertion/replacement, explicit structural migration,
source-to-image assignment and recovery. It does not perform automatic natural-
language contradiction detection, perfect character/prop matching, arbitrary scene
renumbering, live vault writes or application Save/Lock actions. New scene headings
currently inherit anchor scene metadata; treat full scene renumbering as a separate
editing operation. Inspect all outputs, package portable assets, and use resume and
project-model inspect in a new process before claiming recoverability. A new process
is not a new ChatGPT conversation.
