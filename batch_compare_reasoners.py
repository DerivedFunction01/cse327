#!/usr/bin/env python3
"""Run reasoner comparisons across all experiment folders.

This script searches the current working directory recursively for matching
`std-*.csv` and `ming-*.csv` files, runs the comparison logic from
`compare_reasoners.py` on each pair, saves a plot next to the CSV files, and
writes a summary table for all comparisons.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from compare_reasoners import load_results, make_plot, summarize


@dataclass(frozen=True)
class ComparisonPair:
    std_path: Path
    ming_path: Path

    @property
    def suffix(self) -> str:
        name = self.std_path.stem
        if name.startswith("std-"):
            return name.removeprefix("std-")
        return name

    @property
    def plot_path(self) -> Path:
        return self.std_path.with_name(f"reasoner_comparison-{self.suffix}.png")

    @property
    def report_path(self) -> Path:
        return self.std_path.with_name(f"reasoner_comparison-{self.suffix}.txt")

    @property
    def size_tag(self) -> str:
        parts = self.std_path.stem.split("-")
        if len(parts) < 2:
            return "unknown"
        return parts[-1]


def _is_hidden_path(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return any(part.startswith(".") for part in parts)


def find_pairs(root: Path) -> list[ComparisonPair]:
    pairs: list[ComparisonPair] = []
    for std_path in sorted(root.rglob("std-*.csv")):
        if _is_hidden_path(std_path, root):
            continue
        ming_path = std_path.with_name(std_path.name.replace("std-", "ming-", 1))
        if not ming_path.exists():
            continue
        std_parts = std_path.stem.split("-")
        ming_parts = ming_path.stem.split("-")
        if len(std_parts) != len(ming_parts):
            continue
        if std_parts[-1] != ming_parts[-1]:
            continue
        pairs.append(ComparisonPair(std_path=std_path, ming_path=ming_path))
    return pairs


def write_summary(summary_rows: Iterable[dict[str, object]], output_path: Path) -> None:
    rows = list(summary_rows)
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    pair: ComparisonPair,
    summary: dict[str, float],
    output_path: Path,
    root: Path,
) -> None:
    text = (
        "Reasoner comparison\n"
        f"  std file:  {pair.std_path.relative_to(root)}\n"
        f"  ming file: {pair.ming_path.relative_to(root)}\n"
        f"  plot:      {pair.plot_path.relative_to(root)}\n"
        f"  txt file:   {pair.report_path.relative_to(root)}\n"
        "\n"
        f"Queries compared: {int(summary['queries'])}\n"
        f"std mean nodes:   {summary['std_mean_nodes']:.2f}\n"
        f"std median nodes: {summary['std_median_nodes']:.2f}\n"
        f"ming mean nodes:  {summary['ming_mean_nodes']:.2f}\n"
        f"ming median nodes: {summary['ming_median_nodes']:.2f}\n"
        "\n"
        f"std wins:         {int(summary['std_wins'])}\n"
        f"ming wins:        {int(summary['ming_wins'])}\n"
        f"ties:             {int(summary['ties'])}\n"
        "\n"
        f"both success:     {int(summary['both_success'])}\n"
        f"std only success: {int(summary['std_success_only'])}\n"
        f"ming only success: {int(summary['ming_success_only'])}\n"
        f"both fail:        {int(summary['both_fail'])}\n"
        "\n"
        f"mean(std - ming) nodes: {summary['mean_node_delta_std_minus_ming']:.2f}\n"
    )
    output_path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare every std/ming CSV pair under the current directory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Directory to scan recursively. Default: current directory.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("reasoner_comparison_summary.csv"),
        help="Output CSV file for the combined summary.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    pairs = find_pairs(root)
    if not pairs:
        print(f"No std/ming CSV pairs found under {root}")
        return 1

    summary_rows: list[dict[str, object]] = []
    for pair in tqdm(pairs, desc="Comparing reasoners", unit="pair"):
        std = load_results(pair.std_path)
        ming = load_results(pair.ming_path)
        summary = summarize(std, ming)
        make_plot(std, ming, pair.plot_path)

        row: dict[str, object] = {
            "folder": str(pair.std_path.parent.relative_to(root)),
            "std_file": str(pair.std_path.relative_to(root)),
            "ming_file": str(pair.ming_path.relative_to(root)),
            "plot_file": str(pair.plot_path.relative_to(root)),
            "report_file": str(pair.report_path.relative_to(root)),
            "queries": int(summary["queries"]),
            "std_mean_nodes": f"{summary['std_mean_nodes']:.2f}",
            "std_median_nodes": f"{summary['std_median_nodes']:.2f}",
            "ming_mean_nodes": f"{summary['ming_mean_nodes']:.2f}",
            "ming_median_nodes": f"{summary['ming_median_nodes']:.2f}",
            "std_wins": int(summary["std_wins"]),
            "ming_wins": int(summary["ming_wins"]),
            "ties": int(summary["ties"]),
            "both_success": int(summary["both_success"]),
            "std_only_success": int(summary["std_success_only"]),
            "ming_only_success": int(summary["ming_success_only"]),
            "both_fail": int(summary["both_fail"]),
            "mean_node_delta_std_minus_ming": f"{summary['mean_node_delta_std_minus_ming']:.2f}",
        }
        summary_rows.append(row)
        write_report(pair, summary, pair.report_path, root)

        print(
            f"{pair.std_path.parent.relative_to(root)}: "
            f"size={pair.size_tag}, "
            f"std mean={summary['std_mean_nodes']:.2f}, "
            f"ming mean={summary['ming_mean_nodes']:.2f}, "
            f"plot={pair.plot_path.name}, "
            f"txt={pair.report_path.name}"
        )

    summary_path = args.summary
    if not summary_path.is_absolute():
        summary_path = root / summary_path
    write_summary(summary_rows, summary_path)
    print(f"\nWrote summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
