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
    var chips = document.querySelectorAll(".mlx-chip"), none = document.getElementById("mlx-none");
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
  function init() { enhance(); finder(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
