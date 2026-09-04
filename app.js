"use strict";

/* NEI 아키텍처 — data/*.json 에서 지도·막대그림·표를 만든다. */

const DB = {}, STATE = { off: new Set(), sel: null, claim: "all", refArea: "all" };
const KO = { theorem:"theorem", definition:"definition", diagnostic:"diagnostic",
             measured:"exploratory", open:"open", withdrawn:"withdrawn",
             caution:"caution", conjecture:"conjecture", given:"input",
             verdict:"candidate" };
const esc = s => String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const badge = s => `<span class="badge b-${s}">${KO[s]||s}</span>`;

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
  if(!n){ el.innerHTML='<p class="muted">node를 선택하면 본문·SI·Note의 대응 위치와 서술 gap이 열립니다.</p>'; return; }
  const lbl=i=>DB.nodes.nodes.find(x=>x.id===i)?.label||i;
  const inc=DB.edges.edges.filter(e=>e.to===n.id), out=DB.edges.edges.filter(e=>e.from===n.id);
  const vias=[...new Set([...inc,...out].map(e=>e.via))];
  const sm=DB.sources.nodes[n.id]||{};
  const kindLabel={direct:"직접 서술",partial:"부분 서술",none:"직접 대응 없음"};
  const sourceCards=Object.entries(DB.sources.sources).map(([key,meta])=>{
    const x=sm[key]||{kind:"none",location:"직접 대응 없음",summary:"Source mapping이 아직 작성되지 않았다."};
    return `<article class="source-card ${esc(meta.class)} is-${esc(x.kind)}">
      <div class="source-head"><span class="source-name">${esc(meta.label)}</span>
        <span class="source-kind">${esc(kindLabel[x.kind]||x.kind)}</span></div>
      <div class="source-file">${esc(meta.file)}</div>
      <div class="source-location">${esc(x.location)}</div>
      <p>${tex(x.summary)}</p>
    </article>`;
  }).join("");
  el.innerHTML=`
    <div class="node-inspector-head"><span class="node-dot" style="background:${esc(DB.nodes.domains[n.domain].color)}"></span>
      <h3>${esc(n.label)}</h3></div>
    <p class="muted" style="font-size:13px;margin:0 0 12px">${badge(n.status)}
      &nbsp;${esc(DB.nodes.domains[n.domain].label)}</p>
    ${n.formula?`<div class="fml">${texB(n.formula)}</div>`:""}
    <p>${tex(n.def)}</p>
    <div class="sect">Source inspector</div>
    <div class="source-grid">${sourceCards}</div>
    ${vias.length?`<div class="sect">Connectors</div><ul>${
      vias.map(v=>`<li>${tex(DB.connectors[v].label)}</li>`).join("")}</ul>`:""}
    ${inc.length?`<div class="sect">들어오는 연결</div><ul>${
      inc.map(e=>`<li>${badge(e.status)} ${esc(lbl(e.from))} → <i>${esc(e.label)}</i></li>`).join("")}</ul>`:""}
    ${out.length?`<div class="sect">나가는 연결</div><ul>${
      out.map(e=>`<li>${badge(e.status)} <i>${esc(e.label)}</i> → ${esc(lbl(e.to))}</li>`).join("")}</ul>`:""}
    ${n.refs.length?`<div class="sect">References</div><ul>${
      n.refs.map(k=>{const r=DB.refs[k];
        return `<li><a href="#ref-${esc(k)}">${esc(r.authors.split(",")[0])} (${r.year})</a> — ${esc(r.why)}</li>`;
      }).join("")}</ul>`:""}`;
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
      <div class="card"><h3>${tex(c.label)}</h3>
        <p class="cx">잇는 것 — ${c.connects.map(esc).join(" · ")}</p>
        <p>${tex(c.why)}</p></div>`).join("");
}
function renderClaims(){
  const b=document.getElementById("claimFilter");
  b.innerHTML=["all","definition","theorem","diagnostic","measured","open","withdrawn"].map(k=>
    `<button class="tag" data-k="${k}" aria-pressed="${k===STATE.claim}">${
      k==="all"?"전체":KO[k]}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{STATE.claim=x.dataset.k;renderClaims();});
  const rows=DB.claims.claims.filter(c=>STATE.claim==="all"||c.status===STATE.claim);
  document.getElementById("claimsTable").innerHTML=
    `<thead><tr><th>id</th><th>상태</th><th>주장</th><th>근거</th></tr></thead><tbody>${
      rows.map(c=>`<tr><td class="k">${esc(c.id)}</td><td>${badge(c.status)}</td>
        <td>${tex(c.text)}</td>
        <td class="muted" style="font-size:13px">${tex(c.basis)}${
          c.refs.length?" · "+c.refs.map(k=>`<a href="#ref-${esc(k)}">${
            esc(DB.refs[k].authors.split(",")[0].split(" ").pop())} ${DB.refs[k].year}</a>`).join(", "):""
        }</td></tr>`).join("")}</tbody>`;
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
  document.getElementById("refsTable").innerHTML=
    `<thead><tr><th>key</th><th>reference</th><th>why</th></tr></thead><tbody>${
      items.map(([k,r])=>`<tr id="ref-${esc(k)}"><td class="k"><code>${esc(k)}</code>${
        r.verified?"":' <span class="badge b-open">미확인</span>'}</td>
        <td>${esc(r.authors)} (${r.year}). ${esc(r.title)}. <i>${esc(r.venue)}</i>${
          r.volume?" "+esc(r.volume):""}${r.pages?", "+esc(r.pages):""}.${
          r.doi?` <a href="https://doi.org/${esc(r.doi)}" target="_blank" rel="noopener noreferrer">doi:${esc(r.doi)}</a>`:""}</td>
        <td class="muted" style="font-size:13px">${esc(r.why)}</td></tr>`).join("")}</tbody>`;
}

/* ── 1차 일단락 ──────────────────────────────────────── */
function renderScope(){
  const s=DB.scope.first_closure;
  document.getElementById("scopeThesis").innerHTML=tex(s.thesis);
  document.getElementById("scopeClaims").innerHTML=s.four_claims.map(c=>`
    <div class="claimline"><span class="n">${c.n}</span>
      <span><span class="t">${tex(c.t)}</span>
        <span class="s">${tex(c.state)}</span></span></div>`).join("");
  document.getElementById("scopeWhy").innerHTML=
    s.why_this_line.map(w=>`<li>${tex(w)}</li>`).join("");
  document.getElementById("scopeTodo").innerHTML=
    `<thead><tr><th>Analysis</th><th>Rationale</th><th>Priority</th></tr></thead><tbody>${
      s.todo.map(x=>`<tr><td>${tex(x.k)}</td>
        <td class="muted" style="font-size:13px">${tex(x.w)}</td>
        <td><span class="badge need-${esc(x.need)}">${esc(x.need)}</span></td></tr>`).join("")}</tbody>`;
  document.getElementById("scopeOut").innerHTML=
    `<thead><tr><th>Topic</th><th>Rationale</th><th>Stage</th></tr></thead><tbody>${
      s.excluded.map(x=>`<tr><td>${tex(x.k)}</td>
        <td class="muted" style="font-size:13px">${tex(x.w)}</td>
        <td class="k">${esc(x.to)}</td></tr>`).join("")}</tbody>`;
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
          throw new Error(`offline bundle에 ${f}가 없습니다`);
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
      `<p class="err">데이터를 불러오지 못했습니다: ${esc(e.message)}<br>
       <span class="muted"><code>data/offline-data.js</code>를 다시 생성하거나
       GitHub Pages에서 여세요.</span></p>`;
    return;
  }
  renderCharts(); renderFilters(); renderMapLegend(); renderCoverageSummary(); renderScope();
  renderConnectors(); renderClaims(); renderRefs();
  drawMap();
  document.getElementById("zIn").onclick  = ()=>GRAPH?.zoomIn();
  document.getElementById("zOut").onclick = ()=>GRAPH?.zoomOut();
  document.getElementById("zFit").onclick = ()=>{ GRAPH?.fit(); GRAPH?.select(null); STATE.sel=null; renderPanel(); };
})();
