# LLM Evaluation Dataset Governance & Documentation

## Dataset Metadata

- **Name**: LLM Response Quality Benchmark Dataset (`evaluation_dataset.jsonl`)
- **Version**: 1.0.0
- **Format**: JSON Lines (`.jsonl`)
- **Sample Count**: 25 evaluation instances
- **Domains Covered**: Code Generation, Mathematical Reasoning, Factual QA, Instruction Following, Safety Guardrails, Summarization, RAG QA.
- **License**: Creative Commons Attribution 4.0 International (CC-BY-4.0)

## Intended Use

This dataset is designed for benchmarking, scoring, and diagnosing LLM output quality across 9 core dimensions (`correctness`, `relevance`, `completeness`, `clarity`, `conciseness`, `instruction_following`, `factuality`, `safety`, `helpfulness`) and 9 distinct error taxonomy categories.

## Sampling & Data Construction Methodology

1. **Synthetic & Curated Cases**: High-fidelity, real-world prompts designed to test specific edge cases, format constraints, factual bounds, and safety guardrails.
2. **Gold Standard Reference Answers**: Verified expert reference responses provided for factual alignment and lexical similarity metrics.
3. **Deterministic Constraint Annotations**: Explicit structural metadata (e.g. `max_words`, `must_include`, `require_json`, `require_codeblock`).

## Privacy & Bias Considerations

- **PII scrubbing**: No real personal identifiable information (PII) is included. Synthetic PII patterns are included exclusively in negative test cases to verify safety guardrail detection.
- **Content Policy**: Unsafe inputs are strictly limited to benign synthetic testing patterns.
