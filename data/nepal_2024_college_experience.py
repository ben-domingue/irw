#!/usr/bin/env python3
"""Nepal et al. (2024), the College Experience Study: a five-year mobile
sensing and EMA study of Dartmouth undergraduates (2017-2022); the EMA PHQ-4
and state self-esteem items, via the openESM harmonised copy.

Source: https://zenodo.org/records/22953080 (openESM 0040_nepal)
DOI: 10.5281/zenodo.22953080
Original deposit: https://www.kaggle.com/datasets/subigyanepal/college-experience-dataset
    (Kaggle, CC BY-NC-SA 4.0), released by the study team: owner Subigya
    Nepal (first author), creator Arvind Pillai (third author)
Paper: Nepal S, Liu W, Pillai A, Wang W, Vojdanovski V, Huckins JF, Rogers C,
    Meyer ML, Campbell AT (2024). Capturing the College Experience: A
    Four-Year Mobile Sensing Study of Mental Health, Resilience and Behavior
    of College Students during the Pandemic. Proceedings of the ACM on
    Interactive, Mobile, Wearable and Ubiquitous Technologies 8(1), 1-37.
    doi:10.1145/3643501
Data: 0040_nepal_ts.tsv
License: CC BY-NC-SA 4.0 (openESM copy and Kaggle original). ShareAlike: the
    tables carry the same licence.
Item text: shipped. English wording and response labels from the dataset's
    own EMA codebook (0040_nepal_codebook.csv in the openESM record).

openESM ships the EMA part only (not the sensor data), as one row per person
per calendar date, almost all empty. 218 students answered the PHQ-4 and
state self-esteem items, about every six days on average (median gap five
days), on 35,348 dates between 2017-09-07 and 2022-07-02.

Tables written
--------------
nepal_2024_phq4          PHQ-4, 4 items, 0 (not at all) - 3 (nearly every day)
nepal_2024_state_self_esteem
                         4 items from the State Self-Esteem Scale, 1 (not at
                         all) - 5 (extremely), "Right now, ..."

Coding notes
------------
* There is at most one report per person-date, and on every report all
  eight items are answered (asserted).
* `wave` is each person's report number in date order, shared by the two
  tables; `date` is the report's calendar date as Unix seconds at 00:00
  UTC. No time of day is shipped.
* resp is as shipped; no item is reverse-scored (sse3-1, "I worry about
  what other people think of me", runs opposite to the other three).
* No covariates: none are in the openESM copy.

Not shipped
-----------
affect        Photographic Affect Meter: a choice among 16 pictures, not an
              ordinal rating.
stressed, social_level
              Single items.
covid_*, social_media_use
              Ten COVID-19 items on concern, impact, support and social
              media use: not a scale (the codebook marks them as
              non-standard).
avg_ema_rt    Mean time per EMA, an aggregate rather than an item time.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22953080"
TS_FILE = "0040_nepal_ts.tsv"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PHQ_PROMPT = ("Over the last 2 weeks, how often have you been bothered by "
              "the following problems?")
TABLES = {
    "nepal_2024_phq4": dict(
        instrument="Patient Health Questionnaire-4 (PHQ-4)",
        prompt=PHQ_PROMPT, scale=range(0, 4),
        options={0: "Not at all", 1: "Several days",
                 2: "More than half the days", 3: "Nearly every day"},
        items=[("nervous", "Feeling nervous, anxious or on edge"),
               ("worrying", "Not being able to stop or control worrying"),
               ("depressed", "Feeling down, depressed or hopeless"),
               ("anhedonia", "Little interest or pleasure in doing things")]),
    "nepal_2024_state_self_esteem": dict(
        instrument="State Self-Esteem Scale, four items",
        prompt="", scale=range(1, 6),
        options={1: "Not at All", 2: "A Little Bit", 3: "Somewhat",
                 4: "Very Much", 5: "Extremely"},
        items=[("perception_worry",
                "Right now, I worry about what other people think of me."),
               ("appearance_pleased",
                "Right now, I am pleased with my appearance."),
               ("feel_smart", "Right now, I feel as smart as others."),
               ("feel_good", "Right now, Overall, I feel good about myself.")]),
}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{TS_FILE}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == TS_FILE)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep="\t", low_memory=False)


def write_items(table, spec):
    rows = []
    for col, text in spec["items"]:
        for v in spec["scale"]:
            rows.append([table, f"{table}_1", col, spec["instrument"],
                         "English", "", "", spec["prompt"], "", text, "", "",
                         spec["options"][v], "", v])
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
    df = load()
    assert len(df) == 217155 and df["id"].nunique() == 220, df.shape
    assert not df.duplicated(["id", "date"]).any()

    cols = [c for spec in TABLES.values() for c, _ in spec["items"]]
    answered = df[cols].notna()
    assert (answered.all(axis=1) | ~answered.any(axis=1)).all()
    df = df[answered.all(axis=1)].copy()
    assert len(df) == 35348 and df["id"].nunique() == 218

    day = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["date"] = (day - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
    df = df.sort_values(["id", "date"], kind="stable")
    df["wave"] = df.groupby("id").cumcount() + 1

    for table, spec in TABLES.items():
        tcols = [c for c, _ in spec["items"]]
        long = df.melt(id_vars=["id", "wave", "date"], value_vars=tcols,
                       var_name="item", value_name="resp")
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave", "date"]]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        scale = spec["scale"]
        assert long["resp"].between(scale[0], scale[-1]).all(), table
        assert len(long) == 35348 * len(tcols)
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
