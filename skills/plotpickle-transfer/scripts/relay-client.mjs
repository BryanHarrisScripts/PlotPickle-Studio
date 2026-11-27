// PlotPickle original fal transfer: optional MCP App browser client, not a server or deployed UI.
// Ported from PlotPickle Relay v0.1.1. No paid calls, no external storage, no PPF mutation.
export const MAX_MP4_BYTES = 100 * 1024 * 1024;
export function validateSource(url, expectedBytes) {
  let u;
  try { u = new URL(url); } catch { return 'INVALID_URL'; }
  if (u.protocol !== 'https:' || u.hostname !== 'v3b.fal.media' || u.port || u.username || u.password || u.search || u.hash || !/^\/files\/b\/[a-z0-9]+\/[A-Za-z0-9_-]+\.mp4$/.test(u.pathname)) return 'NON_ALLOWLISTED_URL';
  if (!Number.isSafeInteger(expectedBytes) || expectedBytes < 512 || expectedBytes > MAX_MP4_BYTES) return 'INVALID_EXPECTED_BYTES';
  return null;
}
export async function sha256Hex(data, cryptoAPI) {
  const buf = await cryptoAPI.subtle.digest('SHA-256', data);
  return [...new Uint8Array(buf)].map(v => v.toString(16).padStart(2,'0')).join('');
}
export async function fetchOriginal(source, env) {
  const problem = validateSource(source.url, source.expectedBytes);
  if (problem) return {status:'blocked', reason:problem};
  if (typeof env.fetch !== 'function') return {status:'blocked',reason:'FETCH_UNAVAILABLE'};
  let response;
  try {
    response=await env.fetch(source.url, {method:'GET', mode:'cors', credentials:'omit', redirect:'error', cache:'no-store'});
  } catch(err) { return {status:'blocked',reason:'BROWSER_CORS_OR_NETWORK_FAILURE',detail:String(err).slice(0,180)}; }
  if (!response?.ok || response.redirected || response.type==='opaque') return {status:'blocked', reason:'SOURCE_HTTP_OR_OPAQUE_RESPONSE',httpStatus:response?.status??null};
  const ct=(response.headers?.get('content-type')||'').split(';')[0].toLowerCase().trim();
  if (ct && ct!=='video/mp4' && ct!=='application/octet-stream') return {status:'blocked',reason:'UNEXPECTED_CONTENT_TYPE',contentType:ct};
  const cl=response.headers?.get('content-length');
  if (cl !== null && cl!==undefined && cl!=='' && Number(cl)!==source.expectedBytes) return {status:'blocked',reason:'CONTENT_LENGTH_MISMATCH',reportedBytes:Number(cl)};
  let data;
  try { data = await response.arrayBuffer(); }
  catch(e) { return {status:'blocked',reason:'RESPONSE_BYTES_UNREADABLE',detail:String(e).slice(0,180)}; }
  if (data.byteLength!==source.expectedBytes) return {status:'blocked',reason:'BYTE_COUNT_MISMATCH',actualBytes:data.byteLength,expectedBytes:source.expectedBytes};
  const sig=new Uint8Array(data);
  if (sig.length<16 || sig[4]!==0x66 || sig[5]!==0x74 || sig[6]!==0x79 || sig[7]!==0x70) return {status:'blocked',reason:'MP4_SIGNATURE_MISSING'};
  if (!env.crypto?.subtle?.digest) return {status:'blocked',reason:'SHA256_UNAVAILABLE'};
  const sha256=await sha256Hex(data,env.crypto);
  return {status:'bytes-verified', bytes:data.byteLength,sha256, data};
}
export async function uploadOriginal(source, fetched, env) {
  if(fetched.status!=='bytes-verified' || !fetched.data) return {status:'blocked',reason:'NO_VERIFIED_SOURCE_BYTES'};
  if(typeof env.openai?.uploadFile!=='function') return {status:'blocked',reason:'CHATGPT_PLUGIN_UPLOAD_HELPER_UNAVAILABLE',bytes:fetched.bytes,sha256:fetched.sha256};
  // The legacy source naming convention is only for the creator's existing Third Bell test set.
  const filename=`The-Third-Bell-Shot-${String(source.shot).padStart(2,'0')}-fal-original.mp4`;
  let file;
  try { file=new env.File([fetched.data], filename,{type:'video/mp4'}); }
  catch(e) { return {status:'blocked',reason:'BROWSER_FILE_CONSTRUCTION_FAILED',detail:String(e)}; }
  let uploaded;
  try { uploaded=await env.openai.uploadFile(file,{library:true}); }
  catch(e) { return {status:'blocked',reason:'LIBRARY_UPLOAD_REJECTED',detail:String(e).slice(0,180)}; }
  const fileId = uploaded?.fileId;
  if(typeof fileId!=='string' || !/^file[-_][A-Za-z0-9_-]{8,}$/.test(fileId)) return {status:'blocked',reason:'UPLOAD_DID_NOT_RETURN_FILE_ID'};
  const base={status:'library-uploaded-awaiting-independent-readback',fileId,bytes:fetched.bytes,sha256:fetched.sha256};
  if(typeof env.openai?.getFileDownloadUrl !== 'function') return base;
  try {
    const returned=await env.openai.getFileDownloadUrl({fileId});
    const url=returned?.downloadUrl;
    if(!url || !/^https:\/\//.test(url)) return {...base,readback:'url-unavailable'};
    const check = await env.fetch(url,{method:'GET',credentials:'omit',cache:'no-store'});
    if(!check?.ok || check.type==='opaque') return {...base,readback:'fetch-denied'};
    const rb=await check.arrayBuffer();
    const rbSha=await sha256Hex(rb,env.crypto);
    return {...base, readback:rb.byteLength===fetched.bytes && rbSha===fetched.sha256?'browser-byte-match':'MISMATCH',readbackBytes:rb.byteLength,readbackSha256:rbSha};
  } catch(e) { return {...base,readback:'browser-readback-unavailable',detail:String(e).slice(0,180)}; }
}
