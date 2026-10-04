# ML Explained

A post-mortem of deep learning from AlexNet (2012) to today's large language models: take a modern Transformer apart, then trace how each building block evolved and why each replacement won.

Start with [`chapters/index.md`](chapters/index.md) for the reading map and the full evolution tree.

## Repository layout

```
chapters/            one folder per chapter: index.ipynb plus figures/
mlexp/               shared helpers: tiny datasets, the training loop, plots,
                     and the minimal Transformer every chapter builds on
tools/survey.py      paper survey for a lineage (Semantic Scholar)
tools/lineages.json  seed papers for each lineage
mkdocs.yml           site config: notebooks render as pages
```

## Running a chapter

Each notebook has an "Open in Colab" badge and installs the helpers itself. To run locally:

```bash
pip install -e .
pip install jupyter
jupyter lab chapters/01-anatomy/index.ipynb
```

Every experiment is sized to finish in under 10 minutes on a laptop CPU.

## Building the site

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Notebooks are committed with their outputs, so the site build does not re-run them. The `Publish site` workflow deploys to GitHub Pages on every push to `main` once Pages is enabled with "GitHub Actions" as the source (Settings, Pages).

## Surveying papers for a lineage

Run the `Paper survey` workflow from the Actions tab and pick a lineage. It finds each seed paper in `tools/lineages.json` on Semantic Scholar and lists its most-cited follow-ups. The report appears in the run summary and as a downloadable artifact. Locally:

```bash
python tools/survey.py channel-mixing --out surveys/channel-mixing.md
```

An optional `S2_API_KEY` repository secret raises the Semantic Scholar rate limit.
