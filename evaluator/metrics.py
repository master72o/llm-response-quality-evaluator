"""
Aggregate Evaluation Metrics & Statistical Analysis Module.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from evaluator.schema import EvaluationResult, EvaluationDimension
from evaluator.taxonomy import ErrorType, Severity


class MetricsCalculator:
    """Calculates dataset-level aggregate metrics and failure statistics."""

    @staticmethod
    def calculate_aggregate_metrics(results: List[EvaluationResult]) -> Dict[str, Any]:
        if not results:
            return {"total_evaluated": 0, "pass_rate": 0.0, "overall_mean_score": 0.0}

        total = len(results)
        passed_count = sum(1 for r in results if r.passed)
        scores = [r.overall_score for r in results]

        overall_mean = float(np.mean(scores))
        overall_std = float(np.std(scores))
        overall_median = float(np.median(scores))

        # Dimension breakdown
        dimension_data: Dict[str, List[float]] = {}
        for r in results:
            for ds in r.dimension_scores:
                dim_key = ds.dimension.value if isinstance(ds.dimension, EvaluationDimension) else str(ds.dimension)
                if dim_key not in dimension_data:
                    dimension_data[dim_key] = []
                dimension_data[dim_key].append(ds.score)

        dimension_metrics = {}
        for dim, dim_scores in dimension_data.items():
            dimension_metrics[dim] = {
                "mean_score": round(float(np.mean(dim_scores)), 4),
                "std_dev": round(float(np.std(dim_scores)), 4),
                "pass_rate": round(sum(1 for s in dim_scores if s >= 0.70) / len(dim_scores), 4),
                "min_score": round(float(np.min(dim_scores)), 4),
                "max_score": round(float(np.max(dim_scores)), 4),
            }

        # Error taxonomy breakdown
        error_counts: Dict[str, int] = {e.value: 0 for e in ErrorType}
        for r in results:
            if r.primary_error:
                err_key = r.primary_error.value if isinstance(r.primary_error, ErrorType) else str(r.primary_error)
                error_counts[err_key] = error_counts.get(err_key, 0) + 1

        error_distribution = {
            err: {
                "count": count,
                "percentage": round((count / total) * 100, 2)
            }
            for err, count in error_counts.items() if count > 0
        }

        # Severity breakdown
        severity_counts: Dict[str, int] = {s.value: 0 for s in Severity}
        for r in results:
            sev_key = r.max_severity.value if isinstance(r.max_severity, Severity) else str(r.max_severity)
            severity_counts[sev_key] = severity_counts.get(sev_key, 0) + 1

        severity_distribution = {
            sev: {
                "count": count,
                "percentage": round((count / total) * 100, 2)
            }
            for sev, count in severity_counts.items()
        }

        # Failure details
        failures = [
            {
                "id": r.id,
                "prompt": r.prompt,
                "response": r.response,
                "score": round(r.overall_score, 4),
                "primary_error": r.primary_error.value if r.primary_error else None,
                "max_severity": r.max_severity.value,
            }
            for r in results if not r.passed
        ]

        return {
            "total_evaluated": total,
            "passed_count": passed_count,
            "failed_count": total - passed_count,
            "pass_rate": round(passed_count / total, 4),
            "overall_mean_score": round(overall_mean, 4),
            "overall_std_dev": round(overall_std, 4),
            "overall_median_score": round(overall_median, 4),
            "dimension_metrics": dimension_metrics,
            "error_distribution": error_distribution,
            "severity_distribution": severity_distribution,
            "failures": failures,
        }
