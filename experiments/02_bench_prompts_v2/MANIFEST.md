# Experiment set 02 — Stratified benchmark, prompts v2 (4 models)

**STATUS: PENDING — final run in progress on the DISI cluster.**
This manifest will be completed when the results land.

| | |
| --- | --- |
| **Date** | July 2026 |
| **Models** | qwen2.5-3b, qwen2.5-7b, mistral-7b, qwen2.5-14b (local, one L40, chained jobs) |
| **Prompt version** | **v2** — placeholder-neutralised instructions (see [docs/PROMPTS.md](../../docs/PROMPTS.md)) |
| **Dataset** | 103 problems: 3 builtin + 5 tiers × 20 (identical generation seed as set 01), anonymised |
| **Command** | `python3 main.py --backend local --model <m> --benchmark 20 --modes direct cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output results/bench_<m>` |

## Differences vs set 01

1. **Prompts v2**: schema names → angle-bracket placeholders + PLACEHOLDER RULE
   (eliminates the template-copying confound measured at 11.3% in set 01);
   "do not echo the problem" rule.
2. **Strict metrics in-pipeline**: `clean_at_1` / `clean_at_k` now computed and
   reported per mode AND per tier (`summary.json` → `by_tier`).
3. **Model-size axis**: 3B / 7B / 14B (Qwen2.5) + Mistral-7B, to test whether the
   assumption-introduction failure (t2) is a scale problem or a fundamental one.

## Key results

*(to be filled from `summary.json` of each model after the run)*
