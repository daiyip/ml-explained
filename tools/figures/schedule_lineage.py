"""Figure 10.1: the three generations of learning-rate schedule, each drawn as a curve of learning rate against step.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/schedule_lineage.py
"""
import math
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/10-lr-schedule/figures/schedule-lineage.svg"
W, H = 960, 560
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# Each column has a small chart: x = training progress 0..1, y = learning rate 0..1 (of the peak).
PX, PY, PW, PH = 0, 120, 236, 170  # chart offsets relative to column, filled in per column


def chart(cx, n):
    x0, y0 = cx - 96, PY
    out.append(f'<rect x="{cx - 130}" y="{y0 - 18}" width="260" height="{PH + 44}" rx="8" class="b"/>')
    out.append(f'<path d="M{x0} {y0} V{y0 + PH} H{x0 + 212}" class="ax" marker-end="url(#lrs-a)"/>')
    text(x0 - 4, y0 + 4, "peak", cls="q", size=9.5, anchor="end")
    text(x0 + 212, y0 + PH + 16, "step", cls="q", size=10.5, anchor="end")
    text(x0 + 2, y0 - 6, "learning rate", cls="q", size=10.5, anchor="start")

    def pts(f, lo=0.0, hi=1.0, k=120):
        p = []
        for i in range(k + 1):
            u = lo + (hi - lo) * i / k
            p.append(f"{x0 + 200 * u:.1f},{y0 + 8 + (PH - 8) * (1 - f(u)):.1f}")
        return " ".join(p)

    return pts, x0, y0


def poly(p, cls):
    out.append(f'<polyline points="{p}" class="{cls}"/>')


# ---- Column 1: constant and step decay ----
cx = 160
header(cx, 1, "Constant, then step decay", "classic SGD recipes, 2012-2016", "NEW: cut the rate at milestones")
pts, x0, y0 = chart(cx, 1)
poly(pts(lambda u: 0.62), "c0")
poly(pts(lambda u: 1.0 if u < 0.5 else 0.3 if u < 0.75 else 0.09, k=400), "c1")
text(x0 + 50, y0 + 34, "step decay ÷10", cls="cl1", size=10.5, weight=600)
text(cx, 368, "dashed: one rate for the whole run", cls="q", size=12)
text(cx, 386, "big steps to travel, small steps to settle", cls="q", size=12)
text(cx, 404, "milestones are tuned by hand", cls="q", size=12)

# ---- Column 2: warmup + cosine ----
cx = 480
header(cx, 2, "Warmup + cosine", "SGDR, Goyal et al., Transformer, 2016-17", "NEW: ramp up first, then decay smoothly")
pts, x0, y0 = chart(cx, 2)
wu = 0.08
poly(pts(lambda u: min(1.0, u / wu) if u < wu else min(1.0, math.sqrt(wu / u)), lo=0.0, hi=1.0, k=300), "c0")
poly(pts(lambda u: u / wu if u < wu else 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * (u - wu) / (1 - wu))), k=300), "c2")
out.append(f'<rect x="{x0 + 1}" y="{y0}" width="{200 * wu:.1f}" height="{PH}" class="wz"/>')
text(x0 + 24, y0 + PH - 10, "warmup", cls="cl2", size=10.5, weight=600, anchor="start")
text(x0 + 150, y0 + 72, "cosine", cls="cl2", size=10.5, weight=600)
text(cx, 368, "dashed: inverse square root (Transformer)", cls="q", size=12)
text(cx, 386, "warmup protects the first few hundred steps", cls="q", size=12)
text(cx, 404, "cosine needs the total length up front", cls="q", size=12)

# ---- Column 3: warmup-stable-decay ----
cx = 800
header(cx, 3, "Warmup-stable-decay", "MiniCPM 2024; schedule-free 2024", "NEW: hold flat, decay only at the end")
pts, x0, y0 = chart(cx, 3)
wu, d = 0.06, 0.18


def wsd(end):
    def f(u):
        if u < wu:
            return u / wu
        if u < end - d * end:
            return 1.0
        return max(0.1, 1.0 - 0.9 * (u - (end - d * end)) / (d * end))
    return f


poly(pts(wsd(0.5), lo=0.0, hi=0.5, k=200), "c3b")
poly(pts(wsd(0.75), lo=0.4, hi=0.75, k=200), "c3b")
poly(pts(wsd(1.0), k=300), "c3")
for e in (0.5, 0.75):
    out.append(f'<circle cx="{x0 + 200 * (e - d * e):.1f}" cy="{y0 + 8:.1f}" r="3.2" class="dot"/>')
text(x0 + 104, y0 + 0, "stable", cls="cl3", size=10.5, weight=600)
text(cx, 368, "dashed: decays branched off mid-run", cls="q", size=12)
text(cx, 386, "a finished model at any checkpoint", cls="q", size=12)
text(cx, 404, "schedule-free: no decay, average weights", cls="q", size=12)

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

# bottom strip: what each generation still needs to know in advance
for cx, s_ in [(160, "needs: milestones"), (480, "needs: total steps"), (800, "needs: when to stop, decided late")]:
    out.append(f'<rect x="{cx - 130}" y="430" width="260" height="34" rx="8" class="b"/>')
    text(cx, 452, s_, size=12.5, weight=600)
text(480, 510, "same peak learning rate in every column; only the shape over time changes", cls="q", size=12.5)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V490" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.ax{fill:none;stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.25}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.wz{fill:rgba(31,138,91,.10);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent)}
.dot{fill:var(--mlx-warn,#b5562b)}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.c0,.c1,.c2,.c3,.c3b{fill:none;stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}
.c0{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:4 4;stroke-width:1.8}
.c1{stroke:var(--mlx-accent,#2647c9)} .c2{stroke:var(--mlx-good,#1f8a5b)} .c3{stroke:var(--mlx-warn,#b5562b)}
.c3b{stroke:var(--mlx-warn,#b5562b);stroke-dasharray:4 4;stroke-width:1.8;opacity:.8}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".lrs-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="lrs-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="lrs-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
