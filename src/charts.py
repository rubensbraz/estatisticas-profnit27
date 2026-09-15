"""Chart visualization module for PROFNIT entrance exam statistical analysis.

This module generates publication-quality plots (PNG images) that are embedded into
the PDF report.
"""

import logging
from pathlib import Path
from typing import Dict, Union

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from src.analyzer import AnalysisResults

logger = logging.getLogger(__name__)

# Configure default visual style
plt.rcParams["font.sans-serif"] = "Helvetica, Arial, DejaVu Sans, sans-serif"
plt.rcParams["axes.edgecolor"] = "#E2E8F0"
plt.rcParams["axes.linewidth"] = 1.0


class ChartGenerator:
    """Generates analytical charts for PROFNIT exam report."""

    def __init__(self, output_dir: Union[str, Path]) -> None:
        """Initialize ChartGenerator with target directory for images.

        Args:
            output_dir: Directory path where generated chart PNGs will be saved.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_charts(self, results: AnalysisResults) -> Dict[str, Path]:
        """Generate all report charts and return dictionary of file paths.

        Args:
            results: AnalysisResults object containing DataFrame and metrics.

        Returns:
            Dictionary mapping chart identifiers to output Path objects.
        """
        logger.info("Generating chart suite in: %s", self.output_dir)
        chart_paths: Dict[str, Path] = {}

        chart_paths["score_distribution"] = self.plot_score_distribution(results)
        chart_paths["cumulative_distribution"] = self.plot_cumulative_distribution(results)
        chart_paths["regional_volume"] = self.plot_regional_volume(results)
        chart_paths["regional_means"] = self.plot_regional_means(results)

        return chart_paths

    def plot_score_distribution(self, results: AnalysisResults) -> Path:
        """Plot score frequency histogram with mean/median annotations.

        Args:
            results: AnalysisResults container.

        Returns:
            Path to saved PNG image.
        """
        output_path = self.output_dir / "score_distribution.png"
        present_df = results.df[results.df["is_present"]]

        fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)

        # Plot score distribution bar chart
        scores = range(0, 21)
        counts = [int((present_df["score"] == s).sum()) for s in scores]

        colors = ["#3B82F6" if s < 15 else "#1D4ED8" if s < 20 else "#1E3A8A" for s in scores]
        bars = ax.bar(scores, counts, color=colors, width=0.75, edgecolor="#1E293B", linewidth=0.5)

        # Value labels on top of bars
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() + 10,
                    str(count),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                    color="#1E293B",
                )

        # Mean and Median lines
        mean_val = results.descriptive.mean
        median_val = results.descriptive.median

        ax.axvline(
            mean_val,
            color="#EF4444",
            linestyle="--",
            linewidth=1.8,
            label=f"Média: {mean_val:.2f}",
        )
        ax.axvline(
            median_val,
            color="#10B981",
            linestyle=":",
            linewidth=2.0,
            label=f"Mediana: {median_val:.1f}",
        )

        ax.set_title(
            "Distribuição de Acertos dos Candidatos (de 0 a 20)",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color="#0F172A",
        )
        ax.set_xlabel("Número de Acertos (Nota)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_ylabel("Quantidade de Candidatos", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_xticks(scores)
        ax.set_ylim(0, max(counts) * 1.15)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=9)

        sns.despine()
        fig.tight_layout()
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        return output_path

    def plot_cumulative_distribution(self, results: AnalysisResults) -> Path:
        """Plot cumulative percentage of candidates reaching score thresholds.

        Args:
            results: AnalysisResults container.

        Returns:
            Path to saved PNG image.
        """
        output_path = self.output_dir / "cumulative_distribution.png"

        scores = [r.score for r in results.score_frequencies]
        cum_pcts = [r.cumulative_percentage for r in results.score_frequencies]

        fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)

        ax.plot(
            scores,
            cum_pcts,
            marker="o",
            color="#2563EB",
            linewidth=2.2,
            markersize=5,
            markerfacecolor="#1D4ED8",
            label="Percentual Acumulado (Topo -> Base)",
        )

        for s, pct in zip(scores, cum_pcts):
            if s in [20, 19, 18, 15, 10]:
                ax.annotate(
                    f"{pct:.1f}%",
                    (s, pct),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=8,
                    fontweight="bold",
                    color="#1E293B",
                )

        ax.set_title(
            "Porcentagem Acumulada de Candidatos por Nota Mínima",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color="#0F172A",
        )
        ax.set_xlabel("Nota Mínima (Corte)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_ylabel("Porcentagem Acumulada (%)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_xticks(range(0, 21))
        ax.set_ylim(0, 110)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=9)

        sns.despine()
        fig.tight_layout()
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        return output_path

    def plot_regional_volume(self, results: AnalysisResults) -> Path:
        """Plot total candidate volume per CPF Region/State.

        Args:
            results: AnalysisResults container.

        Returns:
            Path to saved PNG image.
        """
        output_path = self.output_dir / "regional_volume.png"

        regions = results.regional_breakdown
        short_codes = [r.short_code for r in regions]
        totals = [r.total_candidates for r in regions]
        perfects = [r.perfect_scores_count for r in regions]

        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)

        x = np.arange(len(short_codes))
        width = 0.38

        rects1 = ax.bar(x - width / 2, totals, width, label="Total de Inscritos", color="#3B82F6")
        rects2 = ax.bar(x + width / 2, perfects, width, label="Gabaritou (20/20)", color="#10B981")

        for rect in rects1:
            h = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                h + 4,
                str(h),
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
            )

        for rect in rects2:
            h = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                h + 4,
                str(h),
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
                color="#047857",
            )

        ax.set_title(
            "Volume de Candidatos e Notas Máximas por Região do CPF",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color="#0F172A",
        )
        ax.set_xlabel("Região do CPF (Estados)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_ylabel("Quantidade de Candidatos", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(short_codes, rotation=25, ha="right", fontsize=8.5)
        ax.set_ylim(0, max(totals) * 1.15)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=9)

        sns.despine()
        fig.tight_layout()
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        return output_path

    def plot_regional_means(self, results: AnalysisResults) -> Path:
        """Plot mean scores per CPF Region/State.

        Args:
            results: AnalysisResults container.

        Returns:
            Path to saved PNG image.
        """
        output_path = self.output_dir / "regional_means.png"

        regions = results.regional_breakdown
        short_codes = [r.short_code for r in regions]
        means = [r.mean_score for r in regions]

        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)

        bars = ax.bar(range(len(short_codes)), means, color="#6366F1", width=0.55, edgecolor="#3730A3")

        for bar, mean_val in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + 0.2,
                f"{mean_val:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color="#1E1B4B",
            )

        # Overall average reference line
        overall_mean = results.descriptive.mean
        ax.axhline(
            overall_mean,
            color="#EF4444",
            linestyle="--",
            linewidth=1.5,
            label=f"Média Nacional: {overall_mean:.2f}",
        )

        ax.set_title(
            "Média de Acertos por Região do CPF",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color="#0F172A",
        )
        ax.set_xlabel("Região do CPF (Estados)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_ylabel("Média de Acertos (de 0 a 20)", fontsize=10, fontweight="bold", labelpad=8)
        ax.set_xticks(range(len(short_codes)))
        ax.set_xticklabels(short_codes, rotation=25, ha="right", fontsize=8.5)

        ax.set_ylim(14, 21)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1", fontsize=9)

        sns.despine()
        fig.tight_layout()
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

        return output_path
