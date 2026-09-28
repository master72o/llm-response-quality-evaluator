"""
Integration test for CLI execution.
"""

import os
import pytest
from evaluator.cli import load_dataset
from evaluator.engines.hybrid import HybridEngine
from evaluator.metrics import MetricsCalculator
from evaluator.report_generator import ReportGenerator


def test_cli_load_dataset(tmp_path):
    jsonl_file = tmp_path / "test.jsonl"
    jsonl_file.write_text('{"prompt": "Hello", "response": "Hi"}\n', encoding="utf-8")

    items = load_dataset(str(jsonl_file))
    assert len(items) == 1
    assert items[0].prompt == "Hello"


def test_full_pipeline_execution(tmp_path):
    dataset_file = tmp_path / "sample.jsonl"
    dataset_file.write_text(
        '{"id": "s1", "prompt": "What is 10/2?", "response": "10/2 is 5", "reference_answer": "5"}\n',
        encoding="utf-8"
    )

    items = load_dataset(str(dataset_file))
    engine = HybridEngine()
    results = [engine.evaluate(item) for item in items]
    metrics = MetricsCalculator.calculate_aggregate_metrics(results)

    out_dir = tmp_path / "results"
    report_path = tmp_path / "report.md"

    ReportGenerator.export_results(results, str(out_dir))
    ReportGenerator.generate_markdown_report(metrics, str(report_path))

    assert os.path.exists(out_dir / "evaluation_results.json")
    assert os.path.exists(out_dir / "evaluation_results.csv")
    assert os.path.exists(report_path)
