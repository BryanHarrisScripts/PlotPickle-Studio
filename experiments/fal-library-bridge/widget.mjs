/**
 * Call this only from an actual ChatGPT Plugin UI widget after user action.
 * It has NOT been verified in a live ChatGPT widget host.
 * proxyUrl must target a trusted authenticated same-origin or CSP-approved endpoint.
 */
export async function saveFalAssetToLibrary({
  falUrl,
  proxyUrl = "/api/fetch-fal-asset",
  fileName,
  expectedBytes,
  openai = globalThis.window?.openai,
  fetchImpl = fetch
}) {
  if (typeof openai?.uploadFile !== "function") {
    throw new Error("ChatGPT uploadFile API unavailable");
  }
  const response = await fetchImpl(proxyUrl, {
    method: "POST",
    credentials: "include",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ falUrl })
  });
  if (!response.ok) throw new Error("Proxy transfer failed: HTTP " + response.status);
  const type = (response.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
  if (!["video/mp4", "image/png", "image/webp", "image/jpeg"].includes(type)) {
    throw new Error("Proxy returned unsupported media");
  }
  const blob = await response.blob();
  if (!blob.size || (expectedBytes && blob.size !== expectedBytes)) {
    throw new Error("Downloaded file size failed verification");
  }
  const extension = type === "video/mp4" ? "mp4" : type === "image/webp" ? "webp" :
                    type === "image/jpeg" ? "jpg" : "png";
  const safeName = (fileName || "fal-render." + extension).replace(/[^a-zA-Z0-9._-]/g, "_");
  const file = new File([blob], safeName, { type });
  const { fileId } = await openai.uploadFile(file, { library: true });
  if (!fileId) throw new Error("Upload did not return a file ID");

  // fileId is an upload receipt. Library visibility, folder placement, and
  // independent byte-for-byte readback must still be verified separately.
  return { fileId, fileName: safeName, sizeBytes: file.size, mimeType: type,
           status: "upload-reported", libraryReadbackVerified: false };
}
