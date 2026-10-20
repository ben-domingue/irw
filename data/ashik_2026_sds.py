"""
Bangla Smartphone Distraction Scale validation in Bangladeshi adolescents:
Smartphone Distraction Scale (SDS, 16 items), Smartphone Addiction Scale -
Short Version (SAS-SV, 10 items), a 6-item problematic academic use scale
(PAUS) and the PHQ-9.

Source: Mohd. Ashik, Shahrier. "Psychometric validation of the Bangla
        Smartphone Distraction Scale and its academic and psychological
        correlates among adolescents." (2026)
DOI: 10.5281/zenodo.23254566
Data: https://zenodo.org/records/23254566
      (SDS Manuscript Data EFA.sav, SDS Manuscript Data CFA.sav)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license = cc-by-4.0)
Item text: not shipped. Checked both SPSS label levels: variable labels are
        positional ("SDS-1" … "SDS-16", "SAS-SV 1", "PAUS 1", "PHQ 1") and
        carry no stems; value labels give only the response-option wording
        ("Almost Never" … "Almost Always"). Option text alone is not shippable,
        and the Bangla item stems are in the paper, not the deposit.

The two .sav files are the same instrument battery administered to two
adolescent samples (EFA calibration, CFA validation), with identical columns,
so they ship as one file per instrument with `cov_study`; CFA ids are offset
past the EFA maximum.

Sentinels dropped: PHQ_* = 9 (out of the documented 0-3 PHQ range, 12 cells)
and PAUS_* = 0 (out of the 1-5 PAUS range, 19 cells).
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

EFA = Path(sys.argv[1])
CFA = Path(sys.argv[2])
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")

COV_MAP = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Residence": "cov_residence",
    "Grade_Class": "cov_grade",
    "GPA": "cov_gpa",
    "Family_Monthly_Income": "cov_family_income",
    "Socio_Economic_Status": "cov_ses",
    "Daily_Time_Spend_in_Acdemic_Tasks": "cov_daily_academic_hours",
    "Daily_Sleeping_Hours": "cov_daily_sleep_hours",
}

SCALES = [
    ("SDS",     [f"SDS_{i}" for i in range(1, 17)],    (1, 5), "ashik_2026_sds"),
    ("SAS_SV",  [f"SAS_SV_{i}" for i in range(1, 11)], (1, 6), "ashik_2026_sas_sv"),
    ("PAUS",    [f"PAUS_{i}" for i in range(1, 7)],    (1, 5), "ashik_2026_paus"),
    ("PHQ",     [f"PHQ_{i}" for i in range(1, 10)],    (0, 3), "ashik_2026_phq9"),
]
AGG = ["SDS_TOTAL", "SAS_SV_TOTAL", "PAUS_TOTAL", "PHQ_TOTAL"]


def pii_screen(df: pd.DataFrame, tag: str) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen [{tag}]: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected free-text columns: {text_cols}"


def load() -> pd.DataFrame:
    a, _ = pyreadstat.read_sav(str(EFA))
    b, _ = pyreadstat.read_sav(str(CFA))
    pii_screen(a, "EFA")
    pii_screen(b, "CFA")
    assert set(a.columns) == set(b.columns)
    b = b[a.columns]
    a = a.reset_index(drop=True)
    b = b.reset_index(drop=True)
    a["id"] = a.index + 1
    b["id"] = b.index + 1 + int(a["id"].max())   # offset past the EFA sample
    a["cov_study"] = "efa"
    b["cov_study"] = "cfa"
    df = pd.concat([a, b], ignore_index=True)
    assert df["id"].is_unique
    print("merged shape", df.shape, "ids", df["id"].nunique())
    return df


def main() -> None:
    df = load()
    for src, dst in COV_MAP.items():
        df[dst] = df[src]
    covs = list(COV_MAP.values()) + ["cov_study"]

    used = {"id", "cov_study"} | set(COV_MAP) | set(covs)
    written: set[str] = set()

    for _, cols, (lo, hi), table in SCALES:
        for c in cols:
            assert c in df.columns, c
        used.update(cols)
        long = df[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        n_all = len(long)
        long = long.dropna(subset=["resp"])
        out_of_range = ~long["resp"].between(lo, hi)
        if out_of_range.any():
            print(f"{table}: dropping {int(out_of_range.sum())} cell(s) outside "
                  f"the documented {lo}-{hi} range (sentinel codes): "
                  f"{sorted(long.loc[out_of_range, 'resp'].unique())}")
        long = long[~out_of_range].copy()
        assert (long["resp"] % 1 == 0).all(), "fractional Likert value"
        long["resp"] = long["resp"].astype(int)
        cols_out = ["id", "item", "resp"] + covs
        long = long[cols_out].sort_values(["id", "item"])
        assert table not in written
        written.add(table)
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, (table, _fails)
        for _c in _checks:
            if _c.status == "warn":
                print(f"  [qc warn] {table} {_c.name}: {_c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} (of {n_all}) ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")

    skipped = {c: "person-level composite (sum of the item columns above)"
               for c in AGG}
    used.update(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


if __name__ == "__main__":
    main()
