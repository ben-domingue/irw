#!/usr/bin/env python3
"""Verify the within-construct order mapping of
pytlikzillig_2017_institutional_trust (and say what can and cannot be
checked for pytlikzillig_2017_dispositional_trust).

Checks, on the staged response table (survey 1 only, 1 = strongly disagree):
 1. Polarity. The appendix's Bias block has exactly one positively-worded
    item, its 4th ("... can be trusted to make decisions that are right for
    the entire community"), and the authors' SAS reverse-scores exactly PfI4.
    So PfI4 must correlate POSITIVELY with the trustworthiness items and
    NEGATIVELY with PfI1-3 and Cyn1-4, which in turn correlate negatively with
    the trustworthiness items. A within-Bias permutation putting the positive
    item anywhere else would break this.
 2. Block structure. Mean |r| within construct vs between constructs, per
    target (NDNR_, NRD_). Constructs are known to be highly correlated
    (article S2 Note G), so this is corroborating, not decisive.
 3. Dispositional trust: all nine items positively worded and loading on one
    factor (S2 Note H); reported for completeness, no route pins the order.

Run: RESP_DIR=<dir> python3 verify_pytlikzillig_2017.py
"""
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RESP_DIR = Path(os.environ["RESP_DIR"])


def wide(table):
    d = pd.read_csv(RESP_DIR / f"{table}.csv")
    d = d[d["wave"] == 1]
    return d.pivot_table(index="id", columns="item", values="resp")


def main():
    w = wide("pytlikzillig_2017_institutional_trust")
    c = w.corr()
    ok = True
    for pre in ("NDNR", "NRD"):
        cols = [x for x in w.columns if x.startswith(pre + "_")]
        neg = [f"{pre}_PfI{i}" for i in (1, 2, 3)] + [f"{pre}_Cyn{i}" for i in range(1, 5)]
        pos = [x for x in cols if x not in neg + [f"{pre}_PfI4"]]
        p4 = f"{pre}_PfI4"
        r_p4_pos = c.loc[p4, pos].mean()
        r_p4_neg = c.loc[p4, neg].mean()
        r_neg_pos = c.loc[neg, pos].values.mean()
        print(f"{pre}: PfI4 vs trustworthiness items mean r = {r_p4_pos:+.2f}; "
              f"PfI4 vs PfI1-3/Cyn mean r = {r_p4_neg:+.2f}; PfI1-3/Cyn vs trustworthiness mean r = {r_neg_pos:+.2f}")
        for i in (1, 2, 3):
            pi = f"{pre}_PfI{i}"
            print(f"    {pi}: vs trustworthiness mean r = {c.loc[pi, pos].mean():+.2f}")
            ok &= c.loc[pi, pos].mean() < 0
        ok &= r_p4_pos > 0 and r_p4_neg < 0 and r_neg_pos < 0

        cons = {}
        for x in cols:
            cons.setdefault(re.sub(r"\d+$", "", x), []).append(x)
        within, between = [], []
        a = c.loc[cols, cols].abs()
        for i, x in enumerate(cols):
            for y in cols[i + 1:]:
                (within if re.sub(r"\d+$", "", x) == re.sub(r"\d+$", "", y) else between).append(a.loc[x, y])
        print(f"    block structure: mean |r| within construct {np.mean(within):.2f}, between {np.mean(between):.2f}")
        hits = 0
        for k, xs in cons.items():
            for x in xs:
                own = np.mean([a.loc[x, y] for y in xs if y != x]) if len(xs) > 1 else np.nan
                best = max((np.mean([a.loc[x, y] for y in ys if y != x]), kk) for kk, ys in cons.items() if len([y for y in ys if y != x]))
                hits += best[1] == k
        print(f"    items whose highest mean |r| is with their own construct: {hits}/{len(cols)}")

    d = wide("pytlikzillig_2017_dispositional_trust").corr()
    off = d.values[np.triu_indices(9, 1)]
    print(f"dispositional trust: inter-item r {off.min():.2f}..{off.max():.2f} (one polarity, one factor; order not testable)")
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
