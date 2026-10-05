"""Check every citation in the chapters against arXiv and Semantic Scholar.

A citation is any "Authors, Year, [Title](url)" in a chapter's Markdown, the
form every Further reading list uses. For each one this checks that the link
resolves to a paper with that title, that the first author matches, that
"et al." is used only for three or more authors, and that the year is the
paper's arXiv or venue year. Writes a Markdown report.

    python tools/cite_check.py --out cite-report.md

Standard library only. Set S2_API_KEY for higher Semantic Scholar rate limits.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).resolve().parents[1]
CITATION = re.compile(r"(?:^|\n)[-*] ([^\n\[\]]+?), (\d{4})[a-z]?, \[([^\]]+)\]\((\S+?)\)")
ARXIV_ID = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5}|[a-z\-]+/\d{7})")
S2 = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,year,authors,publicationDate,externalIds,venue"
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def get(url: str, retries: int = 5) -> bytes | None:
    headers = {"User-Agent": "ml-explained-cite-check"}
    if "semanticscholar" in url and os.environ.get("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code != 429 and e.code < 500:
                raise
        except urllib.error.URLError:
            pass
        time.sleep(2 ** attempt)
    return None


def citations() -> list[dict]:
    found = []
    for nb_path in sorted((REPO / "chapters").glob("*/index.ipynb")):
        nb = json.loads(nb_path.read_text())
        text = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
        for authors, year, title, url in CITATION.findall(text):
            found.append({"chapter": nb_path.parent.name, "authors": authors.strip(), "year": int(year),
                          "title": title.strip(), "url": url})
    return found


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", s.lower())).strip()


def title_matches(cited: str, actual: str) -> bool:
    a, b = norm(cited), norm(actual)
    # Short forms ("Switch Transformers") are fine when they start the full title.
    return a == b or b.startswith(a) or difflib.SequenceMatcher(None, a, b).ratio() > 0.85


def surname(name: str) -> str:
    return norm(name.split()[-1]) if name.split() else ""


def cited_names(authors: str) -> tuple[list[str], bool]:
    et_al = "et al" in authors
    names = re.split(r",\s*|\s+and\s+|\s*&\s*", authors.replace("et al.", "").replace("et al", ""))
    return [n.strip() for n in names if n.strip()], et_al


def arxiv_lookup(ids: list[str], fetch=get) -> dict[str, dict]:
    out = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        raw = fetch("https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(batch), "max_results": len(batch)}))
        if raw is None:
            continue
        for entry in ET.fromstring(raw).findall("a:entry", ATOM):
            m = ARXIV_ID.search(entry.findtext("a:id", "", ATOM))
            if not m:
                continue
            out[m.group(1)] = {
                "title": " ".join(entry.findtext("a:title", "", ATOM).split()),
                "year": int(entry.findtext("a:published", "0", ATOM)[:4]),
                "authors": [a.findtext("a:name", "", ATOM) for a in entry.findall("a:author", ATOM)],
            }
        time.sleep(3)  # arXiv asks for one request every three seconds
    return out


def s2_lookup(c: dict, arxiv_id: str | None, fetch=get) -> dict | None:
    if arxiv_id:
        raw = fetch(f"{S2}/paper/arXiv:{arxiv_id}?fields={S2_FIELDS}")
    else:
        raw = fetch(f"{S2}/paper/search/match?" + urllib.parse.urlencode({"query": c["title"], "fields": S2_FIELDS}))
    if not raw:
        return None
    data = json.loads(raw)
    paper = data["data"][0] if "data" in data else data
    time.sleep(1.1)
    return {"title": paper.get("title") or "", "year": paper.get("year"),
            "authors": [a["name"] for a in paper.get("authors") or []], "venue": paper.get("venue") or ""}


def check(c: dict, paper: dict | None, venue: dict | None) -> list[str]:
    """Return the problems with one citation; an empty list means it checks out."""
    ref = paper or venue
    if ref is None:
        return ["paper not found from its link or title"]
    problems = []
    if not title_matches(c["title"], ref["title"]):
        where = "the link points to" if paper else "the closest match is"
        problems.append(f"title differs: {where} \"{ref['title']}\"")
    names, et_al = cited_names(c["authors"])
    actual = ref["authors"] or (venue or {}).get("authors") or []
    if names and actual and surname(names[0]) != surname(actual[0]):
        problems.append(f"first author is {actual[0]}, not {names[0]}")
    if actual:
        if et_al and len(actual) < 3:
            problems.append(f"\"et al.\" but the paper has {len(actual)} authors: {', '.join(actual)}")
        elif not et_al and len(names) != len(actual):
            shown = ", ".join(actual) if len(actual) <= 4 else f"{actual[0]} and {len(actual) - 1} others"
            problems.append(f"names {len(names)} authors, the paper has {len(actual)}: {shown}")
    years = {y for y in [paper and paper["year"], venue and venue["year"]] if y}
    if years and c["year"] not in years:
        problems.append(f"year {c['year']}, but the paper is from {' / '.join(map(str, sorted(years)))}")
    return problems


def run(fetch=get) -> tuple[str, int]:
    cites = citations()
    ids = sorted({m.group(1) for c in cites if (m := ARXIV_ID.search(c["url"]))})
    arxiv = arxiv_lookup(ids, fetch)
    rows, n_problems = [], 0
    for chapter in sorted({c["chapter"] for c in cites}):
        mine = [c for c in cites if c["chapter"] == chapter]
        bad = []
        for c in mine:
            m = ARXIV_ID.search(c["url"])
            arxiv_id = m.group(1) if m else None
            paper = arxiv.get(arxiv_id) if arxiv_id else None
            if arxiv_id and paper is None:
                bad.append((c, [f"arXiv {arxiv_id} not found"]))
                continue
            venue = s2_lookup(c, arxiv_id, fetch)
            if problems := check(c, paper, venue):
                bad.append((c, problems))
        n_problems += len(bad)
        rows.append(f"## {chapter}: {len(mine) - len(bad)} of {len(mine)} check out\n")
        for c, problems in bad:
            rows.append(f"- {c['authors']}, {c['year']}, [{c['title']}]({c['url']})")
            rows += [f"  - {p}" for p in problems]
        rows.append("")
    head = f"# Citation check\n\n{len(cites)} citations, {n_problems} with something to look at.\n\n"
    return head + "\n".join(rows), n_problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", help="write the report here as well as to stdout")
    args = ap.parse_args()
    report, _ = run()
    print(report)
    if args.out:
        pathlib.Path(args.out).write_text(report)


if __name__ == "__main__":
    sys.exit(main())
