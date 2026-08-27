"""CES-D depression symptoms among students, with psychological covariates.

DOI: 10.17632/c5gpdtj8jv
Source: https://data.mendeley.com/datasets/c5gpdtj8jv
License: CC BY 4.0
Contributor (deposit record): Saha

892 respondents, the 20-item CES-D scored 0-3 (Q1-Q20). The deposit's
companion raw_dataset.xlsx carries the same 20 items with their full
English question wording, a ready source for a future itemtext pass.

Age and Depression_Score arrive z-standardised, not in raw units; Age is
kept as cov_age_z with the name marking that, Depression_Score is a
composite of the 20 items and is dropped. Depression_Level is a banded
recode of that same composite and is likewise dropped.
Academic_Year_* and Field_* are regression dummy expansions; they are
recovered back into two real covariates by index, with the omitted
level as the reference category.
"""
from __future__ import annotations

import io
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/c5gpdtj8jv"
KEY = "c5gpdtj8jv"
FILENAME = 'final_preprocessed_dataset.xlsx'
READ_KW = {}
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE_PREFIX = "saha_2026_"
BLOCKS = {'cesd': 'Q\\d+'}            # table suffix -> regex matching its item columns
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age_z'}
DUMMY_GROUPS = {
    # prefix -> (covariate name, reference level for the omitted indicator)
    "Academic_Year_": ("cov_academic_year", "1st Year"),
    "Field_": ("cov_field", "Arts & Humanities"),
    "Psychological_Factor_": ("cov_psychological_factor", "None reported"),
}
DROP = ["Depression_Score", "Depression_Level"]
DROP_REASON = "composite of the 20 CES-D items (or a banded recode of it), not a raw item"
SCALE = {'cesd': (0, 3)}              # table suffix -> (min, max), or None to infer
QC_WAIVERS = {}


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    files = r.json()["files"]
    match = [f for f in files if f["filename"] == FILENAME]
    assert len(match) == 1, [f["filename"] for f in files]
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    low = FILENAME.lower()
    if low.endswith(".sav"):
        import pyreadstat
        fh = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
        fh.write(rr.content); fh.close()
        return pyreadstat.read_sav(fh.name)[0]
    if low.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(rr.content), **READ_KW)
    return pd.read_csv(io.BytesIO(rr.content), **READ_KW)


def build() -> None:
    df = fetch()
    df.columns = [str(c).strip() for c in df.columns]
    df["id"] = range(1, len(df) + 1)
    cov = df[["id"] + list(COVS)].rename(columns=COVS)

    used = set(COVS) | set(DROP)
    # recover regression dummy expansions into real categorical covariates:
    # the index of whichever indicator is 1, and the omitted level where none is
    for prefix, (name, reference) in DUMMY_GROUPS.items():
        cols = [c for c in df.columns if c.startswith(prefix)]
        assert cols, prefix
        used.update(cols)
        levels = [c[len(prefix):] for c in cols]
        block = df[cols].astype(bool)
        multi = int((block.sum(axis=1) > 1).sum())
        assert multi == 0, f"{prefix}: {multi} rows set more than one indicator"
        picked = block.idxmax(axis=1).str[len(prefix):]
        cov[name] = picked.where(block.any(axis=1), reference)
        print(f"    recovered '{name}' from {len(cols)} dummies "
              f"(+ reference level '{reference}')")
    for c in DROP:
        print(f"    dropped '{c}': {DROP_REASON}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for suffix, pattern in BLOCKS.items():
        items = [c for c in df.columns
                 if re.fullmatch(pattern, c) and c not in DROP and c not in COVS]
        assert items, f"{suffix}: pattern {pattern!r} matched nothing"
        used.update(items)

        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"])
                .merge(cov, on="id"))

        nonint = long["resp"] % 1 != 0
        if nonint.any():
            print(f"    [{suffix}] dropped {int(nonint.sum())} non-integer cells")
            long = long[~nonint]
        long["resp"] = long["resp"].astype(int)

        lo, hi = SCALE[suffix]
        oor = ~long["resp"].between(lo, hi)
        if oor.any():
            vals = sorted(long.loc[oor, "resp"].unique())
            per = long.loc[oor].groupby("item").size().to_dict()
            print(f"    [{suffix}] dropped {int(oor.sum())} out-of-range cells "
                  f"{vals} (data-entry errors, isolated to {per})")
            long = long[~oor]

        long = long[["id", "item", "resp"]
                    + [c for c in long.columns if c.startswith("cov_")]]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        for c in [c for c in fails if c.name in QC_WAIVERS]:
            print(f"    WAIVED [{suffix}] {c.name}: {QC_WAIVERS[c.name]}")
        fails = [c for c in fails if c.name not in QC_WAIVERS]
        assert not fails, f"{suffix} QC failed: {[(c.name, c.detail) for c in fails]}"
        for c in checks:
            if c.status == "warn":
                print(f"    NOTE [{suffix}] {c.name}: {c.detail}")

        assert long["id"].nunique() >= 100, f"{suffix}: N={long['id'].nunique()} < 100"
        assert long["item"].nunique() > 1, f"{suffix}: single-item scale"

        name = f"{TABLE_PREFIX}{suffix}"
        assert name not in written, f"duplicate table name {name}"
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written[name] = (long["id"].nunique(), long["item"].nunique(), len(long))
        print(f"  {name}: {written[name][0]} ids x {written[name][1]} items "
              f"= {written[name][2]} responses")

    unused = [c for c in df.columns if c not in used and c != "id"]
    assert not unused, f"unaccounted source columns: {unused}"
    print(f"  total: {sum(v[2] for v in written.values())} responses "
          f"across {len(written)} tables")


if __name__ == "__main__":
    build()
