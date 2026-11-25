// animation.js: replays the steps recorded by Python (compare, swap, set, ...) on the bars.

const Animator = (function () {
  const COLOR = {
    normal: "#2A2A2A",
    cmp: "#FF5A1F",
    swap: "#FFB08F",
    sorted: "#5E8C61",
    pivot: "#8A3A12",
    zone: "#A9BFA6",
    dim: "#B9B5AD",
    ink: "#2A2A2A",
    muted: "#5A5751",
    line: "#BDB9B1",
  };
  const SPEEDS = [[900, 1], [600, 1], [420, 1], [280, 1], [180, 1], [110, 1], [60, 1], [30, 2], [16, 6], [10, 25]];

  function fmtVal(v) {
    if (Number.isInteger(v)) return String(v);
    return String(Math.round(v * 100) / 100);
  }

  function freshState() {
    return {
      hl: {}, sorted: new Set(), zone: null, range: null, pivot: null, key: null,
      found: null, notfound: false, cmps: 0, moves: 0, msg: "",
    };
  }

  function applyStep(arr, st, s) {
    st.hl = {};
    const d = s.i;
    switch (s.op) {
      case "cmp":
        st.cmps++;
        d.forEach((i) => { st.hl[i] = "cmp"; });
        break;
      case "note":
        d.forEach((i) => { st.hl[i] = "cmp"; });
        break;
      case "swap": {
        const a = d[0], b = d[1];
        const tmp = arr[a]; arr[a] = arr[b]; arr[b] = tmp;
        st.moves++;
        st.hl[a] = "swap"; st.hl[b] = "swap";
        if (st.key === a) st.key = b; else if (st.key === b) st.key = a;
        break;
      }
      case "set":
        arr[d[0]] = d[1];
        st.moves++;
        st.hl[d[0]] = "swap";
        break;
      case "mark": d.forEach((i) => st.sorted.add(i)); break;
      case "zone": st.zone = d; break;
      case "range": st.range = d; break;
      case "pivot": st.pivot = d ? d[0] : null; break;
      case "key": st.key = d ? d[0] : null; break;
      case "found": st.found = d[0]; st.hl[d[0]] = "found"; break;
      case "notfound": st.notfound = true; break;
      default: break;
    }
    if (s.msg) st.msg = s.msg;
  }

  function create(svg, hooks) {
    let initial = [], steps = [], pos = 0, arr = [], st = freshState();
    let algo = "", timer = null, speed = 4, playing = false;

    function notify() {
      if (hooks && hooks.onUpdate) {
        hooks.onUpdate({
          pos: pos, total: steps.length, cmps: st.cmps, moves: st.moves, msg: st.msg,
          playing: playing, finished: steps.length > 0 && pos >= steps.length,
          found: st.found, notfound: st.notfound,
        });
      }
    }

    function colorOf(i) {
      if (st.hl[i] === "found" || st.found === i) return { fill: COLOR.cmp, stroke: COLOR.ink };
      if (st.hl[i] === "swap") return { fill: COLOR.swap };
      if (st.hl[i] === "cmp") return { fill: COLOR.cmp };
      if (st.pivot === i || st.key === i) return { fill: COLOR.pivot };
      if (st.sorted.has(i)) return { fill: COLOR.sorted };
      if (st.zone && i >= st.zone[0] && i <= st.zone[1]) return { fill: COLOR.zone };
      if (st.range && (i < st.range[0] || i > st.range[1])) return { fill: COLOR.dim };
      return { fill: COLOR.normal };
    }

    function render() {
      const n = arr.length;
      const measured = svg.getBoundingClientRect().width;
      const W = Math.max(260, Math.round(measured) || 760);
      const H = W < 520 ? 260 : 320;
      const padX = 12, top = 28, bottom = 62;
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      if (!n) { svg.innerHTML = ""; return; }
      let yMax = Math.max(0, Math.max.apply(null, arr));
      let yMin = Math.min(0, Math.min.apply(null, arr));
      const span = yMax - yMin || 1;
      const plotH = H - top - bottom;
      const y = (v) => top + ((yMax - v) / span) * plotH;
      const y0 = y(0);
      const slot = (W - 2 * padX) / n;
      const bw = Math.min(64, slot * 0.74);
      const showVal = slot >= 20;
      const valSize = slot >= 34 ? 14 : slot >= 26 ? 12 : 10;
      const showIdx = slot >= 16;
      let out = '<line x1="' + padX + '" x2="' + (W - padX) + '" y1="' + y0 + '" y2="' + y0 + '" stroke="' + COLOR.line + '"/>';

      for (let i = 0; i < n; i++) {
        const v = arr[i];
        const cx = padX + slot * i + slot / 2;
        const x = cx - bw / 2;
        const c = colorOf(i);
        let by, bh;
        if (v >= 0) { bh = Math.max(3, y0 - y(v)); by = y0 - bh; }
        else { bh = Math.max(3, y(v) - y0); by = y0; }
        out += '<rect x="' + x + '" y="' + by + '" width="' + bw + '" height="' + bh + '" rx="2" fill="' + c.fill + '"' +
          (c.stroke ? ' stroke="' + c.stroke + '" stroke-width="3"' : "") + "/>";
        if (showVal) {
          const ty = v >= 0 ? by - 5 : by + bh + valSize + 1;
          out += '<text x="' + cx + '" y="' + ty + '" text-anchor="middle" font-size="' + valSize +
            '" font-weight="600" fill="' + (st.range && (i < st.range[0] || i > st.range[1]) ? COLOR.muted : COLOR.ink) + '">' +
            fmtVal(v) + "</text>";
        }
        if (showIdx) {
          out += '<text x="' + cx + '" y="' + (H - 28) + '" text-anchor="middle" font-size="11" fill="' + COLOR.muted + '">' + i + "</text>";
        }
      }

      if (algo === "binary" && st.range && st.range[0] <= st.range[1]) {
        const lo = st.range[0], hi = st.range[1];
        const mark = (idx, label) => '<text x="' + (padX + slot * idx + slot / 2) + '" y="' + (H - 8) +
          '" text-anchor="middle" font-size="13" font-weight="700" fill="' + COLOR.ink + '">' + label + "</text>";
        out += lo === hi ? mark(lo, "L,H") : mark(lo, "L") + mark(hi, "H");
      }
      svg.innerHTML = out;
    }

    function rebuild(target) {
      arr = initial.slice();
      st = freshState();
      for (let k = 0; k < target; k++) applyStep(arr, st, steps[k]);
      pos = target;
    }

    function stepForward() {
      if (pos >= steps.length) return false;
      applyStep(arr, st, steps[pos]);
      pos++;
      return true;
    }

    function tick() {
      const cfg = SPEEDS[speed - 1];
      for (let k = 0; k < cfg[1]; k++) {
        if (!stepForward()) break;
      }
      render();
      if (pos >= steps.length) {
        playing = false; timer = null; notify();
        return;
      }
      notify();
      timer = setTimeout(tick, cfg[0]);
    }

    const api = {
      load(values, newSteps, options) {
        api.pause();
        initial = values.slice();
        steps = newSteps || [];
        algo = (options && options.algo) || "";
        rebuild(0);
        render();
        notify();
      },
      play() {
        if (!steps.length) return;
        if (pos >= steps.length) { rebuild(0); }
        if (playing) return;
        playing = true;
        notify();
        timer = setTimeout(tick, 0);
      },
      pause() {
        if (timer) clearTimeout(timer);
        timer = null;
        if (playing) { playing = false; notify(); }
      },
      toggle() { if (playing) api.pause(); else api.play(); },
      step() { api.pause(); if (stepForward()) { render(); } notify(); },
      back() { api.pause(); if (pos > 0) { rebuild(pos - 1); render(); } notify(); },
      goTo(k) {
        api.pause();
        rebuild(Math.max(0, Math.min(steps.length, k)));
        render(); notify();
      },
      reset() { api.goTo(0); },
      end() { api.goTo(steps.length); },
      setSpeed(v) { speed = Math.max(1, Math.min(10, v)); },
      isPlaying() { return playing; },
      total() { return steps.length; },
      redraw() { render(); },
    };
    return api;
  }

  return { create, applyStep, freshState, COLOR };
})();
