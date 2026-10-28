# How the evaluation got here

A chronological record of *why* the measurement instrument looks the way it
does, kept for the thesis's methodology chapter. Results live in
[EXPERIMENTS.md](EXPERIMENTS.md); this file records the reasoning, the dead
ends, and the errors found — including the ones in our own instrument, which
are the part a methodology chapter needs and a results table hides.

**Framing held throughout.** ASP-ABAlearnB (De Angelis, Proietti & Toni, ECAI
2024) is the reference of the field. The LLM is scored on how faithfully it
**replicates** the algorithm. There is no "beating" in either direction, and
the symbolic `train_only` figure is not a ceiling on the algorithm: it solves
every training split by construction (103/103), and the figure is only how often
the solution it happened to pick *also* generalises to held-out examples —
our added criterion, not Definition 1's. That is 76/103 in set 05's summaries,
run before the Phase 8 fixes, and 88/103 with the current reference. The 53.8%
quoted here before has no data file behind it, and is not k/103 for any k.

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

> **Corrected in Phase 8.** The fallback read into lines 39 → 41 is not in the
> paper: after line 39 Algorithm 1 backtracks to line 19 or line 17, and never
> mints an assumption for a body that already has a relative one. The oracle
> change above credited an illegal step.

## State after Phase 7 (probe prompts v1)

Superseded by Phase 10's outcome (probe prompts v3, set 06).

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
facts. The `introduce` row also credits the line-41 fallback that Phase 8 found
is not in the paper, so it is an upper bound until re-scored.

## Phase 8 — Second audit against the paper (Sept 2026, training-corpus work)

Building training traces meant the reference had to be right step by step, not
only in its answers. Reading Algorithm 1 in the PDF line by line against
`gen_phase` found three errors, all in our instrument. The golden master
(`tests/test_golden_traces.py`) could not have caught any of them: it pins what
the reference does, not whether that is what the paper does.

1. **Line numbers taken from a summary.** During this work the pseudo-code was
   first read through a web summary of the arXiv HTML page, whose numbering is
   off by one after line 28 ("line 40" for `fail`). Code comments and commit
   929cf9b's message carried the wrong numbers. Checked against the PDF (ECAI
   p. 3449, identical to arXiv v2): `fail` is line 39, the relative-assumption
   test line 36, the fold choice line 17. Comments corrected; the commit
   message cannot be. **Rule since:** cite Algorithm 1 from the PDF only.

2. **Minting after a failed reuse.** The paper (p. 3450): if the assumption
   taken at line 36 gives no solution, *"it gets a failure (see line 39) and
   backtracks to the most recent choice point. This point can be line 19 … or
   line 17"*. The reference instead fell through to line 41 and minted a fresh
   α for the same body, which is exactly the reading Phase 7 adopted. Found by
   running the paper's own example: on Nixon (Examples 3 and 10) the reference
   learnt `abnormal_quaker(X) :- quaker(X), alpha_0(X)`, a step unreachable in
   the paper because `normal_quaker` is relative to `quaker(X)`. Fixed in
   929cf9b; Nixon now reproduces R′₂ up to the name of α, and a test pins it.
   `tax_law`
   also needed the `dom(X)` fold candidate that Definition 3 assumes is in R
   for every constant, appended last. 2/103 set-05 traces changed. **Open
   consequence:** the `introduce` oracle still credits the fallback (Phase 7's
   24/24 rescued 32B reuses among them) and has to be re-scored without it.

3. **A fold lookahead at lines 17–19.** The paper:

       17  ρf := applyFolding(ρ, R);
       18  if ¬sat(ASP(⟨Rt ∪ {ρf}, A, ¯⟩, ⟨E+, E−⟩, ∅)) then
       19     ⟨ρd, α(X), S⟩ := applyAsmIntro(ρf, Rt);

   One fold is taken; if it is not a solution, assumption introduction guards
   *that* fold, and another fold is tried only on backtracking. The reference
   checked every fold at line 18 before any assumption introduction, so a later
   fold that happened to be a solution won over line 19 on the first. Every
   output was still a valid run of the nondeterministic algorithm, but the
   procedure differed, and fidelity is scored against the procedure. Fixed:
   10/103 set-05 traces change (t2 2, t3 6, t4 2), all still succeed, all
   re-pinned. Side effect, checked against the paper: every defeasible problem
   now reaches line 39 on its contrary fact, because the first fold reuses the
   new α (relative to that body by Definition 4), fails, and line 17 takes the
   next fold. On the tier-spec-v2 corpus the intended class now agrees with the
   algorithm on 400/400 problems; before, 4–10% of defeasible ones avoided R3
   through a distractor fold, an artefact of the lookahead.

**What the paper leaves open, and we fix by convention.** The order in which
fold alternatives are tried: `fold` applies R2 *"possibly, in a
nondeterministic way"* (Definition 3), and §8 calls Folding's nondeterminism
*"the most critical issue"*. The reference takes them in background-rule order,
with `dom(X)` last. Where a fidelity figure depends on that order it has to say
so; the paper's Prolog implementation (Zenodo) would settle it.

**Effect on reported results.** Sets 04/05 scored fidelity against the
previous reference on these 12 problems, and their probe harvest would now visit
different states there.

## Phase 9 — Training each step on its own (Oct 2026, arm S2)

**Where the SFT ablation left it** (5d7f0bc). The trace arm learnt the trace's
form, not its decisions: its first line-18 verdict is right on 107/200 test
problems, what a guess that ignores the problem expects (107.25), and exact is
89/200.

**The suggestion**, from the thesis supervisors: train the model to execute each step on its
own, RoLe first, then Gen. Only that arm, S2, is built: RoLe is one example and
each step of Gen (lines 16, 17, 18, 36, 38, 44) another, each counting once in
the loss.

- The reference keeps Algorithm 1's control flow (the queue, line 39's
  backtracking, mint naming) and asks its seven computed steps (lines 8, 16, 17,
  18, 36, 38, 44) through an oracle hook; without one it is unchanged bit for
  bit. Each ASP step is one clingo call on that line's framework, checked
  against Definition 2 and an independent stable-extension checker on 2,316
  problems.
- The prompt states the orders the paper leaves open: facts in T order, then
  domain order; folds in background order, `dom(X)` last, never by learnt rules.
- Lines 16 and 18 are answered with the failing examples, then the verdict;
  line 18 is also asked at the folds the search does not reach, `dom(X)`
  excepted (3,344 train rows).
- A run stops on an unusable answer or a cap (200 calls, 64 learnt rules) and
  then has no answer. Illegal list items are dropped and counted; strict exact
  counts a run with any as wrong.
- Evaluated on its own run (chained) and at the reference's states (gold),
  beside a baseline that reads only the step's position.

**D5**, registered in 1395f61 before any S2 output: on v1 test, supported if the
chained first-check and R3 balanced accuracies are ≥ 0.80 and exact beats
89/200 with McNemar p < 0.05; refuted if the first check is ≤ 0.60; otherwise
intermediate. A run that stops before its first check, or without an answer, is
a miss. Expected even if supported: t9 `reuse_ok` near 0, since its deciding
answer (yes, at line 38 on a RoLe fact) never occurs in training.

**N1, an open reading of line 18.** When the test at line 18 succeeds, the
printed Algorithm 1 adds nothing to R: R grows only at line 20, with ρd, inside
the then-branch. The prose (p. 3450) calls ⟨R ∪ Rl ∪ {ρf}, A, ¯⟩ "the current
ABA framework" at that test; the reference keeps ρf, following the prose.

**Corrected before registration:** "about 4× the trace arm's tokens" counted
the tokens read; the supervised target tokens are 0.62× (299k against 482k).

**Outcome: D5 supported** ([`COMPARISON_STEP.md`](../results/sft-step/COMPARISON_STEP.md);
the samples were read by hand first, and the three criteria recomputed from the raw
scores). Training ran at f23ca02, the evaluations at 19bda3d, which changes only
`cluster/setup_env.sh`.

- On v1 test the first line-18 verdict is right on 200/200 (the position
  baseline gets 117/200), R3 balanced is 1.000, and exact is 198/200 against 89
  (109 to 0, p = 3.1e-33). Both misses start with a RoLe answer with one or two
  facts too many. At the reference's states every kind of step is at least 0.98
  on test, and `t8_decoy` is 50/50.
- Exact on test does not separate S2 from the endpoint arm (198 against 200,
  p = 0.5); renamed, S2 keeps more (111 against 90 of 200, p = 0.009).
- `t9_reuse` is 0/50, and every run first goes wrong at line 38: `reuse_ok`
  answers "no" on the RoLe fact, as expected; `reuse_fails` answers "yes" on the
  contrary fact, which was not expected.
- Renaming drops exact from 248 to 150 of 300. In 112 of the 129 renamed test
  runs that go wrong, the first wrong step is the fold-candidate list; RoLe
  (198/200) and the first verdict (192/200) survive.
- Table 1 is 0/16, with RoLe right on 6 of 16 at the reference's states.
- The untrained model under the same prompts gives no usable answer at 88% of
  the reference's states (prose cut by the token budgets), so its run shows only
  that the answer format is not zero-shot.

The confounds stated with D5 stand: S2 reads 4.5× the trace arm's tokens per
epoch on 0.62× its target tokens, its prompts carry no definitions block or step
history, the lines-16/18 targets name the failing examples, and it has 3,344
extra line-18 rows. One seed.

**Noted after the results** (docs/FINDINGS.md):

- **A further confound: the controller.** The reference keeps the control flow, writes the
  state into every prompt, applies every answer and drops illegal answer items. So every
  comparison of S2 with the other arms mixes per-step supervision with that controller.
- **Two criteria do not separate S2 from memorising.** The endpoint arm also reaches R3
  balanced 1.00 and exact 200/200 on test, so neither criterion separates S2 from an arm
  that memorises. Only the first line-18 verdict does.
- **The renamed gain needs a qualifier.** Renamed, 8 of S2's 111 exact runs rely on dropped
  illegal items. Under strict exact it is 103 against the endpoint's 90 (34 to 21,
  p = 0.105).
- **Line 16 rests on few states.** Of the 444 test states of later RoLe facts, 404 are
  "yes" and the 40 "no" are all in `t5_twopath`, so the line-16 result rests on few
  discriminating states.

**Where the runs first go wrong** (`analysis/s2_errors.py`). Each run is replayed from its
recorded calls, and every call is judged against the reference's answer at the same state.

- **Test.**
  - 193 of 200 runs have every call right.
  - No yes/no decision taken at the reference's state is wrong.
  - Three runs drop a fold candidate that the search never tests, and stay exact.
  - Four start with a wrong RoLe answer; two of them are still exact.
- **Renaming.** In 112 of the 129 renamed test runs with a wrong call, the first wrong call
  is the fold-candidate list.
  - All 2,602 training fold lists are in alphabetical order, because the anonymiser names
    predicates by first appearance. So training cannot tell the order the prompt states
    (background order) from alphabetical order.
  - Renamed, the two orders differ on 251 of 398 test calls. There S2 is right on 68,
    against 135 of the 147 calls where the orders agree. Of the other 183:
    - only the first candidate dropped: 76;
    - other drops: 69;
    - the right set in alphabetical order: 23;
    - other: 15.
  - Names never seen as candidates in training are dropped slightly more often than seen
    ones: 121/570 against 58/421.
- **`t9_reuse`.** Every run first goes wrong at line 38, at the reference's state, and
  answers as training answers that state's shape.
  - In training, line 38 says yes exactly when a contrary fact is guarded by a background
    assumption (150 rows). It says no for a contrary fact with a minted assumption (652)
    and for a RoLe fact with a background one (118).
  - `reuse_ok` needs yes on a RoLe fact and gets no (25/25).
  - `reuse_fails` needs no on a contrary fact with a background assumption and gets yes
    (25/25).
  - On test, the position baseline gets all 128 line-38 states, so nothing in distribution
    shows S2 computing line 38.
- **Table 1.** The first wrong call is RoLe in 10 runs, line 16 in 2, line 18 in 2, and the
  contrary facts and the fold list in 1 each.
  - Each Table 1 problem lies outside the range of v1's training problems somewhere:
    - assumptions: 0 or 3 (training 1–2);
    - constants: 2, 5, 7 or 40 (training 6, 8, 10 or 12);
    - binary predicates (none in training);
    - |T| = 4 (training ≤ 2);
    - rules with a body: 0 or 3 (training 1–2);
    - facts written `p(X) :- X = t` (problems 01 and 02).
  - In 03, 05 and 07 the reference's RoLe answer has a predicate other than the examples'.
    No training RoLe target does (0/1,500).

So line 18 is the step S2 is shown to compute: its first verdict is right on 200/200
against the position baseline's 117, and on 192/200 renamed. Lines 17 and 38 cannot be
judged in distribution: training separates neither the fold order from alphabetical order
nor line 38's answer from the state's shape. Table 1 measures transfer, not a step.

**Line 18 off the path, fixed before the run** (seed 0; `eval_stepwise.py --protocol
gold --extra`, the last step of `cluster/stepwise_sft.sbatch`). S2 is asked line 18 at
every non-dom fold its search skips, at the reference's state: 448 test states in 181
problems (94 yes), 145 held-out (38 yes), 38 in Table 1 (all no). Their prompts are built
as on the path, so nothing marks them. S2 trained on 3,344 such rows from the train
problems.

- Floors on test:
  - always no is balanced 0.5 (accuracy 354/448);
  - the position rule voting on every train line-18 row is 0.596 (358/448).
  - The registered rule votes on visited rows only and gets 0.447: it says yes at rank 1,
    where a visited check is yes 712 times out of 770.
- Reading on test:
  - balanced ≥ 0.80: S2 computes line 18 off the path;
  - ≤ 0.60: its line-18 answers depend on where the state falls, and the first-check
    result holds on the path only;
  - intermediate otherwise.
  - Expected: ≥ 0.95, with the failing examples right on ≥ 0.90 (every test state has one
    answer set).
- Held-out and Table 1 are descriptive, as is seed 1's run.
- Which folds are skipped follows the reference's fold order, which Definition 3 leaves
  open (Phase 8).

**Seed 1** ([`s2_s1/COMPARISON_STEP.md`](../results/sft-step/s2_s1/COMPARISON_STEP.md) and
`analysis/s2_errors.py --s2 s2_s1`). This run is descriptive.

- **Setup.** It uses the same code, corpus, hyperparameters and decoding as seed 0, with its
  own problem order and LoRA initialisation (job 73305, trained and evaluated at 4fbd8ab).
  The evaluation code is unchanged since seed 0's evaluation at 19bda3d.
- **Checks.**
  - The samples were read by hand first.
  - Every number in the report was then recomputed from the raw files.
  - The training and evaluation manifests differ from seed 0's only in the seed, the order
    hashes, the adapter and the code revision.

- D5's criteria hold again:
  - the first line-18 verdict is right on 199/200 (balanced 0.995);
  - R3 balanced is 1.000;
  - exact is 198/200 against 89 (109 to 0, p = 3.1e-33).
- Every S2 count in the README's table equals seed 0's: test 198/200, `t8_decoy` 50/50,
  `t9_reuse` 0/50, Table 1 0/16, and original → renamed 248 → 150.
- On v1 test, the two seeds produce the same run, call for call, on 190 of 200 problems.
  On 17 of these, the RoLe facts are listed in another order.
- No test problem is missed by both seeds:
  - seed 1 misses `t3_domain_0030`, whose RoLe answer has an extra fact;
  - it also misses `t5_twopath_0036`, whose first line-18 verdict is wrong at the
    reference's state ("fails: none. yes." where `r1(c)` fails);
  - seed 0 misses `t4_nested_0036` and `t5_twopath_0016`, both RoLe answers with extra
    facts.
- Seed 0's mechanisms recur:
  - every `t9_reuse` run first goes wrong at line 38, with the same answer by state shape
    (identical per problem);
  - on test, line 38 is 128/128 for both S2 and the position baseline;
  - renamed, the first wrong call is the fold list in 104 of 121 broken test runs (seed 0:
    112 of 129);
  - where background and alphabetical orders differ, the list is right on 79 of 231 calls
    (seed 0: 68 of 251); where they agree, on 127 of 143 (135 of 147).
- Renamed, the totals hide the differences:
  - 40 of the 200 test problems change outcome between the seeds (21 against 19);
  - 12 of seed 1's renamed runs stop, against none of seed 0's;
  - 11 of them stop on a fold list whose every body has the fact's constant in place of X
    (`c_alpha_0(X) :- r(g).`), and 1 on a malformed contrary fact.

So the second seed confirms the in-distribution result and its limits. What varies between
seeds is which renamed problems fail, and how.

**Line 18 off the path: outcome** (`results/sft-step/s2/gold_extra/` and
`results/sft-step/s2_s1/gold_extra/`). The samples and 20 more states per seed were read by
hand first. Both seeds meet the reading fixed above.

- **Test** (448 states, 94 yes):
  - balanced 0.995 in seed 0 (447/448) and 0.993 in seed 1 (446/448);
  - the position floor gets 0.596 (358/448);
  - the failing examples are right on 444 and 442 of the 448 states.
  - The three wrong verdicts are on different problems: two say no where the truth is
    yes, one the reverse.
  - Every wrong witness that comes with a right verdict is off by one example.
- **Held-out:** 145/145 in both seeds, against a floor of balanced 0.5.
- **Table 1** (38 states, all no): 22 and 24 of 38, against the floor's 26. The transfer
  failure seen on the path holds off it too. One seed-1 answer, a list of 21 failing
  examples, runs past line 18's 96-token budget.

So S2 computes line 18 at states its search never reaches, in distribution: it trained on
such states, but of other problems.

## Phase 10 — Step probes v3 (Oct 2026)

Written before the run. Stage 1 of [FINDINGS.md](FINDINGS.md), the prompted models, rests
on set 05 (probe prompts v2), and three of its prompts carry a measured defect.

1. **`check` (line 18): "the examples that fail" is never defined.** The models read it as
   "the negative examples". Of the NO answers, the listed examples are exactly the negative
   examples on 180 of 186 for 32B under v2, 181 for 7B and 157 for 3B. The same pattern is
   already in v1 (32B: 160 of 186), so v2's shorter preamble is not its only cause. v3
   defines a failing example as the scorer does: a positive example that no stable extension
   accepts, or a negative example that every stable extension accepts.
2. **`role` (line 8): v2's added clause draws facts for contrary predicates.** The clause
   was "in particular for the contrary of an assumption". Under v2, 14B writes 195 such
   wrong facts and 32B 143, against 1 each under v1. The gold answers hold one such fact in
   345. v3 states line 4's restriction instead: facts only for predicates in T.
3. **`introduce` (lines 36–44): the prompt is not Definition 4.** v2 says "if the
   background already declares an assumption relative to this body" and never defines
   "relative". v3 states Definition 4 (a rule H′ ← B, α(X) among the current rules) and
   lines 36 and 41: reuse a relative assumption when one exists, and a new assumption with
   a new predicate only when none does. It no longer says "so that a solution can be
   recovered", because at line 36 the reuse is taken even when line 38 then fails.

`fold` and `subsume` are unchanged. Their failures are mixed (a wrong predicate, an
equality left in place, bodies of several atoms) and point to no single wording.

**`introduce` scored as printed.** The scorer credited a failed reuse whenever a new
assumption would have worked: the line-41 fallback that Phase 8 found is not in the paper.
An answer is now right iff it guards the folded rule and takes the branch Algorithm 1
takes:

- line 36's, when an assumption relative to the body exists: that assumption, its contrary
  unchanged;
- line 41's, only when none exists: a new predicate for the assumption and for its contrary.

Checked on the benchmark's states, outside the test suite:

- the reference's own decision is right on 166/166;
- a new assumption where line 36 reuses is right on 0/81;
- reusing an assumption that is not relative is right on 0/166.

The reference tests relativity by a subset of the body, where Definition 4 asks for the
body itself. The two never differ on a visited state: 209 benchmark states, 412 in the
first 300 v1 problems, 312 in Table 1.

**The probe set changes with the reference.** Probes are drawn from the states the
reference visits, and Phase 8 changed them: 335 of the 780 set-05 probes per model are not
in the v3 set. In particular, 81 of the 166 `introduce` states now take line 36's branch
(2.9% in set 05), because every defeasible problem now reaches line 36 on its contrary
fact. So v3 against set 05 mixes the change of prompt with the change of states. The v3
figures are read against floors measured on the v3 set. Sets 04 and 05 are not rescored,
because `rescore.py` would rebuild their probes from the current reference.

**Floors on the v3 set** (`analysis/null_baselines.py`): `role` 0, `fold` 0, `check`
0.633 balanced, `subsume` 0.663, `introduce` 0.855 balanced. The `introduce` floor reuses
the last assumption the state lists as introduced, and otherwise a new one; it reads no
rule body. Always answering a new assumption gets 0.500.

**The run** repeats set 05's probe half: Qwen2.5 3B, 7B, 14B and 32B and Mistral-7B, all
4-bit; the same 103 problems (`--benchmark 20`, seed 42); two probes per kind and problem;
greedy decoding, 512 tokens.

**Reading, fixed before the run.**

- A model performs a step above its floor iff the 95% bootstrap interval over problems of
  its metric lies above the floor (`null_baselines.py --set`). The metrics are F1 for
  `role`, accuracy for `fold`, and balanced accuracy for `check`, `subsume` and
  `introduce`.
- `check` is line 18, the step stage 1 of FINDINGS turns on. If no model's interval lies
  above 0.633, stage 1 stands with the prompt defect removed. If one does, stage 1 is
  rewritten: that prompted model performs line 18 above its floor.
- Reported beside the metrics: the NO answers to `check` that list exactly the negative
  examples, and the `role` facts for contrary predicates.
- At least 20 rows across kinds and models are read by hand before any aggregate.
- A smaller model that outranks a larger one on a step needs a mechanism.

**Outcome** ([`experiments/06_probes_v3`](../experiments/06_probes_v3/MANIFEST.md), jobs
73946–73950). 25 rows, one per model and probe, were read by hand first, and every verdict
matched the raw answer. All 845 probes per model were answered, with no error and no
answer at the token cap.

- **As registered.** No model's interval lies above its floor on `check` (0.633),
  `subsume` (0.663) or `introduce` (0.855). On `role` and `fold`, whose registered floors
  were 0, 14B, 32B and Mistral lie above on `role`, and every model on `fold`.
- **Stronger floors, found after the run.** Three registered policies were not the best
  no-reasoning ones:
  - `role`: writing one fact per positive example scores F1 0.994. RoLe's answer is the
    positive examples on 102 of the 103 problems, as on every v1 problem (Phase 11).
    Every right `role` answer of every model is that copy.
  - `fold`: folding onto dom(X) scores 1.000. Since Phase 8, dom(X) is a legal fold at
    every state (Definition 3), and the probe accepts any legal fold.
  - `subsume`: YES iff the state lists a learnt rule with no equality scores 0.762.

  Against these, no model performs any of the five steps above a policy that does no
  reasoning. `null_baselines.py` now takes the best of its policies as the floor, and
  still prints the registered ones.
- **Line 18.** The defined failing example changed nothing for 3B, 7B and 32B. They answer
  NO to all 186 probes and list exactly the negative examples on 172, 177 and 168 (32B:
  160 under v1, 180 under v2). Mistral answers YES to all 186. 14B answers NO on 131,
  lists the negative examples on 28 (v2: 114), and reaches 0.582 [0.527, 0.636]: above a
  constant answer, below the floor.
- **Lines 36 and 41.** Every model is below 0.500, the score of always introducing a new
  assumption. Each follows one habit (the set's MANIFEST): Mistral always introduces a new
  assumption; 3B reuses what the state lists; 32B reuses a background assumption that is
  not relative where line 41 introduces one, and introduces a new one where line 36 reuses.
- **Line 8.** On the same 103 probes as set 05, dropping v2's clause raised F1 from 0.321
  to 0.736 (14B), from 0.688 to 0.744 (32B) and from 0.260 to 0.542 (Mistral). Facts for
  contrary predicates fell from 195 to 83 (14B) and from 143 to 92 (32B), without
  vanishing: T itself contains those predicates.
- **Confound rule.** Smaller models outrank larger ones in three cases: 14B above 32B on `check`;
  3B above 7B, 14B and 32B on `subsume`; Mistral and 3B above 7B, 14B and 32B on
  `introduce`. Each time the larger models give a constant answer, or follow a habit that
  is wrong on both of line 36's branches; none is a smaller model computing the step.

So stage 1 of FINDINGS stands. It now rests on prompts without the measured defects, and on
the corrected reference's states.

## Phase 11 — Why no arm solves Table 1 (Oct 2026)

`analysis/answer_shapes.py` compares the reference's answers with the shape of v1's
training answers, and reads what each arm writes. It found two more properties of corpus
v1:

- **RoLe's answer is the positive examples.** On every v1 problem (1,500 of 1,500 training
  problems, and every test and held-out problem), line 8's answer is one fact per positive
  example. So line 8, like line 17's order and line 38, is answered by a shortcut the data
  leave open, and its in-distribution accuracy shows only copying.
- **New assumptions never nest.** No training answer introduces an assumption in the rule
  for the contrary of another introduced assumption.

The algorithm's run on every Table 1 problem has one of the two. On five it nests a new
assumption (flies, flies_birds_planes, nixon_diamond, tax_law, acute). On three, RoLe has
facts for a predicate other than the examples' (innocent, nixon_diamond_2, tax_law_2). The endpoint and trace
arms never nest. At RoLe, the trace arm and S2 (at the reference's states) write the
positive examples on all six prompts where the algorithm does not. Written up in
[FINDINGS.md](FINDINGS.md), "Table 1: why no arm solves the paper's problems".

## Phase 12 — Rule grammar (Oct 2026)

The answer parser (`_parse_rule_line` in `src/aba_prompts.py`) read any line containing
`:-` as a rule, and any other line of the NEW RULES block as a fact. So explanation prose
became rules, and a contrary written under NEW RULES (`u(X) defeated_by t(X)`) became a
fact whose head is an assumption. Both made the answer ill-formed. In set 05, 1,361 of
the 6,180 end-to-end answers have explanation lines containing `:-`.

- **Fix.** A rule's head must be an atom, and each body element an atom, a `not` atom or
  a comparison; a trailing `% comment` is stripped. Any other line is not a rule. It is
  skipped, and a repair note counts the skipped lines that contain `:-`. A contrary
  written under NEW RULES is dropped, not recovered. Every rule the code generates
  (benchmark, corpus v1 and v1-permuted, Table 1, the step targets) parses as before, and
  the gold-target control (`python -m src.aba_score --control`) still passes on v1 and
  v1-permuted.
- **Rescored.** Every registered fine-tuning result was rescored: the three SFT arms on
  v1 and permuted, S2 (seeds 0 and 1) under all four protocols, and the untrained model at
  the reference's states.
  - **What moved: only the untrained model's two endpoint runs.**
    - 38 of its 616 answers lose rules: 65 prose lines with `:-`, 26 contraries and 18
      prose lines read as facts. The new grammar adds no rule anywhere.
    - 45 score rows change, 29 of them in label, all from `illformed`: 22 become
      `not_a_solution`, 3 `ok`, 3 `valid_but_degenerate` and 1 `parse_error`.
    - Valid becomes true on 6 rows and clean on 3. Exact moves on none.
  - **What did not move:**
    - No fine-tuned arm's answer parses differently.
    - No S2 step parses differently: the replays and `analysis/s2_errors.py` are
      unchanged.
    - No probe row of sets 04–06 scores differently.
    - The floors, the registered decisions, the McNemar tests and the invariance
      verdicts are unchanged.
  - **Trace fidelity.** The frozen trace-fidelity score moves on 21 of the untrained
    model's rows, because it reads the parsed answer.
- **Moved figures** (the untrained model, endpoint scoring; Table 1 valid stays 1/16):

  | set | figure | before | after |
  | --- | --- | --- | --- |
  | v1 test | parsed | 200/200 | 199/200 |
  | v1 test | valid | 26/200 | 27/200 |
  | v1 test | clean | 15/200 | 16/200 |
  | v1 test | agreement | 0.11 | 0.12 |
  | v1 test | R3 balanced | 0.51 | 0.50 |
  | v1 `t9_reuse` reuse_ok | valid, clean | 4/25, 3/25 | 5/25, 4/25 |
  | permuted test | valid | 8/200 | 10/200 |
  | permuted test | agreement | 0.02 | 0.03 |
  | permuted test | R3 balanced | 0.48 | 0.49 |
  | permuted `t8_decoy` key_first | valid | 2/25 | 3/25 |
  | permuted `t8_decoy`, both halves | R3 balanced | 0.44 | 0.46 |
  | permuted `t9_reuse` reuse_ok | valid, clean | 7/25, 3/25 | 8/25, 4/25 |
  | Table 1 | ill-formed | 8/16 | 7/16 |

The end-to-end prompting sets 00–05 were scored under the old grammar and are not
rescored here.

## Phase 13 — The end-to-end study, posed whole (Oct 2026)

**Why the split was withdrawn.** The end-to-end prompting study (sets 00–03 and the
end-to-end half of set 05) did not pose problems whole. It hid part of each problem's
examples from the prompt: `split_problem_examples`, test ratio 0.34, 30.4% of the
benchmark's examples. A `max(1, …)` floor hid one example per list even at ratio 0.
The answers were then scored on the hidden examples: gen@k, det@k and the overfit gap.

- **Why that is wrong.** Definition 1 defines a solution relative to the examples
  given, and Algorithm 1 is run on the whole problem. Hiding examples changes the
  problem: it turned 26–58% of the defeasible problems monotonic (docs/CORPUS.md). It
  also asks the model for something the algorithm is never asked.
- **Consequence.** Those figures measure neither correctness by Definition 1 nor
  fidelity to the algorithm. The sets stay as the as-run record, marked superseded, and
  `rescore.py` refuses them.
- **Unaffected.** The step probes (sets 04–06) and the fine-tuning arms always posed
  problems whole.

**The instrument that replaces it.**

- **Scoring.** Every answer is scored by `src/aba_score.py`, the fine-tuning scorer,
  against the algorithm's run on the same problem:
  - valid and clean (Definition 1 on the posed examples);
  - exact (the algorithm's answer, up to assumption names and body order);
  - agreement off the examples, R2 bodies and R3.

  The step audit is off: it misfires on free prose.
- **Instrument control.** Before any model call, the algorithm's answer must score
  clean and exact, and RoLe's facts valid but not clean. Both hold on all 103 problems.
- **Provenance.** Each sample's seed is derived from the run seed, the problem, the mode
  and the index, so a resumed run draws the same samples. 4-bit kernels are not bitwise
  deterministic: the seed fixes the draw, not the output.
- **The run record.** The run's `summary.json` records:
  - the prompt version (v4) and the hash of each mode's prompt;
  - the code revision, the model revision and the package versions;
  - the decoding settings and the dataset;
  - the hash of the references.

  `rescore.py` rebuilds a run from that record.
- **Retired analyses.** `analysis/conformance.py` and `analysis/step_fidelity.py`
  studied only the split runs. The score card carries R1 (ground rules), R2 (bodies)
  and R3 (defeasibility). Their R4 finding stands:
  - **R4 is unmeasured end to end.** Of set 05's 1,466 answers with ground facts, 1,449
    are not solutions, so only 17 pose R4's question, too few to score.
  - **The reference does not reach an R4 fixpoint.** It tests subsumption once per fact,
    when the fact is popped (line 16), and never retests a rule that a later assumption
    introduction makes redundant. So 8 of the 103 answers in set 05's symbolic traces
    keep a removable intensional rule, and a removable rule is a divergence only when
    it is a ground fact.

**Floors** (`analysis/null_baselines.py --end-to-end`). The benchmark has 103
problems (seed 42, `--benchmark 20`, anonymised). The floors were computed twice,
with identical results.

| policy | valid@1 | clean@k | exact@k | agreement | R3 balanced |
| --- | --- | --- | --- | --- | --- |
| empty answer | 0.000 | 0.000 | 0.000 | 0.000 | 0.500 |
| RoLe's facts | 1.000 | 0.000 | 0.000 | 0.333 | 0.500 |
| positional rule | 0.777 | **0.777** | 0.000 | **1.000** | 0.500 |
| one answer for all (leave one out) | 0.417 | 0.417 | **0.388** | 0.350 | 0.500 |
| tier constant (leave one out), not a floor | 0.951 | 0.951 | 0.951 | 0.967 | 1.000 |

The policies:

- **Positional rule:** `t(X) :- p(X), a.` Here t is the first positive example's
  predicate, p the first listed background head other than t and dom, and a the first
  background assumption. It is clean on all of t1–t4, but it is never the algorithm's
  answer: the algorithm introduces a new assumption with its contrary rule, where this
  rule reuses the background one.
- **One answer for all:** the commonest algorithm's answer among the other 102
  problems.
- **Without t5,** the clean@k floor is 0.964 and the exact@k floor 0.482.

**The benchmark has 9 distinct answers.** Anonymisation names by first appearance, so:

- t2, t3 and t4 each have one answer string across their 20 problems;
- t1 has two answers (18 and 2 problems), t5 two (15 and 5), and the 3 built-ins three;
- t5's 20 problems share one structure; the other tiers have 19–20 structures each.

The tier constant writes the commonest answer of the problem's own tier. It is not a
floor, because it needs the tier and the other problems' answers, which no model is
given. It measures what exact@k means here: whether the model writes its tier's one
answer.

**Registered reading** (written before the run, set 07):

1. **Primary metrics: clean@k and exact@k.** A model × mode cell is *above* iff its
   Wilson 95% lower bound exceeds the floor: 0.777 for clean@k, 0.388 for exact@k
   (without t5: 0.964 and 0.482).
2. **Secondary metrics,** none of which can show reasoning on this benchmark:
   - valid@1 has a floor of 1.000 (RoLe's facts);
   - agreement has a floor of 1.000 and is undefined on 43 of the 103 problems, which
     have no atoms outside the examples;
   - R3 balanced is read against 0.500.
3. **Truncation.** A cell with more than 10% of its samples at the token cap is a lower
   bound.
4. **Hand-reading.** Each model's `sample.md` (20 rows, each beside the algorithm's
   answer) is read before any aggregate.
5. **Size ordering.** A smaller model outranking a larger one is reported with a
   mechanism, or as unexplained.
6. **t5** is reported with and without it.
7. **Independence.** The intervals treat problems as independent. They are not:
   tiers t2–t4 share one answer each, and t5 one structure.
8. **Advantage to the model.** Each floor is one deterministic answer per problem,
   while a model gets k = 3 samples, so @k favours the model. A cell that is not above
   at @k would not be above at @1.
9. **No comparison with sets 00–05.** They posed a different problem.
10. **The finding if nothing is above.** If no cell is above on either primary metric,
    that is the finding.

## Pending

- Decide the `apply_folding` scope question (Phase 6, item 4); measure how many
  extra legal folds appear when folding against `R ∪ learnt`.
- Make the `role` and `fold` probes discriminate (Phase 10): problems whose RoLe answer
  is not the positive examples, and a fold probe that folding onto dom(X) does not pass
  trivially.
- Check the fold-order convention against the Zenodo implementation.
- Settle N1 (Phase 9). When line 18's test succeeds, the printed algorithm adds ρf
  nowhere, while the reference keeps it, following the prose (p. 3450).
- Line 8 and backtracking. The paper (p. 3450) says the #minimize directive "will also
  minimize the set of alternative answer sets that are computed at line 8 in case of
  backtracking". The reference computes RoLe once, and a Gen failure ends the run. Gen
  succeeds from the first RoLe answer on all 2,000 v1 problems and on every Table 1
  problem, so no figure depends on it. Decide whether the reference should backtrack into
  line 8.
