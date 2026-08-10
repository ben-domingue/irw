#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245671
# DOI: 10.1371/journal.pone.0245671
# Gordils et al. (2021), "The effect of perceived interracial competition on
# psychological outcomes". S1 Data (Study 1) + S4 Data (Study 2). CC BY 4.0.
#
# Five distinct scales, each written to its own file per datastandard.md's
# "one file per scale" rule, all on a 1-7 anchor scale:
#   COMP1-5     perceived interracial competition (5 items)
#   DISCRIM1-9  Everyday Discrimination Scale, adapted (9 items)
#   ANX1-4      intergroup anxiety (4 items)
#   AVOID1-11   behavioral avoidance (11 items)
#   TRUST1-4    interracial trust/mistrust, adapted from general trust scale
#               (4 items) -- kept as raw (not reverse-coded) per
#               datastandard.md's resp-direction rule
#
# Study 1 (S1 Data, n=899 raw rows) and Study 2 (S4 Data, n=1774 raw rows)
# both administered these five scales; the paper states "Procedures and
# measures were identical to those reported in Study 1," so per
# datastandard.md's "same instrument administered to multiple sub-studies"
# rule the two samples are merged into one file per scale, with Study 2 ids
# offset by 100000 to keep them distinct from Study 1 ids (both studies use
# small sequential/row-order-based ids that would otherwise collide).
#
# Both raw files include an AttentionCheck column; filtering to
# AttentionCheck == 2 (the value the study intended participants to select)
# recovers exactly the paper's reported analytic Study 1 N (847 of 899).
# Applied identically to Study 2 (1774 -> 1702); this is somewhat higher than
# the paper's reported Study 2 N of 1645, likely because the paper's n also
# reflects a race-comparison-specific restriction to Black/White respondents
# used only for certain analyses -- not applied here since it is not a
# universal exclusion for the item data itself. Documented as a judgment
# call.
#
# Study 1 (S1 Data) has no explicit person-ID column; row index is used as
# id (offset 0). Study 2 (S4 Data) has a unique "ResponseID" column, but it
# is a large opaque platform ID, not used -- row index is used as id (offset
# 100000) for consistency with Study 1 and to avoid carrying platform IDs as
# PII-adjacent identifiers.
#
# Raw item cells use the string sentinel "#NULL!" for missingness in Study 2;
# pd.to_numeric(errors="coerce") converts these to NaN and they are dropped
# along with any other non-numeric cells. No PII columns present (race,
# income range, education, sex, age, political orientation are ordinary
# demographic covariates, not identifiers) -- these are NOT carried as
# cov_* here since they are large blocks of exploratory/manipulation-check
# covariates outside the scope of the five focal scales; only the raw items
# are retained.
#
# QC fix (2026-08-10, ben-domingue catch): in the Study 2 (S4 Data) file,
# the *second* item column of every scale except TRUST (COMP2, DISCRIM2,
# ANX2, AVOID2) is not a raw response -- for all 1774 Study-2 rows it is
# bit-for-bit identical to that scale's own pre-computed composite mean
# column (e.g. AVOID2 == AVOID), a spreadsheet artifact (a dragged formula
# or copy/paste error), not a genuine per-item answer. This is exactly the
# kind of imputed/derived value datastandard.md's "checking for imputed
# values" rule exists to catch. These four Study-2 columns are dropped
# entirely (nulled before melting) rather than shipped; Study 1's own
# COMP2/DISCRIM2/ANX2/AVOID2 are unaffected (verified integer-only, no
# match to any composite column) and are kept.
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

from pathlib import Path
import io

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL_S1 = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0245671.s004")
URL_S4 = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0245671.s007")

SCALES = {
    "gordils_2021_interracial_comp": ["COMP1", "COMP2", "COMP3", "COMP4", "COMP5"],
    "gordils_2021_discrimination": [f"DISCRIM{i}" for i in range(1, 10)],
    "gordils_2021_intergroup_anxiety": ["ANX1", "ANX2", "ANX3", "ANX4"],
    "gordils_2021_behavioral_avoidance": [f"AVOID{i}" for i in range(1, 12)],
    "gordils_2021_interracial_trust": ["TRUST1", "TRUST2", "TRUST3", "TRUST4"],
}


def _load(url: str, id_offset: int) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")
    df["AttentionCheck"] = pd.to_numeric(df["AttentionCheck"], errors="coerce")
    df = df[df["AttentionCheck"] == 2].reset_index(drop=True)
    df["id"] = df.index + id_offset
    return df


# Corrupted in Study 2 only -- see the QC-fix note above.
STUDY2_CORRUPT_ITEMS = ["COMP2", "DISCRIM2", "ANX2", "AVOID2"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df1 = _load(URL_S1, id_offset=0)
    df2 = _load(URL_S4, id_offset=100000)
    for col in STUDY2_CORRUPT_ITEMS:
        df2[col] = pd.NA

    for out_name, item_cols in SCALES.items():
        parts = []
        for df in (df1, df2):
            sub = df[["id"] + item_cols].copy()
            long = sub.melt(id_vars=["id"], value_vars=item_cols,
                             var_name="item", value_name="resp")
            parts.append(long)
        long = pd.concat(parts, ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
        long = long[["id", "item", "resp"]]

        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
