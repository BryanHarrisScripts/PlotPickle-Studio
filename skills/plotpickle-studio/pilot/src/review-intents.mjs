// Source-guarded review intent contract. Pure preparation only; NO saved PPF writes,
// no media generation, no provider spend and no native lock state mutation.
// An authorized host must execute a separate write adapter, CAS-commit it, then
// independently reread the native project and bytes before reporting success.
const HASH=/^[a-f0-9]{64}$/;
const ACTIONS=new Set(['approve','regenerate','lock','unlock']);
export class ReviewBlocked extends Error {
  constructor(code) {super(code);this.name='ReviewBlocked';this.code=code;}
}
const stop=code=>{throw new ReviewBlocked(code);};
const positive=n=>Number.isInteger(n)&&n>0;
function addressKey(a) {
  if(!a || !positive(a.block) || a.block>24 ||
    !positive(a.mini) || a.mini>4 || !positive(a.shot) || a.shot>25) stop('INVALID_SHOT_ADDRESS');
  return [a.block,a.mini,a.shot].join(':');
}
export function prepareReviewIntent({projection,request}) {
  if(!projection || projection.readonly!==true || !projection.source ||
    !Array.isArray(projection.shots)) stop('NATIVE_PROJECTION_REQUIRED');
  if(!request || !ACTIONS.has(request.action)) stop('UNKNOWN_ACTION');
  const source=projection.source;
  if(typeof source.projectId!=='string' || !source.projectId ||
    !Number.isInteger(source.revision) || source.revision<0 ||
    !HASH.test(source.sha256||'') ||
    source.provenance==='SYNTHETIC DEMO') stop('VERIFIED_PROJECT_IDENTITY_REQUIRED');
  if(request.projectId!==source.projectId ||
     request.revision!==source.revision ||
     request.sha256!==source.sha256) stop('STALE_SOURCE_PIN');
  if(typeof request.actionId!=='string' ||
     !/^[a-zA-Z0-9][a-zA-Z0-9._:-]{7,127}$/.test(request.actionId)) stop('INVALID_IDEMPOTENCY_KEY');
  const key=addressKey(request.address);
  const rows=projection.shots.filter(s=>s?.address && addressKey(s.address)===key);
  if(rows.length!==1) stop(rows.length?'AMBIGUOUS_SHOT':'SHOT_NOT_AUTHORED');
  const shot=rows[0];
  const candidates=Array.isArray(shot.candidateRecords)?shot.candidateRecords:[];
  const matching=candidates.filter(c=>c.artifactId===request.artifactId && typeof request.artifactId==='string'&&request.artifactId);
  if(matching.length!==1) stop(matching.length?'AMBIGUOUS_CANDIDATE':'EXACT_IMAGE_CANDIDATE_REQUIRED');
  const candidate=matching[0];
  if(!HASH.test(request.imageSha256||'') || candidate.recordedHash!==request.imageSha256)
    stop('IMAGE_HASH_NOT_PINNED');
  if(!Array.isArray(shot.sourcePassageIds)||!shot.sourcePassageIds.length) stop('SOURCE_PASSAGE_MISSING');
  const reason=typeof request.reason==='string'?request.reason.trim():'';
  if(reason.length>400) stop('REASON_TOO_LONG');
  const mediaOk=candidate.mediaBytesVerifiedThisSession===true &&
    candidate.verifiedSha256===candidate.recordedHash &&
    candidate.mediaDecoded===true;
  if((request.action==='approve' || request.action==='lock') && !mediaOk) stop('MEDIA_NOT_INDEPENDENTLY_VERIFIED');
  if(request.action==='unlock') {
    if(!candidate.locked || !candidate.savedMarkerPresent) stop('NOT_SAVED_AND_LOCKED');
    if(reason.length<3) stop('UNLOCK_REASON_REQUIRED');
  }
  if(request.action==='lock') {
    if(!candidate.savedMarkerPresent) stop('SAVE_BEFORE_LOCK_REQUIRED');
    if(candidate.locked) stop('ALREADY_LOCKED');
    if(request.humanApproved!==true) stop('HUMAN_APPROVAL_REQUIRED');
  }
  if(request.action==='regenerate') {
    if(candidate.locked) stop('UNLOCK_BEFORE_REGENERATE');
    if(reason.length<3) stop('REGENERATION_REASON_REQUIRED');
  }
  if(request.action==='approve' && request.humanApproved!==true) stop('EXPLICIT_HUMAN_APPROVAL_REQUIRED');
  return Object.freeze({
    schema:'plotpickle.review-intent.v1', status:'PREPARED_NOT_COMMITTED', action:request.action,
    actionId:request.actionId,
    expected:{projectId:source.projectId,revision:source.revision,rawSha256:source.sha256,
      address:request.address,artifactId:request.artifactId,imageSha256:request.imageSha256},
    sourcePassageIds:[...shot.sourcePassageIds],
    reason:reason||null,
    nextStage:request.action==='regenerate'?'PREPARE_UNPAID_REPLACEMENT':
       request.action==='approve'?'HUMAN_VISUAL_REVIEW_WRITE':
       request.action==='unlock'?'SOURCE_GUARDED_UNLOCK':'SOURCE_GUARDED_RELOCK',
    saved:false, locked:false, providerInvoked:false, hostPersistenceVerified:false,
    needsHostWriteAndNativeReadback:true
  });
}
