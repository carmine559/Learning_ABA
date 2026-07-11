# Experiment registry

Curated, immutable result sets live in [`experiments/`](../experiments/), one
folder per set, each with a `MANIFEST.md` (date, model, prompt version, exact
command, key metrics, caveats). The `results/` folder is a **gitignored working
directory**: `main.py` writes there; finished runs worth keeping are *promoted*
into `experiments/` together with a manifest.

| Set | Date | Models | Backend | Prompts | Dataset | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [`00_preliminary_api`](../experiments/00_preliminary_api/MANIFEST.md) | May–Jun 2026 | Llama-3.3-70B, Llama-3.1-8B | Groq API | v0 (evolving) | 3 builtin ± early synthetics | done (exploratory) |
| [`01_bench_prompts_v1`](../experiments/01_bench_prompts_v1/MANIFEST.md) | Jul 2026 | Qwen2.5-7B | local (L40) | v1 | 103 problems, 5 tiers, anonymised | done |
| [`02_bench_prompts_v2`](../experiments/02_bench_prompts_v2/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v2 | 103 problems, 5 tiers, anonymised | **running** |

## The benchmark at a glance

`--benchmark N` builds a stratified suite of `5·N` synthetic problems (plus the
3 builtin ones), each tier isolating one capability of the ASP-ABAlearnB
algorithm; everything is anonymised so the LLM cannot lean on world knowledge:

| Tier | Isolates |
| --- | --- |
| `t1_mono` | Folding only (monotonic rule suffices) |
| `t2_defeas` | Assumption introduction (one exception to defeat) |
| `t3_noise` | Distractor robustness (irrelevant predicates) |
| `t4_domain` | Domain-size scaling (12 constants) |
| `t5_twopath` | Two independent defeasible derivation paths |

Primary metrics: `gen@k` (any of k samples generalises to held-out examples)
and the stricter `clean@k` (fits **all** training examples AND generalises —
the criterion matching the ABA-Learning definition). `summary.json` contains
both, overall and per tier (`by_tier`).

## Reproducing

```bash
# quick local demo (no API key, no GPU)
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1

# full benchmark for one model on a GPU
python main.py --backend local --model qwen2.5-7b \
    --benchmark 20 --modes direct cot guided algorithm \
    --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b
```

On the DISI SLURM cluster see [`cluster/README.md`](../cluster/README.md)
(`bash cluster/submit_benchmarks.sh` chains one job per model).

Problem generation is seeded: the same `--benchmark N` reproduces byte-identical
problem sets, and `verify_invariance` (in `src/aba_anonymize.py`) guarantees
anonymisation preserves symbolic solvability.
