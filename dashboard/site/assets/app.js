/* ICLR 2027 Atlas: one script for both pages (overview / AI safety) and both languages.
   Data arrive as globals from assets/*.js: ATLAS_CORE (numbers), ATLAS_TEXT (one language),
   and on each page its paper list (ATLAS_PAPERS27 or ATLAS_SAFETY_PAPERS). */
(function(){
const C = window.ATLAS_CORE, X = window.ATLAS_TEXT, U = X.ui, T = X.text;
const B = document.body, PAGE = B.dataset.page, LANG = document.documentElement.lang === 'en' ? 'en' : 'zh', ZH = LANG === 'zh';
const L = (k, vars) => { let v = U[k] ?? k; if (vars) for (const [a,b] of Object.entries(vars)) v = v.replace('{'+a+'}', b); return v; };
const $ = s => document.querySelector(s);
const el = (tag, attrs={}, ...kids) => { const e = document.createElement(tag);
  for (const [k,v] of Object.entries(attrs)) { if (v==null) continue; if (k==='class') e.className=v; else if (k==='text') e.textContent=v; else if (k==='html') e.innerHTML=v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); }
  for (const k of kids.flat()) if (k!=null) e.append(k.nodeType ? k : document.createTextNode(k)); return e; };
const NS='http://www.w3.org/2000/svg';
const s = (tag, attrs={}) => { const e=document.createElementNS(NS,tag); for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,v); return e; };
const OR = id => 'https://openreview.net/forum?id=' + encodeURIComponent(id);
const fmt = (v, d=1) => v==null||isNaN(v) ? '—' : Number(v).toFixed(d);
const fmtInt = v => Number(v).toLocaleString('en-US');
const ratio = (a,b,eps=0.5) => (b+eps)/(a+eps);
const esc = t => String(t??'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const trunc = (t,n) => t.length>n ? t.slice(0,n-1)+'…' : t;
const textW = (t, px) => [...String(t)].reduce((w,ch) => w + (/[⺀-鿿＀-￯]/.test(ch) ? px : px*0.56), 0);
const pct = v => (v*100).toFixed(0)+'%';
const short = t => (t||'').split(/[：:]/)[0];

/* names in the current language */
const THEME = Object.fromEntries(Object.entries(U.themes).map(([k,v]) => [k, v]));
const SUBN = U.subs, TGT = U.targets, TYP = U.types, TAG = U.tags;
const CL = C.clusters, CT = X.clusterText || {};
const cname = c => ZH ? c.name_zh : (c.name_en || c.name_zh);
const cdesc = c => (CT[c.cluster] || {}).desc || '';
const ctrend = c => (CT[c.cluster] || {}).trend || '';
const conceptName = c => ZH ? c.zh : c.en;
const areaName = a => ZH ? (a.zh || a.area) : a.area.charAt(0).toUpperCase() + a.area.slice(1);
const groupName = g => (U.conceptGroups[g] || g);

/* tooltip */
const tip = $('#tip');
function showTip(ev, html){ tip.innerHTML = html; tip.style.opacity = 1; const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = ev.clientX + 14, y = ev.clientY + 14; if (x + w > innerWidth - 8) x = ev.clientX - w - 14; if (y + h > innerHeight - 8) y = ev.clientY - h - 14; tip.style.left = Math.max(8,x)+'px'; tip.style.top = Math.max(8,y)+'px'; }
function hideTip(){ tip.style.opacity = 0; }
let ROBUST = true; const sh = o => (ROBUST && o.share_r) ? o.share_r : o.share;
const badge = (x, digits=2) => el('span',{class:'badge '+(x>=1.15?'up':x<0.87?'dn':'nt'),text:x.toFixed(digits)+'×'});
const tagBadge = t => el('span',{class:'badge '+({rising:'up',fading:'dn'}[t]||(['shift','watch','gap'].includes(t)?'th':'nt')),text:TAG[t]||t||''});
function refs(ev){ if (!ev || !ev.length) return null; return el('ul',{class:'refs'}, ev.map(p => el('li',{}, el('span',{class:'y',text:String(p.year||'')}), el('a',{href:OR(p.id),target:'_blank',rel:'noopener',text:p.title||p.id})))); }
function niceTicks(max, n){ const step0 = max / n; const mag = Math.pow(10, Math.floor(Math.log10(step0))); const st = [1,2,2.5,5,10].map(m=>m*mag).find(v => v >= step0) || step0; const out=[]; for (let v=0; v<=max+1e-9; v+=st) out.push(+v.toFixed(6)); return out; }
const halo = t => { t.style.fill='var(--text)'; t.style.paintOrder='stroke'; t.style.stroke='var(--halo)'; t.style.strokeWidth='3px'; return t; };
const otherPage = PAGE === 'main' ? B.dataset.safety : B.dataset.main;

/* header */
$('#byline').textContent = T.byline;
$('#links').append(...T.links.map(l => el('a',{href:l.href,target:'_blank',rel:'noopener'}, l.text)));
$('#foot').innerHTML = T.footer;

/* footnotes */
const FN = [];
function fnAdd(text, grp, back){ const i = FN.findIndex(f => f.text===text && f.grp===grp); if (i>=0) return i+1; FN.push({text, grp, back}); return FN.length; }
function supN(n){ return el('sup',{class:'fn'}, el('a',{href:'#fn-'+n, id:'fnr-'+n, title:L('fnTitle')+' '+n}, String(n))); }
function rich(str, grp, back){ const frag = document.createDocumentFragment(); const parts = String(str||'').split(/\{\{fn:([\s\S]*?)\}\}/);
  parts.forEach((p,i) => { if (i%2===0) { const sp = document.createElement('span'); sp.innerHTML = p; while (sp.firstChild) frag.append(sp.firstChild); } else frag.append(supN(fnAdd(p, grp, back))); }); return frag; }
function richEl(tag, str, attrs={}, grp, back){ const e = el(tag, attrs); e.append(rich(str, grp, back)); return e; }

/* charts */
function dumbbell(host, rows, {unit='', labelW=220, rowH=26} = {}){
  host.innerHTML=''; const W = Math.max(320, host.clientWidth || 800); const narrow = W < 560; const lw = narrow ? Math.min(140, W*0.4) : labelW;
  const H = rows.length*rowH + 30; const x0 = lw + 12, x1 = W - 52;
  const vmax = Math.max(...rows.flatMap(r => [r.a, r.b, r.c ?? 0])) * 1.04;
  const X = v => x0 + (x1-x0) * (v / vmax);
  const svg = s('svg',{viewBox:`0 0 ${W} ${H}`, width:'100%', role:'img'});
  const g = s('g',{class:'axis'}); niceTicks(vmax, narrow?3:5).forEach(t => { g.append(s('line',{x1:X(t),x2:X(t),y1:4,y2:H-22})); const tx=s('text',{x:X(t),y:H-6,'text-anchor':'middle'}); tx.textContent = t + unit; g.append(tx); });
  svg.append(g);
  const maxChars = narrow ? (ZH?13:22) : (ZH?28:Math.floor(lw/6.4));
  rows.forEach((r,i) => { const y = 14 + i*rowH; const up = r.b >= r.a; const col = up ? 'var(--hot)' : 'var(--down)';
    const row = s('g',{});
    const lab = s('text',{x:lw,y:y+4,'text-anchor':'end'}); lab.textContent = trunc(r.label, maxChars); lab.style.fill='var(--text)'; row.append(lab);
    row.append(s('line',{x1:X(Math.min(r.a,r.b)),x2:X(Math.max(r.a,r.b)),y1:y,y2:y,stroke:col,'stroke-width':2,'stroke-linecap':'round',opacity:.45}));
    if (r.c!=null) row.append(s('circle',{cx:X(r.c),cy:y,r:3,fill:'var(--y25)'}));
    row.append(s('circle',{cx:X(r.a),cy:y,r:4.2,fill:'var(--y26)',stroke:'var(--halo)','stroke-width':1.5}));
    row.append(s('circle',{cx:X(r.b),cy:y,r:4.8,fill:col,stroke:'var(--halo)','stroke-width':1.5}));
    const vt = s('text',{y:y+4,'font-size':11}); vt.textContent = fmt(r.b, r.b<10?2:1); vt.style.fill='var(--text-light)';
    if (up) { vt.setAttribute('x', Math.min(W-4, X(r.b)+9)); if (X(r.b)+9 > W-38) vt.setAttribute('text-anchor','end'); }
    else { const lx = X(r.b)-9; if (lx - 32 > x0 && (r.c==null || X(r.c) > X(r.b) || X(r.b)-X(r.c) > 40)) { vt.setAttribute('x', lx); vt.setAttribute('text-anchor','end'); } else vt.setAttribute('x', Math.min(W-4, X(r.a)+9)); }
    row.append(vt);
    const hit = s('rect',{x:0,y:y-rowH/2,width:W,height:rowH,fill:'transparent'});
    hit.addEventListener('mousemove', ev => showTip(ev, r.tipHtml || `<b>${esc(r.label)}</b><br>${r.c!=null?`2025 ${fmt(r.c,2)}${unit} · `:''}2026 ${fmt(r.a,2)}${unit} → 2027 <b>${fmt(r.b,2)}${unit}</b>`));
    hit.addEventListener('mouseleave', hideTip); row.append(hit); svg.append(row); });
  host.append(svg);
}
function spark(vals, {w=78,h=22,color='var(--hot)'}={}){ const svg = s('svg',{viewBox:`0 0 ${w} ${h}`,width:w,height:h,style:'vertical-align:middle'}); const mx = Math.max(...vals, 1e-9);
  const pts = vals.map((v,i) => [4 + i*(w-8)/(vals.length-1), h-4 - (h-8)*v/mx]);
  svg.append(s('polyline',{points:pts.map(p=>p.join(',')).join(' '),fill:'none',stroke:color,'stroke-width':1.6,'stroke-linejoin':'round','stroke-linecap':'round'}));
  pts.forEach((p,i)=>svg.append(s('circle',{cx:p[0],cy:p[1],r:i===pts.length-1?2.8:1.8,fill:i===pts.length-1?color:'var(--y26)'}))); return svg; }
function kpiRow(host, list, grp, back){ host.append(...list.map(k => el('div',{class:'kpi'}, el('div',{class:'k',text:k.label}), el('div',{class:'v',html:esc(k.value)+(k.unit?`<small>${esc(k.unit)}</small>`:'')}), el('div',{class:'d'}, rich(k.note||'', grp, back))))); }
function crosslink(host, text, href, label){ host.append(el('div',{class:'crosslink'}, el('span',{text}), el('a',{href},'→ '+label))); }

/* ids quoted in prose become small links */
const IDT = X.idTitles || {};
const pidLink = id => el('a',{class:'pid',href:OR(id),target:'_blank',rel:'noopener',title:IDT[id]||id}, '↗');
function tx(str){ if (!str) return []; const out = []; const re = /[（(]\s*([A-Za-z0-9_\-]{10}(?:\s*[，,、;；]\s*[A-Za-z0-9_\-]{10})*)\s*[)）]|\b([A-Za-z0-9_\-]{10})\b/g; let last = 0, m;
  while ((m = re.exec(str))) { const ids = m[1] ? m[1].split(/\s*[，,、;；]\s*/) : [m[2]]; if (!ids.every(i => i in IDT)) continue;
    out.push(str.slice(last, m.index)); ids.forEach(i => out.push(pidLink(i))); last = re.lastIndex; }
  out.push(str.slice(last)); return out.filter(x => x!==''); }

/* chapters (domains and safety deep dives) */
function prepChapter(ch, grp, anchor){ const nz = ch.notes_zh||[]; ch._fn = {ch: nz.length ? [fnAdd(nz.join('<br>'), grp, anchor)] : [], ins: (ch.insights||[]).map(i => i.note_zh ? fnAdd(i.note_zh, grp, anchor) : 0)}; }
function chapter(ch){ const w = el('div',{});
  w.append(el('h3',{text:ch.title_zh, style:'margin-top:1.5rem'}, ...(ch._fn?.ch||[]).map(supN)));
  if (ch.subtitle_zh) w.append(el('div',{class:'ch-sub',text:ch.subtitle_zh}));
  if (ch.headline_zh) w.append(el('div',{class:'callout'}, el('span',{}, ...tx(ch.headline_zh))));
  if (ch.stats?.length) { const t = el('table',{class:'rt'}); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('metric')}), el('th',{text:'2026 → 2027'}), el('th',{class:'l',text:''})))); const tb=el('tbody'); ch.stats.forEach(st => tb.append(el('tr',{}, el('td',{class:'l',style:'min-width:150px',text:st.label_zh}), el('td',{style:'white-space:nowrap;font-weight:600',text:st.value}), el('td',{class:'l light',text:st.note_zh||''})))); t.append(tb); w.append(el('div',{class:'table-wrap'}, t)); }
  (ch.insights||[]).forEach((i,k) => { const n = ch._fn?.ins?.[k]; w.append(el('div',{class:'insight'}, el('div',{class:'meta'}, tagBadge(i.tag)), el('h4',{text:i.title_zh}), el('p',{}, ...tx(i.body_zh), n?supN(n):null), refs(i.evidence))); });
  const mt = (title, rows, a, b, unit) => { const t = el('table',{class:'rt'}); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:title}), el('th',{text:'2026'}), el('th',{text:'2027'}), el('th',{text:L('colRatio')})))); const tb=el('tbody'); rows.forEach(r => tb.append(el('tr',{}, el('td',{class:'l'}, el('span',{text:r.name_zh}), r.note_zh?el('span',{class:'sub',text:r.note_zh}):null), el('td',{text:r[a]}), el('td',{text:r[b]}), el('td',{}, badge(unit==='n' ? ratio(+r[a]/C.meta.totals['2026'], +r[b]/C.meta.totals['2027'], 0.5/C.meta.totals['2026']) : ratio(+r[a],+r[b],1)))))); t.append(tb); return el('div',{class:'table-wrap'}, t); };
  if (ch.rising?.length || ch.fading?.length) { w.append(el('h4',{text:L('risersFallers'),style:'margin-top:2rem'})); const g = el('div',{class:'grid2'}); if (ch.rising?.length) g.append(mt(L('risingPer10k'), ch.rising, 'from', 'to')); if (ch.fading?.length) g.append(mt(L('fallingPer10k'), ch.fading, 'from', 'to')); w.append(g); }
  if (ch.microtopics?.length) { w.append(el('h4',{text:L('specificProblems'),style:'margin-top:2rem'})); w.append(mt(L('problemN'), ch.microtopics, 'n26', 'n27', 'n')); w.append(el('p',{class:'table-caption',text:L('ratioNote')})); }
  const lists = [['frontline', ch.frontline_zh], ['rewarded', ch.rewarded_2026_zh ? [ch.rewarded_2026_zh] : null], ['gaps', ch.gaps_zh], ['watch', ch.watchlist_zh]];
  lists.forEach(([k, arr]) => { if (arr?.length) { w.append(el('h4',{text:L(k),style:'margin-top:2rem'})); w.append(arr.length===1 && k==='rewarded' ? el('p',{class:'prose'}, ...tx(arr[0])) : el('ul',{class:'dots'}, arr.map(x=>el('li',{}, ...tx(x))))); } });
  return w; }
const SUBTAB = {};
function subtabs(tabHost, bodyHost, chapters, group){ let cur = chapters[0]?.key; if (!cur) { bodyHost.append(el('p',{class:'light',text:L('noChapter')})); return; }
  const render = () => { bodyHost.innerHTML=''; bodyHost.append(chapter(chapters.find(c=>c.key===cur))); [...tabHost.children].forEach(b => b.classList.toggle('on', b.dataset.k===cur)); };
  chapters.forEach(c => tabHost.append(el('button',{type:'button',role:'tab','data-k':c.key,onclick:()=>{cur=c.key; render();}}, short(c.title_zh))));
  SUBTAB[group] = k => { cur = k; render(); tabHost.scrollIntoView({block:'start',behavior:'smooth'}); };
  render(); }

const DRAW = {}, REDRAW = [];

/* ================= OVERVIEW PAGE ================= */
if (PAGE === 'main') {
  function redrawRobust(){ drawThemes(); drawScatter(); drawQuad(); drawClTable(); drawMovers(); drawRadar(); }
  function initRobust(){ document.querySelectorAll('.robustSeg').forEach(seg => { if (seg.children.length) return; [[true,L('robustOn')],[false,L('robustOff')]].forEach(([v,n]) => seg.append(el('button',{type:'button',class:v===ROBUST?'on':'',onclick:()=>{ ROBUST=v; document.querySelectorAll('.robustSeg').forEach(sg=>[...sg.children].forEach((bt,i)=>bt.classList.toggle('on', (i===0)===ROBUST))); redrawRobust(); }}, n))); });
    ['#robustNote1','#robustNote2'].forEach(id => { const e=$(id); if (e && !e.childNodes.length) e.append(rich(T.robustNote || '', L('scope'), '#p-landscape')); }); }

  DRAW.summary = () => {
    T.summary.forEach(p => $('#summary').append(richEl('p', p, {}, L('pSummary'), '#p-summary')));
    kpiRow($('#kpis'), T.kpis, L('pSummary'), '#kpis');
    const SAFE_REFS = ['p-safety','sf-thesis','sf-subs'];
    $('#findings').append(...T.findings.map(f => { const toSafety = SAFE_REFS.includes(f.ref); const href = toSafety ? otherPage + (f.ref==='p-safety'?'':'#'+f.ref) : '#'+f.ref;
      return el('li',{}, richEl('div', f.title, {class:'ft'}), richEl('p', f.body, {class:'fb'}, L('pSummary'), '#findings'), f.fig?richEl('div', f.fig, {class:'ff'}, L('pSummary'), '#findings'):null, f.ref?el('a',{class:'fl',href,text:'→ '+(f.refText||L('seeMore'))}):null); }));
    crosslink($('#p-summary'), L('otherPageMain'), otherPage, L('seeSafety'));
  };

  const themeKeys = Object.keys(THEME); let mapTheme='all';
  var drawThemes = () => dumbbell($('#themeChart'), C.themes.filter(t=>t.theme).map(t => ({label: THEME[t.theme]||t.theme, c:sh(t)[0], a:sh(t)[1], b:sh(t)[2]})).sort((p,q)=>q.b-p.b), {unit:'%', labelW: ZH?200:240});
  var drawAreas = () => dumbbell($('#areaChart'), C.areas.map(a => ({label:areaName(a), c:a.share[0], a:a.share[1], b:a.share[2], tipHtml:`<b>${esc(areaName(a))}</b>${ZH?'<br>'+esc(a.area):''}<br>2025 ${a.share[0]}% · 2026 ${a.share[1]}% → 2027 <b>${a.share[2]}%</b><br>${L('tipN27')} ${fmtInt(a.n[2])} · ${L('tipAcc26')} ${pct(a.acc26)}`})).sort((p,q)=>(q.b-q.a)-(p.b-p.a)), {unit:'%', labelW: ZH?230:300});
  var drawScatter = () => { const host = $('#clusterScatter'); host.innerHTML=''; const W = Math.max(320, host.clientWidth||900), H = Math.min(560, Math.max(360, W*0.56)); const m = {l:44,r:14,t:26,b:34};
    const Lg = v => Math.log10(v + 2); const vmax = Math.max(...CL.map(c=>Math.max(sh(c)[1],sh(c)[2]))); const lo = Lg(0), hi = Lg(vmax*1.1);
    const X = v => m.l + (W-m.l-m.r)*(Lg(v)-lo)/(hi-lo), Y = v => H-m.b - (H-m.t-m.b)*(Lg(v)-lo)/(hi-lo);
    const svg = s('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%',role:'img'});
    const ax = s('g',{class:'axis'}); [0,5,10,20,50,100,200].filter(t=>t<=vmax*1.1).forEach(t => { ax.append(s('line',{x1:X(t),x2:X(t),y1:m.t,y2:H-m.b})); ax.append(s('line',{x1:m.l,x2:W-m.r,y1:Y(t),y2:Y(t)})); const a=s('text',{x:X(t),y:H-m.b+16,'text-anchor':'middle'}); a.textContent=t; ax.append(a); const b=s('text',{x:m.l-6,y:Y(t)+4,'text-anchor':'end'}); b.textContent=t; ax.append(b); });
    svg.append(ax); svg.append(s('line',{x1:X(0),y1:Y(0),x2:X(vmax*1.1),y2:Y(vmax*1.1),stroke:'var(--text-faint)','stroke-width':1,opacity:.6}));
    const xl=s('text',{x:W-m.r,y:H-4,'text-anchor':'end'}); xl.textContent=L('axis26'); svg.append(xl); const yl=s('text',{x:m.l-6,y:12,'text-anchor':'start'}); yl.textContent=L('axis27'); svg.append(yl);
    const nmax = Math.max(...CL.map(c=>c.n[2]));
    [...CL].sort((a,b)=>b.n[2]-a.n[2]).forEach(c => { const on = (mapTheme==='all' || c.theme===mapTheme) && c.coherence!==1; const up = sh(c)[2] >= sh(c)[1];
      const r = 2.5 + 9*Math.sqrt(c.n[2]/nmax); const dot = s('circle',{cx:X(sh(c)[1]),cy:Y(sh(c)[2]),r, fill: c.coherence===1?'var(--y25)':(up?'var(--hot)':'var(--down)'), 'fill-opacity': on?0.62:0.08, stroke:'var(--halo)','stroke-width':1.2});
      dot.addEventListener('mousemove', ev => showTip(ev, `<b>${esc(cname(c))}</b> · ${esc(THEME[c.theme]||'')}${ZH?'<br>'+esc(c.name_en||''):''}<br>${L('tipPer10k')} 2026 ${sh(c)[1]} → 2027 <b>${sh(c)[2]}</b> (${L('tipAllPapers')} ${c.share[2]}, ${L('tipFormulaic')} ${Math.round((c.high27||0)*100)}%)<br>${L('tipN27')} ${c.n[2]}${c.acc26!=null?` · ${L('tipAcc26')} ${pct(c.acc26)}`:''}<br>${esc(ctrend(c))}`));
      dot.addEventListener('mouseleave', hideTip); svg.append(dot); });
    const lab = CL.filter(c => c.coherence!==1 && (mapTheme==='all'||c.theme===mapTheme)).sort((a,b)=>ratio(b.share[1],b.share[2],3)-ratio(a.share[1],a.share[2],3)).slice(0, mapTheme==='all'?16:10);
    const boxes=[]; lab.forEach(c => { const nm = ZH ? cname(c) : trunc(cname(c), 34); const tw = textW(nm, 11.5) + 4; let x = X(sh(c)[1])+8, y = Y(sh(c)[2])-6, anchor='start'; if (x + tw > W - m.r) { x = X(sh(c)[1]) - 8; anchor='end'; }
      const bx = anchor==='start' ? [x, y-12, x+tw, y+2] : [x-tw, y-12, x, y+2]; if (boxes.some(b => !(bx[2]<b[0]||bx[0]>b[2]||bx[3]<b[1]||bx[1]>b[3]))) return; boxes.push(bx);
      const t = s('text',{x,y,'font-size':11.5,'text-anchor':anchor}); t.textContent=nm; svg.append(halo(t)); });
    host.append(svg); };
  function moverTable(t, rows, title){ t.innerHTML=''; t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:title}), el('th',{text:'2026'}), el('th',{text:'2027'}), el('th',{text:L('colRatio')}))));
    const tb=el('tbody'); rows.forEach(r => tb.append(el('tr',{}, el('td',{class:'l'}, el('span',{text:r.name}), r.sub?el('span',{class:'sub',text:r.sub}):null), el('td',{text:fmt(r.a)}), el('td',{text:fmt(r.b)}), el('td',{}, badge(ratio(r.a,r.b,1)))))); t.append(tb); }
  var drawQuad = () => { const host=$('#quadChart'); host.innerHTML=''; const pts = CL.filter(c=>c.coherence!==1 && c.acc26!=null && c.n[1]>=30); const W=Math.max(320,host.clientWidth||900), H=Math.min(520,Math.max(340,W*0.5)), m={l:44,r:14,t:14,b:34};
    const xs = pts.map(c=>Math.log2(ratio(sh(c)[1],sh(c)[2],1))); const xmn=Math.min(...xs,-2), xmx=Math.max(...xs,2); const ymn=0.05, ymx=Math.max(...pts.map(c=>c.acc26))+0.03;
    const X=v=>m.l+(W-m.l-m.r)*(v-xmn)/(xmx-xmn), Y=v=>H-m.b-(H-m.t-m.b)*(v-ymn)/(ymx-ymn);
    const svg=s('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%'}); const ax=s('g',{class:'axis'});
    [-2,-1,0,1,2,3,4,5].filter(v=>v>=xmn&&v<=xmx).forEach(v=>{ax.append(s('line',{x1:X(v),x2:X(v),y1:m.t,y2:H-m.b})); const t=s('text',{x:X(v),y:H-m.b+16,'text-anchor':'middle'}); t.textContent=(2**v>=1?(2**v)+'×':'1/'+(2**-v)); ax.append(t);});
    [0.1,0.2,0.3,0.4,0.5,0.6].filter(v=>v<=ymx).forEach(v=>{ax.append(s('line',{x1:m.l,x2:W-m.r,y1:Y(v),y2:Y(v)})); const t=s('text',{x:m.l-6,y:Y(v)+4,'text-anchor':'end'}); t.textContent=(v*100)+'%'; ax.append(t);}); svg.append(ax);
    svg.append(s('line',{x1:m.l,x2:W-m.r,y1:Y(C.meta.acc_base26),y2:Y(C.meta.acc_base26),stroke:'var(--text-faint)','stroke-dasharray':'3 3'})); svg.append(s('line',{x1:X(0),x2:X(0),y1:m.t,y2:H-m.b,stroke:'var(--text-faint)','stroke-dasharray':'3 3'}));
    const qw = t => textW(t, 11.5) + 8;
    const ql = [[L('qCrowded'),W-m.r-6,m.t+14,'end'],[L('qNiche'),m.l+6,m.t+14,'start'],[L('qRush'),W-m.r-6,H-m.b-8,'end'],[L('qFade'),m.l+6,H-m.b-8,'start']];
    ql.forEach(([t,x,y,a])=>{const e=s('text',{x,y,'text-anchor':a,'font-size':11.5}); e.textContent=t; e.style.fill='var(--text-faint)'; svg.append(e);});
    pts.forEach(c=>{const x=Math.log2(ratio(sh(c)[1],sh(c)[2],1)); const d=s('circle',{cx:X(x),cy:Y(c.acc26),r:4.2,fill:x>=0?'var(--hot)':'var(--down)','fill-opacity':.6,stroke:'var(--halo)','stroke-width':1.2});
      d.addEventListener('mousemove',ev=>showTip(ev,`<b>${esc(cname(c))}</b><br>${L('tipAcc26')} <b>${pct(c.acc26)}</b> (${c.n[1]} ${L('tipPapers')})${c.rating26?` · ${L('tipMean')} ${c.rating26}`:''}<br>${L('tipShare')} ${sh(c)[1]} → ${sh(c)[2]} ${L('per10kUnit')} (${ratio(sh(c)[1],sh(c)[2],1).toFixed(2)}×)`)); d.addEventListener('mouseleave',hideTip); svg.append(d);});
    const lab=[...pts].sort((a,b)=>Math.abs(b.acc26-C.meta.acc_base26)*Math.abs(Math.log2(ratio(b.share[1],b.share[2],1)))-Math.abs(a.acc26-C.meta.acc_base26)*Math.abs(Math.log2(ratio(a.share[1],a.share[2],1)))).slice(0,14);
    const qb=ql.map(([t,x,y,a])=> a==='end'?[x-qw(t),y-12,x,y+4]:[x,y-12,x+qw(t),y+4]);
    lab.forEach(c=>{const xv=Math.log2(ratio(sh(c)[1],sh(c)[2],1)); const nm = ZH ? cname(c) : trunc(cname(c), 30); const tw=textW(nm,11)+4; let x=X(xv)+7, y=Y(c.acc26)-6, an='start'; if (x+tw>W-m.r){x=X(xv)-7; an='end';} const bx = an==='start'?[x,y-11,x+tw,y+2]:[x-tw,y-11,x,y+2]; if (qb.some(b=>!(bx[2]<b[0]||bx[0]>b[2]||bx[3]<b[1]||bx[1]>b[3]))) return; qb.push(bx);
      const t=s('text',{x,y,'font-size':11,'text-anchor':an}); t.textContent=nm; svg.append(halo(t));});
    host.append(svg); };
  var drawMovers = () => { const good = CL.filter(c => c.coherence !== 1);
    moverTable($('#riseTable'), [...good].sort((a,b)=>(sh(b)[2]-sh(b)[1])-(sh(a)[2]-sh(a)[1])).slice(0,15).map(c=>({name:cname(c), sub:ctrend(c), a:sh(c)[1], b:sh(c)[2]})), L('riseMost'));
    moverTable($('#fallTable'), [...good].sort((a,b)=>(sh(a)[2]-sh(a)[1])-(sh(b)[2]-sh(b)[1])).slice(0,15).map(c=>({name:cname(c), sub:ctrend(c), a:sh(c)[1], b:sh(c)[2]})), L('fallMost')); };
  let clSort = {k:'d', dir:-1};
  var drawClTable = () => { const q = $('#clSearch').value.trim().toLowerCase(), th = $('#clTheme').value;
    let rows = CL.filter(c => (th==='all'||c.theme===th) && (!q || (c.name_zh+' '+c.name_en+' '+cdesc(c)+' '+ctrend(c)).toLowerCase().includes(q)));
    const key = c => ({name:cname(c), theme:c.theme, s26:sh(c)[1], s27:sh(c)[2], d:sh(c)[2]-sh(c)[1], x:ratio(sh(c)[1],sh(c)[2],1), n27:c.n[2], hi:c.high27??0, acc:c.acc26??-1})[clSort.k];
    rows.sort((a,b)=> (key(a)>key(b)?1:-1)*clSort.dir);
    const cols = [['name',L('colCluster'),'l'],['theme',L('colTheme'),'l'],['s26',L('colPer10k26')],['s27',L('colPer10k27')],['d',L('colChange')],['x',L('colRatio')],['n27',L('colN27')],['hi',L('colFormulaic')],['acc',L('colAcc26')],[null,L('colTrend')]];
    const t = $('#clTable'); t.innerHTML='';
    t.append(el('thead',{}, el('tr',{}, cols.map(([k,n,cls]) => el('th',{class:(cls||'')+(k?' sort':''),onclick:k?()=>{clSort = {k, dir: clSort.k===k? -clSort.dir : -1}; drawClTable();}:null}, n + (clSort.k===k?(clSort.dir<0?' ↓':' ↑'):''))))));
    const tb = el('tbody'); rows.forEach(c => { const up = sh(c)[2]>=sh(c)[1];
      const det = el('details',{class:'row'}, el('summary',{text:cname(c)+(c.coherence===1?L('pseudoCluster'):'')}), el('div',{class:'body'}, el('div',{text:(ZH?(c.name_en||'')+' — ':'')+cdesc(c)}), el('div',{style:'margin:.3rem 0;color:var(--text)',text:ctrend(c)}), refs((c.examples||[]).map(e=>({id:e.id,year:2027,title:e.title})))));
      tb.append(el('tr',{}, el('td',{class:'l',style:'min-width:260px;max-width:420px'}, det), el('td',{class:'l light',style:'white-space:nowrap',text:THEME[c.theme]||c.theme}), el('td',{text:fmt(sh(c)[1])}), el('td',{text:fmt(sh(c)[2])}), el('td',{style:`color:${up?'var(--up-fg)':'var(--dn-fg)'}`,text:(up?'+':'')+fmt(sh(c)[2]-sh(c)[1])}), el('td',{}, badge(ratio(sh(c)[1],sh(c)[2],1))), el('td',{text:c.n[2]}), el('td',{style:(c.high27>=0.75?'color:var(--dn-fg);font-weight:600':''),text:c.high27!=null?pct(c.high27):'—'}), el('td',{text:c.acc26!=null?pct(c.acc26):'—'}), el('td',{}, spark(sh(c),{color: up?'var(--hot)':'var(--down)'})))); });
    t.append(tb); };
  DRAW.landscape = () => {
    initRobust();
    $('#landIntro').append(rich(T.landIntro,L('pLandscape'),'#p-landscape')); $('#mapIntro').append(rich(T.mapIntro,L('hMap'),'#l-map')); $('#signalIntro').append(rich(T.signalIntro,L('hSignal'),'#l-signal'));
    const seg = $('#mapTheme'); [['all',L('all')], ...themeKeys.map(k=>[k,THEME[k]])].forEach(([k,n]) => seg.append(el('button',{type:'button',class:k===mapTheme?'on':'',onclick:e=>{mapTheme=k; [...seg.children].forEach(b=>b.classList.toggle('on', b===e.target)); drawScatter();}}, n)));
    drawMovers();
    const sel = $('#clTheme'); sel.append(el('option',{value:'all',text:L('allThemes')}), ...themeKeys.map(k => el('option',{value:k,text:THEME[k]})));
    $('#clSearch').addEventListener('input', drawClTable); sel.addEventListener('change', drawClTable);
    drawThemes(); drawScatter(); drawQuad(); drawClTable(); drawAreas(); };

  const CO = C.concepts; const groups = [...new Set(CO.map(c=>c.group))]; let rGroup = groups[0], rSort='x';
  var drawRadar = () => { const t=$('#radarTable'); t.innerHTML=''; let rows = CO.filter(c=>c.group===rGroup);
    rows.sort((a,b)=> rSort==='x' ? ratio(sh(b)[1],sh(b)[2],0.05)-ratio(sh(a)[1],sh(a)[2],0.05) : sh(b)[2]-sh(a)[2]);
    t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('colTech')}), ...['2025','2026','2027','26→27',L('colTrend'),L('colAcc26')].map(h=>el('th',{text:h})))));
    const tb = el('tbody'); rows.forEach(c => { const x = ratio(sh(c)[1],sh(c)[2],0.05);
      tb.append(el('tr',{class: x>=2?'hl':''}, el('td',{class:'l'}, el('span',{text:conceptName(c)}), ZH?el('span',{class:'sub',text:c.en}):null), ...sh(c).map(v=>el('td',{text:v<1?v.toFixed(2)+'%':v.toFixed(1)+'%'})), el('td',{}, badge(x)), el('td',{}, spark(sh(c),{color: x<0.87?'var(--down)':'var(--hot)'})), el('td',{text: c.acc26!=null? pct(c.acc26):'—'}))); });
    t.append(tb); };
  var drawEco = () => { dumbbell($('#modelChart'), C.models.map(m=>({label:m.name,c:m.share[0],a:m.share[1],b:m.share[2]})).sort((a,b)=>b.b-a.b), {unit:'%', labelW:118}); dumbbell($('#benchChart'), C.benchmarks.map(m=>({label:m.name,c:m.share[0],a:m.share[1],b:m.share[2]})).sort((a,b)=>b.b-a.b), {unit:'%', labelW:118}); };
  DRAW.radar = () => {
    initRobust();
    $('#radarIntro').append(rich(T.radarIntro,L('pRadar'),'#p-radar')); $('#ecoIntro').append(rich(T.ecoIntro,L('hEco'),'#r-eco'));
    const segR = $('#radarGroup'); groups.forEach(g => segR.append(el('button',{type:'button',class:g===rGroup?'on':'',onclick:e=>{rGroup=g;[...segR.children].forEach(b=>b.classList.toggle('on',b===e.target));drawRadar();}}, groupName(g))));
    const segS = $('#radarSort'); [['x',L('sortGrowth')],['v',L('sortLevel')]].forEach(([k,n]) => segS.append(el('button',{type:'button',class:k===rSort?'on':'',onclick:e=>{rSort=k;[...segS.children].forEach(b=>b.classList.toggle('on',b===e.target));drawRadar();}}, n)));
    drawRadar(); drawEco();
    [['kw_new',L('kwNew'),L('kwNewCap')],['kw_rise',L('kwRise'),L('kwCap')],['kw_fall',L('kwFall'),L('kwCap')]].forEach(([k,title,cap]) => {
      const t = el('table',{class:'rt'}); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:title}), el('th',{text:'2026'}), el('th',{text:'2027'}))));
      const tb = el('tbody'); (C.kw[k]||[]).slice(0,15).forEach(r => tb.append(el('tr',{}, el('td',{class:'l mono',text:r.kw}), el('td',{text:r.n[1]}), el('td',{text:r.n[2]})))); t.append(tb);
      $('#kwBlocks').append(el('div',{}, el('div',{class:'table-wrap'}, t), el('p',{class:'table-caption',text:cap}))); }); };

  DRAW.domains = () => { $('#domainsIntro').append(rich(T.domainsIntro,L('pDomains'),'#p-domains')); X.domains.forEach(ch => prepChapter(ch, L('pDomains')+' · '+short(ch.title_zh), '#p-domains')); subtabs($('#domainTabs'), $('#domainBody'), X.domains, 'domains'); };

  DRAW.style = () => { const S = X.style; const host = $('#styleBody'); if (!S) { host.append(el('p',{class:'light',text:L('noAnalysis')})); return; }
    const sfn = (S.notes_zh||[]).length ? fnAdd(S.notes_zh.join('<br>'), L('pStyle'), '#p-style') : 0;
    (S.intro_zh||[]).forEach((p,i) => $('#styleIntro').append(el('p',{}, rich(p,L('pStyle'),'#p-style'), (i===0 && sfn) ? supN(sfn) : null)));
    if (S.facts?.length) host.append(el('div',{class:'kpis'}, S.facts.map(f => el('div',{class:'kpi'}, el('div',{class:'k',text:f.label}), el('div',{class:'v',text:f.value}), el('div',{class:'d',text:f.note||''})))));
    if (S.score_hist) { const sec = el('div',{}, el('h3',{'data-nav':L('navHist'),id:'st-hist',text:L('hHist')})); const c = el('div',{id:'histChart'}); sec.append(el('div',{class:'figure'}, el('div',{class:'legend'}, el('span',{html:'<i class="sq" style="background:var(--y26)"></i>2026'}), el('span',{html:'<i class="sq" style="background:var(--hot)"></i>2027'})), c, el('div',{class:'figure-caption',html:`<b>${L('fig')} 10.</b> `+esc(S.hist_caption_zh||L('capHist'))}))); host.append(sec);
      const drawHist = () => { c.innerHTML=''; const bins=S.score_hist.bins, a=S.score_hist['2026'], b=S.score_hist['2027']; const sa=a.reduce((x,y)=>x+y,0), sb=b.reduce((x,y)=>x+y,0); const pa=a.map(v=>v/sa), pb=b.map(v=>v/sb); const W=Math.max(300,c.clientWidth||700),H=260,m={l:42,r:10,t:10,b:30}; const n=pa.length, mx=Math.max(...pa,...pb);
        const svg=s('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%'}); const bw=(W-m.l-m.r)/n; const ax=s('g',{class:'axis'}); niceTicks(mx*100,4).forEach(t=>{const y=H-m.b-(H-m.t-m.b)*(t/100)/mx; ax.append(s('line',{x1:m.l,x2:W-m.r,y1:y,y2:y})); const tx=s('text',{x:m.l-6,y:y+4,'text-anchor':'end'}); tx.textContent=t+'%'; ax.append(tx);}); svg.append(ax);
        for(let i=0;i<n;i++){ const x=m.l+i*bw; [[pa[i],'var(--y26)',0],[pb[i],'var(--hot)',1]].forEach(([v,col,k])=>{const h=(H-m.t-m.b)*v/mx; const r=s('rect',{x:x+1+k*(bw-2)/2,y:H-m.b-h,width:Math.max(1,(bw-2)/2-1),height:h,fill:col,rx:1}); r.addEventListener('mousemove',ev=>showTip(ev,`${L('styleScore')} ${esc(bins[i])}–${esc(bins[i+1]??'')}<br>2026 ${(pa[i]*100).toFixed(2)}% · 2027 <b>${(pb[i]*100).toFixed(2)}%</b>`)); r.addEventListener('mouseleave',hideTip); svg.append(r);}); }
        const lx=s('text',{x:W-m.r,y:H-6,'text-anchor':'end'}); lx.textContent=L('styleScore')+' →'; svg.append(lx); c.append(svg); };
      requestAnimationFrame(drawHist); REDRAW.push(drawHist); }
    if (S.markers?.length) { const t=el('table',{class:'rt'}); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('colMarker')}), el('th',{text:'2025'}), el('th',{text:'2026'}), el('th',{text:'2027'}), el('th',{text:'26→27'})))); const tb=el('tbody'); S.markers.slice(0,20).forEach(mk=>tb.append(el('tr',{}, el('td',{class:'l mono',text:mk.term}), el('td',{text:fmt(mk.r25,1)}), el('td',{text:fmt(mk.r26,1)}), el('td',{text:fmt(mk.r27,1)}), el('td',{}, badge(ratio(mk.r26,mk.r27,0.5),1))))); t.append(tb);
      host.append(el('div',{}, el('h3',{'data-nav':L('navMarkers'),id:'st-markers',text:L('hMarkers')}), el('div',{class:'table-wrap'}, t), el('p',{class:'table-caption',text:S.markers_caption_zh||L('markersCap')}))); }
    (S.sections||[]).forEach((sec,i) => host.append(el('div',{}, el('h3',{'data-nav':sec.nav||sec.title_zh,id:'st-x'+i,text:sec.title_zh}), ...(sec.paras_zh||[]).map(p=>el('p',{class:'prose',html:p})), sec.evidence?refs(sec.evidence):null)));
    if (S.examples?.length) host.append(el('div',{}, el('h3',{'data-nav':L('navExamples'),id:'st-ex',text:L('hExamples')}), el('p',{class:'prose light',text:L('examplesNote')}), refs(S.examples.slice(0,12).map(e=>({id:e.id,year:2027,title:e.title})))));
    if (S.caveat_zh) host.append(el('div',{class:'callout neutral'}, el('span',{text:S.caveat_zh}))); };

  const P27 = window.ATLAS_PAPERS27 || []; const clName = Object.fromEntries(CL.map(c=>[c.cluster,cname(c)]));
  function drawEx(){ const q=($('#exQ')?.value||'').trim().toLowerCase(); const t=$('#exTable'); t.innerHTML=''; const tb=el('tbody'); const LIM=400; const cl=$('#exCl').value;
    const rows = P27.filter(p => (cl==='all'||String(p[2])===cl) && (!q || p[1].toLowerCase().includes(q)));
    t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('colPaper')}), el('th',{class:'l',text:L('colCluster')}))));
    rows.slice(0,LIM).forEach(p => tb.append(el('tr',{}, el('td',{class:'l'}, el('a',{href:OR(p[0]),target:'_blank',rel:'noopener',text:p[1]})), el('td',{class:'l light',text:clName[p[2]]||p[2]}))));
    t.append(tb); $('#exCount').textContent = L('countAll',{n:rows.length.toLocaleString('en-US')}) + (rows.length>LIM?L('countLimit',{lim:LIM}):'') + (ZH?'。':'.'); }
  DRAW.papers = () => { $('#papersIntro').append(rich(T.papersIntro,L('pPapers'),'#p-papers')); const c=$('#exControls');
    c.append(el('input',{class:'search',id:'exQ',placeholder:L('searchAll'),'aria-label':L('searchPapers'),oninput:drawEx}));
    c.append(el('select',{class:'sel',id:'exCl',onchange:drawEx,'aria-label':L('colCluster')}, el('option',{value:'all',text:L('allClusters')}), ...[...CL].sort((a,b)=>b.n[2]-a.n[2]).map(cl=>el('option',{value:cl.cluster,text:`${cname(cl)} (${cl.n[2]})`}))));
    drawEx(); };
  REDRAW.push(() => { drawThemes(); drawScatter(); drawQuad(); drawAreas(); drawEco(); });
}

/* ================= SAFETY PAGE ================= */
if (PAGE === 'safety') {
  const SF = C.safety;
  function stack100(host, obj, order, names){ host.innerHTML=''; const tot = [0,1].map(i => order.reduce((a,k)=>a+(obj[k]?.[i]||0),0));
    const W=Math.max(300,host.clientWidth||500), rowH=34, H=rowH*2+14, lw=40; const svg=s('svg',{viewBox:`0 0 ${W} ${H}`,width:'100%'});
    const pal=['var(--s1)','var(--s2)','var(--s3)','var(--s4)','var(--s5)','var(--s6)','var(--s7)','var(--s8)','var(--y25)'];
    [0,1].forEach(i => { let x=lw; const y=4+i*(rowH+6); const t=s('text',{x:0,y:y+rowH/2+4}); t.textContent=['2026','2027'][i]; svg.append(t);
      order.forEach((k,j) => { const v=(obj[k]?.[i]||0)/tot[i]; const w=(W-lw)*v; if (w<=0) return; const r=s('rect',{x,y,width:Math.max(0,w-2),height:rowH,fill:pal[j%pal.length],rx:2});
        r.addEventListener('mousemove',ev=>showTip(ev,`<b>${esc(names[k]||k)}</b><br>2026 ${(obj[k][0]/tot[0]*100).toFixed(1)}% → 2027 <b>${(obj[k][1]/tot[1]*100).toFixed(1)}%</b><br>${L('tipCount')} ${obj[k][0]} → ${obj[k][1]}`)); r.addEventListener('mouseleave',hideTip); svg.append(r);
        if (w>40){ const lt=s('text',{x:x+6,y:y+rowH/2+4,'font-size':11}); lt.textContent=(v*100).toFixed(0)+'%'; lt.style.fill=j===8?'var(--text)':'#fff'; svg.append(lt);} x+=w; }); });
    host.append(svg); host.append(el('div',{class:'legend'}, order.map((k,j)=>el('span',{html:`<i class="sq" style="background:${pal[j%pal.length]}"></i>${esc(names[k]||k)}`})))); }
  const drawSafetyCharts = () => {
    const rows = SF.subs.filter(r=>r.n[0]+r.n[1]>=12).map(r => ({label:SUBN[r.sub]+(['INTERP_GEN','OOD'].includes(r.sub)?L('adjacent'):''), a:r.share[0], b:r.share[1], tipHtml:`<b>${esc(SUBN[r.sub])}</b> · ${r.sub}<br>${L('tipPer10k')} ${r.share[0]} → <b>${r.share[1]}</b> (${ratio(r.share[0],r.share[1],0.5).toFixed(2)}×)<br>${L('tipCount')} ${r.n[0]} → ${r.n[1]} (${L('tipCore')} ${r.n_core[0]} → ${r.n_core[1]})<br>${L('tipAcc26')} ${r.acc26!=null?pct(r.acc26):'—'}${r.rating26?` · ${L('tipMean')} ${r.rating26}`:''}`}));
    rows.sort((a,b)=>ratio(b.a,b.b,0.5)-ratio(a.a,a.b,0.5)); dumbbell($('#subChart'), rows, {labelW: ZH?220:280});
    stack100($('#targetChart'), SF.target, Object.keys(TGT).filter(k=>SF.target[k]), TGT); stack100($('#typeChart'), SF.type, Object.keys(TYP).filter(k=>SF.type[k]), TYP); };
  DRAW.summary = () => {
    T.safetyIntro.forEach(p => $('#safetyIntro').append(richEl('p', p, {}, L('pSafetySummary'), '#p-summary')));
    const N = T.nest; let inner = null;
    [...N].reverse().forEach((b,i) => { const box = el('div',{class:'box b'+(N.length-i)}, el('div',{class:'lbl'}, el('div',{class:'n',text:b.n}), el('div',{class:'t',text:b.t}))); if (inner) box.append(inner); inner = box; });
    $('#nest').append(inner); $('#nestCap').append(rich(T.nestCaption, L('fig')+' 0', '#nest'));
    kpiRow($('#safetyKpis'), T.safetyKpis, L('pSafetySummary'), '#safetyKpis');
    crosslink($('#p-summary'), L('otherPageSafety'), otherPage, L('seeMain'));
  };
  DRAW.thesis = () => { const th = X.safetyThesis; const tb = $('#thesisBody'); if (!th) { tb.append(el('p',{class:'light',text:L('noThesis')})); return; }
    const tn=(th.notes_zh||[]).length?fnAdd(th.notes_zh.join(' '),L('pThesis'),'#sf-thesis'):0; if (th.intro_zh) tb.append(el('p',{class:'prose'}, th.intro_zh, tn?supN(tn):null));
    (th.theses||[]).forEach((i,k) => { const n = i.note_zh ? fnAdd(i.note_zh, L('pThesis')+' · '+(k+1), '#sf-thesis') : 0; tb.append(el('div',{class:'insight'}, el('div',{class:'meta'}, tagBadge(i.tag||'shift')), el('h4',{text:`${k+1}. ${i.title_zh}`}), el('p',{}, ...tx(i.body_zh), n?supN(n):null), i.fig?el('p',{class:'light',style:'font-size:.84rem;margin-top:-.2rem',text:i.fig}):null, refs(i.evidence))); }); };
  DRAW.subs = () => {
    drawSafetyCharts();
    const st = el('tbody'); [...SF.subs].sort((a,b)=>ratio(b.share[0],b.share[1],0.5)-ratio(a.share[0],a.share[1],0.5)).forEach(r => { const x = ratio(r.share[0],r.share[1],0.5); const acc = r.acc26; st.append(el('tr',{class: acc!=null && acc>=0.32 ? 'hl':''}, el('td',{class:'l',text:SUBN[r.sub]}), el('td',{class:'l mono light',text:r.sub}), el('td',{text:r.n[0]}), el('td',{text:r.n[1]}), el('td',{text:fmt(r.share[0])}), el('td',{text:fmt(r.share[1])}), el('td',{}, badge(x)), el('td',{style: acc!=null&&acc<0.2?'color:var(--dn-fg)':(acc>=0.32?'color:var(--up-fg);font-weight:600':''),text: acc!=null?pct(acc):'—'}))); });
    const t = $('#subTable'); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('colSub')}), el('th',{class:'l',text:L('colCode')}), el('th',{text:L('colN26')}), el('th',{text:L('colN27')}), el('th',{text:L('colPer10k26')}), el('th',{text:L('colPer10k27')}), el('th',{text:L('colRatio')}), el('th',{text:L('colAcc26')})))); t.append(st);
    const h27=SF.heat['2027'], h26=SF.heat['2026']; const subs=SF.subs.filter(r=>r.n[1]>=15).map(r=>r.sub); const tg=Object.keys(TGT); const mx=Math.max(...subs.flatMap(sb=>tg.map(k=>h27[sb]?.[k]||0)));
    const ht=el('table',{class:'rt'}); ht.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:L('colSub')}), tg.map(k=>el('th',{style:'text-align:center',text:TGT[k]})))));
    const hb=el('tbody'); subs.forEach(sb=>{ const tr=el('tr',{}, el('td',{class:'l',style:'white-space:nowrap',text:SUBN[sb]})); tg.forEach(k=>{ const v=h27[sb]?.[k]||0, v6=h26[sb]?.[k]||0; const a=v?0.06+0.7*Math.sqrt(v/mx):0; const td=el('td',{style:`text-align:center;background:rgba(var(--heat),${a.toFixed(3)});color:${a>0.42?'#fff':'var(--text)'}`,text:v||''}); td.addEventListener('mousemove',ev=>showTip(ev,`<b>${esc(SUBN[sb])}</b> × ${esc(TGT[k])}<br>2026 ${v6} → 2027 <b>${v}</b> ${L('tipPapers')}`)); td.addEventListener('mouseleave',hideTip); tr.append(td); }); hb.append(tr); }); ht.append(hb); $('#heat').append(ht);
    const rows=[]; (X.safetyChapters||[]).forEach(ch => (ch.microtopics||[]).forEach(m => rows.push({...m, ch: short(ch.title_zh)})));
    rows.forEach(r => { r.s26 = +r.n26 / C.meta.totals['2026'] * 1e4; r.s27 = +r.n27 / C.meta.totals['2027'] * 1e4; }); rows.sort((a,b) => (b.s27 - b.s26) - (a.s27 - a.s26));
    const mk = (title, list) => { const t=el('table',{class:'rt'}); t.append(el('thead',{}, el('tr',{}, el('th',{class:'l',text:title}), el('th',{text:'2026'}), el('th',{text:'2027'}), el('th',{text:L('shareRatio')})))); const b=el('tbody'); list.forEach(r=>b.append(el('tr',{}, el('td',{class:'l'}, el('span',{text:r.name_zh}), el('span',{class:'sub',text:r.ch+(r.note_zh?' · '+r.note_zh:'')})), el('td',{text:r.n26}), el('td',{text:r.n27}), el('td',{}, badge(ratio(r.s26,r.s27,0.3)))))); t.append(b); return el('div',{class:'table-wrap'}, t); };
    if (rows.length) $('#microBody').append(mk(L('microUp'), rows.slice(0,15)), mk(L('microDown'), [...rows].reverse().filter(r=>r.s27<r.s26).slice(0,15))); };
  DRAW.chapters = () => { X.safetyChapters.forEach(ch => prepChapter(ch, 'AI Safety · '+short(ch.title_zh), '#sf-ch')); subtabs($('#safetyTabs'), $('#safetyBody'), X.safetyChapters, 'safety'); };

  const SP = window.ATLAS_SAFETY_PAPERS || [];
  const STATUS = {accept_oral:'Oral',accept_spotlight:'Spotlight',accept_poster:'Poster',reject:'Reject',withdrawn:'Withdrawn',desk_rejected:'Desk reject',active:''};
  function drawEx(){ const q=($('#exQ')?.value||'').trim().toLowerCase(); const t=$('#exTable'); t.innerHTML=''; const tb=el('tbody'); const LIM=400;
    const y=$('#exYear').value, sb=$('#exSub').value, tg=$('#exTgt').value, ty=$('#exType').value, rel=+$('#exRel').value;
    const rows = SP.filter(p => (y==='all'||String(p[1])===y) && (sb==='all'||p[3]===sb||p[4]===sb) && (tg==='all'||p[6]===tg) && (ty==='all'||p[5]===ty) && p[7]>=rel && (!q || (p[2]+' '+p[8]).toLowerCase().includes(q)));
    t.append(el('thead',{}, el('tr',{}, [L('year'),L('colPaper'),L('colSub'),L('colTarget'),L('colType'),L('colProblem'),L('colResult26')].map((h,i)=>el('th',{class:i===0||i===6?'':'l',text:h})))));
    rows.slice(0,LIM).forEach(p => tb.append(el('tr',{}, el('td',{text:p[1]}), el('td',{class:'l',style:'min-width:260px'}, el('a',{href:OR(p[0]),target:'_blank',rel:'noopener',text:p[2]})), el('td',{class:'l',style:'white-space:nowrap',text:SUBN[p[3]]||p[3]}), el('td',{class:'l light',style:'white-space:nowrap',text:TGT[p[6]]||p[6]}), el('td',{class:'l light',style:'white-space:nowrap',text:TYP[p[5]]||p[5]}), el('td',{class:'l light',style:'min-width:170px',text:p[8]}), el('td',{}, p[9]&&STATUS[p[9]]?el('span',{class:'badge '+(p[9].startsWith('accept')?'up':'nt'),text:STATUS[p[9]]}):null))));
    t.append(tb); $('#exCount').textContent = L('countAll',{n:rows.length.toLocaleString('en-US')}) + (rows.length>LIM?L('countLimit',{lim:LIM}):'') + (ZH?'。':'.'); }
  DRAW.papers = () => { const c=$('#exControls');
    c.append(el('input',{class:'search',id:'exQ',placeholder:L('searchSafety'),'aria-label':L('searchPapers'),oninput:drawEx}));
    c.append(el('select',{class:'sel',id:'exYear',onchange:drawEx,'aria-label':L('year')}, el('option',{value:'all',text:L('bothYears')}), el('option',{value:'2027',text:'2027'}), el('option',{value:'2026',text:'2026'})));
    c.append(el('select',{class:'sel',id:'exSub',onchange:drawEx,'aria-label':L('colSub')}, el('option',{value:'all',text:L('allSubs')}), ...Object.keys(SUBN).map(k=>el('option',{value:k,text:SUBN[k]}))));
    c.append(el('select',{class:'sel',id:'exTgt',onchange:drawEx,'aria-label':L('colTarget')}, el('option',{value:'all',text:L('allTargets')}), ...Object.keys(TGT).map(k=>el('option',{value:k,text:TGT[k]}))));
    c.append(el('select',{class:'sel',id:'exType',onchange:drawEx,'aria-label':L('colType')}, el('option',{value:'all',text:L('allTypes')}), ...Object.keys(TYP).map(k=>el('option',{value:k,text:TYP[k]}))));
    c.append(el('select',{class:'sel',id:'exRel',onchange:drawEx,'aria-label':L('coreOnly')}, el('option',{value:'2',text:L('coreOnly')}), el('option',{value:'1',text:L('inclAdjacent')})));
    drawEx(); };
  REDRAW.push(drawSafetyCharts);
}

/* notes (both pages) */
DRAW.notes = () => { const b = $('#methodBody'); T.method.forEach(sec => { b.append(el('h4',{text:sec.title})); sec.paras.forEach(p => b.append(el('p',{html:p}))); });
  b.append(el('h4',{text:L('bodyNotes')}));
  $('#fnList').append(...FN.map((f,i) => el('li',{id:'fn-'+(i+1)}, f.grp?el('span',{class:'grp',text:f.grp}):null, el('span',{html:f.text}), el('a',{class:'back',href: document.getElementById('fnr-'+(i+1)) ? '#fnr-'+(i+1) : (f.back||'#top'), 'aria-label':L('backToText'),text:'↩'})))); };

const ORDER = PAGE === 'main' ? ['summary','landscape','radar','domains','style','papers','notes'] : ['summary','thesis','subs','chapters','papers','notes'];
ORDER.forEach(k => { try { DRAW[k] && DRAW[k](); } catch(e) { console.error(k, e); } });

/* table of contents + left section nav */
const parts = [...document.querySelectorAll('section.part')];
const toc = $('#toc'); toc.append(el('div',{class:'toc-h',text:L('toc')}));
const tol = el('ol'); toc.append(tol);
const chapterLinks = PAGE === 'main' ? { 'p-domains': ['domains', X.domains] } : { 'sf-ch': ['safety', X.safetyChapters] };
parts.forEach(p => { const no = p.querySelector('.pno')?.textContent || ''; const kids = [...p.querySelectorAll('h3[data-nav]')].map(h => h.dataset.nav);
  const extra = chapterLinks[p.id] ? chapterLinks[p.id][1].map(c => short(c.title_zh)) : [];
  const sub = extra.length ? extra : kids;
  tol.append(el('li',{}, el('a',{class:'tp',href:'#'+p.id}, el('span',{class:'n',text:no}), el('span',{text:p.dataset.part})), sub.length ? el('span',{class:'ts',text:sub.slice(0,7).join(' · ')}) : null)); });
const nav = $('#sectionNav'); const navTargets = [];
parts.forEach(p => { const pa = el('a',{class:'part',href:'#'+p.id,'data-t':p.id}, p.dataset.part); nav.append(pa); navTargets.push(p);
  const kids = el('div',{class:'kids','data-p':p.id});
  [...p.querySelectorAll('h3[data-nav]')].forEach(h => { if (!h.id) return; kids.append(el('a',{class:'nested',href:'#'+h.id,'data-t':h.id}, h.dataset.nav)); navTargets.push(h); });
  if (chapterLinks[p.id]) { const [g, chs] = chapterLinks[p.id]; chs.forEach(c => kids.append(el('a',{class:'nested',href:'#'+p.id,onclick:e=>{ e.preventDefault(); SUBTAB[g](c.key); }}, '· '+short(c.title_zh)))); }
  nav.append(kids); });
let curPart = null;
const setActive = id => { const t = document.getElementById(id); const p = t?.closest('section.part'); if (!p) return;
  nav.querySelectorAll('a[data-t]').forEach(a => a.classList.toggle('active', a.dataset.t===id || a.dataset.t===p.id));
  if (curPart !== p.id) { curPart = p.id; nav.querySelectorAll('.kids').forEach(k => k.classList.toggle('open', k.dataset.p===p.id)); } };
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) setActive(e.target.id); }), {rootMargin:'-15% 0px -75% 0px'});
navTargets.forEach(t => io.observe(t));
new IntersectionObserver(es => nav.classList.toggle('visible', !es[0].isIntersecting)).observe(toc);

/* top bar: hide on scroll down, show on scroll up, near the top edge, or on hover/focus */
const bar = $('#topbar'), prog = $('#progress'); let lastY = scrollY, hoverBar = false;
const showBar = v => bar.classList.toggle('hide', !v);
addEventListener('scroll', () => { const y = scrollY, h = document.documentElement;
  prog.style.width = (100 * y / Math.max(1, h.scrollHeight - h.clientHeight)) + '%';
  bar.classList.toggle('raised', y > 8);
  if (y < 80) showBar(true); else if (!hoverBar && !bar.contains(document.activeElement)) { if (y > lastY + 6) showBar(false); else if (y < lastY - 6) showBar(true); }
  lastY = y; }, {passive:true});
addEventListener('mousemove', e => { if (e.clientY < 56) showBar(true); }, {passive:true});
bar.addEventListener('mouseenter', () => { hoverBar = true; showBar(true); }); bar.addEventListener('mouseleave', () => { hoverBar = false; });
bar.addEventListener('focusin', () => showBar(true));
/* theme toggle */
const root = document.documentElement;
$('#themeBtn').addEventListener('click', () => { const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = dark ? 'light' : 'dark'; try { localStorage.setItem('atlas-theme', root.dataset.theme); } catch(e) {} });
/* language switch keeps the section the reader is on */
$('#langBtn').addEventListener('click', e => { e.preventDefault(); location.href = e.currentTarget.getAttribute('href') + location.hash; });

let lastW = innerWidth, rt; addEventListener('resize', () => { if (Math.abs(innerWidth-lastW)<40) return; lastW=innerWidth; clearTimeout(rt); rt=setTimeout(()=>REDRAW.forEach(f=>f()), 150); });
})();
