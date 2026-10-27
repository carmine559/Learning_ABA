"""What the arms write on a split, against what v1's training answers look like (CPU).

    python analysis/answer_shapes.py                  # table1
    python analysis/answer_shapes.py --split test     # or heldout; --s2 s2_s1 for a replicate

Per problem: the reference's answer and whether its shape lies outside the range of v1's
training answers; whether RoLe's facts are the positive examples, for the reference, the
trace arm and S2 at the reference's state; each arm's new-assumption depth and validity.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from sft.compare_sft import CORPORA, RESULTS, _read
from sft.compare_step import S2
from src.aba_corpus import problem_from_dict
from src.aba_prompts import parse_llm_output
from src.aba_score import load_eval

ARMS = ("base", "sft_endpoint", "sft_trace")
_R1 = re.compile(r"^R1\s+(\w+)\(X\)\s*:-\s*X\s*=\s*(\w+)\.?\s*$")


def _pred(atom: str) -> str:
    return re.sub(r"\s+", "", atom).split("(")[0]


def shape(text: str, background) -> Optional[Dict[str, int]]:
    """New rules, new assumptions, and how deep new assumptions nest: one introduced in a
    rule for the contrary of another introduced one is depth 2."""
    fw = parse_llm_output(text, background)
    if fw is None:
        return None
    contrary = {_pred(a): _pred(fw.contraries.get(a, "")) for a in fw.new_assumptions}
    bodies = collections.defaultdict(list)
    for r in fw.new_rules:
        bodies[_pred(r.head)].append({_pred(b) for b in r.body})

    def depth(a: str, seen: tuple = ()) -> int:
        inner = {b for body in bodies.get(contrary.get(a), []) for b in body
                 if b in contrary and b not in seen}
        return 1 + max((depth(b, seen + (a,)) for b in inner), default=0)

    used = {_pred(b) for r in fw.new_rules for b in r.body if _pred(b) in contrary}
    return {"new rules": len(fw.new_rules), "new assumptions": len(fw.new_assumptions),
            "new-assumption depth": max((depth(a) for a in used), default=0)}


def role(text: str) -> Set[str]:
    """RoLe's facts in a trace or a step answer: the R1 lines before Gen."""
    out = set()
    for line in text.split("Gen.")[0].split("\n"):
        m = _R1.match(line.strip())
        if m:
            out.add(f"{m.group(1)}({m.group(2)})")
    return out


def _facts(rules: List[str]) -> Set[str]:
    return role("\n".join("R1 " + r for r in rules))


def _positives(problem) -> Set[str]:
    return {re.sub(r"\s+", "", e) for e in problem.positive}


def training(corpus: Path) -> Dict:
    """The range of the reference's answers on v1's training problems, and how often RoLe's
    facts are the positive examples."""
    probs = {r["problem_id"]: problem_from_dict(r["problem"]) for r in _read(corpus / "problems.jsonl")}
    train = [r for r in _read(corpus / "sft_endpoint.jsonl") if r["split"] == "train"]
    rng = collections.defaultdict(set)
    for r in train:
        for k, v in (shape(r["target"], probs[r["problem_id"]].background) or {}).items():
            rng[k].add(v)
    facts = {r["problem_id"]: _facts(r["role_facts"]) for r in _read(corpus / "traces.jsonl")}
    is_pos = sum(facts[r["problem_id"]] == _positives(probs[r["problem_id"]]) for r in train)
    return {"range": {k: sorted(v) for k, v in rng.items()}, "n": len(train), "role_is_pos": is_pos}


def report(split: str, run: str, results: Path, corpus: Path) -> str:
    t = training(corpus)
    traces = {r["problem_id"]: r for f in ("traces.jsonl", "table1_traces.jsonl")
              for r in _read(corpus / f)}
    out = {a: {r["problem_id"]: r for r in _read(RESULTS["v1"] / a / "generations.jsonl")}
           for a in ARMS}
    valid = {a: {r["problem_id"]: bool(r["valid"]) for r in _read(RESULTS["v1"] / a / "scores.jsonl")}
             for a in ARMS}
    valid["S2"] = {r["problem_id"]: bool(r["valid"]) for r in
                   _read(results / S2["chained"][0].format(run) / "scores.jsonl")}
    s2_role = {r["problem_id"]: role(r["raw"]) for r in
               _read(results / S2["gold"][0].format(run) / "call_scores.jsonl") if r["kind"] == "role"}

    L = [f"# Answers on {split} against v1's training answers (S2 run {run})", "",
         "Training answers (the reference's, train split): "
         + "; ".join(f"{k} {v}" for k, v in t["range"].items()),
         f"RoLe's facts are the positive examples on {t['role_is_pos']}/{t['n']} training problems.", "",
         "| problem | reference outside the training range | RoLe = E+: reference / trace / S2 "
         "| new-assumption depth: reference / endpoint / trace | valid: " + " / ".join(ARMS + ("S2",)) + " |",
         "|---|---|---|---|---|"]
    count = collections.Counter()
    for row, problem, _ in load_eval(corpus):
        if row["split"] != split:
            continue
        pid, pos = row["problem_id"], _positives(problem)
        ref = shape(row["endpoint_target"], problem.background)
        outside = [f"{k} {v}" for k, v in ref.items() if v not in t["range"][k]]
        ref_pos = _facts(traces[pid]["role_facts"]) == pos
        tr = out["sft_trace"].get(pid)
        tr_pos = role(tr["raw_output"]) == pos if tr else None
        s2_pos = s2_role[pid] == pos if pid in s2_role else None
        depth = [ref["new-assumption depth"]] + [
            (shape(out[a][pid]["raw_output"], problem.background) or {}).get("new-assumption depth")
            if pid in out[a] else None for a in ("sft_endpoint", "sft_trace")]
        ok = [valid[a].get(pid) for a in ARMS + ("S2",)]
        count.update({"problems": 1, "ref outside": bool(outside), "ref RoLe = E+": ref_pos,
                      "trace RoLe = E+": bool(tr_pos), "S2 RoLe = E+": bool(s2_pos),
                      "trace RoLe = E+ where the reference's is not": bool(tr_pos) and not ref_pos,
                      "S2 RoLe = E+ where the reference's is not": bool(s2_pos) and not ref_pos})
        cell = lambda xs: " / ".join("-" if x is None else _yn(x) for x in xs)
        L.append(f"| {pid} | {', '.join(outside) or '-'} | {cell([ref_pos, tr_pos, s2_pos])} "
                 f"| {' / '.join('-' if d is None else str(d) for d in depth)} | {cell(ok)} |")
    L += [""] + [f"- {k}: {v}" for k, v in count.items()]
    return "\n".join(L) + "\n"


def _yn(x) -> str:
    return "yes" if x is True else "no" if x is False else str(x)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="table1", help="table1, test or heldout")
    ap.add_argument("--s2", default="s2", help="the S2 run: s2 (seed 0) or a replicate, s2_s1 ...")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    print(report(a.split, a.s2, Path(a.results), CORPORA["v1"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
