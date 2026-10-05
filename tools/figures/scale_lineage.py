"""Figure 12.1: three generations of thinking about scale, with each generation's new idea highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/scale_lineage.py
"""
import math
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/12-scale/figures/scale-lineage.svg"
W, H = 960, 600
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def rect(x, y, w, h, cls="b", rx=8):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')


def box(cx, y, w, label, sub=None, cls="b", h=None):
    h = h or (48 if sub else 34)
    rect(cx - w / 2, y, w, h, cls)
    text(cx, y + (21 if sub else 22), label, weight=600)
    if sub:
        text(cx, y + 38, sub, cls="q", size=12)
    return h


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#scale-a)"/>')


def poly(pts, cls):
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" class="{cls}"/>')


def axes(x0, y0, w, h, xl, yl):
    """Draw an L-shaped axis with its origin at the bottom-left (x0, y0 + h)."""
    out.append(f'<path d="M{x0} {y0} V{y0 + h} H{x0 + w}" class="ax"/>')
    text(x0 + w / 2, y0 + h + 16, xl, cls="q", size=10.5)
    out.append(f'<text x="{x0 - 8}" y="{y0 + h / 2}" class="q" font-size="12.1" text-anchor="middle" '
               f'transform="rotate(-90 {x0 - 8} {y0 + h / 2})">{yl}</text>')


def star(cx, cy, r, cls):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    out.append(f'<polygon points="{" ".join(pts)}" class="{cls}"/>')


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: scaling laws; new part = loss is a straight line on log-log axes ----
cx = 160
header(cx, 1, "Scaling laws", "Kaplan et al., 2020", "NEW: loss is a power law")
rect(cx - 130, 110, 260, 226, "n1")
text(cx, 133, "Test loss on log-log axes", weight=600)
x0, y0, pw, ph = cx - 96, 150, 210, 140
axes(x0, y0, pw, ph, "log of N, D or C", "log loss")
for (a, b, lab, cls, dy) in [(0.06, 0.52, "C", "l1", 4), (0.20, 0.68, "N", "l2", 4), (0.34, 0.84, "D", "l3", 4)]:
    pts = [(x0 + 10, y0 + ph * a), (x0 + pw - 10, y0 + ph * b)]
    poly(pts, cls)
    text(pts[1][0] + 4, pts[1][1] + dy, lab, cls=f"{cls}t", size=11, weight=700, anchor="start")
text(cx, 324, "straight lines over 7 orders of magnitude", cls="q", size=11)
arrow(f"M{cx} 336 V372")
box(cx, 374, 230, "L(N) = E + A / N<tspan baseline-shift=\"super\" font-size=\"10\">α</tspan>", "E: entropy of the text itself")
arrow(f"M{cx} 422 V452")
box(cx, 454, 230, "Forecast big runs", "from a ladder of small ones")
text(cx, 540, "the same block, just bigger", cls="q", size=12.5)

# ---- Column 2: Chinchilla; new part = grow N and D together ----
cx = 480
header(cx, 2, "Chinchilla", "Hoffmann et al., 2022", "NEW: grow N and D together")
rect(cx - 130, 110, 260, 226, "n2")
text(cx, 133, "IsoFLOP curves: fixed compute", weight=600)
x0, y0, pw, ph = cx - 96, 150, 210, 140
axes(x0, y0, pw, ph, "log model size N", "loss")
mins = []
for c0, base in [(0.28, 0.54), (0.50, 0.36), (0.72, 0.18)]:
    pts = []
    for j in range(31):
        u = j / 30
        xx = x0 + 12 + (pw - 24) * u
        loss = min(1.0, base + 0.9 * (u - c0) ** 2)  # a U with its minimum at u = c0
        yy = y0 + 8 + (ph - 16) * (1 - loss)  # high loss at the top
        pts.append((xx, yy))
    poly(pts, "u")
    k = max(range(31), key=lambda j: pts[j][1])
    mins.append(pts[k])
poly(mins, "path2")
for mx, my in mins:
    star(mx, my, 7, "st2")
text(x0 + pw - 4, y0 + ph - 4, "more compute", cls="g2", size=10.5, weight=600, anchor="end")
text(cx, 324, "each budget has a best size", cls="q", size=11)
arrow(f"M{cx} 336 V372")
box(cx, 374, 230, "N and D both grow as C<tspan baseline-shift=\"super\" font-size=\"10\">0.5</tspan>", "since C ≈ 6 N D")
arrow(f"M{cx} 422 V452")
box(cx, 454, 230, "≈ 20 tokens per parameter", "70B Chinchilla beats 280B Gopher")
text(cx, 540, "same compute, smaller model, more data", cls="q", size=12.5)

# ---- Column 3: in-context learning and emergence; new part = learning from the prompt ----
cx = 800
header(cx, 3, "In-context learning", "GPT-3, 2020; emergence, 2022-23", "NEW: learn the task from the prompt")
rect(cx - 130, 110, 260, 226, "n3")
text(cx, 133, "A prompt with examples", weight=600)
for i, (a, b) in enumerate([("x₁", "y₁"), ("x₂", "y₂"), ("x₃", "y₃")]):
    yy = 150 + i * 36
    rect(cx - 110, yy, 46, 24, "b", rx=6)
    text(cx - 87, yy + 17, a, size=12, weight=600)
    out.append(f'<path d="M{cx - 60} {yy + 12} H{cx - 40}" class="e" marker-end="url(#scale-a)"/>')
    rect(cx - 36, yy, 46, 24, "b", rx=6)
    text(cx - 13, yy + 17, b, size=12, weight=600)
yy = 150 + 3 * 36
rect(cx - 110, yy, 46, 24, "b", rx=6)
text(cx - 87, yy + 17, "x", size=12, weight=600)
out.append(f'<path d="M{cx - 60} {yy + 12} H{cx - 40}" class="e" marker-end="url(#scale-a)"/>')
rect(cx - 36, yy, 46, 24, "n3", rx=6)
text(cx - 13, yy + 17, "?", size=13, weight=700)
rect(cx + 30, 160, 84, 84, "b")
text(cx + 72, 188, "frozen", size=12, weight=600)
text(cx + 72, 204, "weights", size=12, weight=600)
text(cx + 72, 224, "no update", cls="q", size=10.5)
arrow(f"M{cx + 72} 244 V{yy + 12} H{cx + 14}", cls="e3")
text(cx, 324, "the rule is inferred in the forward pass", cls="q", size=11)
arrow(f"M{cx} 336 V368")
# smooth per-token accuracy vs sharp exact match
rect(cx - 130, 370, 260, 124, "b")
x0, y0, pw, ph = cx - 96, 384, 200, 74
axes(x0, y0, pw, ph, "log model size", "score")
p = [0.35 + 0.55 * (j / 30) for j in range(31)]
poly([(x0 + 4 + (pw - 8) * j / 30, y0 + ph - ph * p[j]) for j in range(31)], "c1")
poly([(x0 + 4 + (pw - 8) * j / 30, y0 + ph - ph * p[j] ** 12) for j in range(31)], "c3")
text(x0 + 8, y0 + 12, "per token: smooth", cls="cl1", size=10.5, weight=600, anchor="start")
text(x0 + pw, y0 + ph - 30, "exact match: jumps", cls="cl3", size=10.5, weight=600, anchor="end")
text(cx, 540, "sharp or smooth depends on the metric", cls="q", size=12.5)

for cx, s_, n in TAGS:
    tag_w = len(s_) * 6.3 + 20
    out.append(f'<rect x="{cx - tag_w / 2}" y="{86 - 13}" width="{tag_w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, 87, s_, cls=f"tagt{n}", size=10.5, weight=600)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V570" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.ax{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.25}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.l1,.l2,.l3,.u,.path2,.c1,.c3{fill:none;stroke-width:2.2;stroke-linecap:round}
.l1{stroke:var(--mlx-accent,#2647c9)} .l2{stroke:var(--mlx-accent,#2647c9);stroke-opacity:.7;stroke-dasharray:6 3}
.l3{stroke:var(--mlx-accent,#2647c9);stroke-opacity:.5;stroke-dasharray:2 3}
.l1t,.l2t,.l3t{fill:var(--mlx-accent,#2647c9)}
.u{stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.6;stroke-opacity:.7}
.path2{stroke:var(--mlx-good,#1f8a5b);stroke-dasharray:4 3}
.st2{fill:var(--mlx-good,#1f8a5b)} .g2{fill:var(--mlx-good,#1f8a5b)}
.c1{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:4 3} .c3{stroke:var(--mlx-warn,#b5562b)}
.cl1{fill:var(--mlx-ink-soft,#4a5868)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".scale-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="scale-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="scale-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
