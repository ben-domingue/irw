#!/usr/bin/env python3

# Source: https://zenodo.org/records/19896978
# DOI: 10.5281/zenodo.19896978
#   Bateman, Andre (2026). The DASS-16: Exploring Validity Evidence for a Modified
#   Version of the Depression, Anxiety, and Stress Scale in Jamaican Adults
#   [Dataset]. Zenodo.
# Data: the deposit's single .xlsx -- 371 Jamaican adults, the full DASS-21 as
#       administered (the paper's DASS-16 is a subset of these 21 items, so the
#       21-item administration is what ships).
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. The workbook has one header row of bare item codes
#   (DASS1..DASS21) and no label level -- .xlsx carries none. The DASS-21 wording is
#   the published instrument's, one hop away.
# Rights: the DASS is `ship` in itemtext/instrument_rights_register.csv ("Depression
#   Anxiety Stress Scales (DASS-21 / DASS-42), Lovibond & Lovibond"), whose matcher
#   `^dass[_ ]?[0-9]` matches these codes. Not a block.
#
# SENTINEL. The raw values run -999..3. The DASS-21 is a 0-3 scale, so -999 is a
#   missing-data sentinel, not a response; it is dropped rather than shipped, and
#   the count is printed. Nothing else falls outside 0-3.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the deposit ships the 21 item columns and nothing else.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "19896978"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 19896978
NAME = "bateman_2026_dass21"
SCALE = {0, 1, 2, 3}
SENTINEL = -999


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hits = [p for p in RAW_DIR.glob("*.xlsx")]
    if hits:
        return hits[0]
    j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                     headers=UA, timeout=120).json()
    f = [x for x in j["files"] if x["key"].lower().endswith(".xlsx")][0]
    p = RAW_DIR / f["key"]
    r = requests.get(f["links"]["self"], headers=UA, timeout=300)
    r.raise_for_status()
    p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch())
    items = [f"DASS{i}" for i in range(1, 22)]
    unaccounted = [c for c in df.columns if c not in items]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    df.insert(0, "id", range(len(df)))

    t = (df.melt(id_vars="id", value_vars=items, var_name="item",
                 value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    n_sent = int((t["resp"] == SENTINEL).sum())
    t = t[t["resp"] != SENTINEL]
    print(f"  dropped {n_sent} cells carrying the {SENTINEL} missing-data sentinel")
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the DASS's documented 0-3 scale: {bad}"
    t = t[["id", "item", "resp"]]

    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2
    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:180]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
