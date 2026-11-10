#!/usr/bin/env python3
"""Mapping check for lam_2015_gses (gsesK = GSE item K, positional).

What could pin the order: a polarity split, a subscale split, or per-item
statistics printed by the article. The GSE has none of these. It is one
factor ("The scale is unidimensional", engscal.htm), every item is positively
worded ("No recoding"), and the article (pone.0142620) reports only the CGSES
total and its alpha, no per-item figures. This script confirms the first two on
the staged responses -- all 45 inter-item correlations positive and of similar
size -- so a permutation of the ten stems would leave every statistic
unchanged. Result: NO_ROUTE (recorded as such in mapping_verification.csv);
the script fails only if the data contradict the one-polarity, one-factor
premise, which would make the positional assumption itself suspect.

Run: RESP_DIR=<dir> python3 verify_lam_2015.py
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RESP_DIR = Path(os.environ.get("RESP_DIR", Path(__file__).resolve().parent.parent / "irw_output"))


def main():
    d = pd.read_csv(RESP_DIR / "lam_2015_gses.csv")
    ok = True
    for study, g in d.groupby("cov_study"):
        w = g.pivot_table(index="id", columns="item", values="resp")
        w = w[[f"gses{k}" for k in range(1, 11)]]
        c = w.corr().values
        off = c[np.triu_indices(10, 1)]
        ev = np.sort(np.linalg.eigvalsh(c))[::-1]
        print(f"stage {study}: n={len(w)}; inter-item r {off.min():.2f}..{off.max():.2f}; "
              f"eigenvalues {ev[0]:.2f}, {ev[1]:.2f} (first/second {ev[0] / ev[1]:.1f})")
        ok &= bool(off.min() > 0) and ev[0] / ev[1] > 3
    print("one polarity, one dominant factor:", ok)
    print("no route distinguishes item K from item J under these conditions -> NO_ROUTE")
    print("VERDICT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
