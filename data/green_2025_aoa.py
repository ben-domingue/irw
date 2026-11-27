"""Crowdsourced age-of-acquisition ratings for 11,075 English words in print (Green, Kong,
Brysbaert & Keogh 2025, Behavior Research Methods 57, 304, 10.3758/s13428-025-02843-8;
extends the Kuperman et al. 2012 norms).

Source: OSF ch48r (CC BY 4.0 on the node), https://osf.io/ch48r/,
`Crowdsourced Data/Complete Raw Data.csv`: the Amazon Mechanical Turk results file, one
row per HIT (3,938 HITs by 1,405 workers, `Anonymized_Participant_Id`). Each HIT showed up
to 111 words (`Input.Word1`..`Input.Word111`) and asked two questions per word on a
0-20 year slider in half-year steps (`Code used for Mechanical Turk.xml`):
  aoa_read   "At what age would you have first understood the word if you read it?"
             (`Answer.ageREADw<n>`, with a "Not Applicable" box `Answer.ageREADNAw<n>.on`)
  aoa_write  "At what age would you have first been able to spell the word correctly?"
             (`Answer.ageWRITENAw<n>`). The template gives this slider and its own
             "Not Applicable" box the same name, so the export keeps only the slider.
The item names follow the authors' published means (AoA_Read, AoA_Write). Only the
crowdsourced responses are built: the AI-generated AoA estimates on the node are model
output, not responses, and the cleaned/outlier-replaced versions are derived.

Stimulus-norms shape (irw#2983): id = word, item = aoa_read / aoa_write, rater = worker.
A ticked "Not Applicable" box (the worker could not read the word) is not a rating: both
of that word's rows are kept with resp NA and `dontknow` = 1 (the sliders then mostly sit
at their 0 default; the spelling box itself was not recorded). `dontknow` = 0 otherwise,
and blank for slot 30, whose box is missing from the export. `trial_hit` is the HIT's row
in the source file: workers did up to 50 HITs and 5,866 times met a word again in a later
HIT, so trial_hit separates those ratings. 159 HITs had no 111th word; empty slots produce
no rows. Covariates are as the worker reported them on that HIT (they are not always
constant across a worker's HITs; the few entries over 100, years of birth, are
blanked rather than converted): cov_age,
cov_age_english (age started learning English; 0 = from birth), cov_gender and
cov_education (from the form's one-hot boxes; blank when none was ticked). Place of birth
(free text) is not carried.

    python3 data/green_2025_aoa.py --src "<Complete Raw Data.csv>" -o <out dir>
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

TABLE = "green_2025_aoa"
GENDER = {"Answer.GenderFemale.female": "female", "Answer.GenderMale.male": "male",
          "Answer.GenderNonBinary.nonBinary": "non-binary",
          "Answer.GenderPreferNotToSay.preferNotToSay": "prefer not to say"}
EDUCATION = {"Answer.someHighSchool.someHighSchool": "some high school",
             "Answer.highSchoolDiploma.highSchoolDiploma": "high school diploma",
             "Answer.someCollege.someCollege": "some college",
             "Answer.associates.associates": "associate degree",
             "Answer.bachelors.bachelors": "bachelor's degree",
             "Answer.graduate.graduate": "graduate degree",
             "Answer.preferNotToSay.EdupreferNottoSay": "prefer not to say"}
SLOTS = range(1, 112)
NO_BOX = {30}


def one_hot(g: pd.DataFrame, labels: dict) -> pd.Series:
    hits = g[list(labels)].eq("TRUE")
    assert hits.sum(axis=1).max() <= 1
    return hits.idxmax(axis=1).map(labels).where(hits.any(axis=1))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    g = pd.read_csv(a.src, dtype=str, keep_default_na=False)
    assert len(g) == 3938, len(g)
    g["trial_hit"] = range(1, len(g) + 1)
    g["cov_gender"] = one_hot(g, GENDER)
    g["cov_education"] = one_hot(g, EDUCATION)
    for cov, col in (("cov_age", "Answer.ParticipantAge"),
                     ("cov_age_english", "Answer.ParticipantStartLearningEnglish")):
        v = pd.to_numeric(g[col].replace("", None))
        g[cov] = v.where(v <= 100)   # a handful of entries are years of birth
        print(f"  {cov}: {int((v > 100).sum())} HIT entries over 100 blanked")
    keep = ["Anonymized_Participant_Id", "trial_hit", "cov_age", "cov_age_english",
            "cov_gender", "cov_education"]

    parts = []
    for n in SLOTS:
        s = g[keep].copy()
        s["id"] = g[f"Input.Word{n}"].str.strip()
        box = None if n in NO_BOX else g[f"Answer.ageREADNAw{n:04d}.on"]
        s["dontknow"] = pd.NA if box is None else (box == "TRUE").astype(int)
        for item, col in (("aoa_read", f"Answer.ageREADw{n:04d}"),
                          ("aoa_write", f"Answer.ageWRITENAw{n:04d}")):
            t = s.copy()
            t["item"] = item
            t["resp"] = pd.to_numeric(g[col], errors="raise")
            parts.append(t[t.id != ""])
    df = pd.concat(parts, ignore_index=True)
    df["dontknow"] = df["dontknow"].astype("Int64")
    assert df.resp.between(0, 20).all() and (df.resp * 2 % 1 == 0).all()
    df.loc[df.dontknow == 1, "resp"] = pd.NA
    df = df.rename(columns={"Anonymized_Participant_Id": "rater"})
    cols = ["id", "item", "resp", "dontknow", "trial_hit", "cov_age", "cov_age_english",
            "cov_gender", "cov_education", "rater"]
    df = df[cols].sort_values(["id", "item", "rater", "trial_hit"]).reset_index(drop=True)
    assert not df.duplicated(["id", "item", "trial_hit"]).any()

    rep = validate_frame(df, label=TABLE, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(df)} words={df.id.nunique()} raters={df.rater.nunique()} "
          f"items={df.item.nunique()} dontknow_rows={int(df.dontknow.fillna(0).sum())} "
          f"resp={df.resp.min()}-{df.resp.max()}")


if __name__ == "__main__":
    main()
