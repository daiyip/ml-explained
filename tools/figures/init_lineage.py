"""Figure 11.1: three generations of keeping a network trainable: variance-preserving init,
dropout and weight decay, and muP, with each generation's new idea highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/init_lineage.py
"""
import math
import pathlib
import random
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/11-initialization/figures/init-lineage.svg"
W, H = 960, 600
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


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def polyline(pts, cls):
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" class="{cls}"/>')


def axes(x0, y0, w, h, xlabel, ylabel):
    out.append(f'<path d="M{x0} {y0} V{y0 + h} H{x0 + w}" class="ax"/>')
    text(x0 + w / 2, y0 + h + 16, xlabel, cls="q", size=10.5)
    out.append(f'<text x="{x0 - 8}" y="{y0 + h / 2}" class="q" font-size="12.1" text-anchor="middle" '
               f'transform="rotate(-90 {x0 - 8} {y0 + h / 2})">{ylabel}</text>')


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: Xavier and He; new part = init scaled by fan-in ----
cx = 160
header(cx, 1, "Xavier and He init", "2010 and 2015", "NEW: scale weights by 1/fan-in")
out.append('<g transform="translate(0,40)">')
box(cx, 64, 236, "W ~ N(0, 2 / fan-in)", "He; Xavier uses 2 / (fan-in + fan-out)", cls="n1", h=50)
# signal std across depth, log scale: three regimes
x0, y0, w, h = cx - 98, 150, 200, 190
axes(x0, y0, w, h, "layer 1 to 30", "signal std (log)")
mid = y0 + h / 2
polyline([(x0 + w * i / 29, mid - min(h / 2 - 4, i * 3.6)) for i in range(30)], "c3")
polyline([(x0 + w * i / 29, mid + min(h / 2 - 4, i * 3.6)) for i in range(30)], "c0")
polyline([(x0 + w * i / 29, mid + 2 * math.sin(i / 3)) for i in range(30)], "c1")
text(x0 + 8, y0 + 14, "too large: explodes", cls="cl3", size=10.5, weight=600, anchor="start")
text(x0 + w - 2, mid - 8, "fan-in scaled: flat", cls="cl1", size=10.5, weight=600, anchor="end")
text(x0 + 8, y0 + h - 8, "too small: vanishes", cls="q", size=10.5, anchor="start")
text(cx, 392, "forward signal and backward", cls="q", size=12.5)
text(cx, 410, "gradient both keep their scale", cls="q", size=12.5)
box(cx, 436, 236, "ReLU zeroes half the units", "so He doubles Xavier's variance", h=50)
out.append("</g>")

# ---- Column 2: dropout and weight decay; new part = noise during training ----
cx = 480
header(cx, 2, "Dropout, weight decay", "2012, and much older", "NEW: noise and shrinkage in training")
out.append('<g transform="translate(0,40)">')
rnd = random.Random(3)
layers_x = [cx - 90, cx - 30, cx + 30, cx + 90]
ys = [100 + 42 * i for i in range(6)]
dropped = {(1, 1), (1, 4), (2, 0), (2, 3), (2, 5)}
for li in range(3):
    for i, ya in enumerate(ys):
        for j, yb in enumerate(ys):
            off = (li, i) in dropped or (li + 1, j) in dropped
            if off:
                continue
            out.append(f'<path d="M{layers_x[li]} {ya} L{layers_x[li + 1]} {yb}" class="ln"/>')
for li, lx in enumerate(layers_x):
    for i, yy in enumerate(ys):
        if (li, i) in dropped:
            out.append(f'<circle cx="{lx}" cy="{yy}" r="10" class="b off"/>')
            out.append(f'<path d="M{lx - 6} {yy - 6} L{lx + 6} {yy + 6} M{lx + 6} {yy - 6} L{lx - 6} {yy + 6}" class="x2"/>')
        else:
            out.append(f'<circle cx="{lx}" cy="{yy}" r="10" class="{"n2" if 0 < li < 3 else "b"}"/>')
text(cx, 352, "each step drops a random half", cls="q", size=12.5)
text(cx, 370, "of the hidden units (p = 0.5)", cls="q", size=12.5)
box(cx, 392, 236, "Weight decay", "w ← w − η λ w at every step", h=50)
box(cx, 452, 236, "Both shrink the train/val gap", "the model can't memorize cheaply", h=50)
out.append("</g>")

# ---- Column 3: muP; new part = init and learning rate scaled with width ----
cx = 800
header(cx, 3, "muP", "2022", "NEW: scale init and LR with width")
out.append('<g transform="translate(0,40)">')
box(cx, 64, 236, "hidden LR ∝ 1 / width", "readout starts at zero", cls="n3", h=50)


def bowl(x0, y0, w, h, centre, depth, cls):
    pts = []
    for i in range(41):
        u = i / 40
        pts.append((x0 + w * u, y0 + h * (0.55 + depth) - h * 2.4 * (u - centre) ** 2))
    polyline([(x, max(y, y0 + 4)) for x, y in pts], cls)


for k, (label, shifts) in enumerate([("standard", [0.62, 0.48, 0.34]), ("muP", [0.48, 0.48, 0.48])]):
    x0, y0, w, h = cx - 95, 146 + 132 * k, 196, 88
    axes(x0, y0, w, h, "log learning rate", "loss")
    for j, c in enumerate(shifts):
        bowl(x0, y0, w, h, c, 0.15 * j, f"w{j}")
        bx = x0 + w * c
        out.append(f'<circle cx="{bx:.1f}" cy="{y0 + h * (0.55 + 0.15 * j):.1f}" r="3.2" class="d{j}"/>')
    text(x0 + 4, y0 - 6, label, cls="t", size=11.5, weight=600, anchor="start")
text(cx - 60, 412, "width 64", cls="cw0", size=10.5, weight=600)
text(cx, 412, "256", cls="cw1", size=10.5, weight=600)
text(cx + 50, 412, "1024", cls="cw2", size=10.5, weight=600)
box(cx, 436, 236, "Tune on a small model", "and reuse its LR on a big one", h=50)
out.append("</g>")

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V570" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.off{opacity:.55}
.ax{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.2}
.ln{stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.28;stroke-width:1}
.x2{stroke:var(--mlx-good,#1f8a5b);stroke-width:2;stroke-linecap:round}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.c0,.c1,.c3,.w0,.w1,.w2{fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.c0{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:3 3}
.c1{stroke:var(--mlx-accent,#2647c9);stroke-width:2.6} .c3{stroke:var(--mlx-warn,#b5562b)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl3{fill:var(--mlx-warn,#b5562b)}
.w0{stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.55} .w1{stroke:var(--mlx-warn,#b5562b);stroke-opacity:.6} .w2{stroke:var(--mlx-warn,#b5562b)}
.d0{fill:var(--mlx-ink-soft,#4a5868)} .d1,.d2{fill:var(--mlx-warn,#b5562b)}
.cw0{fill:var(--mlx-ink-soft,#4a5868)} .cw1{fill:var(--mlx-warn,#b5562b);fill-opacity:.7} .cw2{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".init-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="init-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>"] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
