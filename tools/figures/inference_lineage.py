"""Figure 14.1: three generations of using a trained model at inference time: decoding one token at a
time, chain of thought, and test-time search with verifiers and tools. Each column highlights what is new.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/inference_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/14-inference/figures/inference-lineage.svg"
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


def chip(cx, y, s, cls="b", w=34, h=26, tcls="t", size=12.5):
    rect(cx - w / 2, y, w, h, cls, rx=6)
    text(cx, y + h / 2 + 5, s, cls=tcls, size=size, weight=600)


def arrow(d, cls="e"):
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#inf-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: decoding; new part = the sampling rule and the KV cache ----
cx = 160
header(cx, 1, "Decoding", "one token per forward pass", "NEW: sampling knobs and a KV cache")
out.append('<g transform="translate(0,40)">')
# the text so far: three cached tokens and one new one
rect(cx - 110, 446, 150, 50, "n1 dash", rx=8)
for i, w in enumerate(["To", "be", "or"]):
    chip(cx - 82 + i * 47, 452, w, cls="b", w=40)
chip(cx + 74, 452, "not", cls="b", w=48)
text(cx - 35, 514, "KV cache: kept, not recomputed", cls="cl1", size=10.5, weight=600)
text(cx + 80, 514, "new", cls="q", size=10.5)
arrow(f"M{cx + 74} 452 V420")
box(cx, 372, 220, "Transformer", "one pass for the new token only")
arrow(f"M{cx} 372 V346")
rect(cx - 110, 216, 220, 128, "n1")
text(cx, 236, "Next-token probabilities", weight=600, size=13)
probs = [("to", 0.42), ("be", 0.24), ("I", 0.14), ("so", 0.09), ("a", 0.06), ("we", 0.05)]
bx0, base = cx - 84, 316
for i, (w, p) in enumerate(probs):
    x = bx0 + i * 30
    hgt = p * 140
    out.append(f'<rect x="{x}" y="{base - hgt}" width="20" height="{hgt}" rx="2" class="{"bar" if i < 3 else "bar0"}"/>')
    text(x + 10, base + 15, w, cls="q", size=10.5)
cut = bx0 + 3 * 30 - 5
out.append(f'<path d="M{cut} 246 V{base}" class="cut"/>')
text(cut + 4, 256, "top-p cut", cls="cl1", size=10, anchor="start", weight=600)
arrow(f"M{cx} 216 V190")
box(cx, 142, 240, "Pick one token", "greedy, or sample at temperature T")
arrow(f"M{cx} 142 V104")
text(cx, 96, "append it, then repeat", cls="q", size=12)
text(cx, 540, "serial steps per answer: L", cls="q", size=12.5)

# ---- Column 2: chain of thought; new part = intermediate tokens ----
cx = 480
out.append("</g>")
header(cx, 2, "Chain of thought", "write the steps before the answer", "NEW: intermediate tokens as memory")
out.append('<g transform="translate(0,40)">')
# layers x tokens grid: each written token is fed back in, so depth stacks
cols = [cx - 105, cx - 63, cx - 21, cx + 21, cx + 63, cx + 105]
labels = [("Q", "b"), ("=", "b"), ("s1", "n2"), ("s2", "n2"), ("s3", "n2"), ("ans", "b")]
rows = [400, 352, 304]
for (lab, cls), x in zip(labels, cols):
    chip(x, 440, lab, cls=cls, w=36)
    for y in rows:
        out.append(f'<circle cx="{x}" cy="{y}" r="7" class="node"/>')
    out.append(f'<path d="M{x} 440 V{rows[0] + 8}" class="e"/>')
text(cx - 136, rows[1] + 5, "L layers", cls="q", size=11, anchor="end")
out.append(f'<path d="M{cx - 128} {rows[0] + 6} V{rows[2] - 6}" class="e"/>')
# the serial path: up through the layers of one column, out as a token, back in at the next column
for i in range(1, 5):
    x0, x1 = cols[i], cols[i + 1]
    lane = x0 + 21
    out.append(f'<path d="M{x0} {rows[0]} V{rows[2]}" class="e2 thick"/>')
    arrow(f"M{x0} {rows[2] - 8} C{x0} 282 {lane} 282 {lane} 296 V482 H{x1 - 8} V470", cls="e2 thin")
arrow(f"M{cols[5]} {rows[2] - 8} V236")
rect(cx - 110, 186, 220, 48, "n2")
text(cx, 207, "Written tokens are read back", weight=600, size=13)
text(cx, 224, "each one adds L serial steps", cls="q", size=12)
arrow(f"M{cx} 186 V160")
box(cx, 112, 160, "Answer", "after k steps")
text(cx, 540, "serial steps per answer: L × k", cls="q", size=12.5)

# ---- Column 3: search, verification and tools; new part = many samples and a checker ----
cx = 800
out.append("</g>")
header(cx, 3, "Search and tools", "spend more compute per question", "NEW: sample N, verify, call tools")
out.append('<g transform="translate(0,40)">')
box(cx, 452, 200, "Question", "sample N chains from it")
xs = [cx - 87, cx - 29, cx + 29, cx + 87]
ans = [("7", True), ("3", False), ("7", True), ("7", True)]
for i, (ex, (a, ok)) in enumerate(zip(xs, ans)):
    arrow(f"M{cx + (i - 1.5) * 30} 452 L{ex} 424", cls="e")
    rect(ex - 24, 340, 48, 82, "b", rx=8)
    for j in range(3):
        out.append(f'<rect x="{ex - 14}" y="{350 + j * 15}" width="28" height="9" rx="2" class="line"/>')
    text(ex, 412, f"ans {a}", cls="t" if ok else "q", size=11, weight=600)
    out.append(f'<path d="M{ex} 340 V316" class="{"e3" if ok else "ed"}" marker-end="url(#inf-a)"/>')
rect(cx - 115, 262, 230, 52, "n3")
text(cx, 284, "Verifier or majority vote", weight=600, size=13)
text(cx, 302, "keep the answer that checks out", cls="q", size=12)
arrow(f"M{cx} 262 V236")
rect(cx - 115, 160, 230, 74, "b")
text(cx, 180, "Tool call inside a chain", weight=600, size=13)
chip(cx - 52, 192, "[3+5+9]", cls="n3", w=72, h=24, size=11.5)
arrow(f"M{cx - 14} 204 H{cx + 14}", cls="e3")
chip(cx + 50, 192, "17", cls="b", w=48, h=24, size=11.5)
text(cx + 50, 230, "inserted by the harness", cls="q", size=10)
arrow(f"M{cx} 160 V124")
box(cx, 88, 160, "Answer")
text(cx, 540, "cost per answer: N × tokens, plus tools", cls="q", size=12.5)
out.append("</g>")

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V585" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e,.e2,.e3,.ed{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)} .ed{stroke:var(--mlx-ink-soft,#4a5868);stroke-dasharray:3 4;opacity:.6}
.e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.thick{stroke-width:3;stroke-linecap:round} .thin{stroke-width:1.3}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.dash{stroke-dasharray:5 4;stroke-width:1.5}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
.bar{fill:var(--mlx-accent,#2647c9)} .bar0{fill:var(--mlx-ink-soft,#4a5868);opacity:.35}
.cut{stroke:var(--mlx-accent,#2647c9);stroke-width:1.5;stroke-dasharray:4 3}
.cl1{fill:var(--mlx-accent,#2647c9)}
.node{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-width:1.25}
.line{fill:var(--mlx-ink-soft,#4a5868);opacity:.3}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".inf-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="inf-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="inf-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
