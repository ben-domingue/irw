#!/usr/bin/env python3
"""Marian et al. (2023), the dynamic interplay of anxious and depressive
symptoms: 145 Romanian psychology undergraduates, three beeps a day for 21
days in 2020 (EMA anxiety, depression and negative-thought items), via
the openESM harmonised copy.

Source: https://zenodo.org/records/22692208 (openESM 0052_marian)
DOI: 10.5281/zenodo.22692208
Original deposit: https://osf.io/pt9dk/ (OSF, CC BY 4.0): data.csv,
    Codebook.xlsx, Analysis.R
Paper: Marian S, Costantini G, Macsinga I, Sava FA (2023). The Dynamic Interplay of
    Anxious and Depressive Symptoms in a Sample of Undergraduate Students.
    Journal of Psychopathology and Behavioral Assessment 45, 150-159.
    doi:10.1007/s10862-022-10014-8
Data: 0052_marian_ts.tsv (responses); data.csv on OSF (covariates)
License: CC BY 4.0 (openESM copy and OSF original).
Item text: shipped, English only. The study was administered in Romanian,
    and no Romanian wording is in the deposit (Codebook.xlsx and data.csv
    hold no Romanian letters; Analysis.R and the paper give English only),
    so this is the fallback: language=Romanian, the authors' English in the
    base fields, text_source=translated_substitute,
    translation_source=study_supplied. GAD and PHQ wording is the paper's
    Table 1 ("ESM item") where it lists the item, else the codebook; the
    negative-thought wording is the codebook's.

Tables written
--------------
marian_2023_gad      8 items adapted from the GAD-Q-IV, 1-4
marian_2023_phq9     the 9 PHQ-9 items, adapted, 1-4
marian_2023_thoughts 13 negative automatic thoughts, 1-4 (the paper does
                     not analyse or describe these; codebook only)

Coding notes
------------
* openESM's rows and item values match data.csv exactly (asserted), and its
  start_time is true UTC: data.csv's Start carries each phone's own offset
  (+0300 for nearly all, +0200 or +0000 for two people), and the two agree
  to the second on every answered beep (asserted).
* `wave` is the scheduled occasion, 1-63 ((day - 1) * 3 + beep); `date` is
  the beep's start time as Unix seconds (UTC).
* 861 beeps were missed (status 99) and have no answers. 43 are marked
  incomplete (status 2); their answered items are kept.
* resp is as shipped. Response labels follow the codebook: Never / Once /
  Several times / Many times for the GAD and PHQ items, Not at all / A
  short time / A long time / Most of the time for the thoughts. The paper's
  Method gives the second set for all EMA items ("For an extended period of
  time" for 3); the codebook is followed because it is per-item.
* No section prompt is shipped: the paper paraphrases the instruction
  (symptoms "in the past 4 h (since the last beep or since waking up)")
  but does not quote it.
* Covariates (per person, from data.csv): cov_sex, cov_age, cov_education,
  cov_occupation, cov_residence (rural/urban area of origin),
  cov_marital.

Not shipped
-----------
Baseline PHQ-9 and GAD-Q-IV (PHQ_demo*, GAD_demo*, scored GAD and PHQ):
    one occasion each, in data.csv only; not in this pass.
Seconds (completion time per beep), Resp_per_day, Waking_hour.
"""

import csv
import os
import sys

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22692208"
TS_FILE = "0052_marian_ts.tsv"
OSF_DATA = "https://osf.io/download/bnemp/"     # pt9dk data.csv
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FREQ = {1: "Never", 2: "Once", 3: "Several times", 4: "Many times"}
DUR = {1: "Not at all", 2: "A short time", 3: "A long time",
       4: "Most of the time"}

# openESM name, raw name, text
TABLES = {
    "marian_2023_gad": dict(
        instrument="GAD-Q-IV, adapted for EMA", options=FREQ, items=[
            ("worry", "GAD_Q1", "You worried more that it would have been "
             "appropriate for the situation you were in"),
            ("difficulty_control_worry", "GAD_Q2",
             "You found it difficult to control your worry"),
            ("restless", "GAD_Q3",
             "You've been restless or felt keyed up or on edge"),
            ("fatiguability", "GAD_Q4", "You've been easily fatigued"),
            ("difficulty_concentrating", "GAD_Q5",
             "You had concentration difficulties, or you felt like your "
             "mind is going blank"),
            ("irritable", "GAD_Q6", "You've been irritable"),
            ("muscle_tension", "GAD_Q7", "You had muscle tension"),
            ("sleep_difficulty", "GAD_Q8",
             "Last night, you had trouble falling asleep or didn't feel "
             "rested after sleep."),
        ]),
    "marian_2023_phq9": dict(
        instrument="Patient Health Questionnaire-9 (PHQ-9), adapted for EMA",
        options=FREQ, items=[
            ("anhedonia", "PHQ1",
             "Little interest or pleasure in doing things"),
            ("depressed", "PHQ2", "Feeling down, depressed, or hopeless"),
            ("sleep_problems", "PHQ3",
             "Trouble falling or staying asleep or sleeping too much."),
            ("tired", "PHQ4", "Feeling tired or having little energy"),
            ("appetite_change", "PHQ5", "Poor appetite or overeating"),
            ("worthlessness", "PHQ6",
             "Feeling bad about yourself—or that you are a failure or "
             "have let yourself or your family down"),
            ("concentration_trouble", "PHQ7",
             "Trouble concentrating on things, such as reading the "
             "newspaper or watching television"),
            ("psychomotor_change", "PHQ8",
             "Moving or speaking so slowly that other people could have "
             "noticed, or the opposite—being so fidgety or restless "
             "that you have been moving around a lot more than usual"),
            ("suicidal_ideation", "PHQ9",
             "Thoughts that you would be better off dead or of hurting "
             "yourself in some way"),
        ]),
    "marian_2023_thoughts": dict(
        instrument="Negative automatic thoughts (13 items, study EMA list)",
        options=DUR, items=[
            ("something_wrong", "Thought1", "There's something wrong with me."),
            ("cant_go_on", "Thought2", "I don't think I can go on like this."),
            ("dont_like_self", "Thought3", "I don't like myself."),
            ("no_good", "Thought4", "I’m no good."),
            ("nobody_likes", "Thought5", "Nobody likes me."),
            ("alone", "Thought6", "I am alone."),
            ("fear_sickness", "Thought7", "What if I get sick?"),
            ("awful_happen", "Thought8", "Something awful is going to happen."),
            ("life_not_worth", "Thought9", "Life isn’t worth living."),
            ("nobody_cares", "Thought10", "Nobody cares about me."),
            ("cant_stand", "Thought11", "I can't stand it anymore."),
            ("never_make_it", "Thought12", "I will never make it."),
            ("need_change", "Thought13", "Something has to change."),
        ]),
}

SEX = {1: "male", 2: "female"}
EDUCATION = {1: "secondary", 2: "bachelor", 3: "master", 4: "PhD"}
OCCUPATION = {1: "student only", 2: "student, employed part-time",
              3: "student, employed full-time"}
RESIDENCE = {1: "rural", 2: "urban"}
MARITAL = {1: "never married", 2: "married", 3: "in a relationship",
           4: "divorced"}


def fetch(url, path):
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def load():
    api = requests.get(f"https://zenodo.org/api/records/{REC}",
                       headers=HEADERS, timeout=60).json()
    url = next(f["links"]["self"] for f in api["files"]
               if f["key"] == TS_FILE)
    ts = pd.read_csv(fetch(url, f"/tmp/zenodo_{REC}_{TS_FILE}"), sep="\t")
    raw = pd.read_csv(fetch(OSF_DATA, "/tmp/osf_pt9dk_data.csv"))
    return ts, raw


def write_items(table, spec):
    rows = []
    for col, _, text in spec["items"]:
        for v, label in spec["options"].items():
            rows.append([table, f"{table}_1", col, spec["instrument"],
                         "Romanian", "", "", "", "", text, "", "", label,
                         "", v])
    path = os.path.join(ITEMDIR, f"{table}__items.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["table", "section_id", "item", "instrument", "language",
                    "instructions", "instructions_translated",
                    "section_prompt", "section_prompt_translated",
                    "item_text", "item_text_translated", "correct_response",
                    "option_text", "option_text_translated", "resp"])
        w.writerows(rows)
    return path, len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df, raw = load()
    assert len(df) == len(raw) == 9135 and df["id"].nunique() == 145
    for a, b in (("id", "ID"), ("day", "Day_no"), ("beep", "TP_nr")):
        assert (df[a].values == raw[b].values).all(), a
    assert (df["counter"] == (df["day"] - 1) * 3 + df["beep"]).all()
    assert not df.duplicated(["id", "counter"]).any()

    pairs = [(c, r) for spec in TABLES.values() for c, r, _ in spec["items"]]
    x = df[[c for c, _ in pairs]].to_numpy()
    y = raw[[r for _, r in pairs]].to_numpy()
    assert np.array_equal(np.nan_to_num(x, nan=-9), np.nan_to_num(y, nan=-9))

    start = pd.to_datetime(df["start_time"], utc=True, format="ISO8601")
    local = pd.to_datetime(raw["Start"].str.strip().replace("", np.nan),
                           utc=True, format="ISO8601")
    answered = df[[c for c, _ in pairs]].notna().any(axis=1)
    assert answered.sum() == 8274 and start[answered].notna().all()
    assert (start[answered] == local[answered]).all()
    assert (df.loc[~answered, "status"] == 99).all()

    df["wave"] = df["counter"]
    df["date"] = (start - pd.Timestamp("1970-01-01", tz="UTC")) \
        // pd.Timedelta(seconds=1)

    p = raw.groupby("ID").agg(
        Sex=("Sex", "first"), Age=("Age", "first"),
        Education=("Education", "first"), Occupation=("Occupation", "first"),
        Rural_urban=("Rural_urban", "first"), Marital=("Marital", "first"))
    for c in p.columns:
        assert (raw.groupby("ID")[c].nunique() == 1).all(), c
    cov = pd.DataFrame({"id": p.index,
                        "cov_sex": p["Sex"].map(SEX).values,
                        "cov_age": p["Age"].values,
                        "cov_education": p["Education"].map(EDUCATION).values,
                        "cov_occupation":
                            p["Occupation"].map(OCCUPATION).values,
                        "cov_residence":
                            p["Rural_urban"].map(RESIDENCE).values,
                        "cov_marital": p["Marital"].map(MARITAL).values})
    covs = [c for c in cov.columns if c != "id"]
    assert cov[covs].notna().all().all() and len(cov) == 145

    for table, spec in TABLES.items():
        tcols = [c for c, _, _ in spec["items"]]
        long = df.melt(id_vars=["id", "wave", "date"], value_vars=tcols,
                       var_name="item", value_name="resp").dropna(
                           subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(1, 4).all(), table
        long = long.merge(cov, on="id", how="left", validate="m:1")
        long = long[["id", "item", "resp", "wave", "date"] + covs]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item", "wave"]).any()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        print(f"{path}: {long['id'].nunique()} people x "
              f"{long['item'].nunique()} items = {len(long):,} responses, "
              f"max wave {long['wave'].max()}")
        ipath, k = write_items(table, spec)
        print(f"  {ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
