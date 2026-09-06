/* Authorship belongs to nodes; provenance belongs to typed edges.
   Static local assets and the offline data bundle also support file://. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const svgEl = (name, attrs = {}) => {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  };
  const esc = value => String(value ?? "").replace(/[&<>"']/g,
    c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const safeURL = value => /^(https:\/\/|#[a-z])/i.test(value || "") ? value : "";
  const strandColors = {geo:"#a8823f", incon:"#5c7bb8", basin:"#4f9e8e", land:"#8b76b5"};
  const authorColor = n => n.anchor ? "var(--point)" : n.shl ? "var(--success)" : "var(--information)";
  const math = node => {
    if (typeof window.renderMathInElement !== "function") return;
    window.renderMathInElement(node, {
      delimiters: [
        {left:"$$", right:"$$", display:true}, {left:"\\[", right:"\\]", display:true},
        {left:"$", right:"$", display:false}, {left:"\\(", right:"\\)", display:false}
      ],
      throwOnError:false
    });
  };

  window.renderLineage = function (DB) {
    const host = document.getElementById("lineagec");
    const panel = document.getElementById("lineage-panel");
    const legend = document.getElementById("lineage-relations");
    if (!host || !panel || !DB?.nodes || !DB?.relation_types) return;

    const types = Object.fromEntries(DB.relation_types.map(t => [t.id, t]));
    const nodes = DB.nodes.map(n => ({...n}));
    const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
    const links = DB.links.filter(k => byId[k.from] && byId[k.to] && types[k.type]);
    const laneIndex = Object.fromEntries(DB.lanes.map((lane, i) => [lane.id, i]));
    const NW = 184, NH = 90, PX = 246, LEFT = 206, TOP = 55;
    const AXIS = LEFT + 2 * (NW + 38) + 55, BASE = 2009;
    const yearX = year => AXIS + (year - BASE) * PX;
    const groups = {};
    nodes.forEach(n => {
      n.slotKey = n.lane + ":" + (n.pre !== undefined ? "pre" + n.pre : n.year);
      (groups[n.slotKey] ||= []).push(n);
    });
    const laneBoxes = [];
    let cursorY = TOP;
    DB.lanes.forEach(lane => {
      const maxStack = Math.max(1, ...Object.values(groups)
        .filter(g => g[0].lane === lane.id).map(g => g.length));
      const height = maxStack * (NH + 26) + 55;
      laneBoxes.push({y:cursorY, height, center:cursorY + height / 2});
      cursorY += height;
    });
    nodes.forEach(n => {
      const group = groups[n.slotKey], slot = group.indexOf(n);
      n.cx = n.pre !== undefined ? LEFT + n.pre * (NW + 38) + NW / 2 : yearX(n.year);
      n.cy = laneBoxes[laneIndex[n.lane]].center + (slot - (group.length - 1) / 2) * (NH + 26);
    });
    const W = yearX(2026) + NW / 2 + 42, H = cursorY + 48;
    const svg = svgEl("svg", {viewBox:"0 0 " + W + " " + H, width:W, height:H,
      role:"group", "aria-label":"Research lineage: papers and typed relations"});
    const defs = svgEl("defs");
    DB.relation_types.forEach(type => {
      const marker = svgEl("marker", {id:"lin-arrow-" + type.id, viewBox:"0 0 10 10",
        refX:9, refY:5, markerWidth:5, markerHeight:5, orient:"auto-start-reverse"});
      marker.append(svgEl("path", {d:"M 0 0 L 10 5 L 0 10 z", fill:type.color}));
      defs.append(marker);
    });
    svg.append(defs);
    svg.append(svgEl("rect", {x:LEFT - 16, y:TOP - 26, width:2 * (NW + 38), height:H - TOP,
      fill:"var(--surface)"}));
    const label = (text, x, y, cls, attrs = {}) => {
      const node = svgEl("text", {x,y,class:cls,...attrs});
      node.textContent = text; svg.append(node); return node;
    };
    label("FOUNDATIONS · 연도축 밖", LEFT, 22, "lin-lane");
    const years = [...new Set(nodes.filter(n => n.pre === undefined).map(n => n.year))].sort();
    years.forEach(year => {
      svg.append(svgEl("line", {x1:yearX(year), x2:yearX(year), y1:TOP - 24, y2:H - 32,
        stroke:"var(--hairline)", opacity:.4}));
      label(year, yearX(year), H - 11, "lin-year", {"text-anchor":"middle"});
    });
    DB.lanes.forEach((lane, i) => {
      const box = laneBoxes[i];
      const words = lane.label.split(" ");
      let line = "", row = 0;
      for (const word of words) {
        if ((line + " " + word).trim().length > 22) {
          label(line, 12, box.center - 15 + row++ * 17, "lin-lane"); line = word;
        } else line = (line + " " + word).trim();
      }
      label(line, 12, box.center - 15 + row * 17, "lin-lane");
      svg.append(svgEl("rect", {x:12, y:box.center + 10 + row * 17, width:28, height:3,
        fill:strandColors[lane.id]}));
      svg.append(svgEl("line", {x1:LEFT-16, x2:W-12, y1:box.y+box.height, y2:box.y+box.height,
        stroke:"var(--hairline)", opacity:.4}));
    });

    let selectedNode = null, selectedEdge = null, activeType = null;
    const edgeEls = [], nodeEls = {};
    const edgeLayer = svgEl("g");
    svg.append(edgeLayer);
    links.forEach((link, i) => {
      const a = byId[link.from], b = byId[link.to], type = types[link.type];
      const outgoing=links.filter(k=>k.from===link.from), incoming=links.filter(k=>k.to===link.to);
      const port=(items,item)=>items.length>1 ? (items.indexOf(item)/(items.length-1)-.5)*(NH-24) : 0;
      let x1=a.cx+NW/2+3, y1=a.cy+port(outgoing,link), x2=b.cx-NW/2-5, y2=b.cy+port(incoming,link);
      let path;
      if (x2 > x1 + 10) {
        // Route through lane margins, not through intermediate paper cards.
        const box=laneBoxes[laneIndex[a.lane]];
        const corridor=box.y+box.height-12-(i%7)*2.6;
        const leg=Math.min(25,(x2-x1)/3);
        path="M "+x1+" "+y1+" C "+(x1+leg)+" "+y1+", "+(x1+leg)+" "+corridor+", "+(x1+leg)+" "+corridor+
          " L "+(x2-leg)+" "+corridor+" C "+(x2-leg)+" "+corridor+", "+(x2-leg)+" "+y2+", "+x2+" "+y2;
      } else {
        // Same-year papers use the right-hand inter-column corridor.
        x1=a.cx+NW/2+3; x2=b.cx+NW/2+5;
        const bend=Math.max(x1,x2)+48;
        path="M "+x1+" "+y1+" C "+bend+" "+y1+", "+bend+" "+y2+", "+x2+" "+y2;
      }
      const group=svgEl("g", {class:"lin-edge-group", tabindex:"0", role:"button",
        "data-link-type":link.type, "data-from":link.from, "data-to":link.to,
        "aria-label":type.label+": "+a.short_title+" → "+b.short_title});
      const title=svgEl("title"); title.textContent=type.label+" · "+link.text; group.append(title);
      group.append(svgEl("path", {class:"lin-edge-hit", d:path, fill:"none", stroke:"transparent", "stroke-width":13}));
      group.append(svgEl("path", {class:"lin-edge", d:path, fill:"none", stroke:type.color,
        "stroke-dasharray":type.dash, "marker-end":"url(#lin-arrow-"+type.id+")"}));
      const activate=event=>{event.stopPropagation(); showEdge(i);};
      group.addEventListener("click", activate);
      group.addEventListener("keydown", event=>{
        if (event.key==="Enter" || event.key===" ") {event.preventDefault(); activate(event);}
      });
      edgeLayer.append(group); edgeEls.push(group);
    });
    nodes.forEach(n => {
      const group=svgEl("g", {class:"lin-node", tabindex:"0", role:"button",
        "data-node-id":n.id, "aria-label":n.year+" · "+n.authors+" · "+n.title});
      const title=svgEl("title"); title.textContent=n.authors+" · "+n.title; group.append(title);
      group.append(svgEl("rect", {class:"lin-card", x:n.cx-NW/2, y:n.cy-NH/2, width:NW, height:NH,
        rx:6, fill:"var(--canvas)", stroke:authorColor(n), "stroke-width":n.anchor?2.2:1.4}));
      group.append(svgEl("rect", {x:n.cx-NW/2, y:n.cy-NH/2+7, width:4, height:NH-14,
        fill:strandColors[n.lane]}));
      const surname=n.id==="sw82"?"Stillinger–Weber":n.id==="deleeuw"?"de Leeuw":
        n.id==="borgmair"?"Borg & Mair":n.id==="nei"?"NEI":
        n.authors.split(",")[0].trim().split(" ").at(-1);
      const author=svgEl("text", {x:n.cx-NW/2+13, y:n.cy-NH/2+19, class:"lin-yr", fill:authorColor(n)});
      author.textContent=n.year+" · "+surname+(links.some(k=>k.from===n.id&&k.to==="nei")?" ●":"");
      group.append(author);
      const words=(n.short_title || n.title).split(" ");
      const lines=[]; let line="";
      words.forEach(word=>{
        if ((line+" "+word).trim().length>23 && line) {lines.push(line); line=word;}
        else line=(line+" "+word).trim();
      });
      if(line)lines.push(line);
      lines.slice(0,3).forEach((text,row)=>{
        const t=svgEl("text", {x:n.cx-NW/2+13, y:n.cy-NH/2+40+row*16, class:"lin-t", fill:authorColor(n)});
        t.textContent=text; group.append(t);
      });
      group.addEventListener("click", event=>{event.stopPropagation(); showNode(n.id);});
      group.addEventListener("keydown", event=>{
        if(event.key==="Enter" || event.key===" ") {event.preventDefault(); showNode(n.id);}
      });
      svg.append(group); nodeEls[n.id]=group;
    });
    // 선택된 edge를 node 위로 올려 카드에 가리지 않게 하는 layer
    const topLayer = svgEl("g", {class:"lin-top"});
    svg.append(topLayer);
    host.replaceChildren(svg);
    svg.addEventListener("click", ()=>reset());

    const badge = type => '<span class="lin-type" style="--relation-color:'+type.color+'">'+esc(type.label)+'</span>';
    const source = (n, locator) => {
      const url=safeURL(n.source_url);
      const caption=n.doi?"DOI: "+n.doi:n.anchor?"Definition":"출처";
      return '<p class="lin-evidence"><b>Evidence:</b> '+esc(locator || n.source_note)+' '+
        (url?'<a href="'+esc(url)+'"'+(url.startsWith("#")?"":' target="_blank" rel="noopener noreferrer"')+'>'+esc(caption)+'</a>':"")+"</p>";
    };
    const evidence = link => link.evidence.map(e=>source(byId[e.node],e.locator)).join("");
    const relation = link => badge(types[link.type])+'<p><b>Inherited component:</b> '+link.text+'</p>'+
      '<p><b>Boundary of transfer:</b> '+link.boundary+'</p>'+evidence(link);
    function highlight() {
      const keep=new Set();
      if(selectedNode)keep.add(selectedNode);
      topLayer.replaceChildren();
      edgeEls.forEach((group,i)=>{
        const k=links[i];
        const visible=!activeType || k.type===activeType;
        group.classList.toggle("filtered",!visible);
        group.setAttribute("tabindex",visible?"0":"-1");
        const chosen=visible && (selectedEdge===i || !!selectedNode && (k.from===selectedNode || k.to===selectedNode));
        group.classList.toggle("on",chosen);
        group.classList.toggle("dim",visible && (selectedNode!==null || selectedEdge!==null) && !chosen);
        if(chosen){
          keep.add(k.from);keep.add(k.to);
          const vis=group.querySelector(".lin-edge");
          if(vis)topLayer.append(vis.cloneNode(true));
        }
      });
      Object.entries(nodeEls).forEach(([id,group])=>{
        group.classList.toggle("dim",(selectedNode!==null || selectedEdge!==null) && !keep.has(id));
        group.classList.toggle("selected",id===selectedNode);
      });
    }
    function showNode(id) {
      selectedNode=id; selectedEdge=null; highlight();
      const n=byId[id];
      const related=links.map((link,i)=>({link,i})).filter(({link})=>
        (link.from===id || link.to===id) && (!activeType || link.type===activeType));
      panel.innerHTML='<p class="lin-tag" style="color:'+authorColor(n)+'">'+
        esc(DB.lanes[laneIndex[n.lane]].label)+" · "+(n.anchor?"NEI":n.shl?"SHL 공저":"외부 문헌")+"</p>"+
        "<h4>"+esc(n.title)+'</h4><p class="lin-cite">'+esc(n.authors)+" · "+esc(n.venue)+"</p>"+
        source(n)+'<p class="lin-role">'+n.role+'</p>'+
        '<dl class="lin-profile"><dt>Original object</dt><dd>'+esc(n.object)+"</dd>"+
        "<dt>Source of randomness</dt><dd>"+esc(n.randomness)+"</dd>"+
        "<dt>Inherited component</dt><dd>"+esc(n.inherited)+"</dd>"+
        "<dt>Boundary of transfer</dt><dd>"+esc(n.boundary)+"</dd></dl>"+
        '<div class="lin-links"><p class="lin-lh">연결 '+related.length+'건 · 펼쳐서 근거 확인</p><ul>'+
        related.map(({link,i})=>{
          const other=byId[link.from===id?link.to:link.from];
          return '<li><details><summary>'+badge(types[link.type])+" "+(link.from===id?"→ ":"← ")+
            esc(other.year+" · "+other.short_title)+'</summary>'+relation(link)+
            '<button type="button" data-lineage-node="'+esc(other.id)+'">관련 논문 보기</button>'+
            '<button type="button" data-lineage-edge="'+i+'">연결 강조</button></details></li>';
        }).join("")+"</ul></div>";
      bindPanel(); math(panel);
    }
    function showEdge(i) {
      selectedNode=null; selectedEdge=i; highlight();
      const link=links[i],a=byId[link.from],b=byId[link.to];
      panel.innerHTML='<h4>'+esc(a.year+" · "+a.short_title)+" → "+esc(b.year+" · "+b.short_title)+"</h4>"+
        '<p class="lin-cite">'+esc(a.authors)+" → "+esc(b.authors)+"</p>"+relation(link)+
        '<button type="button" data-lineage-node="'+esc(a.id)+'">Source 논문</button> '+
        '<button type="button" data-lineage-node="'+esc(b.id)+'">Target 논문</button>';
      bindPanel(); math(panel);
    }
    function bindPanel() {
      panel.querySelectorAll("[data-lineage-node]").forEach(button=>{
        button.addEventListener("click",()=>showNode(button.dataset.lineageNode));
      });
      panel.querySelectorAll("[data-lineage-edge]").forEach(button=>{
        button.addEventListener("click",()=>showEdge(Number(button.dataset.lineageEdge)));
      });
    }
    function updateLegend() {
      if(!legend)return;
      legend.innerHTML=DB.relation_types.map(type=>
        '<button type="button" class="lin-filter" data-lineage-type="'+type.id+'" aria-pressed="'+
        (activeType===type.id)+'" style="--relation-color:'+type.color+'" title="'+esc(type.description)+'">'+
        badge(type)+" · "+links.filter(k=>k.type===type.id).length+"</button>").join("");
      legend.querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>{
        activeType=activeType===button.dataset.lineageType?null:button.dataset.lineageType;
        selectedEdge=null; updateLegend();
        if(selectedNode)showNode(selectedNode);else reset(false);
      }));
    }
    function reset(clearType=true) {
      selectedNode=null;selectedEdge=null;
      if(clearType)activeType=null;
      updateLegend();highlight();
      panel.innerHTML='<h4>계승 관계 선택</h4><p>Node 선택: original object와 transfer boundary. '+
        'Link 선택: 관계 유형·계승 내용·출처. Conceptual analogy는 historical influence 또는 mathematical implication의 증거가 아님.</p>';
    }
    document.getElementById("lineage-reset")?.addEventListener("click",()=>reset());
    document.getElementById("lineage-focus-nei")?.addEventListener("click",()=>{
      activeType=null; updateLegend(); showNode("nei");
      host.scrollLeft=Math.max(0,byId.nei.cx-host.clientWidth*.7);
    });
    updateLegend();
    showNode("nei");
  };
})();
