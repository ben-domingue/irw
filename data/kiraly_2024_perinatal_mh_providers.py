from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306265
# DOI: 10.1371/journal.pone.0306265
# Kiraly, Boyle-Duke & Shklarski (2024), "The role of maternal and child
# healthcare providers in identifying and supporting perinatal mental
# health disorders". S2 Data (.xlsx). CC BY 4.0. N=101 obstetricians /
# other maternal-child healthcare providers surveyed on their practices.
# Two distinct item blocks -> two tables:
#   freq:    16 items on a 5-pt behavioral frequency scale
#            (never=1, sometimes=2, about half the time=3,
#             most of the time=4, always=5)
#   symptoms: 19-item yes/no checklist of which symptoms respondents
#             consider signs of postpartum depression/anxiety
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0306265.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FREQ_MAP = {
    "never": 1, "sometimes": 2, "about half of the time": 3,
    "most of the time": 4, "always": 5,
}
YN_MAP = {"no": 0, "yes": 1}

FREQ_COLS = [
    "usually_ask_my_patients_about_their_mental_health_and_emotional_state_in_their_first_visit",
    "do_you_use_the_edinburgh_postnatal_depression_scale",
    "if_noticed_that_the_mother_looking_sad_tired_upset_unhappy_or_flat_affect_will_address_it_with_her",
    "ask_about_the_mothers_connection_with_her_infant_during_office_visits",
    "ask_about_the_mothers_social_support_and_forms_of_help",
    "provide_my_patients_with_information_about_pre_postpartum_depression_and_anxiety",
    "in_the_office_waiting_room_there_are_brochures_informative_papers_about_pre_postpartum_depression_and_anxiety",
    "ask_about_my_patients_social_support_and_planning_to_get_forms_of_support_after_birth",
    "ask_about_the_infants_well_being_during_postpartum_office_visits",
    "ask_about_the_mothers_well_being_and_mental_health_during_postpartum_office_visits",
    "more_alert_to_patients_mental_health_and_emotional_state_if_they_had_miscarriages_or_complications_in_the_past",
    "ask_about_the_mother_baby_attachment",
    "ask_the_mother_about_the_birth_and_encourage_her_to_share_her_experiences",
    "focus_on_the_infant_and_do_not_ask_the_mother_about_her_well_being",
    "observe_the_infant_mother_connection_during_the_appointment",
    "when_asking_about_feeding_also_ask_the_mother_about_experiences_feeding_her_infant_with_breastfeeding",
]

SYMPTOM_COLS = [
    "Excessive_crying", "Feeling_numb", "Feeling_little_to_no_attachment_to_the_baby",
    "No_interest_in_things_that_used_to_give_pleasure", "Little_feeling_of_enjoyment",
    "No_energy", "Feelings_of_failure", "Feeling_overwhelmed_by_the_smallest_tasks",
    "Hopelessness", "Anxiety", "Agitation_with_self_others_baby", "Insomnia",
    "Excessive_sleeping", "Difficulty_concentrating", "Change_in_appetite",
    "Fear_of_being_alone_with_the_baby",
    "Intrusive_thoughts_of_harming_the_baby_or_of_harmful_things_happening_to_the_baby",
    "Difficulty_shaking_unwanted_feelings", "Fear_these_symptoms_will_last",
]

COV_COLS = {
    "gender": "cov_gender",
    "age": "cov_age",
    "ethnicity": "cov_ethnicity",
    "highest_degree": "cov_highest_degree",
    "profession": "cov_profession",
    "employment_status": "cov_employment_status",
    "how_long_practicing": "cov_years_practicing",
    "group": "cov_provider_group",
}


def _load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df = pd.read_excel(tmp.name)
    df = df.rename(columns={"subject": "id", **COV_COLS})
    return df


def _ship(df, item_cols, value_map, out_name):
    cov_cols = list(COV_COLS.values())
    d = df.copy()
    for c in item_cols:
        d[c] = d[c].astype(str).str.strip().str.lower().map(value_map)
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = _load()
    _ship(df, FREQ_COLS, FREQ_MAP, "kiraly_2024_perinatal_mh_freq")
    _ship(df, SYMPTOM_COLS, YN_MAP, "kiraly_2024_perinatal_mh_symptoms")


if __name__ == "__main__":
    convert()
