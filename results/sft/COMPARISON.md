# SFT arm comparison

Registered in compare_sft.py before the trace arm was scored. Proportions: value [Clopper-Pearson 95%] (k/n); means: value [bootstrap 95%].

## Floors (test rows; permuted: the tier's answer renamed by the problem's permutation, and literal as a name copier)

- v1, always guard: valid 0.99, clean 0.99, exact 0.43, agreement 0.72
- v1, always monotonic: valid 0.50, clean 0.50, exact 0.50, agreement 0.50
- permuted, always guard: valid 0.99, clean 0.99, exact 0.43, agreement 0.72
- permuted, name copier, always guard: valid 0.00, clean 0.00, exact 0.00, agreement 0.00
- permuted, always monotonic: valid 0.50, clean 0.50, exact 0.50, agreement 0.50
- permuted, name copier, always monotonic: valid 0.00, clean 0.00, exact 0.00, agreement 0.00

## Correctness and held-out choice: v1

| arm | set | parsed | exact | valid | clean | agreement (n) | r3 bal. | choice | main rule | contrary | forbidden |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.04 [0.00, 0.20] (1/25) | 0.00 [0.00, 0.14] (0/25) | 0.01 (25) | - | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | - | 0.00 [0.00, 0.14] (0/25) |
| base | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.04 [0.00, 0.20] (1/25) | 0.04 [0.00, 0.20] (1/25) | 0.04 (25) | - | 0.00 [0.00, 0.14] (0/25) | 0.04 [0.00, 0.20] (1/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| base | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| base | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.20 [0.07, 0.41] (5/25) | 0.16 [0.05, 0.36] (4/25) | 0.20 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| base | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| base | table1 named | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.12 [0.00, 0.53] (1/8) | 0.00 [0.00, 0.37] (0/8) | 0.33 (3) | - | - | - | - | - |
| base | test | 0.99 [0.97, 1.00] (199/200) | 0.00 [0.00, 0.02] (0/200) | 0.14 [0.09, 0.19] (27/200) | 0.08 [0.05, 0.13] (16/200) | 0.12 (199) | 0.50 | - | - | - | - |
| sft_endpoint | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 (25) | - | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.84 [0.64, 0.95] (21/25) | 0.84 [0.64, 0.95] (21/25) | 0.84 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_endpoint | table1 named | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_endpoint | test | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 (200) | 1.00 | - | - | - | - |
| sft_trace | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | - | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.52 [0.31, 0.72] (13/25) | 0.52 [0.31, 0.72] (13/25) | 0.52 [0.31, 0.72] (13/25) | 0.52 (25) | - | 0.52 [0.31, 0.72] (13/25) | 1.00 [0.86, 1.00] (25/25) | 0.52 [0.31, 0.72] (13/25) | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_trace | table1 named | 0.75 [0.35, 0.97] (6/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_trace | test | 1.00 [0.98, 1.00] (200/200) | 0.45 [0.37, 0.52] (89/200) | 0.69 [0.62, 0.75] (138/200) | 0.68 [0.61, 0.74] (135/200) | 0.58 (200) | 0.45 | - | - | - | - |

r3 balanced, held-out tiers pooled over both halves (undefined where one class): base t8_decoy 0.36, t9_reuse -; sft_endpoint t8_decoy 1.00, t9_reuse -; sft_trace t8_decoy 0.50, t9_reuse -

## Step level: v1

| arm | set | with trace | truncated | accuracy | written | omitted | subsume bal. | check bal. | reuse bal. | answer = trace | in support |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sft_trace | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.565 [0.56, 0.57] | 0.565 [0.56, 0.57] | 0.000 | 0.80 | 0.00 | - | 1.00 [0.86, 1.00] (25/25) | - |
| sft_trace | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.933 [0.91, 0.96] | 0.964 [0.95, 0.98] | 0.033 | 1.00 | 1.00 | - | 0.52 [0.31, 0.72] (13/25) | - |
| sft_trace | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.829 [0.78, 0.87] | 0.829 [0.78, 0.87] | 0.000 | 0.84 | - | - | 0.80 [0.59, 0.93] (20/25) | - |
| sft_trace | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.781 [0.72, 0.83] | 0.781 [0.72, 0.83] | 0.000 | 0.87 | - | 0.00 | 0.92 [0.74, 0.99] (23/25) | - |
| sft_trace | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.554 [0.40, 0.67] | 0.571 [0.41, 0.69] | 0.040 | 0.65 | - | - | 0.75 [0.35, 0.97] (6/8) | 0.12 [0.00, 0.53] (1/8) |
| sft_trace | table1 named | 1.00 [0.63, 1.00] (8/8) | 0.25 [0.03, 0.65] (2/8) | 0.420 [0.24, 0.58] | 0.554 [0.39, 0.71] | 0.744 | 0.53 | - | - | 0.75 [0.35, 0.97] (6/8) | 0.12 [0.00, 0.53] (1/8) |
| sft_trace | test | 1.00 [0.98, 1.00] (200/200) | 0.00 [0.00, 0.02] (0/200) | 0.778 [0.75, 0.81] | 0.779 [0.75, 0.81] | 0.003 | 0.75 | 0.65 | 1.00 | 0.99 [0.96, 1.00] (198/200) | - |

Per kind (right/required) and correctness x fidelity:

- sft_trace, t8_decoy decoy_first: role 1.00 (25/25), subsume 0.72 (63/88), fold_candidates 0.50 (25/50), check 0.00 (0/50), reuse_scan 1.00 (25/25), introduce 1.00 (25/25), contrary_facts 0.00 (0/25). Per problem: not exact / unfaithful 25; any illegal 1.00 [0.86, 1.00] (25/25); halted 0.00 [0.00, 0.14] (0/25)
- sft_trace, t8_decoy key_first: role 1.00 (25/25), subsume 1.00 (90/90), fold_candidates 0.76 (38/50), check 0.84 (63/75), reuse_scan 1.00 (50/50), reuse_check 1.00 (25/25), introduce 1.00 (25/25), contrary_facts 1.00 (25/25). Per problem: exact / faithful 13, not exact / unfaithful 12; any illegal 0.48 [0.28, 0.69] (12/25); halted 0.00 [0.00, 0.14] (0/25); omitted with no truth, outside balanced: {'check': 12}
- sft_trace, t9_reuse reuse_fails: role 1.00 (25/25), subsume 0.76 (58/76), fold_candidates 0.97 (38/39), check 0.81 (51/63), reuse_scan 1.00 (51/51), reuse_check 0.66 (25/38), introduce 1.00 (26/26), contrary_facts 1.00 (13/13). Per problem: not exact / unfaithful 25; any illegal 1.00 [0.86, 1.00] (25/25); halted 0.00 [0.00, 0.14] (0/25)
- sft_trace, t9_reuse reuse_ok: role 1.00 (25/25), subsume 0.80 (61/76), fold_candidates 1.00 (42/42), check 0.88 (59/67), reuse_scan 1.00 (59/59), reuse_check 0.00 (0/42), introduce 1.00 (34/34), contrary_facts 1.00 (17/17). Per problem: not exact / unfaithful 25; any illegal 1.00 [0.86, 1.00] (25/25); halted 0.00 [0.00, 0.14] (0/25)
- sft_trace, table1 anon: role 0.38 (3/8), subsume 0.35 (17/49), fold_candidates 0.57 (8/14), check 0.67 (14/21), reuse_scan 0.67 (10/15), introduce 0.86 (6/7), contrary_facts 0.14 (1/7), reuse_check 0.80 (4/5). Per problem: not exact / unfaithful 8; any illegal 1.00 [0.63, 1.00] (8/8); halted 0.00 [0.00, 0.37] (0/8); omitted with no truth, outside balanced: {'check': 2}; minted reuse where right: none reached
- sft_trace, table1 named: role 0.62 (5/8), subsume 0.07 (13/186), fold_candidates 0.36 (4/11), check 0.06 (9/158), reuse_scan 0.70 (7/10), introduce 0.80 (4/5), contrary_facts 0.25 (1/4), reuse_check 0.60 (3/5). Per problem: not exact / unfaithful 8; any illegal 1.00 [0.63, 1.00] (8/8); halted 0.00 [0.00, 0.37] (0/8); omitted with no truth, outside balanced: {'check': 144}; minted reuse where right: none reached
- sft_trace, test: role 0.99 (199/200), subsume 0.74 (548/737), fold_candidates 0.91 (302/333), check 0.64 (254/395), reuse_scan 0.97 (177/182), reuse_check 1.00 (80/80), introduce 0.97 (113/116), contrary_facts 0.42 (41/97). Per problem: exact / faithful 86, exact / unfaithful 3, not exact / unfaithful 111; any illegal 0.43 [0.36, 0.50] (86/200); halted 0.00 [0.00, 0.02] (0/200); omitted with no truth, outside balanced: {'check': 2}

## Correctness and held-out choice: permuted

| arm | set | parsed | exact | valid | clean | agreement (n) | r3 bal. | choice | main rule | contrary | forbidden |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | - | 0.00 [0.00, 0.14] (0/25) |
| base | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.12 [0.03, 0.31] (3/25) | 0.00 [0.00, 0.14] (0/25) | 0.12 (25) | - | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| base | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| base | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.32 [0.15, 0.54] (8/25) | 0.16 [0.05, 0.36] (4/25) | 0.32 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| base | test | 0.99 [0.96, 1.00] (198/200) | 0.00 [0.00, 0.02] (0/200) | 0.05 [0.02, 0.09] (10/200) | 0.02 [0.01, 0.05] (4/200) | 0.03 (198) | 0.49 | - | - | - | - |
| sft_endpoint | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.56 [0.35, 0.76] (14/25) | 0.88 [0.69, 0.97] (22/25) | 0.88 [0.69, 0.97] (22/25) | 0.84 (25) | - | 0.56 [0.35, 0.76] (14/25) | 0.56 [0.35, 0.76] (14/25) | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.48 [0.28, 0.69] (12/25) | 0.60 [0.39, 0.79] (15/25) | 0.60 [0.39, 0.79] (15/25) | 0.60 (25) | - | 0.48 [0.28, 0.69] (12/25) | 0.64 [0.43, 0.82] (16/25) | 0.64 [0.43, 0.82] (16/25) | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.12 [0.03, 0.31] (3/25) | 0.12 [0.03, 0.31] (3/25) | 0.12 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.12 [0.03, 0.31] (3/25) |
| sft_endpoint | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.36 [0.18, 0.57] (9/25) | 0.36 [0.18, 0.57] (9/25) | 0.34 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.04 [0.00, 0.20] (1/25) |
| sft_endpoint | test | 1.00 [0.98, 1.00] (200/200) | 0.45 [0.38, 0.52] (90/200) | 0.51 [0.43, 0.58] (101/200) | 0.50 [0.43, 0.57] (100/200) | 0.48 (200) | 0.88 | - | - | - | - |
| sft_trace | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.04 [0.00, 0.20] (1/25) | 0.48 [0.28, 0.69] (12/25) | 0.40 [0.21, 0.61] (10/25) | 0.43 (25) | - | 0.04 [0.00, 0.20] (1/25) | 0.04 [0.00, 0.20] (1/25) | - | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.36 [0.18, 0.57] (9/25) | 0.44 [0.24, 0.65] (11/25) | 0.44 [0.24, 0.65] (11/25) | 0.42 (25) | - | 0.36 [0.18, 0.57] (9/25) | 0.56 [0.35, 0.76] (14/25) | 0.52 [0.31, 0.72] (13/25) | 0.00 [0.00, 0.14] (0/25) |
| sft_trace | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.08 [0.01, 0.26] (2/25) | 0.20 [0.07, 0.41] (5/25) | 0.20 [0.07, 0.41] (5/25) | 0.20 (25) | - | 0.08 [0.01, 0.26] (2/25) | - | - | 0.12 [0.03, 0.31] (3/25) |
| sft_trace | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.28 [0.12, 0.49] (7/25) | 0.28 [0.12, 0.49] (7/25) | 0.27 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.12 [0.03, 0.31] (3/25) |
| sft_trace | test | 1.00 [0.98, 1.00] (200/200) | 0.14 [0.10, 0.20] (29/200) | 0.24 [0.18, 0.31] (48/200) | 0.22 [0.16, 0.28] (44/200) | 0.20 (200) | 0.51 | - | - | - | - |

r3 balanced, held-out tiers pooled over both halves (undefined where one class): base t8_decoy 0.46, t9_reuse -; sft_endpoint t8_decoy 0.74, t9_reuse -; sft_trace t8_decoy 0.46, t9_reuse -

## Step level: permuted

| arm | set | with trace | truncated | accuracy | written | omitted | subsume bal. | check bal. | reuse bal. | answer = trace | in support |
|---|---|---|---|---|---|---|---|---|---|---|---|
| sft_trace | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.716 [0.65, 0.79] | 0.721 [0.65, 0.79] | 0.006 | 0.83 | 0.49 | - | 0.92 [0.74, 0.99] (23/25) | - |
| sft_trace | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.737 [0.66, 0.81] | 0.742 [0.66, 0.82] | 0.006 | 0.84 | 0.61 | - | 0.96 [0.80, 1.00] (24/25) | - |
| sft_trace | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.693 [0.66, 0.73] | 0.698 [0.67, 0.73] | 0.006 | 0.96 | 0.70 | - | 0.92 [0.74, 0.99] (23/25) | - |
| sft_trace | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.659 [0.61, 0.71] | 0.668 [0.62, 0.72] | 0.009 | 0.94 | 0.66 | 0.40 | 0.80 [0.59, 0.93] (20/25) | - |
| sft_trace | test | 1.00 [0.98, 1.00] (200/200) | 0.00 [0.00, 0.02] (0/200) | 0.679 [0.65, 0.71] | 0.691 [0.66, 0.72] | 0.019 | 0.73 | 0.49 | 0.97 | 0.81 [0.75, 0.87] (163/200) | - |

Per kind (right/required) and correctness x fidelity:

- sft_trace, t8_decoy decoy_first: role 1.00 (25/25), subsume 0.82 (71/87), fold_candidates 0.65 (31/48), check 0.47 (28/59), reuse_scan 0.79 (30/38), introduce 0.92 (23/25), contrary_facts 0.33 (8/24), reuse_check 1.00 (6/6). Per problem: exact / faithful 1, not exact / faithful 3, not exact / unfaithful 21; any illegal 0.56 [0.35, 0.76] (14/25); halted 0.00 [0.00, 0.14] (0/25); omitted with no truth, outside balanced: {'check': 1}
- sft_trace, t8_decoy key_first: role 1.00 (25/25), subsume 0.83 (72/87), fold_candidates 0.63 (29/46), check 0.63 (37/59), reuse_scan 0.81 (30/37), reuse_check 1.00 (8/8), introduce 0.91 (21/23), contrary_facts 0.64 (14/22). Per problem: exact / faithful 6, exact / unfaithful 3, not exact / unfaithful 16; any illegal 0.64 [0.43, 0.82] (16/25); halted 0.00 [0.00, 0.14] (0/25); omitted with no truth, outside balanced: {'check': 1}
- sft_trace, t9_reuse reuse_fails: role 1.00 (25/25), subsume 0.95 (80/84), fold_candidates 0.49 (23/47), check 0.71 (44/62), reuse_scan 0.26 (11/42), introduce 0.28 (7/25), contrary_facts 0.96 (22/23), reuse_check 1.00 (13/13). Per problem: exact / unfaithful 2, not exact / unfaithful 23; any illegal 0.80 [0.59, 0.93] (20/25); halted 0.00 [0.00, 0.14] (0/25); omitted with no truth, outside balanced: {'check': 1}
- sft_trace, t9_reuse reuse_ok: role 1.00 (25/25), subsume 0.93 (75/81), fold_candidates 0.34 (16/47), check 0.70 (43/61), reuse_scan 0.37 (16/43), reuse_check 0.67 (8/12), introduce 0.44 (12/27), contrary_facts 0.95 (21/22). Per problem: not exact / unfaithful 25; any illegal 0.72 [0.51, 0.88] (18/25); halted 0.00 [0.00, 0.14] (0/25); omitted with no truth, outside balanced: {'check': 3}
- sft_trace, test: role 0.98 (196/200), subsume 0.71 (564/799), fold_candidates 0.60 (212/355), check 0.52 (223/433), reuse_scan 0.81 (224/275), reuse_check 0.95 (56/59), introduce 0.91 (156/171), contrary_facts 0.40 (68/170). Per problem: exact / faithful 21, exact / unfaithful 8, not exact / faithful 3, not exact / unfaithful 168; any illegal 0.79 [0.72, 0.84] (157/200); halted 0.00 [0.00, 0.02] (0/200); omitted with no truth, outside balanced: {'check': 28}

## Exact by template novelty (all rows: is the gold string a train target?)

| corpus | arm | gold in train | gold not in train |
|---|---|---|---|
| v1 | base | 0.00 [0.00, 0.02] (0/225) | 0.00 [0.00, 0.04] (0/91) |
| v1 | sft_endpoint | 1.00 [0.98, 1.00] (225/225) | 0.00 [0.00, 0.04] (0/91) |
| v1 | sft_trace | 0.40 [0.33, 0.46] (89/225) | 0.14 [0.08, 0.23] (13/91) |
| permuted | base | 0.00 [0.00, 0.84] (0/2) | 0.00 [0.00, 0.01] (0/298) |
| permuted | sft_endpoint | 0.00 [0.00, 0.84] (0/2) | 0.39 [0.33, 0.45] (116/298) |
| permuted | sft_trace | 0.00 [0.00, 0.84] (0/2) | 0.14 [0.10, 0.18] (41/298) |

## Name invariance (exact, original against permuted; margin 0.05; the registered verdict is the 'all' row)

| arm | split | original | permuted | delta [95%] | McNemar p | verdict |
|---|---|---|---|---|---|---|
| base | all | 0.00 [0.00, 0.01] (0/300) | 0.00 [0.00, 0.01] (0/300) | +0.000 [+0.000, +0.000] | 1.0000 | invariant within +-0.05 |
| base | test | 0.00 [0.00, 0.02] (0/200) | 0.00 [0.00, 0.02] (0/200) | +0.000 [+0.000, +0.000] | 1.0000 | invariant within +-0.05 |
| base | heldout | 0.00 [0.00, 0.04] (0/100) | 0.00 [0.00, 0.04] (0/100) | +0.000 [+0.000, +0.000] | 1.0000 | invariant within +-0.05 |
| sft_endpoint | all | 0.75 [0.70, 0.80] (225/300) | 0.39 [0.33, 0.44] (116/300) | -0.363 [-0.423, -0.300] | 0.0000 | drop |
| sft_endpoint | test | 1.00 [0.98, 1.00] (200/200) | 0.45 [0.38, 0.52] (90/200) | -0.550 [-0.620, -0.480] | 0.0000 | drop |
| sft_endpoint | heldout | 0.25 [0.17, 0.35] (25/100) | 0.26 [0.18, 0.36] (26/100) | +0.010 [-0.080, +0.110] | 1.0000 | inconclusive |
| sft_trace | all | 0.34 [0.29, 0.40] (102/300) | 0.14 [0.10, 0.18] (41/300) | -0.203 [-0.267, -0.143] | 0.0000 | drop |
| sft_trace | test | 0.45 [0.37, 0.52] (89/200) | 0.14 [0.10, 0.20] (29/200) | -0.300 [-0.380, -0.215] | 0.0000 | drop |
| sft_trace | heldout | 0.13 [0.07, 0.21] (13/100) | 0.12 [0.06, 0.20] (12/100) | -0.010 [-0.090, +0.060] | 1.0000 | inconclusive |

## Registered decisions

- trace against endpoint, exact over held-out + permuted: 28 trace only, 115 endpoint only of 400, McNemar p 1.018e-13
- RL base: sft_endpoint
- token-matched endpoint run: no

## Arm against arm (exact, exact McNemar)

| contrast | n | first only | second only | p |
|---|---|---|---|---|
| v1 t8_decoy decoy_first: base vs sft_endpoint | 25 | 0 | 25 | 0.0000 |
| v1 t8_decoy key_first: base vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_fails: base vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_ok: base vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| v1 table1 anon: base vs sft_endpoint | 8 | 0 | 0 | 1.0000 |
| v1 table1 named: base vs sft_endpoint | 8 | 0 | 0 | 1.0000 |
| v1 test: base vs sft_endpoint | 200 | 0 | 200 | 0.0000 |
| permuted t8_decoy decoy_first: base vs sft_endpoint | 25 | 0 | 14 | 0.0001 |
| permuted t8_decoy key_first: base vs sft_endpoint | 25 | 0 | 12 | 0.0005 |
| permuted t9_reuse reuse_fails: base vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| permuted t9_reuse reuse_ok: base vs sft_endpoint | 25 | 0 | 0 | 1.0000 |
| permuted test: base vs sft_endpoint | 200 | 0 | 90 | 0.0000 |
| v1 t8_decoy decoy_first: base vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 t8_decoy key_first: base vs sft_trace | 25 | 0 | 13 | 0.0002 |
| v1 t9_reuse reuse_fails: base vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_ok: base vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 table1 anon: base vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 table1 named: base vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 test: base vs sft_trace | 200 | 0 | 89 | 0.0000 |
| permuted t8_decoy decoy_first: base vs sft_trace | 25 | 0 | 1 | 1.0000 |
| permuted t8_decoy key_first: base vs sft_trace | 25 | 0 | 9 | 0.0039 |
| permuted t9_reuse reuse_fails: base vs sft_trace | 25 | 0 | 2 | 0.5000 |
| permuted t9_reuse reuse_ok: base vs sft_trace | 25 | 0 | 0 | 1.0000 |
| permuted test: base vs sft_trace | 200 | 0 | 29 | 0.0000 |
| v1 t8_decoy decoy_first: sft_endpoint vs sft_trace | 25 | 25 | 0 | 0.0000 |
| v1 t8_decoy key_first: sft_endpoint vs sft_trace | 25 | 0 | 13 | 0.0002 |
| v1 t9_reuse reuse_fails: sft_endpoint vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 t9_reuse reuse_ok: sft_endpoint vs sft_trace | 25 | 0 | 0 | 1.0000 |
| v1 table1 anon: sft_endpoint vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 table1 named: sft_endpoint vs sft_trace | 8 | 0 | 0 | 1.0000 |
| v1 test: sft_endpoint vs sft_trace | 200 | 111 | 0 | 0.0000 |
| permuted t8_decoy decoy_first: sft_endpoint vs sft_trace | 25 | 13 | 0 | 0.0002 |
| permuted t8_decoy key_first: sft_endpoint vs sft_trace | 25 | 7 | 4 | 0.5488 |
| permuted t9_reuse reuse_fails: sft_endpoint vs sft_trace | 25 | 0 | 2 | 0.5000 |
| permuted t9_reuse reuse_ok: sft_endpoint vs sft_trace | 25 | 0 | 0 | 1.0000 |
| permuted test: sft_endpoint vs sft_trace | 200 | 70 | 9 | 0.0000 |
