"""Measured null floors for the step probes — no model, no GPU.

Runs answer policies that contain no reasoning whatsoever through the REAL
`score_probe`, so the floor each probe metric must be read against is measured
rather than assumed. The `chance` field the probe summaries emit
(`src/aba_probes.py`) is 0.5 for the binary kinds and 0.0 otherwise; both are
wrong, and these are the numbers that replace them.

Policies, per probe; the floor is the best of them. The first of each is the one
registered with probe prompts v3 (METHOD_HISTORY, Phase 10).
  role      : always NONE; one fact per positive example.
  fold      : copy the rule back unchanged; fold onto dom(X), which Definition 3
              puts in R for every constant.
  check     : YES iff the rendered state shows an "ASSUMPTIONS INTRODUCED SO FAR"
              section. One surface cue; the rules and the examples are never read.
  introduce : reuse the last assumption that section lists, else a new one. No
              rule body is read.
  subsume   : the check's cue; YES iff the state lists a learnt rule with no
              equality.

Measured on the 103-problem benchmark (seed 42, `--benchmark 20`, anonymised),
with probe prompts v3 and the reference after METHOD_HISTORY Phase 8:

    kind       policy                                   n  accuracy  score  balanced  fails
    role       always NONE                            103     0.000  0.000         -    103
    role       one fact per positive example          103     0.990  0.994         -      1
    fold       the rule copied back                   186     0.000  0.000         -    186
    fold       fold onto dom(X)                       186     1.000  1.000         -      0
    check      YES iff assumptions are listed         186     0.651  0.546     0.633    104
    introduce  reuse the last introduced, else new    166     0.855  0.855     0.855     24
    subsume    YES iff assumptions are listed         204     0.662  0.662     0.663     69
    subsume    YES iff a learnt rule has no equality  204     0.760  0.760     0.762     49

`role` and `fold` cannot discriminate on this set: RoLe's answer is the positive
examples on 102 of 103 problems, and dom(X) is a legal fold at every state, which
the probe accepts. `introduce` is balanced over line 36's two branches (81 reuse,
85 new), so always answering a new assumption gets 0.500; its policy gets 0.855
because every reuse state follows an assumption introduced for the same body.
Sets 04 and 05 were harvested from the earlier reference: their floors are in
their MANIFESTs.

With --set, each model's probe metrics in that set are printed beside these
floors, with 95% bootstrap intervals over problems, and the answers that explain
a check or role score.

Usage:
    python analysis/null_baselines.py [--benchmark 20] [--out null_baselines.json]
    python analysis/null_baselines.py --set experiments/06_probes_v3
"""
import argparse
import glob
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import build_dataset
from src.aba_probes import (BINARY_KINDS, KINDS, ProbeResult, aggregate_probes,
                            generate_probes, score_probe)

# The metric each probe is read by, as named in the probe summary.
METRIC = {"role": "score", "fold": "accuracy", "check": "balanced_accuracy",
          "introduce": "balanced_accuracy", "subsume": "balanced_accuracy"}

ASM_MARKER = "ASSUMPTIONS INTRODUCED SO FAR"


def cue_answer(probe, problem):
    """The whole policy: is there an assumption mentioned in the state?"""
    return "YES" if ASM_MARKER in probe.prompt else "NO"


def general_rule_answer(probe, problem):
    """YES iff the state already lists a learnt rule with no equality."""
    block = probe.prompt.rsplit("=== RULES LEARNT SO FAR ===", 1)[-1].split("\n\n")[0]
    return "YES" if any(":-" in r and "=" not in r for r in block.split("\n")) else "NO"


def positives_answer(probe, problem):
    """One fact per positive example."""
    return "\n".join(re.sub(r"\s+", "", e) + "." for e in problem.positive)


def dom_answer(probe, problem):
    """Fold onto dom(X), which holds for every constant (Definition 3)."""
    return probe.state.get("rule", "").split(":-")[0].strip() + " :- dom(X)."


def introduce_answer(probe, problem):
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


# Per probe, the policies tried; the floor is the best of them. The first is the
# one registered with probe prompts v3 (METHOD_HISTORY, Phase 10).
POLICIES = {
    "role":      {"always NONE": lambda p, pb: "NONE",
                  "one fact per positive example": positives_answer},
    "fold":      {"the rule copied back": lambda p, pb: p.state.get("rule", ""),
                  "fold onto dom(X)": dom_answer},
    "check":     {"YES iff assumptions are listed": cue_answer},
    "introduce": {"reuse the last introduced, else new": introduce_answer},
    "subsume":   {"YES iff assumptions are listed": cue_answer,
                  "YES iff a learnt rule has no equality": general_rule_answer},
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
    by_policy, ids = {}, set()
    for entry in ds:
        problem = entry.problem
        for probe in generate_probes(problem, max_per_kind=args.probes_per_kind,
                                     seed=args.seed):
            ids.add(probe.probe_id)
            for name, policy in POLICIES[probe.kind].items():
                text = policy(probe, problem)
                try:
                    correct, score, parsed = score_probe(probe, text, problem)
                except Exception as exc:                   # scoring must not stop the sweep
                    correct, score, parsed = False, 0.0, f"ERR {exc}"
                by_policy.setdefault((probe.kind, name), []).append(ProbeResult(
                    probe_id=probe.probe_id, problem_id=probe.problem_id,
                    kind=probe.kind, model_name="NULL", raw_output=text,
                    parsed=parsed, correct=correct, score=score,
                    oracle_bool=(probe.oracle if isinstance(probe.oracle, bool) else None)))

    print("\n=== NULL BASELINES (no model) ===")
    print(f"{'kind':<11}{'policy':<40}{'n':>5}{'accuracy':>10}{'score':>9}{'balanced':>10}{'fails':>7}")
    out = {}
    for (kind, name), rs in by_policy.items():
        acc = sum(r.correct for r in rs) / len(rs)
        sc = sum(r.score for r in rs) / len(rs)
        ba = aggregate_probes(rs)[kind].get("balanced_accuracy")
        fails = sum(r.score < 1.0 for r in rs)
        e = {"policy": name, "n": len(rs), "accuracy": round(acc, 3), "score": round(sc, 3),
             "balanced_accuracy": round(ba, 3) if ba is not None else None, "n_below_1": fails}
        if kind not in out or e[METRIC[kind]] > out[kind][METRIC[kind]]:
            out[kind] = e
        print(f"{kind:<11}{name:<40}{len(rs):>5}{acc:>10.3f}{sc:>9.3f}"
              f"{(f'{ba:.3f}' if ba is not None else '-'):>10}{fails:>7}")
    print("\nfloors: " + "; ".join(f"{k} {v[METRIC[k]]:.3f} ({v['policy']})" for k, v in out.items()))

    print("\n=== binary probe class balance ===")
    for kind in BINARY_KINDS:
        rs = next(v for (k, _), v in by_policy.items() if k == kind)
        y = sum(r.oracle_bool is True for r in rs)
        print(f"  {kind:<10} YES {y:>4} / NO {len(rs) - y:>4}  (n={len(rs)})")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"\nwrote {args.out}")
    if args.set:
        compare(args.set, out, ids, {e.problem.problem_id: e.problem for e in ds})


def metric(kind, rs):
    return aggregate_probes(rs)[kind].get(METRIC[kind]) if rs else None


_ATOM = re.compile(r"([a-z]\w*)\s*\(\s*([a-z]\w*)\s*\)")


def _atoms(xs):
    return {re.sub(r"\s+", "", x) for x in xs}


def _listed(r):
    """The examples a check answer lists after its verdict."""
    return {f"{a}({b})" for a, b in _ATOM.findall(r.raw_output.strip().partition("\n")[2])}


def _facts(r):
    return set(filter(None, r.parsed.split("; ")))


def _gold(r):
    return {f"{h}({k})" for h, k in re.findall(r"(\w+)\(X\) :- X = (\w+)\.", r.oracle_repr)}


def compare(set_dir, floors, ids, problems, n_boot=2000, seed=0):
    """Each model's metric per probe, its 95% bootstrap interval over problems,
    and whether the interval lies above the floor."""
    negatives = {k: _atoms(p.negative) for k, p in problems.items()}
    positives = {k: _atoms(p.positive) for k, p in problems.items()}
    contraries = {k: {c.split("(")[0] for c in p.background.contraries.values()}
                  for k, p in problems.items()}
    by_kind_rows = lambda by: [r for rs in by.values() for r in rs]
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
            # The answers that explain a check or role score.
            if kind == "check":
                no = [r for r in by_kind_rows(by) if re.match(r"\s*NO\b", r.raw_output, re.I)]
                neg = sum(_listed(r) == negatives[r.problem_id] for r in no)
                print(f"  {'':<11}NO on {len(no)}/{sum(map(len, by.values()))}; "
                      f"of these, the listed examples are exactly E- on {neg}")
            if kind == "role":
                wrong = [(r, a) for r in by_kind_rows(by) for a in _facts(r) - _gold(r)]
                contrary = sum(a.split("(")[0] in contraries[r.problem_id] for r, a in wrong)
                same = sum(_facts(r) == positives[r.problem_id] for r in by_kind_rows(by))
                print(f"  {'':<11}answers equal to E+: {same}; wrong facts {len(wrong)}, "
                      f"on contrary predicates {contrary}")


if __name__ == "__main__":
    main()
