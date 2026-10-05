"""Re-run a chapter notebook with every random seed shifted by an offset.

    python tools/seeds.py 05-channel-mixing 1 out/

Seed 0 is the run committed in the notebook. Offset k adds k to every
torch, numpy and random seed the notebook sets, so the same code runs on
different initializations and batches. Writes the executed notebook and its
printed output (results.txt) to out/<chapter>/s<k>/.
"""

import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

PATCH = '''import sys, random as _r, numpy as _np, torch as _t
sys.path.insert(0, {repo!r})
_OFF = {off}
_ms = _t.manual_seed
_t.manual_seed = lambda s: _ms(int(s) + _OFF)
class _G(_t.Generator):
    def manual_seed(self, s):
        return super().manual_seed(int(s) + _OFF)
_t.Generator = _G
_rng = _np.random.default_rng
_np.random.default_rng = lambda s=None, *a, **k: _rng(None if s is None else int(s) + _OFF, *a, **k)
_nps = _np.random.seed
_np.random.seed = lambda s=None: _nps(None if s is None else int(s) + _OFF)
_rs = _r.seed
_r.seed = lambda s=None, *a, **k: _rs(s + _OFF if isinstance(s, int) else s, *a, **k)
'''


def printed(nb) -> str:
    lines = []
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            if out.get("name") == "stdout":
                lines += "".join(out["text"]).strip().splitlines()
    return "\n".join(line for line in lines if line.strip()) + "\n"


def main(chapter: str, offset: int, out_root: str) -> None:
    out = pathlib.Path(out_root) / chapter / f"s{offset}"
    out.mkdir(parents=True, exist_ok=True)
    src = REPO / "chapters" / chapter / "index.ipynb"
    nb = json.loads(src.read_text())
    if offset:  # seed 0 is the committed run, so it executes unchanged
        nb["cells"].insert(0, {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                               "source": PATCH.format(repo=str(REPO), off=offset)})
    nb_in = src.with_name(f".seed{offset}.ipynb")  # next to the original, so relative paths resolve
    nb_in.write_text(json.dumps(nb))
    try:
        subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                        "--ExecutePreprocessor.timeout=3600", "--output-dir", str(out),
                        "--output", "executed.ipynb", str(nb_in)], check=True)
    finally:
        nb_in.unlink()
    (out / "results.txt").write_text(printed(json.loads((out / "executed.ipynb").read_text())))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "seed-runs")
