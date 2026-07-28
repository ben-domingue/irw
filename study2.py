
"""
Process Study 2 raw Inquisit IAT data into IRW format.
 
Study 2 is a math/reading x male/female stereotype IAT (different construct
from Study 1's self/other x male/female identity IAT), so it gets its own
table and its own set of "real" trialcodes.
 
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
    "introduction", "consent", "demographics", "assent",
    "instructions_Imp", "end", "exit_survey",
}
 
# The only trialcodes that correspond to genuine categorization trials
# (a real stimulus word shown, real key press expected). Everything else
# in the task blocks is an instruction screen (trialcode starts with
# "instr_") or a feedback screen ("feedback_trial") and gets dropped.
# NOTE: this differs from Study 1 -- math/reading replace self/other.
REAL_TRIALCODES = {
    "female_left", "female_right",
    "male_left", "male_right",
    "math_left", "math_right",
    "reading_left", "reading_right",
}
 
 
def process_study2(path: Path, modality: str) -> pd.DataFrame:
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
    # exists, add it the same way Study 1 does:
    #   inperson = process_study2(SCRIPT_DIR / "Study_2_-_In-Person_Raw_Data.sav", "inperson")
    #   combined = pd.concat([online, inperson], ignore_index=True)
    online = process_study2(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 2 - Online Raw Data (1).sav", "online")
 
    combined = online
    out_path = SCRIPT_DIR / "childrensocialcognition_cvencek_2025_mathgenderstereotype.csv"
    combined.to_csv(out_path, index=False)
 
    print(f"Wrote {out_path}")
    print("Rows:", len(combined))
    print("Unique subjects:", combined["id"].nunique())
    print("Unique items:", combined["item"].nunique())
    print(combined["resp"].value_counts())