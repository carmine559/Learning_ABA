"""The persisted SFT corpus: tier spec v2 problems, held-out tiers, splits.

Layout of a built corpus (`build_corpus.py` writes it):

    problems.jsonl      every accepted problem, all splits, with its seed,
                        tier, split, class, structural signature and name map
    traces.jsonl        the RunRecord of the reference on each problem
    sft_trace.jsonl     train + val prompts with the trace target
    sft_endpoint.jsonl  the same prompts with the endpoint target
    eval.jsonl          test + held-out prompts with both gold targets and the
                        scorer's ceiling on them; never trained on
    rejects.jsonl       every attempt that was not accepted, and why
    table1_*.jsonl      the paper's Table 1 problems (src/aba_zenodo.py), named
                        and anonymised: problems, traces, eval; never trained on
    MANIFEST.json/.md   provenance, counts, gates, pre-registrations

`build_permuted` writes an evaluation-only corpus (problems.jsonl, eval.jsonl,
MANIFEST.json/.md): a built corpus's test and held-out problems, re-posed under
a seeded derangement of each problem's predicate names.

Problems are posed whole, as in Definition 1: prompt and gold trace see all of
a problem's examples. Leakage is prevented between problems instead: no two
accepted problems, in any split, share a structural signature, and none shares
one with a Table 1 problem.

Splits are assigned in a fixed order (held-out, test, val, train), each stream
taking the next accepted problems, so growing the train split never changes
the evaluation problems.
"""
from __future__ import annotations

import collections
import hashlib
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from src.aba_types import ABAFramework, LearningProblem, Rule
from src.aba_anonymize import (NameMap, anonymize_problem, collect_symbols,
                               rewrite_atom, rewrite_rule)
from src.aba_dataset import (
    CORPUS_TIERS, CORPUS_TIER_SPEC_VERSION, HELDOUT_TIERS,
    generate_corpus_problem, generate_heldout_problem, check_heldout,
)
from src.aba_sft import sft_example, gold_self_score, Untrainable
from src.aba_replay import check_example
from src.aba_prompts import SFT_PROMPT_VERSION, _parse_rule_line
from src.aba_tracelog import solve_and_log
from src.aba_zenodo import (TABLE1, ZENODO_DOI, ZENODO_MD5, RELEASE,
                            load_table1, r2_gap)


# ─────────────────────────────────────────────────────────────────────────────
# Serialisation
# ─────────────────────────────────────────────────────────────────────────────

def _rule_to_dict(r: Rule) -> Dict:
    return {"head": r.head, "body": list(r.body)}


def problem_to_dict(p: LearningProblem) -> Dict:
    bg = p.background
    return {
        "problem_id": p.problem_id,
        "background": {"rules": [_rule_to_dict(r) for r in bg.rules],
                       "assumptions": list(bg.assumptions),
                       "contraries": dict(bg.contraries)},
        "positive": list(p.positive), "negative": list(p.negative),
        "learnable": list(p.learnable), "domain": list(p.get_domain()),
    }


def problem_from_dict(d: Dict) -> LearningProblem:
    bg = d["background"]
    return LearningProblem(
        background=ABAFramework(
            rules=[Rule(r["head"], list(r["body"])) for r in bg["rules"]],
            assumptions=list(bg["assumptions"]),
            contraries=dict(bg["contraries"])),
        positive=list(d["positive"]), negative=list(d["negative"]),
        learnable=list(d["learnable"]), domain=list(d["domain"]),
        problem_id=d["problem_id"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Structural signature
# ─────────────────────────────────────────────────────────────────────────────

_ATOM_RE = re.compile(r"^\s*([a-z]\w*)\s*(?:\((.*)\))?\s*$")


def _split_atom(atom: str) -> Tuple[str, List[str]]:
    m = _ATOM_RE.match(atom)
    if not m:
        return atom.strip(), []
    args = [a.strip() for a in (m.group(2) or "").split(",") if a.strip()]
    return m.group(1), args


def structural_signature(p: LearningProblem, rounds: int = 3) -> str:
    """Weisfeiler-Lehman hash of the problem, invariant to renaming and order.

    Nodes: predicates (coloured by role), constants (by example label), and
    one node per non-fact rule. Edges: fact argument, rule head, rule body,
    assumption-contrary, example. Anonymisation is not a canonical form (it
    names by first appearance), so it cannot serve here.
    """
    bg = p.background
    asm = {_split_atom(a)[0] for a in bg.assumptions}
    con = {_split_atom(c)[0] for c in bg.contraries.values()}
    learn = set(p.learnable)
    colour: Dict[Tuple, str] = {}
    adj: Dict[Tuple, List[Tuple[str, Tuple]]] = collections.defaultdict(list)

    def edge(a, b, label):
        adj[a].append((label, b))
        adj[b].append((label, a))

    def pred(name, arity):
        node = ("p", name)
        colour[node] = repr(("pred", name in asm, name in con,
                             name in learn, arity))
        return node

    labels = {}
    for tag, atoms in (("pos", p.positive), ("neg", p.negative)):
        for e in atoms:
            name, args = _split_atom(e)
            for c in args:
                labels[c] = tag
    for c in p.get_domain():
        colour[("c", c)] = repr(("const", labels.get(c, "none")))
    for tag, atoms in (("pos", p.positive), ("neg", p.negative)):
        for e in atoms:
            name, args = _split_atom(e)
            for i, c in enumerate(args):
                edge(pred(name, len(args)), ("c", c), f"{tag}{i}")

    for k, r in enumerate(bg.rules):
        name, args = _split_atom(r.head)
        if not r.body and args and all(a[:1].islower() for a in args):
            for i, c in enumerate(args):
                colour.setdefault(("c", c), repr(("const", "none")))
                edge(pred(name, len(args)), ("c", c), f"arg{i}")
            continue
        node = ("r", k)
        colour[node] = repr(("rule", len(r.body)))
        edge(node, pred(name, len(args)), "head")
        for b in r.body:
            bn, ba = _split_atom(b)
            edge(node, pred(bn, len(ba)), "body")
    for a, c in bg.contraries.items():
        an, aa = _split_atom(a)
        cn, ca = _split_atom(c)
        edge(pred(an, len(aa)), pred(cn, len(ca)), "contrary")

    for _ in range(rounds):
        colour = {v: hashlib.sha1(repr((col, sorted(
            (lab, colour[u]) for lab, u in adj[v]))).encode()).hexdigest()
            for v, col in colour.items()}
    return hashlib.sha1(repr(sorted(colour.values())).encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
# Surface cues
# ─────────────────────────────────────────────────────────────────────────────

def cue_features(p: LearningProblem) -> Dict[str, bool]:
    """Features a model could read off the prompt without folding or checking.

    Exception predicates are the bodies of rules for a contrary; "key-like"
    predicates hold for every positive. The last feature is the semantic test
    itself (a fold on a key-like predicate covers a negative), for reference.
    """
    bg = p.background
    facts = collections.defaultdict(set)
    for r in bg.rules:
        name, args = _split_atom(r.head)
        if not r.body and len(args) == 1:
            facts[name].add(args[0])
    con = {_split_atom(c)[0] for c in bg.contraries.values()}
    asm = {_split_atom(a)[0] for a in bg.assumptions}
    excp = {_split_atom(b)[0] for r in bg.rules
            if _split_atom(r.head)[0] in con for b in r.body} - asm
    exc_c = set().union(*(facts[e] for e in excp)) if excp else set()
    pos = {_split_atom(e)[1][0] for e in p.positive}
    neg = {_split_atom(e)[1][0] for e in p.negative}
    keylike = [q for q, cs in facts.items() if q not in excp and pos <= cs]
    key_c = set().union(*(facts[q] for q in keylike)) if keylike else set()
    return {
        "exc facts exist": bool(exc_c),
        "exc on a negative": bool(exc_c & neg),
        "exc on an unlisted constant": bool(exc_c - pos - neg),
        "exc on a key-like constant": bool(exc_c & key_c),
        "more than one exc fact": sum(len(facts[e]) for e in excp) > 1,
        "more negatives than positives": len(neg) > len(pos),
        "(semantic) a negative has a key-like fact": bool(key_c & neg),
    }


def balanced_accuracy(rows: List[Tuple[Dict[str, bool], bool]],
                      feature: str) -> float:
    """Of `feature -> class` and its negation, the better; 0.5 is no signal."""
    tp = sum(1 for f, y in rows if f[feature] and y)
    fn = sum(1 for f, y in rows if not f[feature] and y)
    tn = sum(1 for f, y in rows if not f[feature] and not y)
    fp = sum(1 for f, y in rows if f[feature] and not y)
    b = (tp / max(tp + fn, 1) + tn / max(tn + fp, 1)) / 2
    return max(b, 1 - b)


# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CorpusConfig:
    base_seed: str = "corpus-v1"
    n_test: int = 20           # per tier and class
    n_val: int = 20
    n_train: int = 150
    n_heldout: int = 25        # per held-out tier and half
    max_attempts: int = 4      # per wanted problem, before the stream gives up


@dataclass
class Accepted:
    row: Dict                  # problems.jsonl
    record: Dict               # traces.jsonl
    example: Dict              # sft_example output
    problem: LearningProblem


def _anon_answers(meta: Dict, nm) -> Dict:
    return {name: {"new_rules": [rewrite_rule(r, nm).to_prolog() for r in rules],
                   "contraries": {rewrite_atom(a, nm): rewrite_atom(c, nm)
                                  for a, c in contr.items()}}
            for name, (rules, contr) in meta["answers"].items()}


def _attempt(tier: Dict, heldout: bool, variant: bool, seed: str, pid: str,
             cls: str, seen: Dict[str, str]) -> Tuple[Optional[Accepted], str]:
    """One attempt: the accepted problem, or None and the reject reason."""
    gen = generate_heldout_problem if heldout else generate_corpus_problem
    out = gen(tier, variant, seed)
    if out is None:
        return None, "generator_none"
    named, meta = out
    if heldout:
        reason = check_heldout(named, meta)
        if reason:
            return None, f"heldout:{reason}"
    problem, nm = anonymize_problem(named, scheme="letters")
    problem.problem_id = pid           # the generator's id carries real names
    sig = structural_signature(problem)
    if sig in seen:
        return None, f"duplicate_signature:{seen[sig]}"
    try:
        ex = sft_example(problem)
    except Untrainable as e:
        return None, f"untrainable:{e}"
    reason = check_example(ex, problem)
    if reason:
        return None, f"replay:{reason}"
    if heldout:
        cls = meta["half"]
        meta = {**{k: v for k, v in meta.items() if k != "answers"},
                "answers": _anon_answers(meta, nm)}
        got = sorted(r.to_prolog() for r in ex["solution"].new_rules)
        assert got == sorted(meta["answers"][meta["expected"]]["new_rules"])
    elif ("R3" in ex["trace"].symbol_sequence()) != variant:
        return None, "class_mismatch"
    row = {"problem_id": pid, "tier": tier["name"], "split": None,
           "class": cls, "seed": seed, "signature": sig,
           "problem": problem_to_dict(problem),
           "name_map": {"pred": nm.pred_map, "const": nm.const_map},
           "meta": meta}
    # Timing and rev would make a rebuild differ; the manifest has the rev.
    record = {k: v for k, v in ex["record"].to_dict().items()
              if k not in ("wall_s", "code_rev")}
    return Accepted(row, record, ex, problem), ""


def _stream(tier: Dict, heldout: bool, variant: bool, cfg: CorpusConfig,
            seen: Dict[str, str], rejects: List[Dict]) -> Iterator[Accepted]:
    """Accepted problems of one (tier, class) stream, in attempt order."""
    cls = (f"v{int(variant)}" if heldout
           else ("defeasible" if variant else "monotonic"))
    attempt = accepted = 0
    while True:
        if attempt > cfg.max_attempts * (accepted + 1):
            raise RuntimeError(f"{tier['name']}/{cls}: {attempt} attempts "
                               f"for {accepted} problems")
        seed = f"{cfg.base_seed}:{tier['name']}:{cls}:{attempt}"
        attempt += 1
        # Interleave the two streams of a tier so ids are stable under growth.
        pid = f"{tier['name']}_{2 * accepted + (0 if variant else 1):04d}"
        got, why = _attempt(tier, heldout, variant, seed, pid, cls, seen)
        if got is None:
            rejects.append({"tier": tier["name"], "class": cls,
                            "seed": seed, "reason": why})
            continue
        accepted += 1
        seen[got.row["signature"]] = pid
        yield got


# Solved, not posed: their prompts (98k and 207k chars) are far beyond the ~6k
# of every training prompt.
TABLE1_NOT_POSED = ("autism", "breast_w")


def _table1(problems: List[Tuple[str, LearningProblem]]) -> List[Accepted]:
    """Table 1, named and anonymised; the problems not posed, named only.

    A Table 1 problem is never dropped: a failed run or replay stops the build.
    """
    out = []
    for name, named in problems:
        posed = name not in TABLE1_NOT_POSED
        variants = [("named", named, None)]
        if posed:
            variants.append(("anon", *anonymize_problem(named, scheme="letters")))
        base = named.problem_id
        for cls, problem, nm in variants:
            problem.problem_id = f"{base}_{cls}"
            if posed:
                ex = sft_example(problem)
                reason = check_example(ex, problem)
                assert not reason, (problem.problem_id, reason)
                record = ex["record"]
            else:
                ex, (_, _, record) = None, solve_and_log(problem)
                assert record.success and record.intensional, problem.problem_id
            row = {"problem_id": problem.problem_id, "tier": "table1",
                   "split": "table1", "class": cls, "name": name,
                   "signature": structural_signature(problem),
                   "problem": problem_to_dict(problem),
                   "name_map": None if nm is None else {
                       "pred": nm.pred_map, "const": nm.const_map},
                   "meta": {"posed": posed, "r2_gap": r2_gap(problem)}}
            rec = {k: v for k, v in record.to_dict().items()
                   if k not in ("wall_s", "code_rev")}
            rec["split"] = "table1"
            out.append(Accepted(row, rec, ex, problem))
    return out


def build(cfg: CorpusConfig, out_dir: Path,
          table1_zip: Optional[Path] = None) -> Dict:
    """Generate, verify and write the corpus; return the manifest.

    `table1_zip` is the Zenodo release (src/aba_zenodo.py); without it the
    Table 1 set is left out.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    table1 = load_table1(table1_zip) if table1_zip else []
    # A generated problem isomorphic to a Table 1 problem is a duplicate.
    seen: Dict[str, str] = {structural_signature(p): p.problem_id
                            for _, p in table1}
    rejects: List[Dict] = []
    accepted: List[Accepted] = []

    streams: Dict = {}

    def take(tier, heldout, variant, n, split):
        key = (tier["name"], variant)
        if key not in streams:
            streams[key] = _stream(tier, heldout, variant, cfg, seen, rejects)
        for _ in range(n):
            a = next(streams[key])
            a.row["split"] = a.record["split"] = split
            accepted.append(a)

    for tier in HELDOUT_TIERS:
        for variant in (True, False):
            take(tier, True, variant, cfg.n_heldout, "heldout")
    for split, n in (("test", cfg.n_test), ("val", cfg.n_val),
                     ("train", cfg.n_train)):
        for tier in CORPUS_TIERS:
            for variant in (True, False):
                take(tier, False, variant, n, split)

    external = _table1(table1)
    _write(out_dir, accepted, rejects, external)
    manifest = _manifest(cfg, out_dir, accepted, rejects, external)
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out_dir / "MANIFEST.md").write_text(_manifest_md(manifest),
                                         encoding="utf-8")
    return manifest


def _jsonl(path: Path, rows: List[Dict]) -> None:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows),
                    encoding="utf-8")


def _prompt_row(a: Accepted) -> Dict:
    r = a.row
    return {"problem_id": r["problem_id"], "tier": r["tier"],
            "split": r["split"], "class": r["class"],
            "prompt_version": SFT_PROMPT_VERSION, "prompt": a.example["prompt"]}


def _eval_row(a: Accepted) -> Dict:
    ex = a.example
    return {**_prompt_row(a), "trace_target": ex["trace_target"],
            "endpoint_target": ex["endpoint_target"],
            "ceiling": gold_self_score(ex, a.problem)}


def _write(out_dir: Path, accepted: List[Accepted], rejects: List[Dict],
           external: List[Accepted]) -> None:
    sft_trace, sft_endpoint, evals = [], [], []
    for a in accepted:
        if a.row["split"] in ("train", "val"):
            sft_trace.append({**_prompt_row(a), "target": a.example["trace_target"]})
            sft_endpoint.append({**_prompt_row(a),
                                 "target": a.example["endpoint_target"]})
        else:
            evals.append(_eval_row(a))
    # Both arms share every prompt, and nothing evaluated is ever trained on.
    assert [x["prompt"] for x in sft_trace] == [x["prompt"] for x in sft_endpoint]
    assert not ({x["problem_id"] for x in sft_trace}
                & {x["problem_id"] for x in evals})
    _jsonl(out_dir / "problems.jsonl", [a.row for a in accepted])
    _jsonl(out_dir / "traces.jsonl", [a.record for a in accepted])
    _jsonl(out_dir / "sft_trace.jsonl", sft_trace)
    _jsonl(out_dir / "sft_endpoint.jsonl", sft_endpoint)
    _jsonl(out_dir / "eval.jsonl", evals)
    _jsonl(out_dir / "rejects.jsonl", rejects)
    if external:
        _jsonl(out_dir / "table1_problems.jsonl", [a.row for a in external])
        _jsonl(out_dir / "table1_traces.jsonl", [a.record for a in external])
        _jsonl(out_dir / "table1_eval.jsonl",
               [{**_eval_row(a), "name": a.row["name"]}
                for a in external if a.example])


# ─────────────────────────────────────────────────────────────────────────────
# Manifest
# ─────────────────────────────────────────────────────────────────────────────

ARM_MATCHING = {
    "primary": "same optimiser steps: both arms see the same train problems, "
               "in the same order, for the same number of epochs, with the "
               "same batch size and learning-rate schedule",
    "secondary": "same supervised target tokens: the endpoint arm is trained "
                 "for as many extra epochs as it takes to see the trace arm's "
                 "total target tokens; the ratio is fixed once, on the train "
                 "split, with the model's own tokenizer, before any run",
}

NOTES = [
    "Problems are posed whole (Definition 1): prompt and gold trace see all "
    "examples. No example-level split; evaluation uses separate problems.",
    "Fold alternatives are taken in background-rule order, dom(X) last. The "
    "paper leaves this order open (Definition 3); t8_decoy depends on it, "
    "t9_reuse's forbidden answer does not.",
    "t5_twopath here is tier spec v2 and is not comparable with set 05's "
    "t5_twopath, whose 20 problems are one structure in 20 surface forms.",
    "Held-out and test problems never appear in sft_*.jsonl.",
    "Table 1 (Zenodo release, src/aba_zenodo.py) is read as the released tool "
    "reads it; T and dom follow that tool and lines 211-212; integer constants "
    "are renamed n<k>. It is posed named and anonymised; autism and breast_w "
    "are solved but not posed (prompts of 98k and 207k chars).",
    "The reference's R2 folds with unary background facts and dom only; the "
    "paper's R2 folds with any rule of R, of any arity (lines 326-329). "
    "`r2_gap` counts the background rules this leaves out. Gold traces are "
    "the reference's.",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table1_manifest(external: List[Accepted]) -> Dict:
    sizes = {name: (bk, pos, neg) for name, _, bk, pos, neg in TABLE1}
    symbols = {a.row["problem_id"]: a.record["symbolic_trace"]["symbols"]
               for a in external}
    problems = {}
    for a in external:
        if a.row["class"] != "named":
            continue
        name, st = a.row["name"], a.record["symbolic_trace"]
        anon = symbols.get(a.row["problem_id"].replace("_named", "_anon"))
        problems[name] = {
            "problem_id": a.row["problem_id"],
            "bk_e+_e-": sizes[name],
            "posed": a.row["meta"]["posed"],
            "symbols": dict(collections.Counter(st["symbols"])),
            "new_rules": len(st["final_new_rules"]),
            "new_assumptions": len(st["final_assumptions"])
                               - len(a.problem.background.assumptions),
            "anon_same_steps": None if anon is None else anon == st["symbols"],
            "r2_gap": len(a.row["meta"]["r2_gap"]),
        }
    return {"source": {"doi": ZENODO_DOI, "md5": ZENODO_MD5,
                       "release": RELEASE},
            "not_posed": list(TABLE1_NOT_POSED), "problems": problems}


def _manifest(cfg: CorpusConfig, out_dir: Path, accepted: List[Accepted],
              rejects: List[Dict], external: List[Accepted]) -> Dict:
    from src.aba_tracelog import _git_rev

    counts = collections.defaultdict(collections.Counter)
    symbols = collections.defaultdict(collections.Counter)
    reuse = collections.Counter()
    line39 = collections.Counter()
    defeasible = with_r3 = 0
    chars = collections.defaultdict(list)
    cue_rows = collections.defaultdict(list)
    for a in accepted:
        r, rec = a.row, a.example["record"]
        tier, split = r["tier"], r["split"]
        counts[tier][f"{split}/{r['class']}"] += 1
        symbols[tier].update(a.example["trace"].symbol_sequence())
        reuse[tier] += any(x.mode == "reuse" and x.accepted
                           for e in rec.path for x in e.asm_attempts)
        line39[tier] += any(c.reuse_scan and c.asm_ok is False
                            for e in rec.path for c in e.candidates)
        if r["class"] == "defeasible":
            defeasible += 1
            with_r3 += "R3" in a.example["trace"].symbol_sequence()
        if split == "train":
            chars["trace"].append(len(a.example["trace_target"]))
            chars["endpoint"].append(len(a.example["endpoint_target"]))
        if split in ("train", "val", "test"):
            cue_rows[split].append((cue_features(a.problem),
                                    r["class"] == "defeasible"))

    per_tier = {t: sum(c.values()) for t, c in counts.items()}
    reject_reasons = collections.Counter(
        (x["tier"], x["reason"].split(":")[0]) for x in rejects)
    attempts = collections.Counter(x["tier"] for x in rejects)
    for t, n in per_tier.items():
        attempts[t] += n
    dup_rate = {t: sum(v for (tt, why), v in reject_reasons.items()
                       if tt == t and why == "duplicate_signature") / attempts[t]
                for t in per_tier}
    features = list(cue_features(accepted[0].problem))
    cues = {split: {f: round(balanced_accuracy(rows, f), 3) for f in features}
            for split, rows in cue_rows.items()}
    mean = lambda xs: sum(xs) / max(len(xs), 1)
    ratio = mean(chars["trace"]) / max(mean(chars["endpoint"]), 1)

    gates = {
        "every tier and split exactly 50/50 by class": all(
            c[f"{s}/defeasible"] == c[f"{s}/monotonic"]
            for t, c in counts.items() if t.startswith(tuple(
                x["name"] for x in CORPUS_TIERS))
            for s in ("train", "val", "test")),
        "R3 in every defeasible problem (coverage)": with_r3 == defeasible,
        # Train only: val/test are small enough for noise to cross 0.55.
        "exception-fact cues <= 0.55 on train": all(
            v <= 0.55 for f, v in cues.get("train", {}).items()
            if f.startswith("exc")),
        "t4_nested reuse in >= 20% of problems": (
            reuse["t4_nested"] >= 0.2 * per_tier.get("t4_nested", 0)),
        # Duplicates are rejected, so this is the hard gate; `duplicate_rate`
        # (the generator's own diversity) is reported, not gated.
        "no signature shared across problems": (
            len({a.row["signature"] for a in accepted}) == len(accepted)),
    }
    if external:
        gates["no generated problem shares a Table 1 signature"] = not (
            {a.row["signature"] for a in accepted}
            & {a.row["signature"] for a in external})

    files = ["problems.jsonl", "traces.jsonl", "sft_trace.jsonl",
             "sft_endpoint.jsonl", "eval.jsonl", "rejects.jsonl"]
    if external:
        files += ["table1_problems.jsonl", "table1_traces.jsonl",
                  "table1_eval.jsonl"]
    import clingo
    import platform
    return {
        "corpus_version": out_dir.name,
        "code_rev": _git_rev(),
        "clingo": clingo.__version__,
        "python": platform.python_version(),
        "config": vars(cfg),
        "tier_spec_version": CORPUS_TIER_SPEC_VERSION,
        "training_tiers": [t["name"] for t in CORPUS_TIERS],
        "heldout_tiers": [t["name"] for t in HELDOUT_TIERS],
        "prompt_version": SFT_PROMPT_VERSION,
        "counts": {t: dict(c) for t, c in sorted(counts.items())},
        "rejects": {f"{t}/{why}": n for (t, why), n
                    in sorted(reject_reasons.items())},
        "duplicate_rate": {t: round(v, 4) for t, v in sorted(dup_rate.items())},
        "symbols": {t: dict(c) for t, c in sorted(symbols.items())},
        "reuse_problems": dict(reuse),
        "line39_problems": dict(line39),
        "cue_balanced_accuracy": cues,
        "target_chars_train": {"trace_mean": round(mean(chars["trace"]), 1),
                               "endpoint_mean": round(mean(chars["endpoint"]), 1),
                               "ratio": round(ratio, 2)},
        "arm_matching": ARM_MATCHING,
        "table1": _table1_manifest(external) if external else None,
        "gates": gates,
        "notes": NOTES,
        "sha256": {f: _sha256(out_dir / f) for f in files},
    }


def _manifest_md(m: Dict) -> str:
    L = [f"# Corpus {m['corpus_version']}", "",
         f"- code rev: `{m['code_rev']}`; clingo {m['clingo']}; "
         f"python {m['python']}",
         f"- tier spec: v{m['tier_spec_version']}; prompt: {m['prompt_version']}",
         f"- config: `{json.dumps(m['config'])}`", "", "## Gates", ""]
    L += [f"- [{'x' if ok else ' '}] {g}" for g, ok in m["gates"].items()]
    L += ["", "## Counts", "", "| tier | split/class | n |", "|---|---|---|"]
    for t, c in m["counts"].items():
        L += [f"| {t} | {k} | {v} |" for k, v in sorted(c.items())]
    L += ["", "## Step symbols (all splits)", "",
          "| tier | R1 | R2 | R3 | R4 | problems with reuse | with line 39 |",
          "|---|---|---|---|---|---|---|"]
    for t, s in m["symbols"].items():
        L.append(f"| {t} | {s.get('R1', 0)} | {s.get('R2', 0)} | "
                 f"{s.get('R3', 0)} | {s.get('R4', 0)} | "
                 f"{m['reuse_problems'].get(t, 0)} | "
                 f"{m['line39_problems'].get(t, 0)} |")
    L += ["", "## Cues (balanced accuracy predicting R3; 0.50 = no signal)", ""]
    splits = list(m["cue_balanced_accuracy"])
    L += ["| feature | " + " | ".join(splits) + " |",
          "|---|" + "---|" * len(splits)]
    for f in next(iter(m["cue_balanced_accuracy"].values())):
        L.append(f"| {f} | " + " | ".join(
            f"{m['cue_balanced_accuracy'][s][f]:.3f}" for s in splits) + " |")
    tc = m["target_chars_train"]
    L += ["", "## Arm matching (pre-registered)", "",
          f"Train-split target length: trace {tc['trace_mean']} chars, "
          f"endpoint {tc['endpoint_mean']} chars (ratio {tc['ratio']}).", "",
          f"- **Primary:** {m['arm_matching']['primary']}.",
          f"- **Secondary:** {m['arm_matching']['secondary']}.", "",
          "## Rejects", ""]
    L += [f"- {k}: {v}" for k, v in m["rejects"].items()] or ["- none"]
    L += ["", "Generator duplicate rate (rejected duplicates / attempts): "
          + ", ".join(f"{t} {v:.1%}" for t, v in m["duplicate_rate"].items())
          + "."]
    if m.get("table1"):
        t1 = m["table1"]
        L += ["", "## Table 1 (external held-out, never trained on)", "",
              f"Zenodo doi {t1['source']['doi']}, release "
              f"`{t1['source']['release']}`, md5 `{t1['source']['md5']}`. "
              "Posed problems have a named and an anonymised prompt.", "",
              "| problem | BK / E+ / E− | posed | R1 | R2 | R3 | R4 | new rules "
              "| new assumptions | anon same steps | R2 gap |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, x in t1["problems"].items():
            s = x["symbols"]
            L.append(f"| {name} | {' / '.join(map(str, x['bk_e+_e-']))} | "
                     f"{'yes' if x['posed'] else 'no'} | {s.get('R1', 0)} | "
                     f"{s.get('R2', 0)} | {s.get('R3', 0)} | {s.get('R4', 0)} | "
                     f"{x['new_rules']} | {x['new_assumptions']} | "
                     f"{'—' if x['anon_same_steps'] is None else x['anon_same_steps']} | "
                     f"{x['r2_gap']} |")
    L += ["", "## Notes", ""] + [f"- {n}" for n in m["notes"]]
    L += ["", "## Files (sha256)", ""]
    L += [f"- `{f}` {h}" for f, h in m["sha256"].items()]
    return "\n".join(L) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Name-permuted evaluation set
# ─────────────────────────────────────────────────────────────────────────────

PERMUTED_SPLITS = ("test", "heldout")
_PRED_CALL = re.compile(r"\b([a-z]\w*)\(")

PERMUTED_NOTES = [
    "The source's test and held-out problems, each re-posed with its predicate "
    "symbols renamed by a derangement of themselves; Table 1 is not included. "
    "Never trained on: there are no sft_*.jsonl.",
    "Constants, and the order of rules, assumptions, contraries, examples, "
    "learnable predicates and domain, are the source's; dom is never renamed. "
    "The inverse permutation gives the source problem back (asserted).",
    "problem_id, tier, split and class are the source's: each row pairs with "
    "the source eval row of the same id.",
    "The gold is the reference's run on the permuted problem. "
    "gold_equal_renamed counts the golds equal to the source gold with its "
    "predicates renamed (alpha_k / c_alpha_k are minted by the algorithm and "
    "keep their names); a problem absent from gold_differences is equal on both "
    "targets.",
    "permutation maps the source's predicate names to this problem's; "
    "name_map is the source name_map composed with it.",
    "Held-out meta.answers are the source's, renamed; expected, forbidden and "
    "half are unchanged.",
    "TOKENS.json (python train_sft.py --audit --corpus <this corpus>) has no "
    "arm matching and inherits the source's max_new_tokens, so both sets are "
    "generated under one budget.",
]


def derangement(names: List[str], seed: str) -> Dict[str, str]:
    """A uniformly random permutation of `names` with no fixed point, by rejection."""
    assert len(set(names)) == len(names) > 1, names
    rng = random.Random(seed)
    while True:
        new = list(names)
        rng.shuffle(new)
        if all(a != b for a, b in zip(names, new)):
            return dict(zip(names, new))


def rename_preds(text: str, perm: Dict[str, str]) -> str:
    """`text` with every predicate symbol in `perm` renamed, all at once."""
    return _PRED_CALL.sub(lambda m: perm.get(m.group(1), m.group(1)) + "(", text)


def _gold_diff(want: str, got: str) -> Optional[Dict]:
    """The first line where `got` departs from `want`; None if they are equal."""
    if want == got:
        return None
    a, b = want.split("\n"), got.split("\n")
    k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y),
             min(len(a), len(b)))
    return {"line": k + 1, "renamed_source": a[k] if k < len(a) else None,
            "permuted": b[k] if k < len(b) else None}


def build_permuted(source: Path, out_dir: Path) -> Dict:
    """Re-pose `source`'s test and held-out problems under predicate-name
    derangements, verify and write them; return the manifest.

    One derangement per problem, seeded on its id, of its predicate symbols in
    `collect_symbols` order. A failed replay or a held-out answer that is not
    the reference's stops the build.
    """
    import clingo
    import platform
    from src.aba_tracelog import _git_rev

    assert out_dir.resolve() != source.resolve(), "would overwrite the source"
    src_m = json.loads((source / "MANIFEST.json").read_text(encoding="utf-8"))
    read = ("problems.jsonl", "eval.jsonl")
    src_sha = {f: _sha256(source / f) for f in read}
    assert src_sha == {f: src_m["sha256"][f] for f in read}, \
        f"{source} differs from its MANIFEST.json"
    load = lambda f: [json.loads(x) for x in
                      (source / f).read_text(encoding="utf-8").splitlines()]
    rows = {r["problem_id"]: r for r in load("problems.jsonl")}
    evals = [e for e in load("eval.jsonl") if e["split"] in PERMUTED_SPLITS]
    seed = f"{src_m['config']['base_seed']}-permuted"
    targets = ("endpoint_target", "trace_target")

    pairs: List[Tuple[Dict, Accepted]] = []        # (source eval row, permuted)
    replay: Dict[str, Optional[str]] = {}
    expected: Dict[str, bool] = {}
    diffs: Dict[str, Dict] = {}
    for ev in evals:
        src = rows[ev["problem_id"]]
        pid = src["problem_id"]
        perm = derangement(collect_symbols(problem_from_dict(src["problem"]))[0],
                           f"{seed}:{pid}")
        nm = NameMap(pred_map=perm, const_map={})
        problem, _ = anonymize_problem(problem_from_dict(src["problem"]), name_map=nm)
        problem.problem_id = pid
        back = problem_to_dict(anonymize_problem(problem, name_map=nm.inverse())[0])
        assert {**back, "problem_id": pid} == src["problem"], f"{pid}: not a renaming"
        ex = sft_example(problem)
        replay[pid] = check_example(ex, problem)
        assert replay[pid] is None, (pid, replay[pid])
        meta = src["meta"]
        if src["split"] == "heldout":
            answers = {k: ([_parse_rule_line(r) for r in v["new_rules"]], v["contraries"])
                       for k, v in meta["answers"].items()}
            meta = {**meta, "answers": _anon_answers({"answers": answers}, nm)}
            got = sorted(r.to_prolog() for r in ex["solution"].new_rules)
            expected[pid] = got == sorted(meta["answers"][meta["expected"]]["new_rules"])
            assert expected[pid], (pid, got)
        row = {**src, "signature": structural_signature(problem),
               "problem": problem_to_dict(problem),
               "name_map": {"pred": {k: perm[v] for k, v in src["name_map"]["pred"].items()},
                            "const": src["name_map"]["const"]},
               "meta": meta, "permutation": perm, "source": source.as_posix()}
        pairs.append((ev, Accepted(row, {}, ex, problem)))   # no traces.jsonl
        d = {t: _gold_diff(rename_preds(ev[t], perm), ex[t]) for t in targets}
        if any(d.values()):
            diffs[pid] = {t: v for t, v in d.items() if v}

    out_dir.mkdir(parents=True, exist_ok=True)
    evals_out = [_eval_row(a) for _, a in pairs]
    _jsonl(out_dir / "problems.jsonl", [a.row for _, a in pairs])
    _jsonl(out_dir / "eval.jsonl", evals_out)

    counts = collections.defaultdict(collections.Counter)
    for _, a in pairs:
        counts[a.row["tier"]][f"{a.row['split']}/{a.row['class']}"] += 1
    gates = {
        "every permutation is a derangement and a bijection": all(
            sorted(p) == sorted(p.values())
            == sorted(collect_symbols(problem_from_dict(rows[pid]["problem"]))[0])
            and all(k != v for k, v in p.items())
            for pid, p in ((a.row["problem_id"], a.row["permutation"])
                           for _, a in pairs)),
        "check_example passes on every problem": (
            len(replay) == len(pairs) and not any(replay.values())),
        "held-out expected answer is the reference's": (
            len(expected) == sum(a.row["split"] == "heldout" for _, a in pairs)
            and all(expected.values())),
        "prompts differ from the source prompts on every row": all(
            e["prompt"] != ev["prompt"] for (ev, _), e in zip(pairs, evals_out)),
        "no signature changes": all(
            a.row["signature"] == rows[a.row["problem_id"]]["signature"]
            for _, a in pairs),
    }
    same = {t: len(pairs) - sum(t in d for d in diffs.values()) for t in targets}
    files = ("problems.jsonl", "eval.jsonl")
    manifest = {
        "corpus_version": out_dir.name,
        "code_rev": _git_rev(),
        "clingo": clingo.__version__,
        "python": platform.python_version(),
        "prompt_version": SFT_PROMPT_VERSION,
        "source": {"corpus": source.as_posix(),
                   "corpus_version": src_m["corpus_version"],
                   "code_rev": src_m["code_rev"], "sha256": src_sha},
        "splits": list(PERMUTED_SPLITS),
        "seed_scheme": f"random.Random(f'{seed}:{{problem_id}}'); a copy of the "
                       "problem's predicate symbols (collect_symbols order) is "
                       "shuffled until no symbol maps to itself",
        "counts": {t: dict(c) for t, c in sorted(counts.items())},
        "gold_equal_renamed": {**same, "both": len(pairs) - len(diffs),
                               "n": len(pairs)},
        "gold_differences": diffs,
        "gates": gates,
        "notes": PERMUTED_NOTES,
        "sha256": {f: _sha256(out_dir / f) for f in files},
    }
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out_dir / "MANIFEST.md").write_text(_permuted_manifest_md(manifest),
                                         encoding="utf-8")
    return manifest


def _permuted_manifest_md(m: Dict) -> str:
    s = m["source"]
    L = [f"# Corpus {m['corpus_version']}", "",
         f"- code rev: `{m['code_rev']}`; clingo {m['clingo']}; "
         f"python {m['python']}",
         f"- prompt: {m['prompt_version']}; splits: {', '.join(m['splits'])}",
         f"- source: `{s['corpus']}` (corpus {s['corpus_version']}, code rev "
         f"`{s['code_rev']}`); "
         + "; ".join(f"`{f}` {h}" for f, h in s["sha256"].items()),
         f"- seed: {m['seed_scheme']}", "", "## Gates", ""]
    L += [f"- [{'x' if ok else ' '}] {g}" for g, ok in m["gates"].items()]
    L += ["", "## Counts", "", "| tier | split/class | n |", "|---|---|---|"]
    for t, c in m["counts"].items():
        L += [f"| {t} | {k} | {v} |" for k, v in sorted(c.items())]
    g = m["gold_equal_renamed"]
    L += ["", "## Gold vs the source gold renamed (reported, not gated)", "",
          f"Equal: endpoint {g['endpoint_target']}/{g['n']}, trace "
          f"{g['trace_target']}/{g['n']}, both {g['both']}/{g['n']}."]
    for pid, d in m["gold_differences"].items():
        L += [f"- {pid} {t} line {x['line']}: `{x['renamed_source']}` -> "
              f"`{x['permuted']}`" for t, x in d.items()]
    L += ["", "## Notes", ""] + [f"- {n}" for n in m["notes"]]
    L += ["", "## Files (sha256)", ""]
    L += [f"- `{f}` {h}" for f, h in m["sha256"].items()]
    return "\n".join(L) + "\n"
