#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/31156927
# DOI: 10.6084/m9.figshare.31156927.v1 (data)
#   Ng H (2026). Nature connectedness, social dominance orientation, and support for marginalized
#   groups [Data set]. figshare.
# License: CC BY 4.0 (figshare)
# Data: data_cond.csv, 1,604 respondents (the deposit's README says 1,601 complete on all 28
#   "nodes"; 3 lack the policy items), each randomly shown nature ("HRHS") or urban ("URBAN")
#   images; data.csv is the same file without the condition column.
#
# Tables (all stored as answered; nothing reversed):
#   ng_2026_cns  -- Connectedness to Nature Scale, cns1-cns14, 1-5. cns4, cns12, cns14 are the
#     scale's reverse-keyed items (Mayer & Frantz 2004) and correlate negatively / near zero with the
#     rest here, i.e. not yet reversed.
#   ng_2026_sdo  -- Social Dominance Orientation, sdo1-sdo8, 1-7; sdo3/4/7/8 run against the rest
#     (con-trait items, unreversed).
#   ng_2026_policy_support -- five 1-7 items whose mean is the deposit's policy_support composite in
#     every row (fin_support_undoc, pos_impact_undoc, fin_support_lower_v_higher,
#     fin_support_lower_v_now, vaccine_priority_lower).
# Not shipped: pos_impact_citizen (a comparison item outside the composite); policy_support (composite);
#   the output*/mgm* files (estimated networks).
# treat: 1 = nature images (HRHS), 0 = urban images. id: row number. No demographics in the deposit.
# Item text: not shipped -- the deposit has variable names only; CNS and SDO are published
#   third-party scales, and the policy items' wording is in the (unpublished) paper.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/61390423"
POLICY = ["fin_support_undoc", "pos_impact_undoc", "fin_support_lower_v_higher",
          "fin_support_lower_v_now", "vaccine_priority_lower"]


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 1604
    assert (d[POLICY].mean(axis=1) - d["policy_support"]).abs().max() < 1e-6
    d["id"] = range(1, len(d) + 1)
    d["treat"] = d["condition"].map({"HRHS": 1, "URBAN": 0})
    assert d["treat"].notna().all()
    blocks = {
        "ng_2026_cns": ([f"cns{i}" for i in range(1, 15)], 5),
        "ng_2026_sdo": ([f"sdo{i}" for i in range(1, 9)], 7),
        "ng_2026_policy_support": (POLICY, 7),
    }
    used = {"Unnamed: 0", "condition", "policy_support", "pos_impact_citizen"}
    for name, (cols, top) in blocks.items():
        used |= set(cols)
        t = d[["id", "treat"] + cols].melt(id_vars=["id", "treat"], var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, top).all()
        t = t[["id", "item", "resp", "treat"]].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    assert used >= set(d.columns) - {"id", "treat"}, set(d.columns) - used


if __name__ == "__main__":
    main()
