"""Figure 8.1: the three generations of training objective, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/objective_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/08-objective/figures/objective-lineage.svg"
W, H = 960, 600
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def box(cx, y, w, label, sub=None, cls="b", h=None, size=14):
    h = h or (48 if sub else 34)
    out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
    text(cx, y + (21 if sub else 22), label, weight=600, size=size)
    if sub:
        text(cx, y + 38, sub, cls="q", size=11.5)
    return h


def cell(cx, y, s, cls="b", w=34, h=30, tcls="t"):
    out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="6" class="{cls}"/>')
    text(cx, y + 20, s, cls=tcls, size=13, weight=600)


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#obj-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: supervised cross-entropy; new part = -log p of the labelled class ----
cx = 160
header(cx, 1, "Supervised", "AlexNet, 2012: learn from labels", "NEW: −log p of the human label")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "an image")
arrow(f"M{cx} 452 V420")
box(cx, 372, 200, "Network", "pixels to K class scores")
arrow(f"M{cx} 372 V346")
out.append(f'<rect x="{cx - 110}" y="196" width="220" height="148" rx="8" class="n1"/>')
text(cx, 216, "softmax over classes", weight=600, size=13)
classes = [("cat", 0.62), ("dog", 0.22), ("car", 0.06), ("ship", 0.07), ("bird", 0.03)]
for i, (name, p) in enumerate(classes):
    bx = cx - 80 + i * 40
    bh = p * 90
    out.append(f'<rect x="{bx - 12}" y="{312 - bh}" width="24" height="{bh}" rx="2" class="{"bar1" if i == 0 else "bar0"}"/>')
    text(bx, 330, name, cls="cl1" if i == 0 else "q", size=10.5, weight=600 if i == 0 else 400)
text(cx - 80, 250, "label", cls="cl1", size=10.5, weight=600)
arrow(f"M{cx} 196 V166")
box(cx, 118, 220, "loss = −log p(cat)", "push the label's share up")
text(cx, 520, "needs a human label per example", cls="q", size=12.5)
out.append("</g>")

# ---- Column 2: self-supervised prediction; new part = the targets come from the data ----
cx = 480
header(cx, 2, "Self-supervised", "word2vec, GPT, BERT", "NEW: the text is its own label")
out.append('<g transform="translate(0,40)">')
chars = ["T", "o", "␣", "b", "e"]
xs = [cx - 96 + 48 * i for i in range(5)]
for x_, c in zip(xs, chars):
    cell(x_, 462, c)
    arrow(f"M{x_} 462 V422")
box(cx, 372, 250, "Causal Transformer", "each position sees only the past")
targets = ["o", "␣", "b", "e", ","]
for x_, c in zip(xs, targets):
    arrow(f"M{x_} 372 V332", cls="e2")
    cell(x_, 300, c, cls="n2")
text(cx, 286, "next-token targets: every position", cls="cl2", size=11, weight=600)
box(cx, 222, 250, "loss = −log p(true next token)", h=34, size=13)
# masked variant
out.append(f'<path d="M{cx - 130} 204 H{cx + 130}" class="sep"/>')
text(cx, 128, "masked variant (BERT)", cls="q", size=11.5, weight=600)
for x_, c in zip(xs, ["T", "o", "?", "b", "e"]):
    cell(x_, 140, "[M]" if c == "?" else c, cls="n2" if c == "?" else "b off", w=40 if c == "?" else 34)
text(cx, 192, "hide 15%, predict them from both sides", cls="q", size=11)
text(cx, 520, "free labels, trillions of them", cls="q", size=12.5)
out.append("</g>")

# ---- Column 3: generative and contrastive; new part = denoise, or match the pairs ----
cx = 800
header(cx, 3, "Generative, contrastive", "diffusion 2020, CLIP 2021", "NEW: denoise, or match pairs")
out.append('<g transform="translate(0,40)">')
lx, rx = cx - 75, cx + 70
text(lx, 184, "diffusion", cls="cl3", size=12, weight=700)
text(rx, 184, "CLIP", cls="cl3", size=12, weight=700)
# diffusion sub-column
box(lx, 452, 120, "x_t", "data + noise ε")
arrow(f"M{lx} 452 V420")
box(lx, 372, 120, "Denoiser", "given x_t and t", cls="n3")
arrow(f"M{lx} 372 V336", cls="e3")
box(lx, 288, 120, "predicted ε", "the noise added")
arrow(f"M{lx} 288 V252")
box(lx, 204, 120, "squared error", "predicted vs true ε", size=13)
# CLIP sub-column
gx, gy, s = rx - 46, 276, 23
for dx, lab in ((-30, "img"), (30, "text")):
    cell(rx + dx, 462, lab, w=50)
    arrow(f"M{rx + dx} 462 V430")
    cell(rx + dx, 398, "enc", w=50)
    arrow(f"M{rx + dx} 398 V{gy + 4 * s + 2}")
text(rx, gy - 10, "similarity", cls="q", size=10.5)
for i in range(4):
    for j in range(4):
        cls = "n3" if i == j else "b off"
        out.append(f'<rect x="{gx + j * s}" y="{gy + i * s}" width="{s - 3}" height="{s - 3}" rx="3" class="{cls}"/>')
text(rx, 216, "pull the diagonal", cls="q", size=11)
text(rx, 232, "up, the rest down", cls="q", size=11)
text(cx, 520, "learn a distribution, or a shared space", cls="q", size=12.5)
out.append("</g>")

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

# column separators
for x in (320, 640):
    out.append(f'<path d="M{x} 20 V570" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.off{opacity:.55}
.e,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)}
.e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.bar0{fill:var(--mlx-ink-soft,#4a5868);opacity:.45} .bar1{fill:var(--mlx-accent,#2647c9)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".obj-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="obj-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="obj-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
