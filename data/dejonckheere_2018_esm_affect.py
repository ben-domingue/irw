#!/usr/bin/env python3
"""Dejonckheere et al. (2018), momentary affect in a two-week experience
sampling study of a Belgian community sample, via the openESM harmonised copy.

Source: https://zenodo.org/records/17347570 (openESM 0012_dejonckheere)
DOI: 10.5281/zenodo.17347570
Original deposit: 10.6084/m9.figshare.7150664 (Figshare, CC BY 4.0)
Paper: Dejonckheere E, Kalokerinos EK, Bastian B, Kuppens P (2018). Poor
    emotion regulation ability mediates the link between depressive symptoms
    and affective bipolarity. Cognition and Emotion 33(5), 1076-1083
    (online 2018, print 2019). doi:10.1080/02699931.2018.1524747
Data: 0012_dejonckheere_ts.tsv
License: CC BY 4.0 (openESM copy and original Figshare deposit)
Item text: shipped. Dutch and English wording from the codebook of the larger
    study (https://osf.io/mqwyv/files/487eg, linked from the openESM record);
    the English is the authors' own, translation_source=study_supplied.

100 people, 7 semi-random prompts a day for 14 days (98 scheduled prompts each),
five momentary-affect sliders per prompt: "How happy / relaxed / sad / angry /
stressed do you feel at the moment?", "not at all [emotion]" .. "very
[emotion]".

Coding notes
------------
* `wave` is the scheduled prompt number, 1..98 (the openESM `counter`, which is
  (day - 1) * 7 + beep -- asserted below). This differs from fried_2022_covid
  and bailon_2020_covidaffect, which number each person's answered reports in
  time order: neither this file nor the original .sav carries a timestamp, so
  there is nothing to sort on, and the schedule index is the only time
  information there is. Missed prompts therefore leave gaps in `wave`, as in
  westhoff2023_pbat.
* No `date`: no timestamp in the openESM copy or the original deposit.
* 1,098 of 9,800 prompts have all five items missing (unanswered prompts).
  Every other prompt has all five answered, so the melt drops exactly those
  rows and no others.
* The codebook gives the slider as 1..100, but the data run 0..100 (0 occurs
  for every item). Kept as shipped; resp is the raw slider position. Every
  value is a whole number, so resp is written as an integer.

Columns not shipped
-------------------
day, beep     Both derivable from `wave`.
static file   ces_dmean, bd_imean, era, rrs_br: per-person means of the CES-D,
              BDI, Emotion Regulation Ability and RRS-brooding scales from the
              baseline survey. Scale composites, not responses or background
              covariates; the item-level baseline data are not in the deposit.
"""

import csv
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "17347570"
FILENAME = "0012_dejonckheere_ts.tsv"
TABLE = "dejonckheere_2018_esm_affect"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

INSTRUMENT = ("Dejonckheere et al. (2018) experience sampling: momentary "
              "affect sliders")
SCALE = range(0, 101)
# item -> (Dutch stem, English stem, (lo anchor), (hi anchor)); anchors are
# (Dutch, English). Both from the codebook, whose anchors are the templates
# "helemaal niet [emotie]" / "zeer [emotie]"; only the endpoints are labelled.
ITEMS = {
    "happy": ("Hoe blij voel je je op dit moment?",
              "How happy do you feel at the moment?",
              ("helemaal niet blij", "not at all happy"),
              ("zeer blij", "very happy")),
    "relaxed": ("Hoe ontspannen voel je je op dit moment?",
                "How relaxed do you feel at the moment?",
                ("helemaal niet ontspannen", "not at all relaxed"),
                ("zeer ontspannen", "very relaxed")),
    "sad": ("Hoe droevig voel je je op dit moment?",
            "How sad do you feel at the moment?",
            ("helemaal niet droevig", "not at all sad"),
            ("zeer droevig", "very sad")),
    "angry": ("Hoe kwaad voel je je op dit moment?",
              "How angry do you feel at the moment?",
              ("helemaal niet kwaad", "not at all angry"),
              ("zeer kwaad", "very angry")),
    "stressed": ("Hoe gestresseerd voel je je op dit moment?",
                 "How stressed do you feel at the moment?",
                 ("helemaal niet gestresseerd", "not at all stressed"),
                 ("zeer gestresseerd", "very stressed")),
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
    for item, (stem, stem_en, lo, hi) in ITEMS.items():
        for v in SCALE:
            opt = lo if v == SCALE[0] else hi if v == SCALE[-1] else ("", "")
            rows.append([TABLE, f"{TABLE}_1", item, INSTRUMENT, "Dutch",
                         "", "", "", "", stem, stem_en, "",
                         opt[0], opt[1], v])
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
    assert len(df) == 9800 and df["id"].nunique() == 100, df.shape
    assert (df.groupby("id").size() == 98).all()
    assert (df["counter"] == (df["day"] - 1) * 7 + df["beep"]).all()
    assert not df.duplicated(["id", "counter"]).any()

    items = list(ITEMS)
    answered = df[items].notna()
    # a prompt is answered in full or not at all
    assert answered.all(axis=1).sum() + (~answered).all(axis=1).sum() == len(df)
    assert (~answered).all(axis=1).sum() == 1098

    df = df.rename(columns={"counter": "wave"})
    long = df.melt(id_vars=["id", "wave"], value_vars=items,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"]]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert long["resp"].between(SCALE[0], SCALE[-1]).all()
    assert len(long) == (9800 - 1098) * len(items)
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
