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
  introduce       : reuse the last assumption that section lists, else a new
                    one. No rule body is read.
  role            : always NONE.
  fold            : copy the rule back unchanged.

Measured on the 103-problem benchmark (seed 42, `--benchmark 20`, anonymised),
with probe prompts v3 and the reference after METHOD_HISTORY Phase 8:

    kind          n   accuracy   score  balanced   fails
    role        103      0.000   0.000         -     103
    fold        186      0.000   0.000         -     186
    check       186      0.651   0.546     0.633     104
    introduce   166      0.855   0.855     0.855      24
    subsume     204      0.662   0.662     0.663      69

`introduce` is balanced over line 36's two branches (81 reuse, 85 new), so
always answering a new assumption gets 0.500; the policy above gets 0.855
because every reuse state follows an assumption introduced for the same body.
Sets 04 and 05 were harvested from the earlier reference: their floors are in
their MANIFESTs.

With --set, each model's probe metrics in that set are printed beside these
floors, with 95% bootstrap intervals over problems.

Usage:
    python analysis/null_baselines.py [--benchmark 20] [--out null_baselines.json]
    python analysis/null_baselines.py --set experiments/06_probes_v3
"""
import argparse
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import build_dataset
from src.aba_probes import (BINARY_KINDS, KINDS, ProbeResult, aggregate_probes,
                            generate_probes, score_probe)

# The metric each probe is read by, as named in the probe summary.
METRIC = {"role": "score", "fold": "accuracy", "check": "balanced_accuracy",
          "introduce": "balanced_accuracy", "subsume": "balanced_accuracy"}

ASM_MARKER = "ASSUMPTIONS INTRODUCED SO FAR"


def cue_answer(probe):
    """The whole policy: is there an assumption mentioned in the state?"""
    return "YES" if ASM_MARKER in probe.prompt else "NO"


def introduce_answer(probe):
    """Reuse the last assumption the state lists as introduced, else a new one."""
    folded = probe.state.get("folded", "")
    body = folded.rstrip().rstrip(".")
    var = "X"
    for tok in body.replace("(", " ").replace(")", " ").replace(",", " ").split():
        if tok[:1].isupper():
            var = tok
            break
    introduced = list(probe.state.get("new_asms", {}).items())
    asm, contrary = introduced[-1] if introduced else (f"zzznull({var})",
                                                       f"c_zzznull({var})")
    return f"RULE: {body}, {asm}.\nASSUMPTION: {asm} defeated_by {contrary}"


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
    ap.add_argument("--set", default=None,
                    help="a probe set (bench_*/probes.jsonl) to read against the floors")
    args = ap.parse_args()

    ds = build_dataset(benchmark_per_tier=args.benchmark, solve_symbolic=True,
                       anonymize=True, anonymize_scheme="letters")
    by_kind, ids = {}, set()
    for entry in ds:
        problem = entry.problem
        for probe in generate_probes(problem, max_per_kind=args.probes_per_kind,
                                     seed=args.seed):
            ids.add(probe.probe_id)
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
        ba = aggregate_probes(rs)[kind].get("balanced_accuracy")
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
    if args.set:
        compare(args.set, out, ids)


def metric(kind, rs):
    return aggregate_probes(rs)[kind].get(METRIC[kind]) if rs else None


def compare(set_dir, floors, ids, n_boot=2000, seed=0):
    """Each model's metric per probe, its 95% bootstrap interval over problems,
    and whether the interval lies above the floor."""
    rng = random.Random(seed)
    print(f"\n=== {set_dir}: metric [95% interval] against the floor ===")
    for d in sorted(glob.glob(os.path.join(set_dir, "bench_*"))):
        with open(os.path.join(d, "probes.jsonl"), encoding="utf-8") as f:
            rows = [ProbeResult(**json.loads(line)) for line in f if line.strip()]
        stray = sum(r.probe_id.rsplit("#", 1)[0] not in ids for r in rows)
        print(os.path.basename(d) + (f"  ({stray} rows not in this probe set)" if stray else ""))
        for kind in KINDS:
            by = {}
            for r in rows:
                if r.kind == kind:
                    by.setdefault(r.problem_id, []).append(r)
            if not by:
                continue
            pids = list(by)
            boots = sorted(m for m in (
                metric(kind, [r for p in rng.choices(pids, k=len(pids)) for r in by[p]])
                for _ in range(n_boot)) if m is not None)
            lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]
            m = metric(kind, [r for p in pids for r in by[p]])
            floor = floors[kind][METRIC[kind]]
            print(f"  {kind:<11}{m:>7.3f}  [{lo:.3f}, {hi:.3f}]  floor {floor:.3f}"
                  f"  {'above' if lo > floor else 'not above'}")


if __name__ == "__main__":
    main()
