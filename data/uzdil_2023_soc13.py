"""
The 13-item Sense of Coherence scale answered by 1,175 Turkish adolescents --
ONE of the deposit's three instruments, because the other two are stored as
scores rather than as responses.

Source: Uzdil, N. (2023). The mediating effect of sense of coherence in the
        relationship between eating attitudes and self-esteem in adolescents
        [Dataset]. Mendeley Data. The deposit's own description: "This study
        aimed to examine the mediating effect of a sense of coherence in the
        relationship between eating attitudes and self-esteem in adolescents
        ... The sample of the study consisted of 1175 adolescents who met the
        inclusion criteria."
DOI: 10.17632/6nns35xpjw
Data: https://data.mendeley.com/datasets/6nns35xpjw (the single
        "ERGEN YEME 01.06.2022.sav")
License: CC BY 4.0 (verified on the DataCite record, rightsList "Creative
        Commons Attribution 4.0 International")
Item text: NOT shipped. The `.sav` has NO item stems -- only 12 of 75
        variables carry a variable label and every one of those is a
        demographic. It DOES carry response anchors for 48 variables, but
        anchors with no stem is option_text alone, which irw#1770 forbids. The
        SOC-13's wording is third-party (Antonovsky), so a register row is owed
        before any of it ships. Where to look: the article this deposit
        supports, which the Mendeley record does not link.

**Two of the three instruments do not ship, and the file's own value labels are
what prove it.** In both cases the labels document one scale and the stored
numbers are a different, narrower set -- so what is in the file is a score
computed from the response, and the response itself is gone:

  * `y1..y26` is the EAT-26. Its value labels document a SIX-point
    administered scale (1 "hiçbir zaman" / never, through 6 "her zaman" /
    always), but the stored values are 0-3 and 22,648 of the 30,550 cells --
    74% -- are 0. That is exactly the EAT-26's published scoring rule, which
    maps always/usually/often to 3/2/1 and collapses sometimes, rarely and
    never all to 0. Three of the six administered categories are therefore
    indistinguishable in the file, and no transformation recovers them.
  * `r1..r10` is the self-esteem scale. Its value labels document a FOUR-point
    scale (1 "çok yanlış" / very false, to 4 "çok doğru" / very true) and the
    stored values are 0/1 -- dichotomised.

`b1..b13` is the opposite case and is why this table exists: no value labels at
all, values spread across all seven points of 1-7, and `btop` equals their sum
exactly. Raw responses on the SOC-13's own 7-point format.

Also dropped as derived: `btop`, `anlas`, `yonet`, `anlam` (SOC total and its
three subscales), `yttop`, `bym`, `dya`, `oko` (EAT-26 total and subscales),
`rtop`, `ygrup` and `yygrp` (cutpoint groups), and `r123`, `r45`, `r910`
(combined indicators over already-dichotomised items). One oddity recorded
rather than smoothed over: `rtop` does NOT equal the sum of `r1..r10` -- they
agree on only 2.6% of rows -- so it is a total of something else again, which
is a further reason not to read the `r` block as responses.

**Three columns are dropped on identification grounds, and the respondents
being minors is why the first one goes.** `lise` names which of six specific
named schools in one Turkish town the respondent attends (Yozgat Lisesi,
Atatürk Sağlık Meslek Lisesi, ...); in a sample aged 13-19 that is a fine-grained
locator, so it goes. `eskidenyasyer` and `simdiyasadıgıyer` are settlement-size
codes (village / town / district / city / metropolis), i.e. geographic codes,
dropped under the 2026-10-20 ruling, which is drop-the-column and ship the rest.

PII: none beyond those three. Every column is numeric, there is no identifier
(`id` is the row index), and no name, date or free-text column; the screen below
prints its denominator.

Output: one table, 15,275 responses -- 1,175 adolescents x 13 items, resp 1-7.
  * uzdil_2023_soc13 -- 13 items, resp 1-7
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ERGEN YEME 01.06.2022.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "uzdil_2023_soc13"
ITEMS = [f"b{i}" for i in range(1, 14)]
PERMITTED = [1, 2, 3, 4, 5, 6, 7]

COV_MAP = {
    "yas": "cov_age",
    "cins": "cov_sex",
    "akaort": "cov_academic_average",
    "sınıf": "cov_grade",
    "yasakişi": "cov_lives_with",
    "ortgelir": "cov_family_income_band",
    "aileyapısı": "cov_family_structure",
    "babaegtımdurumu": "cov_father_education",
    "anneegitimdurumu": "cov_mother_education",
}

# The two blocks whose value labels disagree with their stored values. Each
# disagreement is CHECKED below, not asserted in prose: the point of the check
# is that it is the evidence these are scores and not responses.
SCORED_BLOCKS = {
    "y": (26, 6, [0, 1, 2, 3],
          "the EAT-26, whose labels document a 6-point administered scale but "
          "which stores its published 0-3 scoring -- always/usually/often map "
          "to 3/2/1 and sometimes/rarely/never all collapse to 0"),
    "r": (10, 4, [0, 1],
          "the self-esteem scale, whose labels document a 4-point scale but "
          "which stores a 0/1 dichotomisation"),
}

DROP = {
    "lise": "names which of six specific schools in one town the respondent "
            "attends, in a sample aged 13-19 -- a fine-grained locator",
    "eskidenyasyer": "settlement-size code, dropped under the 2026-10-20 "
                     "geographic ruling",
    "simdiyasadıgıyer": "settlement-size code, dropped under the 2026-10-20 "
                        "geographic ruling",
    "btop": "SOC-13 total (equals the sum of b1..b13 exactly)",
    "anlas": "SOC-13 comprehensibility subscale score",
    "yonet": "SOC-13 manageability subscale score",
    "anlam": "SOC-13 meaningfulness subscale score",
    "yttop": "EAT-26 total",
    "bym": "EAT-26 subscale score",
    "dya": "EAT-26 subscale score",
    "oko": "EAT-26 subscale score",
    "rtop": "a total over the r block -- and it does NOT equal the sum of "
            "r1..r10 (they agree on 2.6% of rows), so it totals something else",
    "ygrup": "a cutpoint group over a score",
    "yygrp": "a cutpoint group over a score",
    "r123": "a combined indicator over already-dichotomised items",
    "r45": "a combined indicator over already-dichotomised items",
    "r910": "a combined indicator over already-dichotomised items",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def show_scored_blocks(df: pd.DataFrame, meta) -> None:
    """Check, don't assert in prose, that these blocks hold scores."""
    for prefix, (n, n_anchors, stored, why) in SCORED_BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in cols), prefix
        labels = meta.variable_value_labels.get(cols[0]) or {}
        observed = sorted(int(v) for v in
                          pd.unique(df[cols].values.ravel()) if v == v)
        assert len(labels) == n_anchors, (prefix, len(labels), n_anchors)
        assert observed == stored, (prefix, observed, stored)
        zeros = int((df[cols] == 0).sum().sum())
        cells = int(df[cols].notna().sum().sum())
        print(f"NOT SHIPPING the {prefix!r} block ({n} items): its value "
              f"labels document {n_anchors} administered categories "
              f"{sorted(int(k) for k in labels)} but the file stores "
              f"{observed} ({zeros} of {cells} cells = "
              f"{100 * zeros / cells:.0f}% are 0). It is {why}.")


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 1175, len(df)

    labelled = [c for c in df.columns
                if (meta.column_names_to_labels.get(c) or "").strip()]
    print(f"variable labels present: {len(labelled)} of {len(df.columns)}, and "
          f"all of them demographic ({labelled[:4]}...) -- no item stems, so "
          "no item text can be recovered from this file")
    assert set(labelled) <= set(COV_MAP) | set(DROP), labelled

    show_scored_blocks(df, meta)

    assert all(c in df.columns for c in ITEMS), ITEMS
    assert not meta.variable_value_labels.get(ITEMS[0]), \
        "b1 has value labels -- re-check whether this block is scored too"
    btop = df[ITEMS].sum(axis=1)
    assert (df["btop"] == btop).all(), \
        "btop no longer equals the sum of b1..b13 -- re-check the block"
    print(f"SHIPPING the 'b' block (SOC-13): no value labels, values spread "
          f"over {sorted(int(v) for v in pd.unique(df[ITEMS].values.ravel()))}, "
          "and btop equals their sum exactly -- raw responses")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = set(COV_MAP) | set(covs) | set(ITEMS) | {"id"} | set(DROP)
    accounted |= {f"{p}{i}" for p, (n, *_r) in SCORED_BLOCKS.items()
                  for i in range(1, n + 1)}
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in sorted(DROP.items()):
        print(f"skipped column {c}: {why}")

    long = df[["id"] + covs + ITEMS].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{before - len(long)} cell(s) outside {PERMITTED}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
