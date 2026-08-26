"""
Input : long_format_data.Rdata (dl, 6300 x 35), wide_format_data.Rdata (dw, 1575 x 50)
        Codebook.xlsx (used as documentation; not read by this script)
Output: 4 IRW tables (see processing notes for design decisions)

ENSURE LONG AND WIDE FORMAT DATA ARE IN SAME FOLDER AS .PY FILE BEFORE PROCESSING.

Codebook alignment (see CODEBOOK CONFLICTS below for the two unresolved items):
  - resp shifted to the documented 1-7 metric        (RESP_OFFSET)
  - gender, country, english_level given their documented labels
  - ordinal codes (experience) left numeric so they stay orderable
  - country_school left as stored: codebook and file disagree
"""

import pyreadr
import pandas as pd
import numpy as np
from pathlib import Path

# data files sit next to this script; falls back to the working directory
# when run from a notebook, where __file__ is not defined
UP = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
OUT = UP / "output"
OUT.mkdir(parents=True, exist_ok=True)

dl = pyreadr.read_r(UP / "long_format_data.Rdata")["dl"].reset_index(drop=True)
dw = pyreadr.read_r(UP / "wide_format_data.Rdata")["dw"].reset_index(drop=True)

# ---------------------------------------------------------------- helpers ----
SCALE_LABELS = {
    "lq": "language_quality",
    "str": "structure",
    "con": "content",
    "hol": "holistic",
}

# Codebook: score and exp_score are documented as 1 (very low quality) to
# 7 (very high quality), but the .Rdata files store 0-6. Shifting up by one
# puts resp on the documented rubric metric.
# NB: the paper's Table 1 was computed on the stored 0-6 values, so with the
# offset applied the means here sit exactly 1.00 above the published ones.
# Set to 0 to reproduce the paper instead.
RESP_OFFSET = 1

# Codebook value labels. Applied to nominal codes only: ordinal ones
# (experience, and the 1-4 agreement items) stay numeric so that they remain
# orderable for analysis. Labels are matched on the string form of the value.
VALUE_LABELS = {
    "gender": {"F": "female", "M": "male", "D": "diverse"},
    "country": {"0": "Switzerland", "1": "Germany", "2": "other"},
    "english_level": {          # the "A" prefix is a survey answer code, not CEFR
        "A1": "B1", "A2": "B2", "A3": "C1", "A4": "C2",
        "A5": "first_language", "A6": "unknown",
    },
}

# ----------------------------------------------------------------------------
# CODEBOOK CONFLICTS - worth one email to the authors before this is submitted
#
# 1. country_school is documented as 0 = Switzerland, 1 = Germany, 2 = other,
#    but the files store 1 / 2 / 3 (n = 166 / 139 / 8). The labels are probably
#    right and the codes off by one, but that is a guess, so the raw codes are
#    kept and no labels are applied.
# 2. score / exp_score documented 1-7, stored 0-6 (see RESP_OFFSET above).
#    Note the two conflicts run in opposite directions, which is why neither
#    should be treated as settled.
# Minor: the codebook lists the agreement scale as "1 = disagree 2 = disagree";
# point 1 is presumably *strongly* disagree. It also names the survey duration
# variable time_total, while the files call it total_time.
# ----------------------------------------------------------------------------


def teacher_id(s):
    """315 preservice teachers; ids stored as floats in the source."""
    return s.astype(float).astype(int).astype(str)


def apply_labels(s, mapping):
    """Map codes to codebook labels; 2 and 2.0 both match the key '2'."""
    key = s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    out = key.map(mapping)
    return out.where(s.notna())


# person-level (rater-level) attributes, identical in every row of a teacher
RATER_ATTRS = {
    "country": "country",
    "country_school": "country_school",
    "gender": "gender",
    "age": "age",
    "semester": "semester",
    "experience": "experience",
    "english_level": "english_level",
    "jump_tracker_ratings": "n_jumps",
    "total_time": "total_time_s",
    # codebook: "duration of the five essay ratings" - a total, not a mean
    "text_time_mean": "essay_time_total_s",
}

teachers = dl.drop_duplicates("id").copy()
teachers["id"] = teacher_id(teachers["id"])
teachers = teachers.set_index("id")

# =========================================================== TABLE 1: main ===
# id    = student essay (the focal unit being measured: its text quality)
# item  = rubric dimension
# rater = preservice teacher, plus one row set for the expert benchmark
# resp  = rating on the documented 1-7 rubric (0-6 in the source + RESP_OFFSET)
t = dl.copy()
t["rater"] = teacher_id(t["id"])
t["id"] = t["essay_id"]
t["item"] = t["scale"].map(SCALE_LABELS)
t["resp"] = t["score"].astype(int) + RESP_OFFSET
t["rt"] = t["text_time"].round(2)          # seconds on that essay (block-level)

main = t[["id", "item", "resp", "rater", "rt"]].copy()
for src, new in RATER_ATTRS.items():
    col = t[src]
    main["ratercov_" + new] = apply_labels(col, VALUE_LABELS[src]) if src in VALUE_LABELS else col
main["ratercov_total_time_s"] = main["ratercov_total_time_s"].round(2)
main["ratercov_essay_time_total_s"] = main["ratercov_essay_time_total_s"].round(2)

# expert benchmark: one value per essay x dimension, constant across teachers
# (codebook: factor "fair" score from the IEA FACETS rater model)
exp = (
    t[["id", "item", "exp_score"]]
    .drop_duplicates(["id", "item"])
    .rename(columns={"exp_score": "resp"})
)
exp["resp"] = exp["resp"].astype(int) + RESP_OFFSET
exp["rater"] = "expert_benchmark"
exp["rt"] = np.nan
for new in RATER_ATTRS.values():
    exp["ratercov_" + new] = np.nan

main = pd.concat([main, exp[main.columns]], ignore_index=True)
main["_r"] = (main["rater"] == "expert_benchmark").astype(int)
main = main.sort_values(["id", "_r", "rater", "item"]).drop(columns="_r")

# ================================== TABLES 2-4: teacher questionnaire scales ===
# All three use the documented 4-point agreement scale (1 = strongly disagree
# to 4 = agree), left numeric. consc_2 ("I am sluggish, I tend to be lazy") is
# reverse-keyed and stays in its source direction, which the IRW standard
# permits: items may load on the latent variable in opposite ways.
# Self-concept wave 2 was measured after the rating task AND after participants
# saw expert feedback, so it is not a clean pre/post.


def covariates(prefix):
    """Rater attributes with codebook labels applied, ready to join on id."""
    cov = pd.DataFrame(index=teachers.index)
    for src, new in RATER_ATTRS.items():
        col = teachers[src]
        cov[prefix + new] = apply_labels(col, VALUE_LABELS[src]) if src in VALUE_LABELS else col
    cov[prefix + "total_time_s"] = cov[prefix + "total_time_s"].round(2)
    cov[prefix + "essay_time_total_s"] = cov[prefix + "essay_time_total_s"].round(2)
    return cov


def questionnaire(items, name, wave_map=None):
    """id = teacher; one row per teacher x item (x wave)."""
    src = dl if all(i in dl.columns for i in items) else dw
    d = src.drop_duplicates("id").copy()
    d["id"] = teacher_id(d["id"])
    long = d.melt(id_vars="id", value_vars=items, var_name="item", value_name="resp")
    if wave_map:
        long["wave"] = long["item"].map(lambda c: wave_map[c][1])
        long["item"] = long["item"].map(lambda c: wave_map[c][0])
    long["resp"] = long["resp"].astype(int)
    long = long.merge(covariates("cov_"), left_on="id", right_index=True, how="left")
    front = ["id", "item", "resp"] + (["wave"] if wave_map else [])
    long = long[front + [c for c in long.columns if c.startswith("cov_")]]
    sort = ["id", "item"] + (["wave"] if wave_map else [])
    return name, long.sort_values(sort)


mot_name, motivation = questionnaire(
    ["mot_1", "mot_2", "mot_3"], "motivation")

sc_items = [f"sc_{i}_t{w}" for w in (1, 2) for i in (1, 2, 3)]
sc_map = {f"sc_{i}_t{w}": (f"sc_{i}", w) for w in (1, 2) for i in (1, 2, 3)}
sc_name, selfconcept = questionnaire(sc_items, "selfconcept", wave_map=sc_map)

# consc_4 lives only in the wide file; merge it back in
d4 = dw.drop_duplicates("id")[["id", "consc_4"]].copy()
d4["id"] = teacher_id(d4["id"])
consc = dl.drop_duplicates("id").copy()
consc["id"] = teacher_id(consc["id"])
consc = consc[["id", "consc_1", "consc_2", "consc_3"]].merge(d4, on="id")
cons_long = consc.melt(id_vars="id", var_name="item", value_name="resp")
cons_long["resp"] = cons_long["resp"].astype(int)
conscientiousness = (
    cons_long.merge(covariates("cov_"), left_on="id", right_index=True, how="left")
    .sort_values(["id", "item"])
)

# ------------------------------------------- integer-valued cols as integers ----
# country, gender and english_level now carry labels, so they are no longer here
INT_COLS = ["country_school", "age", "semester", "experience", "n_jumps"]


def tidy_ints(df):
    for c in df.columns:
        base = c.split("cov_")[-1]
        if base in INT_COLS:
            df[c] = pd.to_numeric(df[c]).astype("Int64")
    return df


# ------------------------------------------------------------------ write ----
STEM = "teacherjudgements_lohmann_2026"
MAIN_SUFFIX = "essayratings"   # set to "" to name the main table just STEM

tables = {
    f"{STEM}_{MAIN_SUFFIX}" if MAIN_SUFFIX else STEM: main,
    f"{STEM}_motivation": motivation,
    f"{STEM}_selfconcept": selfconcept,
    f"{STEM}_conscientiousness": conscientiousness,
}
for name, df in tables.items():
    df = tidy_ints(df)
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name}.csv  {df.shape[0]:>5} rows x {df.shape[1]:>2} cols")

print(f"\nresp offset applied: +{RESP_OFFSET} "
      f"(range {int(main.resp.min())}-{int(main.resp.max())})")
print("country_school left unlabelled: codebook documents 0/1/2, files store "
      f"{sorted(pd.to_numeric(teachers.country_school).dropna().unique().astype(int))}")