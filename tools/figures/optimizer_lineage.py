"""Figure 9.1: the three generations of optimizer, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/optimizer_lineage.py
"""
import math
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/09-optimizer/figures/optimizer-lineage.svg"
W, H = 960, 580
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def box(cx, y, w, label, sub=None, cls="b"):
    h = 48 if sub else 34
    out.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
    text(cx, y + (21 if sub else 22), label, weight=600)
    if sub:
        text(cx, y + 38, sub, cls="q", size=11.5)
    return h


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#opt-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


def panel(cx, y, h, cls="b"):
    out.append(f'<rect x="{cx - 130}" y="{y}" width="260" height="{h}" rx="8" class="{cls}"/>')


# ---- Column 1: SGD with momentum; new part = the velocity ----
cx = 160
header(cx, 1, "SGD + momentum", "one step size for every weight", "NEW: a velocity that remembers")
panel(cx, 104, 178)
# contour ellipses of a long, narrow valley, minimum at (ox, oy)
mx, oy = cx + 16, 190
for rx, ry in [(25, 9), (50, 18), (78, 28), (104, 38)]:
    out.append(f'<ellipse cx="{mx}" cy="{oy}" rx="{rx}" ry="{ry}" class="ct"/>')
# plain gradient descent: zig-zags across the valley
x0, y0 = cx - 92, oy - 30
pts = []
for i in range(11):
    u = i / 10
    x = x0 + (mx - x0) * (1 - (1 - u) ** 1.6)
    y = oy + (y0 - oy) * (1 - u) * (1 if i % 2 == 0 else -1)
    pts.append(f"{x:.1f},{y:.1f}")
out.append(f'<polyline points="{" ".join(pts)}" class="p0"/>')
# momentum: a smooth path down the valley floor
out.append(f'<path d="M{x0} {y0} C{x0 + 40} {oy + 26}, {x0 + 80} {oy + 6}, {mx} {oy}" class="p1"/>')
out.append(f'<circle cx="{mx}" cy="{oy}" r="3.5" class="dot"/>')
text(cx - 76, 128, "SGD: zig-zags", cls="q", size=11, anchor="start")
text(cx - 76, 272, "momentum: follows the valley", cls="cl1", size=11, weight=600, anchor="start")

box(cx, 302, 220, "gradient g", "of the loss, one number per weight")
arrow(f"M{cx} 350 V374")
box(cx, 376, 220, "v ← μ v + g", "a running sum of past gradients", cls="n1")
arrow(f"M{cx} 424 V448")
box(cx, 450, 220, "w ← w − η v", "the same η for every weight")
text(cx, 530, "state: 1 number per weight", cls="q", size=12.5)
text(cx, 550, "fast along the valley, if η is tuned", cls="q", size=12.5)

# ---- Column 2: Adam and AdamW; new part = the per-weight scale ----
cx = 480
header(cx, 2, "Adam, AdamW", "a step size for each weight", "NEW: divide by a running RMS")
panel(cx, 104, 178)
raw = [0.95, 0.12, 0.55, 0.05, 0.75, 0.25, 0.4, 0.08]
base = 196
bx0 = cx - 104
for i, r in enumerate(raw):
    x = bx0 + i * 27
    out.append(f'<rect x="{x}" y="{base - 62 * r:.1f}" width="9" height="{62 * r:.1f}" class="bar0"/>')
    s = 0.62 + 0.08 * math.sin(i * 1.7)
    out.append(f'<rect x="{x + 10}" y="{base - 62 * s:.1f}" width="9" height="{62 * s:.1f}" class="bar2"/>')
out.append(f'<path d="M{cx - 112} {base} H{cx + 112}" class="axis"/>')
text(cx, 216, "eight weights", cls="q", size=11)
out.append(f'<rect x="{cx - 104}" y="234" width="10" height="10" class="bar0"/>')
text(cx - 88, 243, "raw gradient", cls="q", size=11, anchor="start")
out.append(f'<rect x="{cx + 6}" y="234" width="10" height="10" class="bar2"/>')
text(cx + 22, 243, "Adam step", cls="cl2", size=11, weight=600, anchor="start")
text(cx, 270, "small gradients get bigger steps", cls="q", size=11)

box(cx, 302, 220, "gradient g", "of the loss, one number per weight")
arrow(f"M{cx - 56} 350 V374")
arrow(f"M{cx + 56} 350 V374")
box(cx - 56, 376, 108, "m ← avg g", "direction")
box(cx + 56, 376, 108, "s ← avg g²", "scale", cls="n2")
arrow(f"M{cx - 56} 424 V448")
arrow(f"M{cx + 56} 424 V448", cls="e2")
box(cx, 450, 220, "w ← w − η m / √s", "AdamW: also w ← w − ηλw", cls="n2")
text(cx, 530, "state: 2 numbers per weight", cls="q", size=12.5)
text(cx, 550, "decay kept outside the scaling", cls="q", size=12.5)

# ---- Column 3: Muon; new part = orthogonalized matrix update ----
cx = 800
header(cx, 3, "Muon", "treat each weight matrix as a whole", "NEW: orthogonalize the update")
panel(cx, 104, 178)
sv_raw = [1.0, 0.55, 0.3, 0.17, 0.1, 0.06, 0.04, 0.03]
sv_new = [0.86, 0.95, 1.0, 1.04, 0.97, 0.9, 0.84, 0.8]
for j, (vals, cls, lab, x_start) in enumerate([(sv_raw, "bar0", "before", cx - 116), (sv_new, "bar3", "after", cx + 8)]):
    for i, s in enumerate(vals):
        x = x_start + i * 13.5
        out.append(f'<rect x="{x:.1f}" y="{base - 62 * s:.1f}" width="9" height="{62 * s:.1f}" class="{cls}"/>')
    out.append(f'<path d="M{x_start - 2} {base} H{x_start + 108}" class="axis"/>')
text(cx - 62, 216, "momentum M", cls="q", size=11)
text(cx + 62, 216, "update O", cls="cl3", size=11, weight=600)
text(cx, 243, "singular values of the matrix", cls="q", size=11)
text(cx, 270, "every direction moves equally", cls="q", size=11)

box(cx, 302, 220, "gradient matrix G", "for each 2-D weight W")
arrow(f"M{cx} 350 V374")
box(cx, 376, 220, "Newton-Schulz on M", "U Σ Vᵀ becomes U Vᵀ", cls="n3")
arrow(f"M{cx} 424 V448", cls="e3")
box(cx, 450, 220, "W ← W − η O", "same rotation, flat spectrum")
text(cx, 530, "state: 1 number per weight", cls="q", size=12.5)
text(cx, 550, "AdamW still handles vectors", cls="q", size=12.5)

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V560" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)} .e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.axis{stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.6;stroke-width:1}
.ct{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.35;stroke-width:1}
.p0{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.5;stroke-dasharray:3 3}
.p1{fill:none;stroke:var(--mlx-accent,#2647c9);stroke-width:2.5;stroke-linecap:round}
.dot{fill:var(--mlx-ink,#131c27)}
.bar0{fill:var(--mlx-ink-soft,#4a5868);opacity:.45}
.bar2{fill:var(--mlx-good,#1f8a5b)} .bar3{fill:var(--mlx-warn,#b5562b)}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".opt-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="opt-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="opt-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
