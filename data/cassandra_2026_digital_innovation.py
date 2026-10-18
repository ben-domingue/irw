#!/usr/bin/env python3

# Source: https://zenodo.org/records/20301395
# DOI: 10.5281/zenodo.20301395
#   Cassandra, Cadelina (2026). Questionnaire Data [Dataset]. Zenodo.
# Data: "Recap Response Excel 2 - 347.xlsx" -- 347 respondents, 1-6 agreement.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The workbook has one header row of bare construct codes
#   and no label level. The deposit's title is the bare "Questionnaire Data" and the
#   record names no paper, so there is no instrument document to fall back on
#   either -- the wording is not published anywhere this deposit points to. That is
#   the whole answer for a later pass.
#
# A SIX-POINT SCALE, not five. Every block runs 1-6 with all six categories used,
#   so the scale is the source's and no value is a sentinel.
#
# SIX tables, all 1-6, four items each:
#   cassandra_2026_innovativeness    INO1-4   cassandra_2026_learning_fit    LRF1-4
#   cassandra_2026_self_confidence   FSC1-4   cassandra_2026_self_efficacy   STE1-4
#   cassandra_2026_collaboration     CLB1-4   cassandra_2026_resource_dev    RD1-4
#   The construct names are read off the code prefixes, which is all the deposit
#   gives; they are the table's description, not a claim about a named instrument.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the deposit ships no demographics.
# Rights: no register row matches. RD/STE/CLB are this deposit's own codes.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "20301395"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 20301395, "Recap Response Excel 2 - 347.xlsx"
SCALE = set(range(1, 7))

BLOCKS = {
    "cassandra_2026_innovativeness": "INO",
    "cassandra_2026_self_confidence": "FSC",
    "cassandra_2026_collaboration": "CLB",
    "cassandra_2026_learning_fit": "LRF",
    "cassandra_2026_self_efficacy": "STE",
    "cassandra_2026_resource_dev": "RD",
}


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
    df = pd.read_excel(fetch())
    df.insert(0, "id", range(len(df)))
    blocks = {n: [f"{pre}{i}" for i in range(1, 5)] for n, pre in BLOCKS.items()}
    items = {c for cols in blocks.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    unaccounted = [c for c in df.columns if c not in ({"id"} | items)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in blocks.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-6 scale: {bad}"
        t = t[["id", "item", "resp"]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
