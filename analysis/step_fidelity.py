"""End-to-end fidelity to ASP-ABAlearnB, one transformation rule at a time.

Scores a run's FINAL answers against the algorithm's own `symbolic_traces.jsonl`,
split by the transformation each property belongs to, so "does the LLM replicate
the algorithm" becomes four separate answers instead of one aggregate that hides
the difference between them.

  R1  Rote Learning (lines 9-11, 23-25) — ground facts surviving in the answer.
      The algorithm's output is always intensional (Theorem 3), so any ground
      fact left behind is RoLe residue that Gen never cleared.

  R2  Folding (line 17). Isolated from R3 by comparing, for the SAME head
      predicate, the NON-assumption body atoms only: folding fixes those, R3
      appends the assumption afterwards. Relation of model body to algorithm's:
        exact      same folded body
        over-spec  model is a superset: extra conditions, a narrower rule
        over-gen   model is a subset: missing conditions, a broader rule
        other      neither contains the other

  R3  Assumption Introduction (line 19, 34-46). Balanced across the two classes
      (see NULL FLOOR below), plus which branch of `applyAsmIntro` was taken —
      reuse (lines 36-38) vs mint fresh (lines 41-44) — and whether the contrary
      rule that the fresh branch obliges was actually learnt.

  R4  Fact Subsumption (line 16). See the caveat below: NOT separable from R1.

  The line-18 solution check is an INTERNAL decision that leaves no trace in a
  final answer. It is measurable only by the `check` step probe, not here.

NULL FLOOR. On the standard 103-problem benchmark the algorithm's answer is
defeasible on 81 and monotonic on 22, so a policy that guards every rule without
reasoning scores 0.786 raw agreement on R3. Raw agreement is therefore reported
only beside the balanced score, which puts any constant responder at 0.500.
Read the balanced column.

CAVEAT — R4 IS NOT SEPARABLE END-TO-END. The algorithm leaves zero ground facts
on every problem in this benchmark, so "R1 residue not folded away" and "R4 not
applied" are the same observable in a final answer; the R4 column is reported
but is structurally identical to R1. Separating them needs either a redesigned
`subsume` probe or problems whose algorithm answer retains ground facts.

RETRACTED — DO NOT REINTRODUCE. An earlier version of this script gated R3 on
`n_new_assumptions <= the algorithm's R3 count`. That is wrong:
`n_new_assumptions` counts only FRESHLY MINTED assumptions, so it scores a model
that applied R3 by reusing a background assumption as a divergence — which is
precisely what line 36 / Definition 4 REUSE FIRST asks for. It produced a
confident false result ("the model solves defeasible problems monotonically")
that had to be withdrawn. R3 application is detected here by whether a learnt
rule body carries an assumption atom AT ALL, background or fresh.

Reads stored rows only — no model, no GPU.

Usage:
    python analysis/step_fidelity.py [--set experiments/05_scale_4bit_probes_v2]
"""
import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import build_dataset
from src.aba_prompts import parse_llm_output

MODES = ["direct", "cot", "guided", "algorithm"]


def pred_of(atom):
    return str(atom).strip().split("(")[0].strip()


def split_body(body):
    """Split a rule body on top-level commas, keeping p(X,Y) intact."""
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return [p for p in parts if p.strip()]


def has_constant_text(rule_text):
    """A normalised ground fact is `p(X) :- X = t.`; a bare `p(a).` counts too."""
    t = rule_text.strip().rstrip(".")
    if ":-" in t:
        _, body = t.split(":-", 1)
        if "=" in body:
            return True
        args = body
    else:
        args = t
    for seg in args.split("("):
        if ")" not in seg:
            continue
        for a in seg.split(")")[0].split(","):
            a = a.strip()
            if a and a[0].islower():
                return True
    return False


def discover_models(set_dir):
    return sorted(d[len("bench_"):] for d in os.listdir(set_dir)
                  if d.startswith("bench_") and os.path.isdir(os.path.join(set_dir, d)))


def load_traces(set_dir, models):
    """Traces are model-independent; any bench_* copy will do."""
    for m in models:
        path = os.path.join(set_dir, f"bench_{m}", "symbolic_traces.jsonl")
        if os.path.exists(path):
            out = {}
            for line in open(path, encoding="utf-8"):
                t = json.loads(line)
                out[t["problem_id"]] = t
            return out
    raise SystemExit("no symbolic_traces.jsonl found in the set")


def build_reference(problems, traces):
    """Everything the algorithm's own answer says about one problem."""
    ref = {}
    for pid, p in problems.items():
        t = traces.get(pid)
        if t is None or not t.get("success"):
            continue
        bg_asm = {pred_of(a) for a in p.background.assumptions}
        all_asm = bg_asm | {pred_of(a) for a in t.get("final_assumptions", [])}
        contraries = ({pred_of(c) for c in p.background.contraries.values()}
                      | {pred_of(c) for c in t.get("final_contraries", {}).values()})
        known = set()
        for r in p.background.rules:
            known.add(pred_of(r.head))
            known.update(pred_of(b) for b in r.body)
        # Learnable targets are NOT in the background but are not invented
        # either; without them every head collapses to the <new> placeholder.
        known |= bg_asm | contraries
        known |= {pred_of(x) for x in (getattr(p, "learnable", []) or [])}

        def nrm(head, bodies, _all_asm=all_asm, _known=known):
            """head :- sorted(body). Assumption atoms fold to <asm> so that
            reusing `u(X)` and minting `alpha_0(X)` compare equal — the question
            is whether the RULE is the algorithm's, not which assumption it used."""
            def m(x):
                q = pred_of(x)
                if q in _all_asm:
                    return "<asm>"
                return q if q in _known else "<new>"
            return f"{m(head)} :- {','.join(sorted(m(b) for b in bodies))}"

        bodies = {}
        rules = set()
        n_ground = 0
        defeasible = False
        learnt_contrary = False
        for rule in t["final_new_rules"]:
            if has_constant_text(rule):
                n_ground += 1
            head, body = ((rule.split(":-", 1) + [""])[:2] if ":-" in rule
                          else (rule, ""))
            head = head.rstrip(".")
            atoms = split_body(body)
            if any(pred_of(a) in all_asm for a in atoms):
                defeasible = True
            if pred_of(head) in contraries:
                learnt_contrary = True
            bodies[pred_of(head)] = {pred_of(a) for a in atoms
                                     if pred_of(a) not in all_asm and "=" not in a}
            rules.add(nrm(head, atoms))
        ref[pid] = dict(bg_asm=bg_asm, all_asm=all_asm, contraries=contraries,
                        bodies=bodies, rules=rules, nrm=nrm, n_ground=n_ground,
                        defeasible=defeasible, learnt_contrary=learnt_contrary)
    return ref


def score_file(path, problems, ref):
    """One model-mode file -> every per-transformation counter."""
    acc = collections.Counter()
    cmp_n = collections.Counter()
    D = [0, 0]
    M = [0, 0]
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        pid = r["problem_id"]
        p, R = problems.get(pid), ref.get(pid)
        if p is None or R is None or not r.get("parse_success"):
            continue
        cand = parse_llm_output(r["raw_output"], p.background)
        if cand is None:
            continue
        acc["n"] += 1
        new_rules = list(cand.new_rules)

        # ---- R1: ground facts surviving in the answer ----
        gf = [x for x in new_rules if x.contains_constant()]
        acc["ground"] += bool(gf)
        # ---- R4: identical to R1 while the algorithm leaves none (see caveat)
        if gf and R["n_ground"] == 0:
            acc["redundant"] += 1

        # ---- R3 ----
        fresh_preds = {pred_of(x) for x in cand.new_assumptions}
        asms = R["all_asm"] | fresh_preds
        used_bg = any(pred_of(b) in R["bg_asm"] for x in new_rules for b in x.body)
        used_fr = any(pred_of(b) in fresh_preds for x in new_rules for b in x.body)
        mdef = used_bg or used_fr
        if R["defeasible"]:
            D[1] += 1
            D[0] += mdef
        else:
            M[1] += 1
            M[0] += (not mdef)
        acc["raw_agree"] += (mdef == R["defeasible"])
        acc["reuse"] += used_bg
        acc["fresh"] += used_fr
        if R["learnt_contrary"]:
            acc["con_tot"] += 1
            acc["con_hit"] += any(pred_of(x.head) in R["contraries"]
                                  for x in new_rules)

        # ---- R2: non-assumption body, per head, where the model gave one rule
        for head_pred, algo_body in R["bodies"].items():
            mine = [x for x in new_rules if pred_of(x.head) == head_pred]
            if len(mine) != 1:
                continue
            mb = {pred_of(b) for b in mine[0].body if pred_of(b) not in asms}
            cmp_n["n"] += 1
            if mb == algo_body:
                cmp_n["exact"] += 1
            elif mb > algo_body:
                cmp_n["over"] += 1
            elif mb < algo_body:
                cmp_n["under"] += 1
            else:
                cmp_n["other"] += 1

        # ---- whole rule set, modulo naming ----
        got = {R["nrm"](x.head, x.body) for x in new_rules}
        acc["rules_eq"] += (got == R["rules"])
    return acc, cmp_n, D, M


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="experiments/05_scale_4bit_probes_v2",
                    help="experiment set directory containing bench_<model>/")
    ap.add_argument("--benchmark", type=int, default=20,
                    help="problems per tier, must match the run (default 20)")
    ap.add_argument("--min-samples", type=int, default=20,
                    help="skip a model-mode cell with fewer parsed samples")
    args = ap.parse_args()

    models = discover_models(args.set)
    traces = load_traces(args.set, models)

    ds = build_dataset(benchmark_per_tier=args.benchmark, solve_symbolic=False,
                       anonymize=True, anonymize_scheme="letters")
    problems = {e.problem.problem_id: e.problem for e in ds}
    ref = build_reference(problems, traces)

    nD = sum(v["defeasible"] for v in ref.values())
    n_ground = sum(v["n_ground"] > 0 for v in ref.values())
    print(f"\nReference: {len(ref)} problems solved by the algorithm; "
          f"defeasible on {nD}, monotonic on {len(ref) - nD}.")
    print(f"Algorithm leaves ground facts on {n_ground}/{len(ref)} "
          f"(Theorem 3: expected 0).")
    if len(ref):
        print(f"R3 null floor: 'always guard' = {nD}/{len(ref)} = "
              f"{nD/len(ref):.3f} raw; any constant policy = 0.500 balanced.\n")

    print("=" * 100)
    print("R1 ROTE LEARNING  |  R2 FOLDING (non-assumption body vs algorithm)      "
          "| R4*  | whole")
    print("=" * 100)
    hdr = (f"{'model':<13}{'mode':<11}{'n':>5}{'ground':>8} | "
           f"{'cmp':>5}{'exact':>8}{'ovspec':>8}{'ovgen':>7}{'other':>7} | "
           f"{'redund':>6} | {'rules=':>6}")
    print(hdr)
    print("-" * len(hdr))

    r3rows = []
    for model in models:
        for mode in MODES:
            path = os.path.join(args.set, f"bench_{model}", f"results_{mode}.jsonl")
            if not os.path.exists(path):
                continue
            acc, cmp_n, D, M = score_file(path, problems, ref)
            n = acc["n"]
            if n < args.min_samples:
                continue
            c = cmp_n["n"] or 1
            print(f"{model:<13}{mode:<11}{n:>5}{100*acc['ground']/n:>7.0f}% | "
                  f"{cmp_n['n']:>5}{100*cmp_n['exact']/c:>7.0f}%"
                  f"{100*cmp_n['over']/c:>7.0f}%{100*cmp_n['under']/c:>6.0f}%"
                  f"{100*cmp_n['other']/c:>6.0f}% | "
                  f"{100*acc['redundant']/n:>5.0f}% | {100*acc['rules_eq']/n:>5.0f}%")
            aD = D[0] / D[1] if D[1] else 0.0
            aM = M[0] / M[1] if M[1] else 0.0
            r3rows.append((model, mode, n, aD, aM, (aD + aM) / 2,
                           acc["raw_agree"] / n, acc["reuse"] / n, acc["fresh"] / n,
                           acc["con_hit"] / acc["con_tot"] if acc["con_tot"] else None))

    print("\n  * R4 is structurally identical to R1 on this benchmark — see the "
          "caveat in the module docstring.")
    print("  cmp = comparisons made; R2 only scores a head the model gave exactly "
          "one rule for,\n        so a low cmp means that row rests on a small "
          "self-selected subset.")

    print("\n" + "=" * 100)
    print("R3 ASSUMPTION INTRODUCTION — balanced agreement, and which branch of "
          "applyAsmIntro")
    print("=" * 100)
    hdr = (f"{'model':<13}{'mode':<11}{'n':>5}{'agr_D':>8}{'agr_M':>8}"
           f"{'BALANCED':>10}{'raw':>7}{'reuse':>8}{'fresh':>7}{'contrary':>10}")
    print(hdr)
    print("-" * len(hdr))
    for (model, mode, n, aD, aM, bal, raw, ru, fr, co) in r3rows:
        cs = f"{100*co:.0f}%" if co is not None else "-"
        print(f"{model:<13}{mode:<11}{n:>5}{aD:>8.3f}{aM:>8.3f}{bal:>10.3f}"
              f"{raw:>7.3f}{100*ru:>7.0f}%{100*fr:>6.0f}%{cs:>10}")
    print("\n  agr_D = credit for being defeasible where the algorithm is")
    print("  agr_M = credit for being monotonic where the algorithm is")
    print("  BALANCED = (agr_D + agr_M)/2. Read this one, not raw.")
    print("  contrary = learnt a rule headed by a contrary, where the algorithm did")


if __name__ == "__main__":
    main()
