"""Figure 3.1: three generations of position encoding, with each generation's new part highlighted.

Column 1 adds a position vector to each token embedding (sinusoidal or learned).
Column 2 leaves the vectors alone and adds a distance-dependent bias to the attention scores
(Shaw et al.; ALiBi). Column 3 rotates the query and key by an angle proportional to position (RoPE).

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/position_lineage.py
"""
import math
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/03-position/figures/position-lineage.svg"
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
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#pos-a)"/>')


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


# ---- Column 1: absolute positions added to the embedding ----
cx = 160
header(cx, 1, "Absolute", "sinusoidal 2017, learned 2018", "NEW: add a vector for position i")
out.append('<g transform="translate(0,40)">')
lx, rx = cx - 58, cx + 58
box(lx, 452, 104, "token", "embedding")
box(rx, 452, 104, "position i", "sin/cos or table", cls="n1")
# a small sinusoid strip inside the position box is implied; draw waves above the box instead
arrow(f"M{lx} 452 V420 H{cx - 14}")
arrow(f"M{rx} 452 V420 H{cx + 14}", cls="e1")
op(cx, 420, "+", cls="n1")
arrow(f"M{cx} 408 V372")
box(cx, 324, 200, "q, k carry position", "mixed into the content")
arrow(f"M{cx} 324 V292")
box(cx, 244, 200, "score q·k", "content and position tangled")
arrow(f"M{cx} 244 V212")
box(cx, 164, 200, "softmax, weight v", None)
arrow(f"M{cx} 164 V132")
text(cx, 120, "position seen only through q, k", cls="q", size=12)
text(cx, 520, "learned table stops at the trained length", cls="q", size=12.5)

# ---- Column 2: relative bias on the scores ----
cx = 480
out.append("</g>")
header(cx, 2, "Relative bias", "Shaw 2018, T5 2019, ALiBi 2021", "NEW: score bias by distance i−j")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "token", "embedding only")
arrow(f"M{cx} 452 V420")
box(cx, 372, 200, "q, k", "no position inside")
arrow(f"M{cx} 372 V352")
op(cx, 340, "+", cls="n2")
box(cx + 74, 316, 84, "−m·(i−j)", "bias", cls="n2", h=48)
arrow(f"M{cx + 32} 340 H{cx + 14}", cls="e2")
# a tiny bias matrix illustration: darker = more penalty
gx, gy, s = cx - 92, 288, 9
for i in range(6):
    for j in range(6):
        if j > i:
            continue
        a = 0.85 - 0.14 * (i - j)
        out.append(f'<rect x="{gx + j * s}" y="{gy + i * s}" width="{s - 1}" height="{s - 1}" class="cell" fill-opacity="{a:.2f}"/>')
text(gx + 27, gy + 68, "near = small penalty", cls="q", size=10)
arrow(f"M{cx} 328 V272")
box(cx, 224, 200, "score q·k + bias", "position only in the bias")
arrow(f"M{cx} 224 V192")
box(cx, 144, 200, "softmax, weight v", None)
arrow(f"M{cx} 144 V112")
text(cx, 104, "values v carry no position", cls="q", size=12)
text(cx, 520, "depends on i−j, so any length works", cls="q", size=12.5)

# ---- Column 3: RoPE rotation ----
cx = 800
out.append("</g>")
header(cx, 3, "RoPE", "Su et al. 2021, scaled 2023", "NEW: rotate q, k by angle iθ")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "token", "embedding only")
arrow(f"M{cx} 452 V420")
box(cx, 372, 200, "q, k", "pairs of channels")
arrow(f"M{cx} 372 V340")
# rotation dial
out.append(f'<rect x="{cx - 100}" y="214" width="200" height="124" rx="8" class="n3"/>')
text(cx, 234, "Rotate by position", weight=600)
ox, oy, r = cx - 52, 292, 38
out.append(f'<circle cx="{ox}" cy="{oy}" r="{r}" class="dial"/>')
for ang, cls, lab in ((20, "vk", "k at j"), (75, "vq", "q at i")):
    ex = ox + r * math.cos(math.radians(ang))
    ey = oy - r * math.sin(math.radians(ang))
    out.append(f'<path d="M{ox} {oy} L{ex:.1f} {ey:.1f}" class="{cls}" marker-end="url(#pos-a3)"/>')
out.append(f'<path d="M{ox + 20 * math.cos(math.radians(20)):.1f} {oy - 20 * math.sin(math.radians(20)):.1f} A20 20 0 0 0 {ox + 20 * math.cos(math.radians(75)):.1f} {oy - 20 * math.sin(math.radians(75)):.1f}" class="arc"/>')
text(cx + 42, 280, "angle between", cls="q", size=11)
text(cx + 42, 297, "= (i−j)θ", cls="t", size=12, weight=600)
text(cx + 42, 320, "length unchanged", cls="q", size=10)
arrow(f"M{cx} 214 V192")
box(cx, 144, 200, "score q·k", "depends on content and i−j")
arrow(f"M{cx} 144 V112")
text(cx, 104, "then softmax, weight v", cls="q", size=12)
text(cx, 520, "no parameters; scale θ for longer text", cls="q", size=12.5)

out.append("</g>")
for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V570" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e1,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)} .e1{stroke:var(--mlx-accent,#2647c9)}
.e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)} .ah3{fill:var(--mlx-warn,#b5562b)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.cell{fill:var(--mlx-good,#1f8a5b)}
.dial{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.5;stroke-dasharray:3 3}
.vq,.vk{fill:none;stroke-width:2.2;stroke-linecap:round}
.vq{stroke:var(--mlx-warn,#b5562b)} .vk{stroke:var(--mlx-ink,#131c27)}
.arc{fill:none;stroke:var(--mlx-warn,#b5562b);stroke-width:1.5}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".pos-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="pos-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="pos-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker>'
       '<marker id="pos-a3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah3"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
