#!/usr/bin/env python3
"""Scharbert et al. (2024), momentary affect in a 4-week experience sampling
study across Europe and beyond during the outbreak of the war in Ukraine
(January-April 2022). Listed by openESM as 0071_scharbert; built from the
authors' OSF raw files, not openESM's copy (see coding notes).

Source: https://osf.io/8f3yu/ (OSF, CC BY 4.0), files
    01_Data_and_Code/data/00_raw_data/x1_states.csv (ESM reports) and
    x0_traits.csv (demographics)
openESM copy: https://zenodo.org/records/22953262 (0071_scharbert,
    10.5281/zenodo.22953262, CC BY 4.0)
Paper: Scharbert J, Humberg S, Kroencke L, et al. (2024). Psychological
    well-being in Europe after the outbreak of war in Ukraine. Nature
    Communications 15, 1202. doi:10.1038/s41467-024-44693-6
License: CC BY 4.0 (OSF deposit and openESM copy)
Item text: shipped. English wording and response format from the study
    codebook (Codebook_blinded.pdf on OSF, "Momentary Well-Being"). The
    study ran in many countries; the local-language versions are not in the
    deposit, so only the English master wording is given.

2,791 adults from 90 countries of residence (2,783 with at least one answered
report), four ESM surveys a day at random times between 9:00 and 18:00 over
about four weeks. Six momentary affect
items, "I felt angry / anxious / sad / happy / excited / relaxed", 1 (not
agree at all) to 6 (agree completely).

Coding notes
------------
* Built from x1_states.csv rather than openESM's copy because within-day
  order rests on file order (next bullet), and openESM's row order differs
  from the raw file's for 604 of 2,791 people.
* Neither file records a time of day or a prompt number: each report has
  only its calendar date, and people answered up to four (rarely 5-7)
  times a day; the authors themselves average reports within the day.
  `wave` is each person's report number in the raw file's row order. Rows
  are in date order within every person (asserted), so the order across
  days is certain; the order within a day is assumed to be submission
  order and cannot be verified.
* `date` is the report's calendar date as Unix seconds at 00:00 UTC, so
  reports from the same day share a date. It is a date, not a timestamp.
* 653 rows have no answer to any item and are dropped before numbering;
  every other row answers all six.
* cov_country (country of residence, as coded in the source), cov_gender
  (1 female, 2 male, 3 other) and cov_age come from x0_traits.csv, the T1
  trait survey, joined on participant; constant within person.

Not shipped
-----------
x2_daily.csv  Evening-diary items on people in one's country (positivity,
              threat, similarity; 1-10): three single items on different
              constructs, not a scale.
x0_traits.csv scale scores (BFI-2 domains etc.): composites.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

TABLE = "scharbert_2024_esm_affect"
STATES_URL = "https://osf.io/download/rhu7c/"     # x1_states.csv
TRAITS_URL = "https://osf.io/download/v3n85/"     # x0_traits.csv
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

INSTRUMENT = ("Momentary well-being, ESM (Scharbert et al. 2024): three "
              "negative and three positive affect items")
SCALE = range(1, 7)
ANCHORS = {1: "not agree at all", 2: "disagree", 3: "somewhat disagree",
           4: "somewhat agree", 5: "agree", 6: "agree completely"}
# source column -> (item, wording)
ITEMS = {
    "state_na1": ("angry", "I felt angry."),
    "state_na2": ("anxious", "I felt anxious."),
    "state_na3": ("sad", "I felt sad."),
    "state_pa1": ("happy", "I felt happy."),
    "state_pa2": ("excited", "I felt excited."),
    "state_pa3": ("relaxed", "I felt relaxed."),
}
GENDER = {1: "female", 2: "male", 3: "other"}


def fetch(url, name):
    path = os.path.join("/tmp", f"osf_8f3yu_{name}")
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep=";", low_memory=False)


def write_items():
    rows = []
    for item, text in ITEMS.values():
        for v in SCALE:
            rows.append([TABLE, f"{TABLE}_1", item, INSTRUMENT, "English",
                         "", "", "", "", text, "", "", ANCHORS[v], "", v])
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
    df = fetch(STATES_URL, "x1_states.csv")
    traits = fetch(TRAITS_URL, "x0_traits.csv")
    assert len(df) == 95009 and df["participant"].nunique() == 2791
    # the leading index column is the export's row number, 1..n
    assert (df["Unnamed: 0"].to_numpy() == range(1, len(df) + 1)).all()
    df["row"] = range(len(df))
    df["day"] = pd.to_datetime(df["day"], format="%Y-%m-%d")

    cols = list(ITEMS)
    answered = df[cols].notna()
    assert (answered.all(axis=1) | ~answered.any(axis=1)).all()
    n = len(df)
    df = df[answered.all(axis=1)].copy()
    assert n - len(df) == 653

    df = df.sort_values(["participant", "row"], kind="stable")
    assert (df.groupby("participant")["day"].diff().dropna()
            >= pd.Timedelta(0)).all()
    df["wave"] = df.groupby("participant").cumcount() + 1
    df["date"] = (df["day"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(
        seconds=1)
    # study period Jan-Apr 2022
    assert df["date"].between(1640995200, 1651363200).all()

    per = traits.groupby("participant")[["country", "gender", "age"]]
    assert traits["participant"].is_unique and (per.nunique() <= 1).all().all()
    assert traits["gender"].dropna().isin(list(GENDER)).all()
    cov = pd.DataFrame({"id": traits["participant"],
                        "cov_country": traits["country"],
                        "cov_gender": traits["gender"].map(GENDER),
                        "cov_age": traits["age"]})
    df = df.rename(columns={"participant": "id"})
    df = df.merge(cov, on="id", how="left", validate="many_to_one")
    assert df["cov_country"].notna().all()
    covs = ["cov_country", "cov_gender", "cov_age"]

    long = df.melt(id_vars=["id", "wave", "date"] + covs, value_vars=cols,
                   var_name="src", value_name="resp")
    long["item"] = long["src"].map(lambda c: ITEMS[c][0])
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "date"] + covs]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert long["resp"].between(SCALE[0], SCALE[-1]).all()
    assert len(long) == 94356 * len(ITEMS)
    assert not long.duplicated(["id", "item", "wave"]).any()
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
