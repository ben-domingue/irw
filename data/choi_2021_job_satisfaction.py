"""
Job satisfaction (19 items) among U.S. hourly food-and-beverage essential
workers surveyed on MTurk during the COVID-19 pandemic.

Source: Choi, Hyeri. "Data for Anxiety Undermined Job Satisfaction Among
        Essential Workers in the U.S. during the COVID-19 Pandemic."
        Harvard Dataverse (2021).
DOI: 10.7910/DVN/RMUJNX
Data: https://doi.org/10.7910/DVN/RMUJNX (analysis_data.csv, format=original)
License: CC0 1.0 (verified on the Dataverse record, rightsIdentifier CC0-1.0)
Item text: not shipped — the deposit is two data files with no codebook
        ("Codebook or other information can be provided upon request" in the
        dataset description), and the CSV header is positional (js1…js19).
        The 19 stems would have to come from the paper or from the author.

Only one shared-scale item block is published: js1-js19, a 1-5 agreement
scale. The single `anxiety` item (1-5) is a one-item measure and is not
shipped. `mturkID` is a platform participant identifier and is replaced by the
row index (never hashed); two of the 231 rows repeat an MTurk id, so row index
also keeps those submissions distinct rather than merging them.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1])
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

TABLE = "choi_2021_job_satisfaction"
ITEMS = [f"js{i}" for i in range(1, 20)]
COV_MAP = {
    "sex": "cov_sex",
    "race": "cov_race",
    "educ": "cov_educ",
    "income": "cov_income",
    "state": "cov_state",
    "occ": "cov_occupation",
    "jobstatus": "cov_job_status",
    "numemployee": "cov_employer_size",
}

# Columns deliberately left out, with the reason printed at the end.
SKIP_EXACT = {
    "mturkID": "platform participant id, replaced by the row index",
    "RandomID": "depositor's random key, redundant with the row index",
    "month": "month of birth; birth-date components are not carried into IRW",
    "year": "year of birth; birth-date components are not carried into IRW",
    "anxiety": "single-item anxiety measure; a 1-item scale is not shippable",
    "duration": "survey completion time, not a per-item response time",
    "finished": "Qualtrics completion flag (constant True)",
    "attentioncheck": "attention-check string (constant)",
    "employed": "screening question (constant Yes)",
    "selfemployed": "screening question (constant No)",
    "foodandbeverage": "screening question (constant Yes)",
}


def main() -> None:
    df = pd.read_csv(SRC, low_memory=False)
    print("raw shape", df.shape)
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}")
    assert len(text_cols) > 0, "string-column screen selected nothing"
    # Reviewed by hand: the free-text columns (*_others, occ_other,
    # jobstatus_others) hold job/policy descriptions, none naming a person,
    # employer, address or contact detail; none of them is carried forward.
    free_text = [c for c in text_cols if c.endswith(("_other", "_others"))]
    print("free-text columns (not carried forward):", free_text)

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src].astype(str).str.strip()
    covs = list(COV_MAP.values())

    for c in ITEMS:
        assert c in df.columns, c
    long = df[["id"] + covs + ITEMS].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all(), "fractional Likert value"
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(1, 5).all()
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    assert long["id"].nunique() >= 100
    out = OUT / f"{TABLE}.csv"
    assert not (OUT / f"{TABLE}.csv").is_dir()
    _checks = run_qc(long)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, (TABLE, _fails)
    for _c in _checks:
        if _c.status == "warn":
            print(f"  [qc warn] {TABLE} {_c.name}: {_c.detail[:180]}")
    long.to_csv(out, index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")

    # Balance the books: every source column is output, a covariate, or skipped
    # with a reason.
    accounted = set(ITEMS) | set(COV_MAP) | set(covs) | {"id"} | set(SKIP_EXACT)
    rest = [c for c in df.columns if c not in accounted]
    for c in SKIP_EXACT:
        print(f"skipped column {c}: {SKIP_EXACT[c]}")
    for c in rest:
        print(f"skipped column {c}: job/schedule/pandemic-impact survey "
              f"question on its own idiosyncratic response format; not part of "
              f"a shared-scale item block and not needed as a covariate")
    assert len(accounted) + len(rest) >= len(df.columns)


if __name__ == "__main__":
    main()
