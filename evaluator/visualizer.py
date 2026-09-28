"""
Visualization Generator for LLM Response Evaluation Reports.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any


class Visualizer:
    """Generates evaluation visualization figures."""

    @staticmethod
    def generate_all_figures(metrics: Dict[str, Any], output_dir: str = "reports/figures") -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        generated = {}

        # 1. Dimension Scores Plot
        dim_path = os.path.join(output_dir, "dimension_scores.png")
        Visualizer._plot_dimension_scores(metrics.get("dimension_metrics", {}), dim_path)
        generated["dimension_scores"] = dim_path

        # 2. Error Taxonomy Frequency Plot
        err_path = os.path.join(output_dir, "error_taxonomy.png")
        Visualizer._plot_error_taxonomy(metrics.get("error_distribution", {}), err_path)
        generated["error_taxonomy"] = err_path

        # 3. Severity Distribution Plot
        sev_path = os.path.join(output_dir, "severity_distribution.png")
        Visualizer._plot_severity_distribution(metrics.get("severity_distribution", {}), sev_path)
        generated["severity_distribution"] = sev_path

        return generated

    @staticmethod
    def _plot_dimension_scores(dim_metrics: Dict[str, Any], output_path: str):
        if not dim_metrics:
            return

        dimensions = list(dim_metrics.keys())
        scores = [dim_metrics[d]["mean_score"] for d in dimensions]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(dimensions, scores, color="#2b5c8f", edgecolor="#1a365d", height=0.6)
        
        ax.set_xlim(0.0, 1.05)
        ax.set_xlabel("Mean Score (0.0 to 1.0)", fontsize=11, fontweight="bold")
        ax.set_title("LLM Response Quality: Mean Score by Dimension", fontsize=13, fontweight="bold", pad=15)
        ax.axvline(x=0.70, color="#d9534f", linestyle="--", linewidth=1.5, label="Quality Pass Threshold (0.70)")
        ax.legend(loc="lower right")
        ax.grid(axis="x", linestyle=":", alpha=0.6)

        # Annotate bar values
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f"{width:.2f}",
                    va="center", ha="left", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()

    @staticmethod
    def _plot_error_taxonomy(err_dist: Dict[str, Any], output_path: str):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        if not err_dist:
            ax.text(0.5, 0.5, "No Error Taxonomy Failures Detected", ha="center", va="center", fontsize=12)
        else:
            errors = list(err_dist.keys())
            counts = [err_dist[e]["count"] for e in errors]
            
            bars = ax.bar(errors, counts, color="#d9534f", edgecolor="#a94442", width=0.5)
            ax.set_ylabel("Failure Frequency Count", fontsize=11, fontweight="bold")
            ax.set_title("Error Taxonomy Frequency Breakdown", fontsize=13, fontweight="bold", pad=15)
            plt.xticks(rotation=30, ha="right")
            ax.grid(axis="y", linestyle=":", alpha=0.6)

            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, f"{int(height)}",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()

    @staticmethod
    def _plot_severity_distribution(sev_dist: Dict[str, Any], output_path: str):
        fig, ax = plt.subplots(figsize=(8, 5))
        
        severities = ["none", "low", "medium", "high", "critical"]
        color_map = {
            "none": "#5cb85c",
            "low": "#5bc0de",
            "medium": "#f0ad4e",
            "high": "#d9534f",
            "critical": "#d9534f"
        }
        
        counts = [sev_dist.get(s, {}).get("count", 0) for s in severities]
        colors = [color_map[s] for s in severities]

        bars = ax.bar(severities, counts, color=colors, edgecolor="#333333", width=0.5)
        ax.set_ylabel("Evaluation Example Count", fontsize=11, fontweight="bold")
        ax.set_title("Error Severity Distribution", fontsize=13, fontweight="bold", pad=15)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, f"{int(height)}",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
