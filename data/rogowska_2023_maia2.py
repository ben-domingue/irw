#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10693589
# DOI: 10.1038/s41598-023-48536-0
# "Validation of the shortened 24-item multidimensional assessment of
# interoceptive awareness, version 2 (Brief MAIA-2)" (Rogowska, Tataruch &
# Klimowska, 2023), Scientific Reports 13:21270.
# Data: 41598_2023_48536_MOESM1_ESM.xlsx (the article's only supplementary
#       file), sheet "Data Base". Its other two sheets are the Polish MAIA-2
#       and Brief MAIA-2 questionnaires; the rest of the Europe PMC SI zip is
#       the figure image.
# License: CC BY 4.0 (article licence in the Europe PMC full-text record; Data
#          Availability: "All data ... are included in this published article
#          [and its supplementary information file]"). Article-attached SI, so
#          the article licence governs.
#
# Item text: shipped PARTIAL (2026-09-24, ben-domingue's call). Polish stems,
#   instructions and endpoint anchors (0 Nigdy, 5 Zawsze) from this xlsx's own
#   "MAIA-2 (Polish)" sheet, numbered 1-37 as the codes; English _translated
#   from the canonical MAIA-2 (Mehling et al. 2018, PLOS ONE, S1 Questionnaire).
#   No labels exist at either level in the data sheet (headers MAIA2_01..37
#   only). Anchors are withheld on the reverse-keyed items 5-12 and 15: whether
#   the deposit stores them reverse-scored is unresolved (correlations point to
#   as-answered, the gender contrast and item 7's mean point to reversed), and
#   a wrong guess would invert 0/5. Mapping PARTIAL via
#   automated_finding/verify_rogowska_2023_maia2.R.
#
# One instrument, one table: the 37-item MAIA-2 (0-5, "0 = Never to
# 5 = Always"), eight subscales per the paper's Measures section. The Brief
# MAIA-2 is a 24-item subset of these same columns, so it is not a second
# table. The file's 8 MAIA-2 subscale means and 8 Brief subscale sums + total
# are dropped as composites (and used below to confirm the item->subscale map).
#
# Two cells are fractional (row ID 320 MAIA2_03 = 3.342, ID 306 MAIA2_07 =
# 1.387): imputations, not responses -> dropped. N = 323, no PII (ID, sex,
# age, occupational/athlete status only).

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
XLSX_URL = ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-023-"
            "48536-0/MediaObjects/41598_2023_48536_MOESM1_ESM.xlsx")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "rogowska_2023_maia2"

ITEMS = [f"MAIA2_{i:02d}" for i in range(1, 38)]
SCALE06 = {0, 1, 2, 3, 4, 5}
# Paper, Measures: item ranges of the eight MAIA-2 subscales.
SUBSCALES = {
    "Noticing_MAIA2_S1": ("noticing", range(1, 5)),
    "NotDistract_MAIA2_S2": ("not distracting", range(5, 11)),
    "NotWorrying_MAIA2_S3": ("not worrying", range(11, 16)),
    "AttentionReg_MAIA2_S4": ("attention regulation", range(16, 23)),
    "EmotionAwa_MAIA2_S5": ("emotional awareness", range(23, 28)),
    "SelfReg_MAIA2_S6": ("self-regulation", range(28, 32)),
    "BodyList_MAIA2_S7": ("body listening", range(32, 35)),
    "Trusting_MAIA2_S8": ("trusting", range(35, 38)),
}
COV = {"ID": "id", "Sex01": "cov_sex", "Age": "cov_age", "Status": "cov_status"}
SKIP = {"Sex": "string duplicate of Sex01 (1 = Female, 0 = Male)"}
COMPOSITES = list(SUBSCALES) + [
    "Noticing_Brief_S1", "NotDistract_Brief_S2", "NotWorrying_Brief_S3",
    "AttentionReg_Brief_S4", "EmotionAwa_Brief_S5", "SelfReg_Brief_S6",
    "BodyList_Brief_S7", "TrustingS_Brief_S8", "Total Brief MAIA-2"]


def convert() -> None:
    r = requests.get(XLSX_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(BytesIO(r.content), sheet_name="Data Base")

    # Balance the books: every source column is an item, a covariate, or
    # skipped for a printed reason.
    used = set(ITEMS) | set(COV) | set(SKIP) | set(COMPOSITES)
    unaccounted = [c for c in df.columns if c not in used]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    print(f"  [skip] {len(COMPOSITES)} subscale/total composites")

    assert df["ID"].nunique() == len(df) == 323
    assert ((df["Sex01"] == 1) == (df["Sex"] == "Female")).all()

    # Fractional cells are not observed responses: blank them. The file's own
    # subscale means for those two respondents do not reproduce from them
    # (ID 320 Noticing = 4.25 implies an integer 3 at MAIA2_03, ID 306
    # Not-Distracting = 1.0 implies 1 at MAIA2_07), so what was observed is
    # unknowable from the deposit; neither value is shipped.
    frac = df[ITEMS].map(lambda v: pd.notna(v) and v % 1 != 0)
    print(f"  [drop] {int(frac.values.sum())} fractional (imputed) cells: "
          f"{[(int(df.at[r, 'ID']), c, df.at[r, c]) for c in ITEMS for r in df.index[frac[c]]]}")
    assert frac.values.sum() == 2
    df[ITEMS] = df[ITEMS].mask(frac)

    # Confirm the item->subscale map: each MAIA-2 subscale column is the
    # plain mean of its items, to the file's 2-dp rounding.
    item_construct = {}
    for col, (construct, rng) in SUBSCALES.items():
        cols = [f"MAIA2_{i:02d}" for i in rng]
        keep = ~frac[cols].any(axis=1)  # the two rows above cannot reproduce
        dev = (df.loc[keep, cols].mean(axis=1) - df.loc[keep, col]).abs().max()
        assert dev < 0.006, f"{col}: items do not reproduce the subscale ({dev})"
        item_construct.update({c: construct for c in cols})
    assert set(item_construct) == set(ITEMS)

    d = df[list(COV) + ITEMS].rename(columns=COV)
    long = d.melt(id_vars=["id", "cov_sex", "cov_age", "cov_status"],
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    long["cov_sex"] = long["cov_sex"].astype("Int64")  # 1 female, 0 male, NA x3
    long = long[["id", "item", "resp", "cov_age", "cov_sex", "cov_status"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert set(long["resp"]).issubset(SCALE06), "resp outside 0-5"
    assert not long.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 37
    names = [TABLE]
    assert len(names) == len(set(names)), "duplicate output filenames"

    report = irw_validate.validate_frame(
        long, label=TABLE, profile="upload",
        context={"permitted_values": {i: SCALE06 for i in ITEMS},
                 "item_constructs": item_construct})
    print(report)
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
