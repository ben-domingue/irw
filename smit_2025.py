"""
Convert the Validated Touch-Video Database (VTD) raw Qualtrics exports
(DATA1.csv, DATA2.csv) into IRW-standard long-format tables.

Source: Smit & Rich (2025), Behavior Research Methods, 57:134
        https://doi.org/10.3758/s13428-025-02655-w
        OSF: https://osf.io/jvkqa/  (CC BY 4.0)

Each participant rated 45 videos on up to four constructs:
  - hedonic category   (neutral / pleasant / unpleasant / painful)
  - hedonic strength    (1-10, only asked for non-neutral trials)
  - threat              (1-10)
  - arousal             (1-10)

Because these are distinct constructs, each is written out as its own
IRW table (id, item, resp, date, cov_*), per the "split files into
several tables if they have different constructs" guidance.

Usage:
    python process_vtd.py --data1 DATA1.csv --data2 DATA2.csv --outdir out/
"""

import argparse
import pandas as pd

CAT_MAP = {"Neutral": 1, "Pleasant": 2, "Unpleasant": 3, "Painful": 4}
N_ITEMS = 45


def load_and_prep(path: str, qlabel: str, start_num: int = 1) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Drop the trailing "V46_category" column - it isn't described anywhere
    # in the paper (mostly 0, occasionally a 5-digit number of unknown
    # origin). Flag with the data contributors before assuming it's noise.
    df = df.drop(columns=["V46_category"], errors="ignore")

    df = df.reset_index(drop=True)

    # No participant key exists in the export, so IDs are assigned by row
    # order. `id` is a plain, globally unique sequential number (continuing
    # across DATA1 -> DATA2, e.g. 001...179, 180...355) with no questionnaire
    # or item tag embedded in it. Note: if the same person completed both
    # questionnaires (the paper allowed this), there's no way to link their
    # two rows from this file alone.
    df["id"] = [f"{start_num + i:03d}" for i in range(len(df))]

    df["cov_questionnaire"] = qlabel

    df["cov_gender"] = df["Gender"]
    df["cov_age"] = df["Age"]
    df["cov_handedness"] = df["Handedness"]
    df["cov_ethnicity"] = df["Ethnicity"]
    df["cov_survey_duration_sec"] = df["Duration (in seconds)"]

    # IRW standard: convert to Unix time (seconds since 1970-01-01 UTC).
    # Qualtrics exports RecordedDate in UTC by default. Note this is the
    # per-participant survey completion time, not a true per-item timestamp,
    # so it repeats across all 45 of a participant's rows.
    df["date"] = pd.to_datetime(df["RecordedDate"], utc=True).apply(
        lambda x: int(x.timestamp())
    )

    return df


def build_long(df: pd.DataFrame, qlabel: str, n_items: int = N_ITEMS) -> dict:
    cov_cols = [
        "date",
        "cov_questionnaire",
        "cov_gender",
        "cov_age",
        "cov_handedness",
        "cov_ethnicity",
        "cov_survey_duration_sec",
    ]
    cat_rows, strength_rows, threat_rows, arousal_rows = [], [], [], []

    for i in range(1, n_items + 1):
        # Item IDs match the raw dataset's own column naming exactly (V1, V2,
        # ... V45), rather than a constructed label. Note: DATA1 and DATA2
        # each have their own V1...V45, referring to *different* videos, so
        # "V1" alone doesn't uniquely identify a video across both files -
        # cov_questionnaire (q1/q2) is what disambiguates which pool an item
        # came from.
        item_id = f"V{i}"

        cat = df[f"V{i}_category"]
        p, u, pa = df[f"V{i}_pleasant"], df[f"V{i}_unpleasant"], df[f"V{i}_painful"]
        threat, arousal = df[f"V{i}_threat"], df[f"V{i}_arousal"]

        base = df[["id"] + cov_cols].copy()

        # 1. Hedonic category - nominal, coded via CAT_MAP
        c = base.copy()
        c["item"] = item_id
        c["resp"] = cat.map(CAT_MAP)
        cat_rows.append(c)

        # 2. Hedonic strength - scale is 1-10 ("not at all" to "extremely"),
        # so 0 is never a valid rating. It occurs when the question wasn't
        # shown (neutral trials skip Q2) or wasn't answered (a small number
        # of non-neutral trials with all three sub-columns at 0) - keep the
        # row but record resp as NA rather than a literal 0.
        s = base.copy()
        s["item"] = item_id
        strength = p.where(p != 0, u).where(lambda x: x != 0, pa)
        strength = strength.replace(0, pd.NA)
        s["resp"] = strength
        strength_rows.append(s)

        # 3. Threat
        t = base.copy()
        t["item"] = item_id
        t["resp"] = threat
        threat_rows.append(t)

        # 4. Arousal
        a = base.copy()
        a["item"] = item_id
        a["resp"] = arousal
        arousal_rows.append(a)

    def finalize(rows):
        out = pd.concat(rows, ignore_index=True)
        return out[["id", "item", "resp"] + cov_cols]

    return {
        "category": finalize(cat_rows),
        "strength": finalize(strength_rows),
        "threat": finalize(threat_rows),
        "arousal": finalize(arousal_rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data1", default="DATA1.csv", help="Path to DATA1.csv")
    parser.add_argument("--data2", default="DATA2.csv", help="Path to DATA2.csv")
    parser.add_argument("--outdir", default=".", help="Output directory")
    parser.add_argument(
        "--study-name", default="validatedtouchvideo_smit_2025", help="Filename prefix"
    )
    args = parser.parse_args()

    df1 = load_and_prep(args.data1, "q1", start_num=1)
    df2 = load_and_prep(args.data2, "q2", start_num=len(df1) + 1)

    tabs1 = build_long(df1, "q1")
    tabs2 = build_long(df2, "q2")

    for construct in ["category", "strength", "threat", "arousal"]:
        combined = pd.concat(
            [tabs1[construct], tabs2[construct]], ignore_index=True
        )
        fname = f"{args.outdir}/{args.study_name}_{construct}.csv"
        combined.to_csv(fname, index=False)
        print(f"wrote {fname}  shape={combined.shape}")


if __name__ == "__main__":
    main()