"""
PANAS, information-source use and lockdown lifestyle change in 333 adults
surveyed during the first weeks of the COVID-19 pandemic (Spain, April-May
2020). The questionnaire was offered in Spanish and English; 308 of the 333
answered in Spanish.

Source: Andreu-Sánchez, C., & Martín-Pascual, M. Á. (2023). Data - Positive
        and Negative Affect Schedule in early COVID-19 pandemic [Dataset].
        Zenodo.
DOI: 10.5281/zenodo.8057093
Data: https://zenodo.org/records/8057093 (Data_PANAS_early_Covid-19_v2.xlsx,
        sheet "ENGLISH" -- see below)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id =
        cc-by-4.0)
Item text: NOT shipped. The deposit carries the full instrument twice (the
        column headers are the item wording, and two further sheets hold the
        questionnaire verbatim in English and Spanish), so this is a rights
        hold, not an availability gap: the 20 affect items are the Positive
        and Negative Affect Schedule (PANAS; Watson, Clark & Tellegen 1988),
        identified from the adjective list, and the PANAS is registered
        `block` in itemtext/instrument_rights_register.csv (rows 33 and 56,
        2026-10-15 counsel + Ben). The 10 information-source items and the 6
        lifestyle items are study-authored and would be shippable, but their
        wording is in the same sheets and they are not worth a separate pass.

The workbook's ENGLISH and SPANISH sheets are the SAME 333 respondents, not
two samples -- identical timestamps and identical cell values, with the
headers and the Yes/No labels translated. Only one is read. The Spanish sheet
is the as-administered wording for most respondents, which matters for item
text and not for the responses.

Output: three tables. The three blocks are three different instruments on two
different response formats, so they do not merge:
  * panas              -- 20 affect adjectives, 1-5
  * information        -- 10 information sources, 1-5
  * lifestyle          -- 6 lockdown lifestyle statements, Yes/No -> 1/0
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("Data_PANAS_early_Covid-19_v2.xlsx"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

COV_MAP = {
    "Gender": "cov_gender",
    "Age": "cov_age_band",
    "Education": "cov_education",
    "Occupation": "cov_occupation",
    "At the moment, during Covid-19 pandemic, I am in situation of…":
        "cov_lockdown_situation",
    "What is your nationality?": "cov_nationality",
    "Language in which the questionnaire was answered": "cov_language",
}

# The item code is the source's own bracketed label, slugified -- never a
# positional index. The final PANAS header is corrupted in the deposit
# ("Emotions: [Afraid]+AL:ARAS1H:AR"); the bracketed label is intact, which is
# what the code is taken from.
BLOCKS = [
    ("Emotions", 20, "andreu_sanchez_2023_panas"),
    ("Information", 10, "andreu_sanchez_2023_information_sources"),
    ("Sports", 6, "andreu_sanchez_2023_lifestyle"),
]
YESNO = {"Sí": 1, "Si": 1, "Yes": 1, "No": 0}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # No name, email, date of birth, phone or national ID column: age is a
    # band, and the one geographic column is dropped below rather than shipped.
    for banned in ("name", "nombre", "email", "mail", "phone", "dni"):
        bad = [c for c in text_cols if banned in c.lower()]
        assert not bad, f"possible identifier column: {bad}"


def slug(header: str) -> str:
    m = re.search(r"\[(.+?)\]", header)
    assert m, f"no bracketed label in {header!r}"
    return re.sub(r"[^a-z0-9]+", "_", m.group(1).lower()).strip("_")


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="ENGLISH")
    print("raw shape", df.shape)
    pii_screen(df)

    blocks = {p: [c for c in df.columns if str(c).startswith(p)]
              for p, _n, _t in BLOCKS}
    item_cols = [c for cols in blocks.values() for c in cols]

    # Drop rows with no responses at all (the sheet carries blank trailing
    # rows); the Spanish sheet's 333 rows are the real respondent count.
    before = len(df)
    df = df.dropna(subset=item_cols, how="all").reset_index(drop=True)
    print(f"dropped {before - len(df)} all-blank row(s); {len(df)} respondents")
    assert len(df) == 333, len(df)

    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    used = {"id"} | set(COV_MAP) | set(covs) | set(item_cols)
    skipped = {
        "Timestamp": "questionnaire submission time, not an item",
        "What city are you in now?": "free-text city of residence, 133 "
            "distinct values -- a geographic identifier, dropped under the "
            "2026-10-20 ruling (geographic codes are not carried into IRW in "
            "any form) rather than shipped as a covariate",
    }
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")

    for prefix, n, table in BLOCKS:
        cols = blocks[prefix]
        assert len(cols) == n, (prefix, len(cols), n)
        codes = [slug(c) for c in cols]
        assert len(set(codes)) == n, (prefix, codes)
        long = df[["id"] + covs + cols].rename(
            columns=dict(zip(cols, codes)))
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        if prefix == "Sports":
            vals = set(long["resp"].dropna().unique())
            assert vals <= set(YESNO), vals
            long["resp"] = long["resp"].map(YESNO)
        write(long, table, OUT)


def write(long: pd.DataFrame, table: str, out: Path) -> None:
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(float)
    assert not (long["resp"] % 1 != 0).any(), "fractional values"
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
