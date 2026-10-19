# Corpus v1-step

- code rev: `c1ab6c5`; clingo 5.8.0; python 3.12.3
- prompt: v1-step; splits: train, val
- source: `corpus/v1` (corpus v1, code rev `502b725`); permuted: `corpus/v1-permuted`
- gated problems: {'v1': 2000, 'table1': 16, 'permuted': 300}

## Gates

- [x] harvest equals the stored record
- [x] one row per decision of the record
- [x] every target parses back to the reference's answer
- [x] train/val witnesses: unique answer set, empty iff yes
- [x] the extra-row test equals line 18 where the search asks it
- [x] gold answers through the controller reproduce the trace target
- [x] no test, held-out or Table 1 problem in steps.jsonl

## Rows, val

| kind | n |
|---|---|
| check | 452 |
| check (extra) | 463 |
| contrary_facts | 109 |
| fold_candidates | 349 |
| reuse_check | 123 |
| reuse_scan | 232 |
| role | 200 |
| subsume | 732 |
| **total** | 2660 |

## Rows, train

| kind | n |
|---|---|
| check | 3372 |
| check (extra) | 3344 |
| contrary_facts | 802 |
| fold_candidates | 2602 |
| reuse_check | 920 |
| reuse_scan | 1722 |
| role | 1500 |
| subsume | 5543 |
| **total** | 19805 |

## Cells, val

| cell | n |
|---|---|
| after_l39_check | 14 |
| extra_check | 463 |
| first_check | 200 |
| later_role_subsume | 423 |
| other | 1506 |
| role_reuse_check | 14 |
| second_path_check | 40 |

## Cells, train

| cell | n |
|---|---|
| after_l39_check | 118 |
| extra_check | 3344 |
| first_check | 1500 |
| later_role_subsume | 3241 |
| other | 11184 |
| role_reuse_check | 118 |
| second_path_check | 300 |

## Answer sets of ASP(F, <{}, {}>, {}) at lines 16 and 18 (group:count)

permuted:1: 1759, table1:1: 182, table1:1024: 2, table1:16384: 2, table1:2: 14, table1:2048: 2, table1:256: 2, table1:4096: 2, table1:512: 2, table1:8: 4, table1:8192: 2, v1:1: 15665

## Notes

- One row per step the reference takes on each train and val problem of the source (src/aba_steps.py), plus `extra` rows: line 18 asked at every non-dom fold candidate the search does not reach. Extra rows are training-only.
- Prompts are not stored: src/aba_steps.step_prompt rebuilds them from the problem and `state`; prompt_sha256 pins them per split and kind.
- Lines 16 and 18 name the failing examples of the unique answer set of ASP(F, <{}, {}>, {}) before the verdict; the gates require that answer set to be unique and its failing examples empty iff the verdict is yes.
- Test, held-out, Table 1 and the permuted set are harvested here only for the gates and for longest_target; the evaluation harvests them again.

## Files (sha256)

- `steps.jsonl` f30aa39cc43ec1e5273c4b096e641fb2f356150e083ab8f71f24fb1f2b6bcac9

## Rebuilt prompts (sha256)

- train/check: 2b37f8f9ef0e010079baba287a05230f329f1b8908a24882d1d3ee8335960435
- train/contrary_facts: fa96095d4869a77df9d8e41148a3eb77cc55159384ea68bd80f0896d563d5cb0
- train/fold_candidates: b608d91cece34cc89959f93d21b992f573a0dce120b9341a2175bdc78e98f8c1
- train/reuse_check: ce9016e552598ebf7f9fd982da908eb7ab242d22edcc9fc8d216403fa17d9b28
- train/reuse_scan: 8f83b5d8d3d0493bab7cd7e1b1ef9a6701336eab743b57bf269195d7ff2fa26d
- train/role: c896789e05299af77902383003bb043ea84cdeddf4fca7de7db2a9325d9bcbf4
- train/subsume: 275d00e8c3b541fd1e59e2a478e04d84c1a690bb4773a5d04aeb47f61a214b89
- val/check: 338c81b5b4fe320c393c43210f561a35dbd9e8dce0a3c170dc22d4c128cfe5a0
- val/contrary_facts: e2eb18126090773cf17facc06f9f9d6b15b4a54a5adc4451e8784b07da8c9b19
- val/fold_candidates: 9870fb4f792ba863c9e4ec3da89bdd1938e29bddb10c4518758081e1bf12c867
- val/reuse_check: 760922afef8747d4d4a830a36646508131692919f853da6408c224e88ce317da
- val/reuse_scan: 9c14ac9049000ff807d82c7f05d1cef83363a325fa33af4a36141faf9a1f3708
- val/role: 7cb42845ad01b5f668b2077bca88ec8d73897f083e0037d0c4992e1a300e80a2
- val/subsume: e312091930d4b05fd5dc8329d4222bc52a343e0b606e76818767f65ba5ef84fc
