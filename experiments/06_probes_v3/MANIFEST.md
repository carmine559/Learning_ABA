# Set 06 — Step probes v3, five models at 4-bit

The step probes ask for one decision of Algorithm 1 at a state the reference visits. This
set re-runs them with probe prompts **v3**, which fix three defects measured in set 05's
answers, and with the `introduce` probe scored as Algorithm 1 prints lines 36–44. The
reading was fixed before the run ([METHOD_HISTORY.md](../../docs/METHOD_HISTORY.md),
Phase 10).

| Field | Value |
| --- | --- |
| Date | 2026-10-27 |
| Models | Qwen2.5 3B / 7B / 14B / 32B and Mistral-7B, all `--load-4bit` |
| Backend | `local` (L40, DISI cluster), jobs 73946–73950 |
| Code | `df969d1`; probe code as in `99c7a0f` |
| Dataset | 103 problems, 5 tiers, anonymised, `--benchmark 20`, seed 42 (as set 05) |
| Probes | 845 per model: role 103, fold 186, check 186, introduce 166, subsume 204 |
| Decoding | greedy, k = 1, `--max-tokens 512`; no answer reaches the cap |
| **Probe-prompt version** | **v3** (stamped in every `probe_summary.json`) |
| Reference | after METHOD_HISTORY Phase 8 |
| Status | done; read by hand on 25 rows before any aggregate |

## Command

```bash
OUT_ROOT=results/probes_v3 PROBES=1 \
    MODELS="qwen2.5-3b qwen2.5-7b qwen2.5-14b qwen2.5-32b mistral-7b" \
    EXTRA="--load-4bit" bash cluster/submit_benchmarks.sh
```

The outputs were then moved here. Generation took 59 minutes over the five models.
`logs/` holds the SLURM logs of the run and of a first launch (jobs 73935–73939). That
launch stopped at start-up with `ModuleNotFoundError: No module named
'extras.aba_visualization'`: the cluster's scratch storage had deleted files that no one
had read for 40 days.

## What changed since set 05

1. **Probe prompts v2 → v3**, three changes, each tied to a defect measured in set 05's
   answers:
   - `check` defines a failing example;
   - `role` drops v2's clause about contraries and says that facts are only for predicates
     in T;
   - `introduce` states Definition 4 and lines 36 and 41.
2. **`introduce` is scored as printed.** An answer is right iff it guards the folded rule
   and takes line 36's branch (an assumption relative to the body, when one exists) or
   line 41's (a new assumption with a new contrary, when none does). It is reported per
   branch and balanced over the two.
3. **The states are the corrected reference's.** 335 of the 780 set-05 probe ids are not
   in this set; 81 of the 166 `introduce` states now take line 36's branch. The `role`
   probes are the same 103 items as in set 05.

## Results against the no-reasoning floors

`python analysis/null_baselines.py --set experiments/06_probes_v3`. Metrics: F1 for
`role`, accuracy for `fold`, balanced accuracy for the other three. The intervals are 95%
bootstrap intervals over problems. Each floor is the best of the no-reasoning policies
measured on the same probes.

| probe | floor | 3B | 7B | 14B | 32B | Mistral |
| --- | --- | --- | --- | --- | --- | --- |
| `role` (line 8) | 0.994 | 0.000 | 0.000 | 0.736 | 0.744 | 0.542 |
| `fold` (line 17) | 1.000 | 0.032 | 0.129 | 0.113 | 0.403 | 0.403 |
| `check` (line 18) | 0.633 | 0.500 | 0.500 | 0.582 [0.527, 0.636] | 0.500 | 0.500 |
| `introduce` (lines 36/41) | 0.855 | 0.469 | 0.111 | 0.196 | 0.076 | 0.476 |
| `subsume` (line 16) | 0.762 | 0.647 [0.571, 0.715] | 0.500 | 0.500 | 0.520 | 0.525 |

**No model performs any of the five steps above a policy that does no reasoning.**

The floors:

- **`role`:** writing one fact per positive example scores F1 0.994. RoLe's answer is the
  positive examples on 102 of the 103 problems. Every right `role` answer of every model is
  that copy (14B 74, 32B 71, Mistral 51).
- **`fold`:** folding onto dom(X) scores 1.000. dom(X) is a legal fold at every state
  (Definition 3), and the probe accepts any legal fold.
- **`check`:** YES iff the state lists introduced assumptions, 0.633.
- **`introduce`:** reuse the last assumption the state lists as introduced, else a new
  one: 0.855. Always answering a new assumption gets 0.500.
- **`subsume`:** YES iff the state lists a learnt rule with no equality, 0.762.

The registered floors of `role` (always NONE) and `fold` (the rule copied back) were 0, and
`subsume`'s was 0.663; the stronger policies were found after the run. Against the
registered floors, `role` (14B, 32B, Mistral) and `fold` (every model) lie above. No
verdict on `check`, `introduce` or `subsume` depends on the choice.

## What the answers show

- **Line 18: one misreading, unchanged by the prompt.** 3B, 7B and 32B answer NO to all
  186 `check` probes. They list exactly the negative examples as failing on 172, 177 and
  168, although v3 says that being a negative example does not make an example fail. 32B
  did the same under v1 (160 of 186) and v2 (180). Mistral answers YES to all 186. 14B
  answers NO on 131 and lists the negative examples on 28 (v2: 114 of 179). It follows no
  cue we tested, and its interval stays below the floor.
- **Lines 36 and 41: one habit per model.** No model applies Definition 4.

  | model | habit | right at line 41's 85 states | right at line 36's 81 states |
  | --- | --- | --- | --- |
  | Mistral | always a new assumption | 81 | 0 |
  | 3B | reuses an assumption the state lists | 0 | 76 |
  | 7B | reuses an assumption the state lists; at line 36's states, guards another rule | 0 | 18 |
  | 14B | at line 41's states, reuses a background assumption that is not relative (74); mixed at line 36's | 7 | 25 |
  | 32B | reuses a background assumption that is not relative where line 41 introduces one, and introduces a new one where line 36 reuses | 13 | 0 |

  At each of line 36's states, the folded rule is a rule for the contrary of an
  assumption the run introduced; on 80 of the 81, the relative assumption is one the run
  introduced. Where the models miss these states, they introduce a new assumption (32B on
  all 81), guard another rule, or rename the contrary.
- **Line 8: dropping v2's clause helped, on the same 103 probes.** F1 rose from 0.321 to
  0.736 (14B), from 0.688 to 0.744 (32B) and from 0.260 to 0.542 (Mistral). Facts for
  contrary predicates fell from 195 to 83 (14B) and from 143 to 92 (32B). They did not
  vanish, because T itself contains those predicates. 3B answers NONE to every `role`
  probe; 7B answers NONE (43) or facts for background predicates (59).
- **Line 16:** 7B, 14B and 32B answer NO to almost every probe (0, 0 and 4 YES of 204).

**Smaller above larger** (the confound rule): 14B above 32B on `check`, 3B above the
larger models on `subsume`, and Mistral and 3B above the larger Qwen models on `introduce`.
In each case the larger models give a constant answer or follow a habit that is wrong on
both branches; no case is a smaller model computing the step. 7B above 14B on `fold` is
within the intervals.

## Caveats

1. **`role` and `fold` cannot discriminate on this benchmark**, as the floors show. A
   probe set that measures them needs problems whose RoLe answer is not the positive
   examples, and a fold probe that folding onto dom(X) does not pass trivially.
2. **The intervals treat problems as independent.** In this benchmark's legacy
   generator, the 20 `t5_twopath` problems are one structure in 20 surface forms (set 05,
   caveat 5), so the intervals are optimistic.
3. **4-bit for every model:** comparable within this set and with set 05, not with
   bf16 runs.
4. **Against set 05**, only `role` compares item for item. The other probes mix the
   change of prompt with the change of states.
5. **The `chance` field** in each `probe_summary.json` is 0.5 or 0.0, as in set 05. Read
   the floors above instead.
