"""Summarise seed runs: mean and spread of every number a notebook prints.

    python tools/seed_table.py seed-runs/ > summary.md

Lines are matched across seeds by their text with the numbers removed, so
"SwiGLU ... final val loss 1.694" from each seed lands in one row.
"""

import pathlib
import re
import statistics
import sys

NUM = re.compile(r"(?<![\w.])-?\d[\d,]*\.?\d*(?:e[+-]?\d+)?")


def key(line: str) -> str:
    return " ".join(NUM.sub("#", line).split())  # numbers and column padding vary by seed


def numbers(line: str) -> list[float]:
    return [float(n.replace(",", "")) for n in NUM.findall(line)]


def fmt(values: list[float]) -> str:
    if len(set(values)) == 1:
        return f"{values[0]:,.0f}" if values[0].is_integer() else f"{values[0]:g}"
    mean, sd = statistics.mean(values), statistics.stdev(values)
    if 0 < abs(mean) < 0.01:
        return f"{mean:.2g} ± {sd:.2g}"
    return f"{mean:.3f} ± {sd:.3f}"


def summarise(chapter_dir: pathlib.Path) -> list[str]:
    runs = sorted(chapter_dir.glob("s*/results.txt"))
    per_seed = [p.read_text().splitlines() for p in runs]
    rows = [f"## {chapter_dir.name} ({len(runs)} seeds: {', '.join(p.parent.name for p in runs)})", ""]
    seen: dict[str, int] = {}
    for line in per_seed[0] if per_seed else []:
        k = key(line)
        nth = seen[k] = seen.get(k, -1) + 1  # repeated lines (one per epoch, say) pair up in order
        matches = [([l for l in lines if key(l) == k] + [None] * (nth + 1))[nth] for lines in per_seed]
        nums = [numbers(m) for m in matches if m is not None]
        if not nums or not nums[0] or len({len(n) for n in nums}) != 1:
            continue
        cols = [fmt([n[i] for n in nums]) for i in range(len(nums[0]))]
        if all("±" not in c for c in cols):
            continue  # the same in every seed (parameter counts, versions)
        rows.append(f"- `{k}`: " + " | ".join(cols))
    return rows + [""]


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "seed-runs")
    for chapter in sorted(p for p in root.iterdir() if p.is_dir()):
        print("\n".join(summarise(chapter)))
