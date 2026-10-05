"""Figure 4.1: the three generations of token mixing, with each generation's new part highlighted.

Every column shows the same six-token sentence and asks how the representation of the last token,
"are", gets information from "keys", four tokens earlier. The SVG has a transparent background and
takes its colours from the site's CSS variables when it is inlined into the page (falling back to
the light palette when opened on its own).
Run: python tools/figures/mixing_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/04-token-mixing/figures/mixing-lineage.svg"
W, H = 1020, 600
COL = 340
WORDS = ["The", "keys", "to", "the", "cabinet", "are"]
out = []


def text(x, y, s, cls="t", size=14, weight=400, anchor="middle"):
    out.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{round(size * 1.15, 1)}" font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


def rect(cx, cy, w, h, cls="b", rx=7):
    out.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')


def arrow(d, cls="e", marker="mix-a"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#{marker})"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    tag(cx, 86, new, n)


def token_xs(x0):
    step = 52
    first = x0 + COL / 2 - step * 2.5
    return [first + i * step for i in range(6)]


TOK_Y = 470  # centre of the input token row
OUT_Y = 140  # centre of the output token


def inputs(xs, faded=()):
    for i, (x, w) in enumerate(zip(xs, WORDS)):
        cls = "b off" if i in faded else "b"
        rect(x, TOK_Y, 48, 28, cls=cls)
        text(x, TOK_Y + 4.5, w, cls="q" if i in faded else "t", size=10.5, weight=600 if i == 1 else 400)


def output(x, cls):
    rect(x, OUT_Y, 64, 34, cls=cls)
    text(x, OUT_Y - 1, "are", size=12, weight=700)
    text(x, OUT_Y + 12, "new vector", cls="q", size=8.5)


# ---- Column 1: convolution; new part = a fixed local window with shared weights ----
x0 = 0
cx = x0 + COL / 2
header(cx, 1, "Convolution", "AlexNet, VGG, WaveNet", "NEW: a fixed window, shared weights")
xs = token_xs(x0)
inputs(xs, faded=(0, 1, 2))
# the window over the last three tokens
out.append(f'<rect x="{xs[3] - 30}" y="{TOK_Y - 22}" width="{xs[5] - xs[3] + 60}" height="44" rx="10" class="win1"/>')
text((xs[3] + xs[5]) / 2, TOK_Y + 38, "window of k = 3 tokens", cls="cl1", size=11, weight=600)
ox = xs[5]
for i, w in zip((3, 4, 5), ("w₁", "w₂", "w₃")):
    arrow(f"M{xs[i]} {TOK_Y - 16} L{ox - (5 - i) * 9} {OUT_Y + 20}", cls="e1")
    mx, my = (xs[i] * 0.55 + (ox - (5 - i) * 9) * 0.45), (TOK_Y - 16) * 0.55 + (OUT_Y + 20) * 0.45
    text(mx - 13, my, w, cls="cl1", size=11, weight=600)
output(ox, "n1")
text(xs[1], 300, "out of reach", cls="q", size=11)
text(xs[1], 316, "for one layer", cls="q", size=11)
text(cx, 548, "same weights at every position", cls="q", size=12.5)
text(cx, 568, "reach grows only with depth: L(k−1)+1", cls="q", size=12.5)

# ---- Column 2: recurrence; new part = a running state carried from token to token ----
x0 = COL
cx = x0 + COL / 2
header(cx, 2, "Recurrence", "LSTM, seq2seq", "NEW: a running state, one step at a time")
xs = token_xs(x0)
inputs(xs)
HY = 330
for i, x in enumerate(xs):
    arrow(f"M{x} {TOK_Y - 15} V{HY + 17}")
    cls = "n2" if i >= 1 else "b"
    rect(x, HY, 40, 30, cls=cls)
    text(x, HY + 5, f"h{i + 1}", size=12, weight=600)
    if i:
        arrow(f"M{xs[i - 1] + 20} {HY} H{x - 21}", cls="e2")
text((xs[1] + xs[4]) / 2, HY - 30, "&quot;keys&quot; must survive 4 updates", cls="cl2", size=11, weight=600)
arrow(f"M{xs[5]} {HY - 15} V{OUT_Y + 19}")
output(xs[5], "n2")
text(xs[2], 220, "fixed-size", cls="q", size=11)
text(xs[2], 236, "memory", cls="q", size=11)
text(cx, 548, "any distance, but squeezed into one vector", cls="q", size=12.5)
text(cx, 568, "T sequential steps: hard to parallelize", cls="q", size=12.5)

# ---- Column 3: self-attention; new part = content-based weights over all pairs ----
x0 = 2 * COL
cx = x0 + COL / 2
header(cx, 3, "Self-attention", "Bahdanau, then the Transformer", "NEW: weights from content, all pairs")
xs = token_xs(x0)
inputs(xs)
ox = xs[5]
weights = [0.04, 0.62, 0.03, 0.05, 0.14, 0.12]
for i, (x, a) in enumerate(zip(xs, weights)):
    sw = 1 + 7 * a
    tx = ox - 26 + i * 9
    out.append(f'<path d="M{x} {TOK_Y - 15} C{x} {300}, {tx} {260}, {tx} {OUT_Y + 19}" class="e3" style="stroke-width:{sw:.1f};opacity:{0.35 + a:.2f}"/>')
    text(x, TOK_Y + 32, f"{a:.2f}", cls="cl3" if a > 0.3 else "q", size=10, weight=600 if a > 0.3 else 400)
output(ox, "n3")
rect(xs[1] + 4, 200, 156, 46, cls="n3")
text(xs[1] + 4, 196, "weight = softmax(q·k)", size=11, weight=600)
text(xs[1] + 4, 213, "query asks, keys answer", cls="q", size=10)
text(cx, 548, "any distance in one step, chosen by content", cls="q", size=12.5)
text(cx, 568, "cost: T² pairs, all computed in parallel", cls="q", size=12.5)

# column separators
for x in (COL, 2 * COL):
    out.append(f'<path d="M{x} 20 V585" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.off{opacity:.5}
.e,.e1,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)}
.e1{stroke:var(--mlx-accent,#2647c9)} .e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b);stroke-linecap:round}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.win1{fill:none;stroke:var(--mlx-accent,#2647c9);stroke-width:2;stroke-dasharray:6 4}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.cl1{fill:var(--mlx-accent,#2647c9)} .cl2{fill:var(--mlx-good,#1f8a5b)} .cl3{fill:var(--mlx-warn,#b5562b)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".mix-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="mix-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="mix-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
