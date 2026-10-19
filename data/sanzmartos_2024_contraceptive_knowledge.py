#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/RRXBET
# DOI: 10.7910/DVN/RRXBET
#   Sanz Martos, S. (2024). Replication Data for: Sexuality and contraceptive
#   knowledge in university students: instrument development and psychometric
#   analysis using item response theory [Dataset]. Harvard Dataverse.
# Data: "Base de datos_Validación.sav" (served as a .tab) -- Spanish nursing
#   and physiotherapy undergraduates answering a 17-item knowledge test about
#   sexuality and contraception, scored right/wrong. The deposit is the
#   validation sample behind an IRT analysis of that instrument.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped. The items are positional ("Item 14" ... "Ítem 31"),
#   both as column names and as SPSS variable labels, so the deposit contains
#   no wording at all; the stems are in the published instrument. The gap in
#   the numbering (no Item 17, nothing below 14) is the instrument's own --
#   this is the retained pool after validation, which is what the paper is
#   about, not columns lost in deposit.
#
# ONE table: 387 respondents x 17 dichotomous items, complete (no missing
#   cell among the 6,579 responses).
#
# THE DEPOSIT'S OWN TOTAL CHECKS OUT FOR 376 OF 387, and the 11 exceptions are
#   in the total, not the items: `Puntuación` equals the sum of the 17 items
#   for every respondent except eleven CONSECUTIVE rows (P-71 to P-81), where
#   it is 1 to 4 LOWER than the sum. A contiguous block with a one-directional
#   error is a scoring slip in the total; the item responses there are 0/1 and
#   complete like every other row. No total is shipped either way.
#
# TWENTY-THREE ROWS ARE NOT SHIPPED, and the reason is that they cannot be
#   told from duplicates. The file has 410 rows. The last 23 carry complete
#   item responses but a BLANK participant label, no demographic block, none
#   of the deposit's recoded variables and no `Puntuación`; all 23 have
#   Grado=2, and every one of their 17-item response patterns already occurs
#   among the 387 labelled respondents. With 17 binary items that could be
#   coincidence -- 75 patterns repeat among the 387 -- which is exactly why
#   they are not shippable either way: nothing in the deposit says whether
#   they are 23 further students or a paste of existing ones.
#
# `Participante` is NOT used as id: it is a label with inconsistent spacing
#   ("P-1", "P- 2") and "P-110" occurs twice, on rows whose ages differ. id is
#   the row index, 1-387.
#
# Covariates: cov_gender, cov_age, cov_degree, cov_academic_year,
#   cov_religious, cov_lives_with, cov_has_partner, cov_information_source,
#   cov_self_perceived_knowledge -- the deposit's own numeric recodes, with no
#   value labels documented. The sexual-history block (age at first
#   intercourse, partner type, contraception used, previous pregnancy) is NOT
#   shipped: it is intimate personal detail that no IRW use of a knowledge
#   test needs, and leaving it out costs the table nothing.
import os
import re
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
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "rrxbet" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 10782246, "Base de datos_Validación.sav"
COVS = {"Sexo": "cov_gender", "Edad": "cov_age", "Grado": "cov_degree",
        "Curso_Rec": "cov_academic_year", "Religiosidad": "cov_religious",
        "Vive_REC": "cov_lives_with", "Pareja": "cov_has_partner",
        "Informacionusada_REC": "cov_information_source",
        "Autopercepción_REC": "cov_self_perceived_knowledge"}
SCALE = {0, 1}
N_LABELLED = 387
TABLE = "sanzmartos_2024_contraceptive_knowledge"


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
    items = [c for c in df.columns if re.fullmatch(r"[IÍ]tem\s*\d+", c)]
    assert len(items) == 17, items
    assert len(df) == 410, len(df)
    assert not df[items].isna().any().any()
    assert {v for c in items for v in df[c].unique()} == {0.0, 1.0}

    # The unlabelled tail: assert the shape this script's header describes
    # rather than slicing by position.
    label = df["Participante"].fillna("").str.replace(" ", "", regex=False)
    unlabelled = label == ""
    assert unlabelled.sum() == 410 - N_LABELLED, unlabelled.sum()
    assert unlabelled.iloc[N_LABELLED:].all() and not unlabelled.iloc[:N_LABELLED].any()
    assert df.loc[unlabelled, "Puntuación"].isna().all()
    assert (df.loc[unlabelled, "Grado"] == 2).all()
    print(f"not shipped: {int(unlabelled.sum())} unlabelled rows (no "
          f"participant label, no demographics, no score)")

    kept = df[~unlabelled].reset_index(drop=True)
    # The deposit's own arithmetic check, and its eleven exceptions.
    diff = kept["Puntuación"] - kept[items].sum(axis=1)
    agree = int((diff == 0).sum())
    assert agree == 376, agree
    off = kept.index[diff != 0].tolist()
    assert off == list(range(70, 81)), off
    assert (diff[diff != 0] < 0).all(), "the eleven exceptions should be low"
    print(f"the deposit's Puntuación equals the item sum for {agree} of "
          f"{len(kept)}; rows {off[0] + 1}-{off[-1] + 1} are 1-4 low")

    kept = kept.rename(columns=COVS)
    kept["id"] = range(1, len(kept) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(kept[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        kept[cov] = v.astype("Int64")

    t = (kept[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    assert set(t["resp"]) <= SCALE
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == N_LABELLED and t["item"].nunique() == 17
    assert len(t) == N_LABELLED * 17

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
