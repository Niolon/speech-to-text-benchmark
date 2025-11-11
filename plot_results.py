import argparse
import os
from typing import (
    Dict,
    Tuple
)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from benchmark import RESULTS_FOLDER
from dataset import Datasets
from engine import (
    Engines,
)
from results import (
    RTF,
    WER_DE, WER_EN, WER_ES, WER_FR, WER_IT, WER_PT, PER_DE, PER_EN, PER_ES, PER_FR, PER_IT, PER_PT
)
Color = Tuple[float, float, float]


def rgb_from_hex(x: str) -> Color:
    x = x.strip("# ")
    assert len(x) == 6
    return int(x[:2], 16) / 255, int(x[2:4], 16) / 255, int(x[4:], 16) / 255


BLACK = rgb_from_hex("#000000")
GREY1 = rgb_from_hex("#4F4F4F")
GREY2 = rgb_from_hex("#5F5F5F")
GREY3 = rgb_from_hex("#6F6F6F")
GREY4 = rgb_from_hex("#7F7F7F")
GREY5 = rgb_from_hex("#8F8F8F")
WHITE = rgb_from_hex("#FFFFFF")
BLUE = rgb_from_hex("#377DFF")

ENGINE_PRINT_NAMES = {
    Engines.WHISPER_TINY: "Whisper\nTiny",
    Engines.WHISPER_BASE: "Whisper\nBase",
    Engines.WHISPER_SMALL: "Whisper\nSmall",
    Engines.WHISPER_MEDIUM: "Whisper\nMedium",
    Engines.WHISPER_LARGE: "Whisper\nLarge",
}

ENGINE_COLORS = {
    Engines.WHISPER_LARGE: GREY5,
    Engines.WHISPER_MEDIUM: GREY4,
    Engines.WHISPER_SMALL: GREY3,
    Engines.WHISPER_BASE: GREY2,
    Engines.WHISPER_TINY: GREY1,
}


def _plot_error_rate(
    engine_error_rate: Dict[Engines, Dict[Datasets, float]],
    save_path: str,
    streaming: bool,
    show: bool = False,
    punctuation: bool = False,
) -> None:
    sorted_error_rates = sorted(
        [
            (e, round(sum(w for w in engine_error_rate[e].values()) / len(engine_error_rate[e]) + 1e-9, 1))
            for e in engine_error_rate.keys()
        ],
        key=lambda x: x[1],
    )
    print("\n".join(f"{e.value}: {x}" for e, x in sorted_error_rates))

    _, ax = plt.subplots(figsize=(12, 6))

    for i, (engine, error_rate) in enumerate(sorted_error_rates, start=1):
        color = ENGINE_COLORS[engine]
        ax.bar([i], [error_rate], 0.4, color=color)
        ax.text(
            i,
            error_rate + 0.5,
            f"{error_rate}%",
            color=color,
            ha="center",
            va="bottom",
        )

    for spine in plt.gca().spines.values():
        if spine.spine_type != "bottom" and spine.spine_type != "left":
            spine.set_visible(False)

    plt.xticks(
        np.arange(1, len(sorted_error_rates) + 1),
        [ENGINE_PRINT_NAMES[x[0]] for x in sorted_error_rates],
        fontsize=8,
    )
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.0f}%"))
    if punctuation:
        plt.ylabel("Punctuation Error Rate (lower is better)")
    else:
        plt.ylabel("Word Error Rate (lower is better)")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path)
    print(f"Saved plot to `{save_path}`")

    if show:
        plt.show()

    plt.close()


def _plot_cpu(save_folder: str, show: bool, dataset: Datasets = Datasets.TED_LIUM) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    x_limit = 0
    for engine_type, engine_value in RTF.items():
        core_hour = engine_value[dataset] * 100
        core_hour = round(core_hour, 1)
        x_limit = max(x_limit, core_hour)
        ax.barh(
            ENGINE_PRINT_NAMES[engine_type],
            core_hour,
            height=0.5,
            color=ENGINE_COLORS[engine_type],
            edgecolor="none",
            label=ENGINE_PRINT_NAMES[engine_type],
        )
        ax.text(
            core_hour + 30,
            ENGINE_PRINT_NAMES[engine_type],
            f"{core_hour:.1f}\nCore-hour",
            ha="center",
            va="center",
            fontsize=12,
            color=ENGINE_COLORS[engine_type],
        )

    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xlim([0, x_limit + 50])
    ax.set_xticks([])
    ax.set_ylim([-0.5, 6.5])
    plt.title(
        "Core-hour required to process 100 hours of audio (lower is better)",
        fontsize=12,
    )
    plot_path = os.path.join(save_folder, "cpu_usage_comparison.png")
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    print(f"Saved plot to `{plot_path}`")

    if show:
        plt.show()

    plt.close()
    
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    save_folder = os.path.join(RESULTS_FOLDER, "plots")

    _plot_error_rate(WER_EN, save_path=os.path.join(save_folder, "WER.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_FR, save_path=os.path.join(save_folder, "WER_FR.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_DE, save_path=os.path.join(save_folder, "WER_DE.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_ES, save_path=os.path.join(save_folder, "WER_ES.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_IT, save_path=os.path.join(save_folder, "WER_IT.png"), streaming=False, show=args.show)
    _plot_error_rate(WER_PT, save_path=os.path.join(save_folder, "WER_PT.png"), streaming=False, show=args.show)

    _plot_error_rate(PER_EN, save_path=os.path.join(save_folder, "PER_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_FR, save_path=os.path.join(save_folder, "PER_FR_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_DE, save_path=os.path.join(save_folder, "PER_DE_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_ES, save_path=os.path.join(save_folder, "PER_ES_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_IT, save_path=os.path.join(save_folder, "PER_IT_ST.png"), streaming=True, punctuation=True, show=args.show)
    _plot_error_rate(PER_PT, save_path=os.path.join(save_folder, "PER_PT_ST.png"), streaming=True, punctuation=True, show=args.show)

if __name__ == "__main__":
    main()
