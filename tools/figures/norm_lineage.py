"""Figure 6.1: the three generations of normalization, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/norm_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/06-normalization/figures/norm-lineage.svg"
W, H = 960, 610
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle", extra=""):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}"{extra}>{s}</text>')


def box(cx, y, w, label, sub=None, cls="b"):
    h = 48 if sub else 34
    out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
    text(cx, y + (21 if sub else 22), label, weight=600)
    if sub:
        text(cx, y + 38, sub, cls="q", size=11.5)
    return h


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#norm-a)"/>')


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


def grid(cx, n, axis, rows_label, cols_label, caption):
    """A batch-of-vectors grid: rows are examples or tokens, columns are features.
    axis='col' highlights one feature over the batch, axis='row' one vector over its features."""
    rows, cols, s = 6, 8, 15
    x0, y0 = cx - cols * s / 2 + 8, 110
    for r in range(rows):
        for c in range(cols):
            on = (axis == "col" and c == 2) or (axis == "row" and r == 3)
            out.append(f'<rect x="{x0 + c * s}" y="{y0 + r * s}" width="{s - 2}" height="{s - 2}" rx="2" class="{f"g{n}" if on else "g0"}"/>')
    if axis == "col":
        out.append(f'<rect x="{x0 + 2 * s - 3}" y="{y0 - 3}" width="{s + 4}" height="{rows * s + 4}" rx="4" class="hl{n}"/>')
    else:
        out.append(f'<rect x="{x0 - 3}" y="{y0 + 3 * s - 3}" width="{cols * s + 4}" height="{s + 4}" rx="4" class="hl{n}"/>')
    text(x0 + cols * s / 2, y0 + rows * s + 16, cols_label, cls="q", size=10.5)
    lx, ly = x0 - 10, y0 + rows * s / 2
    text(lx, ly, rows_label, cls="q", size=10.5, extra=f' transform="rotate(-90 {lx} {ly})"')
    text(cx, y0 + rows * s + 38, caption, size=12, weight=600, cls=f"cl{n}")


# ---- Column 1: BatchNorm; new part = statistics over the batch ----
cx = 160
header(cx, 1, "BatchNorm", "2015: for convolutional nets", "NEW: normalize over the batch")
grid(cx, 1, "col", "examples", "features", "mean, variance over the batch")
box(cx, 500, 200, "x", "a batch of examples")
arrow(f"M{cx} 500 V476")
box(cx, 428, 200, "Linear", "weights W, no bias needed")
arrow(f"M{cx} 428 V404")
box(cx, 356, 200, "BatchNorm", "each feature, over the batch", cls="n1")
arrow(f"M{cx} 356 V332")
box(cx, 298, 200, "ReLU")
arrow(f"M{cx} 298 V280")
text(cx, 272, "to the next layer", cls="q", size=12)
text(cx, 586, "each output depends on the other examples", cls="q", size=12)

# ---- Column 2: LayerNorm and pre-norm; new part = per-token, inside the branch ----
cx = 480
header(cx, 2, "LayerNorm, pre-norm", "2016, then 2019-2020", "NEW: per token, inside the branch")
grid(cx, 2, "row", "tokens", "features", "mean, variance over one token")
mx, bx = cx - 62, cx + 42
box(cx, 500, 200, "x", "one token at a time")
arrow(f"M{mx} 500 V334", cls="e2")
text(mx - 8, 430, "identity path", cls="cl2", size=10.5, weight=600, anchor="end")
arrow(f"M{bx} 500 V476")
box(bx, 428, 128, "LayerNorm", "mean and variance", cls="n2")
arrow(f"M{bx} 428 V404")
box(bx, 356, 128, "Attention", "or FFN")
arrow(f"M{bx} 356 V322 H{mx + 14}")
op(mx, 322, "+")
arrow(f"M{mx} 310 V280")
text(mx, 272, "to the next block", cls="q", size=12)
text(cx, 586, "post-norm put LayerNorm after the +", cls="q", size=12)

# ---- Column 3: RMSNorm and QK-norm; new part = no mean, normalize q and k ----
cx = 800
header(cx, 3, "RMSNorm, QK-norm", "2019, then 2023", "NEW: drop the mean, normalize q, k")
grid(cx, 3, "row", "tokens", "features", "root mean square only")
qx, kx = cx - 58, cx + 58
box(cx, 500, 200, "x", "after the block's RMSNorm")
arrow(f"M{qx} 500 V476")
arrow(f"M{kx} 500 V476")
box(qx, 428, 104, "Linear q", "d to d")
box(kx, 428, 104, "Linear k", "d to d")
arrow(f"M{qx} 428 V404")
arrow(f"M{kx} 428 V404")
box(qx, 356, 104, "RMSNorm", "per head", cls="n3")
box(kx, 356, 104, "RMSNorm", "per head", cls="n3")
arrow(f"M{qx} 356 V322 H{cx - 14}", cls="e3")
arrow(f"M{kx} 356 V322 H{cx + 14}", cls="e3")
op(cx, 322, "·", cls="n3")
arrow(f"M{cx} 310 V280")
text(cx, 272, "logits q·k / √d, then softmax", cls="q", size=12)
text(cx, 586, "logits stay bounded by the learned gains", cls="q", size=12)

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

# column separators
for x in (320, 640):
    out.append(f'<path d="M{x} 20 V595" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)}
.e2{stroke:var(--mlx-good,#1f8a5b);stroke-width:2.25} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.g0{fill:var(--mlx-ink-soft,#4a5868);fill-opacity:.16}
.g1{fill:var(--mlx-accent,#2647c9);fill-opacity:.7} .g2{fill:var(--mlx-good,#1f8a5b);fill-opacity:.7} .g3{fill:var(--mlx-warn,#b5562b);fill-opacity:.7}
.hl1,.hl2,.hl3{fill:none;stroke-width:1.75}
.hl1{stroke:var(--mlx-accent,#2647c9)} .hl2{stroke:var(--mlx-good,#1f8a5b)} .hl3{stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".norm-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="norm-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="norm-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
