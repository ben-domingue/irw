#!/usr/bin/env python3

# Source: https://borealisdata.ca/dataset.xhtml?persistentId=doi:10.5683/SP3/SWTZFF
# DOI: 10.5683/SP3/SWTZFF
#   Dufour, S. (2024). Replication data for: Biosecurity adoption in Quebec
#   dairy farms: results from a risk assessment questionnaire analyzed using
#   conventional and unsupervised artificial intelligence methods [Dataset].
#   Borealis.
# Data: "mca_dataset_1.tab" -- 3,581 Quebec dairy farms answering the
#   ProAction biosecurity risk-assessment questionnaire. The respondent is the
#   producer; the questions are about the farm's own practice.
# License: CC BY 4.0 (verified on the Borealis record, 2026-10-19).
# Item text: NOT shipped, and nothing about it is unresolved: the deposit
#   ships Codebook.xlsx, which gives every variable's full question wording
#   and its value set, plus the ProAction questionnaire itself as a PDF. That
#   codebook is what this script reads to decide the two response formats
#   below, so the mapping is the source's.
#
# TWO tables, because the questionnaire has two response formats and the
#   codebook states both:
#   dufour_2024_biosecurity_frequency  28 items, 1-4
#       1 = Never, 2 = Sometimes, 3 = Often, 4 = Always
#   dufour_2024_biosecurity_yesno       5 items, 0/1
#       the source codes these 1 = No, 4 = Yes. `resp` is the 0/1 recode and
#       `resp_raw` keeps the source's own code, because a 1/4 "binary" invites
#       every later reader to mistake it for a 4-point scale.
#
# 5 IS "NOT APPLICABLE" AND IS DROPPED, on both formats -- 5,722 cells of the
#   frequency items and 179 of the yes/no ones. The codebook is explicit
#   (5 = Not applicable; 6 = "I don't know", which no respondent used), and an
#   in-range integer that means non-response is exactly the sentinel the data
#   standard says to filter rather than keep or recode. Ten further cells hold
#   0, which the codebook does not define at all; also dropped, and counted
#   below so the next reader does not have to rediscover them.
#
# NOT SHIPPED: `Concerndis` (which disease worries the producer most -- a
#   1-11 categorical, not an item), and `buying`/`reintro`, two 0/1 filter
#   questions that gate blocks the deposit does not include. They ship as
#   covariates instead.
#
# id: the row index. The file carries no farm identifier -- deliberately, as
#   a de-identification measure for a complete-census questionnaire.
# Covariates: cov_disease_concern, cov_buys_cattle, cov_reintroduces_cattle.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "swtzff" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
# Dataverse serves the ingested copy as .tab; ?format=original returns
# the depositor's own .xlsx, which is what this reads.
DATA_ID, DATA_NAME = 706545, "mca_dataset_1.xlsx"
CODEBOOK_ID, CODEBOOK_NAME = 706543, "Codebook.xlsx"
NOT_APPLICABLE, DONT_KNOW = 5, 6
FREQ_SCALE = {1, 2, 3, 4}
YESNO_MAP = {1: 0, 4: 1}
COVS = {"Concern_dis": "cov_disease_concern", "buying": "cov_buys_cattle",
        "reintro": "cov_reintroduces_cattle"}
FREQ_TABLE = "dufour_2024_biosecurity_frequency"
YESNO_TABLE = "dufour_2024_biosecurity_yesno"


def fetch(fid: int, name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://borealisdata.ca/api/access/datafile/{fid}?format=original"
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch(DATA_ID, DATA_NAME))
    cb = pd.read_excel(fetch(CODEBOOK_ID, CODEBOOK_NAME))
    cb = cb.dropna(subset=["Name of the variable in the dataset"])
    assert len(df) == 3581, len(df)

    # The codebook names variables with underscores the data file strips.
    spec = {}
    for _, row in cb.iterrows():
        key = str(row["Name of the variable in the dataset"]).replace("_", "")
        spec[key.strip().lower()] = str(row["Values"])
    freq, yesno, unmatched = [], [], []
    for c in df.columns:
        values = spec.get(c.replace("_", "").strip().lower())
        if values is None:
            unmatched.append(c)
        elif "Never" in values:
            freq.append(c)
        elif "= Yes" in values:
            yesno.append(c)
        else:
            unmatched.append(c)
    assert len(freq) == 28 and len(yesno) == 5, (len(freq), len(yesno))
    assert sorted(unmatched) == sorted(COVS), unmatched
    print(f"codebook: {len(freq)} frequency items, {len(yesno)} yes/no items, "
          f"{len(unmatched)} non-items ({', '.join(sorted(unmatched))})")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, cols in ((FREQ_TABLE, freq), (YESNO_TABLE, yesno)):
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        assert DONT_KNOW not in set(t["resp"]), "a 'don't know' appeared"
        n_na = int((t["resp"] == NOT_APPLICABLE).sum())
        allowed = FREQ_SCALE if name == FREQ_TABLE else set(YESNO_MAP)
        n_undoc = int((~t["resp"].isin(allowed | {NOT_APPLICABLE})).sum())
        t = t[t["resp"].isin(allowed)].copy()
        print(f"{name}: dropped {n_na} 'not applicable' (code "
              f"{NOT_APPLICABLE}) and {n_undoc} undocumented value(s)")
        if name == YESNO_TABLE:
            t["resp_raw"] = t["resp"]
            t["resp"] = t["resp"].map(YESNO_MAP).astype(int)
            scale = set(YESNO_MAP.values())
            t = t[["id", "item", "resp", "resp_raw", *cov_cols]]
        else:
            scale = FREQ_SCALE
            t = t[["id", "item", "resp", *cov_cols]]
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 3000 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:140]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
