# Experiment set 00 — Preliminary API-era explorations

| | |
| --- | --- |
| **Date** | May–June 2026 (several sessions) |
| **Backends** | Groq API (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`) |
| **Prompt version** | pre-v1 (evolving; includes the later-removed `fewshot` mode) |
| **Dataset** | 3 builtin problems (nixon_diamond, flies, tax_law) ± early single-path synthetics; **before** the stratified benchmark suite existed |

## Contents

| Folder | What it is |
| --- | --- |
| `groq_70b/` | Llama-3.3-70B via Groq on the builtin problems (anonymised); includes an early `algorithm`-mode attempt |
| `groq_8b/` | Llama-3.1-8B via Groq, direct mode only |
| `with_synthetic/` | Early run with `--n-synthetic` single-path problems (direct gen@k 0.74, cot 0.39) |
| `early_builtin/` | Accumulated builtin-problem outputs: graded semantics results, framework exports, figures; includes obsolete `fewshot`-era JSONLs |

## Role in the thesis

These runs shaped the pipeline rather than answering the research question:
they exposed API rate-limit constraints (which motivated the local/cluster
backend), parser robustness issues, the need for anonymisation, and the need
for a stratified benchmark. **Numbers here are NOT comparable** with sets
01/02: different dataset, different prompt generations, different metrics
(no `clean@k`, no tiers).

Kept for transparency and to document the project's evolution.
