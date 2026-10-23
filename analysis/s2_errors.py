"""Where arm S2's chained runs first go wrong, replayed from their recorded calls (CPU).

    python analysis/s2_errors.py              # s2 (seed 0)
    python analysis/s2_errors.py --s2 s2_s1   # a replicate

Each call is judged against the reference's answer at the same state (eval_stepwise's
ShadowOracle and judge_run). Beside the run's figures, the facts of v1's training rows
they are read against, and Table 1 against the range of v1's training problems.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from sft.compare_sft import CORPORA, _read
from sft.compare_step import S2
from sft.eval_stepwise import ShadowOracle, judge_run, replay, run
from sft.train_step import load as load_steps
from src.aba_score import load_eval
from src.aba_steps import DECISIONS

STEPS = Path("corpus/v1-step")
_PRED = re.compile(r"([a-z]\w*)\(")
_BODY = re.compile(r":-\s*([a-z]\w*)\(")
_ATOM = re.compile(r"([a-z]\w*)\(([^()]*)\)")


def _set(row: Dict) -> str:
    return row["split"] if row["split"] in ("test", "table1") else row["tier"]


def _alpha(xs: List[str]) -> List[str]:
    """Alphabetical order, dom last."""
    return sorted(x for x in xs if x != "dom") + [x for x in xs if x == "dom"]


def _yn(x) -> str:
    return {True: "yes", False: "no"}.get(x, "none")


def _origin(state: Dict) -> str:
    return "minted" if state["asm"] in state["asms"] else "background"


def _examples(problem) -> Set[str]:
    return {_PRED.match(e).group(1) for e in problem.positive + problem.negative}


def replayed(out: Path, corpus: Path) -> List[Dict]:
    """Each scored chained run, its calls judged against the reference at the same state."""
    calls = collections.defaultdict(list)
    for c in _read(out / "calls.jsonl"):
        calls[c["problem_id"]].append(c)
    exact = {r["problem_id"]: bool(r["exact"]) for r in _read(out / "scores.jsonl")}
    runs = []
    for row, problem, _ in load_eval(corpus):
        pid = row["problem_id"]
        if pid in exact:
            oracle = ShadowOracle(problem, replay(sorted(calls[pid], key=lambda c: c["i"])))
            run(problem, oracle)
            runs.append({"row": row, "log": oracle.log, "exact": exact[pid],
                         "judged": judge_run(problem, oracle.log)})
    return runs


# ─────────────────────────────────────────────────────────────────────────────
# The runs
# ─────────────────────────────────────────────────────────────────────────────

def first_wrong(runs: List[Dict]) -> Dict[str, Dict]:
    """Per set: runs, every call right, wrong decisions at the reference's state, and the
    first wrong call's kind against exact."""
    out = {}
    for r in runs:
        s = out.setdefault(_set(r["row"]), {"runs": 0, "right": 0, "on_path": 0,
                                           "first": collections.Counter()})
        s["runs"] += 1
        w = next((c for c in r["judged"] if not c["correct"]), None)
        if w is None:
            s["right"] += 1
        else:
            s["first"][(w["kind"], r["exact"])] += 1
        s["on_path"] += sum(c["kind"] in DECISIONS and c["on_path"] and not c["correct"]
                            for c in r["judged"])
    return out


def listed(ref: List[str], got: List[str]) -> str:
    """S2's line-17 list against the reference's, as fold bodies in order."""
    if got == ref:
        return "right"
    if got == _alpha(ref):
        return "right set, alphabetical"
    if got in (ref[1:], _alpha(ref[1:])):
        return "only the first dropped"
    return "other drops" if set(got) < set(ref) else "other"


def fold_lists(runs: List[Dict], seen: Dict) -> Dict:
    """Test line-17 calls by whether the reference's order is alphabetical; each right
    candidate kept or dropped, by whether its name is a candidate in training."""
    lists, names = collections.defaultdict(collections.Counter), collections.Counter()
    for r in runs:
        if r["row"]["split"] != "test":
            continue
        for c, e in zip(r["judged"], r["log"]):
            if c["kind"] != "fold_candidates" or e.get("answer") is None:
                continue
            ref = [_BODY.search(x.to_prolog()).group(1) for x, _ in e["gold"]]
            got = [_BODY.search(x.to_prolog()).group(1) for x, _ in e["answer"]]
            lists["agree" if ref == _alpha(ref) else "differ"][listed(ref, got)] += 1
            for b in ref:
                if b != "dom":
                    names[(b in seen[(r["row"]["tier"], c["src"])], b in got)] += 1
    return {"lists": lists, "names": names}


def line38(runs: List[Dict]) -> collections.Counter:
    """Runs whose first wrong call is at line 38: set, class, fact, assumption, said, truth."""
    out = collections.Counter()
    for r in runs:
        i = next((i for i, c in enumerate(r["judged"]) if not c["correct"]), None)
        if i is not None and r["judged"][i]["kind"] == "reuse_check":
            w = r["judged"][i]
            out[(_set(r["row"]), r["row"]["class"], w["src"], _origin(r["log"][i]["state"]),
                 w["said"], w["truth"])] += 1
    return out


def gold_line38(gold: Path) -> Dict[str, List[int]]:
    """Line 38 at the reference's states, per set: n, S2 right, position baseline right."""
    out = collections.defaultdict(lambda: [0, 0, 0])
    for r in _read(gold / "call_scores.jsonl"):
        if r["kind"] == "reuse_check":
            s = out[_set(r)]
            s[0], s[1], s[2] = s[0] + 1, s[1] + r["correct"], s[2] + (r["baseline"] == r["truth"])
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Training rows and Table 1
# ─────────────────────────────────────────────────────────────────────────────

def training(steps: Path) -> Dict:
    """v1's training rows: fold lists, their names per (tier, src), line 38 by the state's
    shape, RoLe answers with a non-example predicate; and the training problems."""
    _, probs, rows = load_steps(steps)
    train = rows["train"]
    folds = [(r, _BODY.findall(r["target"])) for r in train if r["kind"] == "fold_candidates"]
    seen = collections.defaultdict(set)
    for r, bodies in folds:
        seen[(r["tier"], r["src"])].update(bodies)
    role = [r for r in train if r["kind"] == "role"]
    return {"folds": len(folds), "alphabetical": sum(b == _alpha(b) for _, b in folds),
            "seen": seen,
            "line38": collections.Counter((r["src"], _origin(r["state"]), r["verdict"])
                                          for r in train if r["kind"] == "reuse_check"),
            "role": len(role),
            "role_off": sum(bool(set(_PRED.findall(r["target"])) - _examples(probs[r["problem_id"]]))
                            for r in role),
            "problems": [probs[p] for p in sorted({r["problem_id"] for r in train})]}


def features(problem) -> Dict[str, int]:
    """The problem's shape, where Table 1 and v1 can differ."""
    bg, arity = problem.background, {}
    for r in bg.rules:
        for a in [r.head] + list(r.body):
            m = _ATOM.search(a)
            if m:
                arity[m.group(1)] = len(m.group(2).split(","))
    eq = sum(bool(r.body) and all("=" in b for b in r.body) for r in bg.rules)
    return {"|T|": len(problem.learnable), "max arity": max(arity.values(), default=0),
            "constants": len(problem.domain), "assumptions": len(bg.assumptions),
            "facts written X = t": eq, "other rules with a body": sum(bool(r.body) for r in bg.rules) - eq}


def table1(train_problems: List, corpus: Path) -> Dict:
    """Table 1's problems against the range of v1's training problems, and whether the
    reference's RoLe answer has a non-example predicate."""
    rng = collections.defaultdict(set)
    for p in train_problems:
        for k, v in features(p).items():
            rng[k].add(v)
    role = {r["problem_id"]: r["role_facts"] for r in _read(corpus / "table1_traces.jsonl")}
    rows = []
    for row, problem, _ in load_eval(corpus):
        if row["split"] == "table1":
            f = features(problem)
            off = {_PRED.match(x).group(1) for x in role[row["problem_id"]]} - _examples(problem)
            rows.append((row["problem_id"], f, [k for k, v in f.items() if v not in rng[k]], off))
    return {"range": {k: sorted(v) for k, v in rng.items()}, "problems": rows}


# ─────────────────────────────────────────────────────────────────────────────
# The report
# ─────────────────────────────────────────────────────────────────────────────

def _first_md(by_set: Dict) -> List[str]:
    L = ["| set | runs | every call right | wrong decisions on the path | first wrong call "
         "(exact / not) |", "|---|---|---|---|---|"]
    for name, s in by_set.items():
        kinds = collections.defaultdict(lambda: [0, 0])
        for (kind, exact), n in s["first"].items():
            kinds[kind][0 if exact else 1] += n
        cell = ", ".join(f"{k} {e}/{n}" for k, (e, n) in sorted(kinds.items(),
                                                                  key=lambda x: -sum(x[1])))
        L.append(f"| {name} | {s['runs']} | {s['right']} | {s['on_path']} | {cell or '-'} |")
    return L


def _md(run: str, out: Dict, t: Dict, tab1: Dict) -> str:
    L = [f"# Where S2 run {run} first goes wrong (calls judged at the same state)", ""]
    for name, x in out.items():
        L += [f"## {name}: {x['path']}", ""] + _first_md(x["first"]) + [""]
        for group in ("agree", "differ"):
            c = x["folds"]["lists"].get(group)
            if c:
                L.append(f"- line 17 on test, background order and alphabetical {group}: "
                         f"{sum(c.values())} calls; " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
        nm = x["folds"]["names"]
        for known in (True, False):
            n = nm[(known, True)] + nm[(known, False)]
            if n:
                L.append(f"- right candidates whose name is {'' if known else 'never '}a "
                         f"candidate in training: dropped {nm[(known, False)]}/{n}")
        for k, n in sorted(x.get("line38", {}).items(), key=str):
            L.append(f"- first wrong at line 38: {k[0]} {k[1]}, {k[2]} fact, {k[3]} assumption, "
                     f"said {_yn(k[4])}, truth {_yn(k[5])}: {n}")
        for s, (n, ok, base) in sorted(x.get("gold38", {}).items()):
            L.append(f"- line 38 at the reference's states, {s}: S2 {ok}/{n}, position baseline {base}/{n}")
        L.append("")
    L += ["## v1's training rows", "",
          f"- fold lists in alphabetical order: {t['alphabetical']}/{t['folds']}",
          f"- RoLe answers with a predicate other than the examples': {t['role_off']}/{t['role']}",
          "- line 38 by (fact, assumption, answer): "
          + ", ".join(f"{s} fact, {o} assumption, {_yn(v)}: {n}"
                      for (s, o, v), n in sorted(t["line38"].items())), "",
          "## Table 1 against v1's training problems", "",
          "Training range: " + "; ".join(f"{k} {v}" for k, v in tab1["range"].items()), "",
          "| problem | outside the training range | RoLe on a non-example predicate |", "|---|---|---|"]
    for pid, f, outside, off in tab1["problems"]:
        L.append(f"| {pid} | {', '.join(f'{k} {f[k]}' for k in outside) or '-'} "
                 f"| {', '.join(sorted(off)) or '-'} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--s2", default="s2", help="the S2 run: s2 (seed 0) or a replicate, s2_s1 ...")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    t = training(STEPS)
    out = {}
    for name in ("chained", "permuted"):
        sub, corpus = S2[name]
        path = Path(a.results) / sub.format(a.s2)
        runs = replayed(path, CORPORA[corpus])
        if not runs:
            print(f"no scored runs in {path}")
            continue
        out[corpus] = {"path": path.as_posix(), "first": first_wrong(runs),
                       "folds": fold_lists(runs, t["seen"]), "line38": line38(runs)}
        if name == "chained":
            out[corpus]["gold38"] = gold_line38(Path(a.results) / S2["gold"][0].format(a.s2))
    print(_md(a.s2, out, t, table1(t["problems"], CORPORA["v1"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
