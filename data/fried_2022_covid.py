#!/usr/bin/env python3
"""Fried et al. (2022), mental health and social contact during the COVID-19
lockdown in the Netherlands, via the openESM harmonised copy.

Source: https://zenodo.org/records/22809490 (openESM 0001_fried)
DOI: 10.5281/zenodo.22809490
Original deposit: https://osf.io/mvdpe/ (OSF, no separate DOI; CC BY 4.0)
Paper: Fried EI, Papanikolaou F, Epskamp S (2022). Mental Health and Social
    Contact During the COVID-19 Pandemic: An Ecological Momentary Assessment
    Study. Clinical Psychological Science. doi:10.1177/21677026211017839
Data: 0001_fried_ts.tsv
License: CC BY 4.0 (openESM copy and original OSF deposit)

79 people, up to four Ethica-app prompts a day for two weeks (2020-03-16 to
2020-03-29), 18 five-point ordinal items: ten momentary-affect items (stress,
anxiety, depression, fatigue, hunger, loneliness, anger; "Not at all" ..
"Extremely") and eight time-use items, including three COVID-19-specific ones
(social contact, social media, music, procrastination, time outdoors, time on
COVID-19, COVID-19 worry, time at home; "0 minutes" .. "> 2h").

Coding notes
------------
* `wave` is each person's report number in time order (sorted on `date`, the
  openESM-supplied UTC timestamp of the answer). The raw `response` column is
  the same instant in local Europe/Amsterdam time (CET/CEST, ambiguous
  abbreviations pandas will not parse), so `date` -- already ISO 8601 UTC --
  is the timestamp parsed here, not `response`.
* `date` is that UTC timestamp as Unix seconds.
* No `rt`. `duration` is issued-to-response latency, and for the reports
  dropped below (next bullet) it is not a latency at all: it is the literal
  string "Expired" or "Canceled", a marker for a prompt nobody answered.
* 424 of 4372 rows have all 18 items missing -- a prompt that expired,
  was canceled, or was opened and closed with nothing entered. These carry no
  response of any kind (74 of them lack even a timestamp) and are dropped
  before wave numbering, not just at the per-item `resp` stage, so they do not
  consume a wave slot. The remaining 3948 rows each have at least one item
  answered; item-level gaps (up to 21 of 3948 for a single item) are dropped
  per item in the melt, same as any other missing response.

Columns not shipped
--------------------
scheduled, issued, response  Prompt/answer bookkeeping; `date` already carries
              the UTC answer instant. `response` is additionally unreliable
              for unanswered prompts (see above).
duration      Issued-to-response latency; excluded per project convention.
day, beep     day is study day, beep is within-day prompt index -- both
              derivable from `date`/`wave` and not part of the IRW schema.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22809490"
FILENAME = "0001_fried_ts.tsv"
TABLE = "fried_2022_covid"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

INSTRUMENT = "Fried et al. (2022) COVID-19 ecological momentary assessment"

LIKERT = range(1, 6)
LIKERT_ANCHORS = {1: "Not at all", 2: "Slightly", 3: "Moderately", 4: "Very",
                  5: "Extremely"}
DURATION_ANCHORS = {1: "0 minutes", 2: "5-15 min", 3: "15-60 min",
                     4: "1-2 hours", 5: "> 2h"}

# item -> (item_text, section label, anchor map)
ITEMS = {
    "difficulties_relaxing": ("I found it difficult to relax.",
                              "Stress (General Item)", LIKERT_ANCHORS),
    "irritable": ("I felt (very) irritable",
                 "Stress (General Item)", LIKERT_ANCHORS),
    "worry": ("I was worried about different things",
             "Anxiety (General Item)", LIKERT_ANCHORS),
    "nervous": ("I felt nervous, anxious or on edge",
               "Anxiety (General Item)", LIKERT_ANCHORS),
    "nothing_look_forward": ("I felt that I had nothing to look forward to",
                             "Depression (General Item)", LIKERT_ANCHORS),
    "anhedonia": ("I couldn't seem to experience any positive feeling at all",
                 "Depression (General Item)", LIKERT_ANCHORS),
    "tired": ("I felt tired", "Fatigue", LIKERT_ANCHORS),
    "hungry": ("In the past 3h, I was hungry", "Hunger", LIKERT_ANCHORS),
    "alone": ("I felt like I lack companionship, or that I am not close to "
             "people.", "Loneliness", LIKERT_ANCHORS),
    "angry": ("I felt angry", "Anger", LIKERT_ANCHORS),
    "social_offline": ("I spent ___ minutes on meaningful, offline, social "
                       "interaction", "Social Contact", DURATION_ANCHORS),
    "social_online": ("I spent __ minutes using social media to kill/pass "
                      "the time", "Social Media use", DURATION_ANCHORS),
    "time_music": ("I spent __ minutes listening to music", "Music",
                  DURATION_ANCHORS),
    "procrastinated": ("To what degree did you postpone working on a task?",
                       "Procrastination", DURATION_ANCHORS),
    "time_outdoors": ("I spent __ minutes outside (outdoors)?",
                      "Time spent outdoors", DURATION_ANCHORS),
    "covid_occupied": ("I spent __ occupied with the coronavirus (e.g. "
                       "watching news thinking about it talking to friends "
                       "about it)", "COVID-19", DURATION_ANCHORS),
    "covid_worry": ("I spent __ thinking about my own health or that of my "
                    "close friends and family members regarding the "
                    "coronavirus", "COVID-19", DURATION_ANCHORS),
    "time_home": ("I spent __ at home (including the home of parents/"
                 "partner)", "COVID-19", DURATION_ANCHORS),
}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{FILENAME}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep="\t")


def write_items():
    rows = []
    for item, (text, section, anchors) in ITEMS.items():
        for v in LIKERT:
            rows.append([TABLE, f"{TABLE}_{section}", item, INSTRUMENT,
                         "English", "", "", "", "", text, "", "",
                         anchors[v], "", v])
    path = os.path.join(ITEMDIR, f"{TABLE}__items.csv")
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
    df = load()
    assert len(df) == 4372 and df["id"].nunique() == 79, df.shape

    items = list(ITEMS)
    n = len(df)
    df = df[~df[items].isna().all(axis=1)].copy()
    assert n - len(df) == 424, n - len(df)

    df["date"] = pd.to_datetime(df["date"], utc=True)
    assert df["date"].notna().all()
    df = df.sort_values(["id", "date"], kind="stable")
    df["wave"] = df.groupby("id").cumcount() + 1
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    df["date"] = (df["date"] - epoch) // pd.Timedelta(seconds=1)
    # study ran 2020-03-16 .. 2020-03-29 (UTC)
    assert df["date"].between(1584356481, 1585512000).all()

    long = df.melt(id_vars=["id", "wave", "date"], value_vars=items,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "date"]]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert long["resp"].between(1, 5).all()
    assert not long.duplicated(["id", "item", "wave"]).any()
    # wave must follow time within person
    assert (long.groupby("id")["date"].diff().dropna() >= 0).all()
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    print(f"{path}: {long['id'].nunique()} people x {long['item'].nunique()} "
          f"items = {len(long):,} responses, max wave {long['wave'].max()}")
    ipath, k = write_items()
    print(f"{ipath}: {k} item text rows")


if __name__ == "__main__":
    main()
