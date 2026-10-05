"""Survey the papers behind one lineage, using the Semantic Scholar API.

For each seed paper listed in tools/lineages.json, finds the paper, then lists
its most-cited follow-ups, so a chapter author can see which later work changed
the explanation. Writes a Markdown report.

    python tools/survey.py channel-mixing --out surveys/channel-mixing.md

Standard library only. Set S2_API_KEY for higher rate limits.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,citationCount,url,externalIds"
LINEAGES = pathlib.Path(__file__).with_name("lineages.json")


def fetch(path: str, params: dict, retries: int = 6) -> dict:
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    headers = {"User-Agent": "transformer-explained-survey"}
    if os.environ.get("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}
            if e.code != 429 and e.code < 500:
                raise
        except urllib.error.URLError:
            pass
        time.sleep(2 ** attempt)  # rate limited or transient: back off and retry
    raise RuntimeError(f"giving up on {url}")


def find_paper(title: str) -> dict:
    result = fetch("/paper/search/match", {"query": title, "fields": FIELDS})
    return (result.get("data") or [{}])[0]


def top_followups(paper_id: str, n: int) -> list[dict]:
    result = fetch(f"/paper/{paper_id}/citations", {"fields": FIELDS, "limit": 1000})
    citing = [row["citingPaper"] for row in result.get("data", []) if row.get("citingPaper", {}).get("title")]
    return sorted(citing, key=lambda p: p.get("citationCount") or 0, reverse=True)[:n]


def link(p: dict) -> str:
    arxiv = (p.get("externalIds") or {}).get("ArXiv")
    url = f"https://arxiv.org/abs/{arxiv}" if arxiv else p.get("url", "")
    return f"[{p.get('title', 'untitled')}]({url})" if url else p.get("title", "untitled")


def survey(lineage: str, seeds: list[str], n_followups: int, fetch_paper=find_paper, fetch_followups=top_followups) -> str:
    lines = [f"# Paper survey: {lineage}", "",
             f"Seed papers from `tools/lineages.json`, each with its {n_followups} most-cited follow-ups. "
             "Data from Semantic Scholar: follow-ups are ranked among the first 1,000 citing papers it returns, "
             "and citation counts change over time.", ""]
    for title in seeds:
        paper = fetch_paper(title)
        if not paper.get("paperId"):
            lines += [f"## {title}", "", "Not found on Semantic Scholar.", ""]
            continue
        lines += [f"## {paper.get('year', '?')}: {link(paper)}", "",
                  f"Cited by {paper.get('citationCount', 0):,} papers.", "",
                  "| Year | Follow-up | Citations |", "| --- | --- | --- |"]
        for f in fetch_followups(paper["paperId"], n_followups):
            lines.append(f"| {f.get('year') or '?'} | {link(f)} | {f.get('citationCount') or 0:,} |")
        lines.append("")
    return "\n".join(lines)


def main():
    lineages = json.loads(LINEAGES.read_text())
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("lineage", choices=sorted(lineages))
    parser.add_argument("--followups", type=int, default=8)
    parser.add_argument("--out", type=pathlib.Path)
    args = parser.parse_args()
    report = survey(args.lineage, lineages[args.lineage], args.followups)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report)
    print(report)


if __name__ == "__main__":
    main()
