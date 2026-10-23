##Tiger-mascot character-design conjoint (Study 1) from
##Byun, J. (2026). A Perceptual Evaluation Framework for 3D Digital Character Design:
##Aggregate Preference versus Contextual Signaling in a Two-Phase Conjoint Study.
##Data: OSF https://osf.io/cyd9v/ (node created 2026-05-26; no article DOI in the deposit).
##Licence: the OSF node sets NO licence; included on the depositor's written permission
##(Permission via Email, Byun to ben-domingue, 2026-10; see processing_notes/outreach).
##Files read: Study1.csv (raw Qualtrics export). "R Coding for Study 1 Analysis.docx" was
##read as text, not run -- it is the source for the RIT-affiliation coding below.
##Usage: python3 byun_2026_mascot.py <dir holding Study1.csv> <output dir>
##
##114 respondents recruited anonymously at Rochester Institute of Technology (collection
##began 2025-12-19), each shown 6 choice tasks of 3 rendered tiger-mascot characters, with
##one forced choice per task ("Select your favorite tiger character as an RIT mascot." --
##the same wording on all six tasks). 110 answered at least one task and are kept; the 4
##who answered none are dropped (no outcome). A separate practice task preceding the six is
##dropped. Profiles were 3D RENDERS, not attribute grids, so presentation = image and the
##attr_ levels are the author's own labels for what the renders varied, not text any
##respondent read.
##
##THE DESIGN IS FIXED, NOT RANDOMIZED PER RESPONDENT. The 18 profiles (6 tasks x 3) are the
##same for everyone and form a balanced orthogonal array: each of the 3 levels of each of
##the 5 attributes appears exactly 6 times across the 18, and only 18 of the 3^5 = 243
##possible combinations ever occur. What does vary by respondent is the POSITION of the
##three profiles within a task, so `profile` is a display position and not a profile label.
##
##Outcome: use `Task_n`, NOT `Tn_Chosen`. The two agree on every completed response, but
##`Tn_Chosen` is embedded data that is blank for 4 partial respondents who did answer --
##7 real choices in all. The author's own script uses `Tn_Chosen` after filtering
##Finished == 1, so his N is 106 completers; this table keeps all 110 respondents who chose
##at least once and is therefore slightly larger than the deposit's analysis file.
##Kept: cov_rit_affiliation_code (1-4; "Are you currently a member of the RIT community?",
##  and the author's script maps 1/2/3 -> RIT community, 4 -> not RIT, without naming the
##  three affiliation types, so the codes stay), cov_attachment (1-5, "How attached do you
##  feel to Rochester Institute of Technology?", asked only of RIT members),
##  cov_familiarity (1-5, "How familiar are you with RIT's tiger mascot?"),
##  cov_age_group_code and cov_gender_code (no codebook maps either set of codes;
##  cov_gender_code uses 1/2/3/5 as recorded, with 4 -- self-describe -- never chosen),
##  cov_duration_sec, cov_display_check (1 = could see the images clearly; the only value
##  present), trial_practice_choice (which of 3 the respondent picked in the practice task,
##  respondent-level and constant across tasks).
##Dropped: IP address, latitude/longitude, recipient name/email, external reference,
##  Q_RecaptchaScore, the Qualtrics metadata rows, and the Tn_Chosen duplicates. The
##  18-years-or-older consent item is constant (1) and dropped. Gender_4_TEXT is empty.
##Count: 643 tasks x 3 profiles = 1,929 rows over 110 respondents -- 106 answered all six
##  tasks, one answered four, three answered one -- with exactly one chosen profile in each
##  task. The full 110 x 6 grid would be 1,980 rows; the 17 unanswered tasks are omitted.
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
from irw_validate.conjoint import validate_conjoint_frame  # noqa: E402

ATTRS = {
    "Material": "attr_material",
    "HeadBodyRatio": "attr_head_body_ratio",
    "EyeShape": "attr_eye_shape",
    "FurColor": "attr_fur_color",
    "BodyType": "attr_body_type",
}
POS = {"A": 1, "B": 2, "C": 3}

raw, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(os.path.join(raw, "Study1.csv"), dtype=str, keep_default_na=False)
# rows 0-1 of a Qualtrics export are the question label and the ImportId JSON
d = d.iloc[2:].reset_index(drop=True)
assert d["ResponseId"].is_unique and len(d) == 114, (len(d), d["ResponseId"].is_unique)
assert set(d["DistributionChannel"]) == {"anonymous"}, set(d["DistributionChannel"])

# Task_n is the answer of record; Tn_Chosen agrees wherever it is filled in
for t in range(1, 7):
    both = (d[f"Task_{t}"] != "") & (d[f"T{t}_Chosen"] != "")
    assert (d.loc[both, f"Task_{t}"] == d.loc[both, f"T{t}_Chosen"]).all(), t

answered = (d[[f"Task_{t}" for t in range(1, 7)]] != "").sum(axis=1)
d = d[answered > 0].reset_index(drop=True)
assert len(d) == 110, len(d)
ids = {r: i + 1 for i, r in enumerate(sorted(d["ResponseId"]))}

rows = []
for _, r in d.iterrows():
    for t in range(1, 7):
        pick = r[f"Task_{t}"]
        if pick == "":
            continue
        for letter, pos in POS.items():
            lev = {new: r[f"T{t}{letter}_{src}"] for src, new in ATTRS.items()}
            assert all(v != "" for v in lev.values()), (r["ResponseId"], t, letter)
            rows.append({
                "id": ids[r["ResponseId"]],
                "task": t,
                "profile": pos,
                "choice": int(pick == str(pos)),
                **lev,
                "cov_rit_affiliation_code": r["RIT Affiliation"],
                "cov_attachment": r["Attachment"],
                "cov_familiarity": r["Familiarity"],
                "cov_age_group_code": r["Age"],
                "cov_gender_code": r["Gender"],
                "cov_duration_sec": r["Duration (in seconds)"],
                "cov_display_check": r["Display Check"],
                "trial_practice_choice": r["Practice"],
            })

o = pd.DataFrame(rows)
o["cov_duration_sec"] = o["cov_duration_sec"].astype(int)   # numeric, per J8
# one chosen profile per task, three profiles per task
per_task = o.groupby(["id", "task"])["choice"].agg(["sum", "count"])
assert (per_task["sum"] == 1).all() and (per_task["count"] == 3).all()
# the fixed 18-profile design, balanced: each level exactly 6 of 18
design = o.loc[o["id"] == 1, ["task", "profile"] + list(ATTRS.values())]
assert len(design.drop_duplicates(list(ATTRS.values()))) == 18
for c in ATTRS.values():
    assert set(design[c].value_counts()) == {6}, c
assert len(o) == 1929 and len(per_task) == 643, (len(o), len(per_task))

# the conjoint validator (rules J1-J7) gates the write; the core one would fail
# C1 on a table with no item/resp. opt_out=no is this design's design_outcomes.csv row.
report = validate_conjoint_frame(o, label="byun_2026_mascot",
                                 opt_out={"choice": "no"})
assert not report.errors, [(f.check, f.message) for f in report.errors]
for f in report.findings:
    print(f"  [{f.severity}] {f.check}: {f.message}")

o.to_csv(os.path.join(out, "byun_2026_mascot.csv"), index=False)
print("byun_2026_mascot.csv", o.shape, "respondents", o["id"].nunique(), "tasks", len(per_task))
