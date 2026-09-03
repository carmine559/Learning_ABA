# Experiment set 03 — Stratified benchmark, prompts v3 + metrics rev. 4

| | |
| --- | --- |
| **Models** | qwen2.5-3b, qwen2.5-7b, mistral-7b, qwen2.5-14b (local, one L40, chained jobs) |
| **Prompt version** | **v3** — terminologically exact against De Angelis et al. (ECAI 2024); see [docs/PROMPTS.md](../../docs/PROMPTS.md) |
| **Metrics** | **revision 4** — generated under rev. 3, re-scored offline to rev. 4 with `rescore.py`; see [docs/EXPERIMENTS.md](../../docs/EXPERIMENTS.md#metrics--precise-definitions) |
| **Dataset** | 103 problems: 3 builtin + 5 tiers × 20 (same generation seed as sets 01–02), anonymised |
| **Command** | `python3 main.py --backend local --model <m> --benchmark 20 --modes direct cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output results/bench_<m>` |
| **Re-scored with** | `python rescore.py results/bench_<m> --benchmark 20` |

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

3. **Metrics rev. 4** (applied afterwards, without re-running any model). The
   rev.-3 scoring turned out to reject the legal reuse of a background
   assumption, marking **71.8%** of this set's 4 944 samples
   `illformed_solution`, and the parser was discarding ~40% of the rules the
   models had written. Both are scoring defects, not model behaviour, so the
   set was re-scored from its stored `raw_output`. The rev.-3 numbers are void.

## Key results

`clean@k` — at least one of k=3 attempts is a legal, stable, fitting,
generalising, non-degenerate solution:

| Model | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| Qwen2.5-3B | 1.9% | 0.0% | 0.0% | 0.0% |
| Mistral-7B | 5.8% | 3.9% | 5.8% | 3.9% |
| Qwen2.5-7B | 40.8% | 17.5% | 10.7% | 11.7% |
| **Qwen2.5-14B** | **56.3%** [46.7, 65.5] | 30.1% | 7.8% | 21.4% |

Reference, same split and scoring: ASP-ABAlearnB given only the training
examples reaches **53.8%**; given every example it reaches 100%. Only the first
number is comparable with the table.

`det@k` (held-out labels forced in *every* train-consistent extension) equals
`gen@k` in every cell but one — Qwen2.5-14B `direct`, 56.3% vs 55.3%. These
synthetic tiers rarely admit free choice because their assumptions can only be
defeated by fixed background facts; the classical problems do admit it.

Per tier, Qwen2.5-14B:

| Mode | builtin | t1_mono | t2_defeas | t3_noise | t4_domain | t5_twopath |
| --- | --- | --- | --- | --- | --- | --- |
| direct | 67% | 55% | 70% | 80% | **5%** | 70% |
| cot | 33% | 55% | 55% | 20% | 15% | 5% |
| guided | 33% | 35% | 0% | 0% | 0% | 0% |
| algorithm | 0% | 60% | 30% | 15% | 5% | 0% |

## Caveats

- **`direct` beats every guided mode** for all four models, and `guided` — which
  hands over the RoLe ground facts — is the worst mode for both Qwen models.
  Worth an ablation before it is reported as a finding: being shown the ground
  facts may be anchoring the model into restating them.
- **`t4_domain` collapses** (5% at 14B in the best mode) while structurally
  identical tiers over 6 constants reach 55–80%. Domain size, not
  defeasibility, is the binding constraint here.
- `algorithm` mode produces the least intensional solutions (47% at 14B versus
  100% for `direct`) — handed the full algorithm, models fall back on ground
  facts.
- These runs used the **v3** prompt, which still serialised the problem as
  English prose while demanding a Prolog answer. v4 fixes that, so the next run
  is not comparable with this one.
