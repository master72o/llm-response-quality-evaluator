"""
Core Data Schemas for LLM Response Quality Evaluation.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from evaluator.taxonomy import ErrorType, Severity


class EvaluationDimension(str, Enum):
    CORRECTNESS = "correctness"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    CONCISENESS = "conciseness"
    INSTRUCTION_FOLLOWING = "instruction_following"
    FACTUALITY = "factuality"
    SAFETY = "safety"
    HELPFULNESS = "helpfulness"


@dataclass
class DimensionScore:
    dimension: EvaluationDimension
    score: float  # Normalized score between 0.0 and 1.0
    severity: Severity = Severity.NONE
    error_type: Optional[ErrorType] = None
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 4),
            "severity": self.severity.value,
            "error_type": self.error_type.value if self.error_type else None,
            "explanation": self.explanation,
        }


@dataclass
class EvaluationInput:
    id: str
    prompt: str
    response: str
    reference_answer: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationInput":
        return cls(
            id=str(data.get("id", "sample_0")),
            prompt=data["prompt"],
            response=data["response"],
            reference_answer=data.get("reference_answer"),
            metadata=data.get("metadata", {}),
            constraints=data.get("constraints", {}),
        )


@dataclass
class EvaluationResult:
    id: str
    prompt: str
    response: str
    reference_answer: Optional[str]
    dimension_scores: List[DimensionScore]
    overall_score: float
    primary_error: Optional[ErrorType]
    max_severity: Severity
    passed: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "response": self.response,
            "reference_answer": self.reference_answer,
            "overall_score": round(self.overall_score, 4),
            "passed": self.passed,
            "max_severity": self.max_severity.value,
            "primary_error": self.primary_error.value if self.primary_error else None,
            "dimension_scores": [ds.to_dict() for ds in self.dimension_scores],
            "metadata": self.metadata,
        }
