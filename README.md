# Transformer Explained

*A modern Transformer taken apart, one building block at a time.*

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

## Checking results across seeds

The committed notebooks are single runs (seed 0). Run the `Seed runs` workflow from the Actions tab to re-run chapters with more seeds: it runs each chapter and seed as a parallel job, shows the mean and spread of every number the notebooks print in the run summary, and packages the executed notebooks and that summary as the `seed-results` artifact to download. Leave the inputs at `all` and `0 1 2` for everything, or name chapters to run a few. Locally:

```bash
python tools/seeds.py 05-channel-mixing 1 seed-runs   # seed offset 1
python tools/seed_table.py seed-runs > summary.md
```

## Checking citations

Run the `Citation check` workflow from the Actions tab; it also runs on pull requests that change a chapter. It looks up every "Authors, Year, [Title](url)" citation on arXiv and Semantic Scholar and lists any whose link, title, first author, "et al." or year does not match. The report is in the run summary and the `cite-report` artifact. Locally: `python tools/cite_check.py --out cite-report.md`.

## Surveying papers for a lineage

Run the `Paper survey` workflow from the Actions tab and pick a lineage. It finds each seed paper in `tools/lineages.json` on Semantic Scholar and lists its most-cited follow-ups. The report appears in the run summary and as a downloadable artifact. Locally:

```bash
python tools/survey.py channel-mixing --out surveys/channel-mixing.md
```

An optional `S2_API_KEY` repository secret raises the Semantic Scholar rate limit.

## Licence

The code (`mlexp/`, `tools/` and the notebooks' code cells) is [MIT](LICENSE). The text and figures are
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), so you may quote, translate and teach from them with
credit. See [LICENSES.md](LICENSES.md).
