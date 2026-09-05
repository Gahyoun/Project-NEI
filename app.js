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
    // Escape first; then admit only the narrow Markdown emphasis form **text**.
    // This keeps JSON prose inert while allowing compact technical labels.
    return esc(part).replace(/\*\*([^*\n]+)\*\*/g,"<strong>$1</strong>");
  }).join("");
}
function texB(s){ try{ return window.katex.renderToString(s,{throwOnError:false}); }catch{ return esc(`$${s}$`); } }

const NODE_NOTE_JUMPS = [
  {id:"corrected-study", label:"Corrected Rerun and Graph-Null Evidence",
   nodes:["G","protocol","gate","NEI","calib","cmnull","robust","deff","recur"]},
  {id:"local-spread-bound", label:"Local Residual-to-Spread Bound",
   nodes:["hessian","rigidity","gate","NEI","floppy","calib"]},
  {id:"finite-m-inference", label:"Finite-M Inference and Rank Bounds",
   nodes:["NEI","deff","Keff","robust","recur","terminal","protocol"]},
  {id:"scale-equivariance", label:"Observable Scaling and Protocol Equivariance",
   nodes:["G","protocol","stress","NEI","calib","Dp"]},
  {id:"validation-contract", label:"Evidence Production Contract",
   nodes:["G","protocol","gate","calib","cmnull","NEI","recur","robust"]},
  {id:"kernelPanel", label:"Graph-to-Terminal-Law Kernel",
   nodes:["protocol","terminal","gate","NEI"]},
  {id:"metric-calibration", label:"Metric Calibration Proof Note",
   nodes:["schoenberg","negtype","strain","Dp","fit","NEI","calib"]},
  {id:"mass-resolution", label:"Mass Resolution and Detection Power",
   nodes:["terminal","NEI","Keff","recur","multiplicity","robust"]},
  {id:"control-fit", label:"Target-Fit Calibration Contract",
   nodes:["calib","gate","fit","stress"]},
  {id:"majorization-proof", label:"SMACOF Majorization Proof",
   nodes:["stress","strain","gate"]},
  {id:"decisive-experiment", label:"Primary Empirical Test",
   nodes:["G","cmnull","resid","NEI","robust"]},
  {id:"floorFig", label:"Legacy Tolerance Ladder",
   nodes:["gate","NEI","robust","calib"]},
  {id:"sample", label:"Sample and Exclusion Audit",
   nodes:["G","cmnull","robust","resid"]},
  {id:"discussion-A1", label:"A1 · Terminology and Equivalence Policy",
   nodes:["schoenberg","negtype","Dp","shape","aut","hessian","morse","multiplicity","Egap"]},
  {id:"discussion-A2", label:"A2 · Terminal-Kernel Robustness",
   nodes:["protocol","terminal","gate","Keff","recur","robust"]},
  {id:"discussion-A3", label:"A3 · Incompatibility Organization",
   nodes:["G","Dp","hessian","rigidity","floppy","cmnull","resid"]}
];

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
    hyper: null,
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
  const labels={direct:"직접",partial:"부분",none:"없음",unreviewed:"미검토"};
  const chips=Object.entries(DB.sources.sources).map(([key,meta])=>{
    const count={direct:0,partial:0,none:0,unreviewed:0};
    ids.forEach(id=>{
      const k=DB.sources.nodes[id]?.[key]?.kind||"unreviewed";
      count[k]=(count[k]||0)+1;
    });
    return `<span class="coverage-chip ${esc(meta.class)}">${esc(meta.label)}
      ${Object.entries(count).map(([k,v])=>`${labels[k]} ${v}`).join(" · ")}</span>`;
  });
  const common=ids.filter(id=>Object.keys(DB.sources.sources).every(
    key=>DB.sources.nodes[id]?.[key]?.kind==="none"));
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
  const kindLabel={direct:"직접 서술",partial:"부분 서술",none:"직접 대응 없음",
                   unreviewed:"Source audit pending"};
  const sourceCards=Object.entries(DB.sources.sources).map(([key,meta])=>{
    const x=sm[key]||{kind:"unreviewed",location:"source audit pending",
                     summary:"현재 snapshot에서 대응 위치 미검토. 미서술 판정 아님."};
    const passages=DB["excerpts_"+key]?.excerpts[n.id]||[];
    const quoteBody=passages.map((p,i)=>{
      const rendered=window.NEISourceQuote.render(p.tex,key);
      return '<div class="source-passage">'+
        '<p class="source-excerpt-label">원문 발췌 '+(i+1)+' · lines '+p.start_line+'–'+p.end_line+'</p>'+
        '<blockquote class="source-quote">'+rendered.html+'</blockquote>'+
        '<details class="source-raw"><summary>LaTeX 원문</summary><pre>'+esc(p.tex)+'</pre></details></div>';
    }).join("");
    return `<li class="source-slot"><article class="source-card ${esc(meta.class)} is-${esc(x.kind)}">
      <div class="source-head"><h5 class="source-name">${esc(meta.label)}</h5>
        <span class="source-kind">${esc(kindLabel[x.kind]||x.kind)}</span></div>
      <dl class="source-meta">
        ${meta.revision?`<div><dt>Version</dt><dd>${esc(meta.revision)} 개정본</dd></div>`:""}
        <div><dt>Location</dt><dd class="source-location">${esc(x.location)}</dd></div>
      </dl>
      ${quoteBody||`<p class="source-empty">${x.kind==="none"?"직접 대응하는 원문 발췌 없음.":"원문 발췌 미확인. 미서술 판정과 구분."}</p>`}
      <details class="source-audit"><summary>Coverage note · 원문 인용 아님</summary><p>${tex(x.summary)}</p></details>
    </article></li>`;
  }).join("");
  const discussion=(n.discussion||[]).map(group=>`<li><section>
    <h5>${esc(group.label)}</h5><ul>${group.items.map(item=>`<li>${tex(item)}</li>`).join("")}</ul>
    </section></li>`).join("");
  const noteJumps=NODE_NOTE_JUMPS.filter(x=>x.nodes.includes(n.id));
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
        <li><section><h4>Definition and interpretation</h4><p>${tex(n.def)}</p>
          ${discussion?`<ol class="note-tree node-discussion">${discussion}</ol>`:""}
        </section></li>
        <li><section><h4>Evidence traceability</h4>
          <p class="fine">첨부 문서의 실제 문장·수식 발췌. 원문 내용은 교정하지 않으며 현재 interpretation과 구분. 수식은 렌더링하고 citation·cross-reference는 원문 key로 표시. LaTeX 원문과 행 위치로 대조 가능.</p>
          <ol class="source-grid note-tree note-depth-5">${sourceCards}</ol>
        </section></li>
        ${noteJumps.length?`<li><section><h4>Current Research Note</h4>
          <p class="fine">Manuscript coverage와 분리된 working discussion. 해당 anchor로 이동.</p>
          <ul>${noteJumps.map(x=>`<li><a href="#${esc(x.id)}">${esc(x.label)}</a></li>`).join("")}</ul>
        </section></li>`:""}
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
      <div class="claim-maturity"><span>Claim type: ${esc((c.claim_type||"unreviewed").replaceAll("_"," "))}</span><span>Evidence: ${esc((c.evidence_state||"unreviewed").replaceAll("_"," "))}</span></div>
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
function renderCalib(){
  const c=DB.meas.calibration; if(!c||!document.getElementById("ch-calib")) return;
  document.getElementById("cap-calib-t").innerHTML=tex(c.title);
  document.getElementById("cap-calib-s").innerHTML=tex(c.sub);
  // I 는 자릿수가 22 자리에 걸치므로 log10 로 그린다
  const lg=v=>Math.max(0,(Math.log10(v)+24)/24);
  bars(document.getElementById("ch-calib"),
    c.rows.map(r=>({k:r.k, v:[r.D2, lg(r.I_pol)],
      vlabel:`${r.D2.toFixed(3)} / ${r.I_pol.toExponential(1).replace("e-","e−")}`})),
    {max:1, cls:i=>i?"s2":"s1",
     legend:`<span><i style="background:var(--primary)"></i>${tex("$\\mathcal D_2$")}</span>`+
            `<span><i style="background:#7aa2e3"></i>${tex("$\\log_{10}\\widehat{\\mathcal I}_M$ (polish, 눈금 $10^{-24}$–$10^{0}$)")}</span>`});
  document.getElementById("calib-verdict").innerHTML=tex(c.verdict);
}

function renderByType(){
  const r=DB.meas.repr_full; if(!r||!r.bytype||!document.getElementById("ch-bytype")) return;
  const hi=Math.max(...r.bytype.map(x=>x.hi));
  document.getElementById("ch-bytype").innerHTML=`<div class="bars">${
    r.bytype.map(x=>`<div class="bar rangebar">
      <span class="k">${esc(x.k)} <span class="muted">n=${x.n}</span></span>
      <span class="track"><span class="fill" style="left:${x.lo/hi*100}%;width:${
        Math.max((x.hi-x.lo)/hi*100,1.2)}%"></span></span>
      <span class="v">${x.med.toFixed(3)}</span></div>`).join("")}</div>`;
  document.getElementById("bytype-caveat").innerHTML=tex(r.caveat||"");
}

function renderFloor(){
  const f=DB.meas.floor_ladder; if(!f||!document.getElementById("tb-floor")) return;
  document.getElementById("cap-floor-t").innerHTML=tex(f.title);
  document.getElementById("cap-floor-s").innerHTML=tex(f.sub);
  const sci=v=>v.toExponential(4).replace("e-","e−").replace("e+","e");
  const sci2=v=>v.toExponential(2).replace("e-","e−").replace("e+","e");
  const floorVerdictBadge=value=>{
    const raw=String(value||"unresolved");
    const legacy=/\blegacy\b/i.test(raw);
    const core=raw.replace(/\s*\(legacy\)\s*/i,"").trim()||raw;
    const cls=/persistent|signal/i.test(core)?"b-measured":"b-open";
    return `<span class="badge ${cls}">${esc(core)}</span>${legacy?
      ' <span class="badge b-caution">legacy</span>':""}`;
  };
  document.getElementById("tb-floor").innerHTML=
    `<thead><tr><th rowspan="2">Graph</th>${f.rungs.map((r,i)=>`<th colspan="2">
        gtol ${tex(r)}<br><span class="fine">ftol ${tex(f.ftol?.[i]||"—")}</span></th>`).join("")}
        <th rowspan="2">Verdict</th></tr>
      <tr>${f.rungs.map(()=>`<th style="font-weight:400">${tex("$\\widehat{\\mathcal I}_M$")}</th>
        <th style="font-weight:400">${tex(f.gradient_label||"legacy residual")}</th>`).join("")}</tr></thead>
     <tbody>${f.rows.map(r=>{
        const e=(f.eta||{})[r.k]||[];
        return `<tr><td>${tex(r.k)}</td>${
          r.v.map((v,i)=>`<td style="font-variant-numeric:tabular-nums">${sci(v)}</td>
            <td class="muted" style="font-variant-numeric:tabular-nums;font-size:13px">${e[i]!=null?sci2(e[i]):"—"}</td>`).join("")}
          <td>${floorVerdictBadge(r.verdict)}</td></tr>`;
      }).join("")}</tbody>`;
  document.getElementById("floor-verdict").innerHTML=
    (f.caveat?`<span class="badge b-open">Caution</span> ${tex(f.caveat)}<br><br>`:"")
    + tex(f.verdict)
    + (f.verdict_en?`<br><br><i>${tex(f.verdict_en)}</i>`:"");
}

function renderAgenda(){
  const a=DB.agenda, q=i=>document.getElementById(i);
  const capLabel=value=>String(value).replace(/^[a-z]/,c=>c.toUpperCase());
  const displayEq=e=>{
    try{return window.katex.renderToString(e,{displayMode:true,throwOnError:false});}
    catch{return `<code>${esc(e)}</code>`;}
  };
  const decisionItem=x=>typeof x==="string"?`<li>${tex(x)}</li>`:
    `<li><b>${tex(capLabel(x.k))}</b> — ${tex(x.v)}</li>`;
  const o=a.originality;
  if(o && q("origTitle")){
    q("origTitle").innerHTML=tex(o.title);
    q("origBody").innerHTML=`<ol class="note-tree note-depth-4">
      <li><section><h4>Established Precedents</h4><ul>${
        (o.existing||[]).map(x=>`<li><b>${tex(capLabel(x.k))}</b> — ${tex(x.v)}</li>`).join("")
      }</ul></section></li>
      <li><section><h4>Gap</h4><p>${tex(o.gap)}</p>
        <ul><li><b>Why Now</b> — ${tex(o.why_now)}</li></ul></section></li>
      <li><section><h4>Contribution Candidates</h4><ol>${
        (o.new||[]).map(x=>`<li><b>${tex(capLabel(x.k))}</b> — ${tex(x.v)}</li>`).join("")
      }</ol></section></li>
      <li><section><h4>Claim Boundary</h4><ul>${
        (o.not_claiming||[]).map(x=>`<li>${tex(x)}</li>`).join("")
      }</ul></section></li>
      <li><section><h4>Minimum Contribution</h4><p>${tex(o.minimum)}</p></section></li>
    </ol>`;
  }
  q("agFraming").innerHTML=`<b>Framing.</b> ${tex(a.framing)}`;
  if(a.kernel && q("kernelPanel")){
    const K=a.kernel;
    q("kernelPanel").innerHTML=`<h3>${tex(K.title)}</h3>
      <ol class="note-tree note-depth-4">
        <li><section><h4>Definition</h4>${
          (K.eq||[]).map(e=>`<div class="fml" style="text-align:center">${displayEq(e)}</div>`).join("")
        }</section></li>
        <li><section><h4>Interpretation</h4><p>${tex(K.body)}</p></section></li>
        <li><section><h4>Precedents</h4><p>${tex(K.precedent)}</p></section></li>
        <li><section><h4>Novelty Boundary</h4>
          <p>Stochastic kernel 구성 자체는 standard construction. Graph-level estimand와 validation design의 결합에 대한 novelty는 literature audit 이후 판정.</p>
        </section></li>
      </ol>`;
  }
  q("agItems").innerHTML=`<ol class="note-tree note-depth-3 research-discussion-list">${
    (a.items||[]).map(it=>{
      const objectParts=[];
      if(it.senses) objectParts.push(`<ul>${it.senses.map(s=>
        `<li><b>${tex(capLabel(s.k))}</b> — ${tex(s.v)}</li>`).join("")}</ul>`);
      if(it.ours) objectParts.push(`<p><b>Target Estimand.</b> ${tex(it.ours)}</p>`);
      if(it.analogy) objectParts.push(`<p><b>Working Hypothesis.</b> ${tex(it.analogy)}</p>`);
      if(!objectParts.length) objectParts.push(`<p>${tex(it.k)}</p>`);
      return `<li><article class="panel wide research-discussion" id="discussion-${esc(it.id)}"
          aria-labelledby="discussion-title-${esc(it.id)}">
        <header><h3 id="discussion-title-${esc(it.id)}">${esc(it.id)} · ${tex(it.k)}</h3></header>
        <ol class="note-tree note-depth-4">
          <li><section><h4>Why</h4><p>${tex(it.why)}</p></section></li>
          <li><section><h4>Object</h4>${objectParts.join("")}</section></li>
          <li><section><h4>Required Decisions</h4><ul>${
            (it.todo||[]).map(decisionItem).join("")}</ul></section></li>
          ${it.caution?`<li><section><h4>Claim Boundary</h4><p>${tex(it.caution)}</p></section></li>`:""}
          <li><section><h4>Status</h4><p>${tex(it.state)}</p></section></li>
        </ol>
      </article></li>`;
    }).join("")}</ol>`;
  q("agClosing").innerHTML=`<b>Stage Boundary.</b> ${tex(a.closing)}`;
}

function renderSweep(){
  const s=DB.sweep, q=id=>document.getElementById(id);
  q("sweepHead").innerHTML=`<b>${esc(s.status)}</b> · ${esc(s.asof)}<br>${tex(s.headline)}`;
  q("sweepProto").innerHTML=tex(`$M=${s.protocol.M}$ · $p=${s.protocol.p}$ · max_iter ${s.protocol.max_iter} · eps ${s.protocol.eps} · ${s.protocol.optimizer} · polish ${s.protocol.polish}`);
  bars(q("ch-sweep"), s.counts.map(c=>({k:c.k, v:c.v, vlabel:`${c.v} / ${c.of}`})), {max:97});
  const a=s.artifacts;
  q("sweepArt").innerHTML=`
    <p style="font-size:15px;margin:0 0 10px">npz <b>${a.npz}</b> — ${a.nodes.map(esc).join(" · ")}</p>
    <div class="sect">저장됨</div><ul style="font-size:14px;margin:4px 0 10px;padding-left:20px">${
      a.stored.map(x=>`<li>${tex(x)}</li>`).join("")}</ul>
    <div class="sect">없음</div><ul style="font-size:14px;margin:4px 0 10px;padding-left:20px">${
      a.missing.map(x=>`<li>${tex(x)}</li>`).join("")}</ul>
    <p class="fine">${tex(a.consequence)}</p>`;
  q("sweepRange").innerHTML=`<tbody>${s.ranges.map(r=>
    `<tr><td class="k">${tex(r.k)}</td><td>${tex(r.v)}</td>
     <td class="muted" style="font-size:13px">${tex(r.note)}</td></tr>`).join("")}</tbody>`;
  q("sweepEnv").innerHTML=`<tbody>${s.env.map(r=>
    `<tr><td class="k">${esc(r.k)}</td><td><code>${esc(r.v)}</code></td>
     <td class="muted" style="font-size:13px">${esc(r.note)}</td></tr>`).join("")}
     <tr><td class="k">현재 실행</td><td colspan="2">${esc(s.running)}</td></tr></tbody>`;
}

function renderSample(){
  const s=DB.sample, q=i=>document.getElementById(i); if(!s||!q("smpHead")) return;
  q("smpHead").innerHTML=tex(s.headline);
  bars(q("ch-smp"), s.counts.map(c=>({k:c.k,v:c.v,vlabel:String(c.v)})),
    {max:Math.max(...s.counts.map(c=>c.v),1)});
  q("smpMethod").innerHTML=`<tbody>${s.method.map(m=>
    `<tr><td class="k">${esc(m.k)}</td><td>${tex(m.v)}</td></tr>`).join("")}
    <tr><td class="k">Numerical Exclusion</td><td>${tex(s.numerical_exclusion.rule)} — ${tex(s.numerical_exclusion.why)}</td></tr>
    <tr><td class="k">Near-Duplicate Rule</td><td>${tex(s.near_duplicate_rule)}</td></tr></tbody>`;
  let audit=q("smpAudit");
  if(!audit){
    audit=document.createElement("div");
    audit.id="smpAudit";
    audit.className="callout warn";
    (q("smpMethod").closest(".panel")||q("sample")).append(audit);
  }
  audit.innerHTML=`<b>Sample Audit Pending.</b> ${tex(s.open||"Legacy exclusions의 provenance 검토 필요.")}`;
  q("smpDrop").innerHTML=`<thead><tr><th>파일</th><th>처리</th></tr></thead><tbody>${
    s.duplicates.map(d=>`<tr><td>${esc(d.k)}</td><td class="muted" style="font-size:13px">Legacy duplicate candidate → ${esc(d.of)}</td></tr>`).join("")
    + s.excluded.map(e=>`<tr><td>${esc(e.k)}</td><td class="muted" style="font-size:13px">Legacy exclusion record — ${tex(e.why)}</td></tr>`).join("")}</tbody>`;
  const candidates=(s.near_duplicates||[]).map(x=>esc(x.dropped)).join(", ")||"none recorded";
  q("smpNear").innerHTML=`<b>Legacy Exclusions Audit Pending.</b> Near-duplicate candidates provisionally excluded: ${candidates}.`;
}

function renderVision(){
  const v=DB.vision, q=id=>document.getElementById(id);
  q("visionThesis").innerHTML=`<b>${esc(v.target)}</b><br>${tex(v.thesis)}`;
  q("visDisc").innerHTML=`<thead><tr><th>Question</th><th>Test</th><th>Status</th><th>Why</th></tr></thead><tbody>${
    v.discriminators.map(d=>`<tr><td>${tex(d.k)}</td><td>${tex(d.test)}</td>
      <td>${esc(d.state)}</td><td class="muted" style="font-size:13px">${tex(d.why)}</td></tr>`).join("")}</tbody>`;
  q("visPhases").innerHTML=v.phases.map(p=>`
    <div class="claimline"><span class="n">${esc(p.id)}</span>
      <span><span class="t"><b>${tex(p.k)}</b> <span class="badge need-${esc(p.when.replace(/\s/g,""))}">${esc(p.when)}</span></span>
        <ul style="font-size:14px;margin:6px 0 4px;padding-left:20px">${
          p.items.map(x=>`<li>${tex(x)}</li>`).join("")}</ul>
        <span class="s">${tex(p.note)}</span></span></div>`).join("");
  q("visDecK").textContent=v.decision.k+".";
  q("visDecBody").innerHTML=tex(v.decision.body);
  q("visOpt").innerHTML=`<thead><tr><th>선택지</th><th>필요 조건</th><th>위험</th></tr></thead><tbody>${
    v.decision.options.map(o=>`<tr><td>${esc(o.k)}</td><td>${tex(o.need)}</td>
      <td class="muted" style="font-size:13px">${tex(o.risk)}</td></tr>`).join("")}</tbody>`;
}

function renderScope(){
  const s=DB.scope.first_closure;
  const validation=DB.scope.validation;
  document.getElementById("validation-status").innerHTML=tex(validation.status)+
    ' · 아래는 분석·판정 contract. 이번 bounded 실행의 결과와 미충족 조건은 <a href="#corrected-study">corrected evidence</a>에서 별도 보고.';
  document.getElementById("validation-steps").innerHTML=validation.steps.map((step,i)=>
    '<li><section><h4>'+esc((i+1)+". "+step.title)+'</h4><ul>'+
    step.items.map(item=>'<li>'+tex(item)+'</li>').join("")+'</ul></section></li>').join("");
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
  const files={nodes:"nodes",edges:"edges",connectors:"connectors",sweep:"sweep",vision:"vision",agenda:"agenda",sample:"sample",
               claims:"claims",refs:"refs",meas:"measurements",scope:"scope",corrected:"corrected-study",corrected_gates:"corrected-gate-sensitivity",
               sources:"source-map",excerpts_main:"source-excerpts-main",
               excerpts_si:"source-excerpts-si",excerpts_note:"source-excerpts-note"};
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
  renderCorrectedStudy(DB.corrected,DB.corrected_gates);
  renderCalib(); renderByType(); renderFloor(); renderSweep(); renderSample(); renderVision(); renderAgenda();
  renderConnectors(); renderClaims(); renderRefs();
  drawMap();
  document.getElementById("zIn").onclick  = ()=>GRAPH?.zoomIn();
  document.getElementById("zOut").onclick = ()=>GRAPH?.zoomOut();
  document.getElementById("zFit").onclick = ()=>{ GRAPH?.fit(); GRAPH?.select(null); STATE.sel=null; renderPanel(); };
})();
