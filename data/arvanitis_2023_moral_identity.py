#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EDRJYT
# DOI: 10.7910/DVN/EDRJYT
#   Arvanitis, A. (2023). Data Set for "Moral Self-Consistency as the
#   Self-Organization of Moral Identity: A Social-Cognitive Approach"
#   [Dataset]. Harvard Dataverse.
# Data: the deposit's single .sav (served as a .tab) -- 410 Prolific
#   respondents answering the Moral Foundations Questionnaire, the Moral
#   Foundations Vignettes and a four-item compulsion scale, in a 2x2 design.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped, and the reason is rights rather than extraction.
#   Every stem is in the SPSS variable labels in full administered English
#   ("Whether or not someone suffered emotionally"; "You see a boy throwing
#   rocks at cows that are grazing in the local pasture"), so this deposit is
#   extraction-solved for all 34 items. The MFQ and the MFV are Graham/Haidt
#   instruments and neither has a rights-register verdict, so the text waits
#   on a ruling, not on work. The compulsion items are the author's own.
#
# THREE tables, 410 respondents each, complete (no missing cell anywhere):
#   arvanitis_2023_mfq         15 items, 1-6 (the MFQ relevance block)
#   arvanitis_2023_mfv         15 items, 1-5 (the MFV vignettes)
#   arvanitis_2023_compulsion   4 items, 1-5 (the author's own scale)
#
# MFQ_MATH IS NOT SHIPPED, and it is not a data defect: "Whether or not
#   someone was good at math" is the MFQ's own catch item, administered with
#   the block and excluded from its scoring. AttentionCheck is likewise not an
#   item of any scale -- it is a 1-7 agreement rating about the purpose of the
#   research. Both were identified from their labels, not their names.
#
# NOT SHIPPED, the rest: the Qualtrics metadata (StartDate, EndDate, Status,
#   Progress, Finished, RecordedDate, ResponseId, DistributionChannel,
#   UserLanguage, Consent), Duration__in_seconds_ (a whole-survey duration,
#   not a per-item response time, so not `rt`), and the four subscale
#   composites the deposit computes (MFQ_INDI, MFQ_BIND, MFV_INDI, MFV_BIND)
#   plus Compulsion, their four-item mean.
#
# id: the row index. Prolific_ID holds a real 24-hex Prolific account id for
#   every one of the 410 rows; under the 2026-09-20 narrowing that is replaced
#   by the row index, never hashed, and the dataset ships.
# The design is 2x2 -- Identity and Framing, each -0.5/0.5 in the deposit --
#   so neither fits `treat`, which is one 0/1 column. Both ship as 0/1
#   covariates (cov_cond_identity, cov_cond_framing) with the mapping stated
#   here: 0.5 -> 1.
# Covariates: cov_gender, cov_age, cov_political_identity, cov_cond_identity,
#   cov_cond_framing. cov_age is missing for 7 of 410; the deposit documents
#   no value labels for gender (1-4) or political identity (1-7), so both ship
#   as its own codes.
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "edrjyt" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID = 7101069
FNAME = ("SPSS file Moral Self-Consistency as the Self-Organization of Moral "
         "Identity.sav")
MFQ = [f"MFQ_{f}{i}" for i in (1, 2, 3)
       for f in ("HARM", "FAIR", "INGROUP", "AUTHOR", "PURITY")]
MFV = [f"MFV_{f}{i}" for i in (1, 2, 3)
       for f in ("CARE", "FAIR", "AUTHOR", "INGROUP", "PURITY")]
COMP = [f"Compulsion{i}" for i in (1, 2, 3, 4)]
COVS = {"GENDER": "cov_gender", "AGE": "cov_age",
        "PoliticalIdentity": "cov_political_identity",
        "Identity": "cov_cond_identity", "Framing": "cov_cond_framing"}
CONDITIONS = ["cov_cond_identity", "cov_cond_framing"]
NOT_SHIPPED = [
    "StartDate", "EndDate", "Status", "Progress", "Duration__in_seconds_",
    "Finished", "RecordedDate", "ResponseId", "DistributionChannel",
    "UserLanguage", "Consent", "Prolific_ID", "MFQ_MATH", "AttentionCheck",
    "MFQ_INDI", "MFQ_BIND", "MFV_INDI", "MFV_BIND", "Compulsion",
]
TABLES = {
    "arvanitis_2023_mfq": (MFQ, set(range(1, 7))),
    "arvanitis_2023_mfv": (MFV, set(range(1, 6))),
    "arvanitis_2023_compulsion": (COMP, set(range(1, 6))),
}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    all_src = MFQ + MFV + COMP + list(COVS) + NOT_SHIPPED
    assert set(df.columns) == set(all_src), set(df.columns) ^ set(all_src)
    assert len(df) == 410, len(df)
    print(f"not shipped: {NOT_SHIPPED}")

    # Every shipped item carries its administered stem in the label; a code
    # with no label would mean the deposit changed under us.
    for c in MFQ + MFV + COMP:
        assert len((labels.get(c) or "").strip()) > 15, (c, labels.get(c))
    assert labels["MFQ_MATH"] == "Whether or not someone was good at math"

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for c in CONDITIONS:
        assert set(df[c]) == {-0.5, 0.5}, (c, set(df[c]))
        df[c] = (df[c] > 0).astype("Int64")
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols, scale) in TABLES.items():
        assert not df[cols].isna().any().any(), f"{name}: unexpected missing"
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the administered scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 410 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
