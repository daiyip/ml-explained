"""Tiny datasets that download in seconds and train on a laptop CPU."""

from __future__ import annotations

import pathlib
import urllib.request

import torch

TINY_SHAKESPEARE_URL = (
    "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
)
CACHE_DIR = pathlib.Path.home() / ".cache" / "mlexp"


def tiny_shakespeare() -> str:
    """Return the ~1 MB TinyShakespeare corpus, downloading it once."""
    path = CACHE_DIR / "tinyshakespeare.txt"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(TINY_SHAKESPEARE_URL, path)
    return path.read_text(encoding="utf-8")


class CharTokenizer:
    """One token per character: the simplest possible tokenizer."""

    def __init__(self, text: str):
        self.chars = sorted(set(text))
        self.stoi = {c: i for i, c in enumerate(self.chars)}

    @property
    def vocab_size(self) -> int:
        return len(self.chars)

    def encode(self, text: str) -> torch.Tensor:
        return torch.tensor([self.stoi[c] for c in text], dtype=torch.long)

    def decode(self, ids) -> str:
        return "".join(self.chars[int(i)] for i in ids)


def load_char_corpus(val_fraction: float = 0.1):
    """Return (tokenizer, train_ids, val_ids) for TinyShakespeare."""
    text = tiny_shakespeare()
    tok = CharTokenizer(text)
    ids = tok.encode(text)
    split = int(len(ids) * (1 - val_fraction))
    return tok, ids[:split], ids[split:]


def get_batch(ids: torch.Tensor, batch_size: int, block_size: int, generator=None):
    """Sample random windows; targets are the inputs shifted by one token."""
    starts = torch.randint(len(ids) - block_size - 1, (batch_size,), generator=generator)
    x = torch.stack([ids[s : s + block_size] for s in starts])
    y = torch.stack([ids[s + 1 : s + block_size + 1] for s in starts])
    return x, y
