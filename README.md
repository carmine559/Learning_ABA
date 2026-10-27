# Learning ABA — can an LLM replicate ABA Learning?

Can a large language model execute ASP-ABAlearnB, Algorithm 1 of De Angelis,
Proietti & Toni (ECAI 2024)? A brave ABA Learning problem gives a background ABA
framework, positive and negative examples, and the learnable predicates T; a
solution adds rules and assumptions so that the framework admits a stable
extension accepting every positive example and no negative one (Definition 1).
Models are scored on how faithfully they replicate the algorithm, never on
whether they beat it.

MSc thesis project, University of Bologna.

## What is here

- **The reference.** [`src/aba_algorithm.py`](src/aba_algorithm.py) implements
  Algorithm 1: RoLe, then Gen with Folding, Assumption Introduction and Fact
  Subsumption, with every ASP check run by Clingo. It was audited line by line
  against the paper (p. 3449); what was found, fixed and left open is in
  [docs/METHOD_HISTORY.md](docs/METHOD_HISTORY.md). On the paper's Nixon diamond
  (Examples 1 and 3) it learns R₂ up to the name of α.
- **Corpus v1** ([docs/CORPUS.md](docs/CORPUS.md)): 2,000 anonymised problems
  labelled by the reference (train 1,500, val 200 and test 200 over five tiers;
  held-out 100 in `t8_decoy` and `t9_reuse`), plus the paper's Table 1 from its
  Zenodo archive. `corpus/v1-permuted` renames the predicates per problem;
  `corpus/v1-step` holds arm S2's step rows.
- **Fine-tuning** ([`sft/`](sft/)): LoRA on Qwen2.5-7B-Instruct, in arms that
  differ only in the target: **endpoint** (the learnt framework), **trace** (the
  algorithm's decisions, then the framework) and **S2** (one row per step; at
  inference the reference runs the control flow and the model answers each step).
- **One scorer**, [`src/aba_score.py`](src/aba_score.py): validity by
  Definition 1, exact agreement with the reference (up to assumption names and
  body order), the held-out choice, and an audit of written steps.
- **The earlier prompting study** (`main.py`, [`experiments/`](experiments/)
  00–05): four prompting modes and step probes, Qwen2.5 3B–32B and Mistral-7B. Corrections found
  after its figures were produced (a parser defect, missing chance floors) are not
  yet applied, so they are not quoted here.
- **Task 2** ([`gradual/`](gradual/), [docs/GRADED.md](docs/GRADED.md)): BSAF
  gradual semantics for ABA (Rapberger, Russo, Rago & Toni, KR 2025) against an
  argument-tree DF-QuAD baseline.

## Results so far

Endpoint and trace from [`sft/compare_sft.py`](sft/compare_sft.py), registered
before the trace arm was scored; S2 from [`sft/compare_step.py`](sft/compare_step.py),
registered before any S2 output existed. One seed per arm, greedy decoding; S2 also
has a second seed, read descriptively. What these results answer, and what they do not,
is in [docs/FINDINGS.md](docs/FINDINGS.md).

| set | base | endpoint | trace | S2 | constant answer |
| --- | --- | --- | --- | --- | --- |
| test, exact | 0/200 | 200/200 | 89/200 | 198/200 | 100/200 |
| `t8_decoy`, exact | 0/50 | 25/50 | 13/50 | 50/50 | |
| `t9_reuse`, exact | 0/50 | 0/50 | 0/50 | 0/50 | |
| Table 1 (8 problems, named and anonymised), valid | 1/16 | 0/16 | 0/16 | 0/16 | |
| test + held-out, exact, original → renamed | 0 → 0 | 225 → 116 | 102 → 41 | 248 → 150 | |

- A constant answer per tier is valid on 99% of test problems, so validity does
  not discriminate there; exact agreement and the held-out tiers do.
- The endpoint arm is exact exactly when the gold answer is one of the 20
  distinct training answers: 225/225 such prompts, 0/91 others.
- The trace arm writes the trace's form (RoLe facts 199/200, fold candidates
  302/333 on test) and its answer follows its trace on 198/200, but its first
  line-18 verdict is right on 107/200, the level of a guess that ignores the
  problem.
- S2 meets its registered criteria (D5). Its first line-18 verdict is right on
  200/200 test problems, where a baseline that reads only the step's position
  gets 117/200, and at the reference's states every kind of step is at least 98%
  right on test. At the 448 test states its search skips, line 18 is right on 447
  (second seed: 446), where the position rule gets 358. Both of its test misses start
  with a RoLe answer with one or two
  facts too many. Exact on test does not separate it from the endpoint arm
  (198 vs 200); `t8_decoy` does (50/50 against 25/50).
- S2's limits: all 50 `t9_reuse` runs first go wrong at line 38's test, with "no"
  on the RoLe fact where the reuse works (a "yes" there never occurs in training)
  and "yes" on the contrary fact where it does not. Renaming breaks mostly the
  fold-candidate list, the first wrong step in 112 of the 129 renamed test runs
  that go wrong, while RoLe (198/200) and the first line-18 verdict (192/200)
  survive. It reads 4.5× the trace arm's tokens per epoch, but is supervised on
  0.62× its target tokens.
- S2's second seed gives the same count in every S2 cell of the table. On v1 test it
  produces the same run as the first seed on 190 of 200 problems, but misses two other
  problems. Renamed, 40 of the 200 test problems change outcome between the seeds.
- All three fine-tuned arms lose exact answers when predicates are renamed
  (McNemar p < 0.05).
- No arm solves Table 1. On each of its eight problems, the algorithm's answer has a
  shape that no v1 training answer has: a new assumption in the rule for another's
  contrary (five problems), or RoLe facts other than the positive examples (three). The arms write v1's
  shapes ([`analysis/answer_shapes.py`](analysis/answer_shapes.py)).

## Installation

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests -q        # the Table 1 test is skipped without the Zenodo archive
```

Used with Python 3.11–3.13 and Clingo 5.8. Fine-tuning runs on the DISI L40
nodes with the pinned [`requirements-train.txt`](requirements-train.txt),
installed by [`cluster/setup_env.sh`](cluster/setup_env.sh).

## Quick start

```python
from src.aba_dataset import make_nixon_diamond
from src.aba_algorithm import solve_aba_learning

problem, _ = make_nixon_diamond()
solution, trace = solve_aba_learning(problem)
for r in solution.new_rules:
    print(r.to_prolog())
# pacifist(X) :- democrat(X).
# abnormal_quaker(X) :- republican(X), alpha_0(X).
# c_alpha_0(X) :- quaker(X), normal_quaker(X).
```

```bash
python -m src.aba_score --control corpus/v1     # every gold target scores the maximum: 316/316
python main.py --symbolic-only --benchmark 20   # the reference on the prompting benchmark
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1   # prompting pipeline, no GPU

# on the SLURM cluster, giano (cluster/README.md; usage in each script's header)
sbatch --export=ALL,ARMS=trace cluster/train_sft.sbatch
sbatch cluster/stepwise_sft.sbatch
python sft/compare_sft.py     # results/sft/COMPARISON.md
python sft/compare_step.py    # results/sft-step/COMPARISON_STEP.md, the D5 verdict
```

## Repository map

| Path | Content |
| --- | --- |
| [`src/`](src/) | the reference, the Clingo checks, the corpus, the scorer, the step oracle, the prompting pipeline |
| [`sft/`](sft/) | corpus builder, training, evaluation and arm comparisons; run from the root as `python sft/<script>.py` |
| [`corpus/`](corpus/) | `v1`, `v1-permuted`, `v1-step`, each with a MANIFEST |
| `runs/` | one `TRAINING_MANIFEST.json` per run; adapters stay on the cluster |
| `results/` | evaluation outputs, tracked so cluster runs come back with `git push` |
| [`experiments/`](experiments/) | the prompting study's result sets 00–05, one `MANIFEST.md` each |
| `rescored/`, `rescored_v2/` | offline re-scorings of set 04's probe answers |
| [`analysis/`](analysis/) | offline studies of the prompting runs: step fidelity, conformance, null floors |
| [`tests/`](tests/) | golden traces, corpus, scorer, steps, oracle hook |
| [`cluster/`](cluster/) | SLURM scripts for the DISI L40 nodes |
| [`gradual/`](gradual/) | Task 2: gradual semantics |
| [`extras/`](extras/) | reporting for `main.py`: framework export, explanations, figures |
| [`argllm/`](argllm/) | notes on a possible further task; no code |
| [`docs/`](docs/) | [corpus](docs/CORPUS.md) · [method history](docs/METHOD_HISTORY.md) · [experiments](docs/EXPERIMENTS.md) · [prompts](docs/PROMPTS.md) · [CLI](docs/CLI.md) · [graded semantics](docs/GRADED.md) |
| `main.py`, `rescore.py` | the prompting-study pipeline and its offline re-scoring |

## References

De Angelis, E., Proietti, M., & Toni, F. (2024). *Learning Brave
Assumption-Based Argumentation Frameworks via ASP.* ECAI 2024, 3445–3452.

Rapberger, A., Russo, F., Rago, A., & Toni, F. (2025). *On Gradual Semantics for
Assumption-Based Argumentation.* KR 2025.
