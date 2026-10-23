"""Arm S2 (step-wise SFT) against the registered arms, and the D5 verdict.

    python sft/compare_step.py          # -> results/sft-step/COMPARISON_STEP.md and .json
    python sft/compare_step.py --s2 s2_s1     # a replicate -> results/sft-step/s2_s1/

D5, on v1 test (200 problems):
  (a) chained first-check balanced accuracy >= 0.80: each problem's first line-18 test on
      the model's own run; a run that stops before it is a miss;
  (b) R3 balanced accuracy >= 0.80: the answer has an assumption iff the reference's does;
      a run without an answer is a miss;
  (c) exact > 89/200 (sft_trace's) with exact McNemar p < 0.05 against sft_trace.
Supported if (a), (b) and (c) hold; refuted if (a) <= 0.60; intermediate otherwise; read
only on complete test scores. Expected even if supported: t9 reuse_ok near 0 (its deciding
line-38 answer, yes, never occurs in training) and Table 1 low.
Confounds: 4.5x the trace arm's tokens read, 0.62x its target tokens; no definitions block
or step history; witness targets at lines 16/18; extra line-18 rows.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from sft.compare_sft import (CORPORA, MARGIN, _f, _p, _read, _sets, _sha, arm_report,
                             invariance, mcnemar, prop, table1_support)
from sft.eval_stepwise import _balanced
from src.aba_score import load_eval

ARMS = ("base", "sft_endpoint", "sft_trace")
REGISTERED = {"v1": Path("sft"), "permuted": Path("sft-permuted")}
S2 = {"chained": ("sft-step/{}/chained", "v1"), "gold": ("sft-step/{}/gold", "v1"),
      "permuted": ("sft-step-permuted/{}", "permuted")}    # {}: the run, s2 (seed 0) or s2_s1 ...
TRACE_EXACT = 89                    # sft_trace's exact on v1 test
SUPPORT, REFUTE, ALPHA = 0.80, 0.60, 0.05
GROUPS = ("split:test", "split:heldout", "tier:t9_reuse", "split:table1")   # step tables


def _checked(d: Path, corpus: Path) -> Optional[Dict]:
    """d's EVAL_MANIFEST.json; scores made on another build of the corpus are refused."""
    m = d / "EVAL_MANIFEST.json"
    if not m.exists():
        return None
    made = json.loads(m.read_text(encoding="utf-8"))
    stale = [f for f, h in made["sha256"].items() if _sha(corpus / f) != h]
    if stale:
        raise SystemExit(f"{d} was generated on another {stale} of {corpus}")
    return made


def load(results: Path, run: str = "s2") -> Tuple[Dict, Dict]:
    """(corpus -> registered arm -> problem_id -> score row, S2 output name -> its files)."""
    reg = {}
    for corpus, sub in REGISTERED.items():
        for arm in ARMS:
            rows = _read(results / sub / arm / "scores.jsonl")
            if rows:
                _checked(results / sub / arm, CORPORA[corpus])
                reg.setdefault(corpus, {})[arm] = {r["problem_id"]: r for r in rows}
    s2, made = {}, {}
    for name, (sub, corpus) in S2.items():
        d = results / sub.format(run)
        m = _checked(d, CORPORA[corpus])
        if m is not None:
            made[name] = json.dumps([m["adapter_sha256"], m["prompt_version"], m["decoding"]])
        s2[name] = {f: _read(d / f) for f in ("scores.jsonl", "run_scores.jsonl",
                                                "call_scores.jsonl", "generations.jsonl")}
        s2[name]["summary"] = (json.loads((d / "step_summary.json").read_text(encoding="utf-8"))
                               if (d / "step_summary.json").exists() else None)
    if len(set(made.values())) > 1:
        raise SystemExit(f"the S2 outputs are not of one adapter and decoding: {made}")
    return reg, s2


# ─────────────────────────────────────────────────────────────────────────────
# D5
# ─────────────────────────────────────────────────────────────────────────────

def first_pairs(runs: List[Dict]) -> List[Tuple[bool, Optional[bool]]]:
    """(truth, said) of each run's first line-18 test; not reached: a miss against the
    reference's first verdict."""
    return [(r["first_check"]["truth"], r["first_check"]["said"]) if r["first_check"]
            else (r["gold_first_check"], None)
            for r in runs if r["first_check"] or r["gold_first_check"] is not None]


def r3_pairs(scores: List[Dict]) -> List[Tuple[bool, Optional[bool]]]:
    """(the reference's answer has an assumption, the model's has); no answer: a miss."""
    return [(bool(r["ref_defeasible"]), r["defeasible"]) for r in scores]


def d5(s2: Dict, trace: Dict[str, Dict], test: List[str]) -> Dict:
    scores = {r["problem_id"]: r for r in s2["chained"]["scores.jsonl"]}
    runs = {r["problem_id"]: r for r in s2["chained"]["run_scores.jsonl"]}
    gap = sum(p not in scores or p not in runs for p in test)
    if gap or any(p not in trace for p in test):
        return {"verdict": "pending", "why": f"{gap} of the {len(test)} S2 test runs not scored"
                if gap else "sft_trace's test scores missing"}
    k_trace = sum(bool(trace[p]["exact"]) for p in test)
    if k_trace != TRACE_EXACT:
        raise SystemExit(f"sft_trace's exact on test is {k_trace}; D5 registered {TRACE_EXACT}")
    a = _balanced(first_pairs([runs[p] for p in test]))
    b = _balanced(r3_pairs([scores[p] for p in test]))
    k = sum(bool(scores[p]["exact"]) for p in test)
    m = mcnemar([(bool(scores[p]["exact"]), bool(trace[p]["exact"])) for p in test])
    holds = {"a": a is not None and a >= SUPPORT, "b": b is not None and b >= SUPPORT,
             "c": k > k_trace and m["p_exact"] < ALPHA}
    verdict = ("undefined: one class of truth" if a is None else "refuted" if a <= REFUTE
               else "supported" if all(holds.values()) else "intermediate")
    return {"verdict": verdict, "a_first_check_balanced": a, "b_r3_balanced": b,
            "c_exact": {"s2": k, "sft_trace": k_trace, "n": len(test), "mcnemar": m},
            "holds": holds}


# ─────────────────────────────────────────────────────────────────────────────
# Reported beside D5
# ─────────────────────────────────────────────────────────────────────────────

def _acc(pairs) -> Optional[Dict]:
    return prop([t == s for t, s in pairs]) if pairs else None


def reference_first(corpus: Path) -> Dict[str, Optional[bool]]:
    """Each problem's first line-18 verdict on the reference's run (its stored record)."""
    return {r["problem_id"]: next((c["sat"] for e in r["events"] for c in e["candidates"]
                                   if c["sat"] is not None), None)
            for n in ("traces.jsonl", "table1_traces.jsonl") for r in _read(corpus / n)}


def trace_first_pairs(scores: List[Dict], ref: Dict[str, Optional[bool]]):
    """The trace arm's first line-18 test on its own path (audit log); none written: a miss."""
    out = []
    for r in scores:
        c = next((e for e in (r["audit"] or {}).get("log", []) if e[1] == "check"), None)
        if c is not None and c[3] is not None:
            out.append((c[3], c[4] if isinstance(c[4], bool) else None))
        elif ref.get(r["problem_id"]) is not None:
            out.append((ref[r["problem_id"]], None))
    return out


def first_checks(reg: Dict, s2: Dict) -> Dict:
    """Per set: S2 chained and at the reference's state (gold), the position baseline, and
    sft_trace on its own path; and how often chained and gold agree at the same state."""
    out = collections.defaultdict(dict)
    ref = reference_first(CORPORA["v1"])
    for name, rs in _sets(list(reg.get("v1", {}).get("sft_trace", {}).values())).items():
        p = trace_first_pairs(rs, ref)
        out[name]["sft_trace"] = {"balanced": _balanced(p), "accuracy": _acc(p)}
    for name, rs in _sets(s2["chained"]["run_scores.jsonl"]).items():
        p = first_pairs(rs)
        out[name]["s2 chained"] = {"balanced": _balanced(p), "accuracy": _acc(p),
                                   "reached": sum(bool(r["first_check"]) for r in rs),
                                   "at_reference_state": sum(bool(r["first_check"] and
                                                                  r["first_check"]["on_path"])
                                                             for r in rs), "n": len(rs)}
    gold = [r for r in s2["gold"]["call_scores.jsonl"] if r["cell"] == "first_check"]
    for name, rs in _sets(gold).items():
        p = [(r["truth"], r["said"]) for r in rs]
        out[name]["s2 gold"] = {"balanced": _balanced(p), "accuracy": _acc(p)}
        b = [(r["truth"], r["baseline"]) for r in rs]
        out[name]["position baseline"] = {"balanced": _balanced(b), "accuracy": _acc(b)}
    at = {r["problem_id"]: r["said"] for r in s2["chained"]["call_scores.jsonl"]
          if r.get("first") and r["on_path"]}
    same = [at[r["problem_id"]] == r["said"] for r in gold if r["problem_id"] in at]
    return {"sets": dict(out), "chained_equals_gold_at_same_state": prop(same) if same else None}


def step_tables(s2: Dict) -> Dict:
    """Per kind and decision cell: gold (at the reference's states), chained (own run)."""
    g, c = s2["gold"]["summary"], s2["chained"]["summary"]
    tables = {"gold": g or {}, "chained": (c or {}).get("calls", {})}
    return {proto: {k: t[k] for k in GROUPS if k in t} for proto, t in tables.items() if t}


def stops(runs: List[Dict]) -> Dict:
    return {name: {"n": len(rs), "stopped": prop([r["error"] is not None for r in rs]),
                   "codes": dict(collections.Counter(r["error"] for r in rs if r["error"]))}
            for name, rs in _sets(runs).items()}


def exact_by_set(reg: Dict, s2: Dict) -> Dict:
    out = {}
    for corpus, name in (("v1", "chained"), ("permuted", "permuted")):
        arms = {a: list(rows.values()) for a, rows in reg.get(corpus, {}).items()}
        if s2[name]["scores.jsonl"]:
            arms["s2"] = s2[name]["scores.jsonl"]
        sets = {a: _sets(rs) for a, rs in arms.items()}
        strict = _sets(s2[name]["run_scores.jsonl"])
        for set_name in sorted({n for x in sets.values() for n in x}):
            row = {a: prop([bool(r["exact"]) for r in x[set_name]]) if set_name in x else None
                   for a, x in sets.items()}
            if set_name in strict:
                row["s2 strict"] = prop([bool(r["strict_exact"]) for r in strict[set_name]])
            out[f"{corpus} {set_name}"] = row
    return out


def contrasts(reg: Dict, s2: Dict) -> Dict:
    out = {}
    for corpus, name in (("v1", "chained"), ("permuted", "permuted")):
        mine = {r["problem_id"]: r for r in s2[name]["scores.jsonl"]}
        for arm in ("sft_trace", "sft_endpoint"):
            other = reg.get(corpus, {}).get(arm)
            if not mine or not other:
                continue
            for set_name, rs in _sets(list(mine.values())).items():
                pairs = [(bool(r["exact"]), bool(other[r["problem_id"]]["exact"]))
                         for r in rs if r["problem_id"] in other]
                out[f"{corpus} {set_name}: s2 vs {arm}"] = mcnemar(pairs)
    return out


def names(reg: Dict, s2: Dict) -> Dict:
    """Name invariance, S2 and (for reference) the registered arms, as compare_sft reads it."""
    split = collections.defaultdict(set)
    for row, _, _ in load_eval(CORPORA["permuted"]):
        split[row["split"]].add(row["problem_id"])
    expected = {"test": split["test"], "heldout": split["heldout"],
                "all": split["test"] | split["heldout"]}
    arms = {"s2": ({r["problem_id"]: r for r in s2["chained"]["scores.jsonl"]},
                   {r["problem_id"]: r for r in s2["permuted"]["scores.jsonl"]})}
    for arm in ("sft_trace", "sft_endpoint"):
        if arm in reg.get("v1", {}) and arm in reg.get("permuted", {}):
            arms[arm] = (reg["v1"][arm], reg["permuted"][arm])
    return {arm: invariance(v1, perm, expected) for arm, (v1, perm) in arms.items()}


def report(results: Path, run: str = "s2") -> Dict:
    reg, s2 = load(results, run)
    test = sorted(row["problem_id"] for row, _, _ in load_eval(CORPORA["v1"])
                  if row["split"] == "test")
    out = {"d5": d5(s2, reg.get("v1", {}).get("sft_trace", {}), test),
           "first_check": first_checks(reg, s2), "exact": exact_by_set(reg, s2),
           "steps": step_tables(s2), "contrasts": contrasts(reg, s2), "invariance": names(reg, s2),
           "stops": {c: stops(s2[n]["run_scores.jsonl"]) for c, n in (("v1", "chained"),
                                                                      ("permuted", "permuted"))},
           "s2": {}}
    train = {r["target"] for r in _read(CORPORA["v1"] / "sft_endpoint.jsonl") if r["split"] == "train"}
    support = table1_support(CORPORA["v1"])
    for corpus, name in (("v1", "chained"), ("permuted", "permuted")):
        if s2[name]["scores.jsonl"]:
            items = {row["problem_id"]: (row, p, meta) for row, p, meta in load_eval(CORPORA[corpus])}
            gens = {g["problem_id"]: g for g in s2[name]["generations.jsonl"]}
            out["s2"][corpus] = arm_report(s2[name]["scores.jsonl"], gens, items, train, support)
            out["s2"][corpus + " r3_with_misses"] = {
                n: _balanced(r3_pairs(rs)) for n, rs in _sets(s2[name]["scores.jsonl"]).items()}
    return out


# ─────────────────────────────────────────────────────────────────────────────
# The report
# ─────────────────────────────────────────────────────────────────────────────

def _na(x: Optional[Dict]) -> str:
    return f"{_f(x['acc'], '.3f')} ({x['n']})" if x else "-"


def _md(r: Dict) -> str:
    d = r["d5"]
    L = ["# Arm S2 (step-wise SFT) against the registered arms", "",
         "D5 was registered in compare_step.py before any S2 output existed. Proportions: value "
         "[Clopper-Pearson 95%] (k/n). Balanced: mean recall on yes and no, a miss when "
         "no verdict was given.", "", f"## D5: {d['verdict']}", ""]
    if d["verdict"] == "pending":
        L.append(f"- {d['why']}")
    else:
        c, h = d["c_exact"], d["holds"]
        L += ["| criterion, v1 test | S2 | registered | holds |", "|---|---|---|---|",
              f"| (a) first-check balanced, chained | {_f(d['a_first_check_balanced'], '.3f')} "
              f"| >= {SUPPORT} (refuted <= {REFUTE}) | {h['a']} |",
              f"| (b) R3 balanced | {_f(d['b_r3_balanced'], '.3f')} | >= {SUPPORT} | {h['b']} |",
              f"| (c) exact against sft_trace | {c['s2']}/{c['n']} against {c['sft_trace']}; "
              f"{c['mcnemar']['first_only']} S2 only, {c['mcnemar']['second_only']} sft_trace only, "
              f"p {c['mcnemar']['p_exact']:.4g} | > {TRACE_EXACT}, p < {ALPHA} | {h['c']} |"]
    L += ["", "Confounds (with any verdict): S2 reads 4.5x the trace arm's tokens per epoch and is "
          "supervised on 0.62x its target tokens; no definitions block, no step history; the "
          "lines-16/18 targets name the failing examples; 3,344 extra line-18 rows.", ""]

    L += ["## First line-18 check", "",
          "| set | sft_trace, own path | S2 chained (reached, at reference state) "
          "| S2 at the reference's state | position baseline |", "|---|---|---|---|---|"]
    for name, x in r["first_check"]["sets"].items():
        cell = lambda k: (f"{_f(x[k]['balanced'], '.3f')} / {_p(x[k]['accuracy'])}"
                          if k in x else "-")
        ch = x.get("s2 chained")
        extra = f" ({ch['reached']}, {ch['at_reference_state']} of {ch['n']})" if ch else ""
        L.append(f"| {name} | {cell('sft_trace')} | {cell('s2 chained')}{extra} "
                 f"| {cell('s2 gold')} | {cell('position baseline')} |")
    agree = r["first_check"]["chained_equals_gold_at_same_state"]
    L += ["", "Cells: balanced / accuracy. Chained and gold asked at the same state agree on "
          f"{_p(agree)}.", ""]

    L += ["## Exact by set (S2 strict: no illegal item in any call)", "",
          "| set | " + " | ".join(ARMS + ("s2", "s2 strict")) + " |",
          "|---|" + "---|" * (len(ARMS) + 2)]
    for name, row in r["exact"].items():
        L.append(f"| {name} | " + " | ".join(_p(row.get(a)) for a in ARMS + ("s2", "s2 strict"))
                 + " |")

    for corpus, sets in r["s2"].items():
        if corpus.endswith("r3_with_misses"):
            continue
        L += ["", f"## S2, the registered report's fields: {corpus}", "",
              "| set | parsed | exact | valid | clean | agreement (n) | r3 bal. | r3 bal., "
              "misses | choice | main rule | contrary | forbidden |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        misses = r["s2"][corpus + " r3_with_misses"]
        for name, s in sets.items():
            ag = s["agreement"]
            L.append(f"| {name} | {_p(s['parse_ok'])} | {_p(s['exact'])} | {_p(s['valid'])} "
                     f"| {_p(s['clean'])} | {_f(ag['mean'])} ({ag['n']}) | {_f(s['r3_balanced'])} "
                     f"| {_f(misses.get(name))} | {_p(s.get('algorithm_choice'))} "
                     f"| {_p(s.get('main_rule'))} | {_p(s.get('contrary'))} "
                     f"| {_p(s.get('forbidden_choice'))} |")

    for corpus, by_set in r["stops"].items():
        if by_set:
            L += ["", f"## Stops, chained: {corpus}", "", "| set | stopped | codes |", "|---|---|---|"]
            L += [f"| {n} | {_p(x['stopped'])} | {x['codes'] or '-'} |" for n, x in by_set.items()]

    for proto, title in (("gold", "at the reference's states (gold)"),
                         ("chained", "on the model's own run (chained)")):
        for group, t in r["steps"].get(proto, {}).items():
            L += ["", f"## Steps {title}: {group}", "",
                  "| kind or cell | n | acc | balanced | baseline bal. | unusable | witness | fold set "
                  "| at reference state |", "|---|---|---|---|---|---|---|---|---|"]
            at = t.get("at_reference_state", {})
            rows = list(t["by_kind"].items()) + [(f"cell {k}", v) for k, v in t["by_cell"].items()
                                                 if k != "other"]
            for k, s in rows:
                L.append(f"| {k} | {s['n']} | {_f(s['acc'], '.3f')} | {_f(s.get('balanced'), '.3f')} "
                         f"| {_f(s.get('baseline_balanced'), '.3f')} | {s['unusable']} "
                         f"| {_na(s.get('witness_correct'))} | {_na(s.get('set_correct'))} "
                         f"| {_na(at.get(k))} |")

    if r["contrasts"]:
        L += ["", "## Exact McNemar", "", "| contrast | n | S2 only | other only | p |",
              "|---|---|---|---|---|"]
        L += [f"| {k} | {v['n']} | {v['first_only']} | {v['second_only']} | {v['p']:.4f} |"
              for k, v in r["contrasts"].items()]
    L += ["", f"## Name invariance (exact, original against permuted; margin {MARGIN}; the "
          "registered reading is the 'all' row)", "",
          "| arm | split | original | permuted | delta [95%] | McNemar p | verdict |",
          "|---|---|---|---|---|---|---|"]
    for arm, inv in r["invariance"].items():
        for split, x in inv.items():
            if "incomplete" in x:
                L.append(f"| {arm} | {split} | - | - | - | - | incomplete: {x['incomplete']} |")
                continue
            lo, hi = x["delta_ci"]
            L.append(f"| {arm} | {split} | {_p(x['original'])} | {_p(x['permuted'])} "
                     f"| {x['delta']:+.3f} [{lo:+.3f}, {hi:+.3f}] | {x['mcnemar']['p']:.4f} "
                     f"| {x['verdict']} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results",
                    help="holds sft/, sft-permuted/, sft-step/ and sft-step-permuted/")
    ap.add_argument("--s2", default="s2", help="the S2 run: s2 (seed 0) or a replicate, s2_s1 ...")
    ap.add_argument("--out", default=None, help="default <results>/sft-step; a replicate's, "
                                                "<results>/sft-step/<run>")
    a = ap.parse_args(argv)
    default = Path(a.results) / "sft-step"
    out = Path(a.out) if a.out else default if a.s2 == "s2" else default / a.s2
    out.mkdir(parents=True, exist_ok=True)
    r = report(Path(a.results), a.s2)
    (out / "COMPARISON_STEP.json").write_text(json.dumps(r, indent=1, default=str), encoding="utf-8")
    (out / "COMPARISON_STEP.md").write_text(_md(r), encoding="utf-8")
    print(_md(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
