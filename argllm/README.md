# Task 3 — ArgLLMs with Retrieval (RAG)

**Status: not yet implemented (placeholder).** This directory will hold the third
task: an [ArgLLMs](https://arxiv.org/abs/2405.02079)-style pipeline (Freedman et
al., AAAI 2025) that attributes *intrinsic strengths* to the assumptions of a
learned ABA framework, grounded in retrieved evidence rather than the model's
parametric memory.

## Where it sits in the project pipeline

```
TASK 1 (Learn)              TASK 3 (Attribute)          TASK 2 (Evaluate)
BK + E± + ALGORITHM   ──►   intrinsic strengths τ  ──►   σ ∈ [0,1] graded
  (anonymised)              for the assumptions           acceptability
  → learned ABA fw          (LLM + RAG, grounded)         (BSAF semantics)
```

Task 3 consumes a learned ABA framework (Task 1) and produces the base scores
`τ` that Task 2's gradual semantics (`gradual/aba_bsaf.py`) propagates into
strengths `σ`.

## Relationship to anonymisation (Task 1)

Anonymisation (Task 1) and RAG (Task 3) are *opposite controls on the same
problem* — LLM knowledge leakage:

- **Task 1** removes world knowledge (anonymised predicates) to test whether the
  LLM can execute the ABA-learning **algorithm** from structure alone.
- **Task 3** deliberately reintroduces world knowledge, but **channels it through
  retrieval** so each base score is grounded in citable, contestable evidence
  instead of hallucinated confidence.

Consequently Task 3 runs on the **original (named)** frameworks, since retrieval
needs semantic predicate names.

## Planned components (mirroring the ArgLLMs pipeline)

- `retriever.py` — IR/RAG over an evidence corpus (start simple: keyword/BM25).
- `arg_generation.py` — Γ: retrieval-grounded generation of arguments /
  exceptions / contraries for assumptions.
- `strength_attribution.py` — E: LLM attributes base scores `τ` with retrieved
  evidence in context (an upgrade of `gradual/aba_graded.assumption_scores_from_llm`).
- `pipeline.py` — Γ → E → Σ, where Σ is Task 2's BSAF gradual semantics.

Contestability (ArgLLMs Properties 1–2) is already partly available via
`gradual/aba_graded.contest_base_score`.
