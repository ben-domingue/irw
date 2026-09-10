from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Self-Compassion Curbs Adoption of Demotivating Teaching Styles: "
         "The Mediation of Cognitive Reappraisal (Moè, 2025, figshare)")
URL  = "https://figshare.com/articles/dataset/Dataset_paper_Self-Compassion_Curbs_Adoption_of_Demotivating_Teaching_Styles_The_Mediation_of_Cognitive_Reappraisal/30385261"
DOI  = "10.6084/m9.figshare.30385261"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/58837756"

COV_COLS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Yearsofteaching": "cov_years_teaching",
    "Subject": "cov_subject_taught",
    "Region": "cov_region",
}


def convert():
    print("Downloading Moe SC ER demotivating styles.sav ...")
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_spss(pd.io.common.BytesIO(r.content), convert_categoricals=False)

    # SCS25_pre is not item 25's responses (irw#2146). The file carries a
    # reverse-scored twin for all 13 negatively worded SCS items; twelve satisfy
    # raw + rev == 6 for every respondent, but SCS25_pre disagrees with
    # SCS25_pre_rev for 66 of 95. The _rev column is the real item: it
    # correlates -.51 to -.63 with the other Isolation items (raw: -.12 to -.18),
    # and regressing the author's own SelfCompassion composite on every item
    # column weights SCS25_pre_rev 0.96 and SCS25_pre -0.06. So the raw item is
    # recovered as 6 - SCS25_pre_rev.
    rev_cols = [c for c in raw.columns if c.startswith("SCS") and c.endswith("_rev")]
    for c in rev_cols:
        if c == "SCS25_pre_rev":
            continue
        bad = int((raw[c.removesuffix("_rev")] + raw[c] != 6).sum())
        assert bad == 0, f"{c}: {bad} rows break raw + rev == 6; recheck #2146 before trusting it"
    raw["SCS25_pre"] = 6 - raw["SCS25_pre_rev"]

    # "Codice" has one duplicate value -- use row position instead.
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    scales = {
        # SIS (Situations in Schools), 15 scenarios x 4 motivating-style
        # sub-items (a=autonomy-supportive, b=structuring, c=controlling,
        # d=chaotic per the source file's own composite score names), 1-7
        "moe2025_sis": [c for c in raw.columns if c.startswith("SIS")],
        # SCS (Self-Compassion Scale), 26 items, 1-5 -- raw items only,
        # "_rev" suffixed columns are derived reverse-coded duplicates
        "moe2025_scs": [c for c in raw.columns if c.startswith("SCS") and "rev" not in c],
        # ERQ (Emotion Regulation Questionnaire), 10 items, 1-7
        "moe2025_erq": [c for c in raw.columns if c.startswith("ERQ")],
    }

    for table, item_cols in scales.items():
        items = raw[["id"] + item_cols].merge(cov, on="id")
        long = items.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fname = f"{table}.csv"
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
