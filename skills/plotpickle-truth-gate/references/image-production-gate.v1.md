# PlotPickle Image Production Packet v1 — user-scoped data contract

This file is an **empty reusable schema guide**, not a template containing private film data. A host builds a fresh record from the actual authenticated source and approval ledger.

## Preflight packet (`plotpickle.image-production-context.v1`)

```
{
  "schema":"plotpickle.image-production-context.v1",
  "projectId":"<current saved project ID>",
  "sourceTitle":"<actual authorized screenplay title>",
  "sourceFormat":"FDX",
  "sourceRevision":1,
  "sourceFile":"source/actual-script.fdx",
  "sourceSha256":"<64 lowercase hex of those source bytes>",
  "passages":[{"id":"source-passage-1","scene":"INT. VEHICLE - DAY","text":"<verbatim scene/action passage>"}],
  "approvedReferences":[{"id":"character-approved-v1","role":"character","approval":"CREATOR_APPROVED","path":"references/character.png","sha256":"<64 hex>"}],
  "continuityAnchor":{"type":"PREVIOUS_SHOT","shotId":"B01-M01-S01","path":"approved/previous.png","sha256":"<64 hex>"},
  "continuation":{"block":1,"miniBlock":1,"shot":2},
  "shots":[{
    "productionAddress":{"block":1,"miniBlock":1,"shot":2},
    "scriptPassageIds":["source-passage-1"],
    "scene":"INT. VEHICLE - DAY",
    "subjects":["script-backed character"],
    "action":"<visible action from this screenplay passage>",
    "camera":"<single frame and lens/axis>",
    "mustShow":["<essential image evidence>"],
    "mustNotShow":["<continuity contradictions>"],
    "referenceIds":["character-approved-v1"],
    "imagePrompt":"One uninterrupted cinematic 16:9 frame depicting ONLY the exact shot action."
  }]
}
```

For the first genuine shot, `continuityAnchor` may instead be `{"type":"NONE_FIRST_SHOT","reason":"No previous shot exists in the authorized project"}`. `sourceBlockNumber`/`sourceMiniBlockNumber` may be added separately as annotations but never replace `productionAddress`. At preflight verify actual screenplay bytes; `sourceSha256` on its own proves nothing. User-owned material is never committed to the plugin release ZIP.

**The script cannot verify narrative semantics or that the image model was actually given the references.** The host must attach the original reference *image bytes* for each generated frame and retain provider/host attachment receipts where supported. Otherwise report the check as unverified rather than falsely passing a live model-reference gate. Automated prompt scanning is a guardrail against obvious multi-panel requests, not a substitute for visual inspection.

## Postflight packet (`plotpickle.image-production-review.v1`)

Contains `schema`, exact `packetSha256`, `projectId`, `sourceSha256` and `shots[]`, one per intended `productionAddress`. For each entry: `image:{path,sha256,bytes?}`, `semanticState` PASS/DRIFTED/REVIEW_REQUIRED/UNKNOWN, `visualInspectionPerformed` (real visual check), `inspector`, `reason` where drifted, `referenceImagesProvidedToModel` (host must verify rather than assume), and separately recorded `creatorApproved`, `nativePpfSavedReadback`, `nativePpfLockedReadback`, `libraryMediaReadback`, `usableForProduction`. **Self-asserted true values do not establish PPF writeback; offline script always returns `productionReady:false`.** A source-pinned native reader Save→Lock proof and independent readback belong to the existing approval writer.

## Output states

`preflight.gate = BLOCKED`: do not generate or spend credits. `preflight.gate = PASS`: mechanical source/byte/shot validation passed; still need actual host image-reference delivery. `postflight.gate = PASS` and candidateInspectable: an image may be presented for human review; it is not PPF-locked. `DRIFTED` means preserve the original and mark only a review derivative. Never use a rendered montage, even a visually attractive one, as five independent shots.
