export const MAX_BYTES = 100 * 1024 * 1024;
export const RESOURCE_URI = 'ui://plotpickle/fal-library-import/v1.html';
const MEDIA_RE = /^\/files\/b\/[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+\.mp4$/i;

export function validateRequest(input) {
  if (!input || typeof input !== 'object') throw new Error('Input required');
  let uri;
  try { uri = new URL(input.falUrl); } catch { throw new Error('Invalid fal media URL'); }
  if (uri.protocol !== 'https:' || uri.hostname !== 'v3b.fal.media' ||
      uri.username || uri.password || uri.port || uri.hash ||
      !MEDIA_RE.test(uri.pathname)) throw new Error('Only direct v3b.fal.media MP4 URLs are supported');
  const expectedBytes = Number(input.expectedBytes);
  if (!Number.isSafeInteger(expectedBytes) || expectedBytes < 1 || expectedBytes > MAX_BYTES) {
    throw new Error('Expected media byte count must be 1 through 100 MiB');
  }
  const storyId = String(input.storyId || '').trim();
  const shotId = String(input.shotId || '').trim();
  if (!storyId || storyId.length > 120 || !shotId || shotId.length > 120) {
    throw new Error('Story and shot addresses are required');
  }
  const filename = String(input.fileName || `fal-${shotId}.mp4`);
  if (!/^[A-Za-z0-9._-]{1,120}\.mp4$/i.test(filename)) throw new Error('Unsafe filename');
  return Object.freeze({url:uri.toString(),expectedBytes,storyId,shotId,filename,
    transferMode:'direct-fal-to-chatgpt-library',registration:'pending',
    libraryReadbackVerified:false,savedLockedUnchanged:true});
}

export function prepareToolResult(input) {
  const transfer = validateRequest(input);
  return {
    content:[{type:'text',text:`Ready to test original fal video import for ${transfer.storyId} / ${transfer.shotId}. No generation or project edits. Require explicit user click in widget.`}],
    structuredContent:transfer
  };
}
