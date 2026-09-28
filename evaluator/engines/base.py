"""
Base Abstract Evaluation Engine Interface.
"""

from abc import ABC, abstractmethod
from evaluator.schema import EvaluationInput, EvaluationResult


class BaseEvaluationEngine(ABC):
    """Abstract Base Class for Evaluation Engines."""

    @abstractmethod
    def evaluate(self, input_item: EvaluationInput) -> EvaluationResult:
        """Evaluate an individual response against prompt and reference.

        Args:
            input_item: EvaluationInput containing prompt, response, reference, constraints.

        Returns:
            EvaluationResult containing dimension scores, overall score, and error diagnosis.
        """
        pass
