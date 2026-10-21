"""Build the SFT corpus (tier spec v2) into corpus/<version>/.

    python sft/build_corpus.py                      # corpus/v1, default sizes
    python sft/build_corpus.py --out corpus/tiny --n-train 4 --n-val 2 --n-test 2 --n-heldout 2 --no-table1
    python sft/build_corpus.py --permute-from corpus/v1 --out corpus/v1-permuted
    python sft/build_corpus.py --steps-from corpus/v1 --out corpus/v1-step

The paper's Table 1 set needs the Zenodo release zip (GPL, not in the repo):
it is downloaded to --zenodo-zip on first use and md5-checked.

--permute-from generates nothing: it re-poses the source's test and held-out
problems under a seeded predicate-name derangement, an evaluation-only corpus
(src/aba_corpus.build_permuted).

--steps-from generates nothing either: it harvests the step rows of arm S2 from
the source's train and val problems, gated on every source and --permuted
problem (src/aba_corpus.build_steps).

See src/aba_corpus.py for the layout and the guarantees.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from src.aba_corpus import CorpusConfig, build, build_permuted, build_steps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    d = CorpusConfig()
    ap.add_argument("--out", default=None,
                    help="default corpus/v1; required with --permute-from")
    ap.add_argument("--permute-from", metavar="SOURCE",
                    help="built corpus whose test and held-out problems to re-pose")
    ap.add_argument("--steps-from", metavar="SOURCE",
                    help="built corpus whose train and val problems to harvest step rows from")
    ap.add_argument("--permuted", default="corpus/v1-permuted",
                    help="with --steps-from: the permuted corpus the gates also run on")
    ap.add_argument("--seed", default=d.base_seed)
    ap.add_argument("--n-train", type=int, default=d.n_train,
                    help="per tier and class")
    ap.add_argument("--n-val", type=int, default=d.n_val)
    ap.add_argument("--n-test", type=int, default=d.n_test)
    ap.add_argument("--n-heldout", type=int, default=d.n_heldout,
                    help="per held-out tier and half")
    ap.add_argument("--zenodo-zip",
                    default="corpus/zenodo/aba_asp-ASP-ABAlearn_B.zip")
    ap.add_argument("--no-table1", action="store_true",
                    help="leave out the paper's Table 1 set")
    a = ap.parse_args(argv)

    t0 = time.time()
    if a.permute_from or a.steps_from:
        if a.out is None:
            ap.error("--permute-from and --steps-from need --out")
        m = (build_permuted(Path(a.permute_from), Path(a.out)) if a.permute_from else
             build_steps(Path(a.steps_from), Path(a.permuted), Path(a.out)))
    else:
        a.out = a.out or "corpus/v1"
        cfg = CorpusConfig(base_seed=a.seed, n_train=a.n_train, n_val=a.n_val,
                           n_test=a.n_test, n_heldout=a.n_heldout)
        m = build(cfg, Path(a.out), None if a.no_table1 else Path(a.zenodo_zip))
    print(f"built {a.out} in {time.time() - t0:.0f}s")
    for gate, ok in m["gates"].items():
        print(f"  [{'ok' if ok else 'FAIL'}] {gate}")
    if a.permute_from:
        g = m["gold_equal_renamed"]
        print(f"  gold equal to the source gold renamed: endpoint "
              f"{g['endpoint_target']}/{g['n']}, trace {g['trace_target']}/{g['n']}")
    return 0 if all(m["gates"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
