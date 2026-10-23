import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {scene} from '../src/live_explain/web/scene.js';
const snapshots=JSON.parse(execFileSync(process.env.PYTHON||'python3',['-c',`
import sys,json
sys.path.insert(0,'src')
from live_explain.web_server import WebHost
h=WebHost();out=[]
for b in h.session.presentation.beats.values():
 h.session._entry(b.id)
 times=sorted(set(b.holds)|{(a+b)/2 for a,b in zip(b.holds,b.holds[1:])})
 for t in times:
  h.session.seek(t);out.append(h.audience())
print(json.dumps(out))
`],{cwd:new URL('..',import.meta.url),maxBuffer:4*1024*1024}).toString());
test('every authored beat renders at every hold and midpoint with finite SVG geometry',()=>{
  assert.equal(new Set(snapshots.map(s=>s.beat)).size,58);
  for(const s of snapshots){
    const svg=scene(s);
    assert.ok(svg.startsWith('<svg'),s.beat);
    assert.ok(!/undefined|NaN|Infinity/.test(svg),s.beat);
    assert.ok(!/<script|onload=/.test(svg),s.beat);
    for(const match of svg.matchAll(/(?:height|width|r)="(-?\d+(?:\.\d+)?)"/g))assert.ok(Number(match[1])>=0,s.beat);
  }
});
test('secret label stays concealed throughout Spectre and appears at the authored decode reveal',()=>{
  for(const s of snapshots.filter(s=>s.beat==='normal.spectre')) {
    assert.ok(!scene(s).includes('sekret ma wartość 2'));
    assert.equal(s.model.probe,null);
  }
  const before=snapshots.find(s=>s.beat==='normal.decode'&&s.position===2);
  const after=snapshots.find(s=>s.beat==='normal.decode'&&s.position===4);
  assert.ok(scene(before).includes('Jaki wniosek'));
  assert.ok(scene(after).includes('sekret ma wartość 2'));
});
test('authored text is escaped before being inserted into SVG',()=>{
  const s=structuredClone(snapshots[0]);
  s.title='" onload="alert(1)<script>';
  assert.ok(scene(s).includes('&lt;script&gt;'));
  assert.ok(!scene(s).includes('<script>'));
});
