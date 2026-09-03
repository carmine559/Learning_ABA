# Task 2 — gradual semantics for ABA

Clingo returns a binary verdict: a claim is bravely entailed or it is not. The
graded layer computes a **strength σ ∈ [0, 1]** for the same learned framework.
Two semantics are implemented, mirroring the comparison in Rapberger, Russo,
Rago & Toni, *On Gradual Semantics for Assumption-Based Argumentation*
(KR 2025):

| Module | Semantics | Nodes | Role |
| --- | --- | --- | --- |
| [`gradual/aba_bsaf.py`](../gradual/aba_bsaf.py) | **BSAF gradual ABA** — the paper's contribution | assumptions | headline |
| [`gradual/aba_graded.py`](../gradual/aba_graded.py) | **BAF baseline** — argument-tree DF-QuAD | arguments | comparison |

`aba_bsaf.py` computes an iterative strength-evolution **fixpoint**
(Definition 4.17), which resolves cyclic attack structures exactly — on Nixon
Diamond the cycle `normal_quaker ↔ alpha` gives `pacifist(a) = 0.3333`.
`aba_graded.py` builds a per-query argument tree with a depth cap and only
approximates it, reporting `0.375` for the same query. `--graded` runs both
side by side so the difference is visible.

**Design rule.** The LLM's uncertainty enters *only* through the base scores of
the ABA assumptions. The argument structure — rules, attacks, supports — is
always taken from the symbolic framework unchanged.

```text
Learned ABA framework
        │                                       │
        ▼ (structure fixed and symbolic)        ▼
  aba_validator.py                        aba_bsaf.py / aba_graded.py
  Clingo brave entailment                 gradual semantics
  binary: True / False                    continuous: σ ∈ [0, 1]
```

---

## The BSAF pipeline (Figure 1 of the paper)

1. **Abstraction** — build the BSAF `F_D = (A, R_D, S_D)`: nodes are the ground
   assumptions, `R_D = {(E, a) : E ⊢ contrary(a)}` are set-attacks, `S_D` are
   set-supports (non-empty only for non-flat frameworks).
2. **Set strength** — score each attacking/supporting set `E` with a
   set-aggregation `ζ` (`ζ_Π` product or `ζ_⊥` min; Proposition 4.5 shows only
   these two satisfy all the desired properties).
3. **Aggregate** — per assumption, `α` combines the attacker and supporter
   scalars (`α_Π` for DF-QuAD, `α_Σ` for QE).
4. **Influence** — `s_{t+1}(a) = ι(τ(a), α(…))` with `ι_lin` or `ι_q`.
5. **Repeat 2–4 to convergence.** `σ(a) = lim_t s(t)_a`.

A claim's strength is read from the assumption strengths via the argument base
score `β_Π` and a `σ*` extraction mode (`max` = brave, the default).

| `--graded-kernel` | ζ | α + ι | Note |
| --- | --- | --- | --- |
| `dfquad_prod` | product | DF-QuAD | most robust (>90% convergence); default |
| `dfquad_min` | min | DF-QuAD | weakest-link set aggregation |
| `qe_prod` | product | Quadratic Energy | fastest under product |
| `qe_min` | min | Quadratic Energy | degrades on large/cyclic instances |

> Implementation note: the KR-2025 PDF prints the QE influence function as
> `ι_q(b,w) = b − b·h(−w/k) + b·h(w/k)`. The `(1−b)` coefficient on the positive
> term is the standard form (Potyka 2018); `aba_bsaf.py` uses `(1−b)` and treats
> the printed `b` as an OCR artefact.

---

## Base scores

| `--graded-source` | Cost | How scores are obtained |
| --- | --- | --- |
| `uniform` | free | every assumption fixed at 0.5 — the ArgLLMs baseline |
| `sample_freq` | free | fraction of the k LLM samples that introduced each assumption |
| `llm_elicited` | 1 call per assumption | a dedicated prompt, grounded in a Clingo-computed exception base rate |

`llm_elicited` differs from the original ArgLLMs Figure-4 prompt: it first
computes, with Clingo, which domain constants already have the contrary
derivable, then shows the model that distribution and the resulting base rate,
so it reasons from concrete numbers. If the model returns something
unparseable, the fallback is the observed base rate, not 0.5.

---

## Using it from Python

```python
from src.aba_dataset  import make_nixon_diamond
from src.aba_algorithm import solve_aba_learning
from gradual.aba_bsaf  import GradualABA, compare_crisp_vs_graded_bsaf

problem, _ = make_nixon_diamond()
framework, _ = solve_aba_learning(problem)
domain = problem.get_domain()

g = GradualABA(framework, domain, assumption_scores={},
               kernel="dfquad_prod", claim_mode="max")
print(g.converged, g.iterations)
print(g.assumption_strengths())         # ground assumption -> σ
print(g.query_strength("pacifist(a)"))  # 0.3333

for r in compare_crisp_vs_graded_bsaf(
        framework, domain,
        queries=problem.positive + problem.negative,
        assumption_scores={}):
    print(r.query, r.crisp_entailed, r.graded_strength, r.agree, r.converged)
```

### Eliciting base scores first

```python
from gradual.aba_graded import (
    assumption_scores_from_samples, assumption_scores_from_llm,
)
from src.aba_model import get_backend

scores = {}                                     # uniform 0.5
scores = assumption_scores_from_samples(fw_list)  # from the k LLM samples
scores = assumption_scores_from_llm(            # one call per assumption
    framework, get_backend("groq", model="llama3-70b"),
    context="Nixon Diamond", domain=domain,
)
```

### The BAF baseline and its explanation tree

```python
from gradual.aba_graded import GradedABA, compare_crisp_vs_graded

g = GradedABA(framework, domain, assumption_scores=scores, max_depth=8)
strength, tree = g.graded_entailment("pacifist(a)")
print(f"σ = {strength:.3f}")
print(tree.to_text())
```

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

### Contestability

Raise or lower one assumption's score and check the conclusion moves the right
way (ArgLLMs Properties 1 & 2):

```python
from gradual.aba_graded import contest_base_score

result = contest_base_score(
    framework, domain, query="pacifist(a)",
    assumption_pred="normal_quaker", old_scores=scores, new_value=0.9,
)
print(result.intervention, result.original, result.contested, result.direction_ok)
```

`direction_ok=False` flags a non-monotonic response — a sign that the argument
structure contains a hidden indirect attack worth inspecting.

---

## Random ABAFs and the convergence experiment

[`gradual/aba_generate.py`](../gradual/aba_generate.py) reproduces the
benchmark-generation procedure of Lehtonen et al. (IJCAI 2024) and the BSAF
convergence experiment of KR 2025 (their Figure 3).

```python
from gradual.aba_generate import generate_random_abaf, convergence_experiment

q = generate_random_abaf(n_sentences=40, assumption_ratio=0.4,
                         nonflat_coef=0.1, cycle_prob=0.05,
                         base_score_init="random", seed=1)

convergence_experiment(n_frameworks=40, n_sentences=30,
                       nonflat_coef=0.1, cycle_prob=0.08, seed=100)
```

Generator parameters, faithful to `cycle_bengen_asp.py`: `n_sentences`,
`n_assumptions` / `assumption_ratio`, `n_rules_per_head`, `size_of_bodies`,
`cycle_prob`, `nonflat_coef` (0 = flat), `base_score_init`
(`constant` | `random`). As in the paper, DF-QuAD converges most reliably and
Min-based set aggregation degrades on larger or cyclic instances.

---

## Reference

Rapberger, A., Russo, F., Rago, A., & Toni, F. (2025). *On Gradual Semantics for
Assumption-Based Argumentation.* KR 2025, 512–522.
Code: <https://github.com/briziorusso/GradualABA>.

Rago, A., Toni, F., Aurisicchio, M., & Baroni, P. (2016). *Discontinuity-Free
Decision Support with Quantitative Argumentation Debates.* KR 2016. (DF-QuAD.)

Lehtonen, T., Rapberger, A., Toni, F., Ulbricht, M., & Wallner, J. P. (2024).
*Instantiations and Computational Aspects of Non-Flat Assumption-Based
Argumentation.* IJCAI 2024, 3457–3465. (Random ABAF generator.)
