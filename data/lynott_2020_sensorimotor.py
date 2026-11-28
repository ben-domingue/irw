"""Lancaster Sensorimotor Norms, trial-level ratings (Lynott, Connell, Brysbaert, Brand &
Carney 2020, Behavior Research Methods 52(3), 1271-1291, 10.3758/s13428-019-01316-z):
39,954 English words rated 0-5 on six perceptual modalities (auditory, gustatory, haptic,
interoceptive, olfactory, visual) and five action effectors (foot_leg, hand_arm, head,
mouth, torso).

Source: OSF rwhs6 (data component of 7emr6; CC BY 4.0 on both), https://osf.io/rwhs6/,
`Individual_participant_ratings_all_items_sensorimotor_norms_for_39954_words.UPDATED.csv`
(identical bytes to `sm_norms_trial_level.csv` in the update component 8k9mt, whose
`sm_norms_update.Rmd` documents the change; `README_trial_data_UPDATED.txt` gives the
columns). The UPDATED file corrects an error in the sex variable of the original trial
file, which is still on the node and is not used. Long format, one row per participant
response x word x dimension; each participant did one norming component (Perception: six
modalities; Action: five effectors) on one of 1,766 word lists, and a twelfth
pseudo-dimension, `Dont_know_word`, records whether they knew the word (1 = did not know;
the dimension ratings of that word are then NA).

Stimulus-norms shape (irw#2983): id = Word (upper case, as presented), item = the
dimension in lower case, resp = Rating, rater = participant_ID. The Dont_know_word rows
are folded into a `dontknow` column (1 = the participant did not know the word, resp NA;
0 = rated) rather than kept as an item: not knowing a word is not a sensorimotor rating.
`trial_list` is the word list (`List`, file name without `.csv`) and `trial_response` the
response id: participant_ID can cover several completed lists (README), so the response
id separates a participant's lists. In 227 response x word pairs the list showed the
word twice (HONEY, GRASS, ...; 67 words, 170 responses) and the two sets of ratings
sometimes differ; `trial_repeat` numbers the presentations in file order (1 everywhere else), and
each presentation's own Dont_know_word row is matched to it. Rater covariates cov_age and cov_sex are as given
(female, male, "prefer not to say"; NA where the authors had no data). Duration_minutes (Qualtrics completion time, flagged
as unreliable in the README), List_N and Participant_ID_anonymised are not carried.

The file is 1.37 GB and ~12.4M rows; it is read with categorical dtypes and kept categorical
through the build.

    python3 data/lynott_2020_sensorimotor.py --src <...UPDATED.csv> -o <out dir>
"""
import argparse
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from irw_validate import validate_frame  # noqa: E402

TABLE = "lynott_2020_sensorimotor"
DIMS = {"Auditory", "Gustatory", "Haptic", "Interoceptive", "Olfactory", "Visual",
        "Foot_leg", "Hand_arm", "Head", "Mouth", "Torso"}
DTYPES = {"participant_ID": "category", "response_ID": "category", "Word": "category",
          "Dimension": "category", "Rating": "float32", "Age": "float32",
          "Sex": "category", "Norming_Component": "category", "List": "category"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    r = pd.read_csv(a.src, usecols=list(DTYPES), dtype=DTYPES, na_values=["NA"],
                    keep_default_na=False)
    print(f"  read {len(r)} rows")
    assert set(r.Dimension.cat.categories) == DIMS | {"Dont_know_word"}
    assert r.groupby("response_ID", observed=True).participant_ID.nunique().max() == 1

    # A few lists showed a word twice: number the presentations in file order.
    r["trial_repeat"] = r.groupby(["response_ID", "Word", "Dimension"], observed=True).cumcount() + 1
    dk = r[r.Dimension == "Dont_know_word"][["response_ID", "Word", "trial_repeat", "Rating"]]
    assert dk.Rating.isin([0, 1]).all()
    dk = dk.rename(columns={"Rating": "dontknow"})
    r = r[r.Dimension != "Dont_know_word"]
    r = r.merge(dk, on=["response_ID", "Word", "trial_repeat"], how="left", validate="many_to_one")
    assert r.dontknow.notna().all(), "dimension rating without a Dont_know_word row"
    # README: NA rating <=> did not know the word
    assert ((r.dontknow == 1) == r.Rating.isna()).all()
    assert r.Rating.dropna().isin([0, 1, 2, 3, 4, 5]).all()
    assert set(r.Sex.dropna().unique()) <= {"female", "male", "prefer not to say"}

    # Categorical columns throughout: 11M object strings would need several GB.
    item = r.Dimension.cat.remove_unused_categories()
    lst = r.List.cat.remove_unused_categories()
    df = pd.DataFrame({
        "id": r.Word.cat.remove_unused_categories(),
        "item": item.cat.rename_categories([c.lower() for c in item.cat.categories]),
        "resp": r.Rating.astype("Int8"),
        "dontknow": r.dontknow.astype("int8"),
        "trial_list": lst.cat.rename_categories([c.removesuffix(".csv") for c in lst.cat.categories]),
        "trial_response": r.response_ID,
        "trial_repeat": r.trial_repeat.astype("int8"),
        "cov_age": r.Age.astype("Int16"),
        "cov_sex": r.Sex,
        "rater": r.participant_ID,
    })
    del r
    assert not df.duplicated(["id", "item", "trial_response", "trial_repeat"]).any()
    df = df.sort_values(["id", "item", "rater", "trial_response", "trial_repeat"]).reset_index(drop=True)

    rep = validate_frame(df, label=TABLE, profile="upload")
    for f in rep.findings:
        print(f"  {f.severity}: {f.check}: {f.message}")
    assert rep.ok, "validator errors"
    df.to_csv(out / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(df)} words={df.id.nunique()} raters={df.rater.nunique()} "
          f"responses={df.trial_response.nunique()} dims={df.item.nunique()} "
          f"dontknow_rows={int(df.dontknow.sum())}")


if __name__ == "__main__":
    main()
