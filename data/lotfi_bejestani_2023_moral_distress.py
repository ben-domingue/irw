"""
Five instruments administered to 500 Iranian psychiatric nurses: perceived
organizational justice, moral sensitivity, moral courage, moral distress and
burnout (Iran, May-September 2020).

Source: Lotfi-Bejestani, S., Atashzadeh-Shoorideh, F., Ghafouri, R., Nasiri, M.,
        Ohnishi, K., & Ghadirian, F. (2023). Is there any relationship between
        nurses' perceived organizational justice, moral sensitivity, moral
        courage, moral distress and burnout? BMC Nursing, 22, 363.
DOI: 10.1186/s12912-023-01536-x
Data: https://doi.org/10.6084/m9.figshare.24264663.v1 (Additional file 1,
        12912_2023_1536_MOESM1_ESM.xls -- a BIFF2 .xls, which is why pandas
        cannot sniff it and the triage flagged it `recoverable_format`; it reads
        with engine="xlrd")
License: CC BY 4.0 (the figshare record for the article's Additional file 1;
        the article is CC BY per Europe PMC's core record, license "cc by")
Item text: NOT shipped. The deposit is a bare .xls -- a format with no variable
        or value label levels at all, so neither was missed -- and its columns
        are a1..a15, b1..b19, c1..c20, d1..d15, e1..e25 with no glossary. The
        five instruments ARE identified (below), and four of the five are
        published scales whose wording is one hop away in the citing papers:
        Niehoff & Moorman (1993) POJ, Han et al. (2010) MS, Sekerka et al. MC,
        Ohnishi et al. (2018) MD, Kristensen et al. (2005) Copenhagen Burnout
        Inventory. All five were administered in PERSIAN, so a later pass also
        owes the administered wording and the 2026-09-08 translated-adaptation
        rights question, not just the English originals. Paper hunt plus a
        register ruling; recorded rather than done.

WHICH BLOCK IS WHICH INSTRUMENT -- established, not assumed. The column letters
say nothing. Three independent facts line each block up with the paper, and they
agree:

1. Item counts. The paper gives POJ 20 items, MS 25, MC 15, MD 15, CBI 19. The
   blocks are c=20, e=25, a=15, d=15, b=19. That alone fixes c, e and b, and
   leaves only MC-vs-MD between a and d.
2. The deposit's OWN subscale totals, which this script drops but reads first.
   `AA1/AA2/AA3` have means 18.58/14.70/11.90, exactly the paper's three MD
   subscales; `DD1..DD5` have means 10.35/10.78/10.91/10.61/10.46, exactly the
   paper's five MC subscales; `EE1..EE3` 19.72/19.14/21.02, the paper's three MS
   subscales; `BB2/BB3/BB4` 146.79/142.78/278.73, the paper's burnout subscales;
   and `CC1/CC2/CC3` span 5 items, 6 items and 9 items, which is Niehoff &
   Moorman's distributive/procedural/interactional split. Summing each block's
   items reproduces the matching total: block a 45.07 against A's 45.18, block d
   52.90 against DD's 53.16, block e 59.66 against EE's 59.81 (the small gaps
   are the sentinel cells this script drops and those totals do not).
3. Response ranges. MD is a 0-6 scale with 0 = "not distressed or not
   experienced"; MC is 1-7 with no zero. Block a uses 0 (1,282 times), block d
   never does. So a = MD and d = MC, which is what (2) already said.

Taken together: a = moral distress, b = burnout (CBI), c = organizational
justice, d = moral courage, e = moral sensitivity.

SENTINELS. 8 is a missing code in every item block and 9 is a second one in
block c -- both lie outside each instrument's documented range (POJ 1-5, MS 0-4,
MC 1-7, MD 0-6, CBI {0,25,50,75,100}) and both are rare where the real extreme
categories are not (block c: 265 fives against 4 eights and 53 nines). They are
dropped per block against that documented range rather than globally.

ONE ANOMALY, SHIPPED AS OBSERVED AND FLAGGED PUBLICLY. Block a (moral distress)
holds 266 responses of 7, on a scale the paper documents as 0-6. 7 is far too
common to read as a missing code -- the sentinel 8 appears 31 times -- and the
deposit's own MD total runs to 96 where 15 items x 6 would cap at 90, so the 7s
are in the depositor's own scoring too. Something about the Persian
administration's coding is not what the paper describes, and nothing in the
deposit resolves it. The responses ship as stored, with an itemtext_issues.qmd
callout, rather than being silently dropped or silently recoded.

The deposit and the paper also disagree slightly on the demographics: the file
has 114 men and 378 women where Table 2 reports 112 and 377, and 429 bachelor's
where Table 2 reports 426 -- a two-or-three-case difference per variable,
unexplained. The covariates ship as the file has them.

PII: none. Every column is numeric (dtypes are int64/float64 only), there is no
identifier, name, date, free-text or geographic column, and the screen below
prints its denominator.

Output: five tables, 46,851 responses.
  * lotfi_bejestani_2023_moral_distress    -- 15 items, resp 0-7 (see above)
  * lotfi_bejestani_2023_burnout           -- 19 items, resp 0/25/50/75/100
  * lotfi_bejestani_2023_org_justice       -- 20 items, resp 1-5
  * lotfi_bejestani_2023_moral_courage     -- 15 items, resp 1-7
  * lotfi_bejestani_2023_moral_sensitivity -- 25 items, resp 0-4
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("12912_2023_1536_MOESM1_ESM.xls"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# block letter -> (output table, item count, permitted response values)
BLOCKS = {
    # 0-6 per Ohnishi et al. (2018); 7 is observed 266 times and is kept, see
    # the module docstring. 8 is the sentinel.
    "a": ("lotfi_bejestani_2023_moral_distress", 15, [0, 1, 2, 3, 4, 5, 6, 7]),
    "b": ("lotfi_bejestani_2023_burnout", 19, [0, 25, 50, 75, 100]),
    "c": ("lotfi_bejestani_2023_org_justice", 20, [1, 2, 3, 4, 5]),
    "d": ("lotfi_bejestani_2023_moral_courage", 15, [1, 2, 3, 4, 5, 6, 7]),
    "e": ("lotfi_bejestani_2023_moral_sensitivity", 25, [0, 1, 2, 3, 4]),
}

# The paper's Table 3 subscale means, used only to CHECK the block mapping.
# (block letter, deposit total column, expected mean of that total)
MAPPING_CHECKS = [("a", "A", 45.18), ("d", "DD", 53.16), ("e", "EE", 59.81)]

# Deposit-computed totals and subscale sums, dropped. They are also inflated by
# the sentinel cells, which the depositor summed rather than excluded.
TOTALS = ["BB", "BB1", "BB2", "BB3", "BB4", "CC", "CC1", "CC2", "CC3",
          "DD", "DD1", "DD2", "DD3", "DD4", "DD5", "EE", "EE1", "EE2", "EE3",
          "A", "AA1", "AA2", "AA3"]

# Covariates whose documented category set makes 9 impossible, so 9 is missing.
# `workingyears` and `phscologicworkingears` are YEARS, where 9 is a real
# value, so they are deliberately not in this set.
COV_MAP = {
    "age": ("cov_age", True),
    "gender": ("cov_gender", True),
    "mariage": ("cov_marital_status", True),
    "education": ("cov_education", True),
    "job": ("cov_job", True),
    "workingyears": ("cov_working_years", False),
    "phscologicworkingears": ("cov_psych_ward_years", False),
    "workingtimeinweek": ("cov_working_hours_band", True),
    "emloying": ("cov_employment_type", True),
    "workshift": ("cov_work_shift", True),
    "eticalcours": ("cov_ethics_course", True),
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"
    for banned in ("name", "email", "mail", "phone", "birth", "id", "code",
                   "city", "address", "hospital"):
        bad = [c for c in df.columns if banned == c.lower()]
        assert not bad, f"possible identifier column: {bad}"


def main() -> None:
    df = pd.read_excel(SRC, engine="xlrd")
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 500, len(df)

    cols = {b: [f"{b}{i}" for i in range(1, n + 1)]
            for b, (_t, n, _p) in BLOCKS.items()}
    for b, cs in cols.items():
        assert all(c in df.columns for c in cs), (b, cs)

    # The mapping check from the docstring, run rather than asserted in prose.
    for b, total_col, expected in MAPPING_CHECKS:
        got = df[total_col].mean()
        assert abs(got - expected) < 0.05, (total_col, got, expected)
        clean = df[cols[b]].where(df[cols[b]].isin(BLOCKS[b][2]))
        block_sum = clean.sum(axis=1).mean()
        print(f"block {b} -> {BLOCKS[b][0]}: deposit total {total_col} mean "
              f"{got:.2f} matches the paper's {expected:.2f}; summing block "
              f"{b}'s own items gives {block_sum:.2f}")
        assert abs(block_sum - expected) < 1.0, (b, block_sum, expected)
    assert 0 in df[cols["a"]].values and 0 not in df[cols["d"]].values, \
        "the MD/MC separation rests on block a using 0 and block d not"

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, (dst, nine_is_missing) in COV_MAP.items():
        assert src in df.columns, src
        col = df[src]
        df[dst] = col.replace(9, np.nan) if nine_is_missing else col
    covs = [dst for dst, _ in COV_MAP.values()]

    accounted = (set(COV_MAP) | set(covs) | set(TOTALS) | {"id"}
                 | {c for cs in cols.values() for c in cs})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"skipped {len(TOTALS)} depositor-computed total/subscale column(s): "
          f"{TOTALS}")

    for b, (table, n, permitted) in BLOCKS.items():
        long = df[["id"] + covs + cols[b]].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        print(f"{table}: dropped {before - len(long)} cell(s) of {before} "
              f"outside the documented response set {permitted}")
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
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
