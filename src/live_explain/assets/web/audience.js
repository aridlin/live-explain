"use strict";
const frame = document.getElementById("frame"), statusText = document.getElementById("connection");
let etag = "", previousURL = "";
async function updateFrame() {
  try {
    const response = await fetch("./frame.jpg", {headers: etag ? {"If-None-Match": etag} : {}, cache:"no-store", signal:AbortSignal.timeout(6000)});
    if (response.status === 200) {
      const nextURL = URL.createObjectURL(await response.blob());
      const oldURL = previousURL;
      frame.src = nextURL; previousURL = nextURL;
      if (oldURL) URL.revokeObjectURL(oldURL);
      etag = response.headers.get("ETag") || "";
    } else if (response.status !== 304) { throw new Error("HTTP " + response.status); }
    statusText.textContent = "";
  } catch (_) { statusText.textContent = "Brak połączenia z prezentacją. Ponawiam…"; }
  setTimeout(updateFrame, 160);
}
document.getElementById("fullscreen").addEventListener("click", () => document.documentElement.requestFullscreen());
document.addEventListener("keydown", event => {
  if (event.key.toLowerCase() === "f") document.documentElement.requestFullscreen();
});
updateFrame();
