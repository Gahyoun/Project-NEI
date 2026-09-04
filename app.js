"use strict";

/* NEI architecture — data/*.json 기반의 map·bar chart·table rendering. */

const DB = {}, STATE = { off: new Set(), sel: null, claim: "all", refArea: "all" };
const KO = { theorem:"theorem", definition:"definition", diagnostic:"diagnostic",
             measured:"exploratory", open:"open", withdrawn:"withdrawn",
             caution:"caution", conjecture:"conjecture", given:"input",
             verdict:"candidate" };
const esc = s => String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const badge = s => `<span class="badge b-${s}">${KO[s]||s}</span>`;

/* table placeholder를 Markdown형 hierarchical note host로 전환. */
function noteHost(id, label){
  const current=document.getElementById(id);
  if(current?.tagName==="OL"){
    current.setAttribute("aria-label",label);
    return current;
  }
  const next=document.createElement("ol");
  next.id=id;
  next.className="note-tree note-depth-3";
  next.setAttribute("aria-label",label);
  current?.replaceWith(next);
  return next;
}

function tex(s){
  return String(s).split(/(\$[^$]+\$)/g).map(part=>{
    if(part.startsWith("$") && part.endsWith("$")){
      const m=part.slice(1,-1);
      try{ return window.katex.renderToString(m,{throwOnError:false}); }catch{ return esc(part); }
    }
    return esc(part);
  }).join("");
}
function texB(s){ try{ return window.katex.renderToString(s,{throwOnError:false}); }catch{ return esc(`$${s}$`); } }

/* ── 막대그림 ─────────────────────────────────────────── */
function cap(id,t,s){ const e=document.getElementById(id); if(e)
  e.innerHTML=`<span class="t">${tex(t)}</span>${s?`<span class="s">${tex(s)}</span>`:""}`; }

function bars(el, rows, {max=null, fmt=v=>v.toFixed(3), cls=()=>"s1", legend=null}={}) {
  const M = max ?? Math.max(...rows.map(r=>Array.isArray(r.v)?Math.max(...r.v):r.v), 1e-12);
  el.innerHTML = (legend? `<div class="legend">${legend}</div>`:"") +
    `<div class="bars">${rows.map(r=>{
      const vs = Array.isArray(r.v)? r.v : [r.v];
      return `<div class="bar">
        <span class="k">${esc(r.k)}</span>
        <span class="bargroup">${vs.map((v,i)=>
          `<span class="track"><span class="fill ${cls(i)}" style="width:${
            Math.max(v/M*100,0.4)}%"></span></span>`).join("")}</span>
        <span class="v">${r.vlabel ?? vs.map(fmt).join(" / ")}</span></div>`;
    }).join("")}</div>`;
}

function rangeBars(el, rows) {
  const hi = Math.max(...rows.map(r=>r.hi));
  el.innerHTML = `<div class="bars">${rows.map(r=>`
    <div class="bar rangebar">
      <span class="k">${esc(r.k)} <span class="muted">n=${r.n}</span></span>
      <span class="track"><span class="fill" style="left:${r.lo/hi*100}%;width:${
        Math.max((r.hi-r.lo)/hi*100,1)}%"></span></span>
      <span class="v">${r.lo.toFixed(1)}–${r.hi.toFixed(1)}</span></div>`).join("")}</div>`;
}

function renderCharts() {
  const m = DB.meas;

  const D = m.Dp_models;
  cap("cap-Dp", D.title, D.sub);
  bars(document.getElementById("ch-Dp"), D.rows, { max:1,
    cls:i=>`s${i+1}`, fmt:v=>v.toFixed(3),
    legend: D.series.map((s,i)=>`<span><i style="background:${
      ["var(--primary)","#7aa2e3","#b9cef2"][i]}"></i>${s}</span>`).join("") });

  const P = m.polish;
  cap("cap-polish", P.title, P.sub + "  " + P.verdict);
  const lg = v => Math.log10(1/v);            // 작을수록 좋은 양은 자릿수로
  const fmtSci = v => v.toExponential(2).replace("e-","e−").replace("+","");
  bars(document.getElementById("ch-polish"),
    P.rows.map(r=>({ k:r.k,
                     v: r.log ? lg(r.v)/9 : r.v/0.12,
                     vlabel: r.log ? fmtSci(r.v) : r.v.toFixed(4) })),
    { max:1 });

  const C = m.certify;
  cap("cap-certify", C.title, C.sub + "  " + C.verdict);
  document.getElementById("ch-certify").innerHTML = "";
  bars(document.getElementById("ch-certify"),
    C.rows.concat(C.K.map(k=>({k:`K @ cutoff ${k.k}`, v:k.v}))),
    { max:24, fmt:v=>String(v) });

  const V = m.I_vs_deff;
  cap("cap-Ideff", V.title, V.sub);
  rangeBars(document.getElementById("ch-Ideff"), V.rows);

  const Z = m.censoring;
  cap("cap-cens", Z.title, Z.sub);
  bars(document.getElementById("ch-cens"), Z.rows, { max:77, fmt:v=>`${v}/77` });

  const cnt = {};
  DB.claims.claims.forEach(c=>cnt[c.status]=(cnt[c.status]||0)+1);
  cap("cap-status",`주장 ${DB.claims.claims.length}건의 구성`,
      "definition · theorem · diagnostic · exploratory · open · withdrawn");
  const statusOrder=["definition","theorem","diagnostic","measured","open","withdrawn"];
  bars(document.getElementById("ch-status"),
    statusOrder.map(s=>({k:KO[s],v:cnt[s]||0})),
    { max:Math.max(...Object.values(cnt)), fmt:v=>`${v}건` });
}

/* ── 지도 ─────────────────────────────────────────────── */
let GRAPH = null;
function drawMap(){
  const host=document.getElementById("mapc");
  GRAPH?.destroy?.();
  const shown=DB.nodes.nodes.filter(n=>!STATE.off.has(n.domain));
  const ids=new Set(shown.map(n=>n.id));
  GRAPH = window.NEIGraph.makeGraph(host,{
    nodes: shown, domains: DB.nodes.domains,
    edges: DB.edges.edges.filter(e=>ids.has(e.from)&&ids.has(e.to)),
    onSelect: id => { STATE.sel=id; renderPanel(); }
  });
}
function renderMapLegend(){
  const el=document.getElementById("mapLegend"); if(!el) return;
  const nodeStatus=[
    ["#5b6470","input"], ["#256ef4","theorem"], ["#207037","definition"],
    ["#ab5b00","diagnostic / exploratory"], ["#6d7882","open"],
    ["#a8332a","candidate"]
  ];
  el.innerHTML=`<span class="legend-prefix">node text:</span>`+
    nodeStatus.map(([c,label])=>`<span class="node-status-key" style="color:${c}">${label}</span>`).join("")+
    `<span class="legend-divider" aria-hidden="true"></span>`+
    `<span><i style="background:#256ef4"></i>edge: theorem</span>`+
    `<span><i style="background:#477a56"></i>edge: definition / diagnostic</span>`+
    `<span><i style="background:#ab5b00"></i>edge: exploratory</span>`+
    `<span><i style="background:#6a2d86"></i>edge: caution</span>`+
    `<span><i style="background:#6d7882"></i>edge: open</span>`;
}

function renderCoverageSummary(){
  const host=document.getElementById("coverageSummary"); if(!host) return;
  const ids=DB.nodes.nodes.map(n=>n.id);
  const labels={direct:"직접",partial:"부분",none:"없음"};
  const chips=Object.entries(DB.sources.sources).map(([key,meta])=>{
    const count={direct:0,partial:0,none:0};
    ids.forEach(id=>{ const k=DB.sources.nodes[id]?.[key]?.kind||"none"; count[k]++; });
    return `<span class="coverage-chip ${esc(meta.class)}">${esc(meta.label)}
      ${Object.entries(count).map(([k,v])=>`${labels[k]} ${v}`).join(" · ")}</span>`;
  });
  const common=ids.filter(id=>Object.keys(DB.sources.sources).every(
    key=>(DB.sources.nodes[id]?.[key]?.kind||"none")==="none"));
  chips.push(`<span class="coverage-chip gaps">세 문서 공통 미서술 ${common.length}
    · ${common.map(id=>esc(DB.nodes.nodes.find(n=>n.id===id)?.label||id)).join(" · ")}</span>`);
  host.innerHTML=chips.join("");
}

function renderPanel(){
  const el=document.getElementById("panel");
  const n=DB.nodes.nodes.find(x=>x.id===STATE.sel);
  if(!n){ el.innerHTML='<p class="muted">node 선택 시 본문·SI·Note의 대응 위치와 서술 gap 표시.</p>'; return; }
  const lbl=i=>DB.nodes.nodes.find(x=>x.id===i)?.label||i;
  const inc=DB.edges.edges.filter(e=>e.to===n.id), out=DB.edges.edges.filter(e=>e.from===n.id);
  const vias=[...new Set([...inc,...out].map(e=>e.via))];
  const sm=DB.sources.nodes[n.id]||{};
  const kindLabel={direct:"직접 서술",partial:"부분 서술",none:"직접 대응 없음"};
  const sourceCards=Object.entries(DB.sources.sources).map(([key,meta])=>{
    const x=sm[key]||{kind:"none",location:"직접 대응 없음",summary:"Source mapping 미작성."};
    return `<li class="source-slot"><article class="source-card ${esc(meta.class)} is-${esc(x.kind)}">
      <div class="source-head"><h5 class="source-name">${esc(meta.label)}</h5>
        <span class="source-kind">${esc(kindLabel[x.kind]||x.kind)}</span></div>
      <dl class="source-meta">
        <div><dt>File</dt><dd class="source-file">${esc(meta.file)}</dd></div>
        <div><dt>Location</dt><dd class="source-location">${esc(x.location)}</dd></div>
      </dl>
      <p>${tex(x.summary)}</p>
    </article></li>`;
  }).join("");
  const relationGroups=[
    vias.length?`<li><section><h5>Connectors</h5><ul>${
      vias.map(v=>`<li>${tex(DB.connectors[v].label)}</li>`).join("")}</ul></section></li>`:"",
    inc.length?`<li><section><h5>Incoming dependencies</h5><ul>${
      inc.map(e=>`<li>${badge(e.status)} ${esc(lbl(e.from))} → <i>${esc(e.label)}</i></li>`).join("")}</ul></section></li>`:"",
    out.length?`<li><section><h5>Outgoing dependencies</h5><ul>${
      out.map(e=>`<li>${badge(e.status)} <i>${esc(e.label)}</i> → ${esc(lbl(e.to))}</li>`).join("")}</ul></section></li>`:""
  ].join("");
  el.innerHTML=`
    <article class="node-note" aria-labelledby="node-note-${esc(n.id)}">
      <header class="node-inspector-head"><span class="node-dot" style="background:${esc(DB.nodes.domains[n.domain].color)}"></span>
        <div><h3 id="node-note-${esc(n.id)}">${esc(n.label)}</h3>
          <p class="muted note-kicker">${badge(n.status)} &nbsp;${esc(DB.nodes.domains[n.domain].label)}</p></div>
      </header>
      <ol class="note-tree note-depth-4">
        ${n.formula?`<li><section><h4>Formula</h4><div class="fml">${texB(n.formula)}</div></section></li>`:""}
        <li><section><h4>Definition and interpretation</h4><p>${tex(n.def)}</p></section></li>
        <li><section><h4>Evidence traceability</h4>
          <ol class="source-grid note-tree note-depth-5">${sourceCards}</ol>
        </section></li>
        ${relationGroups?`<li><section><h4>Relations</h4><ol class="note-tree note-depth-5">${relationGroups}</ol></section></li>`:""}
        ${n.refs.length?`<li><section><h4>References</h4><ul>${
          n.refs.map(k=>{const r=DB.refs[k];
            return `<li><a href="#ref-${esc(k)}">${esc(r.authors.split(",")[0])} (${r.year})</a> — ${tex(r.why)}</li>`;
          }).join("")}</ul></section></li>`:""}
      </ol>
    </article>`;
}

/* ── 필터 · 카드 · 표 ─────────────────────────────────── */
function renderFilters(){
  const b=document.getElementById("domFilter");
  b.innerHTML=Object.entries(DB.nodes.domains).map(([d,m])=>
    `<button class="tag" data-d="${d}" aria-pressed="true">${esc(m.label)}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{
    const on=x.getAttribute("aria-pressed")==="true";
    x.setAttribute("aria-pressed",String(!on));
    on?STATE.off.add(x.dataset.d):STATE.off.delete(x.dataset.d);
    if(STATE.sel && !DB.nodes.nodes.some(n=>n.id===STATE.sel && !STATE.off.has(n.domain))) STATE.sel=null;
    drawMap(); renderPanel(); });
}
function renderConnectors(){
  document.getElementById("connectors").innerHTML=
    Object.entries(DB.connectors).filter(([k])=>!k.startsWith("_")).map(([,c])=>`
      <article class="card connector-note"><h3>${tex(c.label)}</h3>
        <ol class="note-tree note-depth-4">
          <li><section><h4>Relation scope</h4>
            <p class="cx">${c.connects.map(esc).join(" · ")}</p></section></li>
          <li><section><h4>Rationale</h4><p>${tex(c.why)}</p></section></li>
        </ol>
      </article>`).join("");
}
function renderClaims(){
  const b=document.getElementById("claimFilter");
  b.innerHTML=["all","definition","theorem","diagnostic","measured","open","withdrawn"].map(k=>
    `<button class="tag" data-k="${k}" aria-pressed="${k===STATE.claim}">${
      k==="all"?"전체":KO[k]}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{STATE.claim=x.dataset.k;renderClaims();});
  const rows=DB.claims.claims.filter(c=>STATE.claim==="all"||c.status===STATE.claim);
  noteHost("claimsTable","Claim ledger").innerHTML=rows.map(c=>`
    <li class="ledger-item"><article class="claim-note" aria-labelledby="claim-${esc(c.id)}">
      <header class="ledger-head"><h3 id="claim-${esc(c.id)}"><code>${esc(c.id)}</code></h3>${badge(c.status)}</header>
      <ol class="note-tree note-depth-4">
        <li><section><h4>Claim</h4><p>${tex(c.text)}</p></section></li>
        <li><section><h4>Basis</h4><p class="muted">${tex(c.basis)}</p>${
          c.refs.length?`<section class="note-depth-5"><h5>References</h5><ul>${c.refs.map(k=>`<li><a href="#ref-${esc(k)}">${
            esc(DB.refs[k].authors.split(",")[0].split(" ").pop())} ${DB.refs[k].year}</a></li>`).join("")}</ul></section>`:""
        }</section></li>
      </ol>
    </article></li>`).join("");
}
function renderRefs(){
  const areas=["all",...new Set(Object.entries(DB.refs).filter(([k])=>!k.startsWith("_"))
    .map(([,r])=>r.area).filter(Boolean))];
  const b=document.getElementById("refFilter");
  b.innerHTML=areas.map(a=>`<button class="tag" data-a="${esc(a)}" aria-pressed="${
    a===STATE.refArea}">${a==="all"?"전체":esc(a)}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{STATE.refArea=x.dataset.a;renderRefs();});
  const items=Object.entries(DB.refs).filter(([k])=>!k.startsWith("_"))
    .filter(([,r])=>STATE.refArea==="all"||r.area===STATE.refArea)
    .sort((a,b)=>a[1].year-b[1].year);
  noteHost("refsTable","References").innerHTML=items.map(([k,r])=>`
    <li class="ledger-item"><article class="reference-note" id="ref-${esc(k)}" aria-labelledby="ref-title-${esc(k)}">
      <header class="ledger-head"><h3 id="ref-title-${esc(k)}"><code>${esc(k)}</code> — ${esc(r.title)}</h3>${
        r.verified?"":' <span class="badge b-open">미확인</span>'}</header>
      <ol class="note-tree note-depth-4">
        <li><section><h4>Citation</h4><p>${esc(r.authors)} (${r.year}). <cite>${esc(r.title)}</cite>. <i>${esc(r.venue)}</i>${
          r.volume?" "+esc(r.volume):""}${r.pages?", "+esc(r.pages):""}.${
          r.doi?` <a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener noreferrer">doi:${esc(r.doi)}</a>`:""}</p></section></li>
        <li><section><h4>Architecture role</h4><p class="muted">${tex(r.why)}</p></section></li>
      </ol>
    </article></li>`).join("");
}

/* ── 1차 일단락 ──────────────────────────────────────── */
function renderScope(){
  const s=DB.scope.first_closure;
  document.getElementById("scopeThesis").innerHTML=tex(s.thesis);
  document.getElementById("scopeClaims").innerHTML=`<ol class="note-tree note-depth-4">${s.four_claims.map(c=>`
    <li class="claimline"><span class="n" aria-hidden="true">${c.n}</span><article><h4>Claim ${c.n}</h4>
      <p class="t">${tex(c.t)}</p>
      <dl class="note-meta"><div><dt>Status</dt><dd class="s">${tex(c.state)}</dd></div></dl>
    </article></li>`).join("")}</ol>`;
  document.getElementById("scopeWhy").innerHTML=
    s.why_this_line.map((w,i)=>`<li><article><h4>Boundary ${i+1}</h4><p>${tex(w)}</p></article></li>`).join("");
  noteHost("scopeTodo","Required analyses").innerHTML=s.todo.map((x,i)=>`
    <li><article class="scope-note" data-note-index="${i+1}"><h4>${tex(x.k)}</h4>
      <dl class="note-meta">
        <div><dt>Rationale</dt><dd class="muted">${tex(x.w)}</dd></div>
        <div><dt>Priority</dt><dd><span class="badge need-${esc(x.need)}">${esc(x.need)}</span></dd></div>
      </dl>
    </article></li>`).join("");
  noteHost("scopeOut","2차 일단락 대상").innerHTML=s.excluded.map((x,i)=>`
    <li><article class="scope-note" data-note-index="${i+1}"><h4>${tex(x.k)}</h4>
      <dl class="note-meta">
        <div><dt>Rationale</dt><dd class="muted">${tex(x.w)}</dd></div>
        <div><dt>Stage</dt><dd class="k">${esc(x.to)}</dd></div>
      </dl>
    </article></li>`).join("");
}

/* ── 부팅 ─────────────────────────────────────────────── */
(async function(){
  const files={nodes:"nodes",edges:"edges",connectors:"connectors",
               claims:"claims",refs:"refs",meas:"measurements",scope:"scope",
               sources:"source-map"};
  try{
    if(window.NEI_DATA){
      for(const [k,f] of Object.entries(files)){
        if(!Object.prototype.hasOwnProperty.call(window.NEI_DATA,f))
          throw new Error(`offline bundle에 ${f} 없음`);
        DB[k]=window.NEI_DATA[f];
      }
    }else{
      await Promise.all(Object.entries(files).map(async([k,f])=>{
        const r=await fetch(`data/${f}.json`);
        if(!r.ok) throw new Error(`data/${f}.json ${r.status}`);
        DB[k]=await r.json(); }));
    }
  }catch(e){
    document.getElementById("mapc").innerHTML=
      `<p class="err">데이터 불러오기 실패: ${esc(e.message)}<br>
       <span class="muted"><code>data/offline-data.js</code> 재생성 또는
       GitHub Pages에서 열기.</span></p>`;
    return;
  }
  renderCharts(); renderFilters(); renderMapLegend(); renderCoverageSummary(); renderScope();
  renderConnectors(); renderClaims(); renderRefs();
  drawMap();
  document.getElementById("zIn").onclick  = ()=>GRAPH?.zoomIn();
  document.getElementById("zOut").onclick = ()=>GRAPH?.zoomOut();
  document.getElementById("zFit").onclick = ()=>{ GRAPH?.fit(); GRAPH?.select(null); STATE.sel=null; renderPanel(); };
})();
