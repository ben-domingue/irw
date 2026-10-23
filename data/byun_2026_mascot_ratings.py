##Tiger-mascot design ratings (Study 2) from
##Byun, J. (2026). A Perceptual Evaluation Framework for 3D Digital Character Design:
##Aggregate Preference versus Contextual Signaling in a Two-Phase Conjoint Study.
##Data: OSF https://osf.io/cyd9v/ (node created 2026-05-26; no article DOI in the deposit).
##Licence: the OSF node sets NO licence; included on the depositor's written permission
##(Permission via Email, Byun to ben-domingue, 2026-10; see processing_notes/outreach).
##Files read: Study2.csv (raw Qualtrics export). "R Coding for Study 2 Analysis.docx" was
##read as text, not run; it is the source for the design identities and the preference
##labels below.
##Usage: python3 byun_2026_mascot_ratings.py <dir holding Study2.csv> <output dir>
##
##The second phase of the same project, and NOT a conjoint: each respondent saw two finished
##tiger-mascot designs one after the other and rated each on the same six 1-7 items, so this
##is an ordinary item-response table (two stimuli x six dimensions = 12 items) and belongs in
##the core warehouse rather than the conjoint family. 229 respondents, 12 items, 2,704
##responses. 232 responses were exported: 2 Qualtrics previews are dropped, and 1 of the
##remaining 230 consented and then rated nothing.
##
##WHICH DESIGN IS WHICH. The export names the blocks A and B. The author's analysis script
##prints the A columns under the heading "Expert" and the B columns under "Data-Drv", and
##labels its Q5A preference codes 1 = Expert, 2 = Data-Driven, 3 = No Preference; the A/B
##labels are therefore design identities, not display positions, and the item names follow
##them (expert_*, datadriven_*). The order they were SHOWN in is a separate column in the
##deposit and is kept as cov_presentation_order (Expert_First / DataDriven_First, missing
##for 26 of the kept respondents). This identification rests on the deposit's analysis
##code, not on a codebook: nothing in the deposit states it in prose.
##
##Items, with the wording from the export's label row (the same six for each design):
##  impression   "Please rate your overall impression of this mascot design."
##  approachable "This mascot looks approachable and friendly."
##  confident    "This mascot looks confident."  (the column is named "Leadership")
##  appropriate  "This design feels appropriate for a school or university mascot."
##               (the B block reads "for a university mascot")
##  interact     "I would enjoy interacting with this mascot in person."
##  photo        "I would want to take a photo with this mascot."
##resp is the stored 1-7 code. The deposit records no anchor labels for the 1-7 scale, so
##the direction is assumed from the wording and is not confirmed: treat 7 as agreement.
##Kept: cov_presentation_order, cov_preference (which design the respondent preferred
##  overall, as text from the author's own labels), cov_preference_strength (1-3),
##  cov_noticed_difference_code (1-3; "Did you notice any visual differences between the two
##  mascot designs?"), cov_difference_code (1/3/4 of the coded answer to what difference was
##  noticed; no codebook maps the options), cov_age_group_code, cov_gender_code (1/2/3/5 as
##  recorded; 4 = self-describe was never chosen), cov_duration_sec.
##Dropped: IP address, latitude/longitude, recipient name/email, external reference,
##  Q_RecaptchaScore/Status/Error, the Qualtrics metadata rows, the free-text answer to the
##  "what difference" question (7 respondents), the "Another" page-break display item, and
##  the 18-years-or-older consent item (constant). No attention-check column is present,
##  although the author's script filters on one.
##NO RESPONDENT FILTERING. The author's script keeps only completers who passed an attention
##  check, took at least 90 seconds and did not straightline, which is an analysis decision;
##  this table keeps every non-preview respondent with at least one rating, so it is larger
##  than the deposit's analysis file. cov_duration_sec is kept so that filter can be redone.
import sys
import os
import pandas as pd

DIMS = [
    ("impression", "A1 Impression", "B1 Impression"),
    ("approachable", "A2 Approachable", "B2??Approachable"),
    ("confident", "A3 Leadership", "B3??Leadership"),
    ("appropriate", "A4 Appropriateness", "B4??Appropriateness"),
    ("interact", "A5 Interaction", "B5 Interaction"),
    ("photo", "A6 Photo", "B6 Photo"),
]
PREF = {"1": "Expert", "2": "Data-Driven", "3": "No Preference"}

raw, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(os.path.join(raw, "Study2.csv"), dtype=str, keep_default_na=False)
# rows 0-1 of a Qualtrics export are the question label and the ImportId JSON
d = d.iloc[2:].reset_index(drop=True)
assert d["ResponseId"].is_unique and len(d) == 232, (len(d), d["ResponseId"].is_unique)
d = d[d["DistributionChannel"] == "anonymous"].reset_index(drop=True)
assert len(d) == 230, len(d)

cols = {}
for name, a, b in DIMS:
    cols[f"expert_{name}"] = a
    cols[f"datadriven_{name}"] = b
for c in cols.values():
    assert set(d[c].unique()) <= {"", "1", "2", "3", "4", "5", "6", "7"}, c

d["id"] = [i + 1 for i in range(len(d))]
cov = pd.DataFrame({
    "id": d["id"],
    "cov_presentation_order": d["presentation_order"],
    "cov_preference": d["Q5A Preference"].map(lambda v: PREF.get(v, "")),
    "cov_preference_strength": d["Q5B Strength of pref"],
    "cov_noticed_difference_code": d["Q6A Notice Diff??"],
    "cov_difference_code": d["Q6B Difference"],
    "cov_age_group_code": d["Age"],
    "cov_gender_code": d["Gender"],
    "cov_duration_sec": d["Duration (in seconds)"],
})
assert set(d["Q5A Preference"].unique()) <= set(PREF) | {""}

long = d.melt(id_vars=["id"], value_vars=list(cols.values()),
              var_name="src", value_name="resp")
inv = {v: k for k, v in cols.items()}
long["item"] = long["src"].map(inv)
long = long[long["resp"] != ""].drop(columns=["src"])
o = long.merge(cov, on="id", how="left")
o = o[["id", "item", "resp"] + [c for c in cov.columns if c != "id"]]
o = o.sort_values(["id", "item"]).reset_index(drop=True)

assert o["item"].nunique() == 12 and len(o) == 2704, (o["item"].nunique(), len(o))
assert o["id"].nunique() == 229, o["id"].nunique()
assert (o.groupby(["id", "item"]).size() == 1).all()
o.to_csv(os.path.join(out, "byun_2026_mascot_ratings.csv"), index=False)
print("byun_2026_mascot_ratings.csv", o.shape, "respondents", o["id"].nunique(),
      "items", o["item"].nunique())
