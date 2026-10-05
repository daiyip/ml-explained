"""Figure 7.1: three generations of shortcut path, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/residual_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/07-residual/figures/residual-lineage.svg"
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


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#res-a)"/>')


def line(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def op(cx, cy, s, cls="b"):
    out.append(f'<circle cx="{cx}" cy="{cy}" r="12" class="{cls}"/>')
    text(cx, cy + 5, s, size=15, weight=600)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: highway network; new part = a learned gate that can carry x through ----
cx = 160
header(cx, 1, "Highway network", "2015: a gated bypass", "NEW: a learned gate carries x past the layer")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "input to the layer")
lx, gx, kx = cx - 58, cx + 30, cx + 100
arrow(f"M{cx - 20} 452 V436 H{lx} V404")
arrow(f"M{cx + 20} 452 V436 H{gx} V404")
box(lx, 356, 96, "H(x)", "the layer", h=48)
box(gx, 356, 72, "gate T", "σ(Wx+b)", cls="n1", h=48)
# carry path: x around the right edge, scaled by (1 - T)
line(f"M{cx + 60} 452 V444 H{kx} V250", cls="e1")
arrow(f"M{kx} 250 V234 H{cx + 14}", cls="e1")
text(kx - 4, 300, "carry", cls="cl1", size=11, weight=600, anchor="end")
text(kx - 4, 315, "(1−T)·x", cls="cl1", size=11, anchor="end")
arrow(f"M{lx} 356 V234 H{cx - 14}")
text(lx - 6, 300, "T·H(x)", cls="q", size=11, anchor="end")
arrow(f"M{gx} 356 V272 H{cx} V248", cls="e1")
text(gx + 6, 300, "T", cls="cl1", size=11, weight=600, anchor="start")
op(cx, 234, "+", cls="n1")
arrow(f"M{cx} 222 V190")
box(cx, 142, 200, "y = T·H(x) + (1−T)·x", None)
arrow(f"M{cx} 142 V104")
text(cx, 96, "to the next layer", cls="q", size=12)
text(cx, 524, "gate closed (T≈0): y ≈ x", cls="q", size=12.5)
text(cx, 542, "extra weights for every gate", cls="q", size=12.5)
out.append("</g>")

# ---- Column 2: ResNet; new part = the identity shortcut ----
cx = 480
header(cx, 2, "ResNet", "2015: an identity shortcut", "NEW: y = x + F(x), no gate, no weights")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "input to the block")
bx = cx - 30
arrow(f"M{bx} 452 V420")
box(bx, 384, 140, "Linear + BN")
arrow(f"M{bx} 384 V358")
box(bx, 324, 140, "ReLU")
arrow(f"M{bx} 324 V298")
box(bx, 264, 140, "Linear + BN")
arrow(f"M{bx} 264 V234 H{cx - 14}")
text(bx - 8, 252, "F(x)", cls="q", size=11, anchor="end")
sx = cx + 85
line(f"M{cx + 60} 452 V444 H{sx} V234 H{cx + 26}", cls="e2w")
arrow(f"M{cx + 28} 234 H{cx + 14}", cls="e2")
text(sx + 8, 330, "identity", cls="cl2", size=11, weight=600, anchor="start")
op(cx, 234, "+", cls="n2")
arrow(f"M{cx} 222 V190")
box(cx, 142, 200, "ReLU", "y = ReLU(x + F(x))")
arrow(f"M{cx} 142 V104")
text(cx, 96, "to the next block", cls="q", size=12)
text(cx, 524, "F only learns a correction to x", cls="q", size=12.5)
text(cx, 542, "gradient always has a path of 1", cls="q", size=12.5)
out.append("</g>")

# ---- Column 3: the residual stream; new part = norm inside the branch, blocks read and write ----
cx = 800
header(cx, 3, "Residual stream", "2019-21: pre-norm Transformer", "NEW: a clean stream that blocks read and write")
out.append('<g transform="translate(0,40)">')
sx = cx - 70
box(sx, 466, 120, "embed tokens", h=34)
line(f"M{sx} 466 V140", cls="stream")
text(sx - 16, 300, "residual stream", cls="cl3", size=11.5, weight=600, anchor="middle")
# put the label vertically along the stream
out[-1] = out[-1].replace("<text ", f'<text transform="rotate(-90 {sx - 16} 300)" ')
bxs = cx + 45
for y_block, y_op, name in ((370, 340, "Attention"), (250, 220, "FFN")):
    arrow(f"M{sx} {y_block + 44} H{bxs - 68}", cls="e")
    text(sx + 20, y_block + 39, "read", cls="q", size=10.5, anchor="start")
    box(bxs, y_block, 128, name, "on norm(x)", cls="n3")
    arrow(f"M{bxs} {y_block} V{y_op} H{sx + 14}", cls="e3")
    text(bxs - 30, y_op - 6, "write", cls="cl3", size=10.5, anchor="middle")
    op(sx, y_op, "+", cls="n3")
text(bxs, 442, "× N blocks", cls="q", size=12)
box(sx, 94, 140, "norm + head", h=34)
arrow(f"M{sx} 142 V128", cls="e3")
text(cx, 524, "x ← x + f(norm(x)); x never normalized", cls="q", size=12.5)
text(cx, 542, "every block adds to one shared vector", cls="q", size=12.5)
out.append("</g>")

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V570" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e1,.e2,.e2w,.e3,.stream{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)}
.e1{stroke:var(--mlx-accent,#2647c9)} .e2,.e2w{stroke:var(--mlx-good,#1f8a5b)} .e2w{stroke-width:3} .e3{stroke:var(--mlx-warn,#b5562b)}
.stream{stroke:var(--mlx-warn,#b5562b);stroke-width:5;stroke-opacity:.55}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".res-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="res-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="res-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
