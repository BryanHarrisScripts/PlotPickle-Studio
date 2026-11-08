// PlotPickle Studio: read-only projection. The existing PPF remains authoritative.
// Only source-backed names and relationships are shown. No writes or provider calls.
import { createHash } from 'node:crypto';

const text = (value, max=700) => typeof value === 'string' ? value.replace(/[\u0000-\u001f]/g, ' ').trim().slice(0,max) : '';
const arr = value => Array.isArray(value) ? value : [];
const titleCase = value => text(value,200).toLowerCase().replace(/\b\w/g, x => x.toUpperCase());
const validId = id => typeof id === 'string' && id.length > 0 && id.length < 200;
const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
const knownStates = ['source-backed','proposed','recorded','unverified','not-authored'];

export function sha256(input) { return createHash('sha256').update(input).digest('hex'); }

export function projectStudio(ppf, sourceBytes, verifiedIdentity, { demo=false }={}) {
  if (!isObject(ppf)) throw Error('INVALID_PROJECT');
  if (!isObject(verifiedIdentity) || !validId(verifiedIdentity.id) || !Number.isInteger(verifiedIdentity.revision) || !/^[a-f0-9]{64}$/.test(verifiedIdentity.sha256 ?? '')) throw Error('NATIVE_IDENTITY_REQUIRED');
  if (sha256(sourceBytes) !== verifiedIdentity.sha256) throw Error('SOURCE_FINGERPRINT_MISMATCH');
  if (verifiedIdentity.id !== ppf.id || verifiedIdentity.revision !== ppf.revision) throw Error('IDENTITY_REVISION_MISMATCH');
  const screenplay = arr(ppf.sourceEvidence?.screenplay?.passages);
  const plans = arr(ppf.assetRegistry?.extensions?.storyWorkflow?.plans);
  const prompts = arr(ppf.production?.storyboardImagePrompts);
  const characterMap = new Map(), locationMap = new Map(), scenes = [], shots = [];
  const shotByAddress = new Map();
  const passageIds = new Set(screenplay.map(p=>p?.id).filter(validId));
  let scene = null, currentSceneIndex = -1;
  for (const passage of screenplay) {
    if (!isObject(passage) || !validId(passage.id)) continue;
    const type = text(passage.type,80), value=text(passage.text,1600);
    if (type === 'scene-heading') {
      currentSceneIndex++;
      const placeId = `place:${passage.id}`;
      const place = { id:placeId, name:value || 'Untitled scene heading', headingPassageId:passage.id, state:'source-backed', sceneIds:[] };
      locationMap.set(placeId,place);
      scene = { id:`scene:${passage.id}`, title:value || 'Untitled scene', headingPassageId:passage.id, placeId, passageIds:[], peopleIds:[], blockNumber:passage.blockNumber ?? null, miniBlockNumber:passage.miniBlockNumber ?? null, state:'source-backed' };
      scenes.push(scene); place.sceneIds.push(scene.id);
    }
    if (!scene) continue;
    scene.passageIds.push(passage.id);
    if (type === 'character' && value) {
      // Character cue is evidence of an appearance/cue, not of physical identity or visual approval.
      const key = value.toLocaleLowerCase();
      let person = characterMap.get(key);
      if (!person) {
        person = { id:`person:${passage.id}`, name:titleCase(value), cuePassageIds:[], sceneIds:[], state:'source-cue-only' };
        characterMap.set(key,person);
      }
      person.cuePassageIds.push(passage.id);
      if (!person.sceneIds.includes(scene.id)) person.sceneIds.push(scene.id);
      if (!scene.peopleIds.includes(person.id)) scene.peopleIds.push(person.id);
    }
  }
  // Only authored, traceable planned shots. Never produce all 2,400 empty cells as if made.
  for (const plan of plans) {
    const a=plan?.address;
    if (!a || !Number.isInteger(a.blockNumber) || !Number.isInteger(a.miniBlockNumber)) continue;
    for (const sp of arr(plan.shots)) {
      if (!Number.isInteger(sp?.shotNumber) || sp.shotNumber<1 || sp.shotNumber>25 || sp.state!=='PLANNED') continue;
      const sourceRefs=arr(sp.passageIds).filter(x=>passageIds.has(x));
      const anchor=`storyboard-anchor:block:block-${String(a.blockNumber).padStart(2,'0')}:mini-${a.miniBlockNumber}`;
      const exact=prompts.filter(p=>p?.anchorRef===anchor && p?.position===sp.shotNumber);
      const conflict=exact.length>1 || (exact.length===1 && text(exact[0].prompt,20000)!==text(sp.prompt,20000));
      const matchingScene = scenes.find(s=>sourceRefs.includes(s.headingPassageId) || sourceRefs.some(id=>s.passageIds.includes(id)));
      const row={id:`shot:${a.blockNumber}:${a.miniBlockNumber}:${sp.shotNumber}`, address:{block:a.blockNumber,mini:a.miniBlockNumber,shot:sp.shotNumber}, sceneId:matchingScene?.id??null, sourcePassageIds:sourceRefs, narrativePurpose:text(sp.narrativePurpose), composition:text(sp.composition), prompt:conflict?null:exact.length===1?text(exact[0].prompt,20000):null, promptStatus:conflict?'conflicting-records':exact.length===1?'recorded-exact':'not-authored', imageStatus:'bytes-not-verified', saveLockStatus:'not-verified', motionStatus:'not-verified', state:'authored-plan', candidateRecords:[]};
      shots.push(row);shotByAddress.set(`${a.blockNumber}:${a.miniBlockNumber}:${sp.shotNumber}`,row);
    }
  }
  // Existing PPF exports may have imported artwork mappings without authored shot plans.
  // Show those genuine mappings as records, not fabricated/planned shots or verified media.
  const mapped=[...arr(ppf.assetRegistry?.extensions?.artworkMapping?.entries).map(m=>({...m,recordKind:'artwork-mapping'})),...arr(ppf.assetRegistry?.extensions?.storyWorkflow?.imageMappings).map(m=>({...m,recordKind:'story-workflow-mapping'}))];
  for(const m of mapped){
    const a=m?.address;
    if(!a || !Number.isInteger(a.blockNumber) || !Number.isInteger(a.miniBlockNumber) || !Number.isInteger(a.shotNumber) || a.blockNumber<1 || a.blockNumber>24 || a.miniBlockNumber<1 || a.miniBlockNumber>4 || a.shotNumber<1 || a.shotNumber>25) continue;
    const key=`${a.blockNumber}:${a.miniBlockNumber}:${a.shotNumber}`;
    const recordedRefs=arr(m.passageIds).filter(validId), sourceRefs=recordedRefs.filter(id=>passageIds.has(id));
    const matchingScene=scenes.find(s=>sourceRefs.some(id=>s.passageIds.includes(id)));
    let shot=shotByAddress.get(key);
    if(!shot){shot={id:`shot:${key}`, address:{block:a.blockNumber,mini:a.miniBlockNumber,shot:a.shotNumber}, sceneId:matchingScene?.id??null, sourcePassageIds:sourceRefs, narrativePurpose:'',composition:'',prompt:null,promptStatus:'not-authored',imageStatus:'bytes-not-verified',saveLockStatus:'not-verified',motionStatus:'not-verified',state:'mapped-artwork',candidateRecords:[]};shots.push(shot);shotByAddress.set(key,shot);}
    if(!shot.sceneId && matchingScene)shot.sceneId=matchingScene.id;
    shot.sourcePassageIds=[...new Set([...shot.sourcePassageIds,...sourceRefs])];
    // The exact prompt may be unavailable or reconstructed; don't claim the original was recovered.
    const candidate={artifactId:text(m.artifactId,200)||null,recordKind:m.recordKind,mappingStatus:text(m.mappingStatus,100)||'recorded',filename:text(m.filename,500)||null,
      recordedHash:text(m.sha256,80)||null,promptOrigin:text(m.promptOrigin,120)||'unknown',
      savedMarkerPresent:m.savedMarkerPresent===true,locked:m.locked===true,
      packageBytesPreviouslyReported:m.packageMediaBytesVerified===true||m.packageBytesVerified===true,
      mediaBytesVerifiedThisSession:false,unresolvedPassageIds:recordedRefs.filter(id=>!passageIds.has(id))};
    if(!shot.candidateRecords.some(x=>x.artifactId && x.artifactId===candidate.artifactId&&x.recordKind===candidate.recordKind))shot.candidateRecords.push(candidate);
    shot.imageStatus=`${shot.candidateRecords.length} mapped record(s); bytes not verified this session`;
    shot.saveLockStatus='Recorded flags only; native Save/Lock not reverified';
    if(!shot.prompt && text(m.prompt,20000)){shot.prompt=text(m.prompt,20000);shot.promptStatus=candidate.promptOrigin==='unknown'?'recorded-provenance-unknown':`recorded-${candidate.promptOrigin}`;}
  }
  shots.sort((a,b)=>a.address.block-b.address.block||a.address.mini-b.address.mini||a.address.shot-b.address.shot);
  const source = { projectId:verifiedIdentity.id, revision:verifiedIdentity.revision, sha256:verifiedIdentity.sha256, title:text(ppf.title,300)||'Untitled project', provenance:demo?'SYNTHETIC DEMO':'native-reader-backed PPF', screenplayPassages:screenplay.length };
  // Explicit derived relation edges let a UI and an agent traverse the SAME source.
  // These are read-only views; an edge is never a new adopted story fact.
  const edges = [];
  for (const s of scenes) {
    edges.push({from:s.id,to:s.placeId,kind:'scene-has-heading-place',sourcePassageIds:[s.headingPassageId]});
    for(const personId of s.peopleIds) {
      const person=[...characterMap.values()].find(p=>p.id===personId);
      edges.push({from:s.id,to:personId,kind:'scene-has-character-cue',sourcePassageIds:person?.cuePassageIds?.filter(x=>s.passageIds.includes(x))??[]});
    }
  }
  for(const shot of shots) {
    if(shot.sceneId) edges.push({from:shot.id,to:shot.sceneId,kind:'shot-mapped-to-scene',sourcePassageIds:shot.sourcePassageIds});
    for(const c of shot.candidateRecords) {
      if(c.artifactId)edges.push({from:shot.id,to:`candidate:${c.artifactId}`,kind:'shot-has-recorded-artwork',sourcePassageIds:shot.sourcePassageIds});
    }
  }
  const sourcePassages=screenplay.filter(p=>isObject(p)&&validId(p.id)).map(p=>({id:p.id,type:text(p.type,64),text:text(p.text,1600),blockNumber:p.blockNumber??null,miniBlockNumber:p.miniBlockNumber??null}));
  const data = {schemaVersion:2, readonly:true, modeChoices:['REEL','ONCE'], source, scenes, people:[...characterMap.values()], places:[...locationMap.values()], shots, edges, sourcePassages, tabs:['Story','People','Places','Moments','Visuals','Produce','Learn','Review','Share'],
    guidance:{'REEL':{description:'Turn an idea or screenplay into a visual story and movie.', momentsLabel:'Scenes'}, 'ONCE':{description:'Tell your life story, bring memories to life, and preserve them for family.', momentsLabel:'Memories'}},
    learning:[{topic:'theme',lesson:16,title:'Mood, Colour and Visual Language'},{topic:'structure',lesson:19,title:'Why 24 Blocks Work'},{topic:'character',lesson:58,title:'Prove Character Through Choice'}],
    limitations:['Character identities are screenplay cues, not approved appearances.','Place records reflect scene headings, not author-approved shared geography.','Image bytes and native Save/Lock have not been reverified by this projection, even where earlier project records claim package verification.','Media, edits, sharing and provider spending are not available in this read-only milestone.','Selecting ONCE changes navigation language only; it never reclassifies an existing screenplay as a factual personal memory.']};
  return data;
}
