import { pipeline } from "node:stream/promises";
import { Readable, Transform } from "node:stream";

const ALLOWED_HOST = "v3b.fal.media";
const ALLOWED_TYPES = new Set(["video/mp4", "image/png", "image/webp", "image/jpeg"]);
const PATH_PATTERN = /^\/files\/b\/[A-Za-z0-9_-]+\/[A-Za-z0-9_.-]+\.(?:mp4|png|webp|jpe?g)$/i;

export function validateFalUrl(raw) {
  if (typeof raw !== "string" || raw.length > 2048) throw new Error("Invalid URL");
  let parsed;
  try { parsed = new URL(raw); } catch { throw new Error("Invalid URL"); }
  if (parsed.protocol !== "https:" || parsed.hostname !== ALLOWED_HOST ||
      parsed.port || parsed.username || parsed.password || parsed.hash ||
      !PATH_PATTERN.test(parsed.pathname)) {
    throw new Error("Source must be a supported public fal media asset");
  }
  return parsed.toString();
}

async function readJSON(req, maxBytes = 4096) {
  let size = 0;
  const chunks = [];
  for await (const part of req) {
    size += part.length;
    if (size > maxBytes) throw new Error("Request too large");
    chunks.push(part);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function respond(res, status, message) {
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store"
  });
  res.end(JSON.stringify({ error: message }));
}

/**
 * Prototype ONLY. Mount behind a real authenticated, rate-limited host.
 * authorize(req) must use verified host session/OAuth identity.
 * Never embed API secrets in browser JS, nor open this as a public proxy.
 */
export function makeFalAssetHandler({
  authorize,
  fetchImpl = fetch,
  maxBytes = 100 * 1024 * 1024,
  timeoutMs = 90000
} = {}) {
  if (typeof authorize !== "function") {
    throw new TypeError("A production authorization callback is mandatory");
  }
  return async (req, res) => {
    if (req.method !== "POST") return respond(res, 405, "POST required");
    let source;
    try {
      const authorized = await authorize(req);
      if (!authorized) return respond(res, 401, "Unauthorized");
      const body = await readJSON(req);
      source = validateFalUrl(body?.falUrl);
      const upstream = await fetchImpl(source, {
        method: "GET",
        redirect: "error",
        signal: AbortSignal.timeout(timeoutMs),
        headers: { "accept": "video/mp4, image/png, image/webp, image/jpeg" }
      });
      if (!upstream.ok || !upstream.body) return respond(res, 502, "Fal media unavailable");
      const mime = (upstream.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
      if (!ALLOWED_TYPES.has(mime)) return respond(res, 415, "Unsupported media type");
      const declaredSize = Number(upstream.headers.get("content-length"));
      if (upstream.headers.has("content-length") &&
          (!Number.isSafeInteger(declaredSize) || declaredSize < 1 || declaredSize > maxBytes)) {
        return respond(res, 413, "Media exceeds transfer limit");
      }

      const name = new URL(source).pathname.split("/").pop();
      const safeName = name.replace(/[^a-zA-Z0-9._-]/g, "_");
      res.writeHead(200, {
        "content-type": mime,
        "content-disposition": "attachment; filename=" + JSON.stringify(safeName),
        "cache-control": "no-store",
        "x-content-type-options": "nosniff"
      });
      let total = 0;
      const gate = new Transform({
        transform(chunk, _encoding, callback) {
          total += chunk.length;
          callback(total > maxBytes ? new Error("Transfer size cap exceeded") : null, chunk);
        }
      });
      await pipeline(Readable.fromWeb(upstream.body), gate, res);
    } catch (err) {
      if (res.headersSent) res.destroy(err);
      else {
        const badInput = /Invalid URL|Source must|Request too large|JSON/.test(err.message);
        respond(res, badInput ? 400 : 502, badInput ? "Invalid transfer request" : "Media transfer failed");
      }
    }
  };
}
