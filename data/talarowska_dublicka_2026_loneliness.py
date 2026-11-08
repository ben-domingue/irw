#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0358449
# DOI: 10.1371/journal.pone.0358449
# Paper: Talarowska-Dublicka M, Gapinska A, Finogenow M (2026). Relationships
#   between primal emotional systems and the sense of loneliness: The
#   mediating role of early maladaptive schemas. PLoS ONE.
# Data: OSF 10.17605/OSF.IO/7UQE9, "Talarowska-Dublicka M.xlsx" (one sheet,
#   Polish item wording as column headers). 323 Polish adults recruited
#   online, 2023-24.
# License: CC BY 4.0 (OSF node license, api.osf.io/v2/nodes/7uqe9; node public).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# THREE output tables, items as answered and numbered in deposit (survey)
# order; the column headers carry the full Polish wording:
#   talarowska_dublicka_2026_ysq_s3  Young Schema Questionnaire short form
#     (YSQ-S3-PL), 90 items, 1 completely untrue of me .. 6 describes me
#     perfectly. Empty "Opinia"/"Punkty" scoring columns ignored.
#   talarowska_dublicka_2026_ucla  Revised UCLA Loneliness Scale, 20 items
#     1-4.
#   talarowska_dublicka_2026_banps Brief ANPS, 33 items 1-5.
#   The deposit places a reversed copy ("Odp odwrocone - <wording>") right
#   after each positively/negatively keyed item (10 UCLA, 18 BANPS); every
#   copy equals (k + 1) - x of the column before it (asserted), so the raw
#   items are those columns and the copies are not shipped.
# Checks: N = 323 and mean age 26.9 as in the paper (asserted).
# Covariates: age (one non-integer value, 10.66, set missing). Sex, marital
#   status, education and residence codes have no codebook and are dropped.
# `id` is the deposit's ID (1..326 with gaps; no other identifier).
#
# Item text: NOT SHIPPED. Cheap: the Polish wording of all 143 items is in
#   the column headers (YSQ-S3 and R-UCLA are published instruments; check
#   the register).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/6a8c59d0861c2a5862ff208e/"
RAW = os.environ.get("TALAROWSKA2026_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_talarowska2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    df = df[df["ID"].notna()].copy()
    assert len(df) == 323 and df["ID"].is_unique
    df["id"] = df["ID"].astype(int)
    age = pd.to_numeric(df["Wiek"], errors="coerce")
    assert round(age.mean(), 1) == 26.9
    df["cov_age"] = age.where(age == age.round())
    covs = ["cov_age"]
    cols = list(df.columns)

    # first UCLA item ("Dobrze sie czuje z ludzmi wokol...") starts at col 107,
    # first BANPS item at col 138
    assert str(cols[107]).startswith("Dobrze się czuję z ludźmi")
    assert str(cols[138]).startswith("Ludzie, którzy mnie znają")
    for i, c in enumerate(cols):
        if str(c).startswith("Odp odwr"):
            k = 5 if i < 138 else 6
            assert (df[c] == k - df[cols[i - 1]]).all(), c

    ysq = [c for c in cols[6:107] if not str(c).startswith(("Opinia", "Punkty"))]
    ucla = [c for c in cols[107:138] if not str(c).startswith("Odp odwr")]
    banps = [c for c in cols[138:188] if not str(c).startswith("Odp odwr")]
    assert (len(ysq), len(ucla), len(banps)) == (90, 20, 33)

    for src, pre, name, vals in [
        (ysq, "ysq", "talarowska_dublicka_2026_ysq_s3", range(1, 7)),
        (ucla, "ucla", "talarowska_dublicka_2026_ucla", range(1, 5)),
        (banps, "banps", "talarowska_dublicka_2026_banps", range(1, 6)),
    ]:
        names = [f"{pre}{i:02d}" for i in range(1, len(src) + 1)]
        out = df[["id"] + covs + src].copy()
        out.columns = ["id"] + covs + names
        save(out, covs, names, name, vals)


if __name__ == "__main__":
    convert()
