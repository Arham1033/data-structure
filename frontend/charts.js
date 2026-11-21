/* charts.js: small SVG charts (bar and grouped bar). No libraries needed, so they work offline.
 * Each chart measures its container, so text keeps the same pixel size on phones and desktops. */
const Charts = (function () {
  const INK = "#2A2A2A";
  const MUTED = "#5A5751";
  const GRID = "#D6D3CD";
  const ACCENT = "#FF5A1F";
  const H = 280, T = 26, B = 44, R = 14;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function trim(x, decimals) {
    return String(Number(x.toFixed(decimals)));
  }

  function formatCount(v) {
    if (v >= 1e6) return trim(v / 1e6, 1) + "M";
    if (v >= 1000) return trim(v / 1000, v >= 10000 ? 0 : 1) + "k";
    return trim(v, 1);
  }

  function formatMs(ms) {
    if (ms < 0.01) return trim(ms * 1000, 1) + " µs";
    if (ms < 1) return trim(ms, 3) + " ms";
    return trim(ms, 2) + " ms";
  }

  /* One unit for a whole chart or table, so 12 µs and 0.021 ms never sit side by side. */
  function timeFormatter(maxMs) {
    const num = (x) => trim(x, x >= 100 ? 0 : x >= 10 ? 1 : 2);
    if (maxMs < 1) return (ms) => num(ms * 1000) + " µs";
    return (ms) => num(ms) + " ms";
  }

  /* A y axis from 0 to a round maximum, with at most 5 round tick steps. */
  function axis(v) {
    if (!(v > 0)) return { max: 1, ticks: [0, 0.25, 0.5, 0.75, 1] };
    const raw = v / 4;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw);
    const count = Math.ceil(v / step - 1e-9);
    const ticks = [];
    for (let i = 0; i <= count; i++) ticks.push(i * step);
    return { max: count * step, ticks: ticks };
  }

  function dims(el, tickLabels) {
    const cs = window.getComputedStyle(el);
    const inner = el.clientWidth - parseFloat(cs.paddingLeft || 0) - parseFloat(cs.paddingRight || 0);
    const W = Math.max(280, Math.round(inner || 600));
    const longest = Math.max.apply(null, tickLabels.map((s) => String(s).length));
    const L = Math.max(34, Math.round(14 + longest * 6.6));
    return { W: W, L: L, PW: W - L - R, PH: H - T - B };
  }

  function head(o) {
    return '<div class="chart-title">' + esc(o.title) + "</div>" +
      (o.sub ? '<div class="chart-sub">' + esc(o.sub) + "</div>" : "");
  }

  function legend(items) {
    return '<div class="chart-legend">' + items.map((it) =>
      '<span><i style="background:' + it.color + '"></i>' + esc(it.name) + "</span>").join("") + "</div>";
  }

  function open(d, title) {
    return '<svg viewBox="0 0 ' + d.W + " " + H + '" role="img" aria-label="' + esc(title) + '">';
  }

  function gridLines(d, ticks, yPos, fmt) {
    let out = "";
    ticks.forEach((v) => {
      const y = yPos(v);
      out += '<line x1="' + d.L + '" x2="' + (d.W - R) + '" y1="' + y + '" y2="' + y + '" stroke="' + GRID + '"/>';
      out += '<text x="' + (d.L - 8) + '" y="' + (y + 4) + '" text-anchor="end" font-size="12" fill="' + MUTED + '">' + esc(fmt(v)) + "</text>";
    });
    return out;
  }

  function baseline(d) {
    return '<line x1="' + d.L + '" x2="' + (d.W - R) + '" y1="' + (T + d.PH) + '" y2="' + (T + d.PH) + '" stroke="' + INK + '"/>';
  }

  function labelSize(slot) { return slot >= 64 ? 12 : slot >= 50 ? 11 : 10; }

  /* One bar per label. With highlightMin the smallest bar is orange. */
  function bar(el, o) {
    el.__redraw = function () { bar(el, o); };
    const fmt = o.format || formatCount;
    const ax = axis(Math.max.apply(null, o.values.concat([0])));
    const d = dims(el, ax.ticks.map(fmt));
    const yPos = (v) => T + d.PH - (d.PH * v) / ax.max;
    const n = o.labels.length;
    const slot = d.PW / n;
    const bw = Math.min(56, slot * 0.58);
    const minV = Math.min.apply(null, o.values);
    const distinct = o.values.some((v) => v !== o.values[0]);
    let svg = open(d, o.title) + gridLines(d, ax.ticks, yPos, fmt);
    o.values.forEach((v, i) => {
      const h = Math.max(v > 0 ? 2 : 0, (d.PH * v) / ax.max);
      const x = d.L + slot * i + (slot - bw) / 2;
      const y = T + d.PH - h;
      const hit = o.highlightMin && distinct && v === minV;
      svg += '<rect x="' + x + '" y="' + y + '" width="' + bw + '" height="' + h + '" rx="2" fill="' +
        (hit ? ACCENT : INK) + '"><title>' + esc(o.labels[i] + ": " + fmt(v)) + "</title></rect>";
      svg += '<text x="' + (x + bw / 2) + '" y="' + (y - 6) + '" text-anchor="middle" font-size="12" font-weight="600" fill="' +
        INK + '">' + esc(fmt(v)) + "</text>";
      svg += '<text x="' + (x + bw / 2) + '" y="' + (H - B + 20) + '" text-anchor="middle" font-size="' + labelSize(slot) +
        '" fill="' + INK + '">' + esc(o.labels[i]) + "</text>";
    });
    svg += baseline(d) + "</svg>";
    el.innerHTML = head(o) + svg;
  }

  /* Several bars per label (for example best / average / worst). */
  function grouped(el, o) {
    el.__redraw = function () { grouped(el, o); };
    const fmt = o.format || formatCount;
    let maxRaw = 0;
    o.series.forEach((s) => s.values.forEach((v) => { if (v > maxRaw) maxRaw = v; }));
    const ax = axis(maxRaw);
    const d = dims(el, ax.ticks.map(fmt));
    const yPos = (v) => T + d.PH - (d.PH * v) / ax.max;
    const n = o.labels.length;
    const k = o.series.length;
    const slot = d.PW / n;
    const gap = slot < 60 ? 1 : 3;
    const bw = Math.min(26, (slot * 0.82 - gap * (k - 1)) / k);
    const groupW = bw * k + gap * (k - 1);
    let svg = open(d, o.title) + gridLines(d, ax.ticks, yPos, fmt);
    o.labels.forEach((label, i) => {
      const gx = d.L + slot * i + (slot - groupW) / 2;
      o.series.forEach((s, j) => {
        const v = s.values[i];
        const h = Math.max(v > 0 ? 2 : 0, (d.PH * v) / ax.max);
        svg += '<rect x="' + (gx + j * (bw + gap)) + '" y="' + (T + d.PH - h) + '" width="' + bw + '" height="' + h +
          '" rx="2" fill="' + s.color + '"><title>' + esc(label + " (" + s.name + "): " + fmt(v)) + "</title></rect>";
      });
      svg += '<text x="' + (d.L + slot * i + slot / 2) + '" y="' + (H - B + 20) + '" text-anchor="middle" font-size="' +
        labelSize(slot) + '" fill="' + INK + '">' + esc(label) + "</text>";
    });
    svg += baseline(d) + "</svg>";
    el.innerHTML = head(o) + svg + legend(o.series.map((s) => ({ name: s.name, color: s.color })));
  }

  function redrawAll() {
    Array.prototype.forEach.call(document.querySelectorAll(".chart"), function (el) {
      if (el.__redraw && el.clientWidth > 0) el.__redraw();
    });
  }

  return { bar, grouped, formatCount, formatMs, timeFormatter, redrawAll, esc };
})();
