"""The paper's Table 1 benchmarks, read from their Zenodo archive.

The ten learning problems of Table 1 (PDF lines 750-760) are archived with the
released tool as doi 10.5281/zenodo.13330013. The archive is GPL-3.0-or-later,
so it is not copied into this repository: `fetch_archive` downloads the zip and
checks its md5. `load_table1` reads the specifications as the released tool
(tag ASP-ABAlearn_B, commit 24f26e7) reads them:

  * rules and facts keep their published form, spaced as this code writes
    atoms (`V = c`, `p(a, b)`);
  * `contrary(A, C) :- ...` contributes its head only (bk_term), with C's
    variables renamed to those of the declared assumption;
  * an assumption in no rule body is dropped with its contrary
    (rem_useless_asms_cnts);
  * T is pred(E+ and E-) plus the contraries of the remaining assumptions.
    Definition 1 leaves T to the input; asp_star and footnote 3 fix it;
  * dom holds every constant of the language, examples included (lines
    211-212), so acute's negatives without attribute facts are in it. It is
    kept in order of first appearance in the published files: RoLe emits its
    facts in dom order, and Gen takes them in that order (line 14 leaves it
    open). The released tool takes the positives in E+ order, which dom order
    matches on every file but nixon_diamond_2, where RoLe learns one positive.

Integer constants (the row ids of acute, autism and breast-w) become `n<k>`,
because the reference reads a constant as a lowercase identifier. The renaming
is a bijection, so solutions are unchanged up to it.
"""
from __future__ import annotations

import hashlib
import re
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

from src.aba_algorithm import _EQ_RE, _FACT_RE, _HEAD_RE
from src.aba_types import ABAFramework, LearningProblem, Rule

ZENODO_DOI = "10.5281/zenodo.13330013"
ZENODO_URL = ("https://zenodo.org/records/13330013/files/"
              "ABALearn/aba_asp-ASP-ABAlearn_B.zip?download=1")
ZENODO_MD5 = "32c39f6f437d334206d748412b55df74"
RELEASE = "ASP-ABAlearn_B"               # git tag of ABALearn/aba_asp
_ROOT = "ABALearn-aba_asp-24f26e7/ecai2024/ASP-ABAlearn_B/"

# Table 1 (PDF lines 750-760): name, archive stem, |BK|, |E+|, |E-|.
TABLE1: List[Tuple[str, str, int, int, int]] = [
    ("flies", "01_flies_birds", 8, 4, 2),
    ("flies_birds_planes", "02_flies_birds_planes", 10, 5, 2),
    ("innocent", "03_innocent", 15, 2, 2),
    ("nixon_diamond", "04_nixon_diamond", 6, 1, 1),
    ("nixon_diamond_2", "05_nixon_diamond_2", 15, 3, 2),
    ("tax_law", "06_tax_law", 16, 2, 2),
    ("tax_law_2", "07_tax_law_2", 17, 2, 2),
    ("acute", "08_acute.pp.csv", 96, 21, 19),
    ("autism", "09_autism.pp.csv", 5716, 189, 515),
    ("breast_w", "10_breastw.pp.csv", 6291, 241, 458),
]


def fetch_archive(path: Path) -> Path:
    """The release zip at `path`, downloaded first if absent; md5-checked."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(".part")
        with urllib.request.urlopen(ZENODO_URL, timeout=600) as r:
            part.write_bytes(r.read())
        part.replace(path)
    md5 = hashlib.md5(path.read_bytes()).hexdigest()
    if md5 != ZENODO_MD5:
        raise ValueError(f"{path}: md5 {md5}, expected {ZENODO_MD5} "
                         f"(doi {ZENODO_DOI})")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────────────────────

_CLAUSE_END = re.compile(r"\.(?=\s|$)")
_EQ = re.compile(r"^([A-Z_]\w*)\s*=\s*(\w+)$")
_ATOM = re.compile(r"^([a-z]\w*)(?:\((.*)\))?$")
_VAR = re.compile(r"\b[A-Z_]\w*\b")
_GOAL = re.compile(r"aba_asp\(\s*'[^']*'\s*,\s*\[(.*?)\]\s*,\s*\[(.*?)\]\s*\)",
                   re.S)


def _split_top(s: str) -> List[str]:
    """Split on commas outside brackets."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(s):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(s[start:i].strip())
            start = i + 1
    parts.append(s[start:].strip())
    return [p for p in parts if p]


def _const(t: str) -> str:
    return f"n{t}" if t.isdigit() else t


def _atom(s: str) -> str:
    s = s.strip()
    m = _EQ.match(s)
    if m:
        return f"{m.group(1)} = {_const(m.group(2))}"
    m = _ATOM.match(s)
    if not m:
        raise ValueError(f"unsupported literal: {s!r}")
    if m.group(2) is None:
        return m.group(1)
    return f"{m.group(1)}({', '.join(_const(a) for a in _split_top(m.group(2)))})"


def _pred(atom: str) -> str:
    return atom.split("(", 1)[0]


def _args(atom: str) -> List[str]:
    return _split_top(atom[atom.index("(") + 1:-1]) if "(" in atom else []


def parse_benchmark(aba: str, goal: str, problem_id: str) -> LearningProblem:
    """One ASP-ABAlearn_B specification (.bk.aba) with its goal (.bk.goal)."""
    rules: List[Rule] = []
    declared: List[str] = []
    raw_contraries: List[Tuple[str, str]] = []
    for clause in _CLAUSE_END.split(re.sub(r"%.*", "", aba)):
        if not clause.strip():
            continue
        head, _, body = clause.strip().partition(":-")
        head = head.strip()
        if head.startswith("assumption("):
            declared.append(_atom(head[len("assumption("):-1]))
        elif head.startswith("contrary("):       # head only, as bk_term
            asm, con = _split_top(head[len("contrary("):-1])
            raw_contraries.append((_atom(asm), _atom(con)))
        else:
            rules.append(Rule(_atom(head), [_atom(b) for b in _split_top(body)]))

    contrary_of: Dict[str, str] = {}
    for asm, con in raw_contraries:
        decl = next(a for a in declared if _pred(a) == _pred(asm))
        ren = dict(zip(_args(asm), _args(decl)))
        contrary_of[decl] = _VAR.sub(lambda m: ren.get(m.group(), m.group()), con)

    in_bodies = {b for r in rules for b in r.body}
    assumptions = [a for a in declared if a in in_bodies]
    # The tool keeps an assumption by unification; string equality must agree.
    assert not ({_pred(a) for a in declared if a not in in_bodies}
                & {_pred(b) for b in in_bodies}), problem_id
    contraries = {a: contrary_of[a] for a in assumptions}

    m = _GOAL.search(goal)
    positive = [_atom(e) for e in _split_top(m.group(1))]
    negative = [_atom(e) for e in _split_top(m.group(2))]
    # Definition 1: E+ and E- disjoint, examples are not assumptions.
    assert not set(positive) & set(negative), problem_id
    assert not ({_pred(e) for e in positive + negative}
                & {_pred(a) for a in assumptions}), problem_id

    learnable = list(dict.fromkeys([_pred(e) for e in positive + negative]
                                   + [_pred(c) for c in contraries.values()]))
    # In published order: dom's order is RoLe's fact order (line 14).
    domain = list(dict.fromkeys(
        [c for r in rules for c in r.get_constants()]
        + [c for e in positive + negative for c in Rule(e).get_constants()]))
    return LearningProblem(
        background=ABAFramework(rules=rules, assumptions=assumptions,
                                contraries=contraries),
        positive=positive, negative=negative, learnable=learnable,
        domain=domain, problem_id=problem_id)


def load_table1(zip_path: Path) -> List[Tuple[str, LearningProblem]]:
    """The ten Table 1 problems in the paper's order, sizes checked against it."""
    z = zipfile.ZipFile(fetch_archive(zip_path))
    out = []
    for i, (name, stem, n_bk, n_pos, n_neg) in enumerate(TABLE1, 1):
        aba = z.read(f"{_ROOT}{stem}.bk.aba").decode("utf-8")
        goal = z.read(f"{_ROOT}{stem}.bk.goal").decode("utf-8")
        p = parse_benchmark(aba, goal, f"table1_{i:02d}")
        assert (len(p.background.rules), len(p.positive), len(p.negative)) \
            == (n_bk, n_pos, n_neg), name
        out.append((name, p))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Scope of the reference's Folding
# ─────────────────────────────────────────────────────────────────────────────

def _reference_folds_with(rule: Rule) -> bool:
    """Whether `_candidate_folds_traced` can use `rule` as the paper's rho2."""
    head = _HEAD_RE.match(rule.head.strip())
    if head:                                   # Case A: p(V) :- ..., V = c, ...
        return any((m := _EQ_RE.match(b.strip())) and m.group(1) == head.group(2)
                   for b in rule.body)
    return bool(_FACT_RE.match(rule.head.strip())) and not rule.body   # Case B


def r2_gap(problem: LearningProblem) -> List[str]:
    """Background rules R2 may fold with (lines 326-329) but the reference never does.

    The reference folds with unary background facts and dom only; the paper's
    R2 takes any rule of R, of any arity, learnt rules included. The last part
    applies to every problem and is not listed here.
    """
    return [r.to_prolog() for r in problem.background.rules
            if not _reference_folds_with(r)]
