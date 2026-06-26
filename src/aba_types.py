"""
aba_types.py
Core data structures for ABA framework learning.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import re


# ---------------------------------------------------------------------------
# Core ABA primitives
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    head: str
    body: List[str] = field(default_factory=list)

    def to_prolog(self) -> str:
        if not self.body:
            return f"{self.head}."
        return f"{self.head} :- {', '.join(self.body)}."

    def to_text(self) -> str:
        if not self.body:
            return f"{self.head} is always true."
        return f"{self.head} holds if {' and '.join(self.body)}."

    def is_ground(self) -> bool:
        """True if the rule contains no variables (only constants)."""
        text = self.head + " ".join(self.body)
        # Variables in Prolog start with uppercase or '_'
        tokens = re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', text)
        return not any(t[0].isupper() or t.startswith('_') for t in tokens
                       if t not in ('true', 'false'))

    def is_intensional(self) -> bool:
        """True if no equality X=constant appears in body (rule is general)."""
        eq_pattern = re.compile(r'\b[A-Z]\w*\s*=\s*[a-z]\w*')
        body_str = ", ".join(self.body)
        return not bool(eq_pattern.search(body_str))

    def get_constants(self) -> List[str]:
        """Extract all constant symbols (lowercase atoms) from the rule."""
        text = self.head + " ".join(self.body)
        tokens = re.findall(r'\b([a-z][a-z0-9_]*)\b', text)
        keywords = {'not', 'true', 'dom', 'is', 'if', 'and'}
        return [t for t in tokens if t not in keywords]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rule):
            return False
        return self.head == other.head and self.body == other.body

    def __hash__(self) -> int:
        return hash((self.head, tuple(self.body)))

    def __repr__(self) -> str:
        return self.to_prolog()


@dataclass
class ABAFramework:
    rules: List[Rule] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    contraries: Dict[str, str] = field(default_factory=dict)

    # Track which rules/assumptions were *added* by learning
    new_rules: List[Rule] = field(default_factory=list)
    new_assumptions: List[str] = field(default_factory=list)

    def to_prolog_block(self, include_dom: bool = False,
                        domain: Optional[List[str]] = None) -> str:
        lines = []
        if include_dom and domain:
            for c in domain:
                lines.append(f"dom({c}).")
            lines.append("")
        for rule in self.rules:
            lines.append(rule.to_prolog())
        lines.append("")
        for asm in self.assumptions:
            contrary = self.contraries.get(asm, f"c_{asm}")
            var_match = re.search(r'\((.+)\)', asm)
            var = var_match.group(1) if var_match else 'X'
            lines.append(f"{asm} :- dom({var}), not {contrary}.")
        return "\n".join(lines)

    def to_natural_language(self) -> str:
        parts = ["Rules:"]
        for r in self.rules:
            parts.append(f"  - {r.to_text()}")
        if self.assumptions:
            parts.append("Assumptions (defeasible by default):")
            for asm in self.assumptions:
                contrary = self.contraries.get(asm, f"c_{asm}")
                parts.append(f"  - {asm}  [defeated by: {contrary}]")
        return "\n".join(parts)

    def get_domain(self) -> List[str]:
        """Infer the domain (all constants) from rules."""
        constants = set()
        for rule in self.rules:
            constants.update(rule.get_constants())
        return sorted(constants)

    def is_intensional(self) -> bool:
        """True if all *new* rules are intensional."""
        return all(r.is_intensional() for r in self.new_rules)

    def merge(self, other: 'ABAFramework') -> 'ABAFramework':
        """Return a new framework combining self and other."""
        all_rules = list(dict.fromkeys(self.rules + other.rules))
        all_asms = list(dict.fromkeys(self.assumptions + other.assumptions))
        all_contraries = {**self.contraries, **other.contraries}
        return ABAFramework(
            rules=all_rules,
            assumptions=all_asms,
            contraries=all_contraries,
            new_rules=other.new_rules,
            new_assumptions=other.new_assumptions,
        )

    def copy(self) -> 'ABAFramework':
        return ABAFramework(
            rules=list(self.rules),
            assumptions=list(self.assumptions),
            contraries=dict(self.contraries),
            new_rules=list(self.new_rules),
            new_assumptions=list(self.new_assumptions),
        )

    def __repr__(self) -> str:
        return (f"ABAFramework("
                f"{len(self.rules)} rules, "
                f"{len(self.assumptions)} assumptions)")


@dataclass
class LearningProblem:
    background: ABAFramework
    positive: List[str]       # ground atoms to bravely entail
    negative: List[str]       # ground atoms to NOT bravely entail
    learnable: List[str]      # predicate names allowed to appear in new rule heads
    domain: Optional[List[str]] = None  # explicit domain, inferred if None
    problem_id: str = ""

    def get_domain(self) -> List[str]:
        if self.domain is not None:
            return self.domain
        return self.background.get_domain()

    def __repr__(self) -> str:
        return (f"LearningProblem(id={self.problem_id!r}, "
                f"E+={self.positive}, E-={self.negative})")


# ---------------------------------------------------------------------------
# Transformation trace
# ---------------------------------------------------------------------------

@dataclass
class TransformStep:
    step_type: str   # "rote_learning" | "folding" | "assumption_introduction"
                     # | "fact_subsumption"
    input_rule: Optional[Rule] = None
    output_rule: Optional[Rule] = None
    folding_rule: Optional[Rule] = None       # the rule used to fold
    new_assumption: Optional[str] = None      # for assumption_introduction
    new_contrary_facts: List[Rule] = field(default_factory=list)
    note: str = ""

    def to_text(self) -> str:
        if self.step_type == "rote_learning":
            return f"Rote Learning: added {self.output_rule}"
        if self.step_type == "folding":
            return (f"Folding: {self.input_rule} → {self.output_rule} "
                    f"(using {self.folding_rule})")
        if self.step_type == "assumption_introduction":
            return (f"Assumption Introduction: {self.input_rule} → "
                    f"{self.output_rule}, new assumption {self.new_assumption}")
        if self.step_type == "fact_subsumption":
            return f"Fact Subsumption: removed {self.input_rule}"
        return f"Step({self.step_type})"


@dataclass
class LearningTrace:
    problem_id: str
    steps: List[TransformStep] = field(default_factory=list)
    final_framework: Optional[ABAFramework] = None
    success: bool = False

    def to_cot_text(self) -> str:
        """Serialise trace as chain-of-thought text for SFT."""
        parts = []
        for i, step in enumerate(self.steps, 1):
            parts.append(f"Step {i} [{step.step_type}]: {step.to_text()}")
        if self.final_framework:
            parts.append("\nFinal framework:")
            parts.append(self.final_framework.to_natural_language())
        return "\n".join(parts)
