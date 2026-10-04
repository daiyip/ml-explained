"""A minimal modern Transformer, written to be read top to bottom.

Chapter 1 (anatomy) builds this file block by block. Later chapters import it
and swap one block at a time, e.g. a different feed-forward layer.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class RMSNorm(nn.Module):
    """Rescale each token vector to unit root-mean-square, then apply a learned gain."""

    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        return self.weight * x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)


def apply_rope(x):
    """Rotary position encoding: rotate pairs of channels by a position-dependent angle.

    x has shape (batch, heads, seq, head_dim). Because queries and keys are both
    rotated, their dot product depends only on the distance between positions.
    """
    seq, dim = x.shape[-2], x.shape[-1]
    half = dim // 2
    freqs = 10000 ** (-torch.arange(half, device=x.device) / half)
    angles = torch.arange(seq, device=x.device)[:, None] * freqs[None, :]
    cos, sin = angles.cos(), angles.sin()
    x1, x2 = x[..., :half], x[..., half:]
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)


class Attention(nn.Module):
    """Multi-head self-attention: every token looks up information from other tokens."""

    def __init__(self, dim: int, n_heads: int, causal: bool = True, rope: bool = True):
        super().__init__()
        self.n_heads, self.causal, self.rope = n_heads, causal, rope
        self.qkv = nn.Linear(dim, 3 * dim, bias=False)
        self.out = nn.Linear(dim, dim, bias=False)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=-1)
        q, k, v = (t.view(B, T, self.n_heads, C // self.n_heads).transpose(1, 2) for t in (q, k, v))
        if self.rope:
            q, k = apply_rope(q), apply_rope(k)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=self.causal)
        return self.out(y.transpose(1, 2).reshape(B, T, C))


class SwiGLU(nn.Module):
    """Feed-forward layer: a gated MLP applied to each token independently."""

    def __init__(self, dim: int, hidden: int | None = None):
        super().__init__()
        hidden = hidden or int(8 * dim / 3)  # keeps parameters equal to a 4x ReLU MLP
        self.gate = nn.Linear(dim, hidden, bias=False)
        self.up = nn.Linear(dim, hidden, bias=False)
        self.down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        return self.down(F.silu(self.gate(x)) * self.up(x))


class Block(nn.Module):
    """Pre-norm Transformer block: x + attention(norm(x)), then x + ffn(norm(x))."""

    def __init__(self, dim, n_heads, ffn=None, causal=True, rope=True, norm=True, residual=True):
        super().__init__()
        self.residual = residual
        self.norm1 = RMSNorm(dim) if norm else nn.Identity()
        self.attn = Attention(dim, n_heads, causal=causal, rope=rope)
        self.norm2 = RMSNorm(dim) if norm else nn.Identity()
        self.ffn = ffn if ffn is not None else SwiGLU(dim)

    def forward(self, x):
        if self.residual:
            x = x + self.attn(self.norm1(x))
            return x + self.ffn(self.norm2(x))
        return self.ffn(self.norm2(self.attn(self.norm1(x))))


class TransformerLM(nn.Module):
    """Decoder-only language model: embed tokens, run N blocks, predict the next token."""

    def __init__(self, vocab_size, dim=128, n_layers=4, n_heads=4, make_ffn=None, **block_kwargs):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, dim)
        self.blocks = nn.ModuleList(
            Block(dim, n_heads, ffn=make_ffn(dim) if make_ffn else None, **block_kwargs)
            for _ in range(n_layers)
        )
        self.norm = RMSNorm(dim)
        self.head = nn.Linear(dim, vocab_size, bias=False)

    def forward(self, idx, targets=None, include_aux=True):
        x = self.embed(idx)  # (B, T) -> (B, T, dim)
        for block in self.blocks:
            x = block(x)
        logits = self.head(self.norm(x))  # (B, T, vocab)
        if targets is None:
            return logits, None
        loss = F.cross_entropy(logits.flatten(0, 1), targets.flatten())
        if include_aux:  # extra losses some blocks add, e.g. MoE load balancing
            loss = loss + sum(getattr(b.ffn, "aux_loss", 0.0) for b in self.blocks)
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, n_new, temperature=1.0):
        for _ in range(n_new):
            logits, _ = self(idx)
            probs = F.softmax(logits[:, -1] / temperature, dim=-1)
            idx = torch.cat([idx, torch.multinomial(probs, 1)], dim=1)
        return idx


class PatchEmbed(nn.Module):
    """Cut an image into patches and project each patch to a token vector."""

    def __init__(self, patch: int, channels: int, dim: int):
        super().__init__()
        self.proj = nn.Conv2d(channels, dim, kernel_size=patch, stride=patch)

    def forward(self, images):  # (B, C, H, W) -> (B, n_patches, dim)
        return self.proj(images).flatten(2).transpose(1, 2)


class VisionTransformer(nn.Module):
    """ViT: the same blocks, with patches in and a class label out, and no causal mask."""

    def __init__(self, n_classes, image=32, patch=4, channels=3, dim=128, n_layers=4, n_heads=4):
        super().__init__()
        self.embed = PatchEmbed(patch, channels, dim)
        self.pos = nn.Parameter(torch.zeros(1, (image // patch) ** 2, dim))
        self.blocks = nn.ModuleList(
            Block(dim, n_heads, causal=False, rope=False) for _ in range(n_layers)
        )
        self.norm = RMSNorm(dim)
        self.head = nn.Linear(dim, n_classes)

    def forward(self, images):
        x = self.embed(images) + self.pos
        for block in self.blocks:
            x = block(x)
        return self.head(self.norm(x).mean(dim=1))  # average the patch tokens, then classify
