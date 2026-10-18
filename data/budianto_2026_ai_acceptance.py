#!/usr/bin/env python3

# Source: https://zenodo.org/records/21502225
# DOI: 10.5281/zenodo.21502225
#   Budianto, A. A., Susanto, R. A., Nurzaman, et al. (2026). Dataset and
#   Questionnaire Items of AI Acceptancy [Dataset]. Zenodo.
# Data: "Kuisioner Thesis.csv" -- 415 Indonesian respondents, 1-5 agreement. The
#       deposit also ships "Questionnaire Items.xlsx".
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped, and this one is a near miss worth recording. The deposit
#   DOES include a questionnaire file ("Questionnaire Items.xlsx", 30 rows x 6)
#   whose rows are the item stems, so the mapping is cheap -- but the stems are the
#   administered INDONESIAN with no author-supplied English. Shipping would require
#   an IRW-generated translation, which owes a translation_source and a public
#   issues-page callout, so it belongs in the deliberate translation round queued in
#   TODO. The text is in that workbook when the round runs; this is the strongest
#   candidate in the batch for it, because the stems and codes are already aligned
#   in one file.
#
# SIX tables, all 1-5:
#   budianto_2026_perceived_usefulness   5 items (PU1-5)
#   budianto_2026_perceived_ease         5 items (PEOU1-5)
#   budianto_2026_trust                  5 items (T1-5)
#   budianto_2026_attitude               5 items (ATU1-5)
#   budianto_2026_intention              5 items (BI1-5)
#   budianto_2026_actual_use             4 items (AU1-4)
# Not shipped: the trailing all-empty "Unnamed: 29" column the CSV export left.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the response file ships no demographics.
# Rights: none of the six is in the register. T1-T5 is "trust" here, which a bare
#   ^T[0-9] matcher could collide with; resolved from the deposit's own
#   questionnaire file rather than from the code.
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "21502225"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 21502225, "Kuisioner Thesis.csv"
SCALE = set(range(1, 6))

BLOCKS = {
    "budianto_2026_perceived_usefulness": [f"PU{i}" for i in range(1, 6)],
    "budianto_2026_perceived_ease": [f"PEOU{i}" for i in range(1, 6)],
    "budianto_2026_trust": [f"T{i}" for i in range(1, 6)],
    "budianto_2026_attitude": [f"ATU{i}" for i in range(1, 6)],
    "budianto_2026_intention": [f"BI{i}" for i in range(1, 6)],
    "budianto_2026_actual_use": [f"AU{i}" for i in range(1, 5)],
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
    df = pd.read_csv(fetch())
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    spare = [c for c in df.columns if str(c).startswith("Unnamed")]
    for c in spare:
        assert df[c].isna().all(), f"{c} is not empty -- re-read the header"
        print(f"  skipped {c}: empty trailing column from the CSV export")
    unaccounted = [c for c in df.columns if c not in ({"id"} | items | set(spare))]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-5 scale: {bad}"
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
