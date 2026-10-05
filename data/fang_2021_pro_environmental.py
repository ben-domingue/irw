#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8216169
# DOI: 10.7717/peerj.11635
#   "Determinants of pro-environmental behavior among excessive smartphone usage
#   children and moderate smartphone usage children in Taiwan" (Fang, Ng, Liu,
#   Chiang & Chang, 2021), PeerJ 9:e11635.
# Data: PeerJ supplementary file peerj-09-11635-s001.xlsx (sheet
#       "Norm_behavior_data", 225 x 21, one row per child), fetched from the
#       Europe PMC supplementaryFiles zip. It is the article's only SI file.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: shipped for fang_2021_pbc, fang_2021_pn and fang_2021_peb; not for
#   fang_2021_sn. The xlsx headers are bare codes (PBC1..PEB5, no labels at any
#   level). The article's Tables 2, 3 and 5 print each item against the same
#   code ("PBC1. I take the initiative to go outdoors."), and Appendix A1 (an
#   image of the questionnaire, section D) gives the shared instruction and the
#   five anchors. Per-item means/SDs in those tables reproduce from the xlsx in
#   order (itemtext_verification/verify_fang_2021_*.R).
#   SN is left without text: the questionnaire and Table 4 have SIX social-norm
#   items, the xlsx has five (SN1-SN5), and the columns do not line up with the
#   table's numbering by mean/SD (xlsx SN1 = Table SN3, SN2 = SN4, SN4 = SN5,
#   SN5 = SN6; xlsx SN3, M = 3.19, matches no printed item; Table SN1 and SN2
#   are absent). The responses are shipped, the wording is not.
#   The English is the authors' rendering; the children (Hsinchu, grades 5-6)
#   were presumably administered a Chinese form, which is not in the deposit.
#
# Tables (all 1 = Strongly disagree ... 5 = Strongly agree):
#   fang_2021_pbc  perceived behavioural control, 4 items
#   fang_2021_pn   personal norms, 3 items
#   fang_2021_sn   social norms, 5 items (see above)
#   fang_2021_peb  pro-environmental behaviour, 5 items
#
# `number` (1-225, a row number) is the id. 7 rows are exact duplicates of
# another row, but every one is a straight-liner (all 3s or all 5s) -- chance
# agreement, not duplication, so nothing is dropped. No missing cells, no
# fractional values, no PII.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "fang_2021"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8216169/supplementaryFiles"

TABLES = {
    "fang_2021_pbc": ["PBC1", "PBC2", "PBC3", "PBC4"],
    "fang_2021_pn": ["PN1", "PN2", "PN3"],
    "fang_2021_sn": ["SN1", "SN2", "SN3", "SN4", "SN5"],
    "fang_2021_peb": ["PEB1", "PEB2", "PEB3", "PEB4", "PEB5"],
}
COV = {
    "student_grade": "cov_grade",
    "gender(1=male, 2=female)": "cov_gender",
    "Smartphone usage(1= Excessive; 2 = Moderate)": "cov_smartphone_use",
}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / "supp.zip"
    if not z.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z.write_bytes(r.content)
    zz = zipfile.ZipFile(z)
    return pd.read_excel(io.BytesIO(zz.read("peerj-09-11635-s001.xlsx")),
                         sheet_name="Norm_behavior_data")


def main():
    d = fetch()
    assert d.shape == (225, 21), d.shape
    assert d["number"].is_unique
    items = [c for v in TABLES.values() for c in v]
    assert len(items) == len(set(items))
    accounted = {"number"} | set(COV) | set(items)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    assert d[items].notna().all().all()

    # duplicates are straight-liners only
    dup = d.drop(columns="number").duplicated(keep=False)
    assert (d.loc[dup, items].nunique(axis=1) == 1).all()

    d = d.rename(columns={"number": "id", **COV})
    d["cov_gender"] = d["cov_gender"].map({1: "male", 2: "female"})
    d["cov_smartphone_use"] = d["cov_smartphone_use"].map(
        {1: "excessive", 2: "moderate"})
    assert d[["cov_gender", "cov_smartphone_use"]].notna().all().all()
    assert set(d["cov_grade"]) == {5, 6}
    covs = list(COV.values())

    assert len(TABLES) == len(set(TABLES))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        assert set(t["resp"]) <= {1, 2, 3, 4, 5}
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
