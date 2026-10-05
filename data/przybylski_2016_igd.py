#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5028771
# DOI: 10.7717/peerj.2401
#   "Mischievous responding in Internet Gaming Disorder research"
#   (Przybylski, 2016), PeerJ 4:e2401.
# Data: PeerJ supplementary files, fetched from the Europe PMC supplementaryFiles
#       zip: peerj-04-2401-s001.jasp (Study 1, 1,899 x 22) and
#       peerj-04-2401-s002.jasp (Study 2, 10,009 x 23). A .jasp file is a zip;
#       its data.bin holds the columns back to back (int32 level codes for
#       nominal columns, float64 for scale ones, in metadata.json field order)
#       and xdata.json maps level codes to labels. s003.sps is the analysis
#       syntax. The OSF deposit the paper cites (osf.io/wvezd, reached via a
#       view_only link) has no licence; the data shipped here are the article's
#       own supplementary files, which carry the article's licence.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`).
#
# Item text: not shipped. Variable and value labels are both bare: the item
#   columns are named by DSM-5 criterion (preoccupation, withdrawl [sic], ...)
#   with value labels "0"/"1" only. The paper describes "an indicator checklist"
#   in line with DSM-5 guidance but does not print the wording; it is in the
#   parent project, Przybylski, Weinstein & Murayama (2017), Am J Psychiatry
#   174(3):230-236.
#
# Design: Google Surveys, April-June 2015. Study 1 = UK adults 18+; Study 2 =
# 18-24 year-olds in four national cohorts (US, CA, UK, DE). Each IGD indicator
# is a checklist option, 1 = endorsed, 0 = not endorsed. Study 2 adds a tenth
# option, `distress` (the DSM-5 clinically-significant-distress criterion); the
# other nine are the same columns in both studies, so the two are one table
# with cov_study, ids prefixed s1_/s2_.
#
# Table:
#   przybylski_2016_igd  9 DSM-5 IGD indicators (+ distress in Study 2), 0/1
#
# Rows left out:
#   * Non-players (player = 0: 282 in Study 1, 1,938 in Study 2). Every one of
#     them is 0 on every indicator -- including the 54 who failed the
#     "Semeron Online" sham-game check, a group that endorses indicators at
#     about twice the base rate elsewhere -- so the checklist was evidently not
#     shown to them and their zeros are structural, not responses.
#   * Study 2 duplicate block: Nation 1 (labelled the US cohort) contains 1,258
#     respondents whose Geography is Canadian and who appear again, identical
#     in every column except Nation (same Google UserID, same timestamp, same
#     answers), in Nation 2 (the Canadian cohort). Each is kept once, under
#     Canada. UserID is otherwise unique within and across studies.
#
# UserID (a Google Surveys respondent id) is a platform participant id: it is
# not shipped; id is the row index. Geography is cut to country-region (the
# deposit carries city for some rows); TimeUTC is not shipped. Mischievous
# responders are kept and flagged (cov_mischievous) -- the flag is the paper's
# point. indicator_count is an author composite (it omits `risking` and
# `distress`) and is skipped.

import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "przybylski_2016"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5028771/supplementaryFiles"

IGD9 = ["preoccupation", "withdrawl", "tolerance", "nocontrol", "continuing",
        "misleading", "escaping", "givingup", "risking"]
COUNTRY = {"US": "US", "CA": "Canada", "UK": "UK", "DE": "Germany"}
SKIP = {
    "UserID": "Google Surveys platform respondent id (replaced by row index)",
    "TimeUTC": "submission timestamp, not shipped",
    "Nation": "cohort code; replaced by cov_country from Geography (see header)",
    "Geography": "carried as cov_region (country-region only)",
    "sex": "recode of Gender (asserted)",
    "player": "used to drop non-players (see header)",
    "indicator_count": "author composite of the indicators",
}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / "supp.zip"
    if not z.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z.write_bytes(r.content)
    return zipfile.ZipFile(z)


def read_jasp(blob):
    j = zipfile.ZipFile(io.BytesIO(blob))
    meta = json.loads(j.read("metadata.json"))["dataSet"]
    labels = json.loads(j.read("xdata.json"))
    raw = j.read("data.bin")
    n, off, out = meta["rowCount"], 0, {}
    for f in meta["fields"]:
        if f["measureType"] == "Continuous":
            v = np.frombuffer(raw, dtype="<f8", count=n, offset=off)
            off += 8 * n
        else:
            codes = np.frombuffer(raw, dtype="<i4", count=n, offset=off)
            off += 4 * n
            lab = {int(k): s for k, s in labels.get(f["name"], {}).get("labels", [])}
            v = [lab[int(c)] for c in codes]   # KeyError = unexpected code
        out[f["name"]] = v
    assert off == len(raw), (off, len(raw))
    return pd.DataFrame(out)


def prep(d, study, items):
    d = d.copy()
    for c in items + ["player", "mischievous"]:
        d[c] = d[c].astype(int)
    assert set(d.columns) == set(items) | set(SKIP) | {
        "PublisherCategory", "Gender", "Age", "UrbanDensity", "Income",
        "mischievous"}, set(d.columns)
    assert d["Gender"].isin(["Female", "Male"]).all()
    # non-players: never endorse anything
    assert (d.loc[d["player"] == 0, items].sum(axis=1) == 0).all()
    d = d[d["player"] == 1].copy()
    d["cov_study"] = study
    d["cov_country"] = d["Geography"].str[:2].map(COUNTRY)
    assert d["cov_country"].notna().all()
    d["cov_region"] = d["Geography"].str.split("-").str[:2].str.join("-")
    d["cov_gender"] = d["Gender"].str.lower()
    d["cov_age_band"] = d["Age"]
    d["cov_mischievous"] = d["mischievous"]
    na = {"Unknown": np.nan, "I prefer not to say": np.nan}
    d["cov_income"] = d["Income"].replace(na)
    d["cov_urban_density"] = d["UrbanDensity"].replace({"Unknown": np.nan})
    d["cov_publisher_category"] = d["PublisherCategory"]
    return d


def main():
    z = fetch()
    s1 = read_jasp(z.read("peerj-04-2401-s001.jasp"))
    s2 = read_jasp(z.read("peerj-04-2401-s002.jasp"))
    assert s1.shape == (1899, 22) and s2.shape == (10009, 23)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    # sex is a recode of Gender in both files
    assert (s1["sex"].astype(int) == (s1["Gender"] == "Female")).all()
    assert (s2["sex"].astype(int) == np.where(s2["Gender"] == "Male", 2, 1)).all()

    # Study 2 duplicate block (see header)
    dup = s2["UserID"].duplicated(keep=False)
    assert int(dup.sum()) == 2 * 1258
    body = s2.drop(columns=["Nation"])
    assert body[dup].duplicated(keep=False).all()        # identical but Nation
    assert set(s2.loc[dup, "Nation"]) == {"1", "2"}
    assert (s2.loc[dup, "Geography"].str[:2] == "CA").all()
    s2 = s2[~(dup & (s2["Nation"] == "1"))].reset_index(drop=True)
    assert s2["UserID"].is_unique and not set(s1["UserID"]) & set(s2["UserID"])
    print(f"  Study 2: dropped 1258 duplicate Canadian rows filed under Nation 1")

    a = prep(s1, 1, IGD9)
    b = prep(s2, 2, IGD9 + ["distress"])
    a["id"] = "s1_" + (a.index + 1).astype(str)
    b["id"] = "s2_" + (b.index + 1).astype(str)
    covs = ["cov_study", "cov_country", "cov_region", "cov_gender",
            "cov_age_band", "cov_income", "cov_urban_density",
            "cov_publisher_category", "cov_mischievous"]
    long = pd.concat([
        a.melt(id_vars=["id"] + covs, value_vars=IGD9, var_name="item",
               value_name="resp"),
        b.melt(id_vars=["id"] + covs, value_vars=IGD9 + ["distress"],
               var_name="item", value_name="resp"),
    ], ignore_index=True)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    assert set(long["resp"]) == {0, 1}
    assert not long.duplicated(["id", "item"]).any()

    name = "przybylski_2016_igd"
    items = IGD9 + ["distress"]
    pv = {i: {0, 1} for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        long, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{name}.csv"
    long.to_csv(out, index=False)
    print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"(study1={a.shape[0]}, study2={b.shape[0]}) "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")
    print(long.groupby("cov_country")["id"].nunique().to_dict())


if __name__ == "__main__":
    main()
