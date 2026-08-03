#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280701
# DOI: 10.1371/journal.pone.0280701
# Supporting Information: journal.pone.0280701_S1_Data.xlsx
#
# Chain-mediation study of emotional eating (Chinese sample, N=494).
# Raw file's column names are the actual item text (already in English),
# but item blocks are grouped under cryptic "@10."/"@11."/etc. labels with
# the first item of each block missing that prefix (its column name is
# just the raw item text). Block sizes were matched to the paper's stated
# instrument lengths (all confirmed via WebFetch of the Measures section):
#   @10 block (22 cols) + 1 unprefixed intro item = 23  -> EES-R (23 items, Cronbach's a=.935)
#   @11 block (19 cols) + 1 unprefixed intro item = 20  -> CES-D (20 items, a=.884)
#   @12 block (20 cols)                           = 20  -> UPPS-P short form (20 items, a=.834)
#   @13 block (35 cols) + 1 unprefixed intro item = 36  -> DERS (36 items, a=.934)
# Four separate output files, one per instrument (datastandard.md: one
# scale per file).
#
# Excluded: EESR/CESD/SUPPSP/DERS (pre-computed total/aggregate score
# columns at the front of the sheet), demographic columns (kept as
# covariates instead), 'height (m)' (redundant with the cm column, dropped
# to avoid a duplicate covariate).
#
# No person-ID column exists in the raw file; id is the row index.
#
# Response ranges observed empirically (per-item value_counts checked,
# distributions consistent across all items within each scale -- not
# isolated data-entry values): EES-R 1-5, CES-D 1-4, UPPS-P 1-4, DERS 1-5
# (DERS in this Chinese sample uses a 5-point response format even though
# some English-language summaries describe a 4-point version).

import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0280701.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "@1, Your gender": "cov_gender",
    "@2. Your age": "cov_age",
    "@3. Your grade": "cov_grade",
    "@4. Your height is (in unit: cm)": "cov_height_cm",
    "@5. Your weight is (in: kg)": "cov_weight_kg",
    "@8. Your family's monthly per capita income is": "cov_income",
    "BMI": "cov_bmi",
}


def _process(df, cols, valid_min, valid_max, cov_cols, out_name, item_prefix):
    long = df.reset_index().rename(columns={"index": "id"})
    long["id"] = long["id"] + 1
    # Rename to positional item labels: the raw column header for each
    # block's first item is the instructions/prompt text (an export
    # quirk), not real item content, for the EES-R and DERS blocks -- use
    # generic positional names throughout for consistency rather than a
    # mix of real item text and instruction text.
    rename_map = {c: f"{item_prefix}_{i+1}" for i, c in enumerate(cols)}
    long = long.rename(columns=rename_map)
    item_cols = list(rename_map.values())
    long = long.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]
    long = long[["id", "item", "resp"] + cov_cols]

    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")
    try:
        import pyreadr
        pyreadr.write_rdata(out_path.replace(".csv", ".RData"), long, df_name="d")
    except Exception as e:
        print(f"  ({out_name} RData export skipped: {e})")


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    cols = list(df.columns)
    ees_cols = ["When you have the following emotions, the degree of desire to eat is"] + \
        [c for c in cols if c.startswith("@10")]
    cesd_cols = ["I don't want to eat. I have a bad appetite"] + \
        [c for c in cols if c.startswith("@11")]
    upps_cols = [c for c in cols if c.startswith("@12")]
    ders_cols = ["13Please read the topic carefully and choose it according to your actual situation"] + \
        [c for c in cols if c.startswith("@13")]

    assert len(ees_cols) == 23, len(ees_cols)
    assert len(cesd_cols) == 20, len(cesd_cols)
    assert len(upps_cols) == 20, len(upps_cols)
    assert len(ders_cols) == 36, len(ders_cols)

    _process(df, ees_cols, 1, 5, cov_cols, "yang_2023_emotional_eating_eesr.csv", "EESR")
    _process(df, cesd_cols, 1, 4, cov_cols, "yang_2023_emotional_eating_cesd.csv", "CESD")
    _process(df, upps_cols, 1, 4, cov_cols, "yang_2023_emotional_eating_uppsp.csv", "UPPSP")
    _process(df, ders_cols, 1, 5, cov_cols, "yang_2023_emotional_eating_ders.csv", "DERS")


if __name__ == "__main__":
    convert()
