#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/bxd8g5p4rb
# DOI: 10.17632/bxd8g5p4rb
#   Tantia, Veerta; Kareem, Jacqueline; Balakrishnan, Valarmathi B. (2024).
#   "Dataset of attitude towards statistics." Mendeley Data.
# Data: attitude towards statistics dataset.sav (474 rows x 34 columns;
#       Indian postgraduate students of social sciences, education, and
#       commerce/management).
# License: CC BY 4.0 (Mendeley public API, data_licence.short_name).
#
# Item text: SHIPPED. Both label levels checked. The variable labels carry
#   the full English stem for all 28 items, each prefixed by the
#   instrument's own item number ("1I feel that statistics will be useful to
#   me in my profession."), so the code-to-text tie is the source's
#   numbering rather than positional -- and the numbering is what reveals
#   that item 14 is absent (the labels run 1-13, 15-29). Value labels exist
#   only on the three demographic columns, never on an item, and the deposit
#   ships no codebook, so the five Likert anchors are nowhere in the source:
#   option_text is left blank at every point rather than invented.
#
# The instrument is Wise's (1985) Attitudes Toward Statistics (ATS) scale,
#   whose two subscales the deposit itself averages into ATF and ATC. It has
#   no row in itemtext/instrument_rights_register.csv.
#
# RIGHTS NOTE for whoever runs irw_validate on this: the item codes c1-c9
#   will trip the register's Connor-Davidson Resilience Scale matcher, whose
#   `match_item_code` is `^C[0-9]{1,2}$|cd[-_]?risc`. That is a FALSE
#   POSITIVE -- these are the ATS "attitude toward Course" items, nothing to
#   do with CD-RISC. A match is a lead, not a verdict.
#
# Tables (item codes are the source column names):
#   tantia_2024_ats_field   f1-f19, 1-5. Attitude toward the Field of
#       statistics (the deposit's ATF mean is built from these).
#   tantia_2024_ats_course  c1-c9, 1-5. Attitude toward the statistics
#       Course (the deposit's ATC mean).
#
# Dropped, with reasons printed:
#   - ATF, ATC: the two subscale means (fractional, e.g. 1.6).
#   - Percentage: last percentage scored in statistics, a prior attainment
#     measure, kept as cov_last_statistics_percentage.
# id: row index (the source has no respondent identifier).
# Covariates: cov_programme, cov_year_of_study, cov_prior_statistics,
#   cov_last_statistics_percentage.

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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/bxd8g5p4rb"
FILENAME = "attitude towards statistics dataset.sav"

FIELD = [f"f{i}" for i in range(1, 20)]
COURSE = [f"c{i}" for i in range(1, 10)]
TABLES = {
    "tantia_2024_ats_field": (FIELD, "Attitudes Toward Statistics (ATS, "
                                     "Wise 1985) -- Attitude toward Field"),
    "tantia_2024_ats_course": (COURSE, "Attitudes Toward Statistics (ATS, "
                                       "Wise 1985) -- Attitude toward Course"),
}
COVS = {"PresentProgrammeofstudy": "cov_programme",
        "Yearyouarestudyingincurrently": "cov_year_of_study",
        "Previousbasicknowledgeofstatistics": "cov_prior_statistics",
        "Percentage": "cov_last_statistics_percentage"}
DROPPED = {"ATF", "ATC"}
ALLOWED = {1, 2, 3, 4, 5}


def fetch():
    meta = requests.get(API, headers=UA, timeout=60).json()
    lic = (meta.get("data_licence") or {}).get("short_name")
    assert lic == "CC BY 4.0", lic
    url = next(f["content_details"]["download_url"] for f in meta["files"]
               if f["filename"] == FILENAME)
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    p = OUT_DIR.parent / "runs" / "_tantia.sav"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(r.content)
    df, m = pyreadstat.read_sav(str(p), apply_value_formats=False)
    p.unlink()
    return df, m


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, m = fetch()
    assert d.shape == (474, 34), d.shape

    items = FIELD + COURSE
    known = set(items) | set(COVS) | DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    print(f"dropped {len(DROPPED)} subscale mean(s): {sorted(DROPPED)}")
    print(f"kept {len(COVS)} covariate(s), {len(items)} item(s)")

    # The label numbering is the item's own; confirm it is 1-13,15-29.
    nums = {}
    for it in items:
        lab = m.column_names_to_labels[it]
        n = int("".join(ch for ch in lab[:3] if ch.isdigit()))
        nums[it] = n
    assert sorted(nums.values()) == [i for i in range(1, 30) if i != 14], \
        sorted(nums.values())
    print("label numbering is 1-13,15-29: the instrument's item 14 is absent "
          "from the deposit")

    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    d.insert(0, "id", range(1, len(d) + 1))

    names = []
    for table, (its, instrument) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - ALLOWED
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(its) > 1
        pv = {i: ALLOWED for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        rows = []
        for it in its:
            lab = m.column_names_to_labels[it]
            stem = lab[len(str(nums[it])):].strip().replace("\t", " ")
            stem = " ".join(stem.split())
            assert stem
            for r in sorted(ALLOWED):
                rows.append({
                    "table": table, "section_id": f"{table}_1", "item": it,
                    "instrument": instrument, "language": "",
                    "instructions": "", "section_prompt": "",
                    "item_text": stem, "correct_response": "",
                    "option_text": "", "resp": r,
                })
        it_df = pd.DataFrame(rows)
        assert set(it_df["item"]) == set(its)
        assert set(it_df["resp"]) == ALLOWED
        tp = TEXT_DIR / f"{table}__items.csv"
        it_df.to_csv(tp, index=False)
        print(f"  {tp.name}: {len(it_df)} rows, "
              f"{it_df['item'].nunique()} items x {len(ALLOWED)} options")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
