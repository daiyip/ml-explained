// The evolution tree as an interactive timeline: one row per branch, steps placed by year,
// arrows where vision and language branches merge. Renders into #mlx-tree when present.
(function () {
  "use strict";

  // y: first year (null = before 2010), m: major step, n: one-line note.
  // A branch's `from` lists ["branchKey", stepIndex] sources that feed its first step.
  var TREE = [
    { part: "architecture", title: "Tokens and embeddings", ch: 2, ready: "02-tokens/", branches: [
      { key: "tok-lang", kind: "language", steps: [
        { t: "one-hot words", y: null, n: "Each word is its own dimension, so no two words are similar." },
        { t: "word2vec", y: 2013, m: 1, n: "Dense word vectors learned from context; similar words land close together." },
        { t: "BPE subwords", y: 2016, n: "Merge frequent character pairs into subwords, so no word is out of vocabulary." },
        { t: "byte-level BPE", y: 2019, n: "Tokenize raw bytes (GPT-2) or raw text (SentencePiece), for any language." } ] },
      { key: "tok-vis", kind: "vision", steps: [
        { t: "raw pixels into a CNN", y: 2012, n: "AlexNet reads pixels directly and lets convolutions build the features." },
        { t: "image patches (ViT)", y: 2020, m: 1, n: "Cut the image into 16x16 patches and embed each one as a token." } ] },
      { key: "tok-mm", kind: "merged", from: [["tok-lang", 3], ["tok-vis", 1]], steps: [
        { t: "multimodal tokens", y: 2022, n: "Image patches and text tokens share one sequence in one model." } ] } ] },

    { part: "architecture", title: "Position encoding", ch: 3, ready: "03-position/", branches: [
      { key: "pos-imp", kind: "implicit", steps: [
        { t: "implicit order", y: null, n: "Convolution windows and recurrence gave order for free." } ] },
      { key: "pos-exp", kind: "explicit", from: [["pos-imp", 0]], steps: [
        { t: "sinusoidal", y: 2017, n: "Fixed sine and cosine waves added to the embeddings (original Transformer)." },
        { t: "learned", y: 2018, n: "A trained vector per position (BERT, GPT)." },
        { t: "relative", y: 2018.4, n: "Bias attention by the distance between tokens, not their absolute place." },
        { t: "RoPE", y: 2021, m: 1, n: "Rotate queries and keys by position, so dot products depend only on distance." },
        { t: "ALiBi", y: 2021.5, n: "A linear distance penalty on attention scores; extrapolates to longer inputs." },
        { t: "RoPE scaling", y: 2023, n: "Stretch RoPE's frequencies to extend the context window (YaRN and others)." } ] } ] },

    { part: "architecture", title: "Token mixing", ch: 4, ready: "04-token-mixing/", branches: [
      { key: "mix-vis", kind: "vision", steps: [
        { t: "AlexNet convolution", y: 2012, m: 1, n: "A deep CNN trained on GPUs wins ImageNet by a wide margin." },
        { t: "VGG, Inception", y: 2014, n: "Deeper stacks of small filters, and multi-branch modules." } ] },
      { key: "mix-lang", kind: "language", steps: [
        { t: "RNN", y: null, n: "Read one token at a time and carry a hidden state forward." },
        { t: "LSTM seq2seq", y: 2014, m: 1, n: "An encoder LSTM reads a sentence, a decoder LSTM writes the translation." },
        { t: "Bahdanau attention", y: 2014.6, m: 1, n: "The decoder learns where to look in the source sentence at each step." } ] },
      { key: "mix-tf", kind: "merged", from: [["mix-lang", 2], ["mix-vis", 1]], steps: [
        { t: "Transformer", y: 2017, m: 1, n: "Multi-head self-attention only, no recurrence, so training runs in parallel." },
        { t: "ViT", y: 2020, n: "The same blocks applied to image patches." } ] },
      { key: "mix-cheap", kind: "efficiency", from: [["mix-tf", 0]], steps: [
        { t: "multi-query attention", y: 2019, n: "All heads share one key and value head: a much smaller KV cache." },
        { t: "sliding window", y: 2020.4, n: "Each token attends only to a local window (Longformer, later Mistral)." },
        { t: "FlashAttention", y: 2022, n: "Exact attention computed in tiles to avoid slow memory traffic." },
        { t: "GQA", y: 2023, n: "Groups of query heads share key and value heads: between MHA and MQA." },
        { t: "MLA", y: 2024, n: "Compress keys and values into a small latent vector (DeepSeek-V2)." } ] },
      { key: "mix-ssm", kind: "rival", steps: [
        { t: "S4 state spaces", y: 2021, n: "Structured state-space layers that model very long sequences." },
        { t: "Mamba", y: 2023, n: "Selective state spaces: linear-time sequence mixing that rivals attention." } ] } ] },

    { part: "architecture", title: "Channel mixing", ch: 5, ready: "05-channel-mixing/", branches: [
      { key: "ffn-act", kind: "activations", steps: [
        { t: "sigmoid, tanh", y: null, n: "Bounded activations whose gradients vanish in deep stacks." },
        { t: "ReLU", y: 2010, m: 1, n: "max(0, x): a gradient of exactly 1 for active units." },
        { t: "GELU", y: 2016, m: 1, n: "A smooth ReLU, x times the Gaussian CDF; the BERT and GPT default." },
        { t: "Swish", y: 2017, n: "x times sigmoid(x), found by automated search; almost the same as GELU." },
        { t: "SwiGLU", y: 2020, n: "A Swish-gated MLP with three matrices; standard in today's LLMs." } ] },
      { key: "ffn-moe", kind: "sparsity", steps: [
        { t: "sparse MoE", y: 2017, m: 1, n: "Many expert FFNs; a router sends each token to a few of them." },
        { t: "Switch", y: 2021, n: "Top-1 routing and a load-balancing loss make MoE simple at scale." },
        { t: "Mixtral", y: 2023, n: "8 experts, top-2 routing: an open MoE that matches much larger dense models." },
        { t: "DeepSeekMoE", y: 2024, n: "Many fine-grained experts plus always-on shared experts." } ] } ] },

    { part: "architecture", title: "Normalization", ch: 6, ready: "06-normalization/", branches: [
      { key: "norm", kind: "main", steps: [
        { t: "none", y: null, n: "Careful initialization was the only defence against drifting activations." },
        { t: "BatchNorm", y: 2015, m: 1, n: "Normalize each channel over the batch; much faster CNN training." },
        { t: "LayerNorm", y: 2016, n: "Normalize each token over its channels; works for sequences and batch size 1." },
        { t: "RMSNorm", y: 2019, n: "LayerNorm without the mean subtraction: cheaper, just as good." },
        { t: "pre-norm", y: 2020, n: "Normalize before each sub-layer instead of after; deep stacks train stably." },
        { t: "QK-norm", y: 2023, n: "Normalize queries and keys to stop attention logits from blowing up." } ] } ] },

    { part: "architecture", title: "Residual connections", ch: 7, ready: "07-residual/", branches: [
      { key: "res", kind: "main", steps: [
        { t: "highway networks", y: 2015, n: "Gated skip connections let very deep networks train." },
        { t: "ResNet", y: 2015.6, m: 1, n: "Plain identity shortcuts, x + f(x): 152 layers deep wins ImageNet." },
        { t: "pre-norm residual", y: 2019, n: "Keep the identity path clean of normalization (GPT-2 onward)." },
        { t: "residual-stream view", y: 2021, n: "Every layer reads from and writes to one shared stream." } ] } ] },

    { part: "training", title: "Objective and loss", ch: 8, ready: "08-objective/", branches: [
      { key: "loss-sup", kind: "supervised", steps: [
        { t: "softmax cross-entropy", y: 2012, n: "Predict the label of each image; AlexNet's objective." } ] },
      { key: "loss-lang", kind: "language", steps: [
        { t: "skip-gram", y: 2013, n: "Predict the words around a word (word2vec)." },
        { t: "teacher forcing", y: 2014, n: "Train a decoder on the true previous tokens (seq2seq)." },
        { t: "masked LM (BERT)", y: 2018, m: 1, n: "Hide tokens and predict them from both sides." },
        { t: "next token (GPT)", y: 2018.5, m: 1, n: "Predict the next token on raw text; the objective that scaled." } ] },
      { key: "loss-vis", kind: "vision", steps: [
        { t: "VAE", y: 2013, n: "Learn a latent space by reconstructing images through a bottleneck." },
        { t: "GAN", y: 2014, m: 1, n: "A generator learns to fool a discriminator." },
        { t: "diffusion", y: 2020, m: 1, n: "Learn to remove noise step by step; now the image-generation standard." } ] },
      { key: "loss-clip", kind: "merged", from: [["loss-lang", 3], ["loss-vis", 2]], steps: [
        { t: "contrastive (CLIP)", y: 2021, m: 1, n: "Match images with their captions; one shared image-text space." } ] } ] },

    { part: "training", title: "Optimizer", ch: 9, branches: [
      { key: "opt", kind: "main", steps: [
        { t: "SGD + momentum", y: null, n: "One learning rate for every parameter." },
        { t: "AdaGrad", y: 2011, n: "A per-parameter step size from the history of squared gradients." },
        { t: "RMSProp", y: 2012, n: "AdaGrad with a moving average, so steps do not shrink forever." },
        { t: "Adam", y: 2014, m: 1, n: "Momentum plus RMSProp scaling, with bias correction." },
        { t: "AdamW", y: 2017, n: "Weight decay applied directly, not through the gradient." },
        { t: "Lion", y: 2023, n: "A sign-based update found by program search; less memory." },
        { t: "Muon", y: 2024, n: "Orthogonalized momentum updates for matrix weights." } ] } ] },

    { part: "training", title: "Learning-rate schedule", ch: 10, branches: [
      { key: "lr", kind: "main", steps: [
        { t: "step decay", y: 2012, n: "Divide the learning rate by 10 when progress stalls." },
        { t: "warmup + cosine", y: 2017, m: 1, n: "Ramp up for stability, then decay smoothly to near zero." },
        { t: "warmup-stable-decay", y: 2024, n: "Hold the rate flat and decay only at the end; easy to extend runs." },
        { t: "schedule-free", y: 2024.5, n: "Iterate averaging replaces the schedule altogether." } ] } ] },

    { part: "training", title: "Initialization and regularization", ch: 11, branches: [
      { key: "init", kind: "main", steps: [
        { t: "Xavier init", y: 2010, n: "Scale weights so signal variance is kept across sigmoid and tanh layers." },
        { t: "dropout", y: 2012, n: "Randomly zero units during training to prevent co-adaptation." },
        { t: "He init", y: 2015, n: "Xavier corrected for ReLU's half-zero outputs." },
        { t: "muP", y: 2022, n: "Parametrize so the best hyperparameters transfer from small to large models." } ] } ] },

    { part: "beyond", title: "Scale", ch: 12, branches: [
      { key: "scale", kind: "main", steps: [
        { t: "scaling laws", y: 2020, m: 1, n: "Loss falls as a smooth power law in parameters, data and compute." },
        { t: "in-context learning", y: 2020.5, m: 1, n: "GPT-3 learns new tasks from examples in its prompt." },
        { t: "Chinchilla", y: 2022, n: "For a fixed budget, train smaller models on far more tokens." },
        { t: "emergence", y: 2022.5, n: "Some abilities seem to appear suddenly with scale; the claim is debated." } ] } ] },

    { part: "beyond", title: "Post-training", ch: 13, branches: [
      { key: "post", kind: "main", steps: [
        { t: "instruction tuning", y: 2021, n: "Fine-tune on many tasks phrased as instructions (FLAN, T0)." },
        { t: "RLHF", y: 2022, m: 1, n: "Train a reward model on human preferences, then optimize against it." },
        { t: "DPO", y: 2023, n: "Learn directly from preference pairs, without a separate reward model." },
        { t: "RL on verifiable rewards", y: 2024, m: 1, n: "Reinforce answers that pass checks, such as math and code tests." } ] } ] },

    { part: "beyond", title: "Inference and use", ch: 14, branches: [
      { key: "use", kind: "main", steps: [
        { t: "chain of thought", y: 2022, n: "Asking for step-by-step reasoning improves answers." },
        { t: "tool use, agents", y: 2023, n: "Models call search, code and other tools in a loop." },
        { t: "test-time compute", y: 2024, n: "Spend more inference compute thinking longer to answer better." } ] } ] },
  ];

  var PARTS = { architecture: "Architecture", training: "Training recipe", beyond: "Beyond the block" };
  // The tree sits on the dark bench in both themes, so its colours are fixed.
  var KIND = {
    language: "#8fa6ff", vision: "#f0b35a", merged: "#5cff8a", efficiency: "#c9aaff", rival: "#f08a5d",
    sparsity: "#c9aaff", supervised: "#c9d4e3", implicit: "#97a6b9", explicit: "#8fa6ff", activations: "#8fa6ff", main: "#c9d4e3",
  };
  var LEGEND = [["language", "language"], ["vision", "vision"], ["merged", "vision and language merge"], ["efficiency", "efficiency or sparsity"], ["main", "single lineage"]];

  var W = { left: 224, band: 64, year0: 2010, year1: 2026, perYear: 50, right: 40, axis: 34, lane: 14, char: 6.1 };

  function el(tag, attrs, parent) {
    var e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function render(root, state) {
    var stage = root.querySelector(".mlx-tree__stage");
    stage.querySelectorAll("svg").forEach(function (s) { s.remove(); });
    hideTip(root);
    var width = W.left + W.band + (W.year1 - W.year0) * W.perYear + W.right;
    var xYear = function (y) { return W.left + W.band + (y - W.year0) * W.perYear; };

    // Lay out rows: place nodes, then give each label the first free lane above or below.
    var rows = [], nodes = {}, y = W.axis + 8;
    TREE.forEach(function (lin) {
      if (state.part !== "all" && lin.part !== state.part) return;
      var group = { lin: lin, rows: [], top: y };
      lin.branches.forEach(function (br) {
        var steps = br.steps.map(function (s, i) { return { s: s, i: i }; })
          .filter(function (o) { return !state.major || o.s.m; });
        if (!steps.length) return;
        var pre = 0, lastX = -1e9, placed = [];
        steps.forEach(function (o) {
          var x = o.s.y == null ? W.left + 14 + (pre++) * 22 : xYear(o.s.y);
          x = Math.max(x, lastX + 20);
          lastX = x;
          var w = o.s.t.length * W.char + 8, lane = 0;
          for (;; lane++) {
            var clash = placed.some(function (p) { return p.lane === lane && Math.abs(p.x - x) < (p.w + w) / 2 + 4; });
            if (!clash) break;
          }
          var node = { br: br, lin: lin, s: o.s, i: o.i, x: x, lane: lane, w: w };
          placed.push(node);
        });
        var up = 1 + Math.max(0, Math.max.apply(null, placed.map(function (p) { return p.lane % 2 === 0 ? p.lane / 2 : 0; }))),
            down = Math.max(0, Math.max.apply(null, placed.map(function (p) { return p.lane % 2 ? (p.lane + 1) / 2 : 0; })));
        var cy = y + up * W.lane + 6;
        placed.forEach(function (p) { p.y = cy; nodes[br.key + ":" + p.i] = p; });
        var row = { br: br, nodes: placed, y: cy, top: y };
        y = cy + 8 + down * W.lane + 6;
        group.rows.push(row);
      });
      if (!group.rows.length) return;
      group.bottom = y;
      rows.push(group);
      y += 10;
    });
    var height = y + 6;

    var svg = el("svg", { viewBox: "0 0 " + width + " " + height, width: width, height: height, role: "img",
      "aria-label": "Timeline of how each building block of the Transformer evolved, 2010 to 2026" }, stage);
    var gGrid = el("g", {}, svg), gEdge = el("g", {}, svg), gNode = el("g", {}, svg);

    // Year axis and grid
    el("rect", { x: W.left, y: W.axis - 6, width: W.band - 8, height: height - W.axis, fill: "#ffffff", opacity: 0.03, rx: 4 }, gGrid);
    var pt = el("text", { x: W.left + 4, y: W.axis - 14, class: "mlx-tree__axis" }, gGrid);
    pt.textContent = "earlier";
    for (var yr = W.year0; yr <= W.year1; yr += 2) {
      el("line", { x1: xYear(yr), x2: xYear(yr), y1: W.axis - 6, y2: height, class: "mlx-tree__grid" }, gGrid);
      var t = el("text", { x: xYear(yr) + 3, y: W.axis - 14, class: "mlx-tree__axis" }, gGrid);
      t.textContent = yr;
    }

    var lastPart = null;
    rows.forEach(function (g) {
      if (g.lin.part !== lastPart && state.part === "all") {
        el("line", { x1: 0, x2: width, y1: g.top - 6, y2: g.top - 6, class: "mlx-tree__sep" }, gGrid);
        lastPart = g.lin.part;
      }
      var head = el("text", { x: 4, y: g.rows[0].y - 3, class: "mlx-tree__lin" }, gGrid);
      head.textContent = g.lin.title;
      var sub = el("text", { x: 4, y: g.rows[0].y + 11, class: "mlx-tree__ch" }, gGrid);
      sub.textContent = "Chapter " + g.lin.ch + (g.lin.ready ? " · ready" : "");
      g.rows.forEach(function (r, k) {
        if (g.rows.length > 1) {
          var b = el("text", { x: W.left - 8, y: r.y + 3.5, class: "mlx-tree__kind", "text-anchor": "end", fill: KIND[r.br.kind] }, gGrid);
          b.textContent = r.br.kind;
          if (k === 0) head.setAttribute("y", Math.min(r.y - 3, g.rows[0].y - 3));
        }
      });
    });

    function curve(a, b, color, cls) {
      var mx = (a.x + b.x) / 2;
      return el("path", { d: "M" + a.x + " " + a.y + " C" + mx + " " + a.y + " " + mx + " " + b.y + " " + b.x + " " + b.y,
        stroke: color, class: cls, fill: "none" }, gEdge);
    }

    var edges = [];
    rows.forEach(function (g) { g.rows.forEach(function (r) {
      var color = KIND[r.br.kind];
      for (var i = 1; i < r.nodes.length; i++) {
        var a = r.nodes[i - 1], b = r.nodes[i];
        edges.push({ a: a, b: b, e: el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: color, class: "mlx-tree__edge" }, gEdge) });
      }
      (r.br.from || []).forEach(function (f) {
        var src = nodes[f[0] + ":" + f[1]];
        if (!src) { var cands = Object.keys(nodes).filter(function (k) { return k.indexOf(f[0] + ":") === 0; }); src = nodes[cands[cands.length - 1]]; }
        if (src && r.nodes[0]) edges.push({ a: src, b: r.nodes[0], e: curve(src, r.nodes[0], KIND[src.br.kind], "mlx-tree__edge mlx-tree__edge--merge") });
      });
    }); });

    // Nodes and labels
    Object.keys(nodes).forEach(function (k) {
      var p = nodes[k], color = KIND[p.br.kind];
      var g = el("g", { class: "mlx-tree__node", tabindex: 0, role: "button",
        "aria-label": p.s.t + ", " + (p.s.y == null ? "before 2010" : Math.floor(p.s.y)) + (p.s.m ? ", major step" : "") }, gNode);
      el("circle", { cx: p.x, cy: p.y, r: 11, fill: "transparent" }, g);
      el("circle", { cx: p.x, cy: p.y, r: p.s.m ? 6 : 4, fill: p.s.m ? color : "#05080e", stroke: color, "stroke-width": p.s.m ? 0 : 1.6, class: "mlx-tree__dot" }, g);
      var up = p.lane % 2 === 0, step = Math.floor(p.lane / 2) + (up ? 0 : 0);
      var ly = up ? p.y - 9 - step * W.lane : p.y + 16 + step * W.lane;
      var lab = el("text", { x: p.x, y: ly, "text-anchor": "middle", class: "mlx-tree__label" + (p.s.m ? " mlx-tree__label--major" : "") }, g);
      lab.textContent = p.s.t;
      p.g = g;
      var show = function () { focus(root, p, edges, nodes); };
      g.addEventListener("mouseenter", show);
      g.addEventListener("focus", show);
      g.addEventListener("click", function (ev) { ev.stopPropagation(); root.dataset.pinned = k; show(); });
      g.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); root.dataset.pinned = k; show(); } });
      g.addEventListener("mouseleave", function () { if (root.dataset.pinned !== k) clear(root, edges, nodes); });
    });
    root._clear = function () { clear(root, edges, nodes); };
  }

  // Highlight a step, everything that led to it, and show its card.
  function focus(root, p, edges, nodes) {
    var on = new Set([p]), changed = true;
    while (changed) {
      changed = false;
      edges.forEach(function (ed) { if (on.has(ed.b) && !on.has(ed.a)) { on.add(ed.a); changed = true; } });
    }
    root.classList.add("is-focused");
    Object.keys(nodes).forEach(function (k) { nodes[k].g.classList.toggle("is-on", on.has(nodes[k])); });
    edges.forEach(function (ed) { ed.e.classList.toggle("is-on", on.has(ed.a) && on.has(ed.b)); });

    var tip = root.querySelector(".mlx-tree__tip"), s = p.s, lin = p.lin;
    var year = s.y == null ? "before 2010" : String(Math.floor(s.y));
    var link = lin.ready ? '<a href="' + root.dataset.base.replace(/\/?$/, "/") + lin.ready + root.dataset.ext + '">Read chapter ' + lin.ch + " &rarr;</a>"
                         : "<span>Chapter " + lin.ch + ", coming later</span>";
    tip.innerHTML = '<p class="mlx-tree__tipmeta"><span>' + year + "</span><span>" + lin.title + " &middot; " + p.br.kind + "</span></p>" +
      "<h4>" + s.t + (s.m ? ' <em>major</em>' : "") + "</h4><p>" + s.n + "</p>" + link;
    tip.hidden = false;
    var stage = root.querySelector(".mlx-tree__stage"), sw = stage.scrollWidth, tw = tip.offsetWidth;
    var left = Math.max(8, Math.min(p.x - tw / 2, sw - tw - 8));
    var below = p.y + 28, th = tip.offsetHeight, sh = stage.querySelector("svg").getBoundingClientRect().height;
    tip.style.left = left + "px";
    tip.style.top = (below + th > sh ? p.y - th - 22 : below) + "px";
  }

  function clear(root, edges, nodes) {
    root.classList.remove("is-focused");
    delete root.dataset.pinned;
    hideTip(root);
  }
  function hideTip(root) { var t = root.querySelector(".mlx-tree__tip"); if (t) t.hidden = true; }

  function init() {
    var root = document.getElementById("mlx-tree");
    if (!root) return;
    var state = { part: "all", major: false };
    var legend = root.querySelector(".mlx-tree__legend");
    LEGEND.forEach(function (l) {
      var s = document.createElement("span");
      s.innerHTML = '<i style="background:' + KIND[l[0]] + '"></i>' + l[1];
      legend.appendChild(s);
    });
    var ms = document.createElement("span");
    ms.innerHTML = '<i class="is-major"></i>major step <i class="is-minor"></i>minor step';
    legend.appendChild(ms);
    root.querySelectorAll("[data-tree-part]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.part = b.dataset.treePart;
        root.querySelectorAll("[data-tree-part]").forEach(function (c) { c.setAttribute("aria-pressed", String(c === b)); });
        render(root, state);
      });
    });
    var major = root.querySelector("[data-tree-major]");
    major.addEventListener("click", function () {
      state.major = !state.major;
      major.setAttribute("aria-pressed", String(state.major));
      render(root, state);
    });
    document.addEventListener("click", function (ev) { if (root._clear && !ev.target.closest(".mlx-tree__tip")) root._clear(); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && root._clear) root._clear(); });
    render(root, state);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
