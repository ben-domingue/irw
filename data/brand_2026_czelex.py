"""CzeLex: concreteness, imageability, age-of-acquisition, valence and gender ratings for
9,601 Czech words (Brand, Smolík, Chromý, Ceháková & Preininger 2026, Behavior Research
Methods 58, 347, 10.3758/s13428-026-03217-4).

Source: OSF tqxfm (CC BY-NC-SA 4.0 on the node; the GitHub copy of the code,
jamesbrandscience/czelex, is GPL-3.0, and the OSF stamp governs the data),
https://osf.io/tqxfm/, `Analysis/raw_filtered_data/`:
  czelex_raw_filtered_ratings_data.csv      subject, dimension, name, value, value1, value_known
  czelex_raw_filtered_demographic_data.csv  subject, age, gender, gender_scale
These are trial-level ratings after the authors' participant and response filters
(CzeLex_norms_filtering.Rmd: Czech L1, age, straightlining, calibrator words, AoA
outliers). The unfiltered ratings (`raw_unfiltered_data/`) are on the node too.

Scales (as observed): concreteness 1-5, imageability 1-7; valence and gender -3..3 (negative/masculine
low); AoA is an age in years typed by the participant (0-55 in the file). One table holds
all five, as the stimulus-norms ruling asks.

Stimulus-norms shape (irw#2983): id = word (`name`), item = dimension, resp = `value1`,
rater = `subject`. A response of "unknown" (`value_known` = 0) is kept as resp NA with
`dontknow` = 1; `dontknow` = 0 on every rated row. Two kinds of row are left out:
  * name == "undefined" (10,844 rows): an empty stimulus slot from the jsPsych lists,
    not a word.
  * the gender and valence ratings of the 1,254 SocioLex-CZ participants (254,771
    rows). The authors' preprocessing (CzeLex_norms_preproccessing.Rmd) binds the
    SocioLex word ratings into CzeLex; they are hosted once, in
    preininger_2025_sociolex_words, which also has their location and political
    ratings. Those participants are identified by their Response_ID in SocioLex's
    `sociolex_demographics_words.csv` (OSF pv9md), which this script reads for that.
Rater covariates from the demographic file: cov_age, cov_gender and cov_gender_scale (the
participant's own placement on the gender scale), as recorded.

    python3 data/brand_2026_czelex.py --src-dir <dir with the two czelex csv files> \
        --sociolex-demo <sociolex_demographics_words.csv> -o <out dir>
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

TABLE = "brand_2026_czelex"
DIMS = {"concreteness", "imageability", "aoa", "valence", "gender"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src-dir", required=True)
    p.add_argument("--sociolex-demo", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    src, out = pathlib.Path(a.src_dir), pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    r = pd.read_csv(src / "czelex_raw_filtered_ratings_data.csv", dtype=str, keep_default_na=False)
    d = pd.read_csv(src / "czelex_raw_filtered_demographic_data.csv", dtype=str, keep_default_na=False)
    assert len(r) == 2069077 and set(r.dimension) == DIMS
    assert set(r.subject) == set(d.subject)

    undefined = r.name == "undefined"
    soc = set(pd.read_csv(a.sociolex_demo, dtype=str, usecols=["Response_ID"]).Response_ID)
    from_soc = r.subject.isin(soc)
    assert set(r[from_soc].dimension) == {"gender", "valence"}
    print(f"  dropped: {int(undefined.sum())} 'undefined' rows, "
          f"{int((from_soc & ~undefined).sum())} SocioLex rows from {r[from_soc].subject.nunique()} raters")
    r = r[~undefined & ~from_soc]

    known = r.value_known.map({"1": True, "0": False})
    assert known.notna().all()
    assert (r.value[~known] == "unknown").all() and (r.value1[~known] == "NA").all()
    v = pd.to_numeric(r.value1.where(known), errors="raise")
    df = pd.DataFrame({"id": r.name.values, "item": r.dimension.values, "resp": v.values,
                       "dontknow": (~known).astype(int).values, "rater": r.subject.values})
    for dim, lo, hi in (("concreteness", 1, 5), ("imageability", 1, 7),
                        ("valence", -3, 3), ("gender", -3, 3), ("aoa", 0, 60)):
        s = df.resp[df.item == dim].dropna()
        assert s.between(lo, hi).all(), (dim, s.min(), s.max())

    c = d.rename(columns={"age": "cov_age", "gender": "cov_gender", "gender_scale": "cov_gender_scale"})
    c["cov_age"] = pd.to_numeric(c.cov_age)
    c["cov_gender_scale"] = pd.to_numeric(c.cov_gender_scale.replace("NA", None))
    df = df.merge(c, left_on="rater", right_on="subject", how="left").drop(columns="subject")
    cols = ["id", "item", "resp", "dontknow", "cov_age", "cov_gender", "cov_gender_scale", "rater"]
    df = df[cols].sort_values(["id", "item", "rater"]).reset_index(drop=True)
    assert not df.duplicated(["id", "item", "rater"]).any()

    rep = validate_frame(df, label=TABLE, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(df)} words={df.id.nunique()} raters={df.rater.nunique()} "
          f"dims={df.item.nunique()} dontknow={int(df.dontknow.sum())}")


if __name__ == "__main__":
    main()
