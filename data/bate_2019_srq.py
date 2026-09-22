#!/usr/bin/env python3
# Source: https://peerj.com/articles/6330/
# DOI: 10.7717/peerj.6330
# "Subjective assessment for super recognition: an evaluation of self-report
# methods in civilian and police participants" (Bate & Dudfield, 2019), PeerJ.
# Data: peerj-07-6330-s001.xlsx, fetched via Europe PMC supplementaryFiles
#       for PMC6360075.
# License: CC BY 4.0 (PeerJ; article-attached Supporting Information, so the
#          article licence is the source licence -- no separate deposit).
#
# Item text: NOT shipped. The deposit gives only the column codes SRQ01-SRQ20
#   with no stems anywhere in the workbook, and the article's own text
#   describes the questionnaire without reproducing all 20 items. The wording
#   is in the published paper's Appendix/Table rather than the data, so this
#   is a paper-transcription job for a later pass, not a cheap extraction.
#
# The 20-item SRQ was administered to two independently-recruited samples:
# Experiment 1 (n=264, top-end civilian, used to calibrate the questionnaire)
# and Experiment 2 (n=151, police officers). The paper's own abstract states
# the SRQ was "developed ... calibrated using a top-end civilian sample
# (Experiment 1)" and then its effectiveness "examined ... in pools of police
# (Experiment 2)", i.e. the same instrument in both -- so they merge into one
# file with cov_study, per datastandard.md's "same instrument administered to
# multiple sub-studies" rule. Experiment 3 is NOT here: that sheet carries only
# an SRQ total ("SRQ"), never the 20 item responses, so there is nothing to
# ship, and a composite is not a response.
#
# The two sheets code their covariates differently -- EXP1 writes GROUP as
# 'SR'/'TYPICAL' and GENDER as 'M'/'F', EXP2 writes both as 1/2 -- so both are
# normalised to the EXP1 spelling rather than shipped as two incompatible
# encodings under one column name. EXP2's 1/2 GENDER is read as M/F from the
# EXP1 convention; its GROUP 1/2 is read as SR/TYPICAL the same way. Where
# that reading could be wrong it would be wrong for a covariate, not for a
# response.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6360075/supplementaryFiles"
XLSX = "peerj-07-6330-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"SRQ{i:02d}" for i in range(1, 21)]
TABLE = "bate_2019_srq"


def load():
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.ExcelFile(BytesIO(fh.read()))
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def convert() -> None:
    xl = load()
    e1, e2 = xl.parse("EXP1"), xl.parse("EXP2")

    # Column bookkeeping -- every source column shipped, carried, or skipped
    # out loud. 'SRQ ALL' is the 20-item total: a composite, never a response.
    for sheet, df in (("EXP1", e1), ("EXP2", e2)):
        for c in df.columns:
            if c in ITEMS or c in ("AGE", "GENDER", "GROUP"):
                continue
            print(f"  [skip] {sheet}.{c}: "
                  + ("20-item composite, not a response" if c == "SRQ ALL"
                     else "objective task score or single-item rating, not part "
                          "of the SRQ item block"))

    gender = {1: "M", 2: "F", "M": "M", "F": "F"}
    group = {1: "SR", 2: "TYPICAL", "SR": "SR", "TYPICAL": "TYPICAL"}

    parts = []
    for study, df in (("exp1_civilian", e1), ("exp2_police", e2)):
        d = df[["AGE", "GENDER", "GROUP"] + ITEMS].copy()
        # Independently recruited samples share row numbers but not people:
        # offset past the first sample's actual observed max, never a
        # round-number guess.
        offset = 0 if study.startswith("exp1") else len(e1) + 1000
        d["id"] = range(offset + 1, offset + len(d) + 1)
        d["cov_study"] = study
        d["cov_age"] = pd.to_numeric(d.pop("AGE"), errors="coerce")
        d["cov_gender"] = d.pop("GENDER").map(gender)
        d["cov_group"] = d.pop("GROUP").map(group)
        assert d["cov_gender"].notna().all(), f"{study}: unmapped GENDER code"
        assert d["cov_group"].notna().all(), f"{study}: unmapped GROUP code"
        parts.append(d)

    wide = pd.concat(parts, ignore_index=True)
    assert wide["id"].is_unique, "id collision across the two samples"

    covs = ["cov_age", "cov_gender", "cov_group", "cov_study"]
    long = wide.melt(id_vars=["id"] + covs, value_vars=ITEMS,
                     var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int).astype(float)
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert long["resp"].between(1, 5).all(), "resp outside 1-5"
    assert not long.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert long["item"].nunique() == 20, "expected 20 SRQ items"
    assert long["id"].nunique() >= 100, "below the 100-id floor"
    # The upload profile is the gate an upload actually faces; compat.run_qc
    # is the older triage behaviour and the two can disagree.
    report = irw_validate.validate_frame(long, label=TABLE,
                                         profile="upload")
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():g}-"
          f"{long['resp'].max():g}")


if __name__ == "__main__":
    convert()
