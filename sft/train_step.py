"""LoRA SFT of arm S2: one row per step of Algorithm 1 (corpus/v1-step, src/aba_steps.py).

    python sft/train_step.py --audit                          # once, before any run: TOKENS.json
    python sft/train_step.py --out runs/sft_step              # the run
    python sft/train_step.py --out runs/sft_step_s1 --seed 1  # a replicate
    python sft/train_step.py --out runs/sft_step --dry-run    # everything but the model (login node)
    python sft/train_step.py --out <scratch> --smoke --limit 4   # CPU, the cached tiny Qwen2

Matching to the registered arms (train_sft.py): the same train problems in the same order,
the trace arm's `schedule(1500, 3, seed 0)` (its order hash is asserted; another --seed is
a replicate with its own order and initialisation), each problem
expanded to its step rows; ROWS_PER_STEP rows per optimiser step, about 16 problems' worth,
so about the same 282 steps; the same LoRA, learning rate, cosine schedule, 3% warmup and
seed. What differs is the arm: the prompts are step prompts (rebuilt from corpus/v1-step and
pinned by its prompt_sha256), and the loss is a per-example mean (each row's mean over its
target tokens; rows weigh equally), so a one-token verdict is not drowned by long rows.

Val: the per-example loss every 47 steps on a fixed subset of val problems (5 per tier and
class) and at the end; at the same times, the first line-18 test of all 200 val problems at
gold states, generated greedily and read to its verdict (`val_first_check_balanced`).
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from sft.train_sft import LORA, LR, WARMUP, _write
from src.aba_corpus import _sha256, problem_from_dict
from src.aba_steps import STEP_PROMPT_VERSION, StepStop, parse_answer, step_prompt
from src.aba_tracelog import _git_rev
from src.aba_train import EPOCHS, encode, model_id, revision, schedule, versions

ROWS_PER_STEP, MICRO = 212, 4                # 4 x 53; 3 x 19,805 rows -> 281 steps
EVAL_EVERY = 47                              # as the registered arms: half of 1500 / 16
TRACE_RUN = Path("runs/sft_trace/TRAINING_MANIFEST.json")
SMOKE_MODEL = "trl-internal-testing/tiny-Qwen2ForCausalLM-2.5"
FIRST_CHECK_BUDGET = 64                      # tokens; the longest val first-check target is shorter


# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────

def load(corpus: Path):
    """(manifest, problems by id, rows by split), checked against the corpus manifest."""
    m = json.loads((corpus / "MANIFEST.json").read_text(encoding="utf-8"))
    assert m["prompt_version"] == STEP_PROMPT_VERSION, m["prompt_version"]
    assert _sha256(corpus / "steps.jsonl") == m["sha256"]["steps.jsonl"], "steps.jsonl changed"
    src = Path(m["source"]["corpus"])
    assert _sha256(src / "problems.jsonl") == m["source"]["sha256"]["problems.jsonl"]
    probs = {}
    for line in open(src / "problems.jsonl", encoding="utf-8"):
        r = json.loads(line)
        probs[r["problem_id"]] = problem_from_dict(r["problem"])
    rows = collections.defaultdict(list)
    for line in open(corpus / "steps.jsonl", encoding="utf-8"):
        r = json.loads(line)
        rows[r["split"]].append(r)
    return m, probs, rows


def prompts(rows, probs, manifest=None):
    """Rebuilt prompts, in row order; asserted against prompt_sha256 when given."""
    out, h = [], collections.defaultdict(hashlib.sha256)
    for r in rows:
        p = step_prompt(probs[r["problem_id"]], r["kind"], r["state"])
        out.append(p)
        h[f"{r['split']}/{r['kind']}"].update(p.encode("utf-8") + b"\x00")
    if manifest is not None:
        want = {k: v for k, v in manifest["prompt_sha256"].items()
                if k.split("/")[0] in {r["split"] for r in rows}}
        assert {k: v.hexdigest() for k, v in h.items()} == want, "prompts differ from the build"
    return out


def problem_order(train_ids, seed):
    """The trace arm's problem order: schedule over sft_trace.jsonl's train rows."""
    order = schedule(len(train_ids), EPOCHS, seed)
    return [train_ids[i] for i in order]


def val_subset(rows):
    """5 val problems per tier and class, in file order: the eval-loss rows."""
    per, keep = collections.Counter(), set()
    for r in rows:
        key = (r["tier"], r["class"])
        if r["problem_id"] not in keep and per[key] < 5:
            per[key] += 1
            keep.add(r["problem_id"])
    return [r for r in rows if r["problem_id"] in keep]


# ─────────────────────────────────────────────────────────────────────────────
# Token audit
# ─────────────────────────────────────────────────────────────────────────────

def audit(corpus: Path, model: str) -> int:
    from transformers import AutoConfig, AutoTokenizer
    path = corpus / "TOKENS.json"
    if path.exists():
        raise SystemExit(f"{path} exists: written once, before any run")
    m, probs, rows = load(corpus)
    mid = model_id(model)
    tok = AutoTokenizer.from_pretrained(mid)
    stats, longest_row = {}, 0
    for split, rs in rows.items():
        by = collections.defaultdict(list)
        for r, p in zip(rs, prompts(rs, probs, m)):
            ids, n = encode(tok, p, r["target"])
            by[r["kind"] + (" (extra)" if r["extra"] else "")].append((n, len(ids) - n))
        stats[split] = {k: {"n": len(v), "prompt_mean": round(sum(a for a, _ in v) / len(v), 1),
                            "prompt_max": max(a for a, _ in v),
                            "target_sum": sum(b for _, b in v),
                            "target_mean": round(sum(b for _, b in v) / len(v), 1),
                            "target_max": max(b for _, b in v)}
                        for k, v in sorted(by.items())}
        longest_row = max(longest_row, max(a + b for v in by.values() for a, b in v))
    context = AutoConfig.from_pretrained(mid).max_position_embeddings
    assert longest_row < context
    # every set's longest gold target, Table 1 and permuted included (MANIFEST longest_target)
    target_tokens = lambda t: len(tok(t, add_special_tokens=False)["input_ids"]) + 1
    longest = {k: max([target_tokens(t)] + [s["target_max"] for sp in stats.values()
                                             for kk, s in sp.items() if kk.split(" ")[0] == k])
               for k, t in m["longest_target"].items()}
    n_train = sum(s["n"] for s in stats["train"].values())
    t = {"model": mid, "revision": revision(mid), "versions": versions(),
         "prompt_version": STEP_PROMPT_VERSION, "sha256": m["sha256"],
         "chat": "one user turn (the step prompt), Qwen's default system turn, then the "
                 "target and <|im_end|>; target tokens include <|im_end|>",
         "context": context, "longest_row": longest_row, "files": {"steps.jsonl": stats},
         "longest_target_tokens": longest,
         "max_new_tokens": {k: max(16, 16 * math.ceil(2 * v / 16)) for k, v in longest.items()},
         "matching": {"epochs": EPOCHS, "rows_per_step": ROWS_PER_STEP, "micro_batch": MICRO,
                      "train_rows": n_train,
                      "steps": math.ceil(EPOCHS * n_train / ROWS_PER_STEP),
                      "problems_per_step": round(ROWS_PER_STEP * 1500 / n_train, 1)}}
    _write(path, t)
    print(f"wrote {path}: {n_train} train rows, longest row {longest_row} tokens, "
          f"{t['matching']['steps']} steps\n  max_new_tokens {t['max_new_tokens']}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Loss and the first-check monitor
# ─────────────────────────────────────────────────────────────────────────────

def per_example_trainer():
    import torch
    from transformers import Trainer

    class PerExampleTrainer(Trainer):
        """Each row's loss is the mean over its target tokens; rows weigh equally."""

        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            # num_items_in_batch unused: training_step divides by the micro-batches taken
            self.model_accepts_loss_kwargs = False

        def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
            inputs = dict(inputs)
            labels = inputs.pop("labels")
            out = model(**inputs)
            tgt = labels[:, 1:]
            mask = tgt.ne(-100)
            ce = torch.nn.functional.cross_entropy(out.logits[:, :-1][mask].float(), tgt[mask],
                                                   reduction="none")
            rows = torch.zeros(labels.size(0), device=ce.device, dtype=ce.dtype)
            rows = rows.index_add(0, mask.nonzero()[:, 0], ce) / mask.sum(1).clamp(min=1)
            loss = rows.mean()
            return (loss, out) if return_outputs else loss

    return PerExampleTrainer


def balanced(pairs):
    """Balanced accuracy of (truth, said) pairs; said None counts as wrong."""
    yes = [s is True for t, s in pairs if t]
    no = [s is False for t, s in pairs if not t]
    parts = [sum(v) / len(v) for v in (yes, no) if v]
    return round(sum(parts) / len(parts), 4) if parts else None


def first_check_callback(tok, items):
    """At every evaluation, the val first checks at gold states, greedy, to the verdict."""
    import torch
    from transformers import TrainerCallback

    class FirstCheck(TrainerCallback):
        def on_evaluate(self, args, state, control, model=None, metrics=None, **kw):
            was = model.training
            model.eval()
            pairs = []
            with torch.no_grad():
                for prompt, truth, p in items:
                    ids, _ = encode(tok, prompt)
                    x = torch.tensor([ids], device=model.device)
                    y = model.generate(input_ids=x, attention_mask=torch.ones_like(x),
                                       max_new_tokens=FIRST_CHECK_BUDGET, do_sample=False,
                                       use_cache=True, pad_token_id=tok.pad_token_id)
                    text = tok.decode(y[0, len(ids):], skip_special_tokens=True)
                    try:
                        said = parse_answer("check", text, p)[0]
                    except StepStop:
                        said = None
                    pairs.append((truth, said))
            if was:
                model.train()
            b = balanced(pairs)
            state.log_history.append({"step": state.global_step,
                                      "val_first_check_balanced": b,
                                      "val_first_check_unparseable": sum(s is None for _, s in pairs),
                                      "val_first_check_n": len(pairs)})
            print(f"step {state.global_step}: val first check balanced {b}", flush=True)

    return FirstCheck()


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────

def train(a, corpus: Path, out: Path) -> int:
    m, probs, rows = load(corpus)
    if not a.smoke and not (corpus / "TOKENS.json").exists():
        raise SystemExit(f"{corpus / 'TOKENS.json'} missing: run "
                         "`python sft/train_step.py --audit`")
    tokens = None if a.smoke else json.loads((corpus / "TOKENS.json").read_text(encoding="utf-8"))
    mid = SMOKE_MODEL if a.smoke else model_id(a.model)
    if tokens is not None:
        assert tokens["model"] == mid and tokens["sha256"] == m["sha256"], "TOKENS.json is stale"

    train_ids = [json.loads(x)["problem_id"]
                 for x in open(Path(m["source"]["corpus"]) / "sft_trace.jsonl", encoding="utf-8")
                 if json.loads(x)["split"] == "train"]
    order = problem_order(train_ids, a.seed)
    problem_hash = hashlib.sha256("\n".join(order).encode()).hexdigest()
    if a.seed == 0 and TRACE_RUN.exists():
        want = json.loads(TRACE_RUN.read_text(encoding="utf-8"))["order_sha256"]
        assert problem_hash == want, "not the trace arm's problem order"
    keep = set(train_ids[:a.limit]) if a.limit else None
    by_problem = collections.defaultdict(list)
    for r in rows["train"]:
        by_problem[r["problem_id"]].append(r)
    seq = [r for pid in order if keep is None or pid in keep
           for r in sorted(by_problem[pid], key=lambda r: r["k"])]
    val = val_subset(rows["val"])
    if keep is not None:
        vkeep = set(sorted({r["problem_id"] for r in val})[:a.limit])
        val = [r for r in val if r["problem_id"] in vkeep]
    firsts = [r for r in rows["val"] if r["cell"] == "first_check"][:a.limit]

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(mid)
    unique = {r["row_id"]: r for r in seq}
    # in file order, the order prompt_sha256 was taken in
    p_of = dict(zip((r["row_id"] for r in rows["train"]),
                    prompts(rows["train"], probs, None if a.limit else m)))
    enc = {rid: encode(tok, p_of[rid], r["target"]) for rid, r in unique.items()}
    vp = prompts(val, probs)
    venc = [encode(tok, p, r["target"]) for p, r in zip(vp, val)]
    if tokens is not None and not a.limit:
        tsum = sum(len(ids) - n for ids, n in enc.values())
        want = sum(s["target_sum"] for s in tokens["files"]["steps.jsonl"]["train"].values())
        assert tsum == want, "tokenisation differs from the token audit"
    data = [{"input_ids": enc[r["row_id"]][0],
             "labels": [-100] * enc[r["row_id"]][1] + enc[r["row_id"]][0][enc[r["row_id"]][1]:]}
            for r in seq]
    vdata = [{"input_ids": ids, "labels": [-100] * n + ids[n:]} for ids, n in venc]

    steps = math.ceil(len(data) / ROWS_PER_STEP)
    config = {"arm": "s2", "loss": "per_example_mean", "prompt_version": STEP_PROMPT_VERSION,
              "epochs": EPOCHS, "seed": a.seed, "lora": LORA, "lr": LR, "scheduler": "cosine",
              "warmup": WARMUP, "rows_per_step": ROWS_PER_STEP, "micro_batch": a.micro_batch,
              "limit": a.limit, "smoke": a.smoke,
              "val_subset_sha256": hashlib.sha256(
                  "\n".join(r["row_id"] for r in val).encode()).hexdigest()}
    manifest = {
        "model": mid, "code_rev": _git_rev(), "versions": versions(),
        "corpus": str(corpus), "sha256": m["sha256"],
        "tokens_json_sha256": None if a.smoke else _sha256(corpus / "TOKENS.json"),
        "config": config, "n_rows": {"train_seen": len(data), "val": len(vdata),
                                     "val_first_checks": len(firsts)},
        "kinds_seen": dict(collections.Counter(r["kind"] + (" (extra)" if r["extra"] else "")
                                               for r in seq)),
        "steps_planned": steps,
        "problem_order_sha256": problem_hash,
        "order_sha256": hashlib.sha256("\n".join(r["row_id"] for r in seq).encode()).hexdigest(),
        "status": "dry-run" if a.dry_run else "started",
    }
    print(f"{len(data)} rows seen in {steps} steps of {ROWS_PER_STEP}; val {len(vdata)} rows, "
          f"{len(firsts)} first checks; problem order {problem_hash[:12]}")
    if a.dry_run:
        print(json.dumps({k: v for k, v in manifest.items() if k != "versions"}, indent=1))
        return 0

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments,
                              set_seed)
    bf16 = torch.cuda.is_available()
    manifest.update(revision=revision(mid), cuda=torch.version.cuda,
                    gpu=torch.cuda.get_device_name(0) if bf16 else None)
    config["bf16"] = bf16
    out.mkdir(parents=True, exist_ok=True)
    mpath = out / "TRAINING_MANIFEST.json"
    if a.resume:
        old = json.loads(mpath.read_text(encoding="utf-8"))
        assert (old["config"], old["order_sha256"]) == (config, manifest["order_sha256"]), \
            "resuming a run with another configuration"
    _write(mpath, manifest)

    set_seed(a.seed)
    model = AutoModelForCausalLM.from_pretrained(
        mid, dtype=torch.bfloat16 if bf16 else torch.float32)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(**LORA, task_type="CAUSAL_LM"))
    items = [(step_prompt(probs[r["problem_id"]], "check", r["state"]), r["verdict"],
              probs[r["problem_id"]]) for r in firsts]
    args = TrainingArguments(
        output_dir=str(out), num_train_epochs=1, train_sampling_strategy="sequential",
        per_device_train_batch_size=a.micro_batch, per_device_eval_batch_size=a.micro_batch,
        gradient_accumulation_steps=ROWS_PER_STEP // a.micro_batch,
        learning_rate=LR, lr_scheduler_type="cosine", warmup_steps=WARMUP,
        bf16=bf16, gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        eval_strategy="steps", eval_steps=EVAL_EVERY, eval_on_start=True,
        save_strategy="steps", save_steps=EVAL_EVERY,
        logging_steps=5, report_to="none", seed=a.seed)
    trainer = per_example_trainer()(
        model=model, args=args, train_dataset=data, eval_dataset=vdata,
        data_collator=DataCollatorForSeq2Seq(tok, padding=True, pad_to_multiple_of=8,
                                             label_pad_token_id=-100),
        callbacks=[first_check_callback(tok, items)])
    t0 = time.time()
    trainer.train(resume_from_checkpoint=True if a.resume else None)
    last = trainer.state.global_step
    if not any("eval_loss" in h and h.get("step") == last for h in trainer.state.log_history):
        trainer.evaluate()                      # versions that do not evaluate the last step
    trainer.save_model(str(out / "adapter"))

    logged = [h["grad_norm"] for h in trainer.state.log_history if "grad_norm" in h]
    manifest.update(
        status="done", runtime_s=round(time.time() - t0), steps=trainer.state.global_step,
        peak_memory_gb=round(torch.cuda.max_memory_allocated() / 2**30, 1) if bf16 else None,
        clipped_share=round(sum(g > args.max_grad_norm for g in logged) / max(1, len(logged)), 3),
        log_history=trainer.state.log_history)
    _write(mpath, manifest)
    print(f"adapter -> {out / 'adapter'}  ({manifest['steps']} steps, {manifest['runtime_s']}s)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true", help="write corpus/v1-step/TOKENS.json")
    ap.add_argument("--out")
    ap.add_argument("--corpus", default="corpus/v1-step")
    ap.add_argument("--model", default="qwen2.5-7b")
    ap.add_argument("--micro-batch", type=int, default=MICRO,
                    help=f"rows per forward pass; the effective batch stays {ROWS_PER_STEP}")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None, help="first N train problems (smoke)")
    ap.add_argument("--smoke", action="store_true", help=f"{SMOKE_MODEL} on CPU; needs --limit")
    ap.add_argument("--dry-run", action="store_true", help="everything but the model")
    ap.add_argument("--resume", action="store_true", help="from the last checkpoint in --out")
    a = ap.parse_args(argv)

    corpus = Path(a.corpus)
    if a.audit:
        return audit(corpus, a.model)
    if not a.out:
        ap.error("--out is required (or --audit)")
    if a.smoke and not a.limit:
        ap.error("--smoke needs --limit")
    assert ROWS_PER_STEP % a.micro_batch == 0
    return train(a, corpus, Path(a.out))


if __name__ == "__main__":
    sys.exit(main())
