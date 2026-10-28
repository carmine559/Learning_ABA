# What the experiments answer

**Research question.** Can a large language model execute ASP-ABAlearnB, Algorithm 1 of De
Angelis, Proietti & Toni (ECAI 2024, p. 3449)? Models are scored on how faithfully they
replicate the algorithm's steps and decisions. They are never scored on whether they do
better than it.

## The answer in brief

- **What S2 does.** Fine-tuned on each step separately (arm S2), an LLM matches Algorithm 1
  at every step, under two conditions: the problems are like its training problems, and
  the reference supplies the control flow. On v1 test, every kind of step is right on at
  least 98% of the reference's states.
- **What it is shown to compute.** Of these steps, one is shown to be computed rather than
  read off cues: line 18's test of the folded rule.
  - The first line-18 verdict is right on 200/200; a rule that reads only the step's
    position gets 117/200.
  - Renamed, it is right on 192/200.
  - At fold candidates the search never tests, it is right on 447/448; the position floor
    gets 358.
  - All of this holds on a second seed.
- **What it answers by shortcuts.** Line 16 is right everywhere too, but the state's shape
  decides almost all of its test states. Line 8, line 17's order and line 38 are answered
  by shortcuts that the training data leave open. On every v1 problem, for instance, line
  8's answer is one fact per positive example.
- **What it does not show.** It does not show that the model runs the algorithm on its own.
  The steps do not transfer:
  - `t9_reuse` is 0/50;
  - on the paper's Table 1, no arm is exact and no fine-tuned arm gives a valid answer.
    On each Table 1 problem, the algorithm's answer has a shape that no v1 training answer
    has, and the arms write v1's shapes.
- **The other models do not get that far.** Prompted one step at a time (Qwen2.5 3B–32B,
  Mistral-7B), no model performs any of the five probed steps above a policy that does no
  reasoning. Four of the five answer line 18's test with a constant. The arm fine-tuned
  on whole traces gives a first line-18 verdict at the level of a guess.

## The evidence, in order

### 1. Prompted models (step probes v3, Qwen2.5 3B–32B and Mistral-7B)

Source: [`experiments/06_probes_v3/MANIFEST.md`](../experiments/06_probes_v3/MANIFEST.md).
The reading was fixed before the run (METHOD_HISTORY, Phase 10).

Each probe asks for one decision of Algorithm 1 at a state the reference visits, on 103
problems, with all models at 4-bit. Each is read against the best of the no-reasoning
policies measured on the same probes.

- **No model performs any of the five steps above a policy that does no reasoning.**
  - *Line 18* (`check`): the floor is 0.633 balanced. 3B, 7B, 32B and Mistral answer one
    constant (0.500). 14B reaches 0.582 [0.527, 0.636].
  - *Line 16* (`subsume`): the floor is 0.762, and every model is between 0.500 and 0.647.
  - *Lines 36 and 41* (`introduce`, scored as printed): the floor is 0.855. Every model is
    below 0.500, the score of always introducing a new assumption, because each follows
    one habit instead of Definition 4.
  - *Line 8* (`role`) and *line 17* (`fold`) do not discriminate on these problems.
    Copying the positive examples scores F1 0.994, and folding onto dom(X), legal at
    every state, scores 1.000. 14B and 32B reach F1 0.74 on `role`, and every one of their
    right answers is that copy. The best `fold` score is 0.403.
- **The failure is not the prompt's.** Probe prompts v3 removed three defects measured in
  v2's answers. Line 18 still fails the same way: 3B, 7B and 32B answer NO to every
  `check` probe, and list exactly the negative examples on 172, 177 and 168 of 186. They
  do so although the prompt now says that being a negative example does not make an
  example fail; 32B did the same under v1.
- **One earlier exception.** Under probe prompts v1 (set 04), 14B reached 0.780 on line
  18, above that set's floor of 0.681. v1's prompt carried two defects (METHOD_HISTORY,
  Phase 5), and neither v2 nor v3 reproduces the result.
- **Caveats.** The intervals treat the 103 problems as independent; 20 of them are one
  structure in 20 surface forms. The earlier end-to-end prompting figures (sets 00–03,
  half of 05) hid part of each problem's examples and are superseded. The re-run with
  every problem posed whole (set 07) is read by rules registered before it ran
  (METHOD_HISTORY, Phase 13).

### 2. Fine-tuning on the answer or on the whole trace ([`results/sft/COMPARISON.md`](../results/sft/COMPARISON.md))

This is Qwen2.5-7B-Instruct with LoRA, on corpus v1. The rules for reading the comparison
were fixed before the trace arm was scored.

- **The endpoint arm** is trained on the final framework only.
  - It is exact on 200/200 test problems. But the test answers are 15 distinct strings, all
    of them training answers.
  - It is exact on 225/225 prompts whose answer occurs in training, and on 0/91 others.
  - On `t8_decoy` it gets 25/50: all 25 `decoy_first` problems, where the template answer
    is right, and none of the 25 `key_first` ones.
- **The trace arm** is trained on the algorithm's decisions, then the framework.
  - It writes the trace's form: RoLe facts 199/200, fold candidates 302/333.
  - Its first line-18 verdict is right on 107/200. A guess that knows the tier but not the
    problem expects 107.25.
  - It is exact on 89/200, below a constant answer's 100/200.

So the trace arm learnt the trace's format, but not the test at line 18.

### 3. Training each step on its own: arm S2, the final runs

**Setup.** The reference keeps Algorithm 1's control flow: the queue and its fact order,
the choice points, line 39's backtracking and the naming of new assumptions. It writes the
current state into every prompt and applies every answer. It also drops answer items that
are not legal, such as fold candidates outside its own list. The model answers the seven
computed steps: lines 8, 16, 17, 18, 36, 38 and 44.

Training has one row per step of the reference's run, plus 3,344 line-18 rows at fold
candidates its search skips.

#### D5, the registered criterion: seed 0 ([`COMPARISON_STEP.md`](../results/sft-step/COMPARISON_STEP.md))

D5 is the reading for S2, fixed in `sft/compare_step.py` before any S2 output existed. It is
supported if, on v1 test, three things hold: the first line-18 verdict and the R3 decision
are each balanced ≥ 0.80, and exact beats the trace arm's 89/200 with McNemar p < 0.05.

*Does per-step supervision make the model take the algorithm's decisions?*

On v1 test:

- **The first line-18 verdict** is right on 200/200, against the position baseline's 117/200.
  This is the criterion that separates taking the decision from recalling an answer.
- **The other two criteria** are R3 and exact. R3 is balanced 1.000: the answer introduces
  an assumption exactly when the reference's does. Exact is 198/200, against the trace
  arm's 89 (109 to 0, p = 3.1e-33). These two do not separate S2 from memorising: the
  endpoint arm reaches R3 1.00 and exact 200/200 too (0 to 2, p = 0.5).
- **At the reference's states,** every kind of step is right on at least 0.98.
  - Line 16 is right on all 444 states of later RoLe facts.
  - But 404 of these are "yes" and 40 are "no", all 40 in `t5_twopath`. So few of them
    discriminate.

#### Where the runs first go wrong (`analysis/s2_errors.py`)

*Where does it fail, and why?* Where training leaves a shortcut.

- **Line 17.** All 2,602 training fold lists are in alphabetical order.
  - Renamed, the fold list is the first call that departs from the reference in 112 of the
    129 test runs with a wrong call (seed 0; seed 1: 104 of 121).
  - Where background and alphabetical order differ, it is right on 68 of 251 calls (seed 1:
    79 of 231). Where they agree, it is right on 135 of 147.
  - Most errors drop candidates. The right set in alphabetical order appears on 23 calls.
- **Line 38.** The training answer is fixed by the state's shape, and S2 answers by shape.
  - `t9_reuse` is 0/50.
  - At the reference's held-out states, line 38 is balanced 0.375, against the position
    baseline's 0.5.
  - On test it is 128/128, but so is the position rule.
- **RoLe (line 8)** is where the in-distribution misses start: both of seed 0's test misses,
  one of seed 1's, and 10 of the 16 Table 1 runs (seed 0). On every v1 problem, RoLe's
  answer is one fact per positive example.

#### Line 18 at fold candidates the search never tests (reading fixed before the run; `results/sft-step/{s2,s2_s1}/gold_extra/`)

*Does the line-18 result depend on where the state falls on the reference's path?* No.

- **Test** (448 states, dom(X) excepted):
  - balanced 0.995, with 447 of the 448 verdicts right;
  - the higher of the position floors fixed before the run is balanced 0.596, right on 358;
  - the failing examples are right on 444;
  - seed 1: balanced 0.993, 446 right.
- **Held-out:** 145/145 in both seeds.
- **Table 1:** 22 and 24 of 38, against the floor's 26.
- **On the reference's path, renamed,** the first line-18 verdict stays right on 192/200
  (seed 0).

This holds in distribution: S2 trained on such states, but of other problems.

#### Seed 1 (descriptive; [`s2_s1/COMPARISON_STEP.md`](../results/sft-step/s2_s1/COMPARISON_STEP.md))

*Is it one lucky seed?* No.

- **The README's counts.** Every S2 count in the README's table is the same: 198/200 test,
  50/50 `t8_decoy`, 0/50 `t9_reuse`, 0/16 Table 1, and 248 → 150 of 300 renamed (test and
  held-out).
- **The first line-18 verdict** is right on 199/200. The miss, `t5_twopath_0036`, is at the
  reference's state.
- **The runs themselves.** After the controller sorts the RoLe facts, the two seeds' runs
  are identical call for call on 190 of the 200 test problems. On 17 of these, the raw
  RoLe answers order the facts differently.
- **Renamed, the outcome depends on the seed.** 40 of the 200 test problems change outcome
  (21 against 19). 12 of seed 1's renamed runs stop (11 test, 1 held-out), against none of
  seed 0's. They stop on fold lists with the fact's constant in every body, a failure that
  seed 0 shows only on Table 1.

#### Against the other arms

- **`t8_decoy`:** S2 50/50, the endpoint arm 25/50, the trace arm 13/50. With v1's fold
  order, `t8_decoy` tests line 18 on the first fold, not line 17's order.
- **Renamed test:** S2 is exact on 111, against the endpoint's 90 (p = 0.009; seed 1: 109,
  p = 0.016). But 8 of the 111 rely on the controller dropping illegal items. Under strict
  exact it is 103 against 90 (p = 0.105; seed 1: p = 0.111).
- **Out of range:** on Table 1 no arm is exact, and no fine-tuned arm gives a valid answer
  (0/16; the untrained model 1/16). The next section explains why.

#### Table 1: why no arm solves the paper's problems (`analysis/answer_shapes.py`)

*Why does no arm solve the paper's own problems?* On each of them, the algorithm's answer
has a shape that v1's training answers never have, and every arm writes v1's shapes.

- **What the algorithm's answers have.** On each of the 8 problems, the algorithm's run
  has one of two things that no v1 training run has:
  - *An exception inside an exception* (flies, flies_birds_planes, nixon_diamond, tax_law,
    acute). The algorithm introduces an assumption in the rule for the contrary of another
    assumption it introduced. In the reference's answer to nixon_diamond, for instance, α0
    and α1 defeat each other through their contraries. No v1 training answer nests a new
    assumption past one level.
  - *RoLe facts that are not the positive examples* (innocent, nixon_diamond_2,
    tax_law_2). Line 8's answer has facts for another learnable predicate: guilty,
    abnormal_quaker, exempt. On every v1 problem, line 8's answer is one fact per positive
    example: 1,500 of 1,500 training problems, and every test and held-out problem.
  - Every problem also lies outside the range of v1's training problems on the input side
    (`analysis/s2_errors.py`). It differs in at least one of these: the number of
    constants, of assumptions or of learnable predicates; binary predicates; facts written
    X = t.
- **What the arms write: v1's shapes.**
  - The endpoint and trace arms never nest a new assumption on Table 1. On nixon_diamond,
    the endpoint arm writes the one-level answer c_α0(X) ← republican(X), which is not a
    solution.
  - The trace arm's RoLe lines are the positive examples on 14 of 16 prompts, including
    all 6 where the algorithm's are not.
  - The untrained model's answers break Definition 1's syntax on 7 of 16 prompts, for
    instance with an assumption as a rule head or a background predicate as a new head.
    One of its 16 answers is valid.
- **S2 at the reference's own states** (seed 0; seed 1 in brackets). Here the reference
  supplies every state, so no earlier error carries forward.
  - Its RoLe answer is the positive examples on all 6 problems where it should not be.
    RoLe is right on 6 of 16 (7).
  - Line 44's contrary facts are right on 5 of 28 (6), and the fold list on 33 of 54 (34).
  - Line 16 is at its position baseline: balanced 0.73 (0.68) against 0.74.
  - Only line 18 stays above its baseline: balanced 0.89 (0.79) against 0.59.
  - In the chained runs, 10 of the 16 first go wrong at RoLe (9).
- **What this shows and does not show.** The failure is one of transfer: where the
  algorithm's answer has a new shape, the arms give one of v1's. It does not show what
  training on such shapes would do; that needs a corpus that contains them. Eight problems
  allow a per-problem account, not statistics.

## What the answer rests on, and what it does not show

- **The controller.** The reference decides which step comes next and does everything listed
  under the setup. The model's answers still choose branches: its verdicts, its reuse list,
  and the order of its fold list. Every comparison of S2 with the other arms mixes per-step
  supervision with this controller, and we have not separated the two.
- **The training differs.** These confounds were registered with D5:
  - S2 reads 4.5× the trace arm's tokens per epoch, but is supervised on 0.62× its target
    tokens;
  - its prompts carry no definitions block and no step history;
  - its line-16 and line-18 targets name the failing examples;
  - it has 3,344 extra line-18 rows.
- **The result is in distribution.** Corpus v1 fixes predicate names and positions per
  tier. The renamed corpus changes names only, so shortcuts based on position survive it.
- **One model, little variation.** One model (Qwen2.5-7B-Instruct), LoRA, greedy decoding.
  S2 has two seeds; the other arms have one each.
- **Readings of the paper built into the reference.**
  - *N1.* When line 18's test succeeds, the printed algorithm adds ρf nowhere: ρ left Rl at
    line 15, and R grows only at line 20. The reference keeps ρf, reading the prose
    (p. 3450), which calls ⟨R ∪ Rl ∪ {ρf}, A, ¯⟩ "the current ABA framework" at that test.
    The question is open (METHOD_HISTORY, Phase 9).
  - *Fold scope.* Folding uses background rules only, where line 17 passes R and the prose
    says Rl \ {ρ}. This is open (METHOD_HISTORY Phase 6, item 4).
  - *Orders the paper leaves open.* Fold candidates are taken in background order, dom(X)
    last (Definition 3); facts in T order, then domain order (line 14). `t8_decoy`'s
    answers, the off-path state set and the line-17 failures under renaming are all
    measured against this fold order. It has not yet been checked against the released
    tool.
  - *Line 8.* The reference computes it once, while the paper also backtracks into line 8's
    alternative answer sets (p. 3450). Gen succeeds from the first RoLe answer on all 2,000
    v1 problems and on every Table 1 problem, so no figure depends on it.

## What would settle more

- **The trace arm run under the same controller, or S2's steps chained by the model
  itself.** This separates per-step supervision from the controller.
- **A corpus whose fold orders, positions and line-38 shapes vary independently of the
  answers, with RoLe answers other than the positive examples and nested new
  assumptions.** This removes the shortcuts S2 took, and tests whether Table 1's shapes
  can be learnt.
- **The fold order, checked against the released tool.**
- **Reinforcement learning.** The registered rule chose the endpoint arm as its base.
  Starting from S2 would be a new decision, and would have to be registered.
