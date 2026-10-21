"""
Masters weightlifters surveyed during the COVID-19 pandemic: what attracts
them to the sport, what gets in the way, and how the pandemic changed their
training. 1,055 athletes across Australia, Canada, Europe and the USA.

Source: Huebner, M. (2021). Weightlifting during the COVID-19 pandemic -- A
        transnational study regarding motivation, barriers, and coping of
        master athletes [Dataset]. Zenodo.
DOI: 10.5061/dryad.qfttdz0ht
Data: https://zenodo.org/records/5500789 (wldat_dryad.csv, with
        wldat_dictionary.xlsx as the deposit's own codebook)
License: CC0 1.0 (verified on the Zenodo record, metadata.license.id =
        cc-zero)
Item text: shipped. The deposit ships wldat_dictionary.xlsx, whose `Item`
        column NAMES each data column and whose `Question/Variable` and
        `Values` columns give the stem and the five labelled scale points --
        so code and wording are tied by the source itself, not by position or
        order. instrument: stems match no published scale (searched verbatim);
        they are the author's own transnational Masters-weightlifting survey
        questions; rights: author-authored, and the whole deposit is CC0 1.0.

`id` in the source is a Qualtrics response ID (R_bdb2OJCZNXPafAZ). It is a
platform participant identifier, so it is replaced with the row index -- never
a hash of it, which stays re-linkable from any other deposit holding the same
IDs (2026-09-20 ruling).

Output: three tables, one per question block. They are not one instrument:
each block has its own stem ("The following aspects attract me to ...", "The
following aspects have been barriers ...", "How much do you agree with the
following statements"), and merging them would imply a single scale.
  * attraction   -- 5 items, 1-5 strongly agree .. strongly disagree
  * barriers     -- 7 items, same 1-5
  * pandemic     -- 8 items, same 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("wldat_dryad.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

ATTRACT = ["attract_social", "attract_compete", "attract_stress",
           "attract_strength", "attract_fit"]
BARRIER = ["barrier_finance", "barrier_family", "barrier_work",
           "barrier_gym", "barrier_coach", "barrier_injury",
           "barrier_health"]
# pan_pa is NOT in this block: its scale is "a lot more .. a lot less", not
# the agree/disagree scale the eight statements share.
PANDEMIC = ["pan_newpa", "pan_misspa", "pan_time", "pan_alone", "pan_online",
            "pan_healthpa", "pan_mentalpa", "pan_regime"]

BLOCKS = [(ATTRACT, "huebner_2021_weightlifting_attraction"),
          (BARRIER, "huebner_2021_weightlifting_barriers"),
          (PANDEMIC, "huebner_2021_weightlifting_pandemic")]

COV_MAP = {"region": "cov_region", "agegrp": "cov_age_band",
           "sex": "cov_sex"}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # id (a platform response ID, replaced below), country-level region, age
    # band and sex. No name, email, date of birth, address or postal code.
    assert set(text_cols) == {"id", "region", "agegrp", "sex"}, text_cols


def main() -> None:
    df = pd.read_csv(SRC, low_memory=False)
    print("raw shape", df.shape)
    pii_screen(df)

    assert df["id"].is_unique, "source id is not one row per athlete"
    assert df["id"].astype(str).str.match(r"^R_").all(), \
        "source id is not the expected Qualtrics R_ form"
    df["id"] = range(1, len(df) + 1)

    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    items = ATTRACT + BARRIER + PANDEMIC
    for c in items:
        assert c in df.columns, c

    skipped = {
        "pan_pa": "single question on its own 'a lot more .. a lot less' "
                  "scale, not the agree/disagree scale of the eight pandemic "
                  "statements; one item is below the 3-item floor",
        "post_regime": "single 3-category expectation question (decrease / "
                       "continue / increase), its own format, below the floor",
        "priority": "single 3-category change question (decrease / same / "
                    "increase), its own format, below the floor",
    }
    used = {"id"} | set(COV_MAP) | set(covs) | set(items)
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")

    for cols, table in BLOCKS:
        long = df[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        write(long, table, OUT)


def write(long: pd.DataFrame, table: str, out: Path) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), "fractional Likert values"
    long["resp"] = long["resp"].astype(int)
    cols = ["id", "item", "resp"] + [c for c in long.columns
                                     if c.startswith("cov_")]
    long = long[cols].sort_values(["id", "item"])
    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(out / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
