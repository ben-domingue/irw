#!/usr/bin/env python3

# Source: https://zenodo.org/records/20670480
# DOI: 10.5281/zenodo.20670480
#   yandan, xue; Ong, Choon Hee; Miskon, Suraya (2026). Anonymized Questionnaire
#   Dataset on Chinese University Administrators' Acceptance of Administrative AI
#   [Dataset]. Zenodo.
# Data: "480 PDH 2026 data smartpls MD.sav" -- 480 Chinese university administrators,
#       eight instruments on a shared 1-5 agreement scale.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. Both label levels checked: 68 of 77 variables carry a
#   variable label and 58 carry value labels, and the item labels ARE full stems --
#   but they are the administered Chinese only ("我发现使用行政人工智能很有趣。"), with no
#   author-supplied English anywhere in the deposit or the record. Shipping would
#   require an IRW-generated translation, which owes a translation_source and a
#   public issues-page callout, so it belongs in the deliberate translation round
#   queued in TODO rather than bolted onto this batch. The Chinese stems are in
#   this .sav's variable labels when that round runs.
#
# A NOTE ON THE FRACTIONAL VALUES. Every block appeared fractional on first read,
# which is the mean-imputation signature. It is not imputation: each block ends in a
# BARE unnumbered column (PEOU, PU, CUR, ...) holding that block's row mean, and the
# prefix grouping swept it in with its own items. Checked directly -- the numbered
# items are integers throughout, and each bare column equals the row mean of its
# block. The bare columns, the Z* z-scores, MAH_1 (Mahalanobis distance) and flag_MD
# are dropped as derived.
#
# Eight tables, all 1-5:
#   xue_2026_peou  6   perceived ease of use        xue_2026_aaai  8  acceptance of admin AI
#   xue_2026_pu    6   perceived usefulness         xue_2026_ji    4  job insecurity
#   xue_2026_cur   6   curiosity                    xue_2026_ta    9  technology anxiety
#   xue_2026_joy   6   enjoyment                    xue_2026_con   5  perceived control
# id: the deposit's ID is unique over 480 rows and is used directly.
# Covariates: cov_gender, cov_age, cov_work_experience, cov_education,
#   cov_speciality, cov_vocational_skill, cov_position, cov_monthly_income.
# Rights: none of the eight is in the instrument rights register. TA is "technology
#   anxiety" here, NOT the CD-RISC / Toronto Alexithymia codes a code-prefix matcher
#   would collide with -- resolved by reading the Chinese stems.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "20670480"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 20670480, "480 PDH 2026 data smartpls MD.sav"

BLOCKS = {
    "xue_2026_peou": ("PEOU", 6), "xue_2026_pu": ("PU", 6),
    "xue_2026_cur": ("CUR", 6), "xue_2026_joy": ("JOY", 6),
    "xue_2026_con": ("CON", 5), "xue_2026_aaai": ("AAAI", 8),
    "xue_2026_ji": ("JI", 4), "xue_2026_ta": ("TA", 9),
}
COVS = {"gender": "cov_gender", "age": "cov_age",
        "yearsofworkexperience": "cov_work_experience",
        "educationlevel": "cov_education", "speciality": "cov_speciality",
        "vocationalskill": "cov_vocational_skill", "position": "cov_position",
        "monthlyincome": "cov_monthly_income"}
SCALE = set(range(1, 6))


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df = df.rename(columns={"ID": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "ID does not identify a respondent"

    items, derived = [], []
    for prefix, n in BLOCKS.values():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        for c in cols:
            assert c in df.columns, f"expected item column {c} is absent"
        items += cols
        # Prove the bare column is this block's row mean before dropping it.
        rm = df[cols].mean(axis=1)
        same = (df[prefix] - rm).abs() < 1e-6
        assert same.mean() > 0.99, (
            f"{prefix}: bare column is not the block row mean "
            f"({same.mean():.3f} agree) -- investigate before dropping")
        derived += [prefix, f"Z{prefix}"]
    derived += ["MAH_1", "flag_MD"]

    accounted = {"id"} | set(COVS) | set(items) | set(derived)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c in derived:
        print(f"  skipped {c}: derived (block row mean, z-score, "
              f"Mahalanobis or missing-data flag)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (prefix, n) in BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp survived"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-5 scale: {bad}"
        for c in COVS.values():
            t[c] = t[c].astype("Int64")
        t = t[["id", "item", "resp", *COVS.values()]]

        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
