# How the evaluation got here

A chronological record of *why* the measurement instrument looks the way it
does, kept for the thesis's methodology chapter. Results live in
[EXPERIMENTS.md](EXPERIMENTS.md); this file records the reasoning, the dead
ends, and the errors found — including the ones in our own instrument, which
are the part a methodology chapter needs and a results table hides.

**Framing held throughout.** ASP-ABAlearnB (De Angelis, Proietti & Toni, ECAI
2024) is the reference of the field. The LLM is scored on how faithfully it
**replicates** the algorithm. There is no "beating" in either direction, and
the symbolic `train_only` figure (53.8%) is not a ceiling on the algorithm: it
solves the training problem 28/28 by construction, and 53.8% is only how often
the solution it happened to pick *also* generalises to held-out examples —
our added criterion, not Definition 1's.

---

## Phase 1 — Outcome metrics (sets 00–03)

The question asked was: given a learning problem, does the model produce a
Definition-1 solution? Four metric revisions refined it (see EXPERIMENTS.md);
rev. 3 and 4 were both corrections that changed reported numbers **without any
new model output**, because every run stores its raw answers and can be
re-scored offline. That property is what made every later recovery possible.

## Phase 2 — Outcome and process come apart

At Qwen2.5-14B:

| mode | clean@k | intensional | at 1536 cap |
| --- | --- | --- | --- |
| direct | **56.3%** | 1.00 | 0% |
| cot | 30.1% | 0.91 | 0% |
| algorithm | 21.4% | **0.47** | **0%** |

More procedural guidance made the outcome *worse*, intensionality collapsed and
degeneracy appeared, with truncation ruled out. `guided` confirmed it: handed
the RoLe facts outright, 14B drops to 7.8%, its worst mode. An outcome metric
cannot explain this — it is the signature of performing RoLe and abandoning Gen.

## Phase 3 — Trace mining, attempted and abandoned

First attempt: recover the R1/R2/R3/R4 sequence from the model's free text and
align it against the symbolic trace.

**It sat at its chance floor.** Against random symbol sequences of the same
lengths: mistral 0.323/0.332 vs chance ~0.32/~0.33; Qwen-14B 0.418/0.531 vs
~0.44/~0.49; Qwen-3B 0.156 vs ~0.20 — *below* chance. A four-symbol alphabet
over length-4–8 sequences cannot discriminate. With the metric at its floor,
extraction noise dominated and each cleanup patch swung results wildly (7B moved
0.649 → 0.000 on one fix).

`align_type` was dropped entirely. Rule-keyed measures (chance ≈ 0) survive as
secondary descriptive statistics via `rescore.py --trace`.

> **Lesson that became a standing rule:** no metric is reported without its
> measured chance floor beside it. Applied later, this caught four of eight
> binary probe cells as constant responders that raw accuracy would have shown
> as 0.45–0.55.

**Root cause of the failure**, and the hinge of the whole project: a
transformation is checkable only relative to the framework state it was applied
to — R2 is legal only against the current rule set, R3 justified only if the
framework had actually stopped being a solution. Free-form prose destroys that
state, and alignment tried to recover it *by position*, which prose does not
preserve.

## Phase 4 — Step probes: supply the state instead of inferring it

Each probe presents one decision point from the real execution and asks for that
one decision. States are harvested through an `observer` callback added to
`gen_phase` — not a re-implementation of the loop, which would drift from the
reference. Probes are keyed to lines of Algorithm 1 (table in EXPERIMENTS.md).

**Validation rule:** feeding the reference algorithm's *own* decisions back
through every probe must score correct — currently 328/328. A probe that
rejects the algorithm's own answer is mis-specified. Two were found that way:

1. `introduce` demanded an intensional contrary, but Algorithm 1 rote-learns the
   contrary as ground facts (lines 23–25) and folds it only on a *later* Gen
   iteration — Example 10, ρ17 → ρ19.
2. It rejected assumption **reuse**, where line 36 sets `S := ∅` and there is no
   contrary to write.

## Phase 5 — First probe run (Sept 2026) and two instrument defects

Qwen2.5 3B/7B/14B/32B, all 4-bit, 780 probes each over 103 problems. The
hand-audit gate — read the raw rows before reporting any aggregate — found two
defects, **both in our harness, not the models**:

1. **Format conflict.** `_head()` prepended the full `SYSTEM_PROMPT`, which ends
   *"Output ONLY the two sections… NEW RULES: / NEW ASSUMPTIONS:"*, while `_P4`
   asked for `RULE:` / `ASSUMPTION:`. The scorer required the literal
   `ASSUMPTION:` prefix, so the oracle **never ran** on 87/103 (3B), 70/103 (7B)
   and 92/103 (32B). 14B alone followed the local instruction. Reported 0.029
   for 32B where the content was largely correct — the probe was measuring which
   instruction a model obeyed.
2. **Prompt echo.** 7B echoes the problem *after* its answer in 415/780 probes;
   the fact extractor swallowed the echoed background, scoring one `role` answer
   as 12 facts against an oracle of 2.

Both were recovered offline from stored answers (`rescore.py --probes`). On
recovery 32B's R3 went 0.029 → 0.757, and **14B changed zero rows** — the
regression guard that showed the fix was correct rather than merely permissive.
7B's `role` partial credit went 0.272 → **0.000**: it had been credited for
reciting the background.

## Phase 6 — Definitional audit against the paper

Re-reading §5–6 of the paper against the implementation produced three
corrections and one open item.

1. **`role` tests RoLe, not R1.** R1 adds a *single* fact (`p(X) ← X = t`); the
   minimal-set property comes from `#minimize` in Definition 2(e), used by the
   RoLe procedure. Similarly `fold` tests `applyFolding` (a bounded sequence,
   Prop. 3), not one R2 step. Naming corrected.
2. **R4 was described too narrowly.** The paper licenses removal purely by
   "R \ {ρ} bravely entails E⁺, E⁻"; in Example 9 the redundancy comes from a
   *background* rule, not from something learnt later. Code was already correct.
3. **`introduce` demanded more than the algorithm decides.** `applyAsmIntro`
   returns ⟨ρ, α(X), S⟩, but S is computed by ASP at line 44, not chosen.
   The probe now asks only for the rule and the assumption, and runs that same
   RoLe (T = {c_α}) itself.
4. **Open:** `apply_folding` folds against the *background* only, while
   Algorithm 1 line 17 passes `R`, which grows at line 20 with each learnt
   defeasible rule. Both the solver and the oracle share the restriction, so the
   328/328 test cannot see it — `fold` scores are a lower bound. (The paper is
   itself ambiguous: §6's prose says "rules in `Rl \ {ρ}`" while line 17 passes
   `R`, and every worked example folds against background rules.)

**Also confirmed by the audit**, rather than merely assumed: asking `role` for
ground facts is *required*, since the paper calls RoLe's output "a
(non-intensional) solution" (§6, Example 5) — so `SYSTEM_PROMPT`'s "NEVER leave
ground facts" was the half that contradicted the algorithm. And the paper's own
conclusion names Folding's nondeterminism as *"the most critical issue"*, with
work in progress on controlling it — which is exactly what the `fold` probe
measures, and the strongest external justification for this direction.

## Phase 7 — The backtracking asymmetry

Correcting (3) above inverted the scale trend: 7B 0.903 > 14B 0.864 > 32B 0.767.
The confound check fired, and the cause was ours again.

32B **reuses** an existing assumption on 102/103 probes — line 36's preferred
move, which the paper calls "a key point for enforcing the termination of the
algorithm". When a reuse fails, Algorithm 1 does not err: line 39 fails, it
**backtracks**, and line 41 mints a fresh α. The model gets one shot. Measured,
**all 24** of 32B's failed reuses are rescued by that fallback (7B 7/7, 14B 6/6,
3B only 2/7). Scoring the literal single answer penalised the model that was
most faithful to the reference.

The oracle now credits the documented fallback. R3 then saturates (3B 0.563, 7B
0.971, 14B 0.922, 32B 1.000): **on this benchmark R3 does not discriminate above
3B**, which is a finding, not a defect to engineer around.

A second number, agreement with line 36, was designed and then **rejected as
degenerate**: an assumption relative to the body (Definition 4) exists in only
2.9% of these probes, so "always answer fresh" would score 0.97 — the same trap
the chance-floor rule exists to catch. What is reported instead is `reuse_rate`,
descriptively: 32B reuses on 99% of probes where the algorithm would reuse on
3%, and still reaches a legal result. Identical outcomes, divergent process —
which is the thesis's own question in miniature.

## Current state

| | chance | 3B | 7B | 14B | 32B |
| --- | --- | --- | --- | --- | --- |
| `role` (RoLe) | ~0 | 0.000 | 0.000 | 0.534 | **0.777** |
| `fold` (applyFolding) | ~0 | 0.011 | 0.130 | 0.196 | **0.484** |
| `introduce` (R3, with fallback) | ~0 | 0.563 | 0.971 | 0.922 | **1.000** |
| `check` (balanced) | 0.50 | 0.50 | 0.703 | **0.780** | 0.50 |
| `subsume` (R4, balanced) | 0.50 | 0.50 | 0.50 | 0.52 | 0.51 |

Reading: scale buys the rule-rewriting steps and buys **nothing** on evaluating
the framework state those rewritings act on. `check` peaks at 14B — 32B answers
a constant "no longer a solution" on 186/186, 3B a constant YES — and R4 is at
the floor for every model, all four constant responders, so no model performs
Fact Subsumption anywhere in 3B–32B.

**Caveat on the table.** These are the *committed* answers re-scored under the
corrected oracles. They were generated under probe prompts **v1**, which carried
both conflicts of Phase 5. The prompts are now fixed (v2: definitions-only
preamble, RoLe asked for ground facts explicitly, R3 asking for two lines), so
`role` in particular should be re-run before the figures are final — 3B answered
a literal `NONE` on every `role` probe under a system prompt that forbade ground
facts.

## Pending

- Re-run all four models with probe prompts v2; promote to `experiments/04_*`
  with a MANIFEST recording the prompt version.
- Hand-audit ≥20 rows of the new run before reporting aggregates (the rule that
  caught both Phase-5 defects).
- Decide the `apply_folding` scope question (item 4 above); measure how many
  extra legal folds appear when folding against `R ∪ learnt`.
- Confound check on the new run: no smaller model may outrank a larger one on a
  fidelity measure without an explanation of the mechanism.
