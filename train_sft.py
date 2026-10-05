"""LoRA SFT of one arm on the corpus: endpoint or trace, identical otherwise.

    python train_sft.py --audit                  # once, before any run: TOKENS.json
    python train_sft.py --arm endpoint --out runs/sft_endpoint
    python train_sft.py --arm trace    --out runs/sft_trace
    python train_sft.py --arm endpoint --match tokens --out runs/sft_endpoint_tokens

Arm matching (MANIFEST `arm_matching`). Primary: same train problems in the same
order, same epochs, batch and schedule. The order is drawn here, one seeded
permutation per epoch (`schedule`), and read by a sequential sampler, so it
never depends on torch's RNG; its hash goes into TRAINING_MANIFEST.json and
must be equal across the two arms. Secondary (`--match tokens`): the endpoint
arm runs TOKENS.json `secondary_endpoint_epochs`; its order extends the
primary one, epoch for epoch.

LoRA r=16, alpha=32, dropout 0.05 on every linear projection; bf16; AdamW at
2e-4, cosine, 3% warmup; effective batch 16; loss on the target tokens only
(`src/aba_train.encode`). Val loss every half epoch, from step 0; it is not
comparable across arms, whose targets differ.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

from src.aba_corpus import _sha256
from src.aba_tracelog import _git_rev
from src.aba_train import (
    ARMS, EPOCHS, encode, load_audit, model_id, revision, rows, schedule,
    token_audit, versions,
)

LORA = {"r": 16, "lora_alpha": 32, "lora_dropout": 0.05, "target_modules": "all-linear"}
LR, WARMUP, BATCH = 2e-4, 0.03, 16


def _write(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=1) + "\n", encoding="utf-8")


def audit(corpus: Path, model: str) -> int:
    path = corpus / "TOKENS.json"
    if path.exists():
        raise SystemExit(f"{path} exists: the ratio is fixed once; delete it only "
                         "if the corpus or the model changed")
    t = token_audit(corpus, model)
    _write(path, t)
    m = t["arm_matching"]
    print(f"wrote {path}\n  longest row {t['longest_row']} tokens (context {t['context']})"
          f"\n  target tokens on train: trace {m['trace_target_tokens_train']}, "
          f"endpoint {m['endpoint_target_tokens_train']}, ratio {m['ratio']}"
          f"\n  secondary endpoint epochs {m['secondary_endpoint_epochs']}"
          f"\n  max_new_tokens {t['max_new_tokens']}")
    return 0


def train(a, corpus: Path, out: Path) -> int:
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq,
                              Trainer, TrainingArguments, set_seed)

    tokens_json = load_audit(corpus, a.model)
    mid, name = model_id(a.model), f"sft_{a.arm}.jsonl"
    tok = AutoTokenizer.from_pretrained(mid)
    data, ids_of, target_tokens = {}, {}, {}
    for split in ("train", "val"):
        rs = rows(corpus, name, split)[:a.limit]
        enc = [encode(tok, r["prompt"], r["target"]) for r in rs]
        data[split] = [{"input_ids": ids, "labels": [-100] * n + ids[n:]} for ids, n in enc]
        ids_of[split] = [r["problem_id"] for r in rs]
        target_tokens[split] = sum(len(ids) - n for ids, n in enc)
        if a.limit is None:
            assert target_tokens[split] == \
                tokens_json["files"][name][split]["target"]["target_sum"], \
                "tokenisation differs from the token audit"

    epochs = (tokens_json["arm_matching"]["secondary_endpoint_epochs"]
              if a.match == "tokens" and a.arm == "endpoint" else EPOCHS)
    order = schedule(len(data["train"]), epochs, a.seed)
    per_epoch = len(data["train"]) / BATCH
    bf16 = torch.cuda.is_available()
    config = {"arm": a.arm, "match": a.match, "epochs": epochs, "seed": a.seed,
              "lora": LORA, "lr": LR, "scheduler": "cosine", "warmup": WARMUP,
              "batch": BATCH, "micro_batch": a.micro_batch, "bf16": bf16,
              "limit": a.limit}
    manifest = {
        "model": mid, "revision": revision(mid), "code_rev": _git_rev(),
        "versions": versions(), "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if bf16 else None,
        "corpus": str(corpus), "sha256": {name: tokens_json["sha256"][name]},
        "tokens_json_sha256": _sha256(corpus / "TOKENS.json"),
        "config": config,
        "n": {s: len(v) for s, v in data.items()}, "rows_seen": len(order),
        "steps_per_epoch": per_epoch,     # log_history's `epoch` counts the whole run as 1
        "target_tokens": target_tokens,
        "order_sha256": hashlib.sha256(
            "\n".join(ids_of["train"][i] for i in order).encode()).hexdigest(),
        "status": "started",
    }
    out.mkdir(parents=True, exist_ok=True)
    mpath = out / "TRAINING_MANIFEST.json"
    if a.resume:
        old = json.loads(mpath.read_text(encoding="utf-8"))
        assert (old["config"], old["order_sha256"]) == (config, manifest["order_sha256"]), \
            "resuming a run with another configuration"
    _write(mpath, manifest)

    set_seed(a.seed)                     # the LoRA initialisation, equal across arms
    model = AutoModelForCausalLM.from_pretrained(
        mid, dtype=torch.bfloat16 if bf16 else torch.float32)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(**LORA, task_type="CAUSAL_LM"))
    args = TrainingArguments(
        output_dir=str(out), num_train_epochs=1, train_sampling_strategy="sequential",
        per_device_train_batch_size=a.micro_batch,
        per_device_eval_batch_size=a.micro_batch,
        gradient_accumulation_steps=BATCH // a.micro_batch,
        learning_rate=LR, lr_scheduler_type="cosine", warmup_steps=WARMUP,
        bf16=bf16, gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        eval_strategy="steps", eval_steps=max(1, round(per_epoch / 2)), eval_on_start=True,
        save_strategy="steps", save_steps=max(1, math.ceil(per_epoch)),
        logging_steps=5, report_to="none", seed=a.seed)
    trainer = Trainer(
        model=model, args=args,
        train_dataset=[data["train"][i] for i in order], eval_dataset=data["val"],
        data_collator=DataCollatorForSeq2Seq(tok, padding=True, pad_to_multiple_of=8,
                                             label_pad_token_id=-100))
    t0 = time.time()
    trainer.train(resume_from_checkpoint=True if a.resume else None)
    trainer.save_model(str(out / "adapter"))

    manifest.update(
        status="done", runtime_s=round(time.time() - t0), steps=trainer.state.global_step,
        peak_memory_gb=round(torch.cuda.max_memory_allocated() / 2**30, 1) if bf16 else None,
        log_history=trainer.state.log_history)
    _write(mpath, manifest)
    print(f"adapter -> {out / 'adapter'}  ({manifest['steps']} steps, "
          f"{manifest['runtime_s']}s)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audit", action="store_true", help="write corpus/<v>/TOKENS.json")
    ap.add_argument("--arm", choices=ARMS)
    ap.add_argument("--out")
    ap.add_argument("--corpus", default="corpus/v1")
    ap.add_argument("--model", default="qwen2.5-7b")
    ap.add_argument("--match", choices=("steps", "tokens"), default="steps",
                    help="primary (steps) or secondary (tokens) arm matching")
    ap.add_argument("--micro-batch", type=int, default=2,
                    help="rows per forward pass; the effective batch stays 16")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None, help="first N rows per split "
                                                            "(smoke test)")
    ap.add_argument("--resume", action="store_true", help="from the last checkpoint in --out")
    a = ap.parse_args(argv)

    corpus = Path(a.corpus)
    if a.audit:
        return audit(corpus, a.model)
    if not (a.arm and a.out):
        ap.error("--arm and --out are required (or --audit)")
    assert BATCH % a.micro_batch == 0
    return train(a, corpus, Path(a.out))


if __name__ == "__main__":
    sys.exit(main())
