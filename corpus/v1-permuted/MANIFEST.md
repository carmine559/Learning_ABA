# Corpus v1-permuted

- code rev: `f9dd08d-dirty`; clingo 5.8.0; python 3.12.3
- prompt: v4-sft; splits: test, heldout
- source: `corpus/v1` (corpus v1, code rev `502b725`); `problems.jsonl` a50b82612cf8b38a252a45fb491a70a41fcec951685a07dab86b601362f119e8; `eval.jsonl` d8c1df85b631d0f6809583f3ded8936730783e81652dd82b032d0e041032ce25
- seed: random.Random(f'corpus-v1-permuted:{problem_id}'); a copy of the problem's predicate symbols (collect_symbols order) is shuffled until no symbol maps to itself

## Gates

- [x] every permutation is a derangement and a bijection
- [x] check_example passes on every problem
- [x] held-out expected answer is the reference's
- [x] prompts differ from the source prompts on every row
- [x] no signature changes

## Counts

| tier | split/class | n |
|---|---|---|
| t1_base | test/defeasible | 20 |
| t1_base | test/monotonic | 20 |
| t2_noise | test/defeasible | 20 |
| t2_noise | test/monotonic | 20 |
| t3_domain | test/defeasible | 20 |
| t3_domain | test/monotonic | 20 |
| t4_nested | test/defeasible | 20 |
| t4_nested | test/monotonic | 20 |
| t5_twopath | test/defeasible | 20 |
| t5_twopath | test/monotonic | 20 |
| t8_decoy | heldout/decoy_first | 25 |
| t8_decoy | heldout/key_first | 25 |
| t9_reuse | heldout/reuse_fails | 25 |
| t9_reuse | heldout/reuse_ok | 25 |

## Gold vs the source gold renamed (reported, not gated)

Equal: endpoint 300/300, trace 300/300, both 300/300.

## Notes

- The source's test and held-out problems, each re-posed with its predicate symbols renamed by a derangement of themselves; Table 1 is not included. Never trained on: there are no sft_*.jsonl.
- Constants, and the order of rules, assumptions, contraries, examples, learnable predicates and domain, are the source's; dom is never renamed. The inverse permutation gives the source problem back (asserted).
- problem_id, tier, split and class are the source's: each row pairs with the source eval row of the same id.
- The gold is the reference's run on the permuted problem. gold_equal_renamed counts the golds equal to the source gold with its predicates renamed (alpha_k / c_alpha_k are minted by the algorithm and keep their names); a problem absent from gold_differences is equal on both targets.
- permutation maps the source's predicate names to this problem's; name_map is the source name_map composed with it.
- Held-out meta.answers are the source's, renamed; expected, forbidden and half are unchanged.
- TOKENS.json (python train_sft.py --audit --corpus <this corpus>) has no arm matching and inherits the source's max_new_tokens, so both sets are generated under one budget.

## Files (sha256)

- `problems.jsonl` 886a211ff3c43577c41d0c76df5d27485001fbdc6692b0475bec16f5e5fccb29
- `eval.jsonl` ab362692f4ce7f7734fc881f9635b59fea207e3ff1cffeec80ac2a01294ca594
