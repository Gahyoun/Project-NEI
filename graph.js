/* 계층형 DAG 렌더러 — 줌·팬 되는 캔버스, 초록 점선 hyperedge 지원.
   mermaid 를 쓰지 않는다. 배치를 직접 잡아야 hyperedge 를 정확히 두를 수 있고,
   박스 대신 밑줄로 마디를 그려 계층이 드러나게 한다. */

export function makeGraph(host, { nodes, domains, edges, hyper, onSelect }) {
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a = {}) => { const e = document.createElementNS(NS, t);
    for (const k in a) e.setAttribute(k, a[k]); return e; };

  /* ── 1. 계층 배정: 위상정렬 후 최장경로 깊이 ─────────────── */
  const id2n = new Map(nodes.map(n => [n.id, n]));
  const E = edges.filter(e => id2n.has(e.from) && id2n.has(e.to));
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
  // 순환에 걸린 마디는 선행자 최대깊이+1 로 밀어 넣는다
  nodes.filter(n => !seen.has(n.id)).forEach(n => {
    const pre = E.filter(e => e.to === n.id).map(e => layer.get(e.from));
    layer.set(n.id, pre.length ? Math.max(...pre) + 1 : 0);
  });

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

  /* ── 2b. hyperedge 원소를 층마다 왼쪽으로 모은다 ─────────
     원소가 층마다 흩어져 있으면 어떤 껍질을 씌워도 비원소를 삼킨다.
     층 안에서 원소를 앞으로 안정 분할하면 원소 영역이 층마다 하나의 구간이 되고,
     그 구간들을 세로로 이어 붙인 계단형 폴리곤이 정확히 원소만 감싼다. */
  const MEM = new Set(hyper ? hyper.members : []);
  if (MEM.size) {
    rows.forEach(r => {
      const a = r.filter(id => MEM.has(id)), b = r.filter(id => !MEM.has(id));
      r.length = 0; r.push(...a, ...b);
      r.forEach((id, i) => pos.set(id, i));
    });
  }

  /* ── 3. 글자 크기를 재고 좌표를 잡는다 ───────────────────── */
  const svg = el("svg", { xmlns: NS, class: "graphsvg" });
  const probe = el("g", { opacity: "0" });
  svg.appendChild(probe); host.innerHTML = ""; host.appendChild(svg);
  const W = new Map();
  nodes.forEach(n => {
    const t = el("text", { class: "gn-label" }); t.textContent = n.label;
    probe.appendChild(t); W.set(n.id, t.getBBox().width);
  });
  probe.remove();

  const PADX = 30, ROWH = 108, H = 26;
  const geo = new Map();
  let maxW = 0;
  rows.forEach((r, li) => {
    const tot = r.reduce((s, id) => s + W.get(id) + PADX, 0);
    let x = -tot / 2;
    r.forEach(id => {
      const w = W.get(id) + PADX;
      geo.set(id, { x: x + w / 2, y: li * ROWH, w: W.get(id), h: H });
      x += w;
    });
    maxW = Math.max(maxW, tot);
  });
  const bounds = { x0: -maxW / 2 - 60, y0: -70, x1: maxW / 2 + 60, y1: (L - 1) * ROWH + 70 };

  /* ── 4. 그린다 ───────────────────────────────────────────── */
  const cam = el("g", { id: "cam" });
  const gHyper = el("g"), gEdge = el("g"), gNode = el("g");
  cam.append(gHyper, gEdge, gNode); svg.appendChild(cam);

  const EC = { theorem: "#256ef4", measured: "#ab5b00", open: "#6d7882",
               conjecture: "#6a2d86", caution: "#6a2d86" };
  E.forEach(e => {
    const a = geo.get(e.from), b = geo.get(e.to);
    const y0 = a.y + H / 2, y1 = b.y - H / 2, my = (y0 + y1) / 2;
    const d = `M${a.x},${y0} C${a.x},${my} ${b.x},${my} ${b.x},${y1}`;
    const p = el("path", { d, fill: "none", stroke: EC[e.status] || "#6d7882",
      "stroke-width": 1.3, opacity: 0.75,
      "stroke-dasharray": (e.status === "open" || e.status === "conjecture") ? "5 4" : "" });
    const ti = el("title"); ti.textContent = `${e.label}  (${e.status})`; p.appendChild(ti);
    gEdge.appendChild(p);
    const hd = el("path", { d: `M${b.x - 3.6},${y1 - 5.4} L${b.x},${y1} L${b.x + 3.6},${y1 - 5.4}`,
      fill: "none", stroke: EC[e.status] || "#6d7882", "stroke-width": 1.3, opacity: 0.85 });
    gEdge.appendChild(hd);
  });

  nodes.forEach(n => {
    const g0 = geo.get(n.id), c = domains[n.domain].color;
    const g = el("g", { class: "gn", "data-id": n.id, tabindex: "0" });
    g.appendChild(el("rect", { x: g0.x - g0.w / 2 - 9, y: g0.y - H / 2 - 4,
      width: g0.w + 18, height: H + 8, rx: 4, fill: "#fff", class: "gn-bg" }));
    const t = el("text", { class: "gn-label", x: g0.x, y: g0.y + 5,
      "text-anchor": "middle", fill: "#1e2124" });
    t.textContent = n.label; g.appendChild(t);
    g.appendChild(el("line", { x1: g0.x - g0.w / 2, y1: g0.y + 13,
      x2: g0.x + g0.w / 2, y2: g0.y + 13, stroke: c, "stroke-width": 2.4 }));
    g.onclick = () => { select(n.id); onSelect?.(n.id); };
    g.onkeydown = ev => { if (ev.key === "Enter") g.onclick(); };
    gNode.appendChild(g);
  });

  /* hyperedge: 층마다 원소 구간을 잡아 계단형 폴리곤으로 닫는다.
     볼록껍질과 달리 비원소를 구성상 포함하지 않는다. */
  if (hyper && MEM.size) {
    const PADX2 = 20, half = ROWH / 2 - 6;
    const band = [];
    rows.forEach((r, li) => {
      const ms = r.filter(id => MEM.has(id) && geo.has(id));
      if (!ms.length) return;
      const xs = ms.map(id => geo.get(id));
      band.push({
        y: li * ROWH,
        l: Math.min(...xs.map(g => g.x - g.w / 2)) - PADX2,
        r: Math.max(...xs.map(g => g.x + g.w / 2)) + PADX2
      });
    });
    if (band.length) {
      const pts = [];
      band.forEach((b0, i) => {                       // 왼쪽을 따라 내려간다
        pts.push([b0.l, b0.y - half], [b0.l, b0.y + half]);
        if (i < band.length - 1) pts.push([band[i + 1].l, b0.y + half]);
      });
      for (let i = band.length - 1; i >= 0; i--) {     // 오른쪽을 따라 올라온다
        const b0 = band[i];
        pts.push([b0.r, b0.y + half], [b0.r, b0.y - half]);
        if (i > 0) pts.push([band[i - 1].r, b0.y - half]);
      }
      gHyper.appendChild(el("path", { d: smoothClosed(dedupe(pts), 14),
        fill: hyper.color, "fill-opacity": 0.05, stroke: hyper.color,
        "stroke-width": 2, "stroke-dasharray": "9 6", "stroke-linejoin": "round" }));
      const lab = el("text", { x: (band[0].l + band[0].r) / 2,
        y: band[0].y - half - 12, "text-anchor": "middle",
        fill: hyper.color, class: "gn-hyper" });
      lab.textContent = hyper.label; gHyper.appendChild(lab);
    }
  }

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

  function select(id) {
    gNode.querySelectorAll(".gn").forEach(g => g.classList.remove("sel", "dim"));
    gEdge.querySelectorAll("path").forEach(p => p.style.opacity = "");
    if (!id) return;
    const near = new Set([id]);
    E.forEach(e => { if (e.from === id) near.add(e.to); if (e.to === id) near.add(e.from); });
    gNode.querySelectorAll(".gn").forEach(g => {
      const i = g.dataset.id;
      g.classList.toggle("sel", i === id);
      g.classList.toggle("dim", !near.has(i));
    });
  }
  new ResizeObserver(() => fit()).observe(host);
  fit();
  return { fit, select, zoomIn: () => { const r = host.getBoundingClientRect();
      zoomAt(r.width / 2, r.height / 2, 1.28); },
    zoomOut: () => { const r = host.getBoundingClientRect();
      zoomAt(r.width / 2, r.height / 2, 1 / 1.28); } };
}

/* 이웃한 같은 점을 지운다. 계단이 평평한 곳에서 꼭짓점이 겹치면 모서리 둥글리기가 깨진다 */
function dedupe(p) {
  const o = [];
  for (const q of p) {
    const l = o[o.length - 1];
    if (!l || Math.abs(l[0] - q[0]) > 0.5 || Math.abs(l[1] - q[1]) > 0.5) o.push(q);
  }
  if (o.length > 1) {
    const f = o[0], l = o[o.length - 1];
    if (Math.abs(f[0] - l[0]) < 0.5 && Math.abs(f[1] - l[1]) < 0.5) o.pop();
  }
  return o;
}

/* ── 볼록껍질 (Andrew monotone chain) ─────────────────────── */
function convexHull(p) {
  const s = [...p].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of s) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of s.reverse()) { while (up.length > 1 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  lo.pop(); up.pop();
  return lo.concat(up);
}
/* 껍질 꼭짓점을 모서리에서 잘라 둥글게 닫는다 */
function smoothClosed(h, r = 26) {
  if (h.length < 3) return "";
  const n = h.length, seg = [];
  const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  for (let i = 0; i < n; i++) {
    const p = h[i], a = h[(i - 1 + n) % n], b = h[(i + 1) % n];
    const da = Math.hypot(p[0] - a[0], p[1] - a[1]), db = Math.hypot(b[0] - p[0], b[1] - p[1]);
    const s = lerp(p, a, Math.min(r / (da || 1), 0.5)), e = lerp(p, b, Math.min(r / (db || 1), 0.5));
    seg.push({ s, p, e });
  }
  let d = `M${seg[0].s[0].toFixed(1)},${seg[0].s[1].toFixed(1)}`;
  for (let i = 0; i < n; i++) {
    const c = seg[i], nx = seg[(i + 1) % n];
    d += ` Q${c.p[0].toFixed(1)},${c.p[1].toFixed(1)} ${c.e[0].toFixed(1)},${c.e[1].toFixed(1)}`;
    d += ` L${nx.s[0].toFixed(1)},${nx.s[1].toFixed(1)}`;
  }
  return d + " Z";
}
