/* 좌→우 계층형 DAG 렌더러. dependency depth를 가로축에 두고
   개념을 선택하면 인접한 dependency와 source coverage를 함께 보여준다. */

export function makeGraph(host, { nodes, domains, edges, onSelect }) {
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a = {}) => { const e = document.createElementNS(NS, t);
    for (const k in a) e.setAttribute(k, a[k]); return e; };

  /* ── 1. 계층 배정: 위상정렬 후 최장경로 깊이 ─────────────── */
  const id2n = new Map(nodes.map(n => [n.id, n]));
  const bad = edges.filter(e => !id2n.has(e.from) || !id2n.has(e.to));
  if (bad.length) throw new Error(`graph edge has missing endpoint: ${bad[0].from} -> ${bad[0].to}`);
  const E = edges;
  const indeg = new Map(nodes.map(n => [n.id, 0]));
  const out = new Map(nodes.map(n => [n.id, []]));
  E.forEach(e => { indeg.set(e.to, indeg.get(e.to) + 1); out.get(e.from).push(e.to); });

  const layer = new Map(nodes.map(n => [n.id, 0]));
  const q = nodes.filter(n => indeg.get(n.id) === 0).map(n => n.id);
  const deg = new Map(indeg), seen = new Set();
  while (q.length) {
    const v = q.shift(); seen.add(v);
    for (const w of out.get(v)) {
      layer.set(w, Math.max(layer.get(w), layer.get(v) + 1));
      deg.set(w, deg.get(w) - 1);
      if (deg.get(w) === 0) q.push(w);
    }
  }
  if (seen.size !== nodes.length) {
    const cyclic = nodes.filter(n => !seen.has(n.id)).map(n => n.id).join(", ");
    throw new Error(`architecture graph must be acyclic; unresolved nodes: ${cyclic}`);
  }

  const L = Math.max(...nodes.map(n => layer.get(n.id))) + 1;
  const rows = Array.from({ length: L }, () => []);
  nodes.forEach(n => rows[layer.get(n.id)].push(n.id));

  /* ── 2. 층 안 순서: barycenter 를 두 방향으로 몇 번 쓸어준다 ─ */
  const pos = new Map();
  rows.forEach(r => r.forEach((id, i) => pos.set(id, i)));
  const bary = (id, dir) => {
    const nb = dir < 0 ? E.filter(e => e.to === id).map(e => e.from)
                       : E.filter(e => e.from === id).map(e => e.to);
    if (!nb.length) return pos.get(id);
    return nb.reduce((s, v) => s + pos.get(v), 0) / nb.length;
  };
  for (let s = 0; s < 6; s++) {
    const dir = s % 2 ? 1 : -1;
    const order = dir < 0 ? [...rows.keys()] : [...rows.keys()].reverse();
    for (const li of order) {
      rows[li].sort((a, b) => bary(a, dir) - bary(b, dir));
      rows[li].forEach((id, i) => pos.set(id, i));
    }
  }

  /* ── 3. 가로 전체 보기에서도 읽히도록 label을 최대 3줄로 나눈다 ──── */
  const svg = el("svg", { xmlns: NS, class: "graphsvg" });
  host.innerHTML = ""; host.appendChild(svg);
  const visualLength = s => [...s].reduce((a, c) => a + (/[^\x00-\xff]/.test(c) ? 1.65 : 1), 0);
  const wrapLabel = label => {
    const tokens = label.replace(/([/-])/g, "$1​").split(/\s+/).filter(Boolean);
    const lines = [];
    for (const token0 of tokens) {
      const pieces = token0.split("​").filter(Boolean);
      for (const token of pieces) {
        const last = lines[lines.length - 1] || "";
        const candidate = last ? `${last} ${token}` : token;
        if (last && visualLength(candidate) > 18 && lines.length < 3) lines.push(token);
        else if (lines.length) lines[lines.length - 1] = candidate;
        else lines.push(token);
      }
    }
    if (lines.length === 3 && visualLength(lines[2]) < 5 &&
        visualLength(`${lines[1]} ${lines[2]}`) <= 21) {
      lines[1] = `${lines[1]} ${lines[2]}`; lines.pop();
    }
    return lines.slice(0, 3);
  };

  /* A connection needs its own visual room.  In particular, the old 10 px
     vertical clearance made adjacent cards read as one block and left no
     space for crossing edges. */
  const NODE_W = 150, ROW_GAP = 88, COL_GAP = 58, H = 60;
  const geo = new Map();
  const colWidths = rows.map(() => NODE_W);
  const colX = [];
  let cursorX = 0, maxH = H;
  rows.forEach((r, li) => {
    const cw = colWidths[li];
    colX[li] = cursorX + cw / 2;
    const span = Math.max((r.length - 1) * ROW_GAP, 0);
    r.forEach((id, i) => {
      geo.set(id, { x: colX[li], y: i * ROW_GAP - span / 2, w: NODE_W, h: H });
    });
    maxH = Math.max(maxH, span + H);
    cursorX += cw + COL_GAP;
  });
  const graphW = Math.max(cursorX - COL_GAP, 1);
  const bounds = { x0: -70, y0: -maxH / 2 - 82, x1: graphW + 70, y1: maxH / 2 + 82 };

  /* ── 4. 그린다 ───────────────────────────────────────────── */
  const cam = el("g", { id: "cam" });
  const gEdge = el("g", { class: "graph-edges" }), gNode = el("g");
  cam.append(gEdge, gNode); svg.appendChild(cam);

  const EC = { theorem: "#256ef4", definition: "#477a56", diagnostic: "#477a56",
               measured: "#ab5b00", open: "#6d7882",
               conjecture: "#6a2d86", caution: "#6a2d86" };
  const NC = { given: "#5b6470", theorem: "#256ef4", definition: "#207037",
    diagnostic: "#ab5b00", measured: "#ab5b00", open: "#6d7882",
    caution: "#6a2d86", conjecture: "#6a2d86", verdict: "#a8332a" };
  /* Spread incident edges over independent side ports instead of forcing all
     curves through the centre of a card.  Sorting by the opposite endpoint
     also preserves the barycentric order and avoids gratuitous crossings. */
  const ports = new Map();
  const portOffset = (i, n) => n < 2 ? 0 : (i - (n - 1) / 2) * Math.min(9, 34 / (n - 1));
  let selectedId = null, hoveredId = null;
  nodes.forEach(n => {
    const outgoing = E.map((e, i) => ({ e, i })).filter(x => x.e.from === n.id)
      .sort((u, v) => geo.get(u.e.to).y - geo.get(v.e.to).y);
    const incoming = E.map((e, i) => ({ e, i })).filter(x => x.e.to === n.id)
      .sort((u, v) => geo.get(u.e.from).y - geo.get(v.e.from).y);
    outgoing.forEach((x, i) => {
      const p = ports.get(x.i) || { sy: 0, ty: 0 };
      p.sy = portOffset(i, outgoing.length); ports.set(x.i, p);
    });
    incoming.forEach((x, i) => {
      const p = ports.get(x.i) || { sy: 0, ty: 0 };
      p.ty = portOffset(i, incoming.length); ports.set(x.i, p);
    });
  });

  E.forEach((e, ei) => {
    const a = geo.get(e.from), b = geo.get(e.to), po = ports.get(ei) || { sy: 0, ty: 0 };
    const x0 = a.x + a.w / 2, x1 = b.x - b.w / 2;
    const y0 = a.y + po.sy, y1 = b.y + po.ty;
    const bend = Math.max(30, Math.min(92, (x1 - x0) * 0.42));
    const d = `M${x0},${y0} C${x0 + bend},${y0} ${x1 - bend},${y1} ${x1},${y1}`;
    const arrow = `M${x1 - 7},${y1 - 4.5} L${x1},${y1} L${x1 - 7},${y1 + 4.5}`;
    const common = { "data-from": e.from, "data-to": e.to };

    /* The white under-stroke separates crossings without inventing an edge
       hierarchy.  Draw it immediately before its coloured line so that each
       later edge forms a small, legible bridge at a crossing. */
    gEdge.appendChild(el("path", { d, ...common, class: "ge ge-halo ge-body" }));
    const p = el("path", { d, ...common, class: "ge ge-line ge-body",
      stroke: EC[e.status] || "#6d7882",
      "stroke-dasharray": (e.status === "open" || e.status === "conjecture") ? "7 5" : "" });
    const ti = el("title"); ti.textContent = `${e.label}  (${e.status})`; p.appendChild(ti);
    gEdge.appendChild(p);
    gEdge.appendChild(el("path", { d: arrow, ...common, class: "ge ge-halo ge-arrow" }));
    gEdge.appendChild(el("path", { d: arrow, ...common, class: "ge ge-line ge-arrow",
      stroke: EC[e.status] || "#6d7882" }));
  });

  nodes.forEach(n => {
    const g0 = geo.get(n.id), c = domains[n.domain].color, sc = NC[n.status] || c;
    const g = el("g", { class: "gn", "data-id": n.id, tabindex: "0",
      role: "button", "aria-label": n.label, style: `--node-domain:${c}` });
    g.appendChild(el("rect", { x: g0.x - g0.w / 2, y: g0.y - H / 2,
      width: g0.w, height: H, rx: 10, fill: "#fff", stroke: "#b1b8be",
      "stroke-width": 1.5, class: "gn-bg" }));
    g.appendChild(el("circle", { cx: g0.x - g0.w / 2 + 15, cy: g0.y,
      r: 5, fill: c, class: "gn-dot" }));
    const lines = wrapLabel(n.label), lineH = 14.2;
    const t = el("text", { class: "gn-label", x: g0.x + 7,
      y: g0.y - (lines.length - 1) * lineH / 2 + 4,
      "text-anchor": "middle", fill: sc });
    lines.forEach((line, i) => {
      const span = el("tspan", { x: g0.x + 7, dy: i ? lineH : 0 });
      span.textContent = line; t.appendChild(span);
    });
    g.appendChild(t);
    g.onclick = () => { select(n.id); onSelect?.(n.id); };
    g.onkeydown = ev => { if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault(); g.onclick();
    }};
    g.onmouseenter = () => { hoveredId = n.id; renderEdgeFocus(); };
    g.onmouseleave = () => { if (hoveredId === n.id) hoveredId = null; renderEdgeFocus(); };
    g.onfocus = () => { hoveredId = n.id; renderEdgeFocus(); };
    g.onblur = () => { if (hoveredId === n.id) hoveredId = null; renderEdgeFocus(); };
    gNode.appendChild(g);
  });

  /* ── 5. 줌 · 팬 ─────────────────────────────────────────── */
  let k = 1, tx = 0, ty = 0;
  const apply = () => cam.setAttribute("transform", `translate(${tx},${ty}) scale(${k})`);
  function fit() {
    const r = host.getBoundingClientRect();
    const bw = bounds.x1 - bounds.x0, bh = bounds.y1 - bounds.y0;
    k = Math.min(r.width / bw, r.height / bh, 1.6);
    tx = r.width / 2 - (bounds.x0 + bw / 2) * k;
    ty = r.height / 2 - (bounds.y0 + bh / 2) * k;
    svg.setAttribute("viewBox", `0 0 ${r.width} ${r.height}`);
    svg.setAttribute("width", r.width); svg.setAttribute("height", r.height);
    apply();
  }
  function zoomAt(cx, cy, f) {
    const nk = Math.min(Math.max(k * f, 0.15), 6);
    tx = cx - (cx - tx) * (nk / k); ty = cy - (cy - ty) * (nk / k); k = nk; apply();
  }
  svg.addEventListener("wheel", ev => {
    ev.preventDefault();
    const r = svg.getBoundingClientRect();
    zoomAt(ev.clientX - r.left, ev.clientY - r.top, Math.exp(-ev.deltaY * 0.0016));
  }, { passive: false });
  let drag = null;
  svg.addEventListener("pointerdown", ev => {
    if (ev.target.closest(".gn")) return;
    drag = { x: ev.clientX - tx, y: ev.clientY - ty };
    svg.setPointerCapture(ev.pointerId); svg.style.cursor = "grabbing";
  });
  svg.addEventListener("pointermove", ev => {
    if (!drag) return; tx = ev.clientX - drag.x; ty = ev.clientY - drag.y; apply();
  });
  svg.addEventListener("pointerup", () => { drag = null; svg.style.cursor = ""; });

  function renderEdgeFocus() {
    const focusId = hoveredId || selectedId;
    gEdge.querySelectorAll(".ge").forEach(p => {
      const incident = focusId && (p.dataset.from === focusId || p.dataset.to === focusId);
      p.classList.toggle("incident", Boolean(incident));
      p.classList.toggle("subdued", Boolean(focusId && !incident));
    });
  }
  function select(id) {
    selectedId = id || null;
    gNode.querySelectorAll(".gn").forEach(g => g.classList.remove("sel", "dim"));
    if (!id) { renderEdgeFocus(); return; }
    const near = new Set([id]);
    E.forEach(e => { if (e.from === id) near.add(e.to); if (e.to === id) near.add(e.from); });
    gNode.querySelectorAll(".gn").forEach(g => {
      const i = g.dataset.id;
      g.classList.toggle("sel", i === id);
      g.classList.toggle("dim", !near.has(i));
    });
    renderEdgeFocus();
  }
  const ro = new ResizeObserver(() => fit());
  ro.observe(host);
  fit();
  return { fit, select, destroy: () => ro.disconnect(), zoomIn: () => { const r = host.getBoundingClientRect();
      zoomAt(r.width / 2, r.height / 2, 1.28); },
    zoomOut: () => { const r = host.getBoundingClientRect();
      zoomAt(r.width / 2, r.height / 2, 1 / 1.28); } };
}
