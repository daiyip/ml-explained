"""Figure 13.1: the three generations of post-training, with each generation's new part highlighted.

The SVG has a transparent background and takes its colours from the site's CSS variables when it is
inlined into the page (falling back to the light palette when opened on its own).
Run: python tools/figures/posttrain_lineage.py
"""
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parents[2] / "chapters/13-post-training/figures/posttrain-lineage.svg"
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
    out.append(f'<path d="{d}" class="{cls}" marker-end="url(#post-a)"/>')


def tag(cx, y, s, n):
    w = len(s) * 6.3 + 20
    out.append(f'<rect x="{cx - w / 2}" y="{y - 13}" width="{w}" height="19" rx="9.5" class="tag{n}"/>')
    text(cx, y + 1, s, cls=f"tagt{n}", size=10.5, weight=600)


def chip(cx, cy, ok, n):
    """A sampled answer: a small rounded box marked right or wrong."""
    cls = f"n{n}" if ok else "b off"
    out.append(f'<rect x="{cx - 17}" y="{cy - 13}" width="34" height="26" rx="6" class="{cls}"/>')
    text(cx, cy + 6, "✓" if ok else "✗", cls="t" if ok else "q", size=13, weight=700)


TAGS = []


def header(cx, n, title, sub, new):
    text(cx, 36, f"{n}. {title}", size=17, weight=700)
    text(cx, 57, sub, cls="q", size=13)
    TAGS.append((cx, new, n))


# ---- Column 1: supervised fine-tuning; new part = demonstrations ----
cx = 160
header(cx, 1, "Instruction tuning", "FLAN, InstructGPT SFT, 2021-22", "NEW: imitate demonstrations")
out.append('<g transform="translate(0,40)">')
box(cx, 440, 220, "Pretrained model", "predicts the next token")
arrow(f"M{cx} 440 V408")
out.append(f'<rect x="{cx - 110}" y="296" width="220" height="110" rx="8" class="n1"/>')
text(cx, 318, "Demonstration", weight=600)
out.append(f'<rect x="{cx - 92}" y="330" width="184" height="26" rx="5" class="b"/>')
text(cx, 348, "prompt: Q: love", cls="q", size=11.5)
out.append(f'<rect x="{cx - 92}" y="362" width="184" height="26" rx="5" class="b hi1"/>')
text(cx, 380, "answer: Love is ...", cls="t", size=11.5, weight=600)
arrow(f"M{cx} 296 V252")
box(cx, 204, 220, "Cross-entropy", "on the answer tokens only")
arrow(f"M{cx} 204 V150")
box(cx, 102, 220, "SFT model", "follows the format")
text(cx, 530, "signal: every token of a written answer", cls="q", size=12.5)

# ---- Column 2: preference learning; new part = comparisons ----
cx = 480
out.append("</g>")
header(cx, 2, "Preference learning", "RLHF 2022, DPO 2023", "NEW: learn from comparisons")
out.append('<g transform="translate(0,40)">')
box(cx, 440, 220, "SFT model", "writes two answers")
arrow(f"M{cx} 440 V408")
out.append(f'<rect x="{cx - 110}" y="330" width="220" height="76" rx="8" class="n2"/>')
text(cx, 352, "A person compares them", weight=600)
out.append(f'<rect x="{cx - 92}" y="364" width="86" height="26" rx="5" class="b hi2"/>')
text(cx - 49, 382, "A  better", cls="t", size=11.5, weight=600)
out.append(f'<rect x="{cx + 6}" y="364" width="86" height="26" rx="5" class="b off"/>')
text(cx + 49, 382, "B  worse", cls="q", size=11.5)
lx, rx = cx - 64, cx + 64
arrow(f"M{lx} 330 V300")
arrow(f"M{rx} 330 V300", cls="e2")
box(lx, 252, 120, "Reward model", "Bradley-Terry")
box(rx, 252, 120, "DPO loss", "on the pair", cls="n2")
arrow(f"M{lx} 252 V222")
box(lx, 174, 120, "RL (PPO)", "+ KL to SFT")
arrow(f"M{lx} 174 V150")
arrow(f"M{rx} 252 V150", cls="e2")
box(cx, 102, 220, "Aligned model", "stays near the SFT model")
text(cx, 530, "signal: which of two answers is better", cls="q", size=12.5)

# ---- Column 3: RL on verifiable rewards; new part = a checker ----
cx = 800
out.append("</g>")
header(cx, 3, "RL on verifiable rewards", "GRPO, DeepSeek-R1, 2024-25", "NEW: reward from a checker")
out.append('<g transform="translate(0,40)">')
box(cx, 440, 236, "Checkable prompt", "Q: 23+45, answer known")
arrow(f"M{cx} 440 V408")
out.append(f'<rect x="{cx - 118}" y="330" width="236" height="76" rx="8" class="b"/>')
text(cx, 352, "Sample a group of answers", weight=600)
for i, ok in enumerate([True, False, True, False, False]):
    chip(cx - 84 + i * 42, 380, ok, 3)
arrow(f"M{cx} 330 V300")
box(cx, 252, 220, "Verifier", "reward 1 if correct, else 0", cls="n3")
arrow(f"M{cx} 252 V222", cls="e3")
box(cx, 174, 236, "Group-relative advantage", "reward minus the group mean")
arrow(f"M{cx} 174 V150")
box(cx, 102, 220, "Policy gradient", "more of what was right")
text(cx, 530, "signal: right or wrong, for each sample", cls="q", size=12.5)

out.append("</g>")
for cx, s_, n in TAGS:
    tag(cx, 86, s_, n)

for x in (320, 640):
    out.append(f'<path d="M{x} 20 V580" class="sep"/>')

STYLE = """
.t{fill:var(--mlx-ink,#131c27)} .q{fill:var(--mlx-ink-soft,#4a5868)}
.b{fill:var(--mlx-panel,#fff);stroke:var(--mlx-ink-soft,#4a5868);stroke-opacity:.45;stroke-width:1.25}
.off{opacity:.55}
.e,.e2,.e3{fill:none;stroke-width:1.5}
.e{stroke:var(--mlx-ink-soft,#4a5868)}
.e2{stroke:var(--mlx-good,#1f8a5b)} .e3{stroke:var(--mlx-warn,#b5562b)}
.ah{fill:var(--mlx-ink-soft,#4a5868)}
.sep{stroke:var(--mlx-rule,#d3dae3);stroke-dasharray:2 5}
.n1,.n2,.n3{stroke-width:2}
.n1{fill:rgba(38,71,201,.08);fill:color-mix(in srgb,var(--mlx-accent,#2647c9) 12%,transparent);stroke:var(--mlx-accent,#2647c9)}
.n2{fill:rgba(31,138,91,.08);fill:color-mix(in srgb,var(--mlx-good,#1f8a5b) 14%,transparent);stroke:var(--mlx-good,#1f8a5b)}
.n3{fill:rgba(181,86,43,.08);fill:color-mix(in srgb,var(--mlx-warn,#b5562b) 14%,transparent);stroke:var(--mlx-warn,#b5562b)}
.hi1{stroke:var(--mlx-accent,#2647c9);stroke-opacity:1;stroke-width:1.5}
.hi2{stroke:var(--mlx-good,#1f8a5b);stroke-opacity:1;stroke-width:1.5}
.tag1{fill:var(--mlx-accent,#2647c9)} .tag2{fill:var(--mlx-good,#1f8a5b)} .tag3{fill:var(--mlx-warn,#b5562b)}
.tagt1,.tagt2,.tagt3{fill:var(--mlx-paper,#fff)}
"""

# Scope every rule to this figure, since an inlined <style> applies to the whole page.
STYLE = re.sub(r"(^|\})\s*([^{}]+)\{", lambda m: m.group(1) + " " + ",".join(".post-fig " + x.strip() for x in m.group(2).split(",")) + "{", STYLE)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" class="post-fig" viewBox="0 0 {W} {H}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif">',
       f"<style>{STYLE}</style>",
       '<defs><marker id="post-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
       '<path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>'] + out + ["</svg>"]
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg) + "\n")
print("wrote", OUT)
