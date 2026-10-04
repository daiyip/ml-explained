"""One small training loop shared by every chapter."""

from __future__ import annotations

import math
import time

import torch

from mlexp.data import get_batch


def count_params(module: torch.nn.Module) -> int:
    return sum(p.numel() for p in module.parameters())


@torch.no_grad()
def _estimate_loss(model, ids, batch_size, block_size, iters, generator):
    model.eval()
    losses = []
    for _ in range(iters):
        x, y = get_batch(ids, batch_size, block_size, generator)
        _, loss = model(x, y, include_aux=False)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)


def train_lm(
    model,
    train_ids,
    val_ids,
    steps: int = 600,
    lr: float = 3e-3,
    batch_size: int = 32,
    block_size: int = 128,
    eval_every: int = 50,
    eval_iters: int = 10,
    warmup_frac: float = 0.1,
    seed: int = 0,
    log: bool = True,
):
    """Train a language model with AdamW, warmup and cosine decay.

    The model's forward must accept (x, y, include_aux=...) and return
    (logits, loss). Returns a history dict with step, train and val losses.
    """
    torch.manual_seed(seed)
    gen = torch.Generator().manual_seed(seed)
    eval_gen = torch.Generator().manual_seed(1234)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.95), weight_decay=0.1)
    warmup = max(1, int(steps * warmup_frac))

    def lr_at(step):
        if step < warmup:
            return lr * (step + 1) / warmup
        progress = (step - warmup) / max(1, steps - warmup)
        return lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * progress)))

    history = {"step": [], "train": [], "val": []}
    start = time.time()
    for step in range(steps + 1):
        if step % eval_every == 0 or step == steps:
            history["step"].append(step)
            history["train"].append(_estimate_loss(model, train_ids, batch_size, block_size, eval_iters, eval_gen))
            history["val"].append(_estimate_loss(model, val_ids, batch_size, block_size, eval_iters, eval_gen))
            if log and (step % (eval_every * 4) == 0 or step == steps):
                print(f"step {step:4d}  train {history['train'][-1]:.3f}  val {history['val'][-1]:.3f}  ({time.time() - start:.0f}s)")
        if step == steps:
            break
        for group in opt.param_groups:
            group["lr"] = lr_at(step)
        x, y = get_batch(train_ids, batch_size, block_size, gen)
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    return history
