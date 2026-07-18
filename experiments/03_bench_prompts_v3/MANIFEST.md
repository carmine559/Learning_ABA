# Experiment set 03 — Stratified benchmark, prompts v3 + metrics rev. 3

| | |
| --- | --- |
| **Models** | qwen2.5-3b, qwen2.5-7b, mistral-7b, qwen2.5-14b (local, one L40, chained jobs) |
| **Prompt version** | **v3** — terminologically exact against De Angelis et al. (ECAI 2024); see [docs/PROMPTS.md](../../docs/PROMPTS.md) |
| **Metrics** | **revision 3** — joint Definition-1 generalisation check + well-formedness stage; see [docs/EXPERIMENTS.md](../../docs/EXPERIMENTS.md#metrics--precise-definitions) |
| **Dataset** | 103 problems: 3 builtin + 5 tiers × 20 (same generation seed as sets 01–02), anonymised |
| **Command** | `python3 main.py --backend local --model <m> --benchmark 20 --modes direct cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output results/bench_<m>` |

## Differences vs set 02

1. **Prompts v3**: Definition 1 stated exactly (single-extension condition),
   R2 Folding given syntactically (rho1/rho2/rho3 schema + Proposition-1
   caveat), R3 triggered by "no longer a solution" (including lost positives),
   R4 with the solution-preservation criterion, CoT step 3b labelled a
   heuristic.
2. **Metrics rev. 3**: `gen_valid` = joint Def-1 check on the full problem
   (one common extension for all examples); new `illformed_solution` stage
   rejecting candidates violating Def-1 (ii)/(iv)/flatness. Both make the
   metrics **stricter**, so scores are expected to be ≤ set 02's; the
   comparison quantifies how much the old metrics flattered the models.

## Key results

*(to be filled after the run)*
