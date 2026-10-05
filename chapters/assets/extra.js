// Turn "[established]" style evidence markers into badges, and box each chapter's TL;DR.
(function () {
  function enhance() {
    document.querySelectorAll(".md-typeset strong").forEach(function (el) {
      var m = el.textContent.trim().match(/^\[(established|likely|speculative)\]$/);
      if (!m) return;
      var tag = document.createElement("span");
      tag.className = "mlx-tag mlx-tag--" + m[1];
      tag.textContent = m[1];
      el.replaceWith(tag);
    });
    document.querySelectorAll(".md-typeset p > strong:only-child").forEach(function (el) {
      if (el.textContent.trim() !== "TL;DR") return;
      var p = el.parentElement, list = p.nextElementSibling;
      if (!list || list.tagName !== "UL" || p.parentElement.classList.contains("mlx-tldr")) return;
      var box = document.createElement("div");
      box.className = "mlx-tldr";
      p.before(box);
      box.append(p, list);
    });
  }
  // Landing page: filter the lineage cards by part chip and by search text.
  function finder() {
    var search = document.getElementById("mlx-search");
    if (!search) return;
    var chips = document.querySelectorAll(".mlx-finder .mlx-chip"), none = document.getElementById("mlx-none");
    var cat = "all";
    function apply() {
      var q = search.value.trim().toLowerCase(), shown = 0;
      document.querySelectorAll(".mlx-shelf").forEach(function (shelf) {
        var inShelf = 0;
        shelf.querySelectorAll(".mlx-card").forEach(function (card) {
          var ok = (cat === "all" || card.dataset.cat === cat) && card.textContent.toLowerCase().indexOf(q) !== -1;
          card.hidden = !ok;
          if (ok) inShelf++;
        });
        shelf.hidden = inShelf === 0;
        shown += inShelf;
      });
      none.hidden = shown > 0;
    }
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        cat = chip.dataset.filter;
        chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c === chip)); });
        apply();
      });
    });
    search.addEventListener("input", apply);
  }
  // Chapter pages: textbook furniture.
  function textbook() {
    var content = document.querySelector(".md-content");
    var h1 = content && content.querySelector(".md-typeset h1");
    if (!h1) return;
    // Render the key equations; MathML output needs no extra stylesheet or fonts.
    if (window.renderMathInElement) {
      renderMathInElement(content, {
        delimiters: [{ left: "$$", right: "$$", display: true }, { left: "\\(", right: "\\)", display: false }],
        output: "mathml", throwOnError: false,
      });
    }
    // Number sections and figures after the chapter number in the title ("5.2", "Figure 5.1").
    var m = h1.textContent.match(/^\s*(\d+)\./);
    if (!m) return;
    var ch = m[1], sec = 0, fig = 0;
    content.querySelectorAll(".md-typeset h2").forEach(function (h) {
      if (/^(Further reading)/.test(h.textContent.trim())) return;
      var n = document.createElement("span");
      n.className = "mlx-secnum";
      n.textContent = ch + "." + (++sec);
      h.prepend(n);
    });
    content.querySelectorAll(".md-typeset img[alt]").forEach(function (img) {
      if (!img.alt || /^No description/.test(img.alt) || img.closest("a") || img.closest("figure")) return;
      var f = document.createElement("figure"), cap = document.createElement("figcaption");
      f.className = "mlx-figure";
      cap.innerHTML = "<b>Figure " + ch + "." + (++fig) + "</b> ";
      cap.append(img.alt);
      var host = img.parentElement.tagName === "P" && img.parentElement.childNodes.length === 1 ? img.parentElement : img;
      host.replaceWith(f);
      f.append(img, cap);
    });
    chapterLayout(content);
    // Reading progress along the top edge.
    var bar = document.createElement("div");
    bar.className = "mlx-progress";
    document.body.append(bar);
    function progress() {
      var h = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, scrollY / h) : 0) + ")";
    }
    addEventListener("scroll", progress, { passive: true });
    progress();
  }
  // Heading text without the section number or the anchor-link pilcrow.
  function headingText(h) {
    var c = h.cloneNode(true);
    c.querySelectorAll(".mlx-secnum, .anchor-link, .headerlink").forEach(function (x) { x.remove(); });
    return c.textContent.trim();
  }

  // Chapter pages: themed inline figures that enlarge on click, a folded set-up section,
  // and the "Step N" sections shown as tabs.
  function chapterLayout(content) {
    content.querySelectorAll(".mlx-figure img[src$='.svg']").forEach(function (img, i) {
      var fig = img.closest(".mlx-figure");
      if (i === 0) fig.classList.add("mlx-figure--hero");
      fetch(img.src).then(function (r) { if (!r.ok) throw r; return r.text(); }).then(function (t) {
        var svg = new DOMParser().parseFromString(t, "image/svg+xml").documentElement;
        if (svg.nodeName.toLowerCase() !== "svg") return;
        svg.setAttribute("role", "img");
        svg.setAttribute("aria-label", img.alt);
        img.replaceWith(document.importNode(svg, true));
        fig.classList.add("mlx-figure--inline");
      }).catch(function () {});
      var zoom = document.createElement("button");
      zoom.className = "mlx-zoom";
      zoom.type = "button";
      zoom.setAttribute("aria-label", "Enlarge figure");
      zoom.textContent = "\u2922";
      fig.prepend(zoom);
      fig.addEventListener("click", function (ev) {
        if (ev.target.closest("a")) return;
        var art = fig.querySelector("svg, img");
        if (!art) return;
        var box = document.createElement("div");
        box.className = "mlx-lightbox";
        box.setAttribute("role", "dialog");
        box.setAttribute("aria-label", "Enlarged figure");
        box.append(art.cloneNode(true));
        var hint = document.createElement("p");
        hint.textContent = "Click anywhere or press Escape to close";
        box.append(hint);
        function close() { box.remove(); document.removeEventListener("keydown", onKey); zoom.focus(); }
        function onKey(e) { if (e.key === "Escape") close(); }
        box.addEventListener("click", close);
        document.addEventListener("keydown", onKey);
        document.body.append(box);
      });
    });

    // "What changed" cards become tabs, one per generation.
    content.querySelectorAll(".mlx-why").forEach(function (why) {
      var cards = Array.prototype.slice.call(why.querySelectorAll(":scope > .mlx-why__card"));
      if (cards.length < 2) return;
      var bar = document.createElement("div");
      bar.className = "mlx-steps__bar mlx-why__bar";
      bar.setAttribute("role", "tablist");
      bar.setAttribute("aria-label", "What changed in each generation");
      why.prepend(bar);
      why.classList.add("mlx-why--tabs");
      var tabs = cards.map(function (card, i) {
        var n = card.querySelector(".mlx-why__n"), h = card.querySelector("h3");
        var tab = document.createElement("button");
        tab.type = "button";
        tab.className = "mlx-steps__tab mlx-why__tab mlx-why__tab--" + (i + 1);
        tab.id = "mlx-why-tab-" + (i + 1);
        tab.setAttribute("role", "tab");
        tab.innerHTML = '<span class="mlx-steps__n"></span><span class="mlx-steps__title"></span>';
        tab.firstChild.textContent = n ? n.textContent : String(i + 1);
        tab.lastChild.textContent = h ? h.textContent : "";
        card.setAttribute("role", "tabpanel");
        card.setAttribute("aria-labelledby", tab.id);
        tab.addEventListener("click", function () { pick(i); });
        bar.append(tab);
        return tab;
      });
      bar.addEventListener("keydown", function (e) {
        var i = tabs.indexOf(document.activeElement);
        var j = e.key === "ArrowRight" ? (i + 1) % tabs.length : e.key === "ArrowLeft" ? (i + tabs.length - 1) % tabs.length : -1;
        if (i >= 0 && j >= 0) { e.preventDefault(); pick(j); tabs[j].focus(); }
      });
      function pick(i) {
        tabs.forEach(function (t, k) { t.setAttribute("aria-selected", String(k === i)); t.tabIndex = k === i ? 0 : -1; cards[k].hidden = k !== i; });
      }
      pick(0);
    });

    var first = content.querySelector(".jp-Cell");
    if (!first) return;
    var cells = Array.prototype.filter.call(first.parentElement.children, function (c) { return c.classList.contains("jp-Cell"); });

    // Fold the shared set-up code under "Run it yourself".
    cells.forEach(function (cell, i) {
      var h = cell.querySelector("h2");
      if (!h || !/^Run it yourself/.test(headingText(h))) return;
      var code = [];
      for (var j = i + 1; j < cells.length && !cells[j].querySelector("h2") && cells[j].classList.contains("jp-CodeCell"); j++) code.push(cells[j]);
      if (!code.length) return;
      var d = document.createElement("details");
      d.className = "mlx-setup";
      d.innerHTML = "<summary>Show the set-up code</summary>";
      code[0].before(d);
      code.forEach(function (c) { d.append(c); });
    });

    // Group each "Step N (level): title" section (h2 or h3) into a tab; any other h2 ends the group.
    var steps = [], cur = null;
    cells.forEach(function (cell) {
      var md = cell.classList.contains("jp-MarkdownCell");
      var h = md && cell.querySelector("h2, h3");
      if (h) {
        var m = headingText(h).match(/^Step (\d+)\s*\((\w+)\):\s*(.+)$/);
        if (m) { cur = { h: h, n: m[1], level: m[2], title: m[3], cells: [] }; steps.push(cur); }
        else if (h.tagName === "H2") cur = null;
      }
      if (cur) cur.cells.push(cell);
    });
    if (steps.length < 2) return;

    var wrap = document.createElement("div");
    wrap.className = "mlx-steps";
    var bar = document.createElement("div");
    bar.className = "mlx-steps__bar";
    bar.setAttribute("role", "tablist");
    bar.setAttribute("aria-label", "Steps in this lineage");
    wrap.append(bar);
    steps[0].cells[0].before(wrap);
    steps.forEach(function (st, i) {
      var tab = document.createElement("button");
      tab.type = "button";
      tab.className = "mlx-steps__tab";
      tab.id = "mlx-tab-" + st.n;
      tab.setAttribute("role", "tab");
      tab.innerHTML = '<span class="mlx-steps__n">Step ' + st.n + '</span><span class="mlx-steps__lvl mlx-steps__lvl--' + st.level + '">' + st.level + "</span>" +
        '<span class="mlx-steps__title"></span>';
      tab.querySelector(".mlx-steps__title").textContent = st.title;
      bar.append(tab);
      var panel = document.createElement("div");
      panel.className = "mlx-steps__panel";
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tab.id);
      st.cells.forEach(function (c) { panel.append(c); });
      if (steps[i + 1]) {
        var next = document.createElement("button");
        next.type = "button";
        next.className = "mlx-steps__next";
        next.innerHTML = "Next: Step " + steps[i + 1].n + " &middot; <span></span> &rarr;";
        next.querySelector("span").textContent = steps[i + 1].title;
        next.addEventListener("click", function () { show(i + 1, true); wrap.scrollIntoView({ behavior: "smooth", block: "start" }); });
        panel.append(next);
      }
      wrap.append(panel);
      st.tab = tab; st.panel = panel;
      tab.addEventListener("click", function () { show(i, true); });
    });
    bar.addEventListener("keydown", function (e) {
      var i = steps.findIndex(function (s) { return s.tab === document.activeElement; });
      if (i < 0) return;
      var j = e.key === "ArrowRight" ? (i + 1) % steps.length : e.key === "ArrowLeft" ? (i + steps.length - 1) % steps.length : -1;
      if (j >= 0) { e.preventDefault(); show(j, true); steps[j].tab.focus(); }
    });
    function show(i, record) {
      steps.forEach(function (st, k) {
        st.tab.setAttribute("aria-selected", String(k === i));
        st.tab.tabIndex = k === i ? 0 : -1;
        st.panel.hidden = k !== i;
      });
      if (record && steps[i].h.id) history.replaceState(null, "", "#" + steps[i].h.id);
    }
    // Open the tab that holds a linked heading (from the table of contents or a shared link).
    function follow() {
      var id = decodeURIComponent(location.hash.slice(1));
      var el = id && document.getElementById(id);
      var panel = el && el.closest(".mlx-steps__panel");
      if (!panel) return false;
      show(steps.findIndex(function (s) { return s.panel === panel; }), false);
      el.scrollIntoView();
      return true;
    }
    addEventListener("hashchange", follow);
    if (!follow()) show(0, false);
  }

  // "Part II · Architecture" in the chapter kicker and the side navigation links to that part on the home page.
  var PARTS = { "Anatomy": "", "Architecture": "#architecture", "Training recipe": "#training", "Beyond the block": "#beyond" };
  function partLinks() {
    var home = document.querySelector("a.md-logo");
    if (!home) return;
    function target(text) {
      var m = text.match(/^\s*(Part [IVX]+)\s*\u00b7\s*([^\u00b7]+?)\s*(\u00b7|$)/);
      return m && m[2] in PARTS ? { part: m[1] + " \u00b7 " + m[2], href: home.href.split("#")[0] + PARTS[m[2]] } : null;
    }
    document.querySelectorAll(".mlx-kicker").forEach(function (k) {
      var t = target(k.textContent);
      if (!t || k.querySelector("a")) return;
      var a = document.createElement("a");
      a.href = t.href;
      a.className = "mlx-kicker__part";
      a.textContent = t.part;
      var rest = k.textContent.replace(/^\s*Part [IVX]+\s*\u00b7\s*[^\u00b7]+?\s*(?=\u00b7|$)/, "").trim();
      k.textContent = rest ? " " + rest : "";
      k.prepend(a);
    });
    document.querySelectorAll(".md-nav--primary .md-nav__item--section > .md-nav__link").forEach(function (label) {
      var t = target(label.textContent);
      if (!t) return;
      var a = document.createElement("a");
      a.href = t.href;
      a.className = "mlx-navpart";
      a.textContent = label.textContent.trim();
      a.title = "Go to " + t.part + " on the home page";
      a.addEventListener("click", function (e) { e.stopPropagation(); });
      var host = label.querySelector(".md-ellipsis") || label;
      host.textContent = "";
      host.append(a);
    });
  }

  function init() { enhance(); finder(); textbook(); partLinks(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
