/* lineage.js — SHL research lineage timeline.
   data/lineage.json 을 읽어 SVG 로 그린다.
   x = year (좌측 밴드는 연도축 밖의 foundation), y = research strand.
   글자색 = 저자 (green: SHL 공저, blue: 외부), 좌측 색띠 = strand. */
(function(){
  "use strict";
  const NS="http://www.w3.org/2000/svg";
  const el=(n,a)=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;};
  const esc=s=>String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

  const LANE_C={geo:"#a8823f",incon:"#5c7bb8",basin:"#4f9e8e",land:"#8b76b5"};
  const C_SHL="var(--success)", C_EXT="var(--information)", C_NEI="var(--point)";

  const Y0=2009, Y1=2026.6, PX=86, LH=124, PADL=150, PADT=46, NW=154, NH=58;
  const PRE_X=PADL+8, PRE_GAP=NW+18, AXIS0=PRE_X+2*PRE_GAP+48;

  window.renderLineage=function(DB){
    const host=document.getElementById("lineagec");
    const panel=document.getElementById("lineage-panel");
    if(!host||!DB||!DB.nodes) return;

    const lanes=DB.lanes, laneIx={};
    lanes.forEach((L,i)=>laneIx[L.id]=i);
    const N=DB.nodes.map(n=>Object.assign({},n,{li:laneIx[n.lane]}));
    const byId={}; N.forEach(n=>byId[n.id]=n);
    const L=DB.links.filter(k=>byId[k.from]&&byId[k.to]);

    const xOf=y=>AXIS0+(y-Y0)*PX;
    const yOf=i=>PADT+i*LH+LH/2;
    const AC=n=>n.anchor?C_NEI:(n.shl?C_SHL:C_EXT);

    // stagger nodes sharing (x-slot, lane)
    const cnt={},seen={};
    N.forEach(n=>{const k=(n.pre!==undefined?"p"+n.pre:n.year)+"_"+n.li;cnt[k]=(cnt[k]||0)+1;});
    N.forEach(n=>{
      const k=(n.pre!==undefined?"p"+n.pre:n.year)+"_"+n.li;
      seen[k]=(seen[k]||0)+1;
      const slot=seen[k]-1, tot=cnt[k];
      n.cx=(n.pre!==undefined)?PRE_X+n.pre*PRE_GAP+NW/2:xOf(n.year);
      n.cy=yOf(n.li)+(slot-(tot-1)/2)*(NH+9);
    });

    const W=xOf(Y1)+80, H=PADT+lanes.length*LH+52;
    const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,width:W,height:H,
      role:"img","aria-label":"research lineage timeline"});

    // foundation band
    svg.appendChild(el("rect",{x:PRE_X-14,y:PADT-22,width:2*PRE_GAP+14,height:H-PADT-8,
      fill:"var(--surface)"}));
    svg.appendChild(el("line",{x1:AXIS0-24,y1:PADT-22,x2:AXIS0-24,y2:H-32,
      stroke:"var(--hairline)","stroke-width":1}));
    let t=el("text",{x:PRE_X-10,y:PADT-30,class:"lin-lane"});
    t.textContent="foundation · 연도축 밖"; svg.appendChild(t);

    // year grid
    for(let y=2010;y<=2026;y+=2){
      svg.appendChild(el("line",{x1:xOf(y),y1:PADT-22,x2:xOf(y),y2:H-32,
        stroke:"var(--hairline)","stroke-width":1,opacity:".45"}));
      t=el("text",{x:xOf(y),y:H-14,class:"lin-year","text-anchor":"middle"});
      t.textContent=y; svg.appendChild(t);
    }
    lanes.forEach((Ln,i)=>{
      t=el("text",{x:10,y:yOf(i)-NH/2-11,class:"lin-lane"});
      t.textContent=Ln.label; svg.appendChild(t);
      svg.appendChild(el("rect",{x:10,y:yOf(i)-NH/2-8,width:26,height:3,fill:LANE_C[Ln.id]}));
    });

    // edges
    const gE=el("g",{}); svg.appendChild(gE);
    const eEls=[];
    L.forEach((k,i)=>{
      const A=byId[k.from],B=byId[k.to];
      const x1=A.cx+NW/2,y1=A.cy,x2=B.cx-NW/2,y2=B.cy;
      const dx=Math.max(32,(x2-x1)*0.42);
      const col=k.key?C_NEI:((A.shl===false||B.shl===false)?C_EXT:LANE_C[B.lane]);
      const p=el("path",{class:"lin-edge",fill:"none",stroke:col,
        d:`M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}`});
      p.addEventListener("click",ev=>{ev.stopPropagation();showEdge(i);});
      gE.appendChild(p); eEls.push(p);
    });

    // nodes
    const gN=el("g",{}); svg.appendChild(gN);
    const nEls={};
    N.forEach(n=>{
      const g=el("g",{class:"lin-node",tabindex:"0",role:"button"});
      g.setAttribute("aria-label",n.title);
      const ac=AC(n);
      g.appendChild(el("rect",{class:"lin-card",x:n.cx-NW/2,y:n.cy-NH/2,width:NW,height:NH,rx:3,
        fill:"var(--canvas)",stroke:ac,"stroke-width":n.nei?(n.nei>1?2.2:1.5):1,
        "stroke-opacity":n.nei?1:.45}));
      g.appendChild(el("rect",{x:n.cx-NW/2,y:n.cy-NH/2,width:4,height:NH,fill:LANE_C[n.lane]}));
      let y0=n.cy-NH/2+15;
      t=el("text",{x:n.cx-NW/2+13,y:y0,class:"lin-yr",fill:ac});
      t.textContent=n.year+(n.nei?"  ●":""); g.appendChild(t);
      // wrap title into <=3 lines
      const words=String(n.title).split(" ");let line="",ln=0;
      const put=s=>{const e=el("text",{x:n.cx-NW/2+13,y:y0+14+ln*12.5,class:"lin-t",fill:ac});
        e.textContent=s;g.appendChild(e);ln++;};
      for(const w of words){
        if(ln>=3) break;
        const test=line?line+" "+w:w;
        if(test.length>25){put(line);line=w;} else line=test;
      }
      if(line&&ln<3) put(line.length>25?line.slice(0,24)+"…":line);
      g.addEventListener("click",ev=>{ev.stopPropagation();showNode(n.id);});
      g.addEventListener("keydown",ev=>{if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();showNode(n.id);}});
      gN.appendChild(g); nEls[n.id]=g;
    });

    host.innerHTML=""; host.appendChild(svg);
    svg.addEventListener("click",()=>clear());

    function clear(){
      eEls.forEach(e=>e.classList.remove("on","dim"));
      Object.values(nEls).forEach(g=>g.classList.remove("dim"));
    }
    function tag(n){
      const lane=lanes[n.li]?lanes[n.li].label:"—";
      return lane+" · "+(n.anchor?"NEI":(n.shl?"SHL 공저":"외부 문헌"));
    }
    function showNode(id){
      clear();
      const n=byId[id];
      const rel=L.map((k,i)=>({k,i})).filter(o=>o.k.from===id||o.k.to===id);
      const keep=new Set([id]); rel.forEach(o=>{keep.add(o.k.from);keep.add(o.k.to);});
      eEls.forEach((e,i)=>e.classList.add(rel.some(o=>o.i===i)?"on":"dim"));
      Object.entries(nEls).forEach(([k,g])=>{if(!keep.has(k))g.classList.add("dim");});
      const items=rel.map(o=>{
        const other=o.k.from===id?byId[o.k.to]:byId[o.k.from];
        return `<li><b>${o.k.from===id?"→":"←"} ${other.year} · ${esc(other.title)}</b><br>${o.k.text}</li>`;
      }).join("");
      panel.innerHTML=
        `<p class="lin-tag" style="color:${AC(n)}">${esc(tag(n))}</p>`+
        `<h4>${esc(n.title)}</h4>`+
        `<p class="lin-cite">${esc(n.authors)} · ${esc(n.venue)}</p>`+
        `<p class="lin-role">${n.role}</p>`+
        (items?`<div class="lin-links"><p class="lin-lh">연결 ${rel.length}건</p><ul>${items}</ul></div>`:"");
      if(typeof window.renderMathInElement==="function")
        window.renderMathInElement(panel,{delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],throwOnError:false});
    }
    function showEdge(i){
      clear();
      const k=L[i],A=byId[k.from],B=byId[k.to];
      eEls.forEach((e,j)=>e.classList.add(j===i?"on":"dim"));
      Object.entries(nEls).forEach(([id,g])=>{if(id!==k.from&&id!==k.to)g.classList.add("dim");});
      panel.innerHTML=
        `<p class="lin-tag" style="color:${k.key?C_NEI:C_EXT}">link</p>`+
        `<h4>${esc(A.year)} ${esc(A.title)}　→　${esc(B.year)} ${esc(B.title)}</h4>`+
        `<p class="lin-cite">${esc(A.venue)}　→　${esc(B.venue)}</p>`+
        `<p class="lin-role">${k.text}</p>`;
      if(typeof window.renderMathInElement==="function")
        window.renderMathInElement(panel,{delimiters:[{left:"$$",right:"$$",display:true},{left:"$",right:"$",display:false}],throwOnError:false});
    }
    showNode("nei");
  };
})();
