"""
Unit tests for evaluation data schemas and taxonomy.
"""

import pytest
from evaluator.schema import (
    EvaluationDimension,
    DimensionScore,
    EvaluationInput,
    EvaluationResult,
)
from evaluator.taxonomy import ErrorType, Severity, ERROR_TAXONOMY


def test_evaluation_dimension_enum():
    assert EvaluationDimension.CORRECTNESS.value == "correctness"
    assert EvaluationDimension.SAFETY.value == "safety"
    assert len(EvaluationDimension) == 9


def test_error_taxonomy_mapping():
    assert ErrorType.FACTUAL_ERROR in ERROR_TAXONOMY
    detail = ERROR_TAXONOMY[ErrorType.UNSAFE_RESPONSE]
    assert detail.default_severity == Severity.CRITICAL


def test_dimension_score_serialization():
    ds = DimensionScore(
        dimension=EvaluationDimension.CORRECTNESS,
        score=0.95,
        severity=Severity.NONE,
        error_type=None,
        explanation="High accuracy"
    )
    d = ds.to_dict()
    assert d["dimension"] == "correctness"
    assert d["score"] == 0.95
    assert d["severity"] == "none"
    assert d["error_type"] is None


def test_evaluation_input_deserialization():
    raw = {
        "id": "test_1",
        "prompt": "Hello",
        "response": "World",
        "reference_answer": "World",
        "constraints": {"max_words": 10}
    }
    item = EvaluationInput.from_dict(raw)
    assert item.id == "test_1"
    assert item.prompt == "Hello"
    assert item.constraints["max_words"] == 10
