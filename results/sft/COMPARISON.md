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
| base | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.16 [0.05, 0.36] (4/25) | 0.12 [0.03, 0.31] (3/25) | 0.16 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| base | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| base | table1 named | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.12 [0.00, 0.53] (1/8) | 0.00 [0.00, 0.37] (0/8) | 0.33 (3) | - | - | - | - | - |
| base | test | 1.00 [0.98, 1.00] (200/200) | 0.00 [0.00, 0.02] (0/200) | 0.13 [0.09, 0.18] (26/200) | 0.07 [0.04, 0.12] (15/200) | 0.11 (200) | 0.51 | - | - | - | - |
| sft_endpoint | t8_decoy decoy_first | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | 1.00 (25) | - | 1.00 [0.86, 1.00] (25/25) | 1.00 [0.86, 1.00] (25/25) | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t8_decoy key_first | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t9_reuse reuse_fails | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 [0.00, 0.14] (0/25) | 0.00 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | t9_reuse reuse_ok | 1.00 [0.86, 1.00] (25/25) | 0.00 [0.00, 0.14] (0/25) | 0.84 [0.64, 0.95] (21/25) | 0.84 [0.64, 0.95] (21/25) | 0.84 (25) | - | 0.00 [0.00, 0.14] (0/25) | - | - | 0.00 [0.00, 0.14] (0/25) |
| sft_endpoint | table1 anon | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_endpoint | table1 named | 1.00 [0.63, 1.00] (8/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 [0.00, 0.37] (0/8) | 0.00 (3) | - | - | - | - | - |
| sft_endpoint | test | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 [0.98, 1.00] (200/200) | 1.00 (200) | 1.00 | - | - | - | - |

r3 balanced, held-out tiers pooled over both halves (undefined where one class): base t8_decoy 0.36, t9_reuse -; sft_endpoint t8_decoy 1.00, t9_reuse -

## Step level: v1

| arm | set | with trace | truncated | accuracy | written | omitted | subsume bal. | check bal. | reuse bal. | answer = trace | in support |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Exact by template novelty (all rows: is the gold string a train target?)

| corpus | arm | gold in train | gold not in train |
|---|---|---|---|
| v1 | base | 0.00 [0.00, 0.02] (0/225) | 0.00 [0.00, 0.04] (0/91) |
| v1 | sft_endpoint | 1.00 [0.98, 1.00] (225/225) | 0.00 [0.00, 0.04] (0/91) |

## Registered decisions

- pending: v1: 100 of 200 scores missing; permuted: 600 of 600 scores missing

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
