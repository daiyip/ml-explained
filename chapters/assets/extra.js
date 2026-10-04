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
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", enhance);
  else enhance();
})();
