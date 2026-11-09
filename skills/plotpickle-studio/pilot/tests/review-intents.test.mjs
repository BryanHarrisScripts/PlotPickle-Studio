import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareReviewIntent,ReviewBlocked} from '../src/review-intents.mjs';
const hash='a'.repeat(64),imageHash='b'.repeat(64),address={block:1,mini:1,shot:10};
const fresh=()=>({
  readonly:true,
  source:{projectId:'private-project',revision:11,sha256:hash,provenance:'native-reader-backed PPF'},
  shots:[{address:{...address},sourcePassageIds:['screenplay-30','screenplay-31'],
    candidateRecords:[{artifactId:'candidate-10',recordedHash:imageHash,
      verifiedSha256:imageHash,mediaBytesVerifiedThisSession:true,mediaDecoded:true,
      savedMarkerPresent:true,locked:false}]}]
});
const request=(action='approve')=>({action,actionId:'review-unique-001',projectId:'private-project',
  revision:11,sha256:hash,address:{...address},artifactId:'candidate-10',
  imageSha256:imageHash,reason:'Please revise shot',humanApproved:true});
const blocked=(code,modify)=>{const p=fresh(),r=request();modify(p,r);
  assert.throws(()=>prepareReviewIntent({projection:p,request:r}),e=>e instanceof ReviewBlocked && e.code===code);};
test('explicit visual approval produces intent only, never a commit',()=>{
  const x=prepareReviewIntent({projection:fresh(),request:request()});
  assert.equal(x.status,'PREPARED_NOT_COMMITTED');
  assert.equal(x.hostPersistenceVerified,false);
  assert.equal(x.saved,false);
  assert.equal(x.locked,false);
  assert.equal(x.providerInvoked,false);
  assert.deepEqual(x.sourcePassageIds,['screenplay-30','screenplay-31']);
});
test('regeneration only proposes a job, never spends',()=>{
  let p=fresh(); p.shots[0].candidateRecords[0].mediaBytesVerifiedThisSession=false;
  const result=prepareReviewIntent({projection:p,request:request('regenerate')});
  assert.equal(result.nextStage,'PREPARE_UNPAID_REPLACEMENT');
  assert.equal(result.providerInvoked,false);
});
test('unlock requires reason and a previously saved/locked candidate',()=>{
  let p=fresh();p.shots[0].candidateRecords[0].locked=true;
  let r=request('unlock');r.reason='';
  assert.throws(()=>prepareReviewIntent({projection:p,request:r}),/UNLOCK_REASON_REQUIRED/);
  r.reason='Improve composition';
  assert.equal(prepareReviewIntent({projection:p,request:r}).nextStage,'SOURCE_GUARDED_UNLOCK');
});
test('lock requires Save to precede Lock',()=>blocked('SAVE_BEFORE_LOCK_REQUIRED',(p,r)=>{
  p.shots[0].candidateRecords[0].savedMarkerPresent=false;r.action='lock';
}));
test('lock requires user approval',()=>blocked('HUMAN_APPROVAL_REQUIRED',(p,r)=>{
  r.action='lock';r.humanApproved=false;
}));
test('locked image cannot be regenerated without unlock',()=>blocked('UNLOCK_BEFORE_REGENERATE',(p,r)=>{
  p.shots[0].candidateRecords[0].locked=true;r.action='regenerate';
}));
test('stale PPF revision blocked',()=>blocked('STALE_SOURCE_PIN',(p,r)=>{r.revision=10;}));
test('stale PPF hash blocked',()=>blocked('STALE_SOURCE_PIN',(p,r)=>{r.sha256='c'.repeat(64);}));
test('wrong project blocked',()=>blocked('STALE_SOURCE_PIN',(p,r)=>{r.projectId='other-project';}));
test('tampered image hash blocked',()=>blocked('IMAGE_HASH_NOT_PINNED',(p,r)=>{r.imageSha256='c'.repeat(64);}));
test('missing verified media blocks approval',()=>blocked('MEDIA_NOT_INDEPENDENTLY_VERIFIED',(p,r)=>{
  p.shots[0].candidateRecords[0].mediaBytesVerifiedThisSession=false;
}));
test('hash-only verification blocks approval',()=>blocked('MEDIA_NOT_INDEPENDENTLY_VERIFIED',(p,r)=>{
  p.shots[0].candidateRecords[0].mediaDecoded=false;
}));
test('candidate must be exact',()=>blocked('EXACT_IMAGE_CANDIDATE_REQUIRED',(p,r)=>{
  r.artifactId='another-candidate';
}));
test('ambiguous candidate blocked',()=>blocked('AMBIGUOUS_CANDIDATE',(p,r)=>{
  p.shots[0].candidateRecords.push({...p.shots[0].candidateRecords[0]});
}));
test('invalid address blocked',()=>blocked('INVALID_SHOT_ADDRESS',(p,r)=>{r.address.shot=26;}));
test('missing passage blocked',()=>blocked('SOURCE_PASSAGE_MISSING',(p,r)=>{
  p.shots[0].sourcePassageIds=[];
}));
test('no authored shot blocked',()=>blocked('SHOT_NOT_AUTHORED',(p,r)=>{r.address.shot=9;}));
test('synthetic sources never accept review controls',()=>blocked('VERIFIED_PROJECT_IDENTITY_REQUIRED',(p,r)=>{p.source.provenance='SYNTHETIC DEMO';}));
test('no idempotency key blocked',()=>blocked('INVALID_IDEMPOTENCY_KEY',(p,r)=>{r.actionId='x';}));
test('no approval assertion blocked',()=>blocked('EXPLICIT_HUMAN_APPROVAL_REQUIRED',(p,r)=>{r.humanApproved=false;}));
