# Experiment set 02 — Stratified benchmark, prompts v2 (4 models)

| | |
| --- | --- |
| **Date** | July 2026 |
| **Models** | Qwen2.5-3B / 7B / 14B, Mistral-7B (local, bf16, one NVIDIA L40, chained SLURM jobs) |
| **Prompt version** | **v2** — placeholder-neutralised instructions (see [docs/PROMPTS.md](../../docs/PROMPTS.md)) |
| **Code commit** | `b56c52c` ("benchmark runs") |
| **Dataset** | 103 problems: 3 builtin + 5 tiers × 20 (same generation seed as set 01), **anonymised** |
| **Command** | `python3 main.py --backend local --model <m> --benchmark 20 --modes direct cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output results/bench_<m>` |

## Key results (gen@k / clean@k over 3 samples; symbolic baseline = 100%)

| Model | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| Qwen2.5-3B | 5% / 1% | 4% / 1% | 15% / 6% | 34% / 13% |
| Qwen2.5-7B | 45% / 31% | 32% / 13% | 46% / 13% | 35% / 4% |
| Mistral-7B | 37% / 14% | 40% / 26% | **58%** / 13% | 48% / 10% |
| Qwen2.5-14B | 39% / 17% | 63% / 32% | 53% / 22% | **68% / 42%** |

## Headline findings

1. **Executing the algorithm scales with model size.** At 3B/7B, handing the
   model the full ASP-ABAlearnB algorithm (`algorithm` mode) is mediocre; at
   **14B it becomes the best configuration overall** (68% gen@k, 42% clean@k).
   The set-01 conclusion ("the LLM cannot orchestrate the multi-step
   procedure") is a *capacity* limitation, not a fundamental one.
2. **Assumption Introduction (t2) emerges with scale** — guided-mode per tier
   (gen@k / clean@k):

   | Model | t1_mono | t2_defeas | t3_noise | t4_domain | t5_twopath |
   | --- | --- | --- | --- | --- | --- |
   | 3B | 35% / 30% | 10% / 0% | 5% / 0% | 5% / 0% | 10% / 0% |
   | 7B | 65% / 60% | 25% / **0%** | 35% / 0% | 45% / 5% | 60% / 0% |
   | Mistral-7B | 55% / 55% | 85% / **0%** | 25% / 5% | 85% / 0% | 40% / 0% |
   | 14B | 70% / 15% | 65% / **40%** | 50% / 35% | 60% / 20% | 60% / 20% |

   At ≤7B the defeasible tier never yields a fully clean solution (Mistral hits
   85% gen@k on t2 while violating training negatives — the overgeneralisation
   signature); at 14B clean solutions appear (40%).

## Caveats

- Not directly comparable with set 01 (different prompts — that is the point;
  see [docs/PROMPTS.md](../../docs/PROMPTS.md)). Also note `clean@k` here is
  per-problem (any of 3 samples); set 01's manifest reports a per-*sample*
  clean rate.
- Mistral-7B `algorithm` parse rate is 80% (format drift); all other cells ≥94%.
