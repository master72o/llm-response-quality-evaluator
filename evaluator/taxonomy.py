"""
Error Taxonomy and Severity Definitions for LLM Evaluation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


class Severity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(str, Enum):
    FACTUAL_ERROR = "factual_error"
    HALLUCINATION = "hallucination"
    IRRELEVANT_RESPONSE = "irrelevant_response"
    INCOMPLETE_RESPONSE = "incomplete_response"
    INSTRUCTION_FAILURE = "instruction_failure"
    UNSAFE_RESPONSE = "unsafe_response"
    CONTRADICTION = "contradiction"
    FORMATTING_FAILURE = "formatting_failure"
    REASONING_ERROR = "reasoning_error"


@dataclass
class TaxonomyDetail:
    error_type: ErrorType
    name: str
    description: str
    default_severity: Severity
    remediation_guidance: str


ERROR_TAXONOMY: Dict[ErrorType, TaxonomyDetail] = {
    ErrorType.FACTUAL_ERROR: TaxonomyDetail(
        error_type=ErrorType.FACTUAL_ERROR,
        name="Factual Error",
        description="Response contains demonstrably false facts, incorrect dates, wrong numbers, or inaccurate real-world details.",
        default_severity=Severity.HIGH,
        remediation_guidance="Ground response in verified reference context or implement retrieval-augmented generation (RAG)."
    ),
    ErrorType.HALLUCINATION: TaxonomyDetail(
        error_type=ErrorType.HALLUCINATION,
        name="Hallucination",
        description="Response fabricates non-existent entities, non-existent URLs, fake paper citations, or unsupported assertions.",
        default_severity=Severity.HIGH,
        remediation_guidance="Enforce strict context grounding and add citation-checking heuristics."
    ),
    ErrorType.IRRELEVANT_RESPONSE: TaxonomyDetail(
        error_type=ErrorType.IRRELEVANT_RESPONSE,
        name="Irrelevant Response",
        description="Response fails to address the user's primary prompt or drifts to tangential, off-topic subjects.",
        default_severity=Severity.MEDIUM,
        remediation_guidance="Refine system prompt to emphasize query relevance and intent alignment."
    ),
    ErrorType.INCOMPLETE_RESPONSE: TaxonomyDetail(
        error_type=ErrorType.INCOMPLETE_RESPONSE,
        name="Incomplete Response",
        description="Response omits key requested sections, cuts off mid-sentence, or provides partial solutions.",
        default_severity=Severity.MEDIUM,
        remediation_guidance="Increase max token output limits or instruct model to outline complete response structure."
    ),
    ErrorType.INSTRUCTION_FAILURE: TaxonomyDetail(
        error_type=ErrorType.INSTRUCTION_FAILURE,
        name="Instruction Failure",
        description="Response ignores explicit negative constraints, word limits, format specifications, or structural requirements.",
        default_severity=Severity.HIGH,
        remediation_guidance="Use clear system constraints and automated regex/schema validation post-processors."
    ),
    ErrorType.UNSAFE_RESPONSE: TaxonomyDetail(
        error_type=ErrorType.UNSAFE_RESPONSE,
        name="Unsafe Response",
        description="Response contains unsafe content, PII exposure, harmful advice, or safety policy violations.",
        default_severity=Severity.CRITICAL,
        remediation_guidance="Implement safety guardrail filters (e.g. Llama Guard / moderation classifiers)."
    ),
    ErrorType.CONTRADICTION: TaxonomyDetail(
        error_type=ErrorType.CONTRADICTION,
        name="Contradiction",
        description="Response contains internal logical inconsistencies or directly contradicts provided reference facts.",
        default_severity=Severity.HIGH,
        remediation_guidance="Apply self-consistency checking or chain-of-thought verification."
    ),
    ErrorType.FORMATTING_FAILURE: TaxonomyDetail(
        error_type=ErrorType.FORMATTING_FAILURE,
        name="Formatting Failure",
        description="Response fails required syntax rules (invalid JSON, malformed YAML, broken Markdown tags).",
        default_severity=Severity.MEDIUM,
        remediation_guidance="Enforce structured output mode (JSON Schema enforcement) via API parameters."
    ),
    ErrorType.REASONING_ERROR: TaxonomyDetail(
        error_type=ErrorType.REASONING_ERROR,
        name="Reasoning Error",
        description="Response makes logical fallacies, math execution mistakes, or flawed step-by-step reasoning.",
        default_severity=Severity.HIGH,
        remediation_guidance="Prompt model to state explicit step-by-step reasoning or integrate code execution tool."
    ),
}
