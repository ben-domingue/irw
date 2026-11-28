"""SocioLex-CZ: socio-semantic ratings of Czech words and pictures (Preininger, Brand, Kříž
& Ceháková 2025, Behavior Research Methods 58, 18, 10.3758/s13428-025-02907-9).

Source: OSF pv9md, https://osf.io/pv9md/ (10.17605/OSF.IO/PV9MD). The node's licence
stamp says "Other" and points to its `LICENSE` file, which is CC BY-NC-SA 4.0. Built from
the authors' cleaned long files in `sociolex_data/processed/`:
  sociolex_ratings_words.csv          Response_ID, dimension, item, value, value1
  sociolex_ratings_images.csv         the same for the MultiPic pictures
  sociolex_demographics_{words,images}.csv   one row per participant
These are the raw responses after the authors' participant filters (Czech L1, age,
straightlining on every scale; sociolex_cleaning.Rmd). Unfiltered long files are in
`sociolex_data/raw/`. Two tables, one per stimulus set, since the word and picture
surveys had different participants (no Response_ID is in both):

preininger_2025_sociolex_words: 3,111 strings rated by 1,254 people. The paper reports
  norms for 2,999 words; every string in the ratings file is kept.
preininger_2025_sociolex_images: 500 MultiPic pictures, each shown in colour or in
  grey scale (a participant saw one version), rated by 455 people. id is the picture
  code plus the version (`PICTURE_454_colour`), because the two versions are different
  images; sociolex_coding.csv on the node maps codes to names (454 = chicken).

Stimulus-norms shape (irw#2983): id = the stimulus, item = the dimension (gender,
location, political, valence), resp = the authors' numeric code `value1`, -3..3, rater =
Response_ID. For words the labels run silně/velmi mužské, venkovské, liberální,
negativní = -3 to silně/velmi ženské, městské, konzervativní, pozitivní = 3
(feminine, urban, conservative, positive are high). For pictures the authors reverse
location and valence so that they run the same way as for words; checked on the data
(farm and chicken lowest on location, city and lift highest). Their Rmd's prose says the
opposite for location, but the code and the data agree with the words. "Toto slovo
neznám" (don't know this word) and the pictures' "unknown" are kept as resp NA with
`dontknow` = 1 (0 on every rated row). The words survey's fifth dimension, age (which
age groups a word is associated with, several bands could be ticked), is a multi-select,
not a rating, and is not built (`sociolex_ratings_words_age.csv`). CzeLex (Brand et al.
2026, brand_2026_czelex) reuses these participants' gender and valence word ratings;
that table leaves them out so they are hosted once, here.

Rater covariates from the demographics files: cov_age, cov_gender (female, male,
non-binary or self-report; the free-text self-description is not carried),
cov_education, cov_sample (university or prolific) and the participant's own placement
on the four scales (cov_gender_scale, cov_location_scale, cov_political_scale,
cov_optimism_scale), as recorded.

    python3 data/preininger_2025_sociolex.py --src-dir <dir with the four csv files> -o <out>
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

DIMS = {"gender", "location", "political", "valence"}
COVS = {"participant_age": "cov_age", "participant_gender_category": "cov_gender",
        "participant_education": "cov_education", "participant_sample": "cov_sample",
        "participant_gender_scale": "cov_gender_scale",
        "participant_location_scale": "cov_location_scale",
        "participant_political_scale": "cov_political_scale",
        "participant_optimism_scale": "cov_optimism_scale"}
NUMERIC_COVS = ["cov_age", "cov_gender_scale", "cov_location_scale",
                "cov_political_scale", "cov_optimism_scale"]


def build(ratings, demo, table, unknown, out, images):
    r = pd.read_csv(ratings, dtype=str, keep_default_na=False)
    d = pd.read_csv(demo, dtype=str, keep_default_na=False)
    assert set(r.dimension) == DIMS and set(r.language) == {"cz"}
    assert set(r.Response_ID) <= set(d.Response_ID)
    dk = r.value == unknown
    assert (r.value1[dk] == "NA").all() and not (r.value1[~dk] == "NA").any()
    v = pd.to_numeric(r.value1.where(~dk), errors="raise")
    assert v.dropna().isin(range(-3, 4)).all()
    df = pd.DataFrame({"id": r["item"] + ("_" + r.version if images else ""),
                       "item": r.dimension, "resp": v.astype("Int64"),
                       "dontknow": dk.astype(int), "rater": r.Response_ID})
    if images:
        assert set(r.version) == {"colour", "gray"} and r["item"].str.startswith("PICTURE_").all()
    else:
        assert set(r.version) == {"words"}
    c = d[["Response_ID"] + list(COVS)].rename(columns=COVS)
    for col in NUMERIC_COVS:
        c[col] = pd.to_numeric(c[col].replace("NA", None))
    for col in set(COVS.values()) - set(NUMERIC_COVS):
        c[col] = c[col].replace("NA", None)
    df = df.merge(c, left_on="rater", right_on="Response_ID", how="left").drop(columns="Response_ID")
    cols = ["id", "item", "resp", "dontknow"] + list(COVS.values()) + ["rater"]
    df = df[cols].sort_values(["id", "item", "rater"]).reset_index(drop=True)
    assert not df.duplicated(["id", "item", "rater"]).any()

    rep = validate_frame(df, label=table, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} stimuli={df.id.nunique()} raters={df.rater.nunique()} "
          f"dims={df.item.nunique()} dontknow={int(df.dontknow.sum())} resp={df.resp.min()}-{df.resp.max()}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src-dir", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    src, out = pathlib.Path(a.src_dir), pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    build(src / "sociolex_ratings_words.csv", src / "sociolex_demographics_words.csv",
          "preininger_2025_sociolex_words", "Toto slovo neznám", out, images=False)
    build(src / "sociolex_ratings_images.csv", src / "sociolex_demographics_images.csv",
          "preininger_2025_sociolex_images", "unknown", out, images=True)


if __name__ == "__main__":
    main()
