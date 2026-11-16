#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/dkm73c7s6z/1
# DOI: 10.17632/dkm73c7s6z.1 (data)
#   Li J, Zhang Y (2025). Dataset for "Indoor soundscape perception and soundscape appropriateness
#   assessment while working from home and relaxing at home" [Data set]. Mendeley Data, V1.
# License: CC BY 4.0 (Mendeley Data)
# Data: Data n=247.sav, 247 people working from home in 37 Chinese cities during the COVID-19
#   lockdown. Every item carries an English .sav variable label and value labels.
# Tables (item = the .sav variable name; resp as stored, anchors from the value labels):
#   li_2025_indoor_sound_sources -- perceived prominence of 10 sound sources, rated once for the room
#     used for working from home (WAHS*) and once for the rooms used for relaxing (RAHS*), 1 Not at
#     all .. 5 Dominates completely (20 items).
#   li_2025_indoor_soundscape_attributes -- 8 indoor soundscape attributes (comfortable, full of
#     content, private, engaging, annoying, empty, uncontrolled, detached) for the same two settings,
#     1 Strongly disagree .. 5 Strongly agree (16 items; the RAH items' labels repeat the WAH wording).
#   li_2025_noise_sensitivity -- NS1-NS5, 1 Totally disagree .. 7 Totally agree (NS5 is worded in the
#     non-sensitive direction; as answered).
# Covariates (value labels): cov_sex, cov_education, cov_age.
# Not shipped: work-content ratings (CW1-6), room choices, the two single appropriateness questions,
#   housing items, completion time.
# Item text: not shipped -- the English labels are attribute names ("WAHsoundscape perception--
#   comfortable") rather than the administered (Chinese) wording.
import io
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/dkm73c7s6z/files/"
       "70ee1814-8069-4741-8107-1819a063b165/file_downloaded")
SRC = ["Stn", "Soemn", "Snat", "Spsar", "Spyh", "She", "Sun", "Snn", "Sps", "Sen"]
ATT_W = ["comfortable", "fullofcontent", "private", "engaging", "annoying", "empty", "uncontrolled", "detached"]
ATT_R = ["comfortable", "content", "private", "engaging", "annoying", "empty", "uncontrolled", "detached"]
TABLES = {
    "li_2025_indoor_sound_sources": ([f"WAH{s}" for s in SRC] + [f"RAH{s}" for s in SRC], (1, 5)),
    "li_2025_indoor_soundscape_attributes": ([f"WAH{a}" for a in ATT_W] + [f"RAH{a}" for a in ATT_R], (1, 5)),
    "li_2025_noise_sensitivity": ([f"NS{i}" for i in range(1, 6)], (1, 7)),
}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':
        c = requests.get(json.loads(c)["url"], timeout=120).content
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(c)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 247
    vl = meta.variable_value_labels
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = d["Sex"].map(vl["Sex"])
    d["cov_education"] = d["Education"].map(vl["Education"])
    d["cov_age"] = d["Age"]
    covs = ["cov_sex", "cov_education", "cov_age"]
    for name, (items, (lo, hi)) in TABLES.items():
        assert all(i in d for i in items), [i for i in items if i not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
