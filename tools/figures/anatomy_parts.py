"""Chapter 1 tab figures: the three parts of a modern Transformer (into vectors, one block, the two ends),
one small SVG per part, shown inside the matching "What each part does" tab.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/anatomy_parts.py
"""
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/01-anatomy/figures"
W, H = 960, 620
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def box(cx, y, w, label, sub=None, cls="b", h=None):
    h = h or (48 if sub else 34)
    out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
    text(cx, y + (21 if sub else 22), label, weight=600)
    if sub:
        text(cx, y + 38, sub, cls="q", size=12)
    return h


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#ana-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def op(cx, cy, s, cls="b"):
    out.append(f'<circle cx="{cx}" cy="{cy}" r="12" class="{cls}"/>')
    text(cx, cy + 5, s, size=15, weight=600)


def curve(x0, y0, w, h, f, cls, lo=-3, hi=3):
    pts = []
    for i in range(41):
        u = lo + (hi - lo) * i / 40
        pts.append(f"{x0 + w * i / 40:.1f},{y0 + h - h * f(u):.1f}")
    out.append(f'<polyline points="{" ".join(pts)}" class="{cls}"/>')


TAGS = []
MARKS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


MARKS.append(len(out))
# ---- Column 1: tokens become vectors that know their position ----
cx = 160
header(cx, 1, "Into vectors", "tokens, embedding, position", "NEW: ids become vectors")
out.append('<g transform="translate(0,40)">')
chars = ["T", "o", " ", "b", "e"]
for i, ch in enumerate(chars):
    x = cx - 80 + i * 40
    out.append(f'<rect x="{x - 15}" y="470" width="30" height="26" rx="6" class="b"/>')
    text(x, 488, "␣" if ch == " " else ch, size=12, weight=600)
text(cx, 516, "text, one token per character", cls="q", size=11)
arrow(f"M{cx} 470 V444")
box(cx, 396, 200, "Token ids", "(B, T) integers")
arrow(f"M{cx} 396 V366")
out.append(f'<rect x="{cx - 100}" y="252" width="200" height="112" rx="8" class="n1"/>')
text(cx, 273, "Embedding table", weight=600)
for r in range(4):
    for c in range(8):
        out.append(f'<rect x="{cx - 64 + c * 16}" y="{284 + r * 14}" width="14" height="11" rx="2" class="{"cell1" if r == 1 else "cell"}"/>')
text(cx, 352, "one row of d numbers per id", cls="q", size=10.5)
arrow(f"M{cx} 252 V226")
box(cx, 178, 200, "RoPE", "rotate q and k by position")
arrow(f"M{cx} 178 V136")
text(cx, 128, "(B, T, d) vectors", cls="q", size=12)
out.append("</g>")
text(cx, 588, "order enters only through position", cls="q", size=12.5)

MARKS.append(len(out))
# ---- Column 2: one block; attention mixes tokens, the FFN transforms each ----
cx = 480
header(cx, 2, "One block", "repeated N times", "NEW: mix across, then within")
out.append('<g transform="translate(0,40)">')
rx_ = cx - 88
bx = cx + 22
text(cx, 512, "x: the residual stream", cls="q", size=12)
out.append(f'<path d="M{rx_} 496 V318" class="e2 res"/>')
out.append(f'<path d="M{rx_} 292 V136" class="e2 res"/>')
arrow(f"M{rx_} 470 H{bx} V446")
box(bx, 410, 150, "RMSNorm")
arrow(f"M{bx} 410 V384")
box(bx, 330, 150, "Attention", "mixes across tokens", cls="n2", h=52)
arrow(f"M{bx} 330 V304 H{rx_ + 14}")
op(rx_, 304, "+", cls="n2")
arrow(f"M{rx_} 282 H{bx} V258")
box(bx, 222, 150, "RMSNorm")
arrow(f"M{bx} 222 V196")
box(bx, 142, 150, "Feed-forward", "transforms each token", cls="n2", h=52)
arrow(f"M{bx} 142 V122 H{rx_ + 14}")
op(rx_, 122, "+", cls="n2")
text(rx_, 98, "to the next block", cls="q", size=11)
text(rx_ - 2, 404, "residual", cls="cl2", size=10.5, weight=600, anchor="end")
out.append("</g>")
text(cx, 588, "norm and residual keep a deep stack trainable", cls="q", size=12.5)

MARKS.append(len(out))
# ---- Column 3: the same blocks with different ends for text and images ----
cx = 800
header(cx, 3, "Two ends", "same blocks, text or images", "NEW: swap the ends, keep the blocks")
out.append('<g transform="translate(0,40)">')
lx, rx = cx - 68, cx + 68
box(lx, 448, 124, "Characters", "token embedding")
box(rx, 448, 124, "Image patches", "4×4 pixels each")
arrow(f"M{lx} 448 V420")
arrow(f"M{rx} 448 V420")
out.append(f'<rect x="{cx - 132}" y="296" width="264" height="122" rx="8" class="n3"/>')
text(cx, 318, "The same N blocks", weight=600)
for i in range(3):
    out.append(f'<rect x="{cx - 92}" y="{330 + i * 22}" width="184" height="16" rx="4" class="b"/>')
text(lx, 410, "causal mask", cls="cl3", size=10.5, weight=600)
text(rx, 410, "no mask", cls="cl3", size=10.5, weight=600)
arrow(f"M{lx} 296 V268")
arrow(f"M{rx} 296 V268")
box(lx, 220, 124, "Next-token", "logits per position")
box(rx, 220, 124, "Class logits", "pooled patches")
arrow(f"M{lx} 220 V186")
arrow(f"M{rx} 220 V186")
text(lx, 176, "language model", cls="q", size=12)
text(rx, 176, "Vision Transformer", cls="q", size=12)
out.append("</g>")
text(cx, 588, "only the input and output change", cls="q", size=12.5)

MARKS.append(len(out))
for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

# column separators
for x in (320, 640):
    out.append(f'<path d="M{x} 20 V600" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.off{opacity:.55}
.e,.e2,.e3,.ed{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)} .ed{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:3 4;opacity:.6}
.e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.res{stroke-width:3;opacity:.8}
.cell{fill:var(--mlx-ink-soft,#4a5868);opacity:.18} .cell1{fill:var(--mlx-accent,#2647c9);opacity:.75}
.cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
import re
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".ana-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
NAMES = ["anatomy-part1-vectors.svg", "anatomy-part2-block.svg", "anatomy-part3-ends.svg"]
Y0 = [150, 124, 196]  # crop above each column's top label
for k, name in enumerate(NAMES):
    cls, mid = f"ana{k + 1}-fig", f"ana{k + 1}-a"
    style = STYLE.replace(".ana-fig ", f".{cls} ")
    body = "\n".join(out[MARKS[k]:MARKS[k + 1]]).replace("url(#ana-a)", f"url(#{mid})")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="{cls}" viewBox="{k * 320 + 6} {Y0[k]} 308 {604 - Y0[k]}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
           f"<style>{style}</style>",
           f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>', body, "</svg>"]
    (OUT / name).write_text("\n".join(svg) + "\n")
    print("wrote", OUT / name)
