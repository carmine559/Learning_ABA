# Experiment set 01 — Stratified benchmark, prompts v1

| | |
| --- | --- |
| **Date** | July 2026 |
| **Model** | Qwen2.5-7B-Instruct (local, bf16, one NVIDIA L40) |
| **Backend** | `--backend local` (on-GPU via transformers) |
| **Prompt version** | **v1** — concrete schema names in the instructions (see [docs/PROMPTS.md](../../docs/PROMPTS.md)) |
| **Code commit** | `075c2a4` ("first important run") |
| **Dataset** | 103 problems: 3 builtin + 5 tiers × 20 (stratified suite), **anonymised** |
| **Command** | `python3 main.py --backend local --model qwen2.5-7b --benchmark 20 --modes direct cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b` |

## Key results (gen@k over 3 samples; symbolic baseline = 100%)

| Mode | gen@k | strict clean rate¹ | parse |
| --- | --- | --- | --- |
| guided | **61.2%** | **11.3%** | 100% |
| direct | 36.9% | 2.6% | 100% |
| algorithm | 30.1% | 1.6% | 98% |
| cot | 29.1% | 1.6% | 78% |

¹ fraction of samples with `error_type == "none"` (fits ALL training examples AND
generalises) — computed post-hoc from the JSONL; the `clean_at_k` metric was added
to the pipeline only after this run.

**Per-tier (guided):** t1_mono 80% gen@k (folding works, 69% intensional) ·
t2_defeas 25% (assumption introduction collapses) · t3_noise 80% gen@k but **0% fit**
(writes the overgeneral rule, omits the exception guard) · t4_domain 60% · t5_twopath 65%.

**Headline finding:** the model replicates the *monotonic* part of the algorithm
(folding) but systematically fails the *non-monotonic* core (assumption
introduction). Giving the full algorithm to execute (`algorithm`, 30%) is 2×
WORSE than giving only the RoLe intermediate output (`guided`, 61%).

## Caveats

- **Template-copying artefact:** 11.3% of guided samples copy predicate names
  from the prompt's illustrative schema (`target`, `exception_prop`, …) instead
  of the problem's anonymised symbols. This motivated the v1→v2 prompt change
  and makes this set **not directly comparable** with set 02.
- No `clean_at_k` in `summary.json` (metric added later); use the raw JSONL.
- Mock-era baseline numbers for the 3 builtin problems are noisy (n=3).
