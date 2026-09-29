# Corpus v1

- code rev: `4ea1f31`; clingo 5.8.0; python 3.12.3
- tier spec: v2; prompt: v4-sft
- config: `{"base_seed": "corpus-v1", "n_test": 20, "n_val": 20, "n_train": 150, "n_heldout": 25, "max_attempts": 4}`

## Gates

- [x] every tier and split exactly 50/50 by class
- [x] R3 in every defeasible problem (coverage)
- [x] exception-fact cues <= 0.55 on train
- [x] t4_nested reuse in >= 20% of problems
- [x] no signature shared across problems

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

## Notes

- Problems are posed whole (Definition 1): prompt and gold trace see all examples. No example-level split; evaluation uses separate problems.
- Fold alternatives are taken in background-rule order, dom(X) last. The paper leaves this order open (Definition 3); t8_decoy depends on it, t9_reuse's forbidden answer does not.
- t5_twopath here is tier spec v2 and is not comparable with set 05's t5_twopath, whose 20 problems are one structure in 20 surface forms.
- Held-out and test problems never appear in sft_*.jsonl.

## Files (sha256)

- `problems.jsonl` a50b82612cf8b38a252a45fb491a70a41fcec951685a07dab86b601362f119e8
- `traces.jsonl` a8c802094a45bc8e1e8e648c897bbc0ed62e08103a2e062cca0b715530981398
- `sft_trace.jsonl` d5ae9edcb8f7bc1835bc9378aab2a6f8b34644d368e236e3886da1f98000718d
- `sft_endpoint.jsonl` 1bd841cbc912f0c6171f06abc21e3e066420ffcc47d18bcf8a98bc85f2f40258
- `eval.jsonl` d8c1df85b631d0f6809583f3ded8936730783e81652dd82b032d0e041032ce25
- `rejects.jsonl` 32bd98a6e52e93bf4bf0c27e32a132bb34c0bf030dc5652970607eedc76a9084
