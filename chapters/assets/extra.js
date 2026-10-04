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
  function init() { enhance(); finder(); textbook(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
