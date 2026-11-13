#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GXVPSM (Harvard Dataverse)
# DOI: 10.7910/DVN/GXVPSM (data)
#   Dey M, Dewan MF, Khan MA, et al. (2024). Food Safety Knowledge Attitudes and Practices (KAP)
#   [Data set]. Harvard Dataverse. USAID Feed the Future Food Safety Innovation Lab, Bangladesh.
# License: CC0 1.0 (Dataverse)
# Data: three KoBo surveys of the Bangladesh fish value chain, July-September 2023, interviewer
#   administered (English forms; questionnaires deposited as PDF): 600 consumers (6 districts),
#   240 producers (4 districts), 300 traders (6 districts). Each file has its own codebook
#   (*-codebook.csv: variable, definition, value labels), read here by variable name; downloaded
#   with format=original.
#
# Tables, one per sample x section, item = the deposit's variable name (K1.., A1.., P1..):
#   dey_2024_fish_{consumer,producer,trader}_knowledge  -- 1 Not at all .. 5 To a great extent
#   dey_2024_fish_{consumer,producer,trader}_attitudes  -- 1 Strongly disagree .. 5 Strongly agree
#   dey_2024_fish_{consumer,producer,trader}_practices  -- 1 Never .. 5 Always, EXCEPT the items
#     whose codebook labels run 5 = Never .. 1 = Always (consumer P8 P9 P12 P13; producer P11 P12;
#     trader P1 P2 P3 P4 P6 P15): the depositors stored those undesirable practices reverse-coded,
#     and they are shipped as stored (higher = safer practice throughout).
#   The three samples answered different item sets (same codes, different questions), so they are
#   not stacked.
# Covariates: every other codebook variable, value labels applied (age, sex, education, occupation,
#   family size, earners, income group, fish-consumption days/week, training, advice/contact,
#   production or trading experience, pond size). District is dropped (geographic code).
#   Consumer `advice` has 40 cells coded 2, a value the codebook does not define; set to missing.
# id: row number within each sample file.
# Item text: see make_itemtext_dey_2024.py / BATCH_LOG.
import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
API = "https://dataverse.harvard.edu/api/access/datafile/{}?format=original"
FILES = {  # sample: (data file id, codebook file id, n)
    "consumer": (10227465, 10227466, 600),
    "producer": (10227464, 10227461, 240),
    "trader": (10227463, 10227462, 300),
}
SECTIONS = {"K": "knowledge", "A": "attitudes", "P": "practices"}
COVNAME = {"earning_member": "earners", "consumption_frequency": "fish_days_per_week",
           "pond_size": "pond_size_decimal"}


def get(fid):
    r = requests.get(API.format(fid), timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def is_item(v):
    return v[0] in SECTIONS and v[1:].isdigit()


def main():
    for sample, (fid, cbid, n) in FILES.items():
        d, cb = get(fid), get(cbid)
        assert len(d) == n and list(cb["variable"]) == list(d.columns), sample
        d["id"] = range(1, n + 1)
        covs = []
        for _, r in cb.iterrows():
            v = r["variable"]
            if is_item(v) or v == "district":
                continue
            c = "cov_" + COVNAME.get(v, v)
            if isinstance(r["categories"], str) and r["categories"].strip():
                lab = {int(k): s for k, s in json.loads(r["categories"]).items()}
                bad = ~d[v].isin(list(lab)) & d[v].notna()
                if bad.any():
                    print(f"{sample} {v}: {bad.sum()} undefined code(s) {sorted(d.loc[bad, v].unique())} -> missing")
                d[c] = d[v].map(lab)
            else:
                d[c] = d[v]
            covs.append(c)
        for pre, sec in SECTIONS.items():
            items = [v for v in cb["variable"] if is_item(v) and v[0] == pre]
            for v in items:
                lab = json.loads(cb.set_index("variable").at[v, "categories"])
                assert sorted(map(int, lab)) == [1, 2, 3, 4, 5], (sample, v)
            t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
            t = t.dropna(subset=["resp"])
            t["resp"] = t["resp"].astype(int)
            assert t["resp"].between(1, 5).all()
            t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
            fails = [c for c in run_qc(t) if c.status == "fail"]
            assert not fails, (sample, sec, fails)
            name = f"dey_2024_fish_{sample}_{sec}"
            t.to_csv(OUT / f"{name}.csv", index=False)
            print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
