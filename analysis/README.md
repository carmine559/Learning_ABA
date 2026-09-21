# `analysis/` — offline fidelity re-scoring

Measurement scripts that read a finished run's **stored rows** and score them
against the ASP-ABAlearnB reference. **No model, no GPU** — every row keeps its
`raw_output`, and `src/aba_prompts.py::parse_llm_output` rebuilds the candidate
framework from it, so all of this is CPU-only re-scoring of committed data.

These are measurement scripts, not library modules. Reusable machinery belongs in
`src/`; the report generators live in `extras/`.

| script | answers |
| --- | --- |
| `null_baselines.py` | what does a probe metric score with **no reasoning at all**? |
| `conformance.py` | how much of `gen@k` is a conformant *output*? |
| `step_fidelity.py` | was the *algorithm* followed — R1, R2, R3, R4 separately? |

```bash
python analysis/null_baselines.py
python analysis/conformance.py   --set experiments/05_scale_4bit_probes_v2
python analysis/step_fidelity.py --set experiments/05_scale_4bit_probes_v2
```

`--benchmark` must match the run that produced the set (default 20).

## Why three scripts and not one number

They sit at three different levels, and conflating them is what these scripts
exist to prevent:

1. **`gen_valid` is Definition 1**, on the full problem
   (`src/aba_generalization.py`). It asks whether the output *is a solution*.
2. **Algorithm 1 is one sound, incomplete, nondeterministic procedure** for
   producing one. Theorem 3 runs one way only — algorithm success ⟹ intensional
   solution — so the set of Definition-1 solutions **strictly contains** the set
   of ASP-ABAlearnB outputs.
3. `gen@k` therefore scores membership in the **outer** set. Fidelity to the
   algorithm is a different question, and `step_fidelity.py` is the one that
   asks it.

The paper itself never uses a success-rate metric: Table 1 reports *time*,
because soundness makes correctness a given.

## Read the balanced column, not the raw one

On the 103-problem benchmark the algorithm's answer is defeasible on 81 problems
and monotonic on 22. A policy that guards every rule without reasoning therefore
scores **0.786 raw agreement** on R3. `step_fidelity.py` reports raw beside
balanced for exactly this reason; balanced puts any constant responder at 0.500.

The same trap applies to the probes, which is what `null_baselines.py` measures:
`check` and `subsume` have a **~0.68** surface-cue floor rather than 0.50, and
`introduce` has a floor of **1.000** because Proposition 2 makes it satisfied by
construction — it must be reported inverted, as an error count.

## Known limitation: R4 is not separable end-to-end

The algorithm leaves zero ground facts on every problem in this benchmark
(Theorem 3), so "R1 residue never folded away" and "R4 Fact Subsumption not
applied" are the **same observable** in a final answer. `step_fidelity.py`
prints an R4 column, but it is structurally identical to R1. Separating them
needs either a redesigned `subsume` probe or problems whose algorithm answer
retains ground facts. **Currently Fact Subsumption is measured by neither
instrument** — the `subsume` probe sits at its surface-cue floor for every model.

The line-18 solution check is an internal decision that leaves no trace in a
final answer, and is measurable only by the `check` step probe.

## Retracted — do not reintroduce

R3 fidelity was once gated on `n_new_assumptions <= the algorithm's R3 count`.
That gate is **wrong**. `n_new_assumptions` counts only *freshly minted*
assumptions, so it scores a model that applied R3 by **reusing a background
assumption** as a divergence — which is precisely what line 36 / Definition 4
REUSE FIRST asks for. In `t2_defeas_0000_anon`, `u(X)` is a background
assumption with contrary `t(X)`, so `v(X) :- p(X), u(X).` is a legitimate R3.

The gate produced a confident, wrong headline that had to be withdrawn. R3
application is now detected by whether a learnt rule body carries an assumption
atom **at all**, background or fresh; the branch taken (reuse vs mint-fresh) is
reported separately.

This is the third assumption-counting proxy to misfire the same way, after
`reuse_agreement` and `introduce` accuracy. Treat any such proxy as mis-specified
until it has been checked against the algorithm's own answer.

## Results as of set 05

Numbers below are from `experiments/05_scale_4bit_probes_v2` and reproduce by
running the commands above.

**R2 Folding replicates and scales** — exact-match rate on the non-assumption
body, per head predicate:

| | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| 3B | 0% | 11% | — | 0% |
| mistral-7b | 11% | 20% | 0% | 13% |
| 7B | 20% | 21% | 10% | 24% |
| 14B | 52% | 47% | 21% | 27% |
| **32B** | **79%** | 73% | **84%** | 75% |

**R3 Assumption Introduction does not, at any scale** — balanced agreement is at
the constant-responder floor for every model except 7B `cot` (0.643) and 14B
`guided` (0.636). 3B and 32B are constant responders at opposite poles: 3B never
guards (and emits 0.06 rules/sample against the algorithm's 2.28, so its
`agr_M = 1.000` is vacuous), 32B always guards. 32B's raw 0.780 is *below* the
0.786 null floor.

**Whole rule sets almost never match**: 12 exact matches in 3,708 samples, every
one of them on `t1_mono` — the monotonic tier, where the answer is a single
unguarded rule. Zero on any problem requiring R3.

Taken together: **the model replicates the syntactic rewriting and not the
semantic decision that governs it.** Folding is a local, checkable rewriting;
Assumption Introduction is gated by the line-18 satisfiability test, a global
property of the framework. This reproduces end-to-end what the step probes found
in isolation — `fold` scales with size, `check` sits at the floor for every model
from 3B to 32B.
