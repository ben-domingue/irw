import re
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "rf9k8-osfstorage-archive"
STUDY1 = ARCHIVE / "Study 1 - Actual Lifestyle Polarization"
STUDY2 = ARCHIVE / "Study 2 - Perceived Lifestyle Polarization"

SURVEY_CSV = STUDY1 / "Data" / "Data for Correlations" / "combined_survey.csv"
PERCEIVER_CSV = STUDY2 / "Data" / "perceiver_ratings_raw_data.csv"

OUT_DIR = BASE / "talaifar_2025_lifestyle_polarization"

STUDY1_COVS = {
    "semester": "cov_semester",
    "demog_politicalorientation": "cov_political_orientation",
    "demog_sex": "cov_sex",
    "demog_age": "cov_age",
    "demog_ethnicity": "cov_ethnicity",
    "demog_academicclass": "cov_academic_class",
    "demog_perceivedses": "cov_perceived_ses",
    "demog_religiosity": "cov_religiosity",
    "demog_mother_educationlevel": "cov_mother_education",
    "demog_father_educationlevel": "cov_father_education",
    "demog_relationshipstatus": "cov_relationship_status",
    "demog_currentlylivinginaustin": "cov_living_in_austin",
    "demog_currentemployment": "cov_current_employment",
    "demog_socialmedia_Facebook": "cov_socialmedia_facebook",
    "demog_socialmedia_YikYak": "cov_socialmedia_yikyak",
    "demog_socialmedia_messaging": "cov_socialmedia_messaging",
    "demog_socialmedia_otherSNSs": "cov_socialmedia_other_snss",
    "demog_socialmedia_microbloggingsites": "cov_socialmedia_microblogging",
    "demog_socialmedia_bloggingsites": "cov_socialmedia_blogging",
    "demog_socialmedia_mediasharingsites": "cov_socialmedia_mediasharing",
    "demog_socialmedia_contentsharingsites": "cov_socialmedia_contentsharing",
    "demog_socialmedia_virtualworlds": "cov_socialmedia_virtualworlds",
    "demog_socialmedia_MMORPGs": "cov_socialmedia_mmorpgs",
    "demog_socialmedia_onlineforums": "cov_socialmedia_onlineforums",
    "demog_socialmedia_userreviewsites": "cov_socialmedia_userreviews",
}

STUDY2_COVS = {
    "pol_ori": "cov_political_orientation",
    "pol_soc": "cov_political_orientation_social",
    "pol_ec": "cov_political_orientation_economic",
    "pol_parents": "cov_political_orientation_mom",
    "Q50": "cov_political_orientation_dad",
    "certain": "cov_certainty",
    "gender": "cov_gender",
    "age": "cov_age",
    "year": "cov_academic_class",
    "ethnicity": "cov_ethnicity",
    "perceived_ses": "cov_perceived_ses",
}

STUDY2_ITEMS = {
    "communication1_1": ("smsinnum", "social"),
    "communication1_2": ("smsoutnum", "social"),
    "communication1_3": ("smsinlen", "social"),
    "communication1_4": ("smsoutlen", "social"),
    "communication1_5": ("audioconvonum", "social"),
    "communication1_6": ("audioconvodur", "social"),
    "communication1_7": ("callinnum", "social"),
    "communication1_8": ("calloutnum", "social"),
    "communication1_9": ("callindur", "social"),
    "communication1_10": ("calloutdur", "social"),
    "communication2_1": ("ppl_friends", "social"),
    "communication2_2": ("ppl_alone", "social"),
    "communication2_3": ("ppl_family", "social"),
    "communication2_4": ("ppl_roommates", "social"),
    "communication2_5": ("ppl_sigother", "social"),
    "communication2_6": ("ppl_strangers", "social"),
    "communication2_11": ("act_talkingtextingsocializing", "social"),
    "leisure1_9": ("loc_friendshouse", "social"),
    "leisure1_1": ("timehome", "leisure"),
    "leisure1_2": ("loc_home", "leisure"),
    "leisure1_3": ("act_choreserrands", "leisure"),
    "leisure1_4": ("act_restnap", "leisure"),
    "leisure1_5": ("loc_bar", "leisure"),
    "leisure1_6": ("loc_frat", "leisure"),
    "leisure1_7": ("loc_religious", "leisure"),
    "leisure1_8": ("loc_cafe", "leisure"),
    "leisure1_10": ("loc_store", "leisure"),
    "leisure2_1": ("audioampmean", "leisure"),
    "leisure2_2": ("audiovoice", "leisure"),
    "leisure2_3": ("unlockdur", "leisure"),
    "leisure2_4": ("unlocknum", "leisure"),
    "leisure2_5": ("act_browsinginternetsocialmedia", "leisure"),
    "leisure2_6": ("act_watchtvmovies", "leisure"),
    "work1_1": ("act_working", "work"),
    "work1_2": ("act_studyingreading", "work"),
    "work1_3": ("act_classmeeting", "work"),
    "work1_4": ("loc_campus", "work"),
    "work1_5": ("ppl_students", "work"),
    "work1_6": ("ppl_coworkers", "work"),
    "work1_7": ("loc_library", "work"),
    "work1_8": ("loc_work", "work"),
    "work1_9": ("act_commuting", "work"),
    "movement1_1": ("activitywalk", "movement"),
    "movement1_2": ("activitystationary", "movement"),
    "movement1_3": ("activitybike", "movement"),
    "movement1_4": ("activityrun", "movement"),
    "movement1_5": ("act_exercising", "movement"),
    "movement1_6": ("loc_gym", "movement"),
    "movement1_8": ("routine_index", "movement"),
    "movement1_9": ("timeloc", "movement"),
    "movement1_10": ("locent", "movement"),
    "movement1_11": ("normlocent", "movement"),
    "movement2_1": ("actlevel", "movement"),
    "movement2_2": ("loc", "movement"),
    "movement2_3": ("locvis", "movement"),
    "movement2_4": ("maxdistance", "movement"),
    "movement2_5": ("distance", "movement"),
    "movement2_6": ("maxdistancehome", "movement"),
    "movement2_7": ("transitiontime", "movement"),
    "movement2_8": ("activityvehicle", "movement"),
    "movement2_9": ("loc_vehicle", "movement"),
}

ATTENTION_ITEM = "communication1_11"


def _melt(wide, item_cols, item_names=None):
    long = wide.melt(
        id_vars=["id"] + [c for c in wide.columns if c.startswith("cov_")],
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    if item_names is not None:
        long["item"] = long["item"].map(item_names)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    cov_cols = [c for c in long.columns if c.startswith("cov_")]
    return long[["id", "item", "resp"] + cov_cols]


def _study1_scales(survey):
    wide = survey.rename(columns={"userid": "id", **STUDY1_COVS})
    keep = ["id"] + [c for c in STUDY1_COVS.values() if c in wide.columns]

    bfi_cols = [f"bfi_{i}" for i in range(1, 45)]
    tivi_cols = sorted(
        (c for c in survey.columns if re.match(r"^tivi\d+_", c)),
        key=lambda c: int(re.match(r"^tivi(\d+)_", c).group(1)),
    )
    ls_cols = [f"ls_{i}" for i in range(1, 94)]

    tivi_names = {c: f"tivi_{re.match(r'^tivi(\d+)_', c).group(1)}" for c in tivi_cols}

    return {
        "talaifar_2025_study1_bfi.csv": _melt(wide[keep + bfi_cols], bfi_cols),
        "talaifar_2025_study1_tivi.csv": _melt(wide[keep + tivi_cols], tivi_cols, tivi_names),
        "talaifar_2025_study1_lifestyle_survey.csv": _melt(wide[keep + ls_cols], ls_cols),
    }


def _study2_ratings(raw):
    df = raw.iloc[2:].reset_index(drop=True)

    df = df[(df["id"] != "40607") & (df["Progress"] != "11")]
    df = df[df["id"] != "41799"]
    df = df[pd.to_numeric(df["Duration (in seconds)"], errors="coerce") > 120]

    wide = df.rename(columns={**STUDY2_COVS})
    attention = pd.to_numeric(df[ATTENTION_ITEM], errors="coerce")
    wide["cov_attention_check"] = attention.map({0.5: "pass"}).fillna("fail")

    keep = ["id"] + [c for c in wide.columns if c.startswith("cov_")]
    item_cols = list(STUDY2_ITEMS)
    names = {col: label for col, (label, _) in STUDY2_ITEMS.items()}

    long = _melt(wide[keep + item_cols], item_cols, names)
    domains = {label: domain for label, domain in STUDY2_ITEMS.values()}
    long.insert(3, "itemcov_domain", long["item"].map(domains))
    return long


def _study2_thermometer(raw):
    df = raw.iloc[2:].reset_index(drop=True)
    df = df[(df["id"] != "40607") & (df["Progress"] != "11")]
    df = df[df["id"] != "41799"]
    df = df[pd.to_numeric(df["Duration (in seconds)"], errors="coerce") > 120]

    wide = df.rename(columns={**STUDY2_COVS})
    attention = pd.to_numeric(df[ATTENTION_ITEM], errors="coerce")
    wide["cov_attention_check"] = attention.map({0.5: "pass"}).fillna("fail")

    keep = ["id"] + [c for c in wide.columns if c.startswith("cov_")]
    thermo_cols = ["polarization_9", "polarization_10"]
    names = {"polarization_9": "conservative", "polarization_10": "liberal"}
    long = _melt(wide[keep + thermo_cols], thermo_cols, names)
    return long


def convert_lifestyle_polarization_to_irw():
    OUT_DIR.mkdir(exist_ok=True)
    outputs = {}

    if SURVEY_CSV.is_file():
        outputs.update(_study1_scales(pd.read_csv(SURVEY_CSV)))
    else:
        print(f"Skip Study 1: missing {SURVEY_CSV}")

    if PERCEIVER_CSV.is_file():
        raw = pd.read_csv(PERCEIVER_CSV, dtype=str)
        outputs["talaifar_2025_study2_plp.csv"] = _study2_ratings(raw)
        outputs["talaifar_2025_study2_thermometer.csv"] = _study2_thermometer(raw)
    else:
        print(f"Skip Study 2: missing {PERCEIVER_CSV}")

    for name, df in outputs.items():
        df.to_csv(OUT_DIR / name, index=False)
        print(f"{name}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")


if __name__ == "__main__":
    convert_lifestyle_polarization_to_irw()
