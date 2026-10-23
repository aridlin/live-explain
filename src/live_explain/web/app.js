import {scene, esc} from './scene.js';
const presenter=location.pathname==='/presenter';
const $=s=>document.querySelector(s);
const root=$('#app');
let state=null, catalog=[], pending=false, connected=false, lastBeat='', lastStage=-1, sources=[], receivedAt=0;
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
const controller='web-'+Math.random().toString(36).slice(2);
const time=n=>`${Math.floor(n/60).toString().padStart(2,'0')}:${Math.floor(n%60).toString().padStart(2,'0')}`;
const button=(action,label,cls='',title='')=>`<button type="button" data-action="${action}" class="${cls}" title="${title}">${label}</button>`;
const controls=`${button('undo','↶','icon','Cofnij nawigację · U')}${button('replay','↺','icon','Początek kroku · R')}${button('toggle','▶ Odtwórz','play','Odtwórz / pauza · Spacja')}${button('step','Krok ↓','','Dokończ jeden krok · ↓')}${button('advance','Dalej →','primary','Dalej · →')}`;
root.innerHTML=`
<header class="topbar"><a class="brand" href="${presenter?'/presenter':'/'}"><span class="brand-mark">le<span>↗</span></span><span>live explain<small>SPECTRE / MELTDOWN</small></span></a><div class="top-actions"><span class="connection" role="status">Łączenie…</span>${button('sources','Źródła')}${presenter?'<a class="button audience-link" href="/" target="_blank" rel="noopener">Otwórz ekran publiczności ↗</a>':button('fullscreen','Pełny ekran ↗')}</div></header>
${presenter?`<div class="workspace"><aside class="chapters"><div class="eyebrow">PRZEBIEG PREZENTACJI</div><h2>Od śladu do sekretu.</h2><label class="route-label" for="route">Poziom wyjaśnienia</label><select id="route"><option value="simple">Super prosta</option><option value="normal" selected>Normalna</option><option value="deep">Szczegółowa</option></select><nav id="chapters" aria-label="Rozdziały"></nav><div class="sidebar-foot"><span class="eyebrow">CZAS PREZENTACJI</span><strong id="elapsed">00:00</strong><span id="planned"></span></div></aside><main class="studio"><div class="section-heading"><span class="eyebrow">PODGLĄD PUBLICZNOŚCI</span><span id="scene-count"></span></div>`:'<main class="audience-main">'}
<section class="stage" aria-label="Ekran publiczności"><div class="stage-header"><div class="eyebrow"><span id="chapter-number">01</span> <span class="slash">/</span> <span id="phase-label">KANAŁY BOCZNE</span></div><h1 id="scene-title"></h1><p id="scene-subtitle"></p></div><div id="diagram"></div><div class="stage-footer"><span><i class="legend green"></i> ślad w cache <i class="legend amber"></i> praca przejściowa</span><span>Model poglądowy · czasy umowne</span></div><div class="blank-screen" hidden><span>live explain</span><p>Ekran zasłonięty</p></div></section>
<div class="transport"><div class="progress"><label for="scrub">Krok <span id="step-count">1</span></label><input id="scrub" type="range" min="0" max="6" step="0.01" value="0" aria-label="Pozycja animacji"><output id="position">0.0 / 6.0</output></div><div class="control-row">${controls}<span class="spacer"></span>${button('blank','Zasłoń','blank','Zasłoń i wstrzymaj ekran · B')}${presenter?'':button('presenter','Notatki ↗','','Otwórz prywatny widok w osobnym oknie · P')}</div><p class="status" role="status" id="status">→ kolejny krok · spacja pauza · ↓ dokończ · R powtórz</p></div>
${presenter?`<section class="detour-panel"><div><span class="eyebrow">PYTANIE Z SALI?</span><h2>Zatrzymaj się i wyjaśnij.</h2><p id="return-context">Po powrocie wrócisz dokładnie do tego momentu.</p></div><div id="detours"></div>${button('return','↩ Wróć do wyjaśnienia','return')}</section><details class="tools"><summary>Skróty i zapis próby</summary><p>→ dalej · spacja pauza · ↓ krok · R powtórz · U cofnij · B zasłoń · Backspace powrót · F dokończ · F11 pełny ekran</p><a href="/api/recording" download="rehearsal.session.json">Pobierz zapis sesji JSON</a><p>Telefon: otwórz adres laptopa z /presenter. Serwer musi działać z --remote w tej samej sieci.</p></details></main><aside class="notes"><div class="section-heading"><span class="eyebrow">TYLKO DLA PROWADZĄCEGO</span><span class="private-badge">PRYWATNE</span></div><div class="cue-card"><span class="eyebrow">TERAZ</span><h2 id="cue"></h2><p id="next-cue"></p></div><div class="notes-tabs"><button class="selected" data-tab="script">Pełny tekst</button><button data-tab="prompts">Wskazówki</button><button data-action="text-size" title="Zwiększ tekst">A+</button></div><div id="script" class="script-copy"></div><div id="prompts" hidden></div><div class="next-sentence"><span class="eyebrow">PRZEJŚCIE DALEJ</span><p id="next-sentence"></p></div></aside></div>`:'</main>'}
<dialog id="sources-dialog"><div class="section-heading"><span class="eyebrow">MATERIAŁY I INSPIRACJE</span>${button('close-sources','Zamknij ×')}</div><h2>Najpierw zrozumieć.<br>Potem zobaczyć ślad.</h2><p>Trzy popularne wyjaśnienia pomogły uporządkować narrację. Mechanizm sprawdzono w publikacjach badaczy. Diagramy i tekst są własne.</p><div id="sources-list"></div><p class="source-note">Liczby wyświetleń: odczyt metadanych 23.10.2026. Popularność nie dowodzi poprawności. Starsze filmy nie opisują stanu zabezpieczeń dzisiejszych urządzeń.</p><a href="https://spectreattack.com/spectre.pdf" target="_blank" rel="noopener">Spectre: oryginalna publikacja ↗</a><br><a href="https://meltdownattack.com/meltdown.pdf" target="_blank" rel="noopener">Meltdown: oryginalna publikacja ↗</a></dialog>`;
document.body.classList.toggle('presenter',presenter);

function render(s) {
  state=s; receivedAt=performance.now();
  const a=presenter?s.audience:s;
  const stage=a.holds.reduce((n,v,i)=>a.position+1e-8>=v?i:n,0);
  const current=catalog.findIndex(c=>c.id===a.checkpoint);
  $('#scene-title').textContent=a.title;
  $('#scene-subtitle').textContent=a.subtitle;
  $('#chapter-number').textContent=current>=0?String(current+1).padStart(2,'0'):'↳';
  $('#phase-label').textContent=a.checkpoint==='bridge'?'PRZYPOMNIENIE':a.beat.startsWith('detour.')||a.beat.startsWith('shared.')?'WYJAŚNIENIE DODATKOWE':'SPECTRE / MELTDOWN';
  $('#diagram').innerHTML=scene(a);
  $('.blank-screen').hidden=!a.blank;
  $('#scrub').max=a.duration;
  if(document.activeElement!==$('#scrub')) $('#scrub').value=a.position;
  $('#position').textContent=`${a.position.toFixed(1)} / ${a.duration.toFixed(1)}`;
  $('#step-count').textContent=`${stage+1} / ${a.holds.length}`;
  $('[data-action="toggle"]').textContent=a.playing?'Ⅱ Pauza':'▶ Odtwórz';
  $('[data-action="blank"]').textContent=a.blank?'Odsłoń':'Zasłoń';
  $('[data-action="blank"]').classList.toggle('active',a.blank);
  $('[data-action="advance"]').textContent=presenter?s.next_label+' →':a.position>=a.duration?'Następny punkt →':'Dalej →';
  if(presenter) {
    $('#elapsed').textContent=time(s.elapsed);
    $('#planned').textContent=`plan: ${Math.round(s.route_seconds/60)} min`;
    $('#scene-count').textContent=current>=0?`${current+1} / ${catalog.length}`:'↳ dodatkowe';
    $('#cue').textContent=s.stage_cue;
    $('#next-cue').textContent='Za chwilę: '+s.upcoming_cue;
    $('#route').value=s.canonical;
    $('[data-action="return"]').disabled=!s.return_to;
    $('[data-action="undo"]').disabled=!s.can_undo;
    $('#return-context').textContent=s.return_to?`Zachowany punkt: ${s.return_title}`:s.bridge_target?'Uzupełnij podstawy, a potem przejdź do wybranego rozdziału.':'Po powrocie wrócisz dokładnie do tego momentu.';
    if(lastBeat!==s.beat) {
      $('#script').innerHTML=s.script.wording.split('\n\n').map(p=>`<p${p.startsWith('[')?' class="direction"':''}>${esc(p)}</p>`).join('');
      $('#script').scrollTop=0;
      $('#prompts').innerHTML=`<h3>Cel</h3><p>${esc(s.script.objective)}</p><h3>Granice modelu</h3><p>${esc(s.script.boundary)}</p><h3>Powrót</h3><p>${esc(s.return_sentence||s.script.resume_sentence)}</p>`;
      $('#next-sentence').textContent=s.script.next_sentence;
      $('#detours').innerHTML=s.branches.map(b=>`<button data-detour="${esc(b.id)}">${esc(b.title)} ↗</button>`).join('')||'<p>Przejdź przez przypomnienie, aby kontynuować.</p>';
      document.querySelectorAll('[data-chapter]').forEach(b=>{
        const active=b.dataset.chapter===a.checkpoint;
        b.classList.toggle('selected',active);
        if(active)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');
      });
    }
    if(lastBeat!==s.beat||lastStage!==stage) $('#status').textContent=s.status;
  }
  lastBeat=a.beat; lastStage=stage;
}
function connection(ok) {
  connected=ok;
  $('.connection').textContent=ok?'● Połączono':'○ Brak połączenia · ponawiam…';
  $('.connection').classList.toggle('offline',!ok);
  root.classList.toggle('disconnected',!ok);
  for(const b of document.querySelectorAll('.control-row button, #detours button, [data-chapter], #route, #scrub')) b.disabled=!ok||pending;
  if(presenter){
    $('[data-action="return"]').disabled=!ok||pending||!state?.return_to;
    $('[data-action="undo"]').disabled=!ok||pending||!state?.can_undo;
  }
}
async function fetchState() {
  const response=await fetch(presenter?'/state':'/api/audience',{signal:AbortSignal.timeout(3000)});
  if(!response.ok)throw Error('Stan niedostępny');
  const data=await response.json();
  if(!pending)render(presenter?data.state:data);
  connection(true);
}
async function command(kind,value=null) {
  if(!state||pending||!connected)return;
  pending=true; connection(true);
  const body={epoch:state.epoch,revision:state.revision,id:controller+'-'+Date.now()+'-'+Math.random().toString(36).slice(2),kind,value};
  try {
    let receipt;
    // An uncertain POST is retried with the SAME command id. Never double-advance.
    for(let attempt=0;attempt<2;attempt++) {
      try {
        const response=await fetch('/command',{method:'POST',headers:{'Content-Type':'application/json','X-Controller':controller},body:JSON.stringify(body),signal:AbortSignal.timeout(3000)});
        if(!response.ok)throw Error('HTTP '+response.status);
        receipt=await response.json(); break;
      } catch(e) {if(attempt===1)throw e;}
    }
    if(receipt.state)render(presenter?receipt.state:receipt.state.audience);
    $('#status').textContent=receipt.message||'Stan zmienił się. Spróbuj ponownie.';
  } catch {
    $('#status').textContent='Brak potwierdzenia. Sprawdź stan przed kolejnym poleceniem.';
    connection(false);
  } finally {pending=false; if(connected)connection(true);}
}
async function fullscreen() {
  try {if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
  catch {$('#status').textContent='Użyj pełnego ekranu przeglądarki (F11).';}
}
function action(a) {
  if(a==='fullscreen')return fullscreen();
  if(a==='sources')return $('#sources-dialog').showModal();
  if(a==='close-sources')return $('#sources-dialog').close();
  if(a==='presenter')return window.open('/presenter','live-explain-presenter');
  if(a==='text-size')return $('.notes').classList.toggle('large-text');
  if(a==='toggle')a=(presenter?state?.audience:state)?.playing?'pause':'play';
  if(a==='advance'&&presenter&&state?.next_kind==='return')a='return';
  command(a);
}
root.addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b)return;
  if(b.dataset.action)action(b.dataset.action);
  if(b.dataset.detour)command('detour',b.dataset.detour);
  if(b.dataset.chapter)command('chapter',b.dataset.chapter);
  if(b.dataset.tab){
    $('#script').hidden=b.dataset.tab!=='script';$('#prompts').hidden=b.dataset.tab!=='prompts';
    document.querySelectorAll('[data-tab]').forEach(t=>t.classList.toggle('selected',t===b));
  }
});
$('#scrub').addEventListener('change',e=>command('seek',e.target.value));
$('#route')?.addEventListener('change',e=>command('depth',e.target.value));
document.addEventListener('keydown',e=>{
  if(e.repeat||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea')||(e.key===' '&&e.target.closest('button,a'))||$('#sources-dialog').open)return;
  const key={ArrowRight:'advance',ArrowDown:'step',' ':'toggle',r:'replay',u:'undo',b:'blank',Backspace:'return',f:'finish',p:'presenter',F11:'fullscreen'}[e.key];
  if(key){e.preventDefault();action(key);}
});
async function boot() {
  try {
    [catalog,sources]=await Promise.all(['/api/catalog','/sources.json'].map(async p=>{const r=await fetch(p);if(!r.ok)throw Error();return r.json();}));
    if(presenter)$('#chapters').innerHTML=catalog.map((c,i)=>`<button data-chapter="${c.id}"><span>${String(i+1).padStart(2,'0')}</span>${esc(c.title)}</button>`).join('');
    $('#sources-list').innerHTML=sources.map(s=>`<article class="source"><span class="eyebrow">${esc(s.creator)} · ${s.views.toLocaleString('pl-PL')} WYŚWIETLEŃ</span><h3><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a></h3><p>${esc(s.lesson)}</p></article>`).join('');
  } catch {$('#status').textContent='Nie udało się załadować rozdziałów. Odśwież stronę.';}
  while(true){try{await fetchState();}catch{connection(false);}await new Promise(r=>setTimeout(r,100));}
}
function animate() {
  const a=presenter?state?.audience:state;
  if(a?.playing&&connected&&!a.blank&&!reducedMotion){
    const position=Math.min(a.target,a.position+(performance.now()-receivedAt)/1000);
    $('#diagram').innerHTML=scene({...a,position});
  }
  requestAnimationFrame(animate);
}
animate();
boot();
