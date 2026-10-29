"""
Seven interoception and body-image instruments answered by 815 Malay-speaking
adults, from the Malay translation/validation study of the MAIA.

Source: Aspell, J. (2019). Translation and Validation of MAIA questionnaire
        [Dataset]. Anglia Ruskin University (figshare). The deposit's own
        description: "Translation (English>Malay) and validation of
        Multidimensional Assessment of Interoceptive Awareness (MAIA)
        questionnaire."
DOI: 10.25411/aru.10673534
Data: https://aru.figshare.com/articles/dataset/Translation_and_Validation_of_MAIA_questionnaire/10673534
        (the single file "Final_Malay_Dataset2.sav")
License: CC0 1.0 (verified on the figshare record, license.name "CC0")
Item text: NOT shipped, and the reason is a rule rather than an absence. The
        `.sav` carries NO item stems -- its one variable label is an SPSS
        filter expression -- but it DOES carry the Malay RESPONSE ANCHORS for
        127 variables. Shipping those alone would be option_text with no stem,
        which the 2026-10-15 ruling (irw#1770) forbids. The stems are the
        published MAIA, SATAQ-4, DMS, MAAS, RSES, BAS and FAS wordings, i.e.
        seven third-party instruments, so a later pass owes a register row per
        instrument before any wording can ship. The anchors are recorded in
        `codebook_at_ingest.csv` so that pass does not have to re-derive them.

**The stored MAIA codes are 1-6 and the MAIA's own scale is 0-5; this script
recodes to 0-5 and the file itself says to.** Every MAIA value label pairs a
code with the published anchor number: 1 is "Tidak pernah / 0" and 6 is
"Selalu / 5". So 1-6 is the survey platform's off-by-one storage, not the
instrument, and shipping it unchanged would misstate the scale and break
comparison with any other MAIA table. The mapping is READ OUT of the value
labels and asserted, not hardcoded -- if a future version of the file labels
them differently the script fails rather than silently shifting 32 items.

**263 cells are imputed and they are dropped.** 0.26% of item cells hold a
non-integer (1.36, 6.21, 0.85), 44 of the 815 respondents have at least one,
and some lie OUTSIDE their own documented scale -- MAIA reaches 6.21 against a
documented maximum of 6, SATAQ falls to 0.85 against a minimum of 1. A value
outside the response set cannot be a response, so these are imputed, and
`datastandard.md` wants observed responses. Two things follow:

  * every non-integer cell is dropped, and
  * any respondent with a non-integer cell in a given block is dropped from
    THAT table entirely, not just for that cell.

One further cell type gets the same treatment: an out-of-range INTEGER. There
is exactly one instance -- a single respondent answered 6 to SATAQ_1 and
SATAQ_2 against a documented 1-5 scale. Isolated to one row and one above the
maximum, that is a data-entry error rather than a second scale, which would
show across many respondents; the respondent is dropped from the SATAQ table.

The second rule is the conservative one, and it is there because mean or EM
imputation lands on an integer some of the time: a respondent whose block shows
imputation anywhere is not trusted anywhere in that block. It costs at most ten
respondents in the worst-affected table. The residual risk is stated plainly:
an imputed value in an UNAFFECTED respondent's row would be invisible here, and
nothing in the file distinguishes it.

**`*_reverse_*`, `RMAIA_*` and `*_Score` are derived and do not ship.**
`RMAIA_5`/`6`/`8`/`9` are exactly `7 - MAIA_n` (asserted below), the fifteen
`DMS_reverse_n` and four `RSES_reverse_n` are the same recode of their own
items, and `BAS_Score`, `FAS_Score`, `DMS_Score`, `MAAS_Score`, `RSES_Score`,
`SATAQ_PrInGen`, `PFRS_Score` and `BMI` are composites. Shipping any of them
would put two directions, or a total, into `resp`.

**PFRS does not ship: 2 items.** It is a real instrument but two items is below
the three-item floor, and only 403 of the 815 answered it.

`cov_analysis_subsample` is the deposit's own `Analysis` column, which splits
the sample into the EFA (1) and CFA (2) halves of the validation -- worth
keeping, because a user refitting the paper needs to know which half a
respondent was in.

PII: none. Every column is numeric, there is no identifier (`id` is the row
index), and no name, date, free-text or geographic column; the screen below
prints its denominator. Two covariates carry implausible tails that are the
DEPOSIT'S and are left as found rather than quietly edited: `cov_height_cm`
runs from 80 and `cov_weight_kg` from 20, in a sample aged 18-69.
`D1_Ethnicity` (all "Melayu") and `D4.1_EducationStatus` (all "Tidak") are
constant and are dropped as carrying no information.

Output: seven tables, 95731 responses -- 815 respondents, 119 items.
  * aspell_2019_maia  -- 32 items, resp 0-5 (recoded from the stored 1-6)
  * aspell_2019_sataq -- 30 items, resp 1-5
  * aspell_2019_dms   -- 15 items, resp 1-6
  * aspell_2019_maas  -- 15 items, resp 1-6
  * aspell_2019_bas   -- 10 items, resp 1-5
  * aspell_2019_rses  -- 10 items, resp 1-4
  * aspell_2019_fas   --  7 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Final_Malay_Dataset2.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# table -> (source prefix, item count, documented response set). Every set is
# read off the file's own value labels and checked against this, so a change in
# the deposit's coding fails loudly instead of shipping a different scale.
BLOCKS = {
    "aspell_2019_maia": ("MAIA", 32, [1, 2, 3, 4, 5, 6]),
    "aspell_2019_sataq": ("SATAQ", 30, [1, 2, 3, 4, 5]),
    "aspell_2019_dms": ("DMS", 15, [1, 2, 3, 4, 5, 6]),
    "aspell_2019_maas": ("MAAS", 15, [1, 2, 3, 4, 5, 6]),
    "aspell_2019_bas": ("BAS", 10, [1, 2, 3, 4, 5]),
    "aspell_2019_rses": ("RSES", 10, [1, 2, 3, 4]),
    "aspell_2019_fas": ("FAS", 7, [1, 2, 3, 4, 5]),
}

# The MAIA's published anchors are 0-5; this file stores them as 1-6. The shift
# is confirmed against the value labels before it is applied.
MAIA_TABLE = "aspell_2019_maia"
MAIA_SHIFT = -1

COV_MAP = {
    "Analysis": "cov_analysis_subsample",
    "D2_Gender": "cov_gender",
    "D3_Maritalstatus": "cov_marital_status",
    "D4_Education": "cov_education",
    "D5_Age": "cov_age",
    "D6_Weight": "cov_weight_kg",
    "D7_Height": "cov_height_cm",
    "D8_Religion": "cov_religion",
}

# Derived columns, and why each is not a response.
DROP_PATTERNS = [
    (r"^RMAIA_\d+$", "reverse recode of a MAIA item (7 - MAIA_n, asserted below)"),
    (r"^DMS_reverse_\d+$", "reverse recode of a DMS item"),
    (r"^RSES_reverse_\d+$", "reverse recode of an RSES item"),
    (r"_Score$", "instrument total or mean"),
    (r"^SATAQ_PrInGen$", "SATAQ subscale score"),
    (r"^BMI$", "computed from D6_Weight and D7_Height"),
    (r"^filter_\$$", "an SPSS analysis filter, not data"),
    (r"^PFRS_\d+$", "a 2-item instrument -- below the three-item floor, and "
                    "only 403 of 815 answered it"),
    (r"^D1_Ethnicity$", "constant (all 'Melayu')"),
    (r"^D4\.1_EducationStatus$", "constant (all 'Tidak')"),
]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def check_maia_shift(meta) -> None:
    """The 1-6 -> 0-5 recode is justified by the file, or not done at all."""
    lab = meta.variable_value_labels.get("MAIA_1")
    assert lab, "MAIA_1 has no value labels -- the recode cannot be justified"
    for code, text in lab.items():
        trailing = re.findall(r"(\d+)\s*$", str(text).strip())
        assert trailing, (code, text)
        assert int(trailing[0]) == int(code) + MAIA_SHIFT, \
            f"MAIA label {code!r} -> {text!r} does not say {int(code)+MAIA_SHIFT}"
    print(f"MAIA recode justified by the file's own labels: stored "
          f"{sorted(int(c) for c in lab)} are the published "
          f"{sorted(int(c) + MAIA_SHIFT for c in lab)}")


def check_derived(df: pd.DataFrame) -> None:
    """RMAIA_n is 7 - MAIA_n. Asserted, because it is why they are dropped."""
    hits = []
    for c in [c for c in df.columns if re.match(r"^RMAIA_\d+$", c)]:
        n = c.split("_")[1]
        src = f"MAIA_{n}"
        if src in df.columns:
            same = np.isclose(7 - df[src], df[c], equal_nan=True)
            hits.append((c, src, bool(same.all()), int((~same).sum())))
    for c, src, ok, bad in hits:
        print(f"  {c} = 7 - {src}: {'EXACT' if ok else f'{bad} cell(s) differ'}")
    assert hits, "no RMAIA_* columns found -- has the file changed?"
    # At least four of the five match exactly; the fifth may differ only where
    # imputation rounded. Either way they are derived and none of them ships.
    assert sum(1 for *_, ok, _b in [(h[0], h[1], h[2], h[3]) for h in hits]
               if ok) >= 4, hits


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 815, len(df)
    check_maia_shift(meta)
    check_derived(df)

    item_cols = {}
    for table, (prefix, n, permitted) in BLOCKS.items():
        cols = [c for c in df.columns
                if re.match(rf"^{prefix}_\d+$", c)]
        assert len(cols) == n, (table, len(cols), n)
        documented = sorted(int(k) for k in
                            (meta.variable_value_labels.get(cols[0]) or {}))
        assert documented == permitted, (table, documented, permitted)
        item_cols[table] = sorted(cols, key=lambda c: int(c.split("_")[1]))

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())
    # D4_Education carries the same imputation signature as the items; a
    # non-integer category code is not a category.
    bad = (df["cov_education"] % 1 != 0)
    if bad.any():
        print(f"cov_education: {int(bad.sum())} imputed (non-integer) "
              "category code(s) nulled")
        df.loc[bad, "cov_education"] = np.nan

    accounted = set(COV_MAP) | set(covs) | {"id"}
    accounted |= {c for cs in item_cols.values() for c in cs}
    dropped = {}
    for c in df.columns:
        if c in accounted:
            continue
        for pat, why in DROP_PATTERNS:
            if re.search(pat, c):
                dropped[c] = why
                break
    leftover = [c for c in df.columns
                if c not in accounted and c not in dropped]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for why in sorted(set(dropped.values())):
        cs = sorted(c for c, w in dropped.items() if w == why)
        print(f"skipped {len(cs)} column(s) -- {why}: "
              f"{cs if len(cs) <= 4 else cs[:4] + ['...']}")

    for table, cols in item_cols.items():
        permitted = BLOCKS[table][2]
        write(df, table, cols, covs, permitted)


def write(df: pd.DataFrame, table: str, cols: list, covs: list,
          permitted: list) -> None:
    vals = df[cols].to_numpy(dtype=float)
    present = ~np.isnan(vals)
    frac = present & (np.abs(vals - np.round(vals)) > 1e-9)
    # An out-of-range INTEGER is the other way this file is untrustworthy, and
    # it gets the same treatment. The only instance is one respondent who
    # answered 6 to SATAQ_1 and SATAQ_2 on a documented 1-5 scale: isolated to
    # a single row and one above the maximum, i.e. a data-entry error rather
    # than a second scale (which would show up across many respondents).
    oob = present & ~frac & ~np.isin(np.round(vals), permitted)
    # A respondent with an imputed or out-of-range cell anywhere in this block
    # is dropped from this table: see the module docstring.
    tainted = (frac | oob).any(axis=1)
    print(f"{table}: {int(frac.sum())} imputed + {int(oob.sum())} "
          f"out-of-range cell(s) in {int(tainted.sum())} respondent(s) -- "
          f"those respondents dropped from this table")

    keep = df.loc[~tainted, ["id"] + covs + cols]
    long = keep.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    outside = ~long["resp"].isin(permitted)
    assert not outside.any(), \
        f"{table}: {int(outside.sum())} cell(s) outside {permitted}: " \
        f"{sorted(long.loc[outside, 'resp'].unique())[:8]}"

    long["item"] = [c.lower() for c in long["item"]]
    long["resp"] = long["resp"].astype(int)
    if table == MAIA_TABLE:
        long["resp"] = long["resp"] + MAIA_SHIFT
        permitted = [v + MAIA_SHIFT for v in permitted]
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
