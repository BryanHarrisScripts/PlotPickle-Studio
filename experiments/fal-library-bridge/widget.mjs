/** Experimental ChatGPT plugin UI code. Browser access + host file upload unverified. */
const MIME_TYPES = new Set(['video/mp4', 'image/png', 'image/webp', 'image/jpeg']);

function validateMediaUrl(raw) {
  let u;
  try { u = new URL(raw); } catch { throw new Error('Invalid fal media URL'); }
  if (u.protocol !== 'https:' || u.hostname !== 'v3b.fal.media' || u.port ||
      u.username || u.password || u.hash ||
      !/^\/files\/b\/[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+\.(?:mp4|png|webp|jpe?g)$/i.test(u.pathname)) {
    throw new Error('Fal media URL is not allowlisted');
  }
  return u.toString();
}

export async function saveFalAssetToLibrary({
  falUrl,
  proxyUrl = null,
  fileName,
  expectedBytes,
  maxBytes = 100 * 1024 * 1024,
  openai = globalThis.window?.openai,
  fetchImpl = fetch
}) {
  if (typeof openai?.uploadFile !== 'function') {
    throw new Error('ChatGPT uploadFile API is unavailable in this widget');
  }
  const source = validateMediaUrl(falUrl);
  let response;
  let sourceRoute = 'direct';
  try {
    response = await fetchImpl(source, {method: 'GET', mode: 'cors', redirect: 'error', credentials: 'omit'});
    if (!response.ok) throw new Error(`fal HTTP ${response.status}`);
  } catch (error) {
    if (!proxyUrl) throw new Error('Direct fal download unavailable in widget; no approved proxy configured', {cause: error});
    sourceRoute = 'proxy';
    response = await fetchImpl(proxyUrl, {
      method: 'POST', credentials: 'include', headers: {'content-type': 'application/json'},
      body: JSON.stringify({falUrl: source})
    });
    if (!response.ok) throw new Error(`Approved proxy transfer failed: HTTP ${response.status}`);
  }
  const type = (response.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
  if (!MIME_TYPES.has(type)) throw new Error('Downloaded asset MIME type not supported');
  const declared = response.headers.get('content-length');
  if (declared !== null && (!Number.isSafeInteger(Number(declared)) || Number(declared) > maxBytes || Number(declared) < 1)) {
    throw new Error('Downloaded file exceeds size limits');
  }
  const blob = await response.blob();
  if (!blob.size || blob.size > maxBytes || (expectedBytes && blob.size !== expectedBytes)) {
    throw new Error('Downloaded media failed byte count verification');
  }
  const extension = type === 'video/mp4' ? 'mp4' : type === 'image/webp' ? 'webp' : type === 'image/jpeg' ? 'jpg' : 'png';
  const name = (fileName || `fal-render.${extension}`).replace(/[^a-zA-Z0-9._-]/g, '_');
  const file = new File([blob], name, {type});
  const {fileId} = await openai.uploadFile(file, {library: true});
  if (!fileId) throw new Error('ChatGPT upload did not return a file ID');
  return {fileId, fileName: name, mimeType: type, sizeBytes: file.size, sourceRoute,
    status: 'upload-reported', libraryReadbackVerified: false};
}
