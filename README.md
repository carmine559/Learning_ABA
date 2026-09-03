# Learning ABA — can an LLM replicate ABA Learning?

> **Research question.** Can a large language model *execute* the ASP-ABAlearnB
> algorithm — learning an Assumption-Based Argumentation framework from
> background knowledge and examples that **generalises to unseen cases**,
> rather than memorising the examples it was shown?

MSc thesis project, University of Bologna. The repository provides a symbolic
reference implementation of the published algorithm, a stratified anonymised
benchmark that isolates each of its capabilities, four prompting strategies of
increasing guidance, and a Clingo-verified evaluation.

**Three tasks.**

1. **Learn** *(the core question)* — LLM vs. ASP-ABAlearnB (De Angelis,
   Proietti & Toni, ECAI 2024), on problems **anonymised** so the model cannot
   fall back on world knowledge.
2. **Evaluate gradually** — BSAF gradual ABA semantics (Rapberger, Russo, Rago
   & Toni, KR 2025) against an argument-tree baseline, over the learned
   frameworks. See [docs/GRADED.md](docs/GRADED.md).
3. **Attribute strengths** *(planned, no code yet)* — ArgLLMs + RAG. See
   [argllm/README.md](argllm/README.md).

---

## Status

The current numbers below come from **prompts v3 + metrics rev. 4**, obtained by
re-scoring the four committed cluster runs offline with `rescore.py` — the raw
model answers are unchanged, only the scoring is corrected. Three corrections
matter enough to state up front:

- The previous well-formedness check rejected the **legal reuse of a background
  assumption** (Definition 4 / Algorithm 1 line 36), which alone marked 71.8% of
  all samples ill-formed. Fixed.
- The output parser silently discarded **~40% of the rules the models actually
  wrote** — rules filed under `NEW ASSUMPTIONS:`, and draft answer blocks
  preferred over the final one. Fixed, and every repair is now recorded per
  sample in `parse_repairs`.
- Generalisation was scored per example with independent brave queries, which is
  near-vacuous for a negative on a multi-extension framework. Replaced by a
  single-extension reading plus a strict determinacy check (see below).

Earlier result sets `00`–`02` in [`experiments/`](experiments/) were produced
with earlier prompts *and* earlier metrics; they are not comparable with the
table below. See [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) for the registry and
[docs/PROMPTS.md](docs/PROMPTS.md) for the prompt version history.

---

## Headline results

Four models, 103 anonymised problems (5 capability tiers × 20 + 3 built-ins),
4 prompting modes, k = 3 samples per problem. Cells are **clean@k** — the
fraction of problems where at least one of the 3 attempts produced a legal,
stable, fitting, generalising, non-degenerate solution.

| Model | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| Qwen2.5-3B | 1.9% | 0.0% | 0.0% | 0.0% |
| Mistral-7B | 5.8% | 3.9% | 5.8% | 3.9% |
| Qwen2.5-7B | 40.8% | 17.5% | 10.7% | 11.7% |
| **Qwen2.5-14B** | **56.3%** | 30.1% | 7.8% | 21.4% |

95% Wilson intervals are in each `summary.json`; the best cell is
56.3% [46.7, 65.5], so differences smaller than about ten points are not
resolved by n = 103.

**The reference, on the same footing.** ASP-ABAlearnB solves 100% of these
problems when it sees every example — but that is a different task from the one
the models face. Given only the training split and scored on the held-out
examples exactly like an LLM, the symbolic algorithm reaches **53.8%**. It is a
ceiling, not a perfect score, and the gap it leaves is mostly the same gap the
models face.

**Three findings.**

1. **More guidance does not help — it hurts.** `direct` is the best mode for
   every model, and `guided` — which hands over the Rote-Learning ground facts —
   is the worst for both Qwen models. Being shown the ground facts appears to
   anchor the model into restating them instead of generalising them.
2. **Domain size is the wall, not defeasibility.** Per tier for Qwen2.5-14B
   (`direct`): `t3_noise` 80%, `t2_defeas` 70%, `t5_twopath` 70%, `t1_mono` 55%,
   but `t4_domain` — the same structure over 12 constants instead of 6 — **5%**.
3. **Executing the published algorithm scales with size but stays hard.**
   `algorithm` mode goes 0% → 3.9% → 11.7% → 21.4% across 3B → 14B, and its
   solutions are the least intensional of any mode (47% at 14B, vs 100% for
   `direct`): models handed the full algorithm fall back on ground facts.

---

## What is ABA Learning?

An **ABA framework** ⟨R, A, ‾⟩ is a set of inference rules, a set of defeasible
assumptions, and a mapping from each assumption to its contrary. *Learning* one
means adding rules and assumptions so that the result is satisfiable and admits
**one stable extension Δ** in which every positive example is the claim of an
accepted argument and no negative example is. Both conditions refer to the *same*
Δ: a negative example may still be accepted in some other extension.

New rule heads must be either a **learnable** predicate from T or an entirely
new predicate. A solution is **intensional** when the new rules are non-ground
schemata — no `X = constant`, no bare ground facts.

```prolog
% Background — the Nixon Diamond
quaker(a). quaker(b). quaker(e).
republican(a). republican(b). republican(d). democrat(c).
pacifist(X) :- quaker(X), normal_quaker(X).
normal_quaker(X) defeated_by abnormal_quaker(X)

E+ = {pacifist(a), pacifist(c), pacifist(e)}      T = {pacifist, abnormal_quaker}
E- = {pacifist(b), pacifist(d)}

% A solution
pacifist(X)        :- democrat(X).
abnormal_quaker(X) :- republican(X), alpha(X).
c_alpha(X)         :- quaker(X), normal_quaker(X).
alpha(X) defeated_by c_alpha(X)
```

**ASP-ABAlearnB** solves this in two phases: **RoLe** finds a minimal set of
ground facts by ASP optimisation, then **Gen** generalises them with *Folding*
(R2), *Assumption Introduction* (R3) and *Fact Subsumption* (R4), re-checking
the solution condition after every step. Can an LLM run that loop?

### The four prompting modes

| Mode | What the model receives | What it tests |
| --- | --- | --- |
| `direct` | the problem only | raw zero-shot ability |
| `cot` | step-by-step instructions mirroring RoLe → Folding → AsmIntro → Subsumption | algorithm mimicry from a recipe |
| `guided` | the problem **plus the RoLe ground facts** (computed on the training split only) | the Gen phase in isolation |
| `algorithm` | the **full published algorithm** — both phases and R1–R4 — to execute | can it replicate the algorithm? |

All four are **anonymised by default**: every predicate and constant is renamed
to an abstract symbol (`pacifist(X) :- quaker(X), normal(X)` becomes
`v(X) :- p(X), w(X)`), so the model must reason from rule *structure* rather
than recognise `penguins don't fly`. Renaming is a bijection and both the
symbolic solver and Clingo are purely syntactic, so the anonymised problem is
isomorphic to the original — only the LLM's behaviour can change, which is
exactly the effect being measured. Use `--no-anonymize` to keep real names.

---

## How a sample is scored

Each stage must pass before the next; the first failure names the `error_type`.

| Stage | Check |
| --- | --- |
| 1. parse | the output yields a framework (an explicit `NONE/NONE` counts as an empty one, not a failure) |
| 2. well-formed | Definition-1 side conditions: (ii) new-rule heads, (iv) contraries of existing assumptions unchanged, flatness, assumption freshness |
| 3. stability | the candidate admits at least one stable extension |
| 4. fit | it is a solution of the **training** problem (one joint check) |
| 5. generalisation | it is a solution of the **full** problem, train + held-out (one joint check) |
| 6. non-degenerate | at least one new rule mentions no individual constant |

`X@1` is the mean over the k samples, `X@k` holds if **any** sample passes.
**`clean@k` is the headline metric**: stages 1–6 all pass at least once.

### Why there is a second generalisation metric

Brave ABA Learning is permissive by construction. A framework can contain
mutually attacking assumptions that leave an unseen atom **free** — accepted in
one stable extension, rejected in another — and brave entailment then scores a
coin flip as a success. This is not hypothetical: on the paper's own Nixon
Diamond, the reference solution leaves `pacifist(e)` free once `e` is held out.

So two numbers are reported side by side:

- **`gen@k`** — some extension consistent with the whole problem gets the
  held-out examples right. Faithful to Definition 1.
- **`det@k`** — **every** extension consistent with the *training* examples
  gets the held-out ones right. The framework actually predicts them.

`gen@k − det@k` is how much of the apparent generalisation is free choice rather
than learning. On the current synthetic tiers the gap is small (one problem for
Qwen2.5-14B), because their assumptions can only be defeated by fixed background
facts; the classical problems are where the pathology appears.

Full definitions: [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md).

---

## Installation

Python 3.10+ and Clingo 5.6+.

```bash
conda create -n aba_llm python=3.11 -y
conda activate aba_llm
conda install -c potassco clingo -y
pip install -r requirements.txt
```

For the local GPU backend, install a CUDA-matched torch first — see
[`cluster/setup_env.sh`](cluster/setup_env.sh).

Verify:

```python
from src.aba_dataset  import make_nixon_diamond
from src.aba_algorithm import solve_aba_learning
from src.aba_generalization import is_intensional_strict

problem, _ = make_nixon_diamond()
solution, trace = solve_aba_learning(problem)
print("solved:", trace.success, "intensional:", is_intensional_strict(solution))
for r in solution.new_rules:
    print("  ", r.to_prolog())
```

## Quick start

```bash
# no API key, no GPU — exercises the whole pipeline
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1

# the symbolic reference alone
python main.py --symbolic-only --benchmark 20

# the full benchmark for one model on a GPU (what the cluster jobs run)
python main.py --backend local --model qwen2.5-7b \
    --benchmark 20 --modes direct cot guided algorithm \
    --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b

# recompute every metric of a finished run — no LLM calls, no GPU
python rescore.py results/bench_qwen2.5-7b --benchmark 20
```

Every flag: [docs/CLI.md](docs/CLI.md). On the DISI SLURM cluster,
`bash cluster/submit_benchmarks.sh` chains one job per model —
[cluster/README.md](cluster/README.md).

---

## Repository map

| Path | Content |
| --- | --- |
| [`src/`](src/) | shared core + Task 1 — types, Clingo validation, symbolic solver, anonymisation, prompts, evaluation |
| [`gradual/`](gradual/) | Task 2 — BSAF gradual semantics, BAF baseline, random-ABAF generator |
| [`argllm/`](argllm/) | Task 3 — design spec only, no code yet |
| [`extras/`](extras/) | reporting — framework export, explanations, figures |
| [`cluster/`](cluster/) | SLURM scripts for the DISI GPU cluster |
| [`experiments/`](experiments/) | curated, committed result sets, one `MANIFEST.md` each |
| [`docs/`](docs/) | [CLI](docs/CLI.md) · [experiments](docs/EXPERIMENTS.md) · [prompts](docs/PROMPTS.md) · [graded semantics](docs/GRADED.md) |
| `main.py` | the single pipeline entry point |
| `rescore.py` | recompute metrics from stored raw answers |
| `results/` | scratch output directory (gitignored); finished runs are promoted into `experiments/` |

Inside `src/`:

```text
aba_types.py           Rule, ABAFramework, LearningProblem
aba_validator.py       Clingo — brave entailment, RoLe, witness extensions, determinacy
aba_dataset.py         built-in benchmarks + stratified synthetic generators
aba_model.py           backends: local (GPU), groq, hf_api, google_ai, mock
aba_algorithm.py       symbolic ASP-ABAlearnB: RoLe + Gen  (the reference)
aba_anonymize.py       symbol anonymisation (world-knowledge control)
aba_prompts.py         the four prompt modes + the output parser
aba_evaluation.py      k-sampling, scoring, aggregation
aba_generalization.py  train/test split, generalisation and determinacy metrics
```

---

## Troubleshooting

**Everything is `parse_error`** — the model is not producing the two sections at
all. Check `parse_repairs` in `results_<mode>.jsonl` first; if it is empty the
output has no recognisable structure. Try a larger model or a more guided mode.

**Everything is `illformed_solution`** — read the `wellformed_violations` field.
`condition (iv) violated` means the model redefined the contrary of an existing
background assumption, which is a real Definition-1 violation, not a formatting
slip.

**`gen@k` is much higher than `det@k`** — the framework leaves held-out atoms
free; it is a legal solution but it is not predicting anything. Not a bug, a
result.

**Rate limits (Groq / Gemini)** — `--min-interval 3` spaces requests. Per-day
caps cannot be waited out; switch model or backend.

**Clingo not found** — `conda install -c potassco clingo`, or
`pip install clingo --no-cache-dir`.

---

## References

De Angelis, E., Proietti, M., & Toni, F. (2024). *Learning Brave
Assumption-Based Argumentation Frameworks via ASP.* ECAI 2024, 3445–3452.

Rapberger, A., Russo, F., Rago, A., & Toni, F. (2025). *On Gradual Semantics for
Assumption-Based Argumentation.* KR 2025, 512–522.

Freedman, G., Rago, A., & Toni, F. (2025). *ArgLLM: Harnessing the Power of
Large Language Models for Argumentation.* AAAI 2025.

Rago, A., Toni, F., Aurisicchio, M., & Baroni, P. (2016). *Discontinuity-Free
Decision Support with Quantitative Argumentation Debates.* KR 2016.

Lehtonen, T., Rapberger, A., Toni, F., Ulbricht, M., & Wallner, J. P. (2024).
*Instantiations and Computational Aspects of Non-Flat Assumption-Based
Argumentation.* IJCAI 2024, 3457–3465.
