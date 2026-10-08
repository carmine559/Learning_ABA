"""The SFT arm comparison, registered before the trace arm's outputs were read.

    python compare_sft.py          # -> results/sft/COMPARISON.md and COMPARISON.json

Reads what eval_sft.py scored for every arm present (results/sft/<arm>/ and
results/sft-permuted/<arm>/; arms base, sft_endpoint, sft_trace); generates and
re-scores nothing except the constant responders of the floors. Registered on
2026-10-07, before any trace-arm output was scored:

Sets: test (t1-t5, 200); t8_decoy and t9_reuse by half (25 each); Table 1 (8
problems, named and anonymised); the permuted re-posing of test and held-out
(corpus/v1-permuted).

1. Correctness, every arm and set: exact (the algorithm's answer up to the names
   of fresh assumptions) and agreement beside the floor of the best constant
   training answer of the tier (always guard / always monotonic, scored here;
   on the permuted set renamed by each problem's permutation, and also literal,
   the name copier); valid and clean beside the same floor (1.00 on test).
   Exact also split by whether the gold string is a train target.
2. Held-out choice by half, chance 0.5 by construction: t8 algorithm_choice, and
   the main rule (lines 17-19) and the contrary (its fold, a later Gen
   iteration) against the algorithm's separately; t9 algorithm_choice and
   forbidden_choice.
3. The R3 decision at answer level: r3_balanced, floor 0.5, where both classes
   occur (test; t8 pooled over its halves).
4. Step level, arms that write traces: audit accuracy over the required
   decisions, written_accuracy, omitted share, per kind accuracy and balanced
   accuracy (floor 0.5; omissions with no truth to score are counted beside
   it), answer_matches_trace, and per problem exact x faithful (audit accuracy
   1, no illegal step, the answer is the trace's). Table 1: the gold trace
   reproduced up to its first decision
   whose signature no train trace has, and the verdicts where reusing a minted
   assumption is right (train traces answer it no, 652/652).
5. Name invariance, every arm: exact on each problem against exact on its
   permuted re-posing. Prediction: an arm that copies the tier's training names
   drops; one that executes the algorithm does not; the base model is the
   control.

Intervals: Clopper-Pearson 95% over problems; exact McNemar for paired contrasts
(arm against arm on the same problems, original against permuted); percentile
bootstrap over problems (2000 resamples, seed 0) for means of per-problem ratios.

Decision rules (the user's, 2026-10-07/08), read only on complete scores:
- Invariant: the bootstrap 95% CI of permuted minus original exact lies inside
  +-0.05; a drop: McNemar p < 0.05 with a negative delta. Both can hold and are
  then both reported. The registered verdict is over all 300 permuted problems;
  test and held-out are breakdowns.
- RL base: the arm with the higher exact over the discriminating sets (held-out
  100, permuted 300), trace against endpoint by exact McNemar; at p >= 0.05 the
  trace arm, whose written steps an audit or process reward can check.
- The token-matched endpoint run (TOKENS.json secondary epochs) only if the
  trace arm wins that contrast with p < 0.05.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.aba_algorithm import _current_framework
from src.aba_corpus import problem_from_dict, rename_preds
from src.aba_generalization import _pred_of
from src.aba_prompts import _parse_rule_line, parse_llm_output
from src.aba_replay import trace_lines
from src.aba_score import (YES_NO, _LINES, _norm, _rule_key, load_eval, reference,
                           score_output)

ARMS = ("base", "sft_endpoint", "sft_trace")
CORPORA = {"v1": Path("corpus/v1"), "permuted": Path("corpus/v1-permuted")}
RESULTS = {"v1": Path("results/sft"), "permuted": Path("results/sft-permuted")}


def _read(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# ─────────────────────────────────────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────────────────────────────────────

def _binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k), X ~ Bin(n, p)."""
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0 if k < n else 1.0
    lp, lq = math.log(p), math.log1p(-p)
    return min(1.0, sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                                 + i * lp + (n - i) * lq) for i in range(k + 1)))


def _root(f, lo: float = 0.0, hi: float = 1.0) -> float:
    """f increasing on [lo, hi]: the point where it crosses 0."""
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Optional[Tuple[float, float]]:
    if not n:
        return None
    lo = 0.0 if k == 0 else _root(lambda p: (1 - _binom_cdf(k - 1, n, p)) - alpha / 2)
    hi = 1.0 if k == n else _root(lambda p: alpha / 2 - _binom_cdf(k, n, p))
    return round(lo, 4), round(hi, 4)


def mcnemar(pairs: List[Tuple[bool, bool]]) -> Dict:
    """Exact two-sided McNemar on paired outcomes (a, b); thresholds read p_exact."""
    b = sum(1 for x, y in pairs if x and not y)
    c = sum(1 for x, y in pairs if y and not x)
    p = 1.0 if not b + c else min(1.0, 2 * _binom_cdf(min(b, c), b + c, 0.5))
    return {"n": len(pairs), "first_only": b, "second_only": c, "p": round(p, 4), "p_exact": p}


def bootstrap(values: List[float], seed: int = 0, n: int = 2000) -> Optional[Tuple[float, float]]:
    if not values:
        return None
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(n))
    return round(means[int(0.025 * n)], 4), round(means[int(0.975 * n) - 1], 4)


def prop(flags: List[bool]) -> Dict:
    k, n = sum(flags), len(flags)
    return {"k": k, "n": n, "p": round(k / n, 4) if n else None,
            "ci": clopper_pearson(k, n)}


# ─────────────────────────────────────────────────────────────────────────────
# Floors: the best constant training answer of each tier
# ─────────────────────────────────────────────────────────────────────────────

def _templates(corpus: Path) -> Dict[str, Dict[str, str]]:
    by = collections.defaultdict(collections.Counter)
    for r in _read(corpus / "sft_endpoint.jsonl"):
        if r["split"] == "train":
            by[(r["tier"], r["class"])][r["target"]] += 1
    out = collections.defaultdict(dict)
    for (tier, cls), c in by.items():
        out[tier]["always guard" if cls == "defeasible" else "always monotonic"] = \
            c.most_common(1)[0][0]
    return out


def _sha(path: Path) -> Optional[str]:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _inputs(corpus: Path) -> Dict[str, Optional[str]]:
    return {f: _sha(corpus / f) for f in ("problems.jsonl", "eval.jsonl")}


def floors(cache: Path) -> Dict:
    """Constant responders on the test rows of each corpus, scored like an arm.

    On the permuted corpus the tier's answer is renamed through each problem's
    permutation (roles known, class not), and also kept literal: the name copier.
    """
    out = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    templates = _templates(CORPORA["v1"])
    key = {"templates": templates, "sft_endpoint": _sha(CORPORA["v1"] / "sft_endpoint.jsonl")}
    for name, corpus in CORPORA.items():
        if not (corpus / "eval.jsonl").exists():
            continue
        stamp = {**key, "inputs": _inputs(corpus)}
        if out.get(name, {}).get("stamp") == stamp:
            continue
        perm = {r["problem_id"]: r.get("permutation") for r in _read(corpus / "problems.jsonl")}
        cards = collections.defaultdict(list)
        for row, problem, meta in load_eval(corpus):
            if row["split"] != "test":
                continue
            ref = reference(problem)
            for responder, text in templates[row["tier"]].items():
                answers = {responder: text}
                if perm.get(row["problem_id"]):
                    answers = {responder: rename_preds(text, perm[row["problem_id"]]),
                               f"name copier, {responder}": text}
                for resp, t in answers.items():
                    c = score_output(t, ref, meta)
                    cards[resp].append({"valid": c.valid, "clean": c.clean, "exact": c.exact,
                                        "agreement": c.agreement or 0.0})
        out[name] = {"stamp": stamp,
                     "responders": {resp: {k: round(sum(float(x[k]) for x in xs) / len(xs), 4)
                                           for k in ("valid", "clean", "exact", "agreement")}
                                    for resp, xs in cards.items()}}
    cache.write_text(json.dumps(out, indent=1), encoding="utf-8")
    return {name: x["responders"] for name, x in out.items() if (CORPORA[name] / "eval.jsonl").exists()}


# ─────────────────────────────────────────────────────────────────────────────
# Held-out: the main rule and the contrary, separately
# ─────────────────────────────────────────────────────────────────────────────

def _parts(fw, target: str) -> Tuple[collections.Counter, collections.Counter]:
    """The rules for the example predicate, and those for the contraries guarding
    them, as rules up to variable and fresh-assumption names."""
    fresh = {_pred_of(a) for a in fw.new_assumptions}
    mains = [r for r in fw.new_rules if _pred_of(r.head) == target]
    guards = {_pred_of(b) for r in mains for b in r.body} & fresh
    cons = {_pred_of(fw.contraries[a]) for a in fw.new_assumptions
            if a in fw.contraries and _pred_of(a) in guards}

    def sub(atom: str) -> str:
        p = _pred_of(atom)
        tag = "@a" if p in guards else "@c" if p in cons else None
        return tag + atom.strip()[len(p):] if tag else atom
    key = lambda r: _rule_key(sub(r.head), [sub(b) for b in r.body])
    return (collections.Counter(key(r) for r in mains),
            collections.Counter(key(r) for r in fw.new_rules if _pred_of(r.head) in cons))


def held_out_parts(raw: str, problem, meta: Dict) -> Dict[str, Optional[bool]]:
    bg, target = problem.background, _pred_of(problem.positive[0])
    ans = meta["answers"][meta["expected"]]
    algo = _current_framework(bg, [_parse_rule_line(r) for r in ans["new_rules"]],
                              ans["contraries"])
    want_main, want_con = _parts(algo, target)
    cand = parse_llm_output(raw, bg)
    if cand is None:
        return {"main_rule": False, "contrary": False if want_con else None}
    got_main, got_con = _parts(cand, target)
    return {"main_rule": got_main == want_main,
            "contrary": got_con == want_con if want_con else None}


# ─────────────────────────────────────────────────────────────────────────────
# Table 1: the gold prefix inside the training support
# ─────────────────────────────────────────────────────────────────────────────

def _role(pred: Optional[str], p) -> str:
    if pred in {_pred_of(e) for e in p.positive + p.negative}:
        return "example"
    if pred and re.match(r"^c_alpha_\d+$", pred):
        return "fresh contrary"
    return "learnable" if pred in p.learnable else "background"


def _asm_kind(atom: str) -> str:
    return "minted" if re.match(r"^alpha_\d+\(", atom.strip()) else "background"


def signature(ln: str, p) -> Optional[Tuple]:
    """What a decision line decides, without its names; None for structure or prose."""
    kind, m = next(((k, rx.match(ln)) for k, rx in _LINES if rx.match(ln)), (None, None))
    if kind in (None, "role", "gen", "done"):
        return None
    head = lambda text: _role(_pred_of(text.split(":-")[0].strip("[ ")), p)
    if kind in ("r1", "fact", "r2", "r3_on"):
        return kind, head(m.group(1))
    if kind in ("r4", "check", "reuse"):
        verdict = m.group(m.lastindex).lower()
        return ((kind, verdict) if kind == "r4" else
                (kind, verdict, head(m.group(1))) if kind == "check" else
                (kind, verdict, _asm_kind(m.group(1))))
    if kind == "candidates":
        k = len(re.findall(r"\[", m.group(1)))
        return kind, "none" if not k else f"n={min(k, 6)}"
    if kind == "scan":
        items = re.findall(r"\[([^\]]+)\]", m.group(1))
        return kind, "+".join(sorted({_asm_kind(a) for a in items})) or "none"
    if kind == "r3":
        rule = _parse_rule_line(m.group(1))
        asms = {_pred_of(a) for a in p.background.assumptions}
        kinds = sorted({_asm_kind(b) for b in (rule.body if rule else [])
                        if _asm_kind(b) == "minted" or _pred_of(b) in asms})
        return kind, head(m.group(1)), "+".join(kinds)
    return (kind,)


def _signatures(text: str, p) -> List[Optional[Tuple]]:
    """One per trace line as audit_trace numbers them (normalised, non-empty)."""
    return [signature(ln, p) for ln in map(_norm, trace_lines(text)) if ln]


def table1_support(corpus: Path) -> Dict[str, Dict[str, int]]:
    """Per Table 1 row: the gold line of the first decision no train trace has."""
    problems = {r["problem_id"]: problem_from_dict(r["problem"])
                for r in _read(corpus / "problems.jsonl") + _read(corpus / "table1_problems.jsonl")}
    seen = set()
    for r in _read(corpus / "sft_trace.jsonl"):
        if r["split"] == "train":
            seen.update(_signatures(r["target"], problems[r["problem_id"]]))
    out = {}
    for r in _read(corpus / "table1_eval.jsonl"):
        sigs = _signatures(r["trace_target"], problems[r["problem_id"]])
        line = next((i for i, s in enumerate(sigs) if s is not None and s not in seen), len(sigs))
        out[r["problem_id"]] = {"line": line, "lines": len(sigs),
                                "decisions_before": sum(s is not None for s in sigs[:line])}
    return out


# ─────────────────────────────────────────────────────────────────────────────
# The comparison
# ─────────────────────────────────────────────────────────────────────────────

def _sets(rows: List[Dict]) -> Dict[str, List[Dict]]:
    out = collections.defaultdict(list)
    for r in rows:
        if r["split"] == "test":
            out["test"].append(r)
        elif r["split"] == "table1":
            out[f"table1 {r['class']}"].append(r)
        else:
            out[f"{r['tier']} {r['class']}"].append(r)
    return dict(sorted(out.items()))


def _balanced(c: collections.Counter) -> Optional[float]:
    yes = c["yes/yes"] + c["yes/no"] + c["yes/omitted"]
    no = c["no/no"] + c["no/yes"] + c["no/omitted"]
    return round((c["yes/yes"] / yes + c["no/no"] / no) / 2, 4) if yes and no else None


def step_level(rows: List[Dict]) -> Optional[Dict]:
    audits = [r["audit"] for r in rows if r["audit"]]
    if not audits:
        return None
    kinds, conf = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(collections.Counter)
    for a in audits:
        for k, (right, total) in a["by_kind"].items():
            kinds[k][0] += right
            kinds[k][1] += total
        for k, c in a["confusion"].items():
            conf[k].update(c)
    acc = [a["accuracy"] for a in audits if a["accuracy"] is not None]
    written = [a["written_accuracy"] for a in audits if a["written_accuracy"] is not None]
    faithful = lambda a: (a["accuracy"] == 1.0 and not a["illegal"]
                          and a["answer_matches_trace"])
    cross = collections.Counter(
        f"{'exact' if r['exact'] else 'not exact'} / "
        f"{'no trace' if not r['audit'] else 'faithful' if faithful(r['audit']) else 'unfaithful'}"
        for r in rows)
    no_truth = collections.Counter()
    for a in audits:
        no_truth.update(a.get("omitted_no_truth", {}))
    return {
        "with_trace": prop([bool(r["audit"]) for r in rows]),
        "truncated": prop([r["finish"] == "length" for r in rows]),
        "accuracy": {"mean": round(sum(acc) / len(acc), 4) if acc else None, "ci": bootstrap(acc)},
        "written_accuracy": {"mean": round(sum(written) / len(written), 4) if written else None,
                             "ci": bootstrap(written)},
        "omitted_share": round(sum(a["n_omitted"] for a in audits)
                               / max(sum(a["n_decisions"] for a in audits), 1), 4),
        "by_kind": {k: {"right": r_, "n": t, "acc": round(r_ / t, 4)} for k, (r_, t) in kinds.items()},
        "balanced": {k: _balanced(conf[k]) for k in YES_NO if conf[k]},
        "balanced_excludes": dict(no_truth),          # omissions with no truth to score
        "answer_matches_trace": prop([bool(a["answer_matches_trace"]) for a in audits]),
        "any_illegal": prop([bool(a["illegal"]) for a in audits]),
        "halted": prop([bool(a["gave_up"]) for a in audits]),
        "exact_x_fidelity": dict(cross),
    }


def arm_report(rows: List[Dict], gens: Dict[str, Dict], items: Dict, train: set,
               support: Dict[str, int]) -> Dict:
    out = {}
    for name, rs in _sets(rows).items():
        s = {k: prop([bool(r[k]) for r in rs]) for k in ("parse_ok", "valid", "clean", "exact")}
        ag = [r["agreement"] for r in rs if r["agreement"] is not None]
        s["agreement"] = {"mean": round(sum(ag) / len(ag), 4) if ag else None, "n": len(ag),
                          "ci": bootstrap(ag)}
        r3 = collections.Counter(f"{'yes' if r['ref_defeasible'] else 'no'}/"
                                 f"{'yes' if r['defeasible'] else 'no'}"
                                 for r in rs if r["defeasible"] is not None)
        s["r3_balanced"] = _balanced(r3)
        s["exact_by_gold_in_train"] = {
            str(seen): prop([bool(r["exact"]) for r in rs
                             if (items[r["problem_id"]][0]["endpoint_target"] in train) == seen])
            for seen in (True, False)}
        if rs[0]["split"] == "heldout":
            s["algorithm_choice"] = prop([bool(r["algorithm_choice"]) for r in rs])
            s["forbidden_choice"] = prop([bool(r["forbidden_choice"]) for r in rs])
            if rs[0]["tier"] == "t8_decoy" and not all(r["problem_id"] in gens for r in rs):
                s["note"] = "main rule / contrary not computed: generations.jsonl missing rows"
            elif rs[0]["tier"] == "t8_decoy":
                parts = [held_out_parts(gens[r["problem_id"]]["raw_output"],
                                        *items[r["problem_id"]][1:]) for r in rs]
                s["main_rule"] = prop([x["main_rule"] for x in parts])
                if all(x["contrary"] is not None for x in parts):
                    s["contrary"] = prop([x["contrary"] for x in parts])
        s["step_level"] = step_level(rs)
        if name.startswith("table1") and s["step_level"]:
            s["step_level"]["in_support_prefix"] = prop(
                [_in_support(r, support) for r in rs if r["audit"]])
            s["step_level"]["minted_reuse_when_right"] = _minted_reuse(rs)
        out[name] = s
    return out


def _in_support(r: Dict, support: Dict[str, Dict[str, int]]) -> bool:
    """The trace reproduces the gold up to its first decision outside the train support."""
    s = support[r["problem_id"]]
    return round(r["audit"]["gold_prefix"] * s["lines"]) >= s["line"]


def _minted_reuse(rs: List[Dict]) -> Dict[str, int]:
    """Verdicts at line-38 checks of a minted assumption whose truth is yes."""
    c = collections.Counter()
    for r in rs:
        for n, kind, ok, truth, said, subject in (r["audit"] or {}).get("log", []):
            if kind == "reuse_check" and truth and _asm_kind(subject) == "minted":
                c[said if isinstance(said, str) else ("yes" if said else "no")] += 1
    return dict(c)


MARGIN = 0.05                  # invariance: the delta's 95% CI inside +-MARGIN


def _verdict(ci: Tuple[float, float], delta: float, p: float) -> str:
    """Both registered tests, reported together when both hold."""
    within = -MARGIN <= ci[0] and ci[1] <= MARGIN
    moved = "significant drop" if p < 0.05 and delta < 0 else "significant rise" if p < 0.05 else ""
    if within:
        return f"invariant within +-{MARGIN}" + (f", {moved}" if moved else "")
    return moved.replace("significant ", "") if moved else "inconclusive"


def invariance(v1: Dict[str, Dict], perm: Dict[str, Dict], expected: Dict[str, set]) -> Dict:
    """Per split, and over all permuted problems (the registered verdict)."""
    out = {}
    for split in ("all", "test", "heldout"):
        want = expected["all"] if split == "all" else expected[split]
        missing = len(want - set(v1)) + len(want - set(perm))
        if missing:
            out[split] = {"incomplete": f"{missing} of {2 * len(want)} paired scores missing"}
            continue
        pairs = [(bool(v1[pid]["exact"]), bool(perm[pid]["exact"])) for pid in sorted(want)]
        diffs = [float(b) - float(a) for a, b in pairs]
        delta, ci, m = round(sum(diffs) / len(diffs), 4), bootstrap(diffs), mcnemar(pairs)
        out[split] = {"original": prop([a for a, _ in pairs]), "permuted": prop([b for _, b in pairs]),
                      "delta": delta, "delta_ci": ci, "mcnemar": m,
                      "verdict": _verdict(ci, delta, m["p_exact"])}
    return out


def decisions(arms: Dict[str, Dict[str, Dict[str, Dict]]], items_by: Dict) -> Dict:
    """The RL base and the token-matched run, by the registered rules."""
    pairs, missing = [], []
    for corpus, splits in (("v1", ("heldout",)), ("permuted", ("test", "heldout"))):
        want = {pid for pid, (row, _, _) in items_by.get(corpus, {}).items() if row["split"] in splits}
        T, E = (arms.get(corpus, {}).get(a, {}) for a in ("sft_trace", "sft_endpoint"))
        gap = len(want - set(T)) + len(want - set(E))
        if not want or gap:
            missing.append(f"{corpus}: {gap if want else 'all'} of {2 * len(want)} scores missing")
            continue
        pairs += [(bool(T[pid]["exact"]), bool(E[pid]["exact"])) for pid in sorted(want)]
    if missing:
        return {"pending": "; ".join(missing)}
    m = mcnemar(pairs)
    trace_wins = m["p_exact"] < 0.05 and m["first_only"] > m["second_only"]
    return {"trace_vs_endpoint": m,
            "rl_base": "sft_endpoint" if m["p_exact"] < 0.05 and not trace_wins else "sft_trace",
            "token_matched_run": trace_wins}


def compare(arms: Dict[str, Dict[str, Dict[str, Dict]]]) -> Dict:
    """Arm against arm on the same problems: exact, by set."""
    out = {}
    names = [a for a in ARMS if a in arms["v1"]]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for corpus in arms:
                if a not in arms[corpus] or b not in arms[corpus]:
                    continue
                A, B = arms[corpus][a], arms[corpus][b]
                for name, rs in _sets(list(A.values())).items():
                    pairs = [(bool(r["exact"]), bool(B[r["problem_id"]]["exact"]))
                             for r in rs if r["problem_id"] in B]
                    out[f"{corpus} {name}: {a} vs {b}"] = mcnemar(pairs)
    return out


def _p(x: Optional[Dict]) -> str:
    if not x or x.get("p") is None:
        return "-"
    lo, hi = x["ci"]
    return f"{x['p']:.2f} [{lo:.2f}, {hi:.2f}] ({x['k']}/{x['n']})"


def _f(x: Optional[float], fmt: str = ".2f") -> str:
    return "-" if x is None else format(x, fmt)


def _m(x: Dict) -> str:
    ci = x.get("ci")
    return f"{_f(x['mean'], '.3f')}" + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "")


def _md(report: Dict) -> str:
    L = ["# SFT arm comparison", "",
         "Registered in compare_sft.py before the trace arm was scored. "
         "Proportions: value [Clopper-Pearson 95%] (k/n); means: value [bootstrap 95%].", "",
         "## Floors (test rows; permuted: the tier's answer renamed by the problem's "
         "permutation, and literal as a name copier)", ""]
    for corpus, resp in report["floors"].items():
        for name, f in resp.items():
            L.append(f"- {corpus}, {name}: " + ", ".join(f"{k} {v:.2f}" for k, v in f.items()))
    for corpus, arms in report["arms"].items():
        L += ["", f"## Correctness and held-out choice: {corpus}", "",
              "| arm | set | parsed | exact | valid | clean | agreement (n) | r3 bal. | choice "
              "| main rule | contrary | forbidden |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, sets in arms.items():
            for name, s in sets.items():
                ag = s["agreement"]
                L.append(f"| {arm} | {name} | {_p(s['parse_ok'])} | {_p(s['exact'])} | {_p(s['valid'])} "
                         f"| {_p(s['clean'])} | {_f(ag['mean'])} ({ag['n']}) | {_f(s['r3_balanced'])} "
                         f"| {_p(s.get('algorithm_choice'))} | {_p(s.get('main_rule'))} "
                         f"| {_p(s.get('contrary'))} | {_p(s.get('forbidden_choice'))} |"
                         + (f" {s['note']}" if s.get("note") else ""))
        tiers = report["r3_by_tier"].get(corpus, {})
        L += ["", "r3 balanced, held-out tiers pooled over both halves (undefined where one class): "
              + "; ".join(f"{arm} " + ", ".join(f"{t} {_f(v)}" for t, v in sorted(x.items()))
                          for arm, x in tiers.items())]
        L += ["", f"## Step level: {corpus}", "",
              "| arm | set | with trace | truncated | accuracy | written | omitted | subsume bal. "
              "| check bal. | reuse bal. | answer = trace | in support |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        detail = []
        for arm, sets in arms.items():
            for name, s in sets.items():
                st = s["step_level"]
                if not st:
                    continue
                acc, w, bal = st["accuracy"], st["written_accuracy"], st["balanced"]
                L.append(f"| {arm} | {name} | {_p(st['with_trace'])} | {_p(st['truncated'])} "
                         f"| {_m(acc)} | {_m(w)} | {_f(st['omitted_share'], '.3f')} "
                         f"| {_f(bal.get('subsume'))} | {_f(bal.get('check'))} "
                         f"| {_f(bal.get('reuse_check'))} | {_p(st['answer_matches_trace'])} "
                         f"| {_p(st.get('in_support_prefix'))} |")
                kinds = ", ".join(f"{k} {v['acc']:.2f} ({v['right']}/{v['n']})"
                                  for k, v in st["by_kind"].items())
                cross = ", ".join(f"{k} {v}" for k, v in sorted(st["exact_x_fidelity"].items()))
                extra = (f"; minted reuse where right: {st['minted_reuse_when_right'] or 'none reached'}"
                         if "minted_reuse_when_right" in st else "")
                excl = (f"; omitted with no truth, outside balanced: {st['balanced_excludes']}"
                        if st["balanced_excludes"] else "")
                detail.append(f"- {arm}, {name}: {kinds}. Per problem: {cross}; any illegal "
                              f"{_p(st['any_illegal'])}; halted {_p(st['halted'])}{excl}{extra}")
        if detail:
            L += ["", "Per kind (right/required) and correctness x fidelity:", ""] + detail
    L += ["", "## Exact by template novelty (all rows: is the gold string a train target?)", "",
          "| corpus | arm | gold in train | gold not in train |", "|---|---|---|---|"]
    for corpus, by_arm in report["novelty"].items():
        for arm, x in by_arm.items():
            L.append(f"| {corpus} | {arm} | {_p(x['True'])} | {_p(x['False'])} |")
    if report["invariance"]:
        L += ["", f"## Name invariance (exact, original against permuted; margin {MARGIN}; "
              "the registered verdict is the 'all' row)", "",
              "| arm | split | original | permuted | delta [95%] | McNemar p | verdict |",
              "|---|---|---|---|---|---|---|"]
        for arm, inv in report["invariance"].items():
            for split, x in inv.items():
                if "incomplete" in x:
                    L.append(f"| {arm} | {split} | - | - | - | - | incomplete: {x['incomplete']} |")
                    continue
                lo, hi = x["delta_ci"]
                L.append(f"| {arm} | {split} | {_p(x['original'])} | {_p(x['permuted'])} "
                         f"| {x['delta']:+.3f} [{lo:+.3f}, {hi:+.3f}] | {x['mcnemar']['p']:.4f} "
                         f"| {x['verdict']} |")
    d = report["decisions"]
    L += ["", "## Registered decisions", ""]
    if "pending" in d:
        L.append(f"- pending: {d['pending']}")
    else:
        m = d["trace_vs_endpoint"]
        L += [f"- trace against endpoint, exact over held-out + permuted: {m['first_only']} trace only, "
              f"{m['second_only']} endpoint only of {m['n']}, McNemar p {m['p_exact']:.4g}",
              f"- RL base: {d['rl_base']}", f"- token-matched endpoint run: "
              f"{'yes' if d['token_matched_run'] else 'no'}"]
    L += ["", "## Arm against arm (exact, exact McNemar)", "",
          "| contrast | n | first only | second only | p |", "|---|---|---|---|---|"]
    L += [f"| {k} | {v['n']} | {v['first_only']} | {v['second_only']} | {v['p']:.4f} |"
          for k, v in report["contrasts"].items()]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results",
                    help="holds sft/<arm>/ and sft-permuted/<arm>/")
    ap.add_argument("--out", default=None, help="default <results>/sft")
    a = ap.parse_args(argv)
    results = {c: Path(a.results) / p.name for c, p in RESULTS.items()}
    out = Path(a.out) if a.out else results["v1"]

    train = {r["target"] for r in _read(CORPORA["v1"] / "sft_endpoint.jsonl") if r["split"] == "train"}
    support = table1_support(CORPORA["v1"])
    arms, items_by = {}, {}
    for corpus, root in results.items():
        if not (CORPORA[corpus] / "eval.jsonl").exists():
            continue
        items = {row["problem_id"]: (row, problem, meta) for row, problem, meta in load_eval(CORPORA[corpus])}
        items_by[corpus] = items
        for arm in ARMS:
            rows = _read(root / arm / "scores.jsonl")
            if not rows:
                continue
            m = root / arm / "EVAL_MANIFEST.json"
            if m.exists():                          # scores of another corpus build are refused
                made = json.loads(m.read_text(encoding="utf-8"))["sha256"]
                stale = [f for f, h in made.items() if _sha(CORPORA[corpus] / f) != h]
                if stale:
                    raise SystemExit(f"{root / arm} was generated on another {stale} of {CORPORA[corpus]}")
            arms.setdefault(corpus, {})[arm] = {r["problem_id"]: r for r in rows}

    split_of = lambda c, s: {pid for pid, (row, _, _) in items_by.get(c, {}).items() if row["split"] == s}
    expected = {s: split_of("permuted", s) for s in ("test", "heldout")}
    expected["all"] = expected["test"] | expected["heldout"]
    report = {"floors": floors(out / "floors.json"), "arms": {}, "invariance": {},
              "contrasts": compare(arms), "decisions": decisions(arms, items_by),
              "novelty": {}, "r3_by_tier": {}}
    for corpus, by_arm in arms.items():
        for arm, rows in by_arm.items():
            gens = {g["problem_id"]: g for g in _read(results[corpus] / arm / "generations.jsonl")}
            report["arms"].setdefault(corpus, {})[arm] = arm_report(
                list(rows.values()), gens, items_by[corpus], train, support)
            report["novelty"].setdefault(corpus, {})[arm] = {
                str(seen): prop([bool(r["exact"]) for r in rows.values()
                                 if (items_by[corpus][r["problem_id"]][0]["endpoint_target"]
                                     in train) == seen])
                for seen in (True, False)}
            tiers = collections.defaultdict(collections.Counter)
            for r in rows.values():
                if r["split"] == "heldout" and r["defeasible"] is not None:
                    tiers[r["tier"]][f"{'yes' if r['ref_defeasible'] else 'no'}/"
                                     f"{'yes' if r['defeasible'] else 'no'}"] += 1
            report["r3_by_tier"].setdefault(corpus, {})[arm] = {t: _balanced(c) for t, c in tiers.items()}
    for arm in ARMS:
        if arm in arms.get("v1", {}) and arm in arms.get("permuted", {}):
            report["invariance"][arm] = invariance(arms["v1"][arm], arms["permuted"][arm], expected)

    (out / "COMPARISON.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    (out / "COMPARISON.md").write_text(_md(report), encoding="utf-8")
    print(_md(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
