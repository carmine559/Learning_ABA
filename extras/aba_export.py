"""
aba_export.py
Persist the actual learned ABA frameworks — symbolic ground truth AND every
LLM-generated candidate — so they can be inspected directly.

This is the evidentiary layer: rather than trusting aggregate gen@k numbers,
anyone can open the exported files and read the literal rules the LLM wrote,
see whether each rule is defeasible (uses an assumption) or monotonic, and
compare it side by side with the symbolic reference.

Three outputs per run:
  * frameworks.jsonl  — one machine-readable record per framework (re-loadable)
  * frameworks.md     — a human-readable catalogue for reading / appendices
  * defeasibility.csv — a flat table: per (problem, source, sample) whether the
                        solution is defeasible, intensional, degenerate, valid
"""
from __future__ import annotations
import json
import re
import os
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any

from src.aba_types import Rule, ABAFramework, LearningProblem


# ──────────────────────────────────────────────────────────────────────────────
# Structural classification of a framework
# ──────────────────────────────────────────────────────────────────────────────

def _pred(atom: str) -> str:
    m = re.match(r'^([a-z]\w*)', atom.strip())
    return m.group(1) if m else atom.strip()


def rule_uses_assumption(rule: Rule, assumptions: List[str]) -> bool:
    asm_preds = {_pred(a) for a in assumptions}
    return any(_pred(b) in asm_preds for b in rule.body)


def classify_framework(fw: ABAFramework) -> Dict[str, Any]:
    """
    Structural summary of the *new* part of a framework — the proof that we are
    learning real defeasible rules, not monotonic shortcuts.
    """
    all_asms = list(fw.assumptions)
    new_rules = fw.new_rules if fw.new_rules else fw.rules

    defeasible_rules = [r for r in new_rules
                        if rule_uses_assumption(r, all_asms)]
    contrary_preds = {_pred(c) for c in fw.contraries.values()}
    contrary_rules = [r for r in new_rules
                      if _pred(r.head) in contrary_preds]
    ground_facts = [r for r in new_rules if r.is_ground()]

    return {
        "n_new_rules":        len(new_rules),
        "n_new_assumptions":  len(fw.new_assumptions),
        "is_defeasible":      len(defeasible_rules) > 0,
        "n_defeasible_rules": len(defeasible_rules),
        "n_contrary_rules":   len(contrary_rules),
        "n_ground_facts":     len(ground_facts),
        "is_intensional":     all(not r.is_ground() for r in new_rules) if new_rules else False,
        "is_monotonic":       len(defeasible_rules) == 0 and len(new_rules) > 0,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Serialisable record
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FrameworkRecord:
    problem_id:   str
    source:       str          # "symbolic" | model name (e.g. "llama-3.3-70b")
    mode:         str          # "" for symbolic, else direct/cot/guided/...
    sample_idx:   int          # -1 for symbolic
    new_rules:    List[str]    # prolog strings
    new_assumptions: List[str]
    contraries:   Dict[str, str]
    structure:    Dict[str, Any]
    valid:        Optional[bool] = None
    generalises:  Optional[bool] = None

    # Explainability extensions (populated by enrich_record / from_framework)
    natural_language_rules: List[str] = field(default_factory=list)
    mechanism_tags: Dict[str, str]    = field(default_factory=dict)
    narrative:      Optional[str]     = None
    graded_scores:  Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_framework(
        fw: ABAFramework,
        problem_id: str,
        source: str,
        mode: str = "",
        sample_idx: int = -1,
        valid: Optional[bool] = None,
        generalises: Optional[bool] = None,
    ) -> "FrameworkRecord":
        new_rules = fw.new_rules if fw.new_rules else fw.rules
        nlr: List[str] = []
        for r in new_rules:
            try:
                nlr.append(r.to_text())
            except Exception:
                pass
        return FrameworkRecord(
            problem_id=problem_id,
            source=source,
            mode=mode,
            sample_idx=sample_idx,
            new_rules=[r.to_prolog() for r in new_rules],
            new_assumptions=list(fw.new_assumptions),
            contraries=dict(fw.contraries),
            structure=classify_framework(fw),
            valid=valid,
            generalises=generalises,
            natural_language_rules=nlr,
        )


def record_to_framework(rec: Dict) -> ABAFramework:
    """Re-load a saved record back into an ABAFramework (rules only)."""
    rules = [_parse_prolog_rule(s) for s in rec["new_rules"]]
    rules = [r for r in rules if r is not None]
    fw = ABAFramework(
        rules=rules,
        assumptions=list(rec.get("new_assumptions", [])),
        contraries=dict(rec.get("contraries", {})),
        new_rules=rules,
        new_assumptions=list(rec.get("new_assumptions", [])),
    )
    return fw


def enrich_record(
    record: FrameworkRecord,
    background: ABAFramework,
    *,
    narrative: Optional[str] = None,
    graded_scores: Optional[Dict[str, Any]] = None,
) -> FrameworkRecord:
    """
    In-place enrich a FrameworkRecord with mechanism tags, narrative, and graded scores.
    Call this after from_framework(), passing the problem's background framework so
    that classify_rule_mechanism() can identify which body atoms are assumptions.

    narrative:     build_narrative() output from aba_explain
    graded_scores: {query -> {strength, crisp, agree, explanation}} from aba_graded
    """
    from extras.aba_explain import classify_rule_mechanism  # lazy: avoids circular imports
    rules_obj = [_parse_prolog_rule(s) for s in record.new_rules]
    for r in rules_obj:
        if r is not None:
            try:
                tag = classify_rule_mechanism(r, background)
                record.mechanism_tags[r.to_prolog()] = tag
            except Exception:
                pass
    if narrative is not None:
        record.narrative = narrative
    if graded_scores is not None:
        record.graded_scores = graded_scores
    return record


def _parse_prolog_rule(s: str) -> Optional[Rule]:
    s = s.strip().rstrip(".")
    if not s:
        return None
    if ":-" in s:
        head, body = s.split(":-", 1)
        body_atoms = [b.strip() for b in re.split(r',(?![^()]*\))', body) if b.strip()]
        return Rule(head=head.strip(), body=body_atoms)
    return Rule(head=s, body=[])


# ──────────────────────────────────────────────────────────────────────────────
# Markdown catalogue (human-readable)
# ──────────────────────────────────────────────────────────────────────────────

def _framework_md(rec: FrameworkRecord) -> str:
    st = rec.structure
    kind = ("DEFEASIBLE" if st["is_defeasible"]
            else ("MONOTONIC" if st["is_monotonic"] else "empty"))
    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    head = f"**{rec.source}**"
    if rec.mode:
        head += f" / {rec.mode}"
    if rec.sample_idx >= 0:
        head += f" / sample {rec.sample_idx}"
    flags = []
    if rec.valid is not None:
        flags.append("valid" if rec.valid else "invalid")
    if rec.generalises is not None:
        flags.append("generalises" if rec.generalises else "overfits")
    flag_str = f"  ({', '.join(flags)})" if flags else ""
    lines.append(f"{head} — `{kind}`{flag_str}")

    # ── Prolog rules (with inline mechanism tags) ────────────────────────────
    if rec.new_rules:
        lines.append("```prolog")
        for r in rec.new_rules:
            mech = rec.mechanism_tags.get(r, "")
            comment = f"  % [{mech}]" if mech else ""
            lines.append(f"{r}{comment}")
        for a in rec.new_assumptions:
            c = rec.contraries.get(a, f"c_{a}")
            lines.append(f"% assumption: {a} defeated_by {c}")
        lines.append("```")
    else:
        lines.append("_(no new rules)_")

    # ── Natural-language translation ─────────────────────────────────────────
    if rec.natural_language_rules:
        lines.append("")
        lines.append("_Plain language:_")
        for nl in rec.natural_language_rules:
            lines.append(f"- {nl}")

    # ── Analysis narrative ───────────────────────────────────────────────────
    if rec.narrative:
        lines.append("")
        lines.append(f"> {rec.narrative}")

    # ── Graded entailment table ──────────────────────────────────────────────
    if rec.graded_scores:
        lines.append("")
        lines.append("| Query | Crisp | σ | Agree |")
        lines.append("|---|---|---|---|")
        for q, gs in rec.graded_scores.items():
            agree_str = "yes" if gs.get("agree") else "no"
            strength  = gs.get("strength", gs.get("graded_strength", 0.0))
            lines.append(f"| `{q}` | {gs.get('crisp', gs.get('crisp_entailed', '?'))} "
                         f"| {strength:.3f} | {agree_str} |")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def export_frameworks(
    records: List[FrameworkRecord],
    output_dir: str,
    basename: str = "frameworks",
) -> Dict[str, str]:
    """
    Write all three artefacts. Returns the paths written.
    `records` should contain the symbolic solution AND the LLM samples for each
    problem, so they sit side by side.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths: Dict[str, str] = {}

    # 1. JSONL (re-loadable)
    jsonl_path = os.path.join(output_dir, f"{basename}.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec.to_dict()) + "\n")
    paths["jsonl"] = jsonl_path

    # 2. Markdown catalogue, grouped by problem
    by_problem: Dict[str, List[FrameworkRecord]] = {}
    for rec in records:
        by_problem.setdefault(rec.problem_id, []).append(rec)

    md_lines = ["# Learned ABA frameworks\n",
                "Each problem shows the symbolic ground truth followed by the "
                "LLM-generated candidates. `DEFEASIBLE` means the solution uses "
                "an assumption (the hard case); `MONOTONIC` means it does not.\n"]
    for pid, recs in by_problem.items():
        md_lines.append(f"\n## {pid}\n")
        # symbolic first
        recs_sorted = sorted(recs, key=lambda r: (r.source != "symbolic",
                                                  r.mode, r.sample_idx))
        for rec in recs_sorted:
            md_lines.append(_framework_md(rec))
            md_lines.append("")
    md_path = os.path.join(output_dir, f"{basename}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    paths["md"] = md_path

    # 3. Flat CSV table for quick statistics
    csv_path = os.path.join(output_dir, "defeasibility.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("problem_id,source,mode,sample_idx,is_defeasible,is_monotonic,"
                "is_intensional,n_new_rules,n_defeasible_rules,n_contrary_rules,"
                "valid,generalises\n")
        for rec in records:
            st = rec.structure
            f.write(",".join(str(x) for x in [
                rec.problem_id, rec.source, rec.mode, rec.sample_idx,
                st["is_defeasible"], st["is_monotonic"], st["is_intensional"],
                st["n_new_rules"], st["n_defeasible_rules"], st["n_contrary_rules"],
                rec.valid, rec.generalises,
            ]) + "\n")
    paths["csv"] = csv_path

    return paths


def defeasibility_summary(records: List[FrameworkRecord]) -> Dict[str, Any]:
    """
    Aggregate proof that we are learning defeasible (not monotonic) rules,
    broken down by source.
    """
    by_source: Dict[str, Dict[str, int]] = {}
    for rec in records:
        s = by_source.setdefault(rec.source, {"total": 0, "defeasible": 0,
                                              "monotonic": 0})
        s["total"] += 1
        if rec.structure["is_defeasible"]:
            s["defeasible"] += 1
        if rec.structure["is_monotonic"]:
            s["monotonic"] += 1
    return {
        src: {
            **counts,
            "defeasible_rate": round(counts["defeasible"] / counts["total"], 3)
                               if counts["total"] else 0.0,
        }
        for src, counts in by_source.items()
    }
