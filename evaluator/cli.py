"""
Command-Line Interface for LLM Response Quality Evaluator.
"""

import sys
import os
import json
import argparse
from typing import List
from evaluator.schema import EvaluationInput, EvaluationResult
from evaluator.engines.hybrid import HybridEngine
from evaluator.metrics import MetricsCalculator
from evaluator.report_generator import ReportGenerator
from evaluator.visualizer import Visualizer


def load_dataset(file_path: str) -> List[EvaluationInput]:
    """Load JSON or JSONL evaluation dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    items: List[EvaluationInput] = []
    with open(file_path, "r", encoding="utf-8") as f:
        if file_path.endswith(".jsonl"):
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                if "id" not in data:
                    data["id"] = f"sample_{idx+1}"
                items.append(EvaluationInput.from_dict(data))
        else:
            data_list = json.load(f)
            for idx, item_data in enumerate(data_list):
                if "id" not in item_data:
                    item_data["id"] = f"sample_{idx+1}"
                items.append(EvaluationInput.from_dict(item_data))
    return items


def main():
    parser = argparse.ArgumentParser(
        description="LLM Response Quality Evaluator CLI tool."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    eval_parser = subparsers.add_parser("evaluate", help="Evaluate LLM dataset")
    eval_parser.add_argument("--input", "-i", required=True, help="Path to input dataset (.json or .jsonl)")
    eval_parser.add_argument("--output-dir", "-o", default="results", help="Directory to save output JSON/CSV")
    eval_parser.add_argument("--report", "-r", default="reports/summary_report.md", help="Path to save markdown report")
    eval_parser.add_argument("--figures-dir", "-f", default="reports/figures", help="Directory to save figures")

    args = parser.parse_args()

    if args.command == "evaluate":
        print(f"Loading dataset from: {args.input}")
        items = load_dataset(args.input)
        print(f"Loaded {len(items)} evaluation samples.")

        print("Initializing Hybrid Evaluation Engine...")
        engine = HybridEngine()

        print("Running quality evaluation...")
        results: List[EvaluationResult] = []
        for idx, item in enumerate(items, 1):
            res = engine.evaluate(item)
            results.append(res)
            print(f" [{idx}/{len(items)}] ID: {item.id} | Score: {res.overall_score:.2f} | Passed: {res.passed} | Max Sev: {res.max_severity.value}")

        print("\nCalculating aggregate metrics...")
        metrics = MetricsCalculator.calculate_aggregate_metrics(results)
        print(f" Overall Pass Rate: {metrics['pass_rate']*100:.1f}%")
        print(f" Overall Mean Score: {metrics['overall_mean_score']:.4f}")

        print("\nExporting JSON and CSV results...")
        ReportGenerator.export_results(results, args.output_dir)

        print("\nGenerating visual report figures...")
        Visualizer.generate_all_figures(metrics, args.figures_dir)

        print(f"\nGenerating Markdown summary report at: {args.report}")
        ReportGenerator.generate_markdown_report(metrics, args.report)

        print("\nQuality Evaluation Completed Successfully!")


if __name__ == "__main__":
    main()
