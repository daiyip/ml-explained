"""Figure 5.1: the three generations of feed-forward layer, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/ffn_lineage.py
"""
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/05-channel-mixing/figures/ffn-lineage.svg"
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
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#ffn-a)"/>')


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


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: the classic MLP; new part = the activation ----
cx = 160
header(cx, 1, "MLP", "sigmoid, then ReLU, then GELU", "NEW: a non-saturating activation")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "one token, width d")
arrow(f"M{cx} 452 V420")
box(cx, 372, 200, "Linear up", "d to 4d")
arrow(f"M{cx} 372 V346")
out.append(f'<rect x="{cx - 100}" y="222" width="200" height="122" rx="8" class="n1"/>')
text(cx, 243, "Activation", weight=600)
sig = lambda u: 1 / (1 + math.exp(-u))
curve(cx - 80, 252, 160, 66, lambda u: sig(u * 1.6), "c0")
curve(cx - 80, 252, 160, 66, lambda u: max(0.0, u) / 3, "c1")
curve(cx - 80, 252, 160, 66, lambda u: (u * sig(1.702 * u) + 0.17) / 3.17, "c2")
text(cx - 54, 336, "sigmoid", cls="q", size=10.5)
text(cx + 6, 336, "ReLU", cls="cl1", size=10.5, weight=600)
text(cx + 58, 336, "GELU", cls="cl2", size=10.5, weight=600)
arrow(f"M{cx} 222 V190")
box(cx, 142, 200, "Linear down", "4d to d")
arrow(f"M{cx} 142 V104")
text(cx, 96, "output, width d", cls="q", size=12)
text(cx, 520, "parameters 8d², all used per token", cls="q", size=12.5)

# ---- Column 2: SwiGLU; new part = the gate ----
cx = 480
out.append("</g>")
header(cx, 2, "SwiGLU", "a gate decides what passes", "NEW: multiply by a learned gate")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "one token, width d")
lx, rx = cx - 62, cx + 62
arrow(f"M{cx} 452 V436 H{lx} V412")
arrow(f"M{cx} 436 H{rx} V412")
box(lx, 364, 112, "Linear gate", "d to 8d/3", cls="n2")
box(rx, 364, 112, "Linear up", "d to 8d/3")
arrow(f"M{lx} 364 V334")
box(lx, 286, 112, "Swish", "smooth ReLU")
arrow(f"M{lx} 286 V242 H{cx - 14}", cls="e2")
arrow(f"M{rx} 364 V242 H{cx + 14}")
op(cx, 242, "×", cls="n2")
arrow(f"M{cx} 230 V190")
box(cx, 142, 200, "Linear down", "8d/3 to d")
arrow(f"M{cx} 142 V104")
text(cx, 96, "output, width d", cls="q", size=12)
text(cx, 520, "parameters 8d², the same budget", cls="q", size=12.5)

# ---- Column 3: Mixture of Experts; new part = the router ----
cx = 800
out.append("</g>")
header(cx, 3, "Mixture of Experts", "many FFNs, each token uses k", "NEW: route each token to k of E")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "x", "one token, width d")
arrow(f"M{cx} 452 V420")
box(cx, 372, 230, "Router", "scores E experts, keeps top k", cls="n3")
xs = [cx - 87, cx - 29, cx + 29, cx + 87]
for i, ex in enumerate(xs):
    on = i in (0, 2)
    out.append(f'<path d="M{ex} 372 V322" class="{"e3" if on else "ed"}" marker-end="url(#ffn-a)"/>')
    out.append(f'<rect x="{ex - 24}" y="276" width="48" height="44" rx="8" class="{"n3" if on else "b off"}"/>')
    text(ex, 296, f"FFN{i + 1}", cls="t" if on else "q", size=12, weight=600)
    text(ex, 311, "SwiGLU", cls="q", size=9.5)
    if on:
        arrow(f"M{ex} 276 V242 H{cx + (-14 if ex < cx else 14)}", cls="e3")
op(cx, 242, "Σ", cls="n3")
arrow(f"M{cx} 230 V190")
box(cx, 142, 200, "Weighted sum", "by the router's scores")
arrow(f"M{cx} 142 V104")
text(cx, 96, "output, width d", cls="q", size=12)
text(cx, 520, "parameters E × 8d², compute k × 8d²", cls="q", size=12.5)

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
.c0,.c1,.c2{fill:none;stroke-width:2;stroke-linecap:round}
.c0{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:3 3}
.c1{stroke:var(--mlx-warn,#b5562b)} .c2{stroke:var(--mlx-accent,#2647c9)}
.cl1{fill:var(--mlx-warn,#b5562b)} .cl2{fill:var(--mlx-accent,#2647c9)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
import re
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".ffn-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="ffn-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="ffn-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
