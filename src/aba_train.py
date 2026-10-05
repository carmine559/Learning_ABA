"""The SFT corpus as token ids, the token audit, and run provenance.

`encode` is the one tokenisation of a row: the token audit counts with it,
`train_sft.py` trains on it, and generation is fed its prompt part (asserted in
`eval_sft.py`), so the ids a model is trained after are the ids it generates
after. The chat is `to_messages`: one user turn holding the v4-sft prompt, as
every local run has sent it (Qwen's template adds its default system turn),
then the target, closed by <|im_end|>. The loss is on the target and that
closing token only.

The token audit (`python train_sft.py --audit`) writes corpus/<v>/TOKENS.json
once, before any run: token counts per file, split and target, and the
pre-registered secondary arm matching (MANIFEST `arm_matching`): the trace/
endpoint ratio of supervised target tokens on the train split.
"""
from __future__ import annotations

import collections
import importlib.metadata
import json
import math
import platform
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.aba_corpus import _sha256
from src.aba_model import LOCAL_MODELS, to_messages

ARMS = ("endpoint", "trace")
EPOCHS = 3                        # primary matching: same optimiser steps
AUDITED = ("sft_endpoint.jsonl", "sft_trace.jsonl", "eval.jsonl", "table1_eval.jsonl")
_TARGETS = ("target", "trace_target", "endpoint_target")


def model_id(model: str) -> str:
    return LOCAL_MODELS.get(model, model)


def encode(tok, prompt: str, target: Optional[str] = None) -> Tuple[List[int], int]:
    """(ids, n_prompt): the chat as token ids; generation is fed ids[:n_prompt]."""
    p = tok.apply_chat_template(to_messages(prompt), add_generation_prompt=True,
                                tokenize=True, return_dict=True)["input_ids"]
    if target is None:
        return p, len(p)
    ids = tok.apply_chat_template(to_messages(prompt, target), tokenize=True,
                                  return_dict=True)["input_ids"]
    assert ids[:len(p)] == p, "the chat template does not extend the prompt"
    end = ids.index(tok.eos_token_id, len(p)) + 1
    assert tok.decode(ids[len(p):end]) == target + tok.eos_token
    return ids[:end], len(p)


def schedule(n: int, epochs: float, seed: int) -> List[int]:
    """Row indices in training order: a fresh seeded permutation per epoch."""
    rng, order = random.Random(seed), []
    while len(order) < round(epochs * n):
        perm = list(range(n))
        rng.shuffle(perm)
        order += perm
    return order[:round(epochs * n)]


def rows(corpus: Path, name: str, split: Optional[str] = None) -> List[Dict]:
    with open(corpus / name, encoding="utf-8") as f:
        out = [json.loads(line) for line in f]
    return [r for r in out if split is None or r["split"] == split]


def verified(corpus: Path, names) -> Dict[str, str]:
    """sha256 of each file, which must equal the corpus MANIFEST's."""
    want = json.loads((corpus / "MANIFEST.json").read_text(encoding="utf-8"))["sha256"]
    got = {n: _sha256(corpus / n) for n in names}
    bad = [n for n in names if got[n] != want.get(n)]
    if bad:
        raise SystemExit(f"{corpus}: {bad} differ from MANIFEST.json; rebuild or re-sync")
    return got


def revision(mid: str) -> str:
    """The cached snapshot's commit, read offline."""
    from huggingface_hub import try_to_load_from_cache
    p = try_to_load_from_cache(mid, "tokenizer_config.json")
    return Path(p).parent.name if isinstance(p, str) else "unknown"


def versions() -> Dict[str, Optional[str]]:
    out = {"python": platform.python_version()}
    for pkg in ("torch", "transformers", "tokenizers", "accelerate", "peft", "clingo"):
        try:
            out[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            out[pkg] = None
    return out


# ─────────────────────────────────────────────────────────────────────────────
# The token audit
# ─────────────────────────────────────────────────────────────────────────────

def _summary(pairs: List[Tuple[int, int]]) -> Dict:
    prompt, target = [p for p, _ in pairs], [t for _, t in pairs]
    return {"n": len(pairs),
            "prompt_mean": round(sum(prompt) / len(prompt), 1), "prompt_max": max(prompt),
            "target_sum": sum(target), "target_mean": round(sum(target) / len(target), 1),
            "target_max": max(target), "total_max": max(p + t for p, t in pairs)}


def token_audit(corpus: Path, model: str) -> Dict:
    from transformers import AutoConfig, AutoTokenizer
    mid = model_id(model)
    tok = AutoTokenizer.from_pretrained(mid)
    names = [n for n in AUDITED if (corpus / n).exists()]
    sha = verified(corpus, names)

    arms = {a: rows(corpus, f"sft_{a}.jsonl") for a in ARMS}
    assert ([(r["problem_id"], r["split"], r["prompt"]) for r in arms["trace"]]
            == [(r["problem_id"], r["split"], r["prompt"]) for r in arms["endpoint"]]), \
        "the two arms must pose the same problems, in the same order, with one prompt"

    files = {}
    for name in names:
        by = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows(corpus, name):
            for t in _TARGETS:
                if t in r:
                    ids, n = encode(tok, r["prompt"], r[t])
                    by[r["split"]][t].append((n, len(ids) - n))
        files[name] = {s: {t: _summary(v) for t, v in f.items()} for s, f in by.items()}

    context = AutoConfig.from_pretrained(mid).max_position_embeddings
    longest = max(s["total_max"] for f in files.values() for d in f.values() for s in d.values())
    assert longest < context, f"a row of {longest} tokens exceeds the context ({context})"

    trace = files["sft_trace.jsonl"]["train"]["target"]["target_sum"]
    endpoint = files["sft_endpoint.jsonl"]["train"]["target"]["target_sum"]
    gold = max(s["trace_target"]["target_max"] for name in ("eval.jsonl", "table1_eval.jsonl")
               if name in files for s in files[name].values())
    return {
        "model": mid, "revision": revision(mid), "versions": versions(),
        "chat": "one user turn (the prompt), Qwen's default system turn, then the "
                "target and <|im_end|>; target tokens include <|im_end|>",
        "sha256": sha,
        "context": context, "longest_row": longest,
        "files": files,
        "arm_matching": {
            "trace_target_tokens_train": trace,
            "endpoint_target_tokens_train": endpoint,
            "ratio": round(trace / endpoint, 4),
            "primary_epochs": EPOCHS,
            "secondary_endpoint_epochs": round(EPOCHS * trace / endpoint, 2),
        },
        # Same budget for every arm: twice the longest gold trace it is scored on.
        "max_new_tokens": 128 * math.ceil(2 * gold / 128),
    }


def load_audit(corpus: Path, model: str) -> Dict:
    """TOKENS.json, checked against the model and the corpus it was made from."""
    path = corpus / "TOKENS.json"
    if not path.exists():
        raise SystemExit(f"{path} missing: run `python train_sft.py --audit` and commit it first")
    audit = json.loads(path.read_text(encoding="utf-8"))
    assert audit["model"] == model_id(model), f"TOKENS.json is for {audit['model']}"
    assert verified(corpus, list(audit["sha256"])) == audit["sha256"], \
        "the corpus changed since the token audit"
    return audit
