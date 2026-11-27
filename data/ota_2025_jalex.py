#!/usr/bin/env python3
# JALEX: online visual lexical decision on 11,472 Japanese strings (katakana
# and kanji words, and nonwords), trial level.
# Ota, N., & Mochizuki, M. (2025). JALEX: Japanese version of lexical decision
# database. Frontiers in Language Sciences. doi:10.3389/flang.2024.1506509
# Data: OSF https://osf.io/qr2sg, CC BY-NC 4.0 (license.txt; the OSF licence
# field says "Other"). File rawData.csv; column meanings from
# JALEX_processing_v2.Rmd ("Trial RT" is in seconds; items 11473-11492 are
# practice words).
#
# rawData.csv also holds non-trial rows (the ENDCORE and Psi-Q questionnaire
# responses and demographics) with an empty Target; only the trial rows are
# used, and demographics are taken from the person's other rows.
#
# Layout (person-first):
#   id   = the person's position (1-1652) in the sorted list of source
#          `participant` codes. The source code is the session start time to the
#          millisecond (e.g. 20240521113724842), so it is re-keyed.
#   item = `Target`, the string shown; nonwords are items
#   resp = `Trial Accuracy` (1/0; equals Trial Response == CorrResp). A trial
#          with no key press within 2 s (3,071 trials; RT recorded as 2.0) is
#          0, with rt empty.
#   rt   = `Trial RT` in seconds
#   trial_number = position among the person's trials, practice included
#          (the file's row order, which is presentation order)
#   trial_list   = `List`
#   itemcov_lexicality = word / nonword (`Type`)
#   cov_sex, cov_age, cov_handedness, cov_education (source labels;
#   "Unanswered" kept as given). `Language` is Japanese for everyone and is
#   not carried.
# Practice trials (Item 11473-11492) are dropped.
#
# Usage: python3 ota_2025_jalex.py <rawData.csv> <out_dir>
import os
import sys

import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "rawData.csv"
out_dir = sys.argv[2] if len(sys.argv) > 2 else "."

cols = ["participant", "List", "Item", "Target", "Type", "CorrResp", "Trial Response",
        "Trial Accuracy", "Trial RT", "Sex", "Age", "Handedness", "Education"]
d = pd.read_csv(src, usecols=cols, keep_default_na=False, na_values=["", "NA"],
                low_memory=False)
demo = d.groupby("participant")[["Sex", "Age", "Handedness", "Education"]].first()
assert (d.groupby("participant")[["Sex", "Age", "Handedness", "Education"]].nunique() == 1).all().all()

t = d[d.Target.notna()].copy()
t["trial_number"] = t.groupby("participant").cumcount() + 1
t = t[~t.Item.between(11473, 11492)]
assert t["Trial Accuracy"].notna().all()
assert not t.duplicated(["participant", "Target"]).any()
assert (t.groupby("Target").Type.nunique() == 1).all()
assert ((t["Trial Response"] == t.CorrResp).astype(int) == t["Trial Accuracy"]).all()
noresp = t["Trial Response"].isna()
assert (t.loc[noresp, "Trial RT"] == 2.0).all() and (t.loc[noresp, "Trial Accuracy"] == 0).all()

key = {p: i + 1 for i, p in enumerate(sorted(t.participant.unique()))}
out = pd.DataFrame({
    "id": t.participant.map(key).astype(int),
    "item": t.Target.astype(str),
    "resp": t["Trial Accuracy"].astype(int),
    "rt": np.where(noresp, np.nan, t["Trial RT"]),
    "trial_number": t.trial_number.astype(int),
    "trial_list": t.List.astype(int),
})
for s, c in [("Sex", "cov_sex"), ("Age", "cov_age"), ("Handedness", "cov_handedness"),
             ("Education", "cov_education")]:
    out[c] = t.participant.map(demo[s]).values
out["itemcov_lexicality"] = t.Type.str.lower().values
out = out.sort_values(["id", "trial_number"]).reset_index(drop=True)

name = "ota_2025_jalex"
# The shared checks (irw_validate.contract `no_validator`): fails block,
# warnings are printed (concentrated 0/1 responses are expected here).
_checks = run_qc(out)
_fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
assert not _fails, _fails
for _c in _checks:
    if _c.status == "warn":
        print(f"  [qc warn] {_c.name}: {_c.detail[:120]}")
os.makedirs(out_dir, exist_ok=True)
out.to_csv(os.path.join(out_dir, name + ".csv"), index=False)
print(f"{name}: rows={len(out)} ids={out.id.nunique()} items={out.item.nunique()} "
      f"resp={out.resp.min()}-{out.resp.max()} rt_empty={out.rt.isna().sum()} "
      f"rt={out.rt.min():.3f}-{out.rt.max():.3f}")
