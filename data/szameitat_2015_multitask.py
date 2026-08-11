#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0140371
# DOI: 10.1371/journal.pone.0140371
# SI: S1 Table (Raw data table of the collected data), XLSX
#     https://doi.org/10.1371/journal.pone.0140371.s001
#
# Szameitat et al. 2015, "'Women Are Better Than Men'-Public Beliefs on Gender
# Differences and Other Aspects in Multitasking", PLOS ONE.
#
# The raw file contains two separate 7-point rating instruments:
#   Question 11 (43 items): "How far do you agree with the following being
#     examples of multitasking?" -- Strongly disagree(-3) ... Neutral(0) ...
#     Strongly agree(+3). Columns Childcare..VideoGames.
#   Question 12 (15 items): "What do you think, how much multitasking is
#     required in the following occupations?" -- Not at all(0) ... Somewhat(3)
#     ... A great deal(6). Columns ConstructionWorker..Secretary.
# These are two distinct scales (different item content, different response
# anchors) so they are written as two separate IRW files.

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")
SRC_URL = "https://doi.org/10.1371/journal.pone.0140371.s001"

# Question 11: activities rated for agreement they are examples of multitasking
AGREE_ITEMS = [
    "Childcare", "Walking_Gum", "SATNav_Driving", "Walking_Talk", "GroupConvers",
    "Singing_WashingUp", "RevisingMultiplExams", "WatchScreen_Typing",
    "Keyboard_Mouse", "CookingMeal", "WashingUp_GetDressed", "PresentShopping",
    "Texting_walking", "ToddlerFeeding_Phoning", "Driving_Wiper", "TwoCustomers",
    "WalkDog_Convers", "Phone_Driving_Phone", "Phone_Driving_HandsFree",
    "EntGuests_Dinner", "Gardening", "Music_Cleaning", "Paperwork_Emails",
    "Tablet_Talking", "Exercise_Shower", "Running_Music", "TV_tablet",
    "Driving_TalkPass", "Shelves_Customer", "Dressed_Work", "Hoovering_Child",
    "ConvPhone_NextToYou", "Laundry_Phoning", "Writing_Phoning", "TV_Remote",
    "SortFiles_Customer", "Stroller_TalkChild", "TV_Writing", "Sandwich",
    "Driving_Radio", "Reading_Notes", "Baby_Toddler", "VideoGames",
]
AGREE_MAP = {
    "strongly disagree": -3, "disagree": -2, "slightly disagree": -1,
    "neutral": 0, "slightly agree": 1, "agree": 2, "strongly agree": 3,
}

# Question 12: occupations rated for how much multitasking they require
OCCUPATION_ITEMS = [
    "ConstructionWorker", "BankTeller", "CarMechanic", "Broker", "HousewifeMan",
    "Cleaner", "CashierSupermarket", "Teacher", "OfficeWorker", "ShopAssistant",
    "Carpenter", "CustomerServiceDesk", "BranchManager", "Accountant", "Secretary",
]
OCCUPATION_MAP = {
    "not at all": 0, "not much": 1, "little": 2, "somewhat": 3,
    "a lot": 4, "very much": 5, "a great deal": 6,
}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age_range",
    "Country": "cov_country",
    "Education": "cov_education",
    # "Occupation" is a free-text field (respondent's own job title) -- not
    # included as a covariate since it's uncontrolled open text.
}


def load_raw():
    raw = pd.read_excel(SRC_URL, sheet_name="Raw", header=None)
    hdr = raw.iloc[2].tolist()
    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = hdr
    data = data.reset_index(drop=True)
    data.insert(0, "id", data.index + 1)

    # normalize covariate text casing
    if "Gender" in data.columns:
        data["Gender"] = data["Gender"].astype(str).str.strip().str.title()
        data.loc[data["Gender"].isin(["Nan", ""]), "Gender"] = pd.NA
    data = data.rename(columns=COV_RENAME)
    return data


def clean_scale(data, item_cols, value_map, out_name, cov_cols):
    long = data.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                      var_name="item", value_name="resp_raw")
    long["resp_raw"] = long["resp_raw"].astype(str).str.strip().str.lower()
    long["resp"] = long["resp_raw"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(float)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    data = load_raw()
    cov_cols = [c for c in COV_RENAME.values() if c in data.columns]

    clean_scale(data, AGREE_ITEMS, AGREE_MAP,
                "szameitat_2015_multitask_examples", cov_cols)
    clean_scale(data, OCCUPATION_ITEMS, OCCUPATION_MAP,
                "szameitat_2015_occupation_multitask", cov_cols)


if __name__ == "__main__":
    convert()
