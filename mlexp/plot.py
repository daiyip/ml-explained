"""Plot helpers so every chapter's figures look the same."""

from __future__ import annotations

import matplotlib.pyplot as plt

PALETTE = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#4b5563"]


def setup_style():
    plt.rcParams.update(
        {
            "figure.figsize": (7, 4),
            "figure.dpi": 110,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.prop_cycle": plt.cycler(color=PALETTE),
            "font.size": 10,
        }
    )


def plot_histories(histories: dict, title: str, key: str = "val", ax=None):
    """Plot one loss curve per named run from train_lm histories."""
    if ax is None:
        _, ax = plt.subplots()
    for name, h in histories.items():
        ax.plot(h["step"], h[key], label=name)
    ax.set_xlabel("training step")
    ax.set_ylabel(f"{key} loss (nats per character)")
    ax.set_title(title)
    ax.legend(frameon=False)
    return ax
