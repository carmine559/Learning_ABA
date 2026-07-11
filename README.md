# Learning ABA — Can LLMs Replicate Assumption-Based Argumentation Learning?

> **Research question:** Can a large language model *execute* the
> ASP-ABAlearnB algorithm — learning an Assumption-Based Argumentation (ABA)
> framework from background knowledge and examples that **generalises to unseen
> cases**, rather than memorising the training set?

MSc thesis project (University of Bologna). The pipeline provides a provably
correct symbolic baseline, a **stratified anonymised benchmark** that isolates
each capability of the algorithm, four prompting strategies of increasing
guidance, and two extension tasks (gradual ABA semantics, ArgLLMs + RAG).

**The three tasks:**

1. **Task 1 — Learn** *(the core question)*: LLM vs the ASP-ABAlearnB algorithm
   (De Angelis, Proietti & Toni, ECAI 2024), on problems **anonymised** so the
   model cannot lean on world knowledge.
2. **Task 2 — Gradual semantics**: correct BSAF gradual ABA semantics
   (Rapberger, Russo, Rago & Toni, KR 2025) vs the argument-tree baseline, over
   the learned frameworks. See [`gradual/`](gradual/).
3. **Task 3 — ArgLLMs + RAG** *(planned)*: retrieval-grounded intrinsic-strength
   attribution (Freedman et al., AAAI 2025). See [`argllm/README.md`](argllm/README.md).

## Headline result (so far)

Qwen2.5-7B on 103 anonymised problems (5 capability tiers × 20 + 3 builtin),
3 samples/problem, symbolic baseline solves 100%
([full set + manifest](experiments/01_bench_prompts_v1/MANIFEST.md)):

| Mode (increasing guidance) | gen@k | strict clean rate |
| --- | --- | --- |
| `guided` (RoLe output given, generalise it) | **61%** | **11%** |
| `direct` (problem only) | 37% | 3% |
| `algorithm` (full published algorithm to execute) | 30% | 2% |
| `cot` (step-by-step recipe) | 29% | 2% |

Per tier, the boundary is sharp: the model **replicates Folding** (t1: 80%
gen@k, 69% intensional) but **systematically fails Assumption Introduction**
(t2: 25%) — it handles the monotonic part of the algorithm and breaks exactly
at the non-monotonic core. A 4-model run under improved prompts is in progress
([set 02](experiments/02_bench_prompts_v2/MANIFEST.md)).

## Repository map

| Path | Content |
| --- | --- |
| [`src/`](src/) | shared core + Task 1 (types, Clingo validation, symbolic solver, anonymisation, prompts, evaluation) |
| [`gradual/`](gradual/) | Task 2 — BSAF gradual semantics, BAF baseline, random-ABAF generator |
| [`argllm/`](argllm/) | Task 3 — design spec (planned) |
| [`extras/`](extras/) | reporting: framework export, explanations, figures |
| [`cluster/`](cluster/) | SLURM scripts for the DISI GPU cluster ([guide](cluster/README.md)) |
| [`experiments/`](experiments/) | **curated, committed result sets** — one folder + `MANIFEST.md` per run ([registry](docs/EXPERIMENTS.md)) |
| [`docs/`](docs/) | [experiment registry](docs/EXPERIMENTS.md) · [prompt design & version history](docs/PROMPTS.md) |
| `results/` | gitignored working directory (`main.py` output; promoted runs move to `experiments/`) |

---

## What is ABA Learning?

An **ABA framework** `<R, A, ->` consists of inference rules, defeasible
assumptions, and a contrary mapping. *Learning* an ABA framework means finding
new rules and assumptions such that:

1. Every positive example `e ∈ E+` is **bravely entailed** (derivable in at least one stable extension).
2. No negative example `e ∈ E-` is entailed.
3. New rule heads use only the specified **learnable predicates**.

**Classic example — Nixon Diamond:**

```prolog
% Background
quaker(a). quaker(b). quaker(e).
republican(a). republican(b). republican(d). democrat(c).
pacifist(X) :- quaker(X), normal_quaker(X).
% normal_quaker(X) defeated by abnormal_quaker(X)

E+ = {pacifist(a), pacifist(c), pacifist(e)}
E- = {pacifist(b), pacifist(d)}

% Ground-truth solution
pacifist(X)        :- democrat(X).
abnormal_quaker(X) :- republican(X), alpha(X).
c_alpha(X)         :- quaker(X), normal_quaker(X).
% new assumption: alpha(X) defeated_by c_alpha(X)
```

The symbolic **ASP-ABAlearnB** algorithm (De Angelis, Proietti & Toni, ECAI 2024)
solves this in two phases:

- **RoLe** — finds the minimal set of ground facts via ASP optimisation.
- **Gen** — generalises those facts through *Folding*, *Assumption Introduction*,
  and *Fact Subsumption*, producing intensional (variable-based) rules.

Can an LLM replicate the Gen phase reasoning from a prompt?

---

## Evaluation Methodology

### Why raw validity is not enough

A framework that simply asserts each positive example as a ground fact:

```prolog
flies(X) :- X = tweety.
```

passes a basic validity check while **learning nothing**. To measure genuine
learning, every problem is split at the **example level**:

```text
E+ = {pacifist(a), pacifist(c), pacifist(e)}
      LLM sees: pacifist(a), pacifist(e)   |   Held out: pacifist(c)
```

The LLM learns from **TRAIN** examples only, then the framework is tested on
held-out **TEST** examples it never saw. The gap between training fit and
held-out generalisation (`overfit_gap`) directly measures memorisation.

Each problem is attempted **k times** (default: 5) to account for LLM
stochasticity. The headline metric is **`gen@k`** — success if any of the k
attempts generalises.

---

## Installation

Requires Python 3.10+ and Clingo 5.6+.

```powershell
# Recommended: install Clingo via conda for reliability
conda create -n aba_llm python=3.11 -y
conda activate aba_llm
conda install -c potassco clingo -y

# Core + optional backends (see requirements.txt for the grouped list)
pip install -r requirements.txt
```

For the **local GPU backend** (`--backend local`, used on the cluster) install a
CUDA-matched torch first — see [`cluster/setup_env.sh`](cluster/setup_env.sh).

**Verify:**

```python
import clingo; print("Clingo:", clingo.__version__)
from src.aba_dataset import make_nixon_diamond
from src.aba_algorithm import solve_aba_learning
p, _ = make_nixon_diamond()
sol, _ = solve_aba_learning(p)
print("Symbolic solver OK — intensional:", sol.is_intensional())
```

---

## Quick Start

**No API key (mock backend):**

```powershell
python main.py --backend mock --modes direct cot guided --n-samples 3 --output results\
```

**Groq (free, recommended):**

```powershell
$env:GROQ_API_KEY = "gsk_your_key_here"

python main.py `
  --backend groq --model llama3-70b `
  --modes direct cot guided algorithm `
  --n-samples 5 `
  --output results\my_run
```

**HuggingFace Inference API (free):**

```powershell
$env:HF_TOKEN = "hf_your_token_here"
python main.py --backend hf_api --model qwen2.5-7b --modes guided --n-samples 5
```

**Symbolic baseline only:**

```powershell
python main.py --symbolic-only --output results\
```

---

## Prompting Modes

Modes are ordered by **increasing guidance**, from raw zero-shot to handing the
LLM the published algorithm to execute:

| Mode | What the LLM receives | Tests |
| --- | --- | --- |
| `direct` | The problem only | Raw zero-shot capability |
| `cot` | Step-by-step instructions mirroring RoLe → Folding → AsmIntro → Subsumption | Algorithm mimicry |
| `guided` | The problem **plus the RoLe ground facts** (computed on TRAIN only) | Generalisation in isolation |
| `algorithm` | The **full ASP-ABAlearnB algorithm** — RoLe + Gen and the four transformation rules R1–R4 (De Angelis et al. 2024) — to **execute** | Can the LLM *replicate the algorithm*? |

`algorithm` is the central test of **Task 1**: the model is given the actual
published algorithm (not a paraphrase) and asked to run it. `guided` isolates the
hard part — replacing `X = const` with intensional rules and introducing
assumptions for exceptions — by handing over the RoLe output. All four modes run
by default.

These Task-1 runs are **anonymised by default** (see below), so the LLM must
reason from rule *structure* rather than from world knowledge about the predicates.

---

## Anonymised Problems (controlling for world knowledge)

An LLM carries vast world knowledge. When a problem mentions `flies`, `penguin`,
or `quaker`, the model can **hallucinate** facts it "knows" (penguins don't fly)
that were never stated in the ABA framework, or **leak external knowledge** that
infects the derivation instead of reasoning purely from the supplied rules. Both
contaminate the experiment: you can no longer tell whether the LLM *reasoned* or
merely *recognised*.

Anonymisation removes the semantic anchors. Every predicate and constant is
consistently renamed to an abstract symbol, so the model has nothing to fall back
on but the **structure** of the rules:

```text
ORIGINAL                                ANONYMISED  (default)
pacifist(X) :- quaker(X), normal(X).    v(X) :- p(X), w(X).
quaker(tweety).  republican(tweety).    p(a).  r(a).
E+ = pacifist(tweety)                    E+ = v(a)
```

**This is ON by default** (it is core to Task 1). Use `--no-anonymize` to keep the
original names — e.g. for human inspection, or for Task 3 / RAG, where retrieval
needs real predicate names.

```powershell
python main.py --backend google_ai --modes algorithm guided   # anonymised (default)
python main.py --anonymize-scheme indexed                      # p0,p1 / c0,c1
python main.py --no-anonymize --graded                         # keep real names
```

**Why it is sound.** Renaming is a bijection on symbols, and both ASP-ABAlearnB
and Clingo are purely syntactic — so the anonymised problem is *isomorphic* to the
original. The symbolic solver succeeds on exactly the same problems and the graded
strengths are identical (e.g. `pacifist(a)=0.333` becomes `v(a)=0.333`). **Only the
LLM's behaviour can change** — which is precisely the effect being measured. The
module's `verify_invariance()` asserts this.

The per-problem renaming is written to `name_maps.json`, and
`aba_anonymize.deanonymize_framework(fw, name_map)` translates a learned framework
back to the original vocabulary for human-readable reporting.

> Note: anonymisation composes with every prompting mode; the LLM never sees a
> real predicate name. Use `--no-anonymize` only when you deliberately want the
> model to use world knowledge (Task 3 / RAG) or for human-readable inspection.

---

## LLM Backends

| Backend | Key env var | Default model | Install |
| --- | --- | --- | --- |
| `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | `pip install groq` |
| `hf_api` | `HF_TOKEN` | `Qwen/Qwen2.5-7B-Instruct` | `pip install huggingface_hub` |
| `google_ai` | `GOOGLE_API_KEY` | `gemini-2.5-flash` | `pip install google-genai` |
| `mock` | — | hard-coded responses | — |

### Google AI Studio setup

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create a key.
2. Set the environment variable:

```powershell
$env:GOOGLE_API_KEY = "AIza..."
```

3. Run:

```powershell
python main.py --backend google_ai --modes cot guided --n-samples 5
```

### Which Gemini model to use

| Alias | Model ID | Free quota | Best for |
| --- | --- | --- | --- |
| `gemini-2.5-flash` (default) | `gemini-2.5-flash` | 500 req/day, 10 RPM | **Recommended** — best reasoning/speed balance |
| `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` | 1500 req/day, 15 RPM | High-volume runs, many synthetic problems |
| `gemini-3.0-flash` | `gemini-3.0-flash` | 50 req/day, 5 RPM | Maximum reasoning quality, small runs only |

**Recommendation for this task:** `gemini-3.1-flash-lite`.
The ABA learning problem (folding + assumption introduction) is exactly the kind of
multi-step logical reasoning where Gemini 2.5's built-in chain-of-thought helps most.
The thinking budget is 8 192 tokens and does not count against `--max-tokens`.

```powershell
# Standard run
python main.py --backend google_ai --model gemini-2.5-flash --modes guided cot --n-samples 5

# With thinking mode (better accuracy, higher latency)
python main.py --backend google_ai --model gemini-2.5-flash --thinking --modes cot guided

# High-volume with the more permissive model
python main.py --backend google_ai --model gemini-3.1-flash --n-synthetic 50 --n-samples 5

# Slow down requests to stay under 10 RPM
python main.py --backend google_ai --min-interval 7 --modes guided --n-samples 5
```

### Groq model aliases

`llama3-70b`, `llama3-8b`, `gemma2-9b`, `qwen`.

### HuggingFace model aliases

`qwen2.5-7b`, `llama3-8b`, `mistral-7b`, `phi3-mini`, `gemma2-9b`.

---

## Key Metrics

| Metric | Meaning |
| --- | --- |
| `gen@k` | Any of k samples generalises to held-out examples — **headline metric** |
| `gen@1` | Mean generalisation rate across samples |
| `fit@1` | Mean training-fit rate |
| `overfit_gap` | fit − gen_score — memorisation indicator |
| `intensional_rate` | Fraction of fit solutions with no constants in new rules |
| `degenerate_rate` | Fraction of fit solutions that only memorised ground facts |
| `parse_rate` | Fraction of samples the parser could read |

**Error types per sample:** `none` (correct), `parse_error`, `stability_error`,
`completeness_error`, `soundness_error`, `generalization_error`, `degenerate`.

---

## Architecture

The project is organised around **three sequential tasks** that compose into one
pipeline:

```text
TASK 1 (Learn)              TASK 3 (Attribute)          TASK 2 (Evaluate)
BK + E± + ALGORITHM   ──►   intrinsic strengths τ  ──►   σ ∈ [0,1] graded
  (anonymised)              for the assumptions           acceptability
  → learned ABA fw          (LLM + RAG, grounded)         (BSAF semantics)
```

```text
src/                        SHARED CORE + TASK 1 (can an LLM replicate ABA Learning?)
  aba_types.py              Rule, ABAFramework, LearningProblem            [core]
  aba_validator.py          Clingo API — brave entailment, RoLe phase      [core]
  aba_dataset.py            Benchmarks + synthetic generators              [core]
  aba_model.py              Backends: groq, hf_api, google_ai, mock        [core]
  aba_algorithm.py          Symbolic ASP-ABAlearnB: RoLe + Gen (reference) [task 1]
  aba_anonymize.py          Symbol anonymisation (world-knowledge control) [task 1]
  aba_prompts.py            Prompt modes + markdown-robust output parser   [task 1]
  aba_evaluation.py         k-sampling, fit/gen metrics                    [task 1]
  aba_generalization.py     Train/test split, gen scoring, degeneracy      [task 1]

gradual/                    TASK 2 — gradual ABA semantics (Rapberger et al. 2025)
  aba_bsaf.py               CORRECT BSAF gradual semantics (fixpoint)
  aba_graded.py             BAF baseline — argument-tree DF-QuAD
  aba_generate.py           Random ABAF generator + convergence experiment

argllm/                     TASK 3 — ArgLLMs + RAG (Freedman et al. 2025) — PLANNED
  (see argllm/README.md)

extras/                     Reporting utilities (Task 1 output)
  aba_export.py             Dump frameworks to JSONL / Markdown / CSV
  aba_explain.py            Mechanism tags + per-sample narratives
  aba_visualization.py      Publication figures (PDF)

main.py                     Single-pipeline CLI orchestration
```

See [Graded Semantics](#graded-semantics) for Task 2 and `argllm/README.md`
for the Task 3 design.

---

## Graded Semantics

The graded layer adds a **continuous reasoning layer** on top of any learned ABA
framework. Where Clingo returns a binary verdict (bravely entailed or not), it
computes a **strength score σ ∈ [0, 1]**. Two semantics are provided, mirroring
the comparison in Rapberger, Russo, Rago & Toni, *On Gradual Semantics for
Assumption-Based Argumentation* (KR 2025):

| Module | Semantics | Nodes | Role |
| --- | --- | --- | --- |
| `aba_bsaf.py` | **BSAF gradual ABA** (the paper's contribution) | assumptions | **headline / correct** |
| `aba_graded.py` | **BAF baseline** (argument-tree DF-QuAD) | arguments | comparison baseline |

**Why two?** The paper shows the *assumption-based* BSAF semantics is more
principled and converges more reliably than the *argument-based* BAF instantiation.
`aba_bsaf.py` implements the BSAF semantics as an **iterative strength-evolution
fixpoint** (Definition 4.17), which resolves cyclic attack structures (e.g.
`normal_quaker ↔ alpha` in Nixon Diamond) exactly — giving `pacifist(a) = 1/3`.
The older `aba_graded.py` builds a per-query argument tree with a depth cap; it is
the paper's baseline and only approximates even that (it reports `0.375` for the
same query). `--graded` runs **both side by side** so the difference is visible.

### Design principle

The two readings coexist without contradiction:

```text
Learned ABA framework  ──────────────────────────────────────────────
        │                                                             │
        ▼  (structure is fixed and symbolic)                         ▼
  aba_validator.py                                          aba_bsaf.py / aba_graded.py
  Clingo brave entailment                                   gradual semantics
  binary: True / False                                      continuous: σ ∈ [0, 1]
```

The LLM's uncertainty enters **only** through the base scores of the ABA
assumptions. The argument structure (rules, attacks, support) is always taken
from the symbolic framework unchanged.

### The BSAF semantics (correct, headline)

`aba_bsaf.py` follows the paper's 5-step pipeline (Figure 1):

1. **Abstraction** — build the BSAF `F_D = (A, R_D, S_D)`: nodes are the ground
   assumptions; `R_D = {(E,a) : E ⊢ contrary(a)}` are *set-attacks*; `S_D` are
   *set-supports* (non-empty only for non-flat frameworks).
2. **Set strength** — each attacking/supporting set `E` is scored by a
   **set-aggregation** `ζ` (`ζ_Π` product or `ζ_⊥` min — Prop 4.5).
3. **Aggregate** — per assumption, an **aggregation** `α` combines attacker and
   supporter scalars (`α_Π` for DF-QuAD, `α_Σ` for QE).
4. **Influence** — `s_{t+1}(a) = ι(τ(a), α(...))` (`ι_lin` or `ι_q`).
5. **Repeat 2–4 to convergence.** `σ(a) = lim_t s(t)_a`.

A claim's strength is read from the assumption strengths via the argument
base-score `β_Π` and a `σ*` extraction mode (`max` = brave, the default).
The modular kernel is selected with `--graded-kernel` and the claim reading with
`--graded-claim-mode`.

### Step 1 — get a framework

`aba_graded.py` consumes any `ABAFramework` object — from the symbolic solver or
from a successful LLM sample:

```python
from aba_dataset import make_nixon_diamond
from aba_algorithm import solve_aba_learning

problem, _ = make_nixon_diamond()
framework, _ = solve_aba_learning(problem)
domain = problem.get_domain()
```

### Step 2 — assign base scores to assumptions

Three sources are available, trading cost for interpretability:

| Source | How to obtain | When to use |
| --- | --- | --- |
| **Uniform** | empty dict (default 0.5) | Quick baseline; no extra calls needed |
| **Sample frequency** | `assumption_scores_from_samples(fw_list)` | Free when k-sampling already ran; reflects the model's own distribution |
| **LLM-elicited** | `assumption_scores_from_llm(framework, backend)` | Most informative; one extra LLM call per assumption |

```python
from gradual.aba_graded import (
    assumption_scores_from_samples,
    assumption_scores_from_llm,
)

# Option A — uniform (nothing extra needed, pass {} later)
scores = {}

# Option B — sample frequency
# fw_list is your List[ABAFramework] collected from the k LLM samples
scores = assumption_scores_from_samples(fw_list)
# e.g. {"normal_quaker": 0.6, "alpha": 0.4}

# Option C — LLM-elicited
from aba_model import get_backend
backend = get_backend("groq", model="llama3-70b")
scores = assumption_scores_from_llm(framework, backend,
                                    context="Nixon Diamond problem")
```

### Step 3 — compute graded entailment

```python
from gradual.aba_graded import GradedABA

g = GradedABA(
    framework=framework,
    domain=domain,
    assumption_scores=scores,   # from Step 2; {} → uniform 0.5
    default_score=0.5,
    max_depth=8,
)

strength, tree = g.graded_entailment("pacifist(a)")
print(f"σ = {strength:.3f}")
print(tree.to_text())
```

The explanation tree shows every argument, its base score, the supports and
attacks that flow into it, and the final DF-QuAD strength at each node:

```text
pacifist(a)  base=0.00 σ=0.71
  +support:
    body_of(pacifist(a))  base=1.00 σ=0.71
      +support:
        quaker(a) [fact]  base=1.00 σ=1.00
        normal_quaker(a) [asm]  base=0.60 σ=0.54
          -attack:
            abnormal_quaker(a)  base=0.00 σ=0.46
```

### Step 4 — compare crisp vs. graded across all queries

```python
from gradual.aba_graded import compare_crisp_vs_graded

reports = compare_crisp_vs_graded(
    framework, domain,
    queries=problem.positive + problem.negative,
    assumption_scores=scores,
    threshold=0.5,
)

for r in reports:
    print(f"{r.query:20s}  crisp={r.crisp_entailed}  "
          f"graded={r.graded_strength:.3f}  agree={r.agree}")
```

`agree=True` means the graded reading (strength > 0.5) matches the Clingo binary
verdict. Disagreements indicate cases where the framework is technically valid but
the assumptions are scored weakly — useful as a confidence diagnostic.

### Step 5 — contestability (optional robustness check)

Raise or lower one assumption's score and verify that the conclusion moves in the
expected direction:

```python
from gradual.aba_graded import contest_base_score

result = contest_base_score(
    framework, domain,
    query="pacifist(a)",
    assumption_pred="normal_quaker",
    old_scores=scores,
    new_value=0.9,          # raise the assumption's strength
)

print(result.intervention)   # "normal_quaker: 0.60 -> 0.90"
print(result.original)       # σ before the intervention
print(result.contested)      # σ after
print(result.direction_ok)   # True if raising a pro-assumption raised the conclusion
```

`direction_ok=False` flags a non-monotonic response — a sign that the argument
structure contains a hidden indirect attack worth inspecting.

### Using the BSAF semantics directly

```python
from gradual.aba_bsaf import GradualABA, compare_crisp_vs_graded_bsaf

g = GradualABA(framework, domain, assumption_scores=scores,
               kernel="dfquad_prod", claim_mode="max")
print(g.converged, g.iterations)        # fixpoint convergence info
print(g.assumption_strengths())          # ground assumption -> σ
print(g.query_strength("pacifist(a)"))   # claim strength (brave reading)

# crisp vs BSAF graded across queries (same shape as the baseline's function)
for r in compare_crisp_vs_graded_bsaf(framework, domain,
                                      queries=problem.positive + problem.negative,
                                      assumption_scores=scores):
    print(r.query, r.crisp_entailed, r.graded_strength, r.agree, r.converged)
```

### Random ABAF generation + convergence experiment

`gradual/aba_generate.py` reproduces the benchmark-generation procedure of
Lehtonen et al. (IJCAI 2024) and the BSAF convergence experiment of the KR-2025
paper (its Figure 3).

```python
from gradual.aba_generate import generate_random_abaf, convergence_experiment

# one random (possibly non-flat) quantitative ABAF
q = generate_random_abaf(n_sentences=40, assumption_ratio=0.4,
                         nonflat_coef=0.1, cycle_prob=0.05,
                         base_score_init="random", seed=1)
# q.framework, q.base_scores, q.flat, q.meta

# convergence rate + avg steps per (kernel, base-score init)
convergence_experiment(n_frameworks=40, n_sentences=30, nonflat_coef=0.1,
                       cycle_prob=0.08, seed=100)
```

Generator parameters (faithful to `cycle_bengen_asp.py`): `n_sentences`,
`n_assumptions` / `assumption_ratio`, `n_rules_per_head`, `size_of_bodies`,
`cycle_prob`, `nonflat_coef` (0 = flat), `base_score_init` (`constant` | `random`).
As in the paper, **DF-QuAD converges most reliably** and Min-based set
aggregation degrades on larger or cyclic instances.

---

## Command-Line Reference

### Dataset

| Argument | Default | Description |
| --- | --- | --- |
| `--n-synthetic N` | `0` | Generate N random single-path synthetic problems |
| `--n-complex N` | `0` | Generate N two-path complex synthetic problems (see below) |
| `--anonymize` / `--no-anonymize` | **on** | Rename predicates/constants to abstract symbols (see [Anonymised Problems](#anonymised-problems-controlling-for-world-knowledge)); on by default, `--no-anonymize` keeps real names |
| `--anonymize-scheme {letters,indexed}` | `letters` | Abstract naming scheme: `p,q,…/a,b,…` or `p0,p1,…/c0,c1,…` |

**`--n-synthetic`** generates single-path problems: one background predicate, one
assumption, one contrary rule. Fast to generate; useful for aggregate statistics.
The graded reading gives binary σ (0 or 1) because there is exactly one argument
path per query.

**`--n-complex`** generates two-path problems: two independent background predicates
each leading to the same target predicate, each gated by its own assumption. This
forces the symbolic solver and the LLM alike to discover **two** defeasible rules
for the same head. The richer QBAF produces genuinely intermediate σ values — constants
reachable via both paths score higher than those reachable via only one:

```text
target(c6)  — reachable via prop_a AND prop_b:  sigma=0.750  crisp=True
target(c2)  — reachable via prop_a only:        sigma=0.500  crisp=True
target(c3)  — exception (prop_a defeated):      sigma=0.000  crisp=False
```

### LLM

| Argument | Default | Description |
| --- | --- | --- |
| `--backend BACKEND` | `mock` | LLM backend: `groq`, `hf_api`, `google_ai`, or `mock` |
| `--model MODEL` | backend default | Model name or alias (see [LLM Backends](#llm-backends)) |
| `--thinking` | off | Gemini thinking mode (google_ai, gemini-2.5-*) |
| `--modes MODE …` | `direct cot guided algorithm` | Prompt modes: `direct`, `cot`, `guided`, `algorithm` |
| `--n-samples N` | `5` | LLM samples per problem (controls pass@k) |
| `--temperature F` | `0.7` | Sampling temperature |
| `--max-tokens N` | `1024` | Maximum tokens per LLM response |
| `--min-interval F` | `0.0` | Minimum seconds between requests (rate-limit throttle; try `2`–`4`) |

### Run modes

| Argument | Description |
| --- | --- |
| `--symbolic-only` | Run only the ASP-ABAlearnB baseline; skip all LLM calls |
| `--verbose` | Print per-step trace for the symbolic solver |

### Graded semantics

| Argument | Default | Description |
| --- | --- | --- |
| `--graded` | off | Run graded analysis (BSAF headline + BAF baseline, side-by-side) |
| `--graded-source SOURCE` | `uniform` | Base score source: `uniform`, `sample_freq`, or `llm_elicited` |
| `--graded-kernel KERNEL` | `dfquad_prod` | BSAF modular kernel: `dfquad_prod`, `dfquad_min`, `qe_prod`, `qe_min` |
| `--graded-claim-mode MODE` | `max` | Claim reading: `max` (brave), `min`, `avg`, `noisy_or` (accrual) |

| `--graded-source` value | Cost | How scores are obtained |
| --- | --- | --- |
| `uniform` | free | All assumptions fixed at 0.5 — ArgLLMs baseline |
| `sample_freq` | free (reuses k-samples) | Fraction of LLM samples that include each assumption |
| `llm_elicited` | 1 extra call/assumption | Dedicated LLM prompt; uses Clingo to pre-compute the exception base rate |

| `--graded-kernel` value | Set-agg | Agg + Influence | Note |
| --- | --- | --- | --- |
| `dfquad_prod` | product | DF-QuAD | Most robust (>90% convergence); the default |
| `dfquad_min` | min | DF-QuAD | Weakest-link set aggregation |
| `qe_prod` | product | Quadratic Energy | Fastest under product |
| `qe_min` | min | Quadratic Energy | Degrades on large/cyclic instances |

### Output

| Argument | Default | Description |
| --- | --- | --- |
| `--output PATH` | `./results` | Directory for all output files and figures |
| `--export` | off | Export all frameworks to `frameworks.jsonl`, `frameworks.md`, `defeasibility.csv` |

---

## Benchmark Problems

| Problem | Description | Difficulty |
| --- | --- | --- |
| `nixon_diamond` | Pacifists and republicans — requires Assumption Introduction | High |
| `flies` | Tweety flies but penguins don't | Low |
| `tax_law` | Employed vs. self-employed tax rules | Medium |

Add synthetic problems for statistical power:

```powershell
# Single-path (fast; binary sigma values)
python main.py --backend groq --model llama3-70b --n-synthetic 50 --modes guided --n-samples 5

# Two-path (richer argument structure; intermediate sigma values)
python main.py --backend groq --model llama3-70b --n-complex 10 --modes guided --graded
```

---

## Exporting Frameworks

Pass `--export` to dump every learned framework — symbolic ground truth and
all LLM samples — to three human-readable files:

```powershell
python main.py --backend groq --model llama3-70b --modes guided --export
python main.py --symbolic-only --export          # symbolic solutions only
python main.py --graded --export                 # include DF-QuAD scores
```

### What each file contains

| File | Format | Content |
| --- | --- | --- |
| `frameworks.jsonl` | JSONL | One record per framework; machine-readable, re-loadable |
| `frameworks.md` | Markdown | Human catalogue grouped by problem; for reading and appendices |
| `defeasibility.csv` | CSV | Flat table: per (problem, source, sample) defeasibility flags |

### What each record includes

Each record is enriched with four explainability layers beyond the raw Prolog:

1. **Natural-language rules** — each rule rendered as `"head holds if body."` using `Rule.to_text()`
2. **Mechanism tags** — each rule labelled as one of:
   - `ground_fact` — memorised a specific constant (bad)
   - `assumption_guarded` — uses a defeasible assumption (the right structure)
   - `contrary_rule` — defines when an assumption is defeated
   - `intensional_copy` — conditions on background predicates only, no constants (generalises to unseen)
   - `mixed` — combination of the above
3. **Analysis narrative** — a one-paragraph natural-language account of how the model generalised, generated by `aba_explain.build_narrative()`
4. **Graded entailment table** — per-query `(crisp, σ, agree)` triplets from DF-QuAD (only when `--graded` is also given)

### Example Markdown output

````markdown
**llama-3.3-70b** / guided / sample 2 — `DEFEASIBLE`  (valid, generalises)

```prolog
pacifist(X) :- quaker(X), normal_quaker(X).  % [assumption_guarded]
abnormal_quaker(X) :- republican(X), alpha(X).  % [assumption_guarded]
% assumption: alpha(X) defeated_by c_alpha(X)
```

*Plain language:*

- pacifist(X) holds if quaker(X) and normal_quaker(X).
- abnormal_quaker(X) holds if republican(X) and alpha(X).

> On 'nixon_diamond', the model produced a framework that fits the training
> examples and correctly classifies ALL held-out examples (100%). It introduced
> 2 new rule(s): 2 assumption guarded. It also introduced the assumption(s)
> alpha(X) to make a rule defeasible, capturing exceptions.

| Query           | Crisp | σ     | Agree |
|-----------------|-------|-------|-------|
| `pacifist(a)`   | True  | 0.714 | yes   |
| `pacifist(b)`   | False | 0.286 | yes   |
````

---

## Output Structure

`main.py` writes into `--output` (default `./results/`, **gitignored** — a
working directory). Runs worth keeping are *promoted* to
[`experiments/`](experiments/) with a `MANIFEST.md`; see the
[experiment registry](docs/EXPERIMENTS.md).

```text
results/<run>/
├── summary.json              # Metrics per mode + symbolic baseline + per-tier (by_tier)
├── results_<mode>.jsonl      # Per-sample records: raw LLM output, error class, metrics
├── explanations.md           # Per-problem narrative of how the model generalised
├── frameworks.{jsonl,md}     # Every learned framework, mechanism-tagged   (--export)
├── defeasibility.csv         # Flat per-sample table for stats             (--export)
├── graded_results.json       # BSAF vs BAF graded semantics                (--graded)
├── name_maps.json            # Anonymisation maps (de-anonymise for reading)
└── figures/                  # validity, error breakdown, heatmap, complexity (PDF)
```

Quick analysis:

```python
import json
path = "experiments/01_bench_prompts_v1/bench_qwen2.5-7b/results_guided.jsonl"
samples = [json.loads(l) for l in open(path)]
clean = [s for s in samples if s["error_type"] == "none"]
print(f"{len(clean)}/{len(samples)} samples fully solve the learning problem")
```

---

## Troubleshooting

**All results are `parse_error`** — the model is not following the output format.
Try a stronger model (`--model llama3-70b` / `--backend google_ai`) or a more
guided mode (`--modes guided` or `--modes algorithm`).

**Groq rate limit** — use `--min-interval 3` to space requests, or switch to
`--model llama3-8b`. Per-day caps cannot be worked around by waiting; switch to
`--backend hf_api` instead.

**`gen@1` is low but `degenerate_rate` is high** — the model is memorising.
This is a result, not a bug; the `overfit_gap` and `degenerate_rate` quantify it.

**Clingo not found** — install via `conda install -c potassco clingo` or
`pip install clingo --no-cache-dir`.

---

## Reference

De Angelis, E., Proietti, M., & Toni, F. (2024). *Learning Brave
Assumption-Based Argumentation Frameworks via ASP.* ECAI 2024, 3445–3452.

Rago, A., Toni, F., Aurisicchio, M., & Baroni, P. (2016). *Discontinuity-Free
Decision Support with Quantitative Argumentation Debates.* KR 2016.

Freedman, G., Rago, A., & Toni, F. (2025). *ArgLLM: Harnessing the Power of
Large Language Models for Argumentation.* AAAI 2025.

Rapberger, A., Russo, F., Rago, A., & Toni, F. (2025). *On Gradual Semantics for
Assumption-Based Argumentation.* KR 2025, 512–522. (BSAF gradual semantics;
code: <https://github.com/briziorusso/GradualABA>.)

Lehtonen, T., Rapberger, A., Toni, F., Ulbricht, M., & Wallner, J. P. (2024).
*Instantiations and Computational Aspects of Non-Flat Assumption-Based
Argumentation.* IJCAI 2024, 3457–3465. (Random ABAF benchmark generator.)
