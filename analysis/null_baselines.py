"""Measured null floors for the step probes — no model, no GPU.

Runs answer policies that contain no reasoning whatsoever through the REAL
`score_probe`, so the floor each probe metric must be read against is measured
rather than assumed. The `chance` field the probe summaries emit
(`src/aba_probes.py`) is 0.5 for the binary kinds and 0.0 otherwise; both are
wrong, and these are the numbers that replace them.

Policies
  check / subsume : answer YES iff the rendered state block shows an
                    "ASSUMPTIONS INTRODUCED SO FAR" section. One surface cue;
                    the rules and the examples are never read.
  introduce       : always guard the folded rule with a brand-new assumption
                    and a brand-new contrary. Never reuses, never inspects.
  role            : always NONE.
  fold            : copy the rule back unchanged.

Measured on the 103-problem benchmark (seed 42, `--benchmark 20`, anonymised):

    kind          n   accuracy   score  balanced   fails
    role        103      0.000   0.000         -     103
    fold        184      0.000   0.000         -     184
    check       186      0.688   0.551     0.681     109
    introduce   103      1.000   1.000         -       0
    subsume     204      0.686   0.686     0.687      64

Two consequences, both of which change how the probe table must be reported:

  * `introduce` is satisfied BY CONSTRUCTION — this is Proposition 2 (R3 + RoLe
    always recovers a solution), so the oracle cannot fail when the instruction
    is followed literally. Every model scores at or below the trivial baseline.
    Report it inverted, as an error count, not as an accuracy.
  * `check` and `subsume` have a ~0.68 surface-cue floor, not 0.50.

Usage:
    python analysis/null_baselines.py [--benchmark 20] [--out null_baselines.json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import build_dataset
from src.aba_probes import (BINARY_KINDS, ProbeResult, balanced_accuracy,
                            generate_probes, score_probe)

ASM_MARKER = "ASSUMPTIONS INTRODUCED SO FAR"


def cue_answer(probe):
    """The whole policy: is there an assumption mentioned in the state?"""
    return "YES" if ASM_MARKER in probe.prompt else "NO"


def introduce_answer(probe):
    folded = probe.state.get("folded", "")
    body = folded.rstrip().rstrip(".")
    var = "X"
    for tok in body.replace("(", " ").replace(")", " ").replace(",", " ").split():
        if tok[:1].isupper():
            var = tok
            break
    return (f"RULE: {body}, zzznull({var}).\n"
            f"ASSUMPTION: zzznull({var}) defeated_by c_zzznull({var})")


POLICIES = {
    "check":     cue_answer,
    "subsume":   cue_answer,
    "introduce": introduce_answer,
    "role":      lambda p: "NONE",
    "fold":      lambda p: p.state.get("rule", ""),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benchmark", type=int, default=20,
                    help="problems per tier, must match the run (default 20)")
    ap.add_argument("--probes-per-kind", type=int, default=2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None,
                    help="optional path to write the floors as JSON")
    args = ap.parse_args()

    ds = build_dataset(benchmark_per_tier=args.benchmark, solve_symbolic=True,
                       anonymize=True, anonymize_scheme="letters")
    by_kind = {}
    for entry in ds:
        problem = entry.problem
        for probe in generate_probes(problem, max_per_kind=args.probes_per_kind,
                                     seed=args.seed):
            text = POLICIES[probe.kind](probe)
            try:
                correct, score, parsed = score_probe(probe, text, problem)
            except Exception as exc:                       # scoring must not stop the sweep
                correct, score, parsed = False, 0.0, f"ERR {exc}"
            by_kind.setdefault(probe.kind, []).append(ProbeResult(
                probe_id=probe.probe_id, problem_id=probe.problem_id,
                kind=probe.kind, model_name="NULL", raw_output=text,
                parsed=parsed, correct=correct, score=score,
                oracle_bool=(probe.oracle if isinstance(probe.oracle, bool) else None)))

    print("\n=== NULL BASELINES (no model) ===")
    print(f"{'kind':<12}{'n':>5}{'accuracy':>10}{'score':>9}{'balanced':>10}{'fails':>7}")
    out = {}
    for kind, rs in by_kind.items():
        acc = sum(r.correct for r in rs) / len(rs)
        sc = sum(r.score for r in rs) / len(rs)
        ba = balanced_accuracy(rs) if kind in BINARY_KINDS else None
        fails = sum(r.score < 1.0 for r in rs)
        out[kind] = {"n": len(rs), "accuracy": round(acc, 3), "score": round(sc, 3),
                     "balanced_accuracy": round(ba, 3) if ba is not None else None,
                     "n_below_1": fails}
        print(f"{kind:<12}{len(rs):>5}{acc:>10.3f}{sc:>9.3f}"
              f"{(f'{ba:.3f}' if ba is not None else '-'):>10}{fails:>7}")

    print("\n=== binary probe class balance ===")
    for kind in BINARY_KINDS:
        rs = by_kind.get(kind, [])
        y = sum(r.oracle_bool is True for r in rs)
        print(f"  {kind:<10} YES {y:>4} / NO {len(rs) - y:>4}  (n={len(rs)})")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
