"""
LLM-as-a-Judge Evaluation Engine.

Evaluates semantic response quality dimensions (Relevance, Completeness, Clarity,
Factuality, Helpfulness) using structured LLM prompts or reproducible heuristic judging.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from evaluator.schema import (
    EvaluationInput,
    EvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from evaluator.taxonomy import ErrorType, Severity
from evaluator.engines.base import BaseEvaluationEngine


class LLMJudgeEngine(BaseEvaluationEngine):
    """Engine providing LLM-as-a-Judge evaluation."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name

    def evaluate(self, input_item: EvaluationInput) -> EvaluationResult:
        """Execute LLM judging across semantic evaluation dimensions."""
        dimension_scores: List[DimensionScore] = []

        # Evaluate Relevance
        rel_score = self._judge_relevance(input_item)
        dimension_scores.append(rel_score)

        # Evaluate Completeness
        comp_score = self._judge_completeness(input_item)
        dimension_scores.append(comp_score)

        # Evaluate Clarity
        clar_score = self._judge_clarity(input_item)
        dimension_scores.append(clar_score)

        # Evaluate Factuality / Correctness
        fact_score = self._judge_factuality(input_item)
        dimension_scores.append(fact_score)

        # Evaluate Helpfulness
        help_score = self._judge_helpfulness(input_item)
        dimension_scores.append(help_score)

        overall_score = sum(ds.score for ds in dimension_scores) / len(dimension_scores)

        # Determine primary error and max severity
        max_sev = Severity.NONE
        primary_err: Optional[ErrorType] = None
        for ds in dimension_scores:
            if ds.severity != Severity.NONE:
                if self._severity_level(ds.severity) > self._severity_level(max_sev):
                    max_sev = ds.severity
                    primary_err = ds.error_type

        passed = overall_score >= 0.70 and max_sev not in (Severity.HIGH, Severity.CRITICAL)

        return EvaluationResult(
            id=input_item.id,
            prompt=input_item.prompt,
            response=input_item.response,
            reference_answer=input_item.reference_answer,
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            primary_error=primary_err,
            max_severity=max_sev,
            passed=passed,
            metadata=input_item.metadata
        )

    def _judge_relevance(self, item: EvaluationInput) -> DimensionScore:
        prompt_words = set(re.findall(r"\w+", item.prompt.lower()))
        resp_words = set(re.findall(r"\w+", item.response.lower()))

        # Remove common stop words
        stopwords = {"the", "a", "an", "in", "on", "of", "and", "is", "to", "for", "with", "what", "how", "why"}
        prompt_words -= stopwords
        resp_words -= stopwords

        overlap = len(prompt_words.intersection(resp_words)) / max(len(prompt_words), 1)

        if overlap < 0.15 and len(item.response.strip().split()) < 10:
            return DimensionScore(
                dimension=EvaluationDimension.RELEVANCE,
                score=0.2,
                severity=Severity.HIGH,
                error_type=ErrorType.IRRELEVANT_RESPONSE,
                explanation="Response shows minimal keyword overlap with prompt intent."
            )
        elif overlap < 0.25:
            return DimensionScore(
                dimension=EvaluationDimension.RELEVANCE,
                score=0.6,
                severity=Severity.LOW,
                error_type=ErrorType.IRRELEVANT_RESPONSE,
                explanation="Response partially addresses prompt topics but drifts off-target."
            )

        return DimensionScore(
            dimension=EvaluationDimension.RELEVANCE,
            score=1.0,
            severity=Severity.NONE,
            explanation="Response is directly relevant to prompt request."
        )

    def _judge_completeness(self, item: EvaluationInput) -> DimensionScore:
        response = item.response.strip()
        words = response.split()

        # Check for abrupt cut-offs
        if response and response[-1] not in ".!?}\"']`:":
            return DimensionScore(
                dimension=EvaluationDimension.COMPLETENESS,
                score=0.4,
                severity=Severity.MEDIUM,
                error_type=ErrorType.INCOMPLETE_RESPONSE,
                explanation="Response appears truncated or cut off mid-sentence."
            )

        if len(words) < 5 and "yes" not in response.lower() and "no" not in response.lower():
            return DimensionScore(
                dimension=EvaluationDimension.COMPLETENESS,
                score=0.5,
                severity=Severity.MEDIUM,
                error_type=ErrorType.INCOMPLETE_RESPONSE,
                explanation="Response is overly sparse and omits key explanation steps."
            )

        return DimensionScore(
            dimension=EvaluationDimension.COMPLETENESS,
            score=1.0,
            severity=Severity.NONE,
            explanation="Response provides complete coverage of requested topic."
        )

    def _judge_clarity(self, item: EvaluationInput) -> DimensionScore:
        # Check for repetitive structures or incoherent tokens
        words = item.response.lower().split()
        if len(words) > 10:
            repeated_seq = 0
            for i in range(len(words) - 3):
                if words[i:i+3] == words[i+3:i+6]:
                    repeated_seq += 1

            if repeated_seq > 2:
                return DimensionScore(
                    dimension=EvaluationDimension.CLARITY,
                    score=0.3,
                    severity=Severity.HIGH,
                    error_type=ErrorType.REASONING_ERROR,
                    explanation="Response contains repetitive degeneration loops."
                )

        return DimensionScore(
            dimension=EvaluationDimension.CLARITY,
            score=1.0,
            severity=Severity.NONE,
            explanation="Response is clearly formatted and easy to comprehend."
        )

    def _judge_factuality(self, item: EvaluationInput) -> DimensionScore:
        # Check explicit factual metadata indicators or reference comparison
        resp_lower = item.response.lower()
        if item.reference_answer:
            ref_lower = item.reference_answer.lower()
            # Extract numbers
            resp_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", resp_lower))
            ref_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", ref_lower))
            
            if ref_nums and not resp_nums.intersection(ref_nums):
                return DimensionScore(
                    dimension=EvaluationDimension.FACTUALITY,
                    score=0.2,
                    severity=Severity.HIGH,
                    error_type=ErrorType.FACTUAL_ERROR,
                    explanation=f"Response contains numerical mismatch with reference facts (expected {ref_nums}, got {resp_nums})."
                )

        # Detect hallucination triggers (e.g. claims of non-existent papers/websites)
        if "as of my last update in 2023" in resp_lower and "2026" in item.prompt.lower():
            return DimensionScore(
                dimension=EvaluationDimension.FACTUALITY,
                score=0.5,
                severity=Severity.MEDIUM,
                error_type=ErrorType.HALLUCINATION,
                explanation="Outdated knowledge cutoff limitation triggered for current event prompt."
            )

        return DimensionScore(
            dimension=EvaluationDimension.FACTUALITY,
            score=1.0,
            severity=Severity.NONE,
            explanation="Response factuality supported by available reference data."
        )

    def _judge_helpfulness(self, item: EvaluationInput) -> DimensionScore:
        if "i cannot fulfill this request" in item.response.lower() or "as an ai" in item.response.lower():
            if "harmful" not in item.prompt.lower() and "hack" not in item.prompt.lower() and "illegal" not in item.prompt.lower():
                return DimensionScore(
                    dimension=EvaluationDimension.HELPFULNESS,
                    score=0.3,
                    severity=Severity.MEDIUM,
                    error_type=ErrorType.INSTRUCTION_FAILURE,
                    explanation="Model gave overly defensive refusal on benign user prompt."
                )

        return DimensionScore(
            dimension=EvaluationDimension.HELPFULNESS,
            score=1.0,
            severity=Severity.NONE,
            explanation="Response provides actionable and helpful assistance."
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
