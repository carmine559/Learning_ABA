"""Build the SFT corpus (tier spec v2) into corpus/<version>/.

    python build_corpus.py                      # corpus/v1, default sizes
    python build_corpus.py --out corpus/tiny --n-train 4 --n-val 2 --n-test 2 --n-heldout 2

See src/aba_corpus.py for the layout and the guarantees.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from src.aba_corpus import CorpusConfig, build


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    d = CorpusConfig()
    ap.add_argument("--out", default="corpus/v1")
    ap.add_argument("--seed", default=d.base_seed)
    ap.add_argument("--n-train", type=int, default=d.n_train,
                    help="per tier and class")
    ap.add_argument("--n-val", type=int, default=d.n_val)
    ap.add_argument("--n-test", type=int, default=d.n_test)
    ap.add_argument("--n-heldout", type=int, default=d.n_heldout,
                    help="per held-out tier and half")
    a = ap.parse_args(argv)

    cfg = CorpusConfig(base_seed=a.seed, n_train=a.n_train, n_val=a.n_val,
                       n_test=a.n_test, n_heldout=a.n_heldout)
    t0 = time.time()
    m = build(cfg, Path(a.out))
    print(f"built {a.out} in {time.time() - t0:.0f}s")
    for gate, ok in m["gates"].items():
        print(f"  [{'ok' if ok else 'FAIL'}] {gate}")
    return 0 if all(m["gates"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
