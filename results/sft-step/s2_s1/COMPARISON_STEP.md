# Arm S2 (step-wise SFT) against the registered arms

D5 was registered in compare_step.py before any S2 output existed. Proportions: value [Clopper-Pearson 95%] (k/n). Balanced: mean recall on yes and no, a miss when no verdict was given.

## D5: supported

| criterion, v1 test | S2 | registered | holds |
|---|---|---|---|
| (a) first-check balanced, chained | 0.995 | >= 0.8 (refuted <= 0.6) | True |
| (b) R3 balanced | 1.000 | >= 0.8 | True |
| (c) exact against sft_trace | 198/200 against 89; 109 S2 only, 0 sft_trace only, p 3.081e-33 | > 89, p < 0.05 | True |

Confounds (with any verdict): S2 reads 4.5x the trace arm's tokens per epoch and is supervised on 0.62x its target tokens; no definitions block, no step history; the lines-16/18 targets name the failing examples; 3,344 extra line-18 rows.

## First line-18 check

| set | sft_trace, own path | S2 chained (reached, at reference state) | S2 at the reference's state | position baseline |
|---|---|---|---|---|
| t8_decoy decoy_first | - / 0.00 [0.00, 0.14] (0/25) | - / 1.00 [0.86, 1.00] (25/25) (25, 25 of 25) | - / 1.00 [0.86, 1.00] (25/25) | - / 0.00 [0.00, 0.14] (0/25) |
| t8_decoy key_first | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) (25, 25 of 25) | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) |
| t9_reuse reuse_fails | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) (25, 25 of 25) | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) |
| t9_reuse reuse_ok | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) (25, 25 of 25) | - / 1.00 [0.86, 1.00] (25/25) | - / 1.00 [0.86, 1.00] (25/25) |
| table1 anon | - / 0.88 [0.47, 1.00] (7/8) | - / 0.50 [0.16, 0.84] (4/8) (7, 3 of 8) | 0.750 / 0.62 [0.24, 0.91] (5/8) | 0.500 / 0.75 [0.35, 0.97] (6/8) |
| table1 named | - / 0.62 [0.24, 0.91] (5/8) | - / 0.50 [0.16, 0.84] (4/8) (7, 1 of 8) | 0.833 / 0.75 [0.35, 0.97] (6/8) | 0.500 / 0.75 [0.35, 0.97] (6/8) |
| test | 0.536 / 0.54 [0.46, 0.61] (107/200) | 0.995 / 0.99 [0.97, 1.00] (199/200) (200, 199 of 200) | 0.995 / 0.99 [0.97, 1.00] (199/200) | 0.558 / 0.58 [0.51, 0.65] (117/200) |

Cells: balanced / accuracy. Chained and gold asked at the same state agree on 1.00 [0.99, 1.00] (303/303).

## Exact by set (S2 strict: no illegal item in any call)

| set | base | sft_endpoint | sft_trace | s2 | s2 strict |
|---|---|---|---|---|---|
| v1 t8_decoy decoy_first | 0.00 [0.00, 0.14] (0/25) | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) |
| v1 t8_decoy key_first | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.52 [0.31, 0.72] (13/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) |
| v1 t9_reuse reuse_fails | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| v1 t9_reuse reuse_ok | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| v1 table1 anon | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) |
| v1 table1 named | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) |
| v1 test | 0.00 [0.00, 0.02] (0/200) | 1.00 [0.98, 1.00] (200/200) | 0.45 [0.37, 0.52] (89/200) | 0.99 [0.96, 1.00] (198/200) | 0.99 [0.96, 1.00] (198/200) |
| permuted t8_decoy decoy_first | 0.00 [0.00, 0.14] (0/25) | 0.56 [0.35, 0.76] (14/25) | 0.04 [0.00, 0.20] (1/25) | 0.64 [0.43, 0.82] (16/25) | 0.64 [0.43, 0.82] (16/25) |
| permuted t8_decoy key_first | 0.00 [0.00, 0.14] (0/25) | 0.48 [0.28, 0.69] (12/25) | 0.36 [0.18, 0.57] (9/25) | 0.72 [0.51, 0.88] (18/25) | 0.72 [0.51, 0.88] (18/25) |
| permuted t9_reuse reuse_fails | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.08 [0.01, 0.26] (2/25) | 0.28 [0.12, 0.49] (7/25) | 0.28 [0.12, 0.49] (7/25) |
| permuted t9_reuse reuse_ok | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| permuted test | 0.00 [0.00, 0.02] (0/200) | 0.45 [0.38, 0.52] (90/200) | 0.14 [0.10, 0.20] (29/200) | 0.55 [0.47, 0.62] (109/200) | 0.52 [0.44, 0.59] (103/200) |

## S2, the registered report's fields: v1

| set | parsed | exact | valid | clean | agreement (n) | r3 bal. | r3 bal., misses | choice | main rule | contrary | forbidden |
|---|---|---|---|---|---|---|---|---|---|---|---|
| t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 (25) | - | - | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | - | 0.00 [0.00, 0.14] (0/25) |
| t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 (25) | - | - | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) |
| t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - | - |
| table1 named | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - | - |
| test | 1.00 [0.98, 1.00] (200/200) | 0.99 [0.96, 1.00] (198/200) | 0.99 [0.96, 1.00] (198/200) | 0.99 [0.96, 1.00] (198/200) | 0.99 (200) | 1.00 | 1.00 | - | - | - | - |

## S2, the registered report's fields: permuted

| set | parsed | exact | valid | clean | agreement (n) | r3 bal. | r3 bal., misses | choice | main rule | contrary | forbidden |
|---|---|---|---|---|---|---|---|---|---|---|---|
| t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.64 [0.43, 0.82] (16/25) | 0.96 [0.80, 1.00] (24/25) | 0.96 [0.80, 1.00] (24/25) | 0.96 (25) | - | - | 0.64 [0.43, 0.82] (16/25) | 0.64 [0.43, 0.82] (16/25) | - | 0.00 [0.00, 0.14] (0/25) |
| t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.72 [0.51, 0.88] (18/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 (25) | - | - | 0.72 [0.51, 0.88] (18/25) | 0.72 [0.51, 0.88] (18/25) | 0.76 [0.55, 0.91] (19/25) | 0.00 [0.00, 0.14] (0/25) |
| t9_reuse reuse_fails | 0.96 [0.80, 1.00] (24/25) | 0.28 [0.12, 0.49] (7/25) | 0.32 [0.15, 0.54] (8/25) | 0.32 [0.15, 0.54] (8/25) | 0.33 (24) | - | - | 0.28 [0.12, 0.49] (7/25) | - | - | 0.04 [0.00, 0.20] (1/25) |
| t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.52 [0.31, 0.72] (13/25) | 0.48 [0.28, 0.69] (12/25) | 0.52 (25) | - | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| test | 0.94 [0.90, 0.97] (189/200) | 0.55 [0.47, 0.62] (109/200) | 0.65 [0.57, 0.71] (129/200) | 0.64 [0.56, 0.70] (127/200) | 0.66 (189) | 0.89 | 0.84 | - | - | - | - |

## Stops, chained: v1

| set | stopped | codes |
|---|---|---|
| t8_decoy decoy_first | 0.00 [0.00, 0.14] (0/25) | - |
| t8_decoy key_first | 0.00 [0.00, 0.14] (0/25) | - |
| t9_reuse reuse_fails | 0.00 [0.00, 0.14] (0/25) | - |
| t9_reuse reuse_ok | 0.00 [0.00, 0.14] (0/25) | - |
| table1 anon | 0.00 [0.00, 0.37] (0/8) | - |
| table1 named | 0.00 [0.00, 0.37] (0/8) | - |
| test | 0.00 [0.00, 0.02] (0/200) | - |

## Stops, chained: permuted

| set | stopped | codes |
|---|---|---|
| t8_decoy decoy_first | 0.00 [0.00, 0.14] (0/25) | - |
| t8_decoy key_first | 0.00 [0.00, 0.14] (0/25) | - |
| t9_reuse reuse_fails | 0.04 [0.00, 0.20] (1/25) | {'empty:fold_candidates': 1} |
| t9_reuse reuse_ok | 0.00 [0.00, 0.14] (0/25) | - |
| test | 0.06 [0.03, 0.10] (11/200) | {'empty:fold_candidates': 10, 'empty:contrary_facts': 1} |

## Steps at the reference's states (gold): split:test

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 200 | 0.995 | - | - | 0 | - | - | - |
| subsume | 753 | 1.000 | 1.000 | 0.943 | 0 | 1.000 (753) | - | - |
| fold_candidates | 349 | 1.000 | - | - | 0 | - | 1.000 (349) | - |
| check | 457 | 0.998 | 0.998 | 0.774 | 0 | 0.996 (457) | - | - |
| reuse_scan | 237 | 1.000 | - | - | 0 | - | - | - |
| reuse_check | 128 | 1.000 | 1.000 | 1.000 | 0 | - | - | - |
| contrary_facts | 109 | 1.000 | - | - | 0 | - | - | - |
| cell after_l39_check | 19 | 1.000 | 1.000 | 0.500 | 0 | 1.000 (19) | - | - |
| cell first_check | 200 | 0.995 | 0.995 | 0.558 | 0 | 0.995 (200) | - | - |
| cell later_role_subsume | 444 | 1.000 | 1.000 | 0.500 | 0 | 1.000 (444) | - | - |
| cell role_reuse_check | 19 | 1.000 | - | - | 0 | - | - | - |
| cell second_path_check | 40 | 1.000 | 1.000 | 0.500 | 0 | 1.000 (40) | - | - |

## Steps at the reference's states (gold): split:heldout

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 100 | 1.000 | - | - | 0 | - | - | - |
| subsume | 299 | 0.983 | 0.983 | 1.000 | 0 | 0.983 (299) | - | - |
| fold_candidates | 150 | 1.000 | - | - | 0 | - | 1.000 (150) | - |
| check | 250 | 1.000 | 1.000 | 0.524 | 0 | 0.996 (250) | - | - |
| reuse_scan | 175 | 1.000 | - | - | 0 | - | - | - |
| reuse_check | 125 | 0.600 | 0.375 | 0.500 | 0 | - | - | - |
| contrary_facts | 50 | 1.000 | - | - | 0 | - | - | - |
| cell after_l39_check | 25 | 1.000 | - | - | 0 | 1.000 (25) | - | - |
| cell first_check | 100 | 1.000 | 1.000 | 0.500 | 0 | 1.000 (100) | - | - |
| cell later_role_subsume | 149 | 0.966 | - | - | 0 | 0.966 (149) | - | - |
| cell role_reuse_check | 50 | 0.500 | 0.500 | 0.500 | 0 | - | - | - |

## Steps at the reference's states (gold): tier:t9_reuse

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 50 | 1.000 | - | - | 0 | - | - | - |
| subsume | 146 | 0.966 | 0.965 | 1.000 | 0 | 0.966 (146) | - | - |
| fold_candidates | 75 | 1.000 | - | - | 0 | - | 1.000 (75) | - |
| check | 150 | 1.000 | 1.000 | 0.300 | 0 | 0.993 (150) | - | - |
| reuse_scan | 125 | 1.000 | - | - | 0 | - | - | - |
| reuse_check | 100 | 0.500 | 0.333 | 0.500 | 0 | - | - | - |
| contrary_facts | 25 | 1.000 | - | - | 0 | - | - | - |
| cell after_l39_check | 25 | 1.000 | - | - | 0 | 1.000 (25) | - | - |
| cell first_check | 50 | 1.000 | - | - | 0 | 1.000 (50) | - | - |
| cell later_role_subsume | 71 | 0.930 | - | - | 0 | 0.930 (71) | - | - |
| cell role_reuse_check | 50 | 0.500 | 0.500 | 0.500 | 0 | - | - | - |

## Steps at the reference's states (gold): split:table1

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 16 | 0.438 | - | - | 0 | - | - | - |
| subsume | 142 | 0.669 | 0.683 | 0.744 | 0 | 0.729 (118) | - | - |
| fold_candidates | 54 | 0.630 | - | - | 2 | - | 0.731 (52) | - |
| check | 72 | 0.792 | 0.789 | 0.594 | 1 | 0.556 (63) | - | - |
| reuse_scan | 58 | 0.707 | - | - | 0 | - | - | - |
| reuse_check | 30 | 0.800 | 0.750 | 0.500 | 0 | - | - | - |
| contrary_facts | 28 | 0.214 | - | - | 0 | - | - | - |
| cell after_l39_check | 8 | 0.500 | 0.667 | 1.000 | 0 | 0.500 (6) | - | - |
| cell first_check | 16 | 0.688 | 0.792 | 0.500 | 0 | 0.571 (14) | - | - |
| cell later_role_subsume | 64 | 0.812 | 0.679 | 0.500 | 0 | 0.823 (62) | - | - |
| cell role_reuse_check | 8 | 1.000 | - | - | 0 | - | - | - |
| cell second_path_check | 8 | 1.000 | - | - | 0 | 1.000 (6) | - | - |

## Steps on the model's own run (chained): split:test

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 200 | 0.995 | - | - | 0 | - | - | 0.995 (200) |
| subsume | 753 | 0.992 | 0.992 | - | 0 | - | - | 1.000 (743) |
| fold_candidates | 349 | 0.997 | - | - | 0 | - | - | 1.000 (344) |
| check | 457 | 0.991 | 0.992 | - | 0 | - | - | 0.998 (449) |
| reuse_scan | 236 | 1.000 | - | - | 0 | - | - | 1.000 (231) |
| reuse_check | 128 | 0.992 | 0.976 | - | 0 | - | - | 1.000 (125) |
| contrary_facts | 108 | 0.982 | - | - | 0 | - | - | 1.000 (106) |
| cell after_l39_check | 20 | 0.950 | 0.929 | - | 0 | - | - | - |
| cell first_check | 200 | 0.995 | 0.995 | - | 0 | - | - | - |
| cell later_role_subsume | 445 | 0.987 | 0.943 | - | 0 | - | - | - |
| cell role_reuse_check | 20 | 0.950 | 0.500 | - | 0 | - | - | - |
| cell second_path_check | 41 | 1.000 | 1.000 | - | 0 | - | - | - |

## Steps on the model's own run (chained): split:heldout

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 100 | 1.000 | - | - | 0 | - | - | 1.000 (100) |
| subsume | 324 | 1.000 | 1.000 | - | 0 | - | - | 1.000 (265) |
| fold_candidates | 175 | 1.000 | - | - | 0 | - | - | 1.000 (150) |
| check | 250 | 1.000 | 1.000 | - | 0 | - | - | 1.000 (200) |
| reuse_scan | 200 | 1.000 | - | - | 0 | - | - | 1.000 (150) |
| reuse_check | 125 | 0.400 | 0.250 | - | 0 | - | - | 0.500 (100) |
| contrary_facts | 75 | 1.000 | - | - | 0 | - | - | 1.000 (50) |
| cell after_l39_check | 50 | 1.000 | - | - | 0 | - | - | - |
| cell first_check | 100 | 1.000 | 1.000 | - | 0 | - | - | - |
| cell later_role_subsume | 149 | 1.000 | - | - | 0 | - | - | - |
| cell role_reuse_check | 50 | 0.500 | 0.500 | - | 0 | - | - | - |

## Steps on the model's own run (chained): tier:t9_reuse

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 50 | 1.000 | - | - | 0 | - | - | 1.000 (50) |
| subsume | 171 | 1.000 | 1.000 | - | 0 | - | - | 1.000 (112) |
| fold_candidates | 100 | 1.000 | - | - | 0 | - | - | 1.000 (75) |
| check | 150 | 1.000 | - | - | 0 | - | - | 1.000 (100) |
| reuse_scan | 150 | 1.000 | - | - | 0 | - | - | 1.000 (100) |
| reuse_check | 100 | 0.250 | 0.167 | - | 0 | - | - | 0.333 (75) |
| contrary_facts | 50 | 1.000 | - | - | 0 | - | - | 1.000 (25) |
| cell after_l39_check | 50 | 1.000 | - | - | 0 | - | - | - |
| cell first_check | 50 | 1.000 | - | - | 0 | - | - | - |
| cell later_role_subsume | 71 | 1.000 | - | - | 0 | - | - | - |
| cell role_reuse_check | 50 | 0.500 | 0.500 | - | 0 | - | - | - |

## Steps on the model's own run (chained): split:table1

| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set | at reference state |
|---|---|---|---|---|---|---|---|---|
| role | 16 | 0.438 | - | - | 0 | - | - | 0.438 (16) |
| subsume | 86 | 0.477 | - | - | 0 | - | - | 0.714 (7) |
| fold_candidates | 41 | 0.683 | - | - | 0 | - | - | 0.800 (5) |
| check | 61 | 0.590 | - | - | 0 | - | - | 0.250 (4) |
| reuse_scan | 36 | 0.556 | - | - | 0 | - | - | 1.000 (1) |
| reuse_check | 23 | 0.870 | - | - | 0 | - | - | - |
| contrary_facts | 13 | 0.000 | - | - | 0 | - | - | 0.000 (1) |
| cell after_l39_check | 5 | 0.800 | - | - | 0 | - | - | - |
| cell first_check | 14 | 0.571 | - | - | 0 | - | - | - |
| cell later_role_subsume | 55 | 0.236 | - | - | 0 | - | - | - |
| cell role_reuse_check | 5 | 1.000 | - | - | 0 | - | - | - |
| cell second_path_check | 13 | 0.385 | - | - | 0 | - | - | - |

## Exact McNemar

| contrast | n | S2 only | other only | p |
|---|---|---|---|---|
| v1 t8_decoy decoy_first: s2 vs sft_trace | 25 | 25 | 0 | 0.0000 |
| v1 t8_decoy key_first: s2 vs sft_trace | 25 | 12 | 0 | 0.0005 |
| v1 t9_reuse reuse_fails: s2 vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_ok: s2 vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 table1 anon: s2 vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 table1 named: s2 vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 test: s2 vs sft_trace | 200 | 109 | 0 | 0.0000 |
| v1 t8_decoy decoy_first: s2 vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 t8_decoy key_first: s2 vs sft_endpoint | 25 | 25 | 0 | 0.0000 |
| v1 t9_reuse reuse_fails: s2 vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_ok: s2 vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 table1 anon: s2 vs sft_endpoint | 8 | 0 | 0 | 1.0000 |
| v1 table1 named: s2 vs sft_endpoint | 8 | 0 | 0 | 1.0000 |
| v1 test: s2 vs sft_endpoint | 200 | 0 | 2 | 0.5000 |
| permuted t8_decoy decoy_first: s2 vs sft_trace | 25 | 15 | 0 | 0.0001 |
| permuted t8_decoy key_first: s2 vs sft_trace | 25 | 12 | 3 | 0.0352 |
| permuted t9_reuse reuse_fails: s2 vs sft_trace | 25 | 6 | 1 | 0.1250 |
| permuted t9_reuse reuse_ok: s2 vs sft_trace | 25 | 0 | 0 | 1.0000 |
| permuted test: s2 vs sft_trace | 200 | 85 | 5 | 0.0000 |
| permuted t8_decoy decoy_first: s2 vs sft_endpoint | 25 | 7 | 5 | 0.7744 |
| permuted t8_decoy key_first: s2 vs sft_endpoint | 25 | 9 | 3 | 0.1460 |
| permuted t9_reuse reuse_fails: s2 vs sft_endpoint | 25 | 7 | 0 | 0.0156 |
| permuted t9_reuse reuse_ok: s2 vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| permuted test: s2 vs sft_endpoint | 200 | 38 | 19 | 0.0163 |

## Name invariance (exact, original against permuted; margin 0.05; the registered reading is the 'all' row)

| arm | split | original | permuted | delta [95%] | McNemar p | verdict |
|---|---|---|---|---|---|---|
| s2 | all | 0.83 [0.78, 0.87] (248/300) | 0.50 [0.44, 0.56] (150/300) | -0.327 [-0.383, -0.270] | 0.0000 | drop |
| s2 | test | 0.99 [0.96, 1.00] (198/200) | 0.55 [0.47, 0.62] (109/200) | -0.445 [-0.510, -0.375] | 0.0000 | drop |
| s2 | heldout | 0.50 [0.40, 0.60] (50/100) | 0.41 [0.31, 0.51] (41/100) | -0.090 [-0.180, +0.000] | 0.0931 | inconclusive |
| sft_trace | all | 0.34 [0.29, 0.40] (102/300) | 0.14 [0.10, 0.18] (41/300) | -0.203 [-0.267, -0.143] | 0.0000 | drop |
| sft_trace | test | 0.45 [0.37, 0.52] (89/200) | 0.14 [0.10, 0.20] (29/200) | -0.300 [-0.380, -0.215] | 0.0000 | drop |
| sft_trace | heldout | 0.13 [0.07, 0.21] (13/100) | 0.12 [0.06, 0.20] (12/100) | -0.010 [-0.090, +0.060] | 1.0000 | inconclusive |
| sft_endpoint | all | 0.75 [0.70, 0.80] (225/300) | 0.39 [0.33, 0.44] (116/300) | -0.363 [-0.423, -0.300] | 0.0000 | drop |
| sft_endpoint | test | 1.00 [0.98, 1.00] (200/200) | 0.45 [0.38, 0.52] (90/200) | -0.550 [-0.620, -0.480] | 0.0000 | drop |
| sft_endpoint | heldout | 0.25 [0.17, 0.35] (25/100) | 0.26 [0.18, 0.36] (26/100) | +0.010 [-0.080, +0.110] | 1.0000 | inconclusive |
