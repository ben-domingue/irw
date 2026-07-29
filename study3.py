"""
Process Study 3 (Online + In-Person) raw Inquisit IAT data into IRW format.

Study 3 is an insects/flowers x good/bad IAT (different construct from
Study 1 and Study 2), so it gets its own table and its own set of "real"
trialcodes. Note that the online and in-person files use different block
naming conventions (e.g. "introduction"/"end" vs "intro_block"/"end_block",
and "instr_..." vs "CM_instr_..." for instruction trials), so this script
unions both naming schemes and relies on a trialcode whitelist rather than
a blacklist to stay robust to that.

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
# Union of both the online naming scheme (introduction/end/...) and the
# in-person naming scheme (intro_block/end_block, no logged consent/
# demographics/assent).
META_BLOCKS = {
    "introduction", "consent", "demographics", "assent", "instructions_Imp",
    "end", "exit_survey", "intro_block", "end_block",
}

# The only trialcodes that correspond to genuine categorization trials
# (a real stimulus word/image shown, real key press expected). Everything
# else in the task blocks is an instruction screen ("instr_..." online,
# "CM_instr_..." online, or "warmup_trial"/"practice_trial"/"test_trial"
# placeholder rows in-person) and gets dropped. A whitelist is used rather
# than a blacklist since the instruction-trialcode naming isn't consistent
# between the online and in-person files.
REAL_TRIALCODES = {
    "bad_left", "bad_right",
    "good_left", "good_right",
    "flowers_left", "flowers_right",
    "insects_left", "insects_right",
}


def process_study3(path: Path, modality: str) -> pd.DataFrame:
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
    online = process_study3(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 3 - Online Raw Data.sav", "online")
    inperson = process_study3(SCRIPT_DIR / "/Users/rubinashrestha/Documents/childrensocialcognition_cvencek_2025/Study 3 - In-Person Raw Data.sav", "inperson")

    # Sanity check: make sure subject ids don't collide across modality
    # before combining into one table.
    overlap = set(online["id"]) & set(inperson["id"])
    if overlap:
        print(f"WARNING: overlapping subject ids across modality: {sorted(overlap)}")

    combined = pd.concat([online, inperson], ignore_index=True)
    out_path = SCRIPT_DIR / "childrensocialcognition_cvencek_2025_flowerinsectattitude.csv"
    combined.to_csv(out_path, index=False)

    print(f"Wrote {out_path}")
    print("Rows:", len(combined))
    print("Unique subjects:", combined["id"].nunique())
    print("Unique items:", combined["item"].nunique())
    print(combined["resp"].value_counts())