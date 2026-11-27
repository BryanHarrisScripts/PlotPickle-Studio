/* PlotPickle Studio — authenticated Library adapter & atomic review draft contracts.
   Portable reference implementation. Site must supply authenticated Library and
   per-user persistent object store adapters; this module never accepts client
   user IDs or performs provider/PPF mutations. */
import { createHash } from 'node:crypto';

export const ROOT = '/PlotPickle/Stories';
export const STORY_PREFIX = 'PP - ';

export function canonicalStoryFolder(story) {
  if (typeof story !== 'string') throw new Error('Story name must be text');
  const clean = story.trim().replace(/^(?:PP\s*-\s*)+/i, '').trim();
  if (!clean || /[\/\\\0]/.test(clean) || clean === '.' || clean === '..')
    throw new Error('Invalid story folder name');
  return `${STORY_PREFIX}${clean}`;
}

const MEDIA = Object.freeze({
  image: new Set(['webp', 'png', 'jpg', 'jpeg', 'gif', 'avif']),
  video: new Set(['mp4', 'mov', 'm4v', 'webm', 'mkv']),
  audio: new Set(['wav', 'mp3', 'flac', 'aac', 'm4a', 'aiff', 'ogg']),
});
const SHA = /^[0-9a-f]{64}$/;
const VALID_ACTIONS = new Set(['keep', 'redo', 'discard']);

export function fileKind(filename) {
  const ext = String(filename || '').split('.').pop().toLowerCase();
  if (Object.values(MEDIA).some(s => s.has(ext))) {
    return Object.entries(MEDIA).find(([, s]) => s.has(ext))[0];
  }
  if (filename.endsWith('.ppf.json')) return 'ppf';
  if (ext === 'json') return 'metadata';
  if (ext === 'zip' || ext === 'tar' || ext === 'gz') return 'archive';
  return 'other';
}

function assertPath(path, root=ROOT) {
  if (typeof path !== 'string' || !path.startsWith(root + '/') || /\x00|\\|\/\.\.?\//.test(path)) {
    throw new Error('File path outside authorized story root');
  }
  return path;
}

export function summarizeProjects(entries, root=ROOT) {
  if (!Array.isArray(entries)) throw new Error('Library entries must be an array');
  const projects = new Map();
  for (const entry of entries) {
    const path = assertPath(entry.path, root);
    const relative = path.slice(root.length + 1);
    const [story, ...rest] = relative.split('/');
    if (!story) continue;
    // Recognize physical PP - folder names without duplicating the prefix.
    // A top-level registry JSON is not a story; a folder is.
    if (!rest.length && entry.kind !== 'folder') continue;
    const normalized = canonicalStoryFolder(story);
    const project = projects.get(normalized) || { story: normalized.slice(STORY_PREFIX.length),
      displayName: normalized,
      folder: `${root}/${story}`, sourceStatus:'unknown', discovered:0, verified:0,
      types:{ image:0,video:0,audio:0,ppf:0,metadata:0,archive:0,other:0 }, unassigned:0, files:[] };
    if (entry.kind === 'file') {
      const kind = fileKind(entry.name);
      project.discovered++;
      project.types[kind]++;
      const verified = entry.verifiedHash === true && SHA.test(entry.sha256 || '');
      if (verified) project.verified++;
      if (kind === 'ppf') project.sourceStatus = verified ? 'source-hash-verified' : 'source-unverified';
      const mapped = verified && Boolean(entry.sourceMappingVerified);
      if (['image','video','audio'].includes(kind) && !mapped) project.unassigned++;
      project.files.push({ path, kind, bytes:entry.size_bytes ?? null,
        libraryFileId:entry.library_file_id ?? null, verified, sourceMappingVerified:mapped });
    }
    projects.set(normalized, project);
  }
  return [...projects.values()].sort((a,b)=>a.displayName.localeCompare(b.displayName));
}

function requireSource(source) {
  if (!source || typeof source.projectId !== 'string' || !source.projectId ||
      typeof source.ppfSha256 !== 'string' || !SHA.test(source.ppfSha256) ||
      !Number.isSafeInteger(source.revision) || source.revision < 0) {
    throw new Error('Missing or invalid source PPF pin');
  }
}

export function prepareBatchPreview({source, candidates, decisions}) {
  requireSource(source);
  if (!Array.isArray(candidates) || !Array.isArray(decisions)) throw new Error('Expected arrays');
  if (decisions.length > 2500) throw new Error('Batch too large');
  const byKey = new Map(), visited = new Set(), items=[];
  for (const item of candidates) {
    const key = `${item.shot}:${item.kind}:${item.candidateId}`;
    if (byKey.has(key)) throw new Error('Duplicate catalog candidate');
    byKey.set(key,item);
  }
  for (const d of decisions) {
    if (!Number.isInteger(d.shot) || d.shot < 1 || d.shot > 25 ||
        !['image','video','audio'].includes(d.kind) ||
        typeof d.candidateId !== 'string' || !d.candidateId ||
        !VALID_ACTIONS.has(d.action) || !SHA.test(d.mediaSha256||'')) {
      throw new Error('Malformed batch decision');
    }
    const key = `${d.shot}:${d.kind}:${d.candidateId}`;
    if (visited.has(key)) throw new Error('Duplicate decision');
    visited.add(key);
    const current = byKey.get(key), issues=[];
    if (!current) issues.push('candidate-not-registered');
    else {
      if (current.mediaSha256 !== d.mediaSha256) issues.push('candidate-hash-changed');
      if (current.verified !== true) issues.push('media-unverified');
      if (current.sourceMappingVerified !== true) issues.push('shot-link-unverified');
      if (current.ppfLocked === true && (d.action === 'redo' || d.action === 'discard'))
        issues.push('locked-source-requires-unlock');
    }
    if (d.requestLock === true && d.action !== 'keep') issues.push('lock-requires-keep');
    if (d.requestLock === true && current?.humanApproved !== true)
      issues.push('lock-requires-explicit-approval');
    const {shot,kind,candidateId,mediaSha256,action} = d;
    items.push({shot,kind,candidateId,mediaSha256,action,requestLock:d.requestLock===true,
      issues,blocked:issues.length>0});
  }
  const canonical = JSON.stringify({source,items});
  const fingerprint = createHash('sha256').update(canonical).digest('hex');
  return {schema:'plotpickle.batch-draft.v1',source,items,fingerprint,
    counts:Object.fromEntries(['keep','redo','discard'].map(action=>[action,items.filter(i=>i.action===action).length])),
    blocked:items.filter(i=>i.blocked).length,
    execution:false, nativePpfWritten:false, providerJobSubmitted:false,
    note:'Read-only batch preview; Keep is not Save/Lock, Redo/Discard do not mutate media.'};
}

/* A site-hosted persistence bridge must implement:
   store.read(actor,projectId)->{revision,value}|null
   store.compareAndSwap(actor,projectId,expectedRevision,nextValue)->{revision,value}
   Both methods must resolve actor identity from the authenticated SERVER session,
   never from an HTTP parameter or client header. No global/shared fallback. */
export async function persistReviewDraft({authenticatedActor,store,source,candidates,
                                           decisions,expectedStudioRevision}) {
  if (!authenticatedActor || typeof authenticatedActor !== 'string') throw new Error('Not authenticated');
  if (!Number.isSafeInteger(expectedStudioRevision) || expectedStudioRevision<0)
    throw new Error('Expected Studio revision required');
  const preview=prepareBatchPreview({source,candidates,decisions});
  // A rejected execution action can still be recorded as a REVIEW PROPOSAL.
  // The review batch remains non-executing; blocked items visibly retain their
  // issues and cannot be promoted to generation, deletion or native Save/Lock.
  const current=await store.read(authenticatedActor,source.projectId);
  if ((current?.revision??0)!==expectedStudioRevision) throw new Error('Stale Studio revision');
  if (current?.value?.source && (
     current.value.source.ppfSha256 !== source.ppfSha256 ||
     current.value.source.revision !== source.revision)) throw new Error('Source changed since review');
  // Draft state only. Source PPF, originals and production timeline unchanged.
  const receipt=await store.compareAndSwap(authenticatedActor,source.projectId,
    expectedStudioRevision,{...(current?.value || {}),source,reviewBatch:preview,
      modifiedAt:new Date().toISOString()});
  const reread=await store.read(authenticatedActor,source.projectId);
  if (reread?.revision!==receipt.revision || reread?.value?.reviewBatch?.fingerprint!==preview.fingerprint)
    throw new Error('Independent saved-draft readback failed');
  return {saved:true,studioRevision:reread.revision,fingerprint:preview.fingerprint,
    nativePpfWritten:false,mediaDeleted:false,providerJobSubmitted:false,
    blockedItems:preview.blocked};
}

/* Real Library loading requires the Site's authorized ChatGPT Library adapter.
   The registry is only a pointer list. A caller-supplied folder or user ID
   NEVER becomes an authorization grant. The adapter must resolve an identity
   from the authenticated server session and provide:
      listFilesForActor({actor,folderPath,recursive:true})
      readFileForActor({actor,libraryFileId}) -> Uint8Array
   Optional decodeMedia({kind,bytes,path}) checks media validity and metadata.
   Unknown/unmapped assets stay in the Media Bin, never the timeline. */
export async function loadProjectFromLibrary({authenticatedActor,registry,projectKey,library,decodeMedia}) {
  if (!authenticatedActor || typeof authenticatedActor !== 'string') throw new Error('Not authenticated');
  if (!registry || registry.schema !== 'plotpickle.library-project-registry.v1' || !Array.isArray(registry.projects))
    throw new Error('Invalid project registry');
  const project = registry.projects.find(p=>p.key===projectKey);
  if (!project) throw new Error('Unknown project key');
  const folder = assertPath(project.libraryPath);
  const basename = folder.slice(ROOT.length + 1);
  if (!basename || basename.includes('/') || canonicalStoryFolder(basename)!==basename)
    throw new Error('Project registry path is not a PP - story folder');
  if (typeof library?.listFilesForActor !== 'function' || typeof library?.readFileForActor !== 'function')
    throw new Error('LIBRARY_CONNECTOR_UNAVAILABLE');
  const entries=await library.listFilesForActor({actor:authenticatedActor,folderPath:folder,recursive:true});
  if (!Array.isArray(entries) || entries.length>2500) throw new Error('Invalid Library response');
  const observed = [];
  const seenIds = new Set();
  for (const item of entries) {
    if (item.kind !== 'file') continue;
    const path = assertPath(item.path);
    if (!path.startsWith(folder+'/') || !item.library_file_id || seenIds.has(item.library_file_id))
      throw new Error('Invalid or repeated Library file');
    seenIds.add(item.library_file_id);
    const kind=fileKind(item.name);
    if (!['image','video','audio','ppf'].includes(kind)) {
      observed.push({kind,path,libraryFileId:item.library_file_id,bytes:item.size_bytes??null,
        hashVerified:false,decodeVerified:false,sourceMappingVerified:false,editorPlacement:'support-file'});
      continue;
    }
    const raw=await library.readFileForActor({actor:authenticatedActor,libraryFileId:item.library_file_id});
    if (!(raw instanceof Uint8Array)) throw new Error('Library raw media unavailable');
    const hash=createHash('sha256').update(raw).digest('hex');
    if (item.size_bytes!==undefined && item.size_bytes!==raw.byteLength)
      throw new Error('Library byte count differs from file metadata');
    const expectedSource=project.source?.path===path?project.source:null;
    if (expectedSource?.sha256 && expectedSource.sha256!==hash)
      throw new Error('PPF_SOURCE_HASH_CONFLICT');
    let decoded=null;
    if (['image','video','audio'].includes(kind) && typeof decodeMedia==='function')
      decoded=await decodeMedia({kind,path,bytes:raw});
    // Only the real PPF/mapping may establish shot placement. Newly scanned
    // media has no verified map, regardless of file numbering or folder name.
    observed.push({kind,path,libraryFileId:item.library_file_id,bytes:raw.byteLength,
      sha256:hash,hashVerified:true,decodeVerified:decoded?.verified===true,
      mediaDetails:decoded?.verified===true?(decoded.details??null):null,
      sourceMappingVerified:false,editorPlacement:kind==='ppf'?'source':'unassigned',
      sourcePpf:!!expectedSource});
  }
  const bin=observed.filter(f=>['image','video','audio'].includes(f.kind));
  return {schema:'plotpickle.library-project-snapshot.v1',projectKey,displayName:project.displayName,
    sourcePpf:observed.find(f=>f.sourcePpf)??null,folder,items:observed,
    counts:{total:observed.length,image:bin.filter(f=>f.kind==='image').length,
      video:bin.filter(f=>f.kind==='video').length,audio:bin.filter(f=>f.kind==='audio').length,
      mediaHashVerified:bin.filter(f=>f.hashVerified).length,
      mediaDecodeVerified:bin.filter(f=>f.decodeVerified).length,
      unassigned:bin.length},
    editorLoaded:false,libraryAuthorized:true,ppfWritten:false,timelineModified:false,
    note:'Actual Library files inspected. Editor assignment requires source-linked mapping and guarded site-side import.'};
}
