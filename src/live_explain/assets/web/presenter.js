"use strict";
const $ = id => document.getElementById(id);
const API = new URL("../", location.href);
const prefix = "live-explain:" + API.href;
let controller = localStorage.getItem(prefix + ":controller");
if (!controller) { controller = crypto.randomUUID(); localStorage.setItem(prefix + ":controller", controller); }
let state = null, busy = false, displayedBeat = "", lastScript = "", connectionLost = false;
let pending = JSON.parse(sessionStorage.getItem(prefix + ":pending") || "null");
const headers = {"Content-Type":"application/json", "X-Controller":controller};
async function request(path, envelope) {
  const response = await fetch(new URL(path, API), {method:envelope ? "POST":"GET", headers,
    body:envelope ? JSON.stringify(envelope):undefined, cache:"no-store", signal:AbortSignal.timeout(7000)});
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}
function options(select, values) {
  const selected = select.value;
  const key = JSON.stringify(values.map(v => [v.id, v.title]));
  if (select.dataset.options === key) return;
  select.replaceChildren(...values.map(v => { const option = document.createElement("option"); option.value = v.id; option.textContent = v.title; return option; }));
  select.dataset.options = key;
  if (values.some(v => v.id === selected)) select.value = selected;
}
function render(nextState) {
  state = nextState;
  $("title").textContent = state.title;
  $("stage").textContent = state.stage_cue;
  $("next").textContent = state.next_label || "Dalej";
  $("pause").textContent = state.playing || state.transitioning && !state.transition_paused ? "Pauza":"Wznów";
  if (lastScript !== state.script.wording) {
    $("script").replaceChildren(...state.script.wording.split("\n\n").map(text => { const paragraph = document.createElement("p"); paragraph.textContent = text; return paragraph; }));
    lastScript = state.script.wording;
  }
  $("return-context").textContent = state.return_sentence || "";
  options($("route"), state.routes);
  options($("branch"), state.branches);
  if (displayedBeat !== state.beat) { $("route").value = state.canonical; displayedBeat = state.beat; window.scrollTo(0, 0); }
  const blocked = busy || Boolean(pending);
  for (const button of document.querySelectorAll("button")) button.disabled = blocked;
  $("back").disabled = blocked || !state.return_to;
  $("undo").disabled = blocked || !state.can_undo;
  $("open-branch").disabled = blocked || !state.branches.length;
  $("blank").textContent = state.blank ? "Pokaż ekran":"Zasłoń ekran";
}
async function resolvePending() {
  if (!pending) return true;
  const result = await request("resolve", pending);
  if (result.status === "pending") return false;
  pending = null; sessionStorage.removeItem(prefix + ":pending");
  if (result.state) render(result.state);
  $("status").textContent = result.message || (result.status === "wrong_epoch" ? "Sesja serwera została zmieniona. Wczytano nowy stan.":"");
  return true;
}
async function send(kind, value = null) {
  if (busy || pending || !state) return;
  busy = true;
  render(state);
  pending = {epoch:state.epoch, revision:state.revision, id:crypto.randomUUID(), kind, value};
  sessionStorage.setItem(prefix + ":pending", JSON.stringify(pending));
  try {
    const result = await request("command", pending);
    if (result.status === "pending") throw new Error("Niepotwierdzone polecenie");
    pending = null; sessionStorage.removeItem(prefix + ":pending");
    if (result.state) render(result.state);
    if (kind === "reset" && result.status === "accepted") window.scrollTo(0, 0);
    $("status").textContent = result.message || "";
  } catch (_) {
    $("status").textContent = "Sprawdzam wynik polecenia. Nie wysyłam kolejnego kroku.";
    try { await resolvePending(); } catch (_) { /* Polling resolves the SAME identity after reconnect. */ }
  } finally { busy = false; if (state) render(state); }
}
$("next").onclick = () => send(state.next_kind || "advance");
$("pause").onclick = () => send(state.playing || state.transitioning && !state.transition_paused ? "pause":"play");
$("finish").onclick = () => send("finish");
$("reset").onclick = () => {
  if (confirm("Wrócić do początku bieżącej wersji prezentacji? Postęp i historia cofania zostaną wyzerowane.")) send("reset");
};
$("back").onclick = () => send("return");
$("undo").onclick = () => send("undo");
$("replay").onclick = () => send("replay");
$("blank").onclick = () => send("blank", state.blank ? "off":"on");
$("change-route").onclick = () => send("depth", $("route").value);
$("open-branch").onclick = () => send("detour", $("branch").value);
async function poll() {
  if (!busy) {
    try {
      busy = true;
      if (pending && !await resolvePending()) throw new Error("pending");
      const result = await request("state");
      if (result.state) {
        busy = false; render(result.state);
        if (connectionLost) $("status").textContent = "Połączono ponownie.";
        connectionLost = false;
      }
    } catch (_) { connectionLost = true; $("status").textContent = "Brak połączenia. Ponawiam odczyt stanu…"; }
    finally { busy = false; if (state) render(state); }
  }
  setTimeout(poll, 500);
}
for (const button of document.querySelectorAll("button")) button.disabled = true;
poll();
