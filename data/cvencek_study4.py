"""
Process Study 4 raw Inquisit IAT data into IRW format.

Study 4 is a gender x good/bad stereotype/attitude IAT (girl/boy images vs.
good/bad words) -- a different construct from Studies 1-3, so it gets its
own table and its own set of "real" trialcodes. Like Studies 2/3-online, its
instruction trialcodes are prefixed "CM_instr_..." rather than "instr_...",
so a trialcode whitelist is used instead of a blacklist to stay robust to
that.

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

# ---- Config ---------------------------------------------------------------

# Blocks that are pure study logistics (not IAT trials) -- dropped entirely.
# exit_survey is also excluded here since it's a separate item-response
# table (one column per question), not trial-level data.
META_BLOCKS = {
    "introduction", "consent", "demographics", "assent", "instructions_Imp",
    "end", "exit_survey", "intro_block", "end_block",
}

# The only trialcodes that correspond to genuine categorization trials
# (a real stimulus word/image shown, real key press expected). Everything
# else in the task blocks is an instruction/feedback screen and gets
# dropped.
REAL_TRIALCODES = {
    "female_left", "female_right",
    "male_left", "male_right",
    "good_left", "good_right",
    "bad_left", "bad_right",
}


def process_study4(path: Path, modality: str) -> pd.DataFrame:
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
    # Put the raw .sav file(s) in the same folder as this script, or edit
    # the paths below to point at wherever they actually live.
    #
    # Only the online file has shown up so far -- once an in-person file
    # exists, add it the same way Study 1 and 3 do:
    #   inperson = process_study4(SCRIPT_DIR / "Study_4_-_In-Person_Raw_Data.sav", "inperson")
    #   combined = pd.concat([online, inperson], ignore_index=True)
    online = process_study4(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 4 - Online Raw Data.sav", "online")

    combined = online
    out_path = SCRIPT_DIR / "childrensocialcognition_cvencek_2025_genderingroupbias.csv"
    combined.to_csv(out_path, index=False)

    print(f"Wrote {out_path}")
    print("Rows:", len(combined))
    print("Unique subjects:", combined["id"].nunique())
    print("Unique items:", combined["item"].nunique())
    print(combined["resp"].value_counts())