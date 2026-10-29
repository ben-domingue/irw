"""
AI literacy, AI-TPACK, self-efficacy and technology acceptance in 702 Turkish
pre-service mathematics teachers.

Source: Mersin, N. (2025). AI Literacy and Technology Acceptance Dataset
        (Pre-service Mathematics Teachers, N=702) [Dataset]. Zenodo. The
        deposit's own description: "This dataset contains anonymized survey
        responses used to examine AI literacy, AI-TPACK, self-efficacy, and
        technology acceptance among pre-service mathematics teachers."
DOI: 10.5281/zenodo.17631162
Data: https://zenodo.org/records/17631162 ("Dataset.sav")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: NOT shipped and NOT recoverable from here. The `.sav` carries NO
        variable labels (0 of 29) and NO value labels (0 variables), which the
        script asserts, so both levels were checked and both are empty; there
        is no codebook, second file or questionnaire in the deposit. Where to
        look: the description says the data "supports the findings reported in
        the article" without naming or linking it, and the record carries no
        related identifier, so a later pass must find Mersin's AI-literacy /
        technology-acceptance paper on this 702-student sample first. The
        constructs are known (below) but no published instrument is identified
        for any of them, so there is nothing yet to check a rights register
        against.

**The four tables follow the DEPOSIT'S OWN grouping, not an inference from the
column prefixes.** The description names exactly four things — "AI literacy,
AI-TPACK, self-efficacy, and technology acceptance" — and the 29 columns fall
into exactly four groups that match: `AIL` (6), `TPCK` (5), `SE` (3), and then
`PU`/`PEU`/`ATT`/`BI` (3+4+4+4 = 15), which are the four canonical
technology-acceptance constructs: perceived usefulness, perceived ease of use,
attitude and behavioural intention.

So technology acceptance is ONE 15-item table rather than four three-or-four
item ones. The source groups it as one construct, all 15 items share the 1-5
response format and one administration, and the item codes keep the source
prefixes, so anyone who wants `pu`, `peu`, `att` and `bi` separately can take
them straight off the `item` column. Splitting on a prefix the deposit itself
treats as one thing would be reading structure into it that the source does not
claim.

PII: none. Every one of the 29 columns is numeric with no missing values at
all, there is no identifier, name, date, free-text or geographic column, and the
screen below prints its denominator.

Output: four tables, 20,358 responses -- 702 respondents, no missing data.
  * mersin_2025_technology_acceptance -- 15 items, resp 1-5
  * mersin_2025_ai_literacy           --  6 items, resp 1-5
  * mersin_2025_ai_tpack              --  5 items, resp 1-5
  * mersin_2025_ai_self_efficacy      --  3 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Dataset.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5]

# output table -> (source prefixes in order, expected item count)
BLOCKS = {
    "mersin_2025_ai_literacy": (["AIL"], 6),
    "mersin_2025_ai_tpack": (["TPCK"], 5),
    "mersin_2025_ai_self_efficacy": (["SE"], 3),
    "mersin_2025_technology_acceptance": (["PU", "PEU", "ATT", "BI"], 15),
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def numbered(df: pd.DataFrame, prefix: str) -> list:
    """Columns named <prefix><digits>, so PU does not swallow PEU."""
    return [c for c in df.columns
            if c.startswith(prefix) and c[len(prefix):].isdigit()]


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 702, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)} -- "
          "BOTH levels are empty, so there is no item wording to recover from "
          "this file")
    assert labelled == 0 and len(meta.variable_value_labels) == 0

    cols = {}
    for table, (prefixes, n) in BLOCKS.items():
        cs = [c for p in prefixes for c in numbered(df, p)]
        assert len(cs) == n, (table, len(cs), n, cs)
        cols[table] = cs

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)

    accounted = {"id"} | {c for cs in cols.values() for c in cs}
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print("no covariates: the deposit ships the 29 item columns and nothing "
          "else -- no demographics, no identifier, no computed scores")

    for table, cs in cols.items():
        codes = {c: c.lower() for c in cs}
        assert len(set(codes.values())) == len(cs), codes
        long = df[["id"] + cs].rename(columns=codes)
        long = long.melt(id_vars=["id"], var_name="item", value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(PERMITTED)]
        assert before == len(long), f"{table}: {before - len(long)} cell(s) " \
            f"outside {PERMITTED} -- the deposit had none, re-check the file"
        write(long, table)


def write(long: pd.DataFrame, table: str) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
