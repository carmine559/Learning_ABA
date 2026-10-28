"""
aba_evaluation.py
End-to-end evaluation of prompted answers, every problem posed whole.

Each answer is scored by `src.aba_score.score_output` against the algorithm's run
on the same problem: Definition 1 on the posed examples (valid, clean), exact
agreement with the algorithm's answer, and agreement off the examples. Each
problem is asked n_samples times, each sample with its own seed; @1 is the mean
over samples, @k any sample, with Wilson intervals over problems.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import re
from dataclasses import dataclass, field, fields
from typing import Dict, List, Optional, Tuple

from src.aba_dataset import ABADataset, DatasetEntry
from src.aba_model import LLMBackend
from src.aba_prompts import _parse_rule_line, problem_to_prompt
from src.aba_score import Reference, ScoreCard, balanced, mean, score_output

METRICS = ("valid", "clean", "exact")
_CARD_FIELDS = {f.name for f in fields(ScoreCard)}
_TIER_RE = re.compile(r"^(t\d+_[a-z]+)_\d+")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sample_seed(run_seed: int, pid: str, mode: str, idx: int) -> int:
    """The same seed for the same sample, in whatever order a run reaches it."""
    return int(sha256(f"{run_seed}:{pid}:{mode}:{idx}")[:8], 16) % 2 ** 31


class ResumeMismatch(RuntimeError):
    """A stored row is not the sample this run would draw: stop, do not mix runs."""


def tier_of(pid: str) -> str:
    """`t1_mono_0007[_anon]` -> `t1_mono`; the built-ins group as `builtin`."""
    m = _TIER_RE.match(pid)
    return m.group(1) if m else "builtin"


# ──────────────────────────────────────────────────────────────────────────────
# One sample
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SampleResult:
    """One answer to one problem. Every score is in `card`."""
    problem_id: str
    mode: str
    model_name: str
    sample_idx: int = 0
    seed: Optional[int] = None
    problem_sha256: str = ""
    prompt_sha256: str = ""
    raw_output: str = ""
    finish: str = ""                # stop | length | error
    llm_latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    error: str = ""                 # the card's label, llm_error or unscorable:<type>
    card: ScoreCard = field(default_factory=ScoreCard)

    def to_dict(self) -> Dict:
        row = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "card"}
        row.update({k: v for k, v in self.card.to_dict().items() if k != "error"})
        return row

    @classmethod
    def from_dict(cls, row: Dict) -> "SampleResult":
        card = ScoreCard(**{k: row[k] for k in _CARD_FIELDS if k in row})
        own = {f.name for f in fields(cls)} - {"card"}
        return cls(**{k: row[k] for k in own if k in row}, card=card)


def score_sample(ref: Reference, raw: str, truncated: bool,
                 audit: bool = False) -> Tuple[ScoreCard, str]:
    """Never raises: model text must not stop a GPU job."""
    try:
        card = score_output(raw, ref, truncated=truncated, audit=audit)
        return card, card.error
    except Exception as exc:                       # noqa: BLE001
        return ScoreCard(truncated=truncated), f"unscorable:{type(exc).__name__}"


def evaluate_one_sample(
    entry: DatasetEntry,
    ref: Reference,
    backend: LLMBackend,
    mode: str,
    sample_idx: int = 0,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    run_seed: int = 0,
    problem_sha256: str = "",
    role_facts=None,
    audit: bool = False,
) -> SampleResult:
    """Prompt the model once, then score its answer.

    Deliberately ONE turn: a follow-up carrying the solver's verdict back to the
    model would measure oracle-guided search, not replication.
    """
    pid = entry.problem.problem_id
    prompt = problem_to_prompt(entry.problem, mode=mode,
                               precomputed_role_facts=role_facts)
    s = SampleResult(problem_id=pid, mode=mode,
                     model_name=getattr(backend, "model", type(backend).__name__),
                     sample_idx=sample_idx, seed=sample_seed(run_seed, pid, mode, sample_idx),
                     problem_sha256=problem_sha256, prompt_sha256=sha256(prompt))
    try:
        resp = backend.generate(prompt, temperature=temperature,
                                max_tokens=max_tokens, seed=s.seed)
    except Exception as exc:                       # noqa: BLE001
        import traceback
        # The full traceback: an opaque error costs a cluster run to diagnose.
        s.finish, s.error = "error", "llm_error"
        s.raw_output = (f"[LLM ERROR] {type(exc).__name__}: {exc}\n"
                        + traceback.format_exc())
        return s
    s.raw_output = resp.text
    s.llm_latency_s = resp.latency_s
    s.prompt_tokens, s.completion_tokens = resp.prompt_tokens, resp.completion_tokens
    s.finish = resp.finish_reason or (
        "length" if resp.completion_tokens and resp.completion_tokens >= max_tokens
        else "stop")
    s.card, s.error = score_sample(ref, resp.text, s.finish == "length", audit)
    return s


# ──────────────────────────────────────────────────────────────────────────────
# k samples per problem
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProblemResult:
    problem_id: str
    mode: str
    model_name: str
    structure: str = ""             # src.aba_corpus.structural_signature
    samples: List[SampleResult] = field(default_factory=list)

    @property
    def tier(self) -> str:
        return tier_of(self.problem_id)

    def at_1(self, key: str) -> float:
        """Mean over the samples."""
        if not self.samples:
            return 0.0
        return sum(bool(getattr(s.card, key)) for s in self.samples) / len(self.samples)

    def at_k(self, key: str) -> bool:
        """Any sample."""
        return any(getattr(s.card, key) for s in self.samples)


def evaluate_dataset(
    dataset: ABADataset,
    refs: Dict[str, Reference],
    backend: LLMBackend,
    mode: str,
    n_samples: int = 3,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    run_seed: int = 0,
    structures: Optional[Dict[str, str]] = None,
    problem_sha: Optional[Dict[str, str]] = None,
    rows_path: Optional[str] = None,
    audit: bool = False,
    verbose: bool = True,
) -> List[ProblemResult]:
    """Every problem with a reference, n_samples each.

    Rows are appended to `rows_path` as they are scored and rows already there
    are reused, so a killed run resumes; a reused row must be the same sample
    (same seed and prompt), or the run stops.
    """
    model_name = getattr(backend, "model", type(backend).__name__)
    done: Dict[Tuple[str, int], SampleResult] = {}
    if rows_path and os.path.exists(rows_path):
        with open(rows_path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    s = SampleResult.from_dict(json.loads(line))
                    if s.mode == mode:
                        done[(s.problem_id, s.sample_idx)] = s
    out = open(rows_path, "a", encoding="utf-8") if rows_path else None
    entries = [e for e in dataset if e.problem.problem_id in refs]
    results: List[ProblemResult] = []
    shown_error = False
    try:
        for i, entry in enumerate(entries, 1):
            pid = entry.problem.problem_id
            ref = refs[pid]
            role_facts = ([_parse_rule_line(f) for f in ref.record.role_facts]
                          if mode == "guided" else None)
            pr = ProblemResult(pid, mode, model_name,
                               structure=(structures or {}).get(pid, ""))
            for idx in range(n_samples):
                s = done.get((pid, idx))
                if s is not None:
                    want = problem_to_prompt(entry.problem, mode=mode,
                                             precomputed_role_facts=role_facts)
                    if (s.seed, s.prompt_sha256, s.model_name) != (
                            sample_seed(run_seed, pid, mode, idx), sha256(want), model_name):
                        raise ResumeMismatch(
                            f"{rows_path} holds a row of another run ({pid} #{idx}); "
                            "move it away or use another --output")
                else:
                    s = evaluate_one_sample(
                        entry, ref, backend, mode, sample_idx=idx,
                        temperature=temperature, max_tokens=max_tokens,
                        run_seed=run_seed, problem_sha256=(problem_sha or {}).get(pid, ""),
                        role_facts=role_facts, audit=audit)
                    if out:
                        out.write(json.dumps(s.to_dict()) + "\n")
                        out.flush()
                pr.samples.append(s)
            results.append(pr)
            if verbose:
                print(f"  [{i}/{len(entries)}] {pid}: clean {pr.at_1('clean'):.0%} "
                      f"exact {pr.at_1('exact'):.0%} parse {pr.at_1('parse_ok'):.0%}")
            # The first LLM error, in full: otherwise a bad model id looks like
            # a run of unparseable answers.
            errs = [s for s in pr.samples if s.error == "llm_error"]
            if errs and not shown_error:
                shown_error = True
                print(f"\n  [!] LLM ERROR ({type(backend).__name__}): "
                      f"{errs[0].raw_output}\n")
    finally:
        if out:
            out.close()
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Aggregation
# ──────────────────────────────────────────────────────────────────────────────

def wilson_interval(successes: float, n: int, z: float = 1.96) -> List[float]:
    """Wilson 95% score interval for a proportion."""
    if n <= 0:
        return [0.0, 0.0]
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round(max(0.0, (centre - half) / denom), 3),
            round(min(1.0, (centre + half) / denom), 3)]


def aggregate_results(results: List[ProblemResult]) -> Dict:
    """@1 and @k for valid, clean and exact, with the answer-level details."""
    if not results:
        return {}
    n = len(results)
    samples = [s for r in results for s in r.samples]
    cards = [s.card for s in samples]
    out: Dict = {"n_problems": n,
                 "n_structures": len({r.structure or r.problem_id for r in results}),
                 "n_samples": len(samples)}
    ci = {}
    for key in METRICS:
        k = sum(r.at_k(key) for r in results)
        out[f"{key}_at_1"] = round(sum(r.at_1(key) for r in results) / n, 3)
        out[f"{key}_at_k"] = round(k / n, 3)
        ci[f"{key}_at_k"] = wilson_interval(k, n)
    out["ci95"] = ci
    # Agreement over the answers where it is defined, as in sft/eval_sft.py.
    out["agreement"] = mean(c.agreement for c in cards)
    out["parse_rate"] = mean(c.parse_ok for c in cards)
    out["truncated_rate"] = mean(c.truncated for c in cards)
    out["intensional_rate"] = mean(c.intensional for c in cards if c.valid)
    r3 = collections.Counter(f"{'yes' if c.ref_defeasible else 'no'}/"
                             f"{'yes' if c.defeasible else 'no'}"
                             for c in cards if c.defeasible is not None)
    out["r3"] = dict(r3)
    out["r3_balanced"] = balanced(r3)
    r2 = collections.Counter()
    for c in cards:
        r2.update(c.r2_bodies)
    out["r2_exact"] = round(r2["exact"] / r2["n"], 4) if r2["n"] else None
    # `direct` asks for an answer, not a derivation: it has no trace to score.
    out["trace_f1"] = mean(c.trace_fidelity["f1"] for s, c in zip(samples, cards)
                           if s.mode != "direct" and c.trace_fidelity
                           and c.trace_fidelity["has_trace"])
    out["errors"] = dict(collections.Counter(s.error for s in samples))
    out["parse_repairs"] = dict(collections.Counter(
        rep.split(":")[0] for c in cards for rep in c.repairs))
    return out


def tier_breakdown(results_by_mode: Dict[str, List[ProblemResult]]) -> Dict[str, Dict[str, Dict]]:
    """mode -> tier -> aggregate; {} when no benchmark problems are present."""
    out: Dict[str, Dict[str, Dict]] = {}
    for mode, results in results_by_mode.items():
        groups: Dict[str, List[ProblemResult]] = collections.defaultdict(list)
        for pr in results:
            groups[pr.tier].append(pr)
        out[mode] = {tier: aggregate_results(prs) for tier, prs in sorted(groups.items())}
    return out if any(t != "builtin" for m in out.values() for t in m) else {}


def summarise(results_by_mode: Dict[str, List[ProblemResult]], run: Dict) -> Dict:
    """summary.json: the run's provenance, one aggregate per mode, and per tier."""
    summary: Dict = {"run": run}
    summary.update({mode: aggregate_results(rs) for mode, rs in results_by_mode.items()})
    by_tier = tier_breakdown(results_by_mode)
    if by_tier:
        summary["by_tier"] = by_tier
    return summary


def complexity_analysis(dataset: ABADataset, results: List[ProblemResult]) -> List[Dict]:
    """One row per problem: its size against clean@k, for the scatter plot."""
    rmap = {r.problem_id: r for r in results}
    rows = []
    for entry in dataset:
        r = rmap.get(entry.problem.problem_id)
        if r is None:
            continue
        p = entry.problem
        rows.append({
            "problem_id": p.problem_id,
            "n_background_rules": len(p.background.rules),
            "n_assumptions": len(p.background.assumptions),
            "n_positive": len(p.positive),
            "n_negative": len(p.negative),
            "domain_size": len(p.get_domain()),
            "clean_at_k": r.at_k("clean"),
            "clean_at_1": r.at_1("clean"),
            "exact_at_k": r.at_k("exact"),
        })
    return rows
