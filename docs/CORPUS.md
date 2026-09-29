# The SFT corpus

`corpus/v1` is the data for the thesis's core ablation. Does training on the
algorithm's **trace** make a model *execute* ASP-ABAlearnB, or does training on
the **endpoint** alone produce answers that pass the checker just as well? Both
arms are trained on the same problems under one prompt (v4-sft, see
[PROMPTS.md](PROMPTS.md)) and differ only in their target.

Built by [`build_corpus.py`](../build_corpus.py) from
[`src/aba_corpus.py`](../src/aba_corpus.py). Only the MANIFEST is committed:
a rebuild is byte-identical given the same code and Clingo version, and the
MANIFEST records the sha256 of every file. See [Reproducing](#reproducing).

| split | problems | used for |
| --- | --- | --- |
| train | 1500 (5 tiers × 300) | SFT, both arms |
| val | 200 (5 tiers × 40) | SFT monitoring, both arms |
| test | 200 (5 tiers × 40) | in-distribution evaluation |
| held-out | 100 (2 tiers × 50) | evaluation where the checker cannot separate answers |

## What a problem is

Each problem is a brave ABA Learning problem in the sense of Definition 1: a
background framework, positive and negative examples, and the learnable
predicates T. The generator draws a hidden target framework and labels
examples from it, but the gold answer is never that target. It is whatever the
reference implementation of Algorithm 1 ([`src/aba_algorithm.py`](../src/aba_algorithm.py))
returns, together with the decisions it took to get there. The generator only
chooses inputs.

Problems are **posed whole**, as Definition 1 poses them: prompt and gold trace
see every example. There is no example-level train/test split inside a
problem. Holding out a third of a problem's examples turned 26–58% of the
defeasible problems monotonic, because the held-out negative was often the one
that required R3. Leakage is prevented *between* problems instead (below).

Every problem is anonymised (predicates `p, q, …`, constants `a, b, …`) before
it is solved, so the gold trace is the trace on the anonymised problem.

## Training tiers (tier spec v2)

| tier | constants | distractor predicates | what it adds |
| --- | --- | --- | --- |
| `t1_base` | 6 | 2 | the smallest problems |
| `t2_noise` | 8 | 4 | more distractor predicates |
| `t3_domain` | 12 (4–5 E+, 4–5 E−) | 2 | a larger domain |
| `t4_nested` | 8 | 2 | an exception to the exception, exception facts listed first |
| `t5_twopath` | 10 | 2 | two derivation paths, each with its own exception |

**Every tier is exactly 50/50 defeasible/monotonic.** The class is defined by
the reference, not by the generator: a problem is *defeasible* when the gold
trace contains an R3 step. The build rejects any problem whose trace disagrees
with the class it was drawn for (none were rejected for this in v1).

**Why the construction looks the way it does.** In the set-05 benchmark,
"the prompt contains exception facts" predicted R3 on 98 of 101 problems. A
model could learn that shortcut and never check anything. In tier spec v2:

- every problem carries two exception facts, one on a negative example and
  one on an unlisted constant;
- in a defeasible problem the negative with the exception also has the key
  predicate, so folding on the key covers it (line 18 fails, R3 is needed);
  in a monotonic problem it is the unlisted constant that has the key;
- fact counts and example counts follow the same distribution in both
  classes, and facts are shuffled within each predicate.

Only the check itself, *does this fold cover a negative?*, separates the
classes. Balanced accuracy of each surface cue at predicting R3 (0.50 = no
signal):

| surface cue | first v2 draft (941 problems) | v1, train split |
| --- | --- | --- |
| exception facts exist | 0.50 | 0.500 |
| an exception fact on a negative | 0.73 | 0.500 |
| an exception fact on an unlisted constant | 0.74 | 0.500 |
| an exception fact on a key-like constant | 0.62 | 0.505 |
| more negatives than positives | 0.50 | 0.514 |

The first v2 draft put the exception *either* on an unsupported negative *or* on
an unlisted supported constant. Each half closed one shortcut and left the
other; pairing the two facts closed both. These are the cues that were
measured, not a proof that no other cue exists.

`t5_twopath` replaces the legacy two-path generator, whose 20 set-05 problems
were one structure in 20 surface forms. The two are not comparable.

## Held-out tiers

Held-out problems are never trained on. In every one of them **two different
intensional solutions pass the checker**, and only following Algorithm 1 gives
the reference's. Each tier has two halves that swap which answer that is, so
a model with a fixed preference scores 0.5.

| tier | paper basis | half A: Algorithm 1 returns | half B: Algorithm 1 returns | also passes the checker |
| --- | --- | --- | --- | --- |
| `t8_decoy` | lines 17–19 | decoy facts first → `t(X) :- decoy(X)` | key facts first → R3 on the key fold | the other half's answer |
| `t9_reuse` | Definition 4, lines 36–39 | β's contrary covers the negative → reuse β | it does not → line 39, then a fresh α on `key2` | a fresh α on `key` |

In `t8_decoy`, `decoy` holds for exactly the positives and `key` for the
positives plus one negative. Line 17 takes the fold whose facts come first:
`decoy` passes line 18 as it stands, `key` does not and line 19 guards it.

In `t9_reuse`, the background rule `h(X) :- key(X), beta(X)` makes `beta`
relative to `key(X)` (Definition 4), so line 36 must reuse it on the fold
`t(X) :- key(X)`. `key2` has the same facts as `key` and no relative
assumption.

The two tiers differ in one respect that matters for reporting.
`t9_reuse`'s wrong answer, minting on `key`, is **forbidden by line 36 under
any fold order**. `t8_decoy`'s wrong answer is only wrong under *our* fold
order: with the decoy facts taken first, Algorithm 1 itself would return it.
`meta.forbidden` in `problems.jsonl` records which answers are forbidden
outright, so the two can be reported separately.

`check_heldout` verifies, for every held-out problem, that each listed answer
is a solution and that the reference returns the expected one.

The paper's own benchmarks (Table 1: seven classic problems and three tabular
ones) will be a second held-out set, imported from the Zenodo archive
(doi 10.5281/zenodo.13330013). They add external validity and comparability
with Table 1. The two-answers property is not built into them.

## Splits and leakage

- **No two problems in the corpus share a structural signature**, in any split.
  The signature is a Weisfeiler–Lehman hash of the problem graph (predicates
  coloured by role, constants by example label, one node per rule),
  invariant to renaming and ordering. Anonymisation cannot play this role,
  because it names symbols by first appearance and so is not a canonical
  form.
- **Splits are filled held-out → test → val → train**, each (tier, class)
  stream taking its next accepted problems. Growing the train split never
  changes an evaluation problem; `tests/test_corpus.py` checks this.
- Each problem is drawn from its own `Random(seed)`, with
  `seed = "corpus-v1:<tier>:<stream>:<attempt>"` (the stream is `defeasible`
  or `monotonic`, or `v1`/`v0` for a held-out half), recorded in
  `problems.jsonl`.
- Structural duplicates are rejected, not kept. The generator's own duplicate
  rate is reported, not gated: `t1_base` 4.5% (its structure space is small)
  and `t8_decoy` 9.1% (its two halves differ only in fact order, which the
  signature ignores). Every other tier: 0%.

## What the reference does

The reference follows Algorithm 1 of the ECAI paper
(p. 3449; line numbers as in the PDF). Two corrections were made to it while
building this corpus; [METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 8, records
both.

- **Lines 17–19.** One fold is taken. If it is not a solution (line 18),
  applyAsmIntro guards that same fold (line 19). Another fold is tried only on
  backtracking.
- **Lines 36–39.** If an assumption is relative to the body (Definition 4), it
  must be reused. If that gives no solution, line 39 fails and the search
  returns to the most recent choice point. A fresh assumption is introduced
  only when none is relative (line 41).
- **Fold order.** The paper leaves open the order in which fold alternatives
  are tried (Definition 3: "possibly, in a nondeterministic way"; §8 calls it
  "the most critical issue"). The reference takes them in background-rule
  order, with `dom(X)` last. This is a convention, and `t8_decoy` depends on
  it.

One consequence shows up throughout the corpus: **line 39 fires in every
defeasible problem of `t1`, `t2`, `t3` and `t5`**, on the contrary fact. Its
first fold is on the key, where the α just minted is relative (Definition 4);
reusing it fails, and line 17 moves to the next fold. In `t4_nested` the
exception facts come first, so the contrary's first fold is on the exception
and reuses its background assumption successfully. There, line 39 fires on a
target fact instead, in 151 of the 190 defeasible problems: the first fold is
again on the exception, the reused assumption lets the negative through, and
line 17 moves on to the key.

## The two targets

The **endpoint** target is the answer block alone, exactly as
`parse_llm_output` reads it. The **trace** target is the algorithm's decisions,
one per line, followed by the same answer block byte for byte. A defeasible
`t1_base` training problem (`t1_base_0098`):

```text
RoLe.
R1 v(X) :- X = b.
R1 v(X) :- X = c.
Gen.
fact v(X) :- X = b.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact v(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

Only applied transformations are written as bare rules (`R1/R2/R3 <rule>`).
Everything merely considered is in `[brackets]`, which the frozen fidelity
scorer strips, so a model that records its own search loses nothing for it.
The full grammar is in [`src/aba_sft.py`](../src/aba_sft.py).

**Every target is verified before it is kept** (`check_example`). The
algorithm's framework, a replay from the recorded decisions, a replay from the
trace text alone, and the parser's reading of each answer block must all
coincide, with zero parser repairs, and the replayed framework must still be a
solution.

**The scorer's ceiling is stored with each evaluation row.** The frozen scorer
does not give a perfect copy of the gold trace full marks (R4 is inferred only
at the end of a trace), so `eval.jsonl` carries `ceiling`, the score of the
gold trace itself, and model scores are read against it.

## Step counts

| tier | R1 | R2 | R3 | R4 | problems with a reuse | problems with a line-39 failure |
| --- | --- | --- | --- | --- | --- | --- |
| `t1_base` | 867 | 380 | 190 | 487 | 0 | 190 |
| `t2_noise` | 938 | 380 | 190 | 558 | 0 | 190 |
| `t3_domain` | 1709 | 380 | 190 | 1329 | 0 | 190 |
| `t4_nested` | 958 | 190 | 380 | 578 | 190 | 151 |
| `t5_twopath` | 1536 | 760 | 260 | 776 | 0 | 190 |
| `t8_decoy` | 128 | 50 | 25 | 78 | 0 | 25 |
| `t9_reuse` | 121 | 25 | 50 | 71 | 25 | 25 |

All splits, 380 problems per training tier (190 defeasible). Every defeasible
`t4_nested` problem reuses an assumption. R3 is 5–18% of all steps in the
training tiers (`t3_domain` 5.3%, `t4_nested` 18.0%): each path needs one
assumption however many exceptions it has, while R1 and R4 grow with the
number of positives. The planned gate "R3 ≥ 20% of steps" was therefore
replaced by coverage: **every defeasible problem contains R3**.

## Arm matching (pre-registered)

Train-split targets average 681 characters (trace) against 86 (endpoint), a
ratio of 7.9. "Same epochs" is therefore not "same compute", and both
criteria are fixed now, before any training run:

- **Primary: same optimiser steps.** Both arms see the same train problems, in
  the same order, for the same number of epochs, with the same batch size and
  learning-rate schedule.
- **Secondary: same supervised target tokens.** The endpoint arm is trained for
  as many extra epochs as it takes to see the trace arm's total target tokens.
  The ratio is fixed once, on the train split, with the model's own tokenizer,
  before any run.

## Gates

A build fails unless all of these hold:

- every training tier and split is exactly 50/50 by class;
- R3 appears in every defeasible problem;
- every exception-fact cue is ≤ 0.55 on the train split (val and test are
  small enough for sampling noise to cross that);
- `t4_nested` reuses an assumption in ≥ 20% of its problems;
- no structural signature is shared by two problems.

Two gates from the original plan were replaced, each for a stated reason: the
R3 step share (above), and "≥ 98% distinct signatures per tier", which became
the hard uniqueness gate plus the reported duplicate rate.

## Files

| file | contents |
| --- | --- |
| `problems.jsonl` | every accepted problem: seed, tier, split, class, signature, the anonymised problem, the name map, and for held-out problems the answers and which is expected |
| `traces.jsonl` | the reference's full decision record on each problem |
| `sft_trace.jsonl`, `sft_endpoint.jsonl` | train and val only; identical prompts, different targets |
| `eval.jsonl` | test and held-out; prompt, both gold targets, the scorer's ceiling |
| `rejects.jsonl` | every rejected attempt and why |
| `MANIFEST.json`, `MANIFEST.md` | provenance, counts, gates, cues, pre-registration, sha256 |

## Reproducing

```bash
python build_corpus.py            # writes corpus/v1, about 2 minutes
python -m pytest tests/test_corpus.py -q
```

Compare the sha256 values in the rebuilt `MANIFEST.json` with the committed
one. They match as long as the code revision and the Clingo version are the
same (v1: Clingo 5.8.0; the paper's tool used 5.6.2). A different Clingo
version may choose a different minimal answer set in RoLe.
