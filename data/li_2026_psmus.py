#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13175062
# DOI: 10.7717/peerj.21138
#   "Reliability, factor structure, and criterion validity: testing the
#   problematic social media use scale in Chinese college students" (Li, Liu,
#   Wang, Wang, Hao, Chen, Potenza & Moretta, 2026), PeerJ 14:e21138.
# Data: PeerJ supplementary files from the Europe PMC supplementaryFiles zip:
#       peerj-14-21138-s001.xlsx (788 x 23 raw data), peerj-14-21138-s002.docx
#       (the 15 PSMUS items, numbered 1-15, in English) and
#       peerj-14-21138-s004.docx (codebook: gender 1 male / 2 female; items 1-8,
#       1 Strongly disagree ... 8 Strongly agree).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary file.
#
# Item text: shipped. The xlsx has plain headers (Item1..Item15, no stems); the
#   stems are s002's numbered list and the eight anchors are s004's codebook.
#   Item k is tied to s002's item k by number (checked by
#   verify_li_2026_psmus.R against the deposit's five subscale sums). The survey
#   was administered to Chinese college students; the deposit and SI carry only
#   English, so the English is a translated substitute (language = Chinese).
#
# Sample: 788 Chinese college students aged 18-35. No id column: row index
# (assigned before the duplicate drop, so ids are the source row numbers).
#
# Tables:
#   li_2026_psmus  Problematic Social Media Use Scale, Item1-Item15, 1-8
#
# Skipped: `total` (sum of the 15 items, asserted) and the five 3-item subscale
# sums aPOSI, MoodRegulation, cognitivepreoccupation, compulsiveuse,
# negativeoutcomes.
# Duplicates: three pairs of rows are identical on all 23 columns (gender, age,
# all 15 items and the composites); the second row of each pair is dropped as a
# data-entry double (asserted: exactly 3), giving 785 respondents vs the paper's
# 788. No missing cells, no fractional values.

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13175062/supplementaryFiles"

ITEMS = [f"Item{i}" for i in range(1, 16)]
COV = {"gender": "cov_gender", "age": "cov_age"}
SKIP = {
    "total": "sum of Item1-Item15 (composite)",
    "aPOSI": "subscale sum (composite)",
    "MoodRegulation": "subscale sum (composite)",
    "cognitivepreoccupation": "subscale sum (composite)",
    "compulsiveuse": "subscale sum (composite)",
    "negativeoutcomes": "subscale sum (composite)",
}


def load() -> pd.DataFrame:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_excel(io.BytesIO(z.read("peerj-14-21138-s001.xlsx")))


def main() -> None:
    d = load()
    assert d.shape == (788, 23), d.shape
    assert set(d.columns) == set(ITEMS) | set(COV) | set(SKIP), set(d.columns)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert not d.isna().any().any()
    assert (d[ITEMS].sum(axis=1) == d["total"]).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    dup = d.drop(columns="id").duplicated()
    assert int(dup.sum()) == 3, int(dup.sum())
    print(f"  dropped {int(dup.sum())} exact-duplicate rows (ids {list(d.loc[dup, 'id'])})")
    d = d[~dup]

    d = d.rename(columns=COV)
    covs = list(COV.values())
    name = "li_2026_psmus"
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 785
    pvset = set(range(1, 9))
    pv = {i: pvset for i in ITEMS}
    for i in ITEMS:
        assert set(t.loc[t["item"] == i, "resp"]) <= pvset, i
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
