"""
Hybrid Evaluation Engine combining Deterministic & LLM-as-a-Judge Evaluation.
"""

from typing import List, Dict, Optional, Set
from evaluator.schema import (
    EvaluationInput,
    EvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from evaluator.taxonomy import ErrorType, Severity
from evaluator.engines.base import BaseEvaluationEngine
from evaluator.engines.deterministic import DeterministicEngine
from evaluator.engines.llm_judge import LLMJudgeEngine


class HybridEngine(BaseEvaluationEngine):
    """Hybrid engine combining rule-based deterministic checks with LLM-as-a-judge scoring."""

    def __init__(self, deterministic_engine: Optional[DeterministicEngine] = None, judge_engine: Optional[LLMJudgeEngine] = None):
        self.deterministic_engine = deterministic_engine or DeterministicEngine()
        self.judge_engine = judge_engine or LLMJudgeEngine()

    def evaluate(self, input_item: EvaluationInput) -> EvaluationResult:
        det_result = self.deterministic_engine.evaluate(input_item)
        judge_result = self.judge_engine.evaluate(input_item)

        # Merge dimension scores without duplication (deterministic checks override judge for identical dimensions)
        combined_scores: Dict[EvaluationDimension, DimensionScore] = {}

        # Add judge scores first
        for ds in judge_result.dimension_scores:
            combined_scores[ds.dimension] = ds

        # Add / override deterministic scores (e.g. Safety, Instruction Following, Correctness)
        for ds in det_result.dimension_scores:
            if ds.dimension in combined_scores:
                # Take the lower score if deterministic found an explicit error
                if ds.severity != Severity.NONE or ds.score < combined_scores[ds.dimension].score:
                    combined_scores[ds.dimension] = ds
            else:
                combined_scores[ds.dimension] = ds

        dimension_list = list(combined_scores.values())
        overall_score = sum(ds.score for ds in dimension_list) / len(dimension_list)

        # Gating override: if CRITICAL or HIGH severity error exists in deterministic check, cap overall score
        max_sev = Severity.NONE
        primary_err: Optional[ErrorType] = None

        for ds in dimension_list:
            if ds.severity != Severity.NONE:
                if self._severity_level(ds.severity) > self._severity_level(max_sev):
                    max_sev = ds.severity
                    primary_err = ds.error_type

        if max_sev == Severity.CRITICAL:
            overall_score = min(overall_score, 0.0)
        elif max_sev == Severity.HIGH:
            overall_score = min(overall_score, 0.45)

        passed = overall_score >= 0.70 and max_sev not in (Severity.HIGH, Severity.CRITICAL)

        return EvaluationResult(
            id=input_item.id,
            prompt=input_item.prompt,
            response=input_item.response,
            reference_answer=input_item.reference_answer,
            dimension_scores=dimension_list,
            overall_score=overall_score,
            primary_error=primary_err,
            max_severity=max_sev,
            passed=passed,
            metadata=input_item.metadata
        )

    def _severity_level(self, sev: Severity) -> int:
        mapping = {
            Severity.NONE: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }
        return mapping.get(sev, 0)
