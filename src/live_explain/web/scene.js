// Pure SVG projection of the server's deterministic educational model.
export const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const C = {ink:'#eeeee5', muted:'#a9b4a9', green:'#b9f584', amber:'#ffbd78', red:'#ff8c87', blue:'#8bd5e8', line:'#3e4941', panel:'#1b231e'};
const text = (x,y,t,size=24,color=C.ink,extra='') => `<text x="${x}" y="${y}" fill="${color}" font-size="${size}" ${extra}>${esc(t)}</text>`;
const box = (x,y,w,h,stroke=C.line,fill=C.panel) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
const line = (x,y,x2,y2,color=C.line,dash=false) => `<path d="M${x} ${y} L${x2} ${y2}" fill="none" stroke="${color}" stroke-width="3" ${dash?'stroke-dasharray="8 8"':''} marker-end="url(#arrow)"/>`;
const pill = (x,y,label,color=C.green,w=210) => box(x,y,w,42,color,'#202b22')+text(x+16,y+28,label,19,color);
function card(x,y,w,h,label,value,color=C.green,detail='') {
  const size=Math.min(36,(w-48)/Math.max(1,String(value).length*.62));
  const words=detail.split(' '), rows=[];let row='';
  for(const word of words){if((row+' '+word).length*11>w-48&&row){rows.push(row);row=word;}else row+=(row?' ':'')+word;}if(row)rows.push(row);
  return box(x,y,w,h)+text(x+24,y+40,label,Math.min(19,(w-48)/Math.max(1,label.length*.6)),C.muted)+text(x+24,y+98,value,size,color)+rows.map((r,i)=>text(x+24,y+h-24-(rows.length-1-i)*25,r,19,C.muted)).join('');
}
function chain(labels,active=4,y=185) {
  return labels.map((label,i)=>{
    const x=40+i*285, on=i<=active;
    return box(x,y,250,140,on?C.green:C.line)+text(x+20,y+37,`0${i+1}`,18,C.muted)+text(x+20,y+92,label,Math.min(29,210/(label.length*.62)),on?C.green:C.muted)+(i<3?line(x+254,y+70,x+280,y+70):'');
  }).join('');
}
function memory(s, y=340) {
  let out=text(40,y-30,'PAMIĘĆ OFIARY',20,C.muted)+text(710,y-30,'granica funkcji: 8 elementów',20,C.amber);
  for(let i=0;i<16;i++) {
    const x=40+i*70, chosen=i===s.model.index;
    out+=text(x+24,y-8,String(i),18,C.muted)+box(x,y,60,64,chosen?C.amber:C.line,i>=8?'#29221e':C.panel)+text(x+30,y+42,i===12&&s.diagram.secret&&!s.model.revealed?'?':String(s.model.memory[i]),25,chosen?C.amber:C.ink,'text-anchor="middle"');
  }
  return out+`<path d="M595 ${y-25} v110" stroke="${C.amber}" stroke-dasharray="5 5" stroke-width="2"/>`;
}
function code(s,x=40,y=65,w=600) {
  const m=s.model;
  let focus=m.discarded?-1:m.cached?3:m.issued?2:m.predicted?1:0;
  if(s.checkpoint==='bytes'||s.checkpoint==='timing') focus=m.elapsed_units===2?2:m.issued?1:0;
  return box(x,y,w,210)+text(x+24,y+35,'KOD POGLĄDOWY',18,C.muted)+s.code.map((l,i)=>
    (i===focus?`<rect x="${x+12}" y="${y+51+i*29}" width="${w-24}" height="29" rx="4" fill="#2f402e"/>`:'')+
    text(x+24,y+73+i*29,String(i+1).padStart(2,'0'),17,C.muted)+text(x+66,y+73+i*29,l,19,i===focus?C.green:C.ink,'font-family="Mono, monospace"')).join('');
}
function probes(s,y=370,measured=false) {
  let out=text(40,y-28,'PROBE · miejsca obserwowane przez pomiar czasu',20,C.muted);
  const m=s.model;
  const values=Array.isArray(m.measurements?.[0])?m.measurements[2]:m.measurements;
  for(let i=0;i<4;i++) {
    const hit=measured ? values?.[i]<5 : m.probe===i;
    const x=40+i*285;
    out+=box(x,y,250,115,hit?C.green:C.line)+text(x+18,y+32,`probe[${i} × stride]`,19,C.muted)+text(x+18,y+82,measured&&values?`${values[i]} j.`:hit?'w cache':s.diagram.secret&&m.cached?'ślad ukryty':'—',30,hit?C.green:C.ink);
  }
  return out;
}
function token(s,x1,y1,x2,y2,start=0,end=4,label='adres 4') {
  const p=Math.max(0,Math.min(1,(s.position-start)/(end-start)));
  if(p<=0||p>=1) return '';
  const x=x1+(x2-x1)*p, y=y1+(y2-y1)*p;
  return `<circle cx="${x}" cy="${y}" r="12" fill="${C.amber}"/>`+text(x,y-25,label,20,C.amber,'text-anchor="middle"');
}
export function scene(s) {
  const m=s.model, p=s.position, phase=s.diagram.phase||s.checkpoint;
  let out='';
  if(s.checkpoint==='bridge') {
    const cards=s.diagram.cards||[];
    out=card(40,120,530,255,cards[0],cards[1],C.blue)+card(610,120,530,255,cards[2],cards[3],C.green)+text(40,465,'Krótki most do wybranego rozdziału.',26,C.muted);
  } else if(phase==='opening') {
    out=text(40,85,'CZY ŚLAD MOŻE ZDRADZIĆ SEKRET?',20,C.green)+text(40,165,'Nie widzisz spotkania.',48)+text(40,230,'Widzisz jego ślady.',48,C.green);
    out+=box(40,300,330,200)+text(68,345,'PENTAGON',20,C.muted)+`<path d="M190 375 l62 40 -24 65 h-76 l-24 -65 z" fill="none" stroke="${C.ink}" stroke-width="3"/>`;
    out+=line(380,400,460,400,C.amber)+box(480,300,330,200)+text(508,345,'ZAMÓWIENIA',20,C.muted);
    [0,1,2,3,4,5,6].forEach((i)=>out+=`<rect x="${510+i*39}" y="${470-(m.pizza_busy?40+i*13:20)}" width="22" height="${m.pizza_busy?40+i*13:20}" rx="4" fill="${m.pizza_busy?C.amber:C.line}"/>`);
    out+=text(850,355,'Obserwacja',27,C.amber)+text(850,400,'≠',40,C.muted)+text(850,445,'pewność',27)+text(40,565,'W komputerze obserwujemy czas dostępu do pamięci.',26,C.muted);
  } else if(phase==='isolation'||phase==='bounds') {
    out=card(40,55,335,200,'WEJŚCIE',m.allowed===false?'x = 12':'x = 4',C.amber,'numer wybranego elementu')+card(420,55,335,200,'REGUŁA','x < 8',C.blue,'dozwolony zakres: 0–7')+card(800,55,340,200,'WYNIK',m.allowed===null?'czekamy':m.allowed?'dozwolony':'odmowa',m.allowed===false?C.red:C.green);
    out+=memory(s,360)+text(40,535,phase==='isolation'?'Reguła funkcji i uprawnienia sprzętu to różne granice.':'12 < 8 jest fałszem. Predykcja nie zmienia tej reguły.',27,C.amber);
  } else if(phase==='bytes'||phase==='timing') {
    out=code(s,40,35,600)+card(690,35,450,210,'ODCZYT TEGO SAMEGO ADRESU',m.elapsed_units===null?'…':`${m.elapsed_units} jednostek`,m.elapsed_units===2?C.green:C.amber,m.elapsed_units===2?'kopię znaleziono w cache':'pierwszy odczyt czeka na pamięć');
    out+=memory(s,340)+line(355,253,355,310,C.amber)+token(s,355,255,355,320,0,4);
    out+=text(40,510,'RAM',22,C.muted)+`<rect x="130" y="487" width="${p>=4?540:Math.min(p/4,1)*540}" height="30" rx="5" fill="${C.amber}"/>`+text(700,511,p>=4?'9 j.':'',24,C.amber);
    if(phase==='timing') out+=text(40,560,'CACHE',22,C.muted)+`<rect x="130" y="537" width="${p>=6?120:Math.max(0,p-4)/2*120}" height="30" rx="5" fill="${C.green}"/>`+text(280,561,p>=6?'2 j.':'',24,C.green);
  } else if(phase==='cache') {
    out=box(40,55,770,430)+text(70,99,'PROCESOR',20,C.muted)+card(75,155,310,210,'RDZEŃ','wykonuje',C.ink,'instrukcje programu')+card(430,155,340,210,'CACHE','kopie danych',C.green,'blisko rdzenia')+line(390,260,425,260,C.green)+card(865,155,275,210,'RAM','pamięć',C.blue,'większa i wolniejsza')+line(815,260,860,260,C.blue);
    out+=text(70,440,p>=2?'Cache przechowuje całe linie, nie tylko wybrany bajt.':'Najpierw szukamy kopii blisko procesora.',24,C.muted);
    if(p>=2) { for(let i=0;i<16;i++) out+=box(60+i*67,520,59,49,i===4?C.amber:C.green)+text(87+i*67,553,String(i),19,i===4?C.amber:C.ink,'text-anchor="middle"'); }
  } else if(phase==='channel') {
    out=chain(['wartość 1','adres probe','cache','czas'],p>=2?3:0,90)+probes(s,370)+text(40,560,'Wartość steruje wyborem adresu. Czas pozwala rozpoznać wybór.',26,C.green);
  } else if(phase==='speculation') {
    out=text(40,55,'DLACZEGO PROCESOR WYPRZEDZA PROGRAM?',20,C.green);
    out+=text(40,150,'CZEKAJ',23,C.muted)+box(290,95,500,100,C.blue)+text(315,138,'Warunek czeka na dane',26,C.blue)+text(315,172,'jednostki wykonawcze mogą być bezczynne',19,C.muted)+box(830,95,310,100)+text(854,153,'dopiero potem praca',24);
    out+=line(795,145,825,145,C.muted)+line(290,245,1130,245,C.line)+text(292,282,'wcześniej',19,C.muted)+text(1030,282,'później',19,C.muted);
    out+=text(40,380,'PRZEWIDUJ',23,C.amber)+box(290,320,500,95,C.blue)+text(315,374,'Ten sam czas oczekiwania',26,C.blue);
    if(m.predicted)out+=box(430,435,360,90,m.discarded?C.red:C.amber)+text(454,489,m.discarded?'błędny wynik odrzucony':'praca wybranej ścieżki',25,m.discarded?C.red:C.amber);
    else out+=text(430,485,'Czy możemy zacząć wcześniej?',25,C.muted);
    out+=text(40,590,m.discarded?'Pomyłka: odrzuć wynik. Co stało się z cache?':'Trafna predykcja oszczędza czas. Błędną trzeba wycofać.',27,m.discarded?C.green:C.ink);
  } else if(phase==='training') {
    out=card(40,60,330,180,'WARUNEK','czeka na dane',C.blue)+line(375,150,455,150,C.amber)+card(470,60,670,180,'PREDYKTOR',m.discarded?'pomylił się':'przewiduje kierunek',m.discarded?C.red:C.amber,'Wykonanie może ruszyć przed rozstrzygnięciem.');
    out+=text(40,305,'HISTORIA POPRAWNYCH WEJŚĆ',20,C.muted);
    [1,3,0,2].forEach((v,i)=>out+=card(40+i*220,340,190,145,`PRÓBA ${i+1}`,phase==='training'&&m.history.length<=i?'…':`x = ${v}`,C.green));
    out+=pill(955,390,'x = 12 ?',C.amber,185)+text(40,555,'Procesor przewiduje ścieżkę, a nie wartość sekretu.',29,C.amber);
  } else if(phase==='rollback') {
    out=card(40,75,535,260,'STAN ARCHITEKTONICZNY',m.discarded?'wynik odrzucony':'praca przejściowa',m.discarded?C.red:C.ink,'To widzi poprawnie wykonany program.')+card(610,75,530,260,'STAN MIKROARCHITEKTURY',m.cached?'ślad pozostaje':'cache bez śladu',m.cached?C.green:C.muted,'Czas dostępu może ujawnić zmianę.');
    out+=text(40,430,'COFNIĘCIE WYNIKU',21,C.muted)+text(40,510,'nie jest wymazaniem historii sprzętu.',40,C.green);
  } else if(phase==='spectre'||phase==='meltdown') {
    out=code(s,40,30,645)+card(730,30,410,210,phase==='spectre'?'SPRAWDZENIE ZAKRESU':'UPRAWNIENIA ODCZYTU',m.discarded?'brak wyniku':m.issued?'przejściowy odczyt':'czekamy',m.discarded?C.red:C.amber,phase==='spectre'?'ofiara ma dostęp do danych':'dotyczy podatnych układów');
    out+=line(350,250,350,335,C.amber)+token(s,350,255,350,335,2,4,'wartość ?')+probes(s,385);
    out+=pill(40,525,m.discarded?'wynik: odrzucony':'wynik: niezatwierdzony',m.discarded?C.red:C.amber,330)+pill(410,525,m.cached?'cache: zmieniony':'cache: bez śladu',m.cached?C.green:C.muted,330);
    out+=text(40,590,m.revealed?'Pomiar pozwala wnioskować o wartości 2.':'Sekret pozostaje zasłonięty. Najpierw sprawdźmy ślad.',26,C.ink);
  } else if(phase==='decode') {
    const measured=!!m.measurements;
    const values=Array.isArray(m.measurements?.[0])?m.measurements[2]:m.measurements;
    out=text(40,55,'KTÓRY ODCZYT JEST SZYBSZY?',20,C.green);
    for(let i=0;i<4;i++) {
      const v=values?.[i]||0, x=115+i*285;
      out+=`<rect x="${x}" y="${300-v*22}" width="105" height="${v*22}" rx="7" fill="${v<5?C.green:C.amber}"/>`+text(x+52,335,`probe ${i}`,22,C.muted,'text-anchor="middle"')+text(x+52,300-v*22-15,measured?`${v} j.`:'?',28,v<5?C.green:C.amber,'text-anchor="middle"');
    }
    out+=line(70,302,1120,302)+probes(s,390,true)+text(40,570,m.revealed?'Wniosek z pomiaru: wybrano 2 → sekret ma wartość 2.':'Zatrzymaj się tutaj. Jaki wniosek wyciągasz z czasów?',27,m.revealed?C.green:C.ink);
    if(s.diagram.noise) out+=text(40,90,'Serie: [2,9,8,9] → [9,8,3,10] → [8,9,2,9]',23,C.amber);
  } else if(phase==='compare') {
    out=card(40,50,535,255,'SPECTRE v1','zła ścieżka',C.amber,'sprawdzenie zakresu w kodzie ofiary')+card(610,50,530,255,'ORYGINALNY MELTDOWN','złe uprawnienia',C.blue,'odczyt narusza ochronę pamięci');
    out+=line(300,315,480,390)+line(870,315,700,390)+box(310,405,570,120,C.green)+text(595,454,'WSPÓLNY KANAŁ',20,C.muted,'text-anchor="middle"')+text(595,496,'wartość → cache → czas',29,C.green,'text-anchor="middle"');
    out+=text(40,580,'Podobny ślad. Inna przyczyna.',32);
  } else if(phase==='defenses') {
    out=chain(['przejściowy odczyt','zależny adres','ślad w cache','obserwacja'],3,100);
    out+=card(40,330,345,215,'SPECTRE v1','kod + platforma',C.green,'bariery i ograniczanie indeksów')+card(415,330,345,215,'MELTDOWN','izolacja mapowań',C.blue,'KPTI + poprawki sprzętu')+card(790,330,350,215,'WARSTWY OCHRONY','aktualizacje',C.amber,'system, firmware, przeglądarka');
    out+=text(40,595,'Ochrona musi przerwać konkretny etap. Szczegóły zależą od wariantu.',24,C.muted);
  } else {
    out=text(40,90,'ZAPAMIĘTAJ TĘ ZALEŻNOŚĆ',20,C.green)+chain(['wartość','adres','cache','czas'],3,155)+text(40,410,'Wynik może zniknąć.',45)+text(40,475,'Ślad może zostać.',45,C.green)+text(40,565,'Pytania? Możemy wrócić do dowolnego kroku.',26,C.muted);
  }
  return `<svg viewBox="0 0 1180 640" role="img" aria-label="${esc(s.title)}. ${esc(s.subtitle)}" xmlns="http://www.w3.org/2000/svg"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10" fill="none" stroke="${C.muted}" stroke-width="1.5"/></marker></defs>${out}</svg>`;
}
