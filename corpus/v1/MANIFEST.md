# Corpus v1

- code rev: `502b725`; clingo 5.8.0; python 3.12.3
- tier spec: v2; prompt: v4-sft
- config: `{"base_seed": "corpus-v1", "n_test": 20, "n_val": 20, "n_train": 150, "n_heldout": 25, "max_attempts": 4}`

## Gates

- [x] every tier and split exactly 50/50 by class
- [x] R3 in every defeasible problem (coverage)
- [x] exception-fact cues <= 0.55 on train
- [x] t4_nested reuse in >= 20% of problems
- [x] no signature shared across problems
- [x] no generated problem shares a Table 1 signature

## Counts

| tier | split/class | n |
|---|---|---|
| t1_base | test/defeasible | 20 |
| t1_base | test/monotonic | 20 |
| t1_base | train/defeasible | 150 |
| t1_base | train/monotonic | 150 |
| t1_base | val/defeasible | 20 |
| t1_base | val/monotonic | 20 |
| t2_noise | test/defeasible | 20 |
| t2_noise | test/monotonic | 20 |
| t2_noise | train/defeasible | 150 |
| t2_noise | train/monotonic | 150 |
| t2_noise | val/defeasible | 20 |
| t2_noise | val/monotonic | 20 |
| t3_domain | test/defeasible | 20 |
| t3_domain | test/monotonic | 20 |
| t3_domain | train/defeasible | 150 |
| t3_domain | train/monotonic | 150 |
| t3_domain | val/defeasible | 20 |
| t3_domain | val/monotonic | 20 |
| t4_nested | test/defeasible | 20 |
| t4_nested | test/monotonic | 20 |
| t4_nested | train/defeasible | 150 |
| t4_nested | train/monotonic | 150 |
| t4_nested | val/defeasible | 20 |
| t4_nested | val/monotonic | 20 |
| t5_twopath | test/defeasible | 20 |
| t5_twopath | test/monotonic | 20 |
| t5_twopath | train/defeasible | 150 |
| t5_twopath | train/monotonic | 150 |
| t5_twopath | val/defeasible | 20 |
| t5_twopath | val/monotonic | 20 |
| t8_decoy | heldout/decoy_first | 25 |
| t8_decoy | heldout/key_first | 25 |
| t9_reuse | heldout/reuse_fails | 25 |
| t9_reuse | heldout/reuse_ok | 25 |

## Step symbols (all splits)

| tier | R1 | R2 | R3 | R4 | problems with reuse | with line 39 |
|---|---|---|---|---|---|---|
| t1_base | 867 | 380 | 190 | 487 | 0 | 190 |
| t2_noise | 938 | 380 | 190 | 558 | 0 | 190 |
| t3_domain | 1709 | 380 | 190 | 1329 | 0 | 190 |
| t4_nested | 958 | 190 | 380 | 578 | 190 | 151 |
| t5_twopath | 1536 | 760 | 260 | 776 | 0 | 190 |
| t8_decoy | 128 | 50 | 25 | 78 | 0 | 25 |
| t9_reuse | 121 | 25 | 50 | 71 | 25 | 25 |

## Cues (balanced accuracy predicting R3; 0.50 = no signal)

| feature | test | val | train |
|---|---|---|---|
| exc facts exist | 0.500 | 0.500 | 0.500 |
| exc on a negative | 0.500 | 0.500 | 0.500 |
| exc on an unlisted constant | 0.500 | 0.500 | 0.500 |
| exc on a key-like constant | 0.510 | 0.520 | 0.505 |
| more than one exc fact | 0.500 | 0.500 | 0.500 |
| more negatives than positives | 0.510 | 0.535 | 0.514 |
| (semantic) a negative has a key-like fact | 0.750 | 0.760 | 0.787 |

## Arm matching (pre-registered)

Train-split target length: trace 680.5 chars, endpoint 86.1 chars (ratio 7.9).

- **Primary:** same optimiser steps: both arms see the same train problems, in the same order, for the same number of epochs, with the same batch size and learning-rate schedule.
- **Secondary:** same supervised target tokens: the endpoint arm is trained for as many extra epochs as it takes to see the trace arm's total target tokens; the ratio is fixed once, on the train split, with the model's own tokenizer, before any run.

## Rejects

- t1_base/duplicate_signature: 18
- t8_decoy/duplicate_signature: 5

Generator duplicate rate (rejected duplicates / attempts): t1_base 4.5%, t2_noise 0.0%, t3_domain 0.0%, t4_nested 0.0%, t5_twopath 0.0%, t8_decoy 9.1%, t9_reuse 0.0%.

## Table 1 (external held-out, never trained on)

Zenodo doi 10.5281/zenodo.13330013, release `ASP-ABAlearn_B`, md5 `32c39f6f437d334206d748412b55df74`. Posed problems have a named and an anonymised prompt.

| problem | BK / E+ / E− | posed | R1 | R2 | R3 | R4 | new rules | new assumptions | anon same steps | R2 gap |
|---|---|---|---|---|---|---|---|---|---|---|
| flies | 8 / 4 / 2 | yes | 4 | 1 | 2 | 5 | 3 | 2 | True | 2 |
| flies_birds_planes | 10 / 5 / 2 | yes | 5 | 2 | 3 | 3 | 5 | 3 | True | 2 |
| innocent | 15 / 2 / 2 | yes | 3 | 1 | 2 | 1 | 3 | 1 | True | 4 |
| nixon_diamond | 6 / 1 / 1 | yes | 1 | 0 | 3 | 0 | 3 | 2 | True | 0 |
| nixon_diamond_2 | 15 / 3 / 2 | yes | 2 | 1 | 2 | 0 | 3 | 1 | True | 3 |
| tax_law | 16 / 2 / 2 | yes | 2 | 1 | 3 | 2 | 4 | 2 | True | 5 |
| tax_law_2 | 17 / 2 / 2 | yes | 2 | 1 | 2 | 1 | 3 | 1 | True | 6 |
| acute | 96 / 21 / 19 | yes | 21 | 0 | 3 | 32 | 3 | 2 | True | 0 |
| autism | 5716 / 189 / 515 | no | 189 | 20 | 38 | 1213 | 58 | 24 | — | 0 |
| breast_w | 6291 / 241 / 458 | no | 241 | 24 | 38 | 687 | 62 | 23 | — | 0 |

## Notes

- Problems are posed whole (Definition 1): prompt and gold trace see all examples. No example-level split; evaluation uses separate problems.
- Fold alternatives are taken in background-rule order, dom(X) last. The paper leaves this order open (Definition 3); t8_decoy depends on it, t9_reuse's forbidden answer does not.
- t5_twopath here is tier spec v2 and is not comparable with set 05's t5_twopath, whose 20 problems are one structure in 20 surface forms.
- Held-out and test problems never appear in sft_*.jsonl.
- Table 1 (Zenodo release, src/aba_zenodo.py) is read as the released tool reads it; T and dom follow that tool and lines 211-212; integer constants are renamed n<k>. It is posed named and anonymised; autism and breast_w are solved but not posed (prompts of 98k and 207k chars).
- The reference's R2 folds with unary background facts and dom only; the paper's R2 folds with any rule of R, of any arity (lines 326-329). `r2_gap` counts the background rules this leaves out. Gold traces are the reference's.

## Files (sha256)

- `problems.jsonl` a50b82612cf8b38a252a45fb491a70a41fcec951685a07dab86b601362f119e8
- `traces.jsonl` a8c802094a45bc8e1e8e648c897bbc0ed62e08103a2e062cca0b715530981398
- `sft_trace.jsonl` d5ae9edcb8f7bc1835bc9378aab2a6f8b34644d368e236e3886da1f98000718d
- `sft_endpoint.jsonl` 1bd841cbc912f0c6171f06abc21e3e066420ffcc47d18bcf8a98bc85f2f40258
- `eval.jsonl` d8c1df85b631d0f6809583f3ded8936730783e81652dd82b032d0e041032ce25
- `rejects.jsonl` 32bd98a6e52e93bf4bf0c27e32a132bb34c0bf030dc5652970607eedc76a9084
- `table1_problems.jsonl` 3c4f932241bf20623fe09d99856b03aaeff8fada4a5f369d49f1b5f4fb7f099b
- `table1_traces.jsonl` 7f76bee1407d0239ff2e1f0de8d7e74de1fbaf541be5bdd1a5eb58ddf589d22b
- `table1_eval.jsonl` ba2cef57b8238898b398bb20e4cfc90f9a562942a62d9ad08bf4f1a5b16f5151
