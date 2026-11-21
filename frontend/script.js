/* script.js: the page. It collects the list, asks Python (Flask) to run the algorithm with fetch(),
 * plays the steps with animation.js and draws charts with charts.js.
 * The sections follow the numbers on the page: 1 list, 2 run, 3 results, 4 complexity, 5 cases, 6 compare. */
(function () {
  "use strict";

  var MAX_LIST = 1000;      // same limit as main.py
  var MAX_ANIMATED = 80;    // longer lists are calculated but not animated

  var list = [];            // the user's numbers
  var algo = "bubble";      // selected algorithm
  var info = null;          // complexity table from Python
  var lastRun = null;       // last result from Python
  var resultsShown = false;

  function $(id) { return document.getElementById(id); }
  function isSearch(name) { return info.algorithms[name].type === "search"; }
  function nameOf(name) { return info.algorithms[name].name; }
  function shortName(name) { return nameOf(name).split(" ")[0]; }
  function fmtVal(v) { return Number.isInteger(v) ? String(v) : String(Math.round(v * 100) / 100); }
  function esc(s) { return Charts.esc(s); }
  function isSorted(a) { for (var i = 0; i < a.length - 1; i++) { if (a[i] > a[i + 1]) return false; } return true; }

  function parseNum(text) {
    var t = String(text).trim();
    if (!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(t)) return null;
    var v = Number(t);
    return isFinite(v) ? (v === 0 ? 0 : v) : null;     // turns -0 into 0
  }

  function setMsg(id, text, isError) {
    $(id).textContent = text || "";
    $(id).className = "msg" + (isError ? " error" : "");
  }

  /* Talk to Python. */
  function api(url, body) {
    var options = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : undefined;
    return fetch(url, options).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) throw new Error(data.error || "Something went wrong.");
        return data;
      });
    });
  }

  /* ============================================================ 1. the list */
  function showList() {
    $("chips").innerHTML = list.length
      ? list.map(function (v, i) {
          return '<span class="chip">' + fmtVal(v) + '<button type="button" data-i="' + i + '" aria-label="Remove ' + fmtVal(v) + '">&times;</button></span>';
        }).join("")
      : '<span class="empty">No numbers yet.</span>';
    $("listCount").textContent = list.length + (list.length === 1 ? " number" : " numbers");
    Array.prototype.forEach.call(document.querySelectorAll("[data-case]"), function (b) { b.disabled = !list.length; });
  }

  function listChanged() {
    showList();
    $("sortBanner").hidden = true;
    resetResults();
    showStage();
  }

  function addNumbers(values) {
    if (list.length + values.length > MAX_LIST) {
      setMsg("listMsg", "The list can have at most " + MAX_LIST + " numbers.", true);
      return;
    }
    list = list.concat(values);
    setMsg("listMsg", "Added " + values.length + (values.length === 1 ? " number." : " numbers."));
    listChanged();
  }

  $("addBtn").onclick = function () {
    var v = parseNum($("numInput").value);
    if (v === null) { setMsg("listMsg", "Type one number, like -5, 0 or 3.5.", true); return; }
    addNumbers([v]);
    $("numInput").value = "";
    $("numInput").focus();
  };
  $("numInput").onkeydown = function (e) { if (e.key === "Enter") $("addBtn").click(); };

  $("randBtn").onclick = function () {
    var n = Math.max(1, Math.min(60, parseInt($("randCount").value, 10) || 10));
    list = [];
    for (var i = 0; i < n; i++) list.push(Math.floor(Math.random() * 100) - 20);   // -20 .. 79, repeats allowed
    setMsg("listMsg", "Made a random list of " + n + " numbers.");
    listChanged();
  };

  $("clearBtn").onclick = function () { list = []; setMsg("listMsg", ""); listChanged(); };

  $("chips").onclick = function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    list.splice(Number(b.dataset.i), 1);
    listChanged();
  };

  /* ============================================================ 2. choose and run */
  var anim = Animator.create($("stage"), { onUpdate: onAnimation });

  function makeButtons(boxId, names) {
    $(boxId).innerHTML = names.map(function (n) {
      return '<button type="button" class="algo-btn" data-algo="' + n + '" aria-pressed="false">' + esc(nameOf(n)) + "</button>";
    }).join("");
  }

  function pickAlgorithm(name) {
    algo = name;
    Array.prototype.forEach.call(document.querySelectorAll(".algo-btn"), function (b) {
      b.setAttribute("aria-pressed", b.dataset.algo === name ? "true" : "false");
    });
    $("targetRow").hidden = !isSearch(name);
    $("sortBanner").hidden = true;
    $("swapLabel").textContent = name === "insertion" ? "Shifts" : name === "merge" ? "Moves" : "Swaps";
    $("stageTitle").textContent = nameOf(name);
    showComplexity();
    resetResults();
    showStage();
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest(".algo-btn");
    if (b) pickAlgorithm(b.dataset.algo);
  });

  /* Draw the plain list (no animation yet). */
  function showStage() {
    $("stageNote").hidden = true;
    $("stageWrap").hidden = false;
    $("controls").hidden = false;
    anim.load(list, [], { algo: algo });
    $("explain").textContent = list.length ? "Pick an algorithm and press Run." : "Add some numbers, pick an algorithm and press Run.";
    $("stepText").textContent = "Step 0 / 0";
  }

  function run(force) {
    setMsg("runMsg", "");
    if (!list.length) { setMsg("runMsg", "Add at least one number first.", true); return; }
    var body = { algorithm: algo, array: list };
    if (isSearch(algo)) {
      var target = parseNum($("targetInput").value);
      if (target === null) { setMsg("runMsg", "Enter the number to find.", true); return; }
      body.target = target;
      if (algo === "binary" && !force && !isSorted(list)) { $("sortBanner").hidden = false; return; }
    }
    $("sortBanner").hidden = true;
    setMsg("runMsg", "Running...");
    api(isSearch(algo) ? "/api/search" : "/api/sort", body).then(function (data) {
      setMsg("runMsg", "");
      lastRun = data;
      resultsShown = false;
      resetResults();
      if (list.length > MAX_ANIMATED || data.truncated) {
        $("stageWrap").hidden = true;
        $("controls").hidden = true;
        $("explain").textContent = "More than " + MAX_ANIMATED + " numbers: the animation is skipped, see the results in step 3.";
        showResults();
      } else {
        $("stageWrap").hidden = false;
        $("controls").hidden = false;
        anim.load(list, data.steps, { algo: algo });
        anim.play();
      }
    }).catch(function (err) { setMsg("runMsg", err.message, true); });
  }

  $("runBtn").onclick = function () { run(false); };
  $("anywayBtn").onclick = function () { run(true); };
  $("targetInput").onkeydown = function (e) { if (e.key === "Enter") run(false); };

  $("sortFirstBtn").onclick = function () {     // sort the list with Python, then search it
    api("/api/sort", { algorithm: "merge", array: list }).then(function (data) {
      list = data.array;
      listChanged();
      setMsg("listMsg", "Your list is now sorted.");
      run(false);
    }).catch(function (err) { setMsg("runMsg", err.message, true); });
  };

  /* Best / average / worst buttons: the SAME numbers of your list in a different order. */
  Array.prototype.forEach.call(document.querySelectorAll("[data-case]"), function (b) {
    b.onclick = function () {
      api("/api/sample", { algorithm: algo, case: b.dataset.case, array: list }).then(function (data) {
        list = data.array;
        if (data.target !== null) $("targetInput").value = data.target;
        listChanged();
        setMsg("listMsg", "Your numbers are now arranged as the " + b.dataset.case + " case for " + nameOf(algo) + ". Press Run.");
      }).catch(function (err) { setMsg("runMsg", err.message, true); });
    };
  });

  /* Animation controls. */
  $("btnPlay").onclick = function () { anim.toggle(); };
  $("btnStep").onclick = function () { anim.step(); };
  $("btnBack").onclick = function () { anim.back(); };
  $("btnReset").onclick = function () { anim.reset(); };
  $("btnEnd").onclick = function () { anim.end(); };
  $("speed").oninput = function () { anim.setSpeed(Number($("speed").value)); };
  $("progress").oninput = function () { anim.goTo(Number($("progress").value)); };
  anim.setSpeed(Number($("speed").value));

  function onAnimation(s) {
    $("stepText").textContent = "Step " + s.pos + " / " + s.total;
    $("progress").max = s.total;
    $("progress").value = s.pos;
    $("btnPlay").textContent = s.playing ? "Pause" : s.finished ? "Replay" : "Play";
    if (s.msg) $("explain").textContent = s.msg;
    if (s.finished && lastRun && !resultsShown) showResults();   // show the answer only when the animation ends
  }

  /* ============================================================ 3. results */
  function resetResults() {
    ["statTime", "statCmp", "statSwap", "statResult", "statCase"].forEach(function (id) { $(id).textContent = "–"; });
    $("resultCard").hidden = true;
  }

  function showResults() {
    var r = lastRun;
    resultsShown = true;
    $("statTime").textContent = Charts.timeFormatter(r.time_ms)(r.time_ms);
    $("statCmp").textContent = r.comparisons;
    $("statSwap").textContent = isSearch(r.algorithm) ? "0" : r.swaps;
    $("statCase").textContent = r.case.label;

    var text, chips;
    if (isSearch(r.algorithm)) {
      $("statResult").textContent = r.found ? "Found at index " + r.index : "Not found";
      text = r.found
        ? fmtVal(r.target) + " found at index " + r.index + " after " + r.comparisons + " comparisons." +
          (r.indices.length > 1 ? " It appears " + r.indices.length + " times (indices " + r.indices.join(", ") + "); the search stops at the first one it meets." : "")
        : fmtVal(r.target) + " is not in the list (" + r.comparisons + " comparisons).";
      if (r.algorithm === "binary" && !r.input_sorted) text += " Your list was not sorted, so the answer may be wrong.";
      chips = list.map(function (v, i) { return '<span class="' + (r.indices.indexOf(i) !== -1 && (i === r.index || r.algorithm === "linear") ? "hit" : "") + '">' + fmtVal(v) + "</span>"; });
    } else {
      $("statResult").textContent = "Sorted";
      text = "Ordered list (sorted from smallest to largest):";
      chips = r.array.map(function (v) { return "<span>" + fmtVal(v) + "</span>"; });
    }
    $("resultText").textContent = text;
    $("resultText").hidden = !text;
    $("caseText").textContent = r.case.label + " (" + r.case.big_o + "): " + r.case.reason;
    $("resultChips").innerHTML = chips.join("");
    $("resultCard").hidden = false;
  }

  /* ============================================================ 4. complexity */
  function showComplexity() {
    var rows = info.search_order.concat(info.sort_order).map(function (n) {
      var c = info.algorithms[n];
      return '<tr class="' + (n === algo ? "picked" : "") + '"><td><b>' + esc(c.name) + "</b></td>" +
        '<td class="big-o">' + esc(c.best) + '</td><td class="big-o">' + esc(c.average) + '</td><td class="big-o">' + esc(c.worst) +
        '</td><td class="big-o">' + esc(c.space) + "</td></tr>";
    }).join("");
    $("cxTable").innerHTML = "<table><thead><tr><th>Algorithm</th><th>Best case</th><th>Average case</th><th>Worst case</th><th>Space</th></tr></thead><tbody>" + rows + "</tbody></table>";
    var c = info.algorithms[algo];
    $("cxNotes").innerHTML = "<div><b>" + esc(c.name) + ":</b> " + esc(c.summary) + "</div>" +
      "<div><b>Best</b> " + esc(c.best_note) + "</div><div><b>Average</b> " + esc(c.average_note) + "</div>" +
      "<div><b>Worst</b> " + esc(c.worst_note) + "</div><div><b>Space</b> " + esc(c.space_note) + "</div>";
  }

  /* ============================================================ 5. best / average / worst */
  function measureCases() {
    if (!list.length) { setMsg("caseMsg", "Add some numbers in step 1 first.", true); return; }
    setMsg("caseMsg", "Measuring...");
    api("/api/cases", { array: list }).then(function (data) {
      setMsg("caseMsg", "Comparisons for your " + data.n + " numbers.");
      var c = data.cases;
      var rows = info.search_order.concat(info.sort_order).map(function (name) {
        return "<tr><td><b>" + esc(nameOf(name)) + '</b></td><td class="num">' + c[name].best + '</td><td class="num">' +
          c[name].average + '</td><td class="num">' + c[name].worst + "</td></tr>";
      }).join("");
      $("casesTable").innerHTML = "<table><thead><tr><th>Algorithm</th><th class=\"num\">Best</th><th class=\"num\">Average</th><th class=\"num\">Worst</th></tr></thead><tbody>" + rows + "</tbody></table>";
    }).catch(function (err) { setMsg("caseMsg", err.message, true); });
  }
  $("caseBtn").onclick = measureCases;

  /* ============================================================ 6. compare */
  $("compareBtn").onclick = function () {
    if (!list.length) { setMsg("compareMsg", "Add some numbers in step 1 first.", true); return; }
    setMsg("compareMsg", "Comparing...");
    api("/api/compare", { array: list }).then(function (data) {
      setMsg("compareMsg", "");
      var names = info.sort_order, s = data.sorts;
      var labels = names.map(shortName);
      var maxMs = Math.max.apply(null, names.map(function (n) { return s[n].time_ms; }));
      Charts.bar($("chartTime"), { title: "Execution time", sub: "Smaller is faster", labels: labels,
        values: names.map(function (n) { return s[n].time_ms; }), format: Charts.timeFormatter(maxMs), highlightMin: true });
      Charts.bar($("chartCmp"), { title: "Comparisons", sub: "Orange = fewest", labels: labels,
        values: names.map(function (n) { return s[n].comparisons; }), highlightMin: true });
      Charts.bar($("chartSwaps"), { title: "Swaps / shifts / moves", sub: "Orange = fewest", labels: labels,
        values: names.map(function (n) { return s[n].swaps; }), highlightMin: true });
      $("compareResults").hidden = false;
      Charts.redrawAll();
    }).catch(function (err) { setMsg("compareMsg", err.message, true); });
  };

  /* ============================================================ start */
  window.addEventListener("resize", function () { Charts.redrawAll(); anim.redraw(); });

  api("/api/complexity").then(function (data) {
    info = data;
    makeButtons("searchButtons", info.search_order);
    makeButtons("sortButtons", info.sort_order);
    showList();
    pickAlgorithm("bubble");
  }).catch(function () {
    $("explain").textContent = "Cannot reach the Python server. Start it with: python main.py";
  });
})();
