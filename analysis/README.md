# `analysis/` — offline studies

Measurement scripts that read a finished run's **stored rows** and score them
against the ASP-ABAlearnB reference. **No model, no GPU** — every row keeps its
`raw_output`, so all of this is CPU-only re-scoring of committed data.

These are measurement scripts, not library modules. Reusable machinery belongs in
`src/`; the report generators live in `extras/`.

| script | answers |
| --- | --- |
| `null_baselines.py` | what does a probe metric, or with `--end-to-end` an end-to-end metric, score with **no reasoning at all**? |
| `s2_errors.py` | where does an arm-S2 run first leave the reference, and what in training explains it? |
| `answer_shapes.py` | what do the arms write on a split, against the shape of v1's training answers? |

```bash
python analysis/null_baselines.py
python analysis/null_baselines.py --set experiments/06_probes_v3   # each model against the floors
python analysis/null_baselines.py --end-to-end --set experiments/07_e2e_whole_v4
python analysis/s2_errors.py     --s2 s2          # s2_s1: the seed-1 replicate
python analysis/answer_shapes.py --split table1   # or test, heldout
```

`--benchmark` must match the run that produced the set (default 20).

## What the end-to-end metrics measure

Valid and clean ask whether an answer *is a solution* (Definition 1, on the posed
examples). Exact asks whether it is *the algorithm's* answer. They differ because
Algorithm 1 is one sound, incomplete, nondeterministic procedure for producing a
solution: Theorem 3 runs one way only (algorithm success ⟹ intensional solution),
so the set of Definition-1 solutions strictly contains the set of ASP-ABAlearnB
outputs. The paper itself never uses a success-rate metric: Table 1 reports
*time*, because soundness makes correctness a given.

## Read every metric against its floor

A floor is what a policy that does no reasoning scores through the same scorer, and
`null_baselines.py` measures it rather than assuming 0 or 0.5.

- **Probes.** Each probe's floor is the best of several no-reasoning policies. On
  the v3 set they are:
  - `role` **0.994** (one fact per positive example);
  - `fold` **1.000** (fold onto dom(X));
  - `check` **0.633** and `subsume` **0.762** (surface cues; a constant answer
    scores 0.500 balanced);
  - `introduce` **0.855** (METHOD_HISTORY, Phase 10).

  In sets 04 and 05, `introduce` had a floor of **1.000**, because the fallback
  those sets credited makes it satisfied by construction.
- **End to end.** On the 103-problem benchmark, the floors from the problem as
  posed are:
  - clean@k **0.777** (a positional rule that reads no rule body);
  - exact@k **0.388** (one answer for all problems);
  - valid@1 and agreement **1.000**.

  The benchmark has only 9 distinct algorithm answers, so the tier constant
  (the commonest answer of the problem's own tier) is exact on 0.951. It is
  reported as a diagnostic, not a floor: no model is given the tier or the other
  answers (METHOD_HISTORY, Phase 13).

## Known limitation: R4 is unmeasured — for a sample-size reason

**Fact Subsumption is measured by neither instrument.** The `subsume` probe sits
at its floor for every model. End to end, R4's question (is the answer still a
solution without this ground fact?) arises only for answers that are solutions.
In set 05, 1,449 of the 1,466 answers with ground facts were not solutions, so
only 17 posed it, too few to score.

Any later measure must also handle this: the reference does not reach an R4
fixpoint. It tests subsumption once, when a fact is popped (line 16), and never
retests a rule that a *later* assumption introduction makes redundant. So 8 of the
103 answers in set 05's symbolic traces keep a removable intensional rule. For
example, `t2_defeas_0006_anon` answers `v(X) :- r(X).` beside
`v(X) :- p(X), alpha_0(X).`, and the first is removable. "Contains a removable rule"
is therefore a divergence only for ground facts.

The line-18 solution check is an internal decision that leaves no trace in a
final answer, and is measurable only by the `check` step probe.

## Retracted — do not reintroduce

R3 fidelity was once gated on `n_new_assumptions <= the algorithm's R3 count`.
That gate is **wrong**. `n_new_assumptions` counts only *freshly minted*
assumptions, so it scores an answer that guards a rule by **reusing a background
assumption** as a divergence. In `t2_defeas_0000_anon`, `u(X)` is a background
assumption with contrary `t(X)`, and `v(X) :- p(X), u(X).` is a valid solution.
Whether Algorithm 1 would reuse it is a separate question: line 36 reuses an
assumption only when it is relative to the rule's body (Definition 4).

The gate produced a confident, wrong headline that had to be withdrawn. The score
card reads R3 as whether a learnt rule body carries an assumption atom **at all**,
background or fresh (`defeasible` against `ref_defeasible`).

This is the third assumption-counting proxy to misfire the same way, after
`reuse_agreement` and `introduce` accuracy. Treat any such proxy as mis-specified
until it has been checked against the algorithm's own answer.
