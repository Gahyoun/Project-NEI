import { makeGraph } from "./graph.js";

/* NEI 아키텍처 — data/*.json 에서 지도·막대그림·표를 만든다. */

const DB = {}, STATE = { off: new Set(), sel: null, claim: "all", refArea: "all" };
const KO = { theorem:"정리", measured:"측정", open:"미해결", withdrawn:"철회",
             caution:"주의", conjecture:"가설", given:"입력", verdict:"판정" };
const esc = s => String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const badge = s => `<span class="badge b-${s}">${KO[s]||s}</span>`;

function tex(s){ return String(s).replace(/\$([^$]+)\$/g,(_,m)=>{
  try{ return katex.renderToString(m,{throwOnError:false}); }catch{ return esc(m); } }); }
function texB(s){ try{ return katex.renderToString(s,{throwOnError:false}); }catch{ return esc(s); } }

/* ── 막대그림 ─────────────────────────────────────────── */
function cap(id,t,s){ const e=document.getElementById(id); if(e)
  e.innerHTML=`<span class="t">${tex(esc(t))}</span>${s?`<span class="s">${tex(esc(s))}</span>`:""}`; }

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
  cap("cap-status","주장 22건의 구성","정리 · 측정 · 미해결 · 철회");
  bars(document.getElementById("ch-status"),
    ["theorem","measured","open","withdrawn"].map(s=>({k:KO[s],v:cnt[s]||0})),
    { max:Math.max(...Object.values(cnt)), fmt:v=>`${v}건` });
}

/* ── 지도 ─────────────────────────────────────────────── */
let GRAPH = null;
function drawMap(){
  const host=document.getElementById("mapc");
  const shown=DB.nodes.nodes.filter(n=>!STATE.off.has(n.domain));
  const ids=new Set(shown.map(n=>n.id));
  const hy=DB.scope.pre2026;
  GRAPH = makeGraph(host,{
    nodes: shown, domains: DB.nodes.domains,
    edges: DB.edges.edges.filter(e=>ids.has(e.from)&&ids.has(e.to)),
    hyper: { label: hy.label, color: hy.color,
             members: hy.members.filter(i=>ids.has(i)) },
    onSelect: id => { STATE.sel=id; renderPanel(); }
  });
}
function renderMapLegend(){
  const el=document.getElementById("mapLegend"); if(!el) return;
  el.innerHTML=Object.entries(DB.nodes.domains).map(([,m])=>
      `<span><i style="background:${m.color}"></i>${m.label}</span>`).join("")
    +`<span style="margin-left:12px"><i style="background:#256ef4"></i>정리</span>`
    +`<span><i style="background:#ab5b00"></i>측정</span>`
    +`<span><i style="background:#6d7882"></i>미해결</span>`
    +`<span><i style="background:${DB.scope.pre2026.color}"></i>PRE 2026 hyperedge</span>`;
}

function renderPanel(){
  const el=document.getElementById("panel");
  const n=DB.nodes.nodes.find(x=>x.id===STATE.sel);
  if(!n){ el.innerHTML='<p class="muted">마디를 선택하세요.</p>'; return; }
  const lbl=i=>DB.nodes.nodes.find(x=>x.id===i)?.label||i;
  const inc=DB.edges.edges.filter(e=>e.to===n.id), out=DB.edges.edges.filter(e=>e.from===n.id);
  const vias=[...new Set([...inc,...out].map(e=>e.via))];
  el.innerHTML=`
    <h3>${esc(n.label)}</h3>
    <p class="muted" style="font-size:13px;margin:0 0 12px">${badge(n.status)}
      &nbsp;${esc(DB.nodes.domains[n.domain].label)}</p>
    ${n.formula?`<div class="fml">${texB(n.formula)}</div>`:""}
    <p>${tex(esc(n.def))}</p>
    ${vias.length?`<div class="sect">지나는 연결요소</div><ul>${
      vias.map(v=>`<li>${tex(DB.connectors[v].label)}</li>`).join("")}</ul>`:""}
    ${inc.length?`<div class="sect">들어오는 연결</div><ul>${
      inc.map(e=>`<li>${badge(e.status)} ${esc(lbl(e.from))} → <i>${esc(e.label)}</i></li>`).join("")}</ul>`:""}
    ${out.length?`<div class="sect">나가는 연결</div><ul>${
      out.map(e=>`<li>${badge(e.status)} <i>${esc(e.label)}</i> → ${esc(lbl(e.to))}</li>`).join("")}</ul>`:""}
    ${n.refs.length?`<div class="sect">참고문헌</div><ul>${
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
    on?STATE.off.add(x.dataset.d):STATE.off.delete(x.dataset.d); drawMap(); });
}
function renderConnectors(){
  document.getElementById("connectors").innerHTML=
    Object.entries(DB.connectors).filter(([k])=>!k.startsWith("_")).map(([,c])=>`
      <div class="card"><h3>${tex(c.label)}</h3>
        <p class="cx">잇는 것 — ${c.connects.map(esc).join(" · ")}</p>
        <p>${tex(esc(c.why))}</p></div>`).join("");
}
function renderClaims(){
  const b=document.getElementById("claimFilter");
  b.innerHTML=["all","theorem","measured","open","withdrawn"].map(k=>
    `<button class="tag" data-k="${k}" aria-pressed="${k===STATE.claim}">${
      k==="all"?"전체":KO[k]}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{STATE.claim=x.dataset.k;renderClaims();});
  const rows=DB.claims.claims.filter(c=>STATE.claim==="all"||c.status===STATE.claim);
  document.getElementById("claimsTable").innerHTML=
    `<thead><tr><th>id</th><th>상태</th><th>주장</th><th>근거</th></tr></thead><tbody>${
      rows.map(c=>`<tr><td class="k">${esc(c.id)}</td><td>${badge(c.status)}</td>
        <td>${tex(esc(c.text))}</td>
        <td class="muted" style="font-size:13px">${tex(esc(c.basis))}${
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
    `<thead><tr><th>키</th><th>문헌</th><th>왜</th></tr></thead><tbody>${
      items.map(([k,r])=>`<tr id="ref-${esc(k)}"><td class="k"><code>${esc(k)}</code>${
        r.verified?"":' <span class="badge b-open">미확인</span>'}</td>
        <td>${esc(r.authors)} (${r.year}). ${esc(r.title)}. <i>${esc(r.venue)}</i>${
          r.volume?" "+esc(r.volume):""}${r.pages?", "+esc(r.pages):""}.</td>
        <td class="muted" style="font-size:13px">${esc(r.why)}</td></tr>`).join("")}</tbody>`;
}

/* ── PRE 2026 절단선 ──────────────────────────────────── */
function renderScope(){
  const s=DB.scope.pre2026;
  document.getElementById("scopeThesis").innerHTML=tex(esc(s.thesis));
  document.getElementById("scopeClaims").innerHTML=s.four_claims.map(c=>`
    <div class="claimline"><span class="n">${c.n}</span>
      <span><span class="t">${tex(esc(c.t))}</span>
        <span class="s">${tex(esc(c.state))}</span></span></div>`).join("");
  document.getElementById("scopeWhy").innerHTML=
    s.why_this_line.map(w=>`<li>${tex(esc(w))}</li>`).join("");
  document.getElementById("scopeTodo").innerHTML=
    `<thead><tr><th>항목</th><th>내용</th><th>지위</th></tr></thead><tbody>${
      s.todo.map(x=>`<tr><td>${tex(esc(x.k))}</td>
        <td class="muted" style="font-size:13px">${tex(esc(x.w))}</td>
        <td><span class="badge need-${esc(x.need)}">${esc(x.need)}</span></td></tr>`).join("")}</tbody>`;
  document.getElementById("scopeOut").innerHTML=
    `<thead><tr><th>항목</th><th>내용</th><th>어디로</th></tr></thead><tbody>${
      s.excluded.map(x=>`<tr><td>${tex(esc(x.k))}</td>
        <td class="muted" style="font-size:13px">${tex(esc(x.w))}</td>
        <td class="k">${esc(x.to)}</td></tr>`).join("")}</tbody>`;
}

/* ── landscape ────────────────────────────────────────── */
const LS={ rigid:{n:"강체형",f:x=>0.9*(x-0.5)**2},
  multi:{n:"다중안정형",f:x=>0.28*Math.cos(6*Math.PI*x)/3+0.55*(x-0.5)**2},
  floppy:{n:"floppy",f:x=>0.30*Math.pow(Math.abs(x-0.5)*2,4)} };
let lsK="multi";
const rngf=s=>{let a=s>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};};
function descend(f,x){const h=1e-4,e=0.004;
  for(let i=0;i<5000;i++){const g=(f(x+h)-f(x-h))/(2*h);x-=e*g;
    if(x<-0.15)x=-0.15; if(x>1.15)x=1.15; if(Math.abs(g)<1e-10)break;} return x;}
function drawLS(){
  const cv=document.getElementById("ls"),g=cv.getContext("2d"),W=cv.width,H=cv.height,f=LS[lsK].f;
  g.clearRect(0,0,W,H);
  const lo=-0.15,hi=1.15,x2p=x=>44+(x-lo)/(hi-lo)*(W-70);
  let a=Infinity,b=-Infinity;
  for(let i=0;i<=500;i++){const v=f(lo+(hi-lo)*i/500);a=Math.min(a,v);b=Math.max(b,v);}
  const y2p=v=>H-104-(v-a)/(b-a+1e-12)*(H-140);
  g.strokeStyle="#1e2124";g.lineWidth=1.8;g.beginPath();
  for(let i=0;i<=500;i++){const x=lo+(hi-lo)*i/500;i?g.lineTo(x2p(x),y2p(f(x))):g.moveTo(x2p(x),y2p(f(x)));}
  g.stroke();
  const M=600,r=rngf(20260904),T=[];
  for(let m=0;m<M;m++)T.push(descend(f,r()));
  const B=90,hist=new Array(B).fill(0);
  T.forEach(t=>{const i=Math.floor((t-lo)/(hi-lo)*B);if(i>=0&&i<B)hist[i]++;});
  const hm=Math.max(...hist,1);
  g.fillStyle="#256ef4";
  for(let i=0;i<B;i++){ if(!hist[i])continue;
    const x0=x2p(lo+(hi-lo)*i/B),x1=x2p(lo+(hi-lo)*(i+1)/B),h=hist[i]/hm*70;
    g.fillRect(x0,H-26-h,Math.max(x1-x0-1,1.4),h); }
  g.fillStyle="#6d7882";g.font="12px system-ui";
  g.fillText("stress",44,18); g.fillText(`terminal 분포  (M=${M}, ${B} bin)`,44,H-8);
  const mu=T.reduce((s,v)=>s+v,0)/M, va=T.reduce((s,v)=>s+(v-mu)**2,0)/M;
  const p=hist.map(h=>h/M).filter(v=>v>0), pr=1/p.reduce((s,v)=>s+v*v,0);
  document.getElementById("lsOut").innerHTML=`
    <div><b>${LS[lsK].n}</b></div>
    <div>분산 (𝓘 대응) <b>${va.toFixed(5)}</b></div>
    <div>점유 bin <b>${p.length}</b> / ${B}</div>
    <div>participation ratio <b>${pr.toFixed(2)}</b></div>
    <p class="fine" style="max-width:26ch">분산은 degeneracy 의 크기를,
    participation ratio 는 그것이 차지하는 자유도의 수를 준다. 다중안정형은 좁은 봉우리
    여러 개로, floppy 는 넓은 골 하나로 같은 분산에 도달하며, 두 경우를 participation
    ratio 가 가른다.</p>`;
}
function renderLsBtns(){
  const b=document.getElementById("lsButtons");
  b.innerHTML=Object.entries(LS).map(([k,v])=>
    `<button class="tag" data-k="${k}" aria-pressed="${k===lsK}">${v.n}</button>`).join("");
  b.querySelectorAll("button").forEach(x=>x.onclick=()=>{lsK=x.dataset.k;renderLsBtns();drawLS();});
}

/* ── 부팅 ─────────────────────────────────────────────── */
(async function(){
  const files={nodes:"nodes",edges:"edges",connectors:"connectors",
               claims:"claims",refs:"refs",meas:"measurements",scope:"scope"};
  try{
    await Promise.all(Object.entries(files).map(async([k,f])=>{
      const r=await fetch(`data/${f}.json`);
      if(!r.ok) throw new Error(`data/${f}.json ${r.status}`);
      DB[k]=await r.json(); }));
  }catch(e){
    document.getElementById("mapc").innerHTML=
      `<p class="err">데이터를 불러오지 못했습니다: ${esc(e.message)}<br>
       <span class="muted">file:// 로 열면 브라우저가 fetch 를 막습니다.
       <code>python3 -m http.server</code> 또는 GitHub Pages 에서 여세요.</span></p>`;
    return;
  }
  renderCharts(); renderFilters(); renderMapLegend(); renderScope();
  renderConnectors(); renderClaims(); renderRefs(); renderLsBtns(); drawLS();
  drawMap();
  document.getElementById("zIn").onclick  = ()=>GRAPH?.zoomIn();
  document.getElementById("zOut").onclick = ()=>GRAPH?.zoomOut();
  document.getElementById("zFit").onclick = ()=>{ GRAPH?.fit(); GRAPH?.select(null); };
  renderMathInElement(document.body,{delimiters:[
    {left:"$",right:"$",display:false}],throwOnError:false});
})();
