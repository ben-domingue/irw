#!/usr/bin/env python3
"""Menghini, Pastore & Balducci (2023), experience sampling of momentary mood,
task demands and task control in Italian office workers, via the openESM
harmonised copy.

Source: https://zenodo.org/records/22952987 (openESM 0022_menghini)
DOI: 10.5281/zenodo.22952987
Original deposit: https://osf.io/87a9p/ (OSF, CC BY 4.0; S5 processed data and
    S6 protocol and scales). openESM cites the GitHub code repository
    (Luca-Menghini/ESMscales-workplaceStress, GPL-3.0), but that repository
    holds code only and points to OSF for the data.
Paper: Menghini L, Pastore M, Balducci C (2023). Workplace Stress in Real Time:
    Three Parsimonious Scales for the Experience Sampling Measurement of
    Stressors and Strain at Work. European Journal of Psychological Assessment
    39(6), 424-432. doi:10.1027/1015-5759/a000725
Data: 0022_menghini_ts.tsv (responses); ESM_processed.csv from OSF
    (https://osf.io/download/srh9c/) for the person-level covariates, which
    openESM does not ship
License: openESM lists its copy as GPL-3.0 (inherited from the code
    repository); the OSF data deposit is CC BY 4.0. The table carries GPL-3.0,
    the terms of the copy it is built from (datastandard.md, "Before you
    start").
Item text: shipped for the task tables only. Italian wording and anchors
    from the app screenshots in S6 (https://osf.io/download/ehw38/), English
    from the same figures (the authors' own), translation_source=
    study_supplied. The MDMQ wording is not written: the MDMQ adapts Steyer
    et al.'s MDBF, which is `block` in itemtext/instrument_rights_register.csv
    (Hogrefe charges a reprint fee for its test items). Its wording stays in
    TABLES below for reference only. The screenshots show
    the feminine Italian forms (rilassata, tesa, ...); the app presumably
    gendered the adjectives per participant, so men saw masculine forms.

175 workers with data (211 ids in the file), three non-consecutive workdays
(Mon/Wed/Fri), seven prompts a day from 9:15 to 18:15. Prompt 1 is a
'baseline' questionnaire with the mood items only; prompts 2-7 are 'work'
questionnaires that add the task items. All items are 1-7 sliders.

Tables written
--------------
menghini_2023_mdmq          Italian MDMQ, 9 bipolar items: valence (well,
                            discontent, state), tense arousal (tense, calm,
                            placid), fatigue (awake, energyless, rested)
menghini_2023_task_demands  Task Demand Scale, 4 items
menghini_2023_task_control  Task Control Scale, 3 items

Coding notes
------------
* resp is the scale as presented (1 = left anchor, 7 = right anchor). The
  paper reverse-scored six MDMQ items (v1, v3, t2, t3, f1, f3) before
  analysis, and the OSF processed file holds them reversed; openESM's copy
  holds them unreversed (openESM == 8 - OSF for all six, on all 1,979
  matched prompts). The unreversed values are shipped, so every item's
  direction matches its item text. Across items, direction varies.
* The timestamps are Italian local time, although openESM suffixes them with
  `Z`: prompt 1 is scheduled at 9:15 local and its run times fall at
  09:12-10:38 as stamped. They are parsed as Europe/Rome and converted to
  Unix seconds for `date`. All prompts fall on weekday working hours, so no
  stamp lands in a DST gap or overlap.
* `wave` is each person's answered-prompt number in time order (sorted on the
  submission timestamp), shared by the three tables, so one prompt has the
  same wave in each. Baseline prompts carry no task items, so the task
  tables skip those waves.
* 36 rows have no timestamp and no item responses. Each is the only row of
  its id -- 36 enrolled people who never answered a prompt -- so dropping
  them leaves 175 people (174 with any task item).
* Covariates come from OSF ESM_processed.csv, joined on id; all four are
  constant within person. 9 of the 175 people have all four missing.

Columns not shipped
-------------------
os, survey_type, day, day_of_week, beep, run_timestamp
              Device and schedule bookkeeping; the time information is in
              `wave` and `date`.
what, how, whom, n_people
              Work-sampling context (task type, means of work, people
              involved): multiple-choice categories, not item responses.
job, jobOut   Free-form job title (19 values) and a flag derived from it.
              Not shipped: with age, gender and sector in a 211-person sample
              they add re-identification risk for little analytic value.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22952987"
TS_FILE = "0022_menghini_ts.tsv"
OSF_COV_URL = "https://osf.io/download/srh9c/"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALE = range(1, 8)
COVS = {"gender": "cov_gender", "age": "cov_age",
        "work.hours": "cov_work_hours", "job.sector": "cov_job_sector"}

# table -> (instrument, (Italian prompt, English prompt), items)
# item -> (Italian lo, Italian hi, English lo, English hi, Italian stem,
#          English stem); MDMQ items are bipolar, with no stem beyond the
#          section prompt.
TABLES = {
    "menghini_2023_mdmq": (
        "Multidimensional Mood Questionnaire (MDMQ), Italian adaptation, "
        "with three added items (Menghini et al. 2023)",
        ("Come ti senti in questo momento?", "How do you feel at the moment?"),
        {
            "well": ("Molto male", "Molto bene", "Very unwell", "Very well",
                     "", ""),
            "tense": ("Molto rilassata", "Molto tesa", "Very relaxed",
                      "Very tense", "", ""),
            "awake": ("Molto stanca", "Molto sveglia", "Very tired",
                      "Very awake", "", ""),
            "discontent": ("Molto soddisfatta", "Molto insoddisfatta",
                           "Very content", "Very discontent", "", ""),
            "calm": ("Molto agitata", "Molto calma", "Very agitated",
                     "Very calm", "", ""),
            "energyless": ("Molto pieno di energia", "Molto privo di energia",
                           "Very full of energy", "Very without energy",
                           "", ""),
            "state": ("In uno stato molto negativo",
                      "In uno stato molto positivo",
                      "In a very negative state", "In a very positive state",
                      "", ""),
            "placid": ("Molto nervosa", "Molto tranquilla", "Very nervous",
                       "Very placid", "", ""),
            "rested": ("Molto affaticata", "Molto fresca", "Very fatigued",
                       "Very rested", "", ""),
        }),
    "menghini_2023_task_demands": (
        "Task Demand Scale (TDS; Menghini et al. 2023)",
        ("In relazione all'attività svolta...",
         "In relation with the work activity..."),
        {
            "too_much": ("Per niente", "Moltissimo", "Not at all",
                         "Very much", "Ho avuto molto da fare",
                         "I had to do too much"),
            "work_fast": ("Per niente", "Moltissimo", "Not at all",
                          "Very much",
                          "L'attività mi ha richiesto di lavorare velocemente",
                          "The activity required me to work very fast"),
            "multitasking": ("Per niente", "Moltissimo", "Not at all",
                             "Very much", "Ho fatto più cose contemporaneamente",
                             "I did multiple things at once"),
            "hard_work": ("Per niente", "Moltissimo", "Not at all",
                          "Very much",
                          "Ho dovuto lavorare in maniera molto intensa",
                          "I had to work very hard"),
        }),
    "menghini_2023_task_control": (
        "Task Control Scale (TCS; Menghini et al. 2023)",
        ("In relazione all'attività svolta...",
         "In relation with the work activity..."),
        {
            "change_task": ("Per niente", "Moltissimo", "Not at all",
                            "Very much", "Potevo scegliere di cambiare attività",
                            "I could change task if I chose to"),
            "decide_task": ("Per niente", "Moltissimo", "Not at all",
                            "Very much",
                            "Ho potuto scegliere come svolgere l'attività",
                            "I could decide how to perform the task"),
            "schedule_task": ("Per niente", "Moltissimo", "Not at all",
                              "Very much",
                              "Ho potuto pianificare il tempo di svolgimento "
                              "dell'attività",
                              "I could schedule the time of the task"),
        }),
}
# MDBF-derived wording: rights register verdict block (Hogrefe reprint fee)
NO_ITEMTEXT = {"menghini_2023_mdmq"}
EXPECTED = {"menghini_2023_mdmq": 175, "menghini_2023_task_demands": 174,
            "menghini_2023_task_control": 174}


def fetch(url, path):
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{TS_FILE}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == TS_FILE)
        fetch(url, path)
    df = pd.read_csv(path, sep="\t")
    osf = pd.read_csv(fetch(OSF_COV_URL, "/tmp/osf_87a9p_ESM_processed.csv"))
    return df, osf


def covariates(osf):
    per = osf.groupby("ID")[list(COVS)].nunique(dropna=True)
    assert (per <= 1).all().all()
    cov = (osf.groupby("ID")[list(COVS)].first().reset_index()
              .rename(columns={"ID": "id", **COVS}))
    assert len(cov) == 211
    assert cov["cov_gender"].dropna().isin(["F", "M"]).all()
    assert cov["cov_job_sector"].dropna().isin(["Private", "Public"]).all()
    return cov


def write_items(table, instrument, prompt, items):
    rows = []
    for item, (lo_it, hi_it, lo_en, hi_en, stem_it, stem_en) in items.items():
        if not stem_it:                      # bipolar MDMQ item
            stem_it, stem_en = f"{lo_it} - {hi_it}", f"{lo_en} - {hi_en}"
        for v in SCALE:
            opt = ((lo_it, lo_en) if v == SCALE[0] else
                   (hi_it, hi_en) if v == SCALE[-1] else ("", ""))
            rows.append([table, f"{table}_1", item, instrument, "Italian",
                         "", "", prompt[0], prompt[1], stem_it, stem_en, "",
                         opt[0], opt[1], v])
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
    df, osf = load()
    assert len(df) == 2015 and df["id"].nunique() == 211, df.shape
    all_items = [i for _, _, items in TABLES.values() for i in items]

    n = len(df)
    unanswered = df["submission_timestamp"].isna()
    assert not df.loc[unanswered, all_items].notna().any().any()
    df = df[~unanswered].copy()
    assert n - len(df) == 36

    # stamped "Z" but local Italian time (see coding notes)
    local = pd.to_datetime(df["submission_timestamp"].str.rstrip("Z"))
    df["date"] = (local.dt.tz_localize("Europe/Rome", ambiguous="raise",
                                       nonexistent="raise")
                  .dt.tz_convert("UTC").astype("int64") // 10**9)
    first = df.loc[df["beep"] == 1, "run_timestamp"].str[11:16]
    assert first.between("09:00", "10:45").all()
    df = df.sort_values(["id", "date"], kind="stable")
    assert not df.duplicated(["id", "date"]).any()
    df["wave"] = df.groupby("id").cumcount() + 1

    cov = covariates(osf)
    df = df.merge(cov, on="id", how="left", validate="many_to_one")
    cov_cols = list(COVS.values())

    for table, (instrument, prompt, items) in TABLES.items():
        long = df.melt(id_vars=["id", "wave", "date"] + cov_cols,
                       value_vars=list(items), var_name="item",
                       value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave", "date"] + cov_cols]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        assert long["resp"].between(SCALE[0], SCALE[-1]).all(), table
        assert long["id"].nunique() == EXPECTED[table], (
            table, long["id"].nunique())
        assert not long.duplicated(["id", "item", "wave"]).any()
        assert (long.groupby("id")["date"].diff().dropna() >= 0).all()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        print(f"{path}: {long['id'].nunique()} people x "
              f"{long['item'].nunique()} items = {len(long):,} responses, "
              f"max wave {long['wave'].max()}")
        if table in NO_ITEMTEXT:
            continue
        ipath, k = write_items(table, instrument, prompt, items)
        print(f"{ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
