"""
130 tenth-grade chemistry students in Germany rating SMOKEChem, a web-based
learning environment with AI-supported and peer feedback for scientific
argumentation, on three instruments administered in the same lesson: chatbot
usability (BUS-11), technology acceptance (TAM), and cognitive load.

Source: Leppla, L. C., Spanier, M., & Seibert, J.-N. (2026). Technology
        acceptance, chatbot usability, and cognitive load of secondary school
        students in the SMOKEChem pilot study (Version 1) [Data set]. Zenodo.
DOI: 10.5281/zenodo.22208333
Data: https://zenodo.org/records/22208333 -- SMOKEChem_Data.xlsx, sheet
        "SMOKEChem_Data", with sheet "Items" as the deposit's own instrument
        and SMOKEChem_Data_Documentation.docx
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id =
        cc-by-4.0)
Item text: NOT shipped, and it is in hand -- the workbook's "Items" sheet
        gives all 34 items in the administered German AND in the depositors'
        own English, each against its data column name, so the extraction
        itself is cheap and the translation is the authors' rather than
        IRW-generated. It is RIGHTS, not recoverability, that holds it:
        - the cognitive-load block is the Leppink, Paas, Van der Vleuten et
          al. Cognitive Load Scale, which is registered `hold` in
          itemtext/instrument_rights_register.csv (2026-10-18, #3077, under
          Ben's 2026-10-15 silence ruling);
        - the BUS-11 and TAM blocks are the depositors' own
          SMOKEChem-specific adaptations ("Using the SMOKEChem web
          application improves my arguments in science lessons") published
          under their CC BY, which is exactly the shape of class ruling R16
          -- but R16 is deliberately non-sweeping ("a new table needs its own
          triage showing the same shape"), and the upstream triage for
          Borsci et al.'s BUS-11 and for Davis's TAM has not been done.
        Named as a ruling request in automated_finding/TODO.md rather than
        decided here.

This deposit was flagged `pii_suspected` on a column named `Code` holding
"full postal codes in the values". It does not: `Code` holds the
self-generated pseudonymous participant codes used in German classroom
research -- a letter, a two-digit day, and two initials ("J27SE", "K29Ab",
"M17MN"). 106 of 130 are five characters, exactly one is all digits, and a
German postal code is five DIGITS. The postal-code detector
(`_holds_full_postal_codes`) over-fires on this shape; recorded in BATCH_LOG
so the next hit on a `Code` column is read before it is skipped. The column is
still not carried forward: a self-generated code encodes a birth day and
initials by construction, and the row index serves as `id` perfectly well.

`Number` is NOT usable as an id either -- it has 111 distinct values over 130
rows. The row index is used.

The cognitive-load block ships as ONE table although its extraneous-load items
observe 1-4 while the intrinsic and germane items observe 1-5. That is three
negatively-worded items nobody answered at the top of the scale, not a
separate instrument: all eight sit under one heading ("Kognitive
Belastung/Cognitive Load") in the deposit's own Items sheet, and an observed
range does not establish a permitted response set.

Output: three tables, one per instrument.
  leppla_2026_smokechem_bot_usability  11 items, 1-5, 130 ids, 1430 responses
  leppla_2026_smokechem_acceptance     15 items, 1-5, 130 ids, 1950 responses
  leppla_2026_smokechem_cognitive_load  8 items, 1-5, 130 ids, 1040 responses
Skipped: the twelve M* subscale means (composites) and the four open-ended
German/English reflection items on the Qualitative_Responses sheet.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("SMOKEChem_Data.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BUS11 = ["CBPA1", "CBPA2", "CBPQ1", "CBPQ2", "CBPQ3", "CBPQC1", "CBPQC2",
         "CBPQC3", "CBPQC4", "CBPP", "CBTR"]
TAM = ["TAMPU1", "TAMPU2", "TAMPU3", "TAMPU4", "TAMBI1", "TAMBI2",
       "TAMPEOU1", "TAMPEOU2", "TAMPEOU3", "TAMEoF1", "TAMEoF2", "TAMEoF3",
       "TAMATU1", "TAMATU2", "TAMATU3"]
COGLOAD = ["CLPICL1", "CLPICL2", "CLPGCL1", "CLPGCL2", "CLPGCL3",
           "CLPECL1", "CLPECL2", "CLPECL3"]

BLOCKS = [("bot_usability", BUS11), ("acceptance", TAM),
          ("cognitive_load", COGLOAD)]

MEANS = ["MCBPA", "MCBPQ", "MCBPQC", "MCBPP", "MCBTR", "MPU", "MBI",
         "MPEOU", "MEoF", "MATU", "MICL", "MGCL", "MECL"]

COV_MAP = {"Age": "cov_age",
           "Gender": "cov_gender",
           "grade level": "cov_grade_level",
           "school type": "cov_school_type",
           "course": "cov_course",
           "current chemistry grade": "cov_chemistry_grade"}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(text_cols) > 0, "screen selected no columns"
    assert set(text_cols) == {"Code", "Gender", "school type", "course"}, \
        text_cols
    code = df["Code"].astype(str)
    all_digits = int(code.str.fullmatch(r"\d{5}").sum())
    print(f"  Code: {len(code)} values, {all_digits} of them a five-digit "
          f"string (the shape of a German postal code); e.g. "
          f"{list(code[:4])} -- self-generated participant codes, not "
          "postal codes. Dropped anyway, not carried forward in any form.")
    assert all_digits <= 2, \
        "Code really does look like postal codes; re-triage before shipping"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="SMOKEChem_Data")
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 130, len(df)

    # The deposit's own Items sheet names every data column; use it to assert
    # the item lists here are the instrument's, not a guess from prefixes.
    items_sheet = pd.read_excel(SRC, sheet_name="Items", header=None)
    named = set(items_sheet[0].dropna().astype(str).str.strip())
    for c in BUS11 + TAM + COGLOAD:
        assert c in df.columns, c
        assert c in named, f"{c} is not named in the deposit's Items sheet"
        vals = sorted(df[c].dropna().unique())
        assert set(vals) <= {1, 2, 3, 4, 5}, (c, vals)

    print(f"  Number has {df['Number'].nunique()} distinct values over "
          f"{len(df)} rows, so it is not a respondent id; using the row index")

    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src].values
    covs = list(COV_MAP.values())

    skipped = {c: "subscale mean over the items of one block -- a composite, "
                  "not a response" for c in MEANS}
    skipped["Code"] = ("self-generated pseudonymous participant code "
                       "(letter + day of birth + initials); not carried "
                       "forward in any form")
    skipped["Number"] = ("administrative row number with 111 distinct values "
                         "over 130 rows; the row index is used as id")
    used = set(COV_MAP) | set(BUS11) | set(TAM) | set(COGLOAD)
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped column {c}: {why}")
    print("  skipped sheet Qualitative_Responses: four open-ended reflection "
          "items in German with the depositors' English, free text rather "
          "than item responses")

    wide = pd.concat([out, df[BUS11 + TAM + COGLOAD]], axis=1)
    for name, cols in BLOCKS:
        long = wide[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        table = f"leppla_2026_smokechem_{name}"
        assert long["id"].nunique() >= 100, (table, long["id"].nunique())
        assert long["item"].nunique() == len(cols)
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
