"""Figure 2.1: three generations of input representation, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/tokens_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/02-tokens/figures/tokens-lineage.svg"
W, H = 960, 525
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
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#tok-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def chip(x, y, w, s, cls="b", tcls="t", size=12):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="5" class="{cls}"/>')
    text(x + w / 2, y + 17, s, cls=tcls, size=size, weight=600)


def vec(x, y, vals, cls, cell=11):
    """A row of small cells; opacity encodes the value (one-hot or dense)."""
    for i, v in enumerate(vals):
        out.append(f'<rect x="{x + i * cell}" y="{y}" width="{cell - 2}" height="{cell - 2}" rx="2" class="{cls}" fill-opacity="{v:.2f}"/>')


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


DENSE = [[.9, .2, .6, .35, .8, .15, .5, .7], [.85, .3, .55, .4, .75, .2, .45, .65], [.2, .8, .15, .9, .3, .6, .85, .1]]

# ---- Column 1: one-hot over characters (or words) ----
cx = 160
header(cx, 1, "One-hot", "characters or whole words", "NEW: one symbol, one slot")
text(cx, 140, "text: “the king”", size=13)
chars = ["t", "h", "e", "␣", "k", "i", "n", "g"]
for i, c in enumerate(chars):
    chip(cx - 96 + i * 24, 152, 20, c, size=11)
text(cx, 202, "8 tokens", cls="q", size=12)
arrow(f"M{cx} 212 V238")
out.append(f'<rect x="{cx - 115}" y="244" width="230" height="168" rx="8" class="n1"/>')
text(cx, 266, "one-hot vectors, length V", weight=600, size=13)
for r, hot in enumerate([3, 6, 1, 5]):
    vec(cx - 72, 280 + r * 22, [1.0 if i == hot else 0.06 for i in range(13)], "v1")
text(cx, 384, "every pair equally far apart", cls="q", size=11.5)
text(cx, 400, "cosine(king, queen) = 0", cls="q", size=11.5)
text(cx, 446, "V = 65 characters: long sequences", cls="q", size=12)
text(cx, 466, "V = 12,631 words: huge, sparse", cls="q", size=12)
text(cx, 486, "rare and new words unseen", cls="q", size=12)

# ---- Column 2: learned dense embeddings (word2vec) ----
cx = 480
header(cx, 2, "Learned embeddings", "word2vec, then nn.Embedding", "NEW: a dense vector learned per token")
text(cx, 140, "text: “the king”", size=13)
chip(cx - 70, 152, 60, "the")
chip(cx + 10, 152, 60, "king")
text(cx, 202, "2 tokens (words)", cls="q", size=12)
arrow(f"M{cx} 212 V238")
out.append(f'<rect x="{cx - 115}" y="244" width="230" height="168" rx="8" class="n2"/>')
text(cx, 266, "lookup row of table E (V × d)", weight=600, size=13)
for r, (w, vals) in enumerate(zip(["king", "queen", "sword"], DENSE)):
    text(cx - 62, 290 + r * 24, w, cls="q", size=11, anchor="end")
    vec(cx - 52, 280 + r * 24, vals, "v2", cell=14)
text(cx, 384, "trained to predict neighbours", cls="q", size=11.5)
text(cx, 400, "similar use, nearby vectors", cls="q", size=11.5)
text(cx, 446, "d ≈ 100–300 numbers per word", cls="q", size=12)
text(cx, 466, "same as one-hot × a weight matrix", cls="q", size=12)
text(cx, 486, "still one row per whole word", cls="q", size=12)

# ---- Column 3: subwords and patches into the same width-d stream ----
cx = 800
header(cx, 3, "Subwords and patches", "BPE, ViT, multimodal", "NEW: a learned vocabulary of pieces")
text(cx, 140, "text and image", size=13)
for i, c in enumerate(["the", " k", "ing"]):
    chip(cx - 112 + i * 40, 152, 36, c, cls="n3", size=11)
for i in range(4):
    out.append(f'<rect x="{cx + 20 + (i % 2) * 22}" y="{150 + (i // 2) * 15}" width="20" height="13" rx="2" class="px"/>')
text(cx + 87, 169, "patches", cls="q", size=10.5)
text(cx, 202, "3 subwords + 4 patches", cls="q", size=12)
arrow(f"M{cx} 212 V238")
out.append(f'<rect x="{cx - 115}" y="244" width="230" height="168" rx="8" class="n3"/>')
text(cx, 266, "one sequence, width d", weight=600, size=13)
for r, (w, vals) in enumerate(zip(["“ing”", "patch 1", "patch 2"], DENSE)):
    text(cx - 62, 290 + r * 24, w, cls="q", size=11, anchor="end")
    vec(cx - 52, 280 + r * 24, vals[::-1] if r else vals, "v3" if r else "v2", cell=14)
text(cx, 384, "lookup for text, linear for pixels", cls="q", size=11.5)
text(cx, 400, "then the same Transformer", cls="q", size=11.5)
text(cx, 446, "V ≈ 32k–200k pieces, no unknowns", cls="q", size=12)
text(cx, 466, "a 16×16 patch is one token", cls="q", size=12)
text(cx, 486, "any modality, one stream", cls="q", size=12)

for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)
for x in (320, 640):
    out.append(f'<path d="M{x} 20 V505" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.e{fill:none;stroke-width:1.5;stroke:var(--mlx-ink-soft,#4a5868)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.v1{fill:var(--mlx-accent,#2647c9)} .v2{fill:var(--mlx-good,#1f8a5b)} .v3{fill:var(--mlx-warn,#b5562b)}
.px{fill:var(--mlx-warn,#b5562b);fill-opacity:.35;stroke:var(--mlx-warn,#b5562b);stroke-width:1}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".tok-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="tok-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="tok-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
