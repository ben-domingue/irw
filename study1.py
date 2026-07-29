"""
Process Study 1 (Online + In-Person) raw Inquisit IAT data into IRW format.

Requires: pandas, pyreadstat
    pip install pandas pyreadstat
"""

from pathlib import Path

import pandas as pd
import pyreadstat

# Anchor all file paths to the folder this script lives in, rather than
# relying on the current working directory (which some IDEs/launchers set
# to a read-only location).
SCRIPT_DIR = Path(__file__).resolve().parent

# ---- Config -------------------------------------------------------------

# Blocks that are pure study logistics (not IAT trials) -- dropped entirely.
# exit_survey is also excluded here since it's a separate item-response
# table (one column per question), not trial-level data.
META_BLOCKS = {
    "introduction", "consent", "demographics", "assent",
    "instructions_Imp", "end", "exit_survey",
}

# The only trialcodes that correspond to genuine categorization trials
# (a real stimulus word shown, real key press expected). Everything else
# in the task blocks is an instruction screen (trialcode starts with
# "instr_") or a feedback screen ("feedback_trial") and gets dropped.
REAL_TRIALCODES = {
    "female_left", "female_right",
    "male_left", "male_right",
    "other_left", "other_right",
    "self_left", "self_right",
}


def process_study1(path: str, modality: str) -> pd.DataFrame:
    df, _meta = pyreadstat.read_sav(path)

    df = df[~df["blockcode"].isin(META_BLOCKS)]
    df = df[df["trialcode"].isin(REAL_TRIALCODES)]

    out = pd.DataFrame()
    out["id"] = df["subject"].astype(int).astype(str)
    out["item"] = (
        df["blockcode"].astype(str) + "|"
        + df["stimulusitem1"].astype(str) + "|"
        + df["trialcode"].astype(str)
    )
    out["resp"] = df["correct"].astype(int)
    out["rt"] = (df["latency"].astype(float) / 1000.0).round(3)  # ms -> seconds
    out["cov_modality"] = modality
    return out


if __name__ == "__main__":
    # Put the two .sav files in the same folder as this script, or edit
    # these two lines to point at wherever they actually live.
    online = process_study1(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 1 - In-Person Raw Data.sav", "online")
    inperson = process_study1(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 1 - Online Raw Data.sav", "inperson")

    # Sanity check: make sure subject ids don't collide across modality
    # before combining into one table.
    overlap = set(online["id"]) & set(inperson["id"])
    if overlap:
        print(f"WARNING: overlapping subject ids across modality: {sorted(overlap)}")

    combined = pd.concat([online, inperson], ignore_index=True)
    out_path = SCRIPT_DIR / "childrensocialcognition_cvencek_2025_genderidentity.csv"
    combined.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")

    print("Rows:", len(combined))
    print("Unique subjects:", combined["id"].nunique())
    print("Unique items:", combined["item"].nunique())
    print(combined["resp"].value_counts())