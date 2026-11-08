# Workflow commands and contracts

Resolve paths relative to this skill. Run `python3 scripts/story-workflow.py --help`
for commands. No network calls, server, provider keys or dependency installation.
All writer output directories must be new. Persist the completed snapshot using
the user's file service; do not expose internal command details unless useful.

## Inputs and identity

Run `node scripts/inspect-project.mjs --file FILE --operation identity` first for
an existing project. Every existing-project command takes:

    --project FILE --project-id ID --revision REV --sha256 HASH

Use exactly the identity returned by the reader, including the file fingerprint.
Each output snapshot contains project.ppf.json and resume.json. Writer commands
increment existing revisions; a new project starts at revision 0. Never reuse stale
identity arguments after a write. Output directories contain only new snapshots;
there is no automatic backup copy of the original project.

## Import a screenplay

    python3 scripts/story-workflow.py import-fdx --file story.fdx --title "Story" --out new-project

Read only FinalDraft/Content screenplay paragraphs (including dual dialogue), join
formatting spans, retain full original paragraph text, and split normalized text
into <=780-character segments below the canonical limit. Preserve the original
FDX as source.fdx. Full text and the original-to-retained passage map also live in
assetRegistry.extensions.storyWorkflow. No user data is placed in the plugin.

Automatic chronological word-share placement is a labelled provisional allocation,
not dramatic analysis. Review it before planning shots. Empty Mini-Blocks stay empty.

## Start from an idea

    python3 scripts/story-workflow.py idea --file premise.txt --title "Story" --out idea-project

This stores a premise and the canonical scaffold, with no invented screenplay.
Develop the script with the host writing model when requested, retain assumptions
as proposals, then write a valid FDX draft. To import it into the same idea project,
use import-fdx with the pinned idea-project identity arguments as well as --file,
--title and --out. This retains the idea, adds draft screenplay evidence and increments
the revision. It rejects replacing an already imported screenplay implicitly.

## Propose dramatic placement

Write a mapping JSON using the current identity:

    {"project":{"id":"...","title":"...","revision":0,"sha256":"..."},
     "assignments":[{"passageId":"screenplay-1","blockNumber":1,
                     "miniBlockNumber":1,"reason":"Opening setting and action."}]}

Cover every retained passage exactly once. Preserve its text and ID. Every address
must fit 24 Blocks and 4 Mini-Blocks. Specify a reason for every assignment.

    python3 scripts/story-workflow.py map <identity-args> --mapping map.json --out mapped-project

This stores an editorial proposal; it does not certify story truth. It rejects
remapping when media or shot prompts exist, because those require explicit migration.

## Prepare and author one Mini-Block

    python3 scripts/story-workflow.py prepare-mini <identity-args> --block 1 --mini 1 --out packet.json

The packet includes the actual Mini-Block source and 25 initially GAP positions.
Author the JSON as an editorial proposal, retaining its project identity/address.
Add allocationReview explaining the chosen scope. Add continuity truths such as:

    {"id":"character-age","origin":"source","text":"The protagonist is ten.",
     "passageIds":["screenplay-3"]}

Use origin `visual-proposal` for details not established by the script. Truths may
cite any passage in the current project; shot evidence stays inside its Mini-Block.
Reuse known truth IDs exactly; changing one requires a separate continuity revision.

Each planned slot requires:

    {"shotNumber":1,"state":"PLANNED","passageIds":["screenplay-4"],
     "coverageType":"story-beat","narrativePurpose":"Establish the pursuit.",
     "composition":"Wide view showing both characters running toward the trees.",
     "truthIds":["character-age"],"prompt":"One cinematic landscape storyboard frame ..."}

coverageType can also be `alternative-view` or `detail`. Make composition/prompt
specific and distinct, and explicitly preserve relevant identities, setting, props,
wardrobe, lighting and screen direction. Avoid text, logos and watermarks unless
requested. Propose synthetic story additions through project-model.py before adopting them as
source for shots. Keep invented appearance labelled as a visual proposal.

Unsupported slots remain:

    {"shotNumber":25,"state":"GAP","passageIds":[],"reason":"No supported shot design yet."}

    python3 scripts/story-workflow.py plan-mini <identity-args> --plan packet.json --out planned-project

This requires exactly 25 unique positions, checks IDs/address and distinct prompts,
stores semantic claims as unverified editorial proposals, and persists each planned
prompt in canonical production.storyboardImagePrompts. It does not silently replace
an existing Mini-Block plan or prompts. Schema validation cannot prove that a prompt
follows from its cited text; read the passages and review that reasoning yourself.

## Generate or supply an image

When requested, call the host image tool with the stored prompt and accessible
continuity references. No image provider is bundled. If the result has no usable
local bytes, do not fabricate a path or claim registration. Use the host's supported
file retrieval, or report that registration is pending.

    python3 scripts/story-workflow.py attach-image <identity-args> --block 1 --mini 1 --shot 1 --image output.png --provider "actual source" --out with-image

Optional --model records an actual model if known. `--replace` explicitly replaces
that shot's existing candidates and their accepted-ID linkage. Other shots are
preserved; replacing all previous artwork requires an explicit batch workflow.
Never inherit an old image's Lock. The image is decoded, converted to WebP, named
using its address/hash, registered as a draft candidate and mapped to passage IDs.
Portable assets from the input project directory are carried forward when present;
missing files are reported in resume.json. Package-relative image files are not
installed into a live application by this command.

Every assignment lives in assetRegistry.extensions.storyWorkflow.imageMappings.
Every plan and continuity ledger lives beside it in the same project. Include the
current project and assets when saving/delivering. For supplied artwork batches,
inspect actual bytes and source/generation context before authoring assignments;
never treat artwork index 026 as a canonical slot by arithmetic alone.

## Resume and verify

    python3 scripts/story-workflow.py resume <identity-args>

This reopens the pinned snapshot in a new process and verifies available mapped
image hashes. It also understands the artworkMapping ledger from the earlier ZIP
mapping workflow. It reports absent or changed bytes and does not fetch remote URLs.

Use inspect-project.mjs for read-only summary/source/shot status; its existing
Save/Lock rules are unchanged. Store an updated export via the user's durable file
service, preserving the existing file identity when replacing. A successful local
command isn't proof of a durable save, live application update, or a fresh host chat.

Version 0.3: use project-model.py for assessments, synthetic proposals and explicit
adoption. Read project-model.md for contracts. Keep canonical baseline timing distinct
from an actual short/feature production plan. A planned position may supply its own
positive durationTargetSeconds; default 3 is a baseline, never a runtime measurement.
The snapshot receipt now names canonicalBaselineShotSeconds and
canonicalBaselineMiniBlockSeconds and carries a separate projectRuntimePlan.
