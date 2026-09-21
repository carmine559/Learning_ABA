"""How much of a run's gen@k is a conformant ASP-ABAlearnB output?

`gen_valid` is Definition 1 of De Angelis et al. on the full problem
(`src/aba_generalization.py`) — a faithful solution criterion, but the set of
Definition-1 solutions STRICTLY CONTAINS the set of ASP-ABAlearnB outputs:
Theorem 3 runs one way only (algorithm success => intensional solution), and the
algorithm is incomplete besides. So gen@k scores membership in the outer set.

This script adds the output-level properties the paper states about the
algorithm's own answer, which a Definition-1 solution need not have:

  G1  intensional     Theorem 3: the algorithm's output is always intensional,
                      so a non-intensional solution is a certified divergence
  G2  not degenerate  a framework that entails everything is not learning
  G3  semantic match  entailment-equivalent to the symbolic reference

These are all properties of the OUTPUT. They say nothing about whether the
algorithm was followed to get there — for that, use `step_fidelity.py`, which
scores each transformation against the algorithm's trace. A run can pass every
gate here and still reach the answer by a procedure the algorithm never takes.

NOT A GATE — `n_new_assumptions` vs the algorithm's R3 count was tried and is
wrong; it counts only freshly minted assumptions and so scores the REUSE FIRST
branch (line 36 / Definition 4) as a divergence. See `step_fidelity.py`.

Reads stored rows only — no model, no GPU.

Usage:
    python analysis/conformance.py [--set experiments/05_scale_4bit_probes_v2]
"""
import argparse
import collections
import json
import os

MODES = ["direct", "cot", "guided", "algorithm"]
GATES = ["G1_intensional", "G2_not_degenerate", "G3_semantic_match"]


def gates_for(row):
    return {
        "G1_intensional":    bool(row.get("intensional")),
        "G2_not_degenerate": not bool(row.get("is_degenerate")),
        "G3_semantic_match": bool(row.get("semantic_match")),
    }


def discover_models(set_dir):
    return sorted(d[len("bench_"):] for d in os.listdir(set_dir)
                  if d.startswith("bench_") and os.path.isdir(os.path.join(set_dir, d)))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="experiments/05_scale_4bit_probes_v2")
    args = ap.parse_args()

    models = discover_models(args.set)

    print("\nHow much of gen@k survives the output-level conformance gates")
    print("(@k = the problem passes on ANY of its samples)\n")
    hdr = (f"{'model':<13}{'mode':<11}{'gen@k':>7}{'conf@k':>8}"
           f"{'survives':>10}{'rate gen':>10}{'rate conf':>11}")
    print(hdr)
    print("-" * len(hdr))

    gate_loss = collections.Counter()
    n_samples = 0

    for model in models:
        for mode in MODES:
            path = os.path.join(args.set, f"bench_{model}", f"results_{mode}.jsonl")
            if not os.path.exists(path):
                continue
            by_problem = collections.defaultdict(list)
            for line in open(path, encoding="utf-8"):
                r = json.loads(line)
                by_problem[r["problem_id"]].append(r)

            gen_k = conf_k = 0
            for samples in by_problem.values():
                gv = [s for s in samples if s.get("gen_valid")]
                if not gv:
                    continue
                gen_k += 1
                passed = False
                for s in gv:
                    n_samples += 1
                    gd = gates_for(s)
                    for g in GATES:
                        if not gd[g]:
                            gate_loss[g] += 1
                    passed = passed or all(gd.values())
                conf_k += passed

            n = len(by_problem) or 1
            surv = f"{100*conf_k/gen_k:.0f}%" if gen_k else "-"
            print(f"{model:<13}{mode:<11}{gen_k:>7}{conf_k:>8}{surv:>10}"
                  f"{gen_k/n:>10.3f}{conf_k/n:>11.3f}")

    print(f"\n=== which gate does the filtering (per gen_valid sample) ===")
    print(f"  gen_valid samples examined: {n_samples}")
    for g in GATES:
        print(f"  {g:<20} failed by {gate_loss[g]:>5}  "
              f"({100*gate_loss[g]/max(n_samples,1):.1f}%)")
    print("\n  These gates inspect the ENDPOINT only. For whether the algorithm "
          "was followed,\n  see analysis/step_fidelity.py.")


if __name__ == "__main__":
    main()
