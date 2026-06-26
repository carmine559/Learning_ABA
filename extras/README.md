# extras/ — reporting utilities

These modules turn the raw Task-1 results into human-readable artefacts (figures,
catalogues, narratives). They are kept out of `src/` so the three-task spine stays
clean; `main.py` imports them lazily during the report/export steps.

| Module | What it does | Triggered by |
| --- | --- | --- |
| `aba_visualization.py` | Publication figures (PDF) | always, in the report step |
| `aba_export.py` | Dump learned frameworks to JSONL / Markdown / CSV | `--export` |
| `aba_explain.py` | Mechanism tags + natural-language narratives per sample | `--export` |
