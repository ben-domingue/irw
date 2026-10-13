#!/usr/bin/env python3
"""Tammilehto et al. (2022), dynamics of attachment and emotion regulation in
daily life: 122 Finnish adults (mostly students at Tampere), a trait
questionnaire, then EMA seven times a day for a week in 2017, via the
openESM harmonised copy plus the authors' OSF trait file.

Source: https://zenodo.org/records/22953122 (openESM 0054_tammilehto)
DOI: 10.5281/zenodo.22953122
Original deposit: https://osf.io/e8423 ("Data and Codebook", in project
    osf.io/u59nd; OSF, CC BY 4.0): Basic_data.txt, AT_ER_MPLUS*.dat, codebook
Paper: Tammilehto J, Bosmans G, Kuppens P, Flykt M, Peltonen K, Kerns KA,
    Lindblom J (2022). Dynamics of attachment and emotion regulation in daily
    life: uni- and bidirectional associations. Cognition and Emotion 36(6),
    1109-1131. doi:10.1080/02699931.2022.2081534
Data: 0054_tammilehto_ts.tsv (EMA); Basic_data.txt on OSF (trait items and
    covariates)
License: CC BY 4.0 (openESM copy and OSF original).
Item text: shipped for the two EMA tables only, English only. The study was
    administered in Finnish and no Finnish wording is in the deposit (the
    codebook is English, the data files numeric), so this is the fallback:
    language=Finnish, the authors' English (the paper's Measures section,
    which quotes every EMA item) in the base fields,
    text_source=translated_substitute, translation_source=study_supplied.
    The trait tables ship without item text: the paper quotes one example
    item per scale, and the column order of the AVO/ANX items is not tied to
    the ECR-R's item numbers anywhere in the deposit.

Tables written
--------------
tammilehto_2022_state_attachment   6 items from the State Adult Attachment
                                   Measure (security, anxiety, avoidance; 2
                                   each), 1-7, EMA
tammilehto_2022_emotion_regulation reappraisal, rumination, suppression
                                   since the previous beep, one item each,
                                   1-5, EMA
tammilehto_2022_ecr_r              Experiences in Close Relationships-
                                   Revised, 18 anxiety + 18 avoidance items,
                                   1-7, once
tammilehto_2022_ipip_neuroticism   IPIP-NEO neuroticism, 9 of its 10 items
                                   (one was dropped by a technical error),
                                   1-5, once

Coding notes
------------
* The openESM EMA values equal the authors' AT_ER_MPLUS.dat column for
  column, and its time_elapsed equals Basic_data's `aika` (asserted).
* `wave` (EMA tables) is DTIME, the 1-h-43-min block in which the beep was
  sent: 1-92 over the week, a fixed grid, so the gaps include nights. No
  calendar date or clock time is in the deposit, so there is no `date`.
* 4,637 answered beeps (matching the paper); 8 have only the attachment
  items and 10 only the ER items, and each table keeps what was answered.
* Items with an R suffix (AVO_1R, ANX_9R, NEUR_5R, ...) are stored reverse-
  scored by the authors: the shipped trait means are the plain means of the
  columns as given (asserted). resp is as shipped; the item names keep the
  suffix so the direction is visible.
* Covariates (per person, from Basic_data.txt): cov_sex (female/male),
  cov_age, cov_student (university / open university / other student /
  not a student).

Not shipped
-----------
SES1P, SES2P   financial strain, already rescaled to 0-1 by the authors.
TRAIT_*, SES, SECURITY/ANXIETY/AVOIDANCE, LAG_*   composites.
reagointi, aika, aika2   reaction time and hours since the study began.
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

REC = "22953122"
TS_FILE = "0054_tammilehto_ts.tsv"
OSF_BASIC = "https://osf.io/download/4jc9h/"    # e8423 Basic_data.txt
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

AGREE7 = {1: "Strongly disagree", 7: "Strongly agree"}
MUCH5 = {1: "Not at all", 5: "Very much"}
EMA = {
    "tammilehto_2022_state_attachment": dict(
        instrument="State Adult Attachment Measure (SAAM), 6 items",
        scale=range(1, 8), anchors=AGREE7, items=[
            ("feel_loved", "I feel loved"),
            ("rely_on", "I feel like I have someone to rely on"),
            ("need_love",
             "I feel a strong need to be unconditionally loved right now"),
            ("share_feelings", "I want to share my feelings with someone"),
            ("keep_distance", "If someone tried to get close to me, I would "
             "try to keep my distance"),
            ("closeness_nervous", "The idea of being emotionally close to "
             "someone makes me nervous"),
        ]),
    "tammilehto_2022_emotion_regulation": dict(
        instrument="Emotion regulation strategies, one item each "
                   "(after Heiy & Cheavens, 2014)",
        scale=range(1, 6), anchors=MUCH5, items=[
            ("reappraisal",
             "I thought about the situation in a more positive way"),
            ("rumination", "I thought over and over again about the negative "
             "situation and my feelings"),
            ("suppression",
             "I avoided showing my situation-elicited negative feelings"),
        ]),
}
TRAIT = {
    "tammilehto_2022_ecr_r": (("AVO_", "ANX_"), range(1, 8)),
    "tammilehto_2022_ipip_neuroticism": (("NEUR_",), range(1, 6)),
}

SEX = {0: "female", 1: "male"}
STUDENT = {1: "university student", 2: "open university student",
           3: "other student", 4: "not a student"}


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
    basic = pd.read_csv(fetch(OSF_BASIC, "/tmp/osf_e8423_Basic_data.txt"),
                        sep="\t")
    return ts, basic


def write_items(table, spec):
    rows = []
    for col, text in spec["items"]:
        for v in spec["scale"]:
            rows.append([table, f"{table}_1", col, spec["instrument"],
                         "Finnish", "", "", "", "", text, "", "",
                         spec["anchors"].get(v, ""), "", v])
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


def finish(table, long, covs, scale):
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(scale[0], scale[-1]).all(), table
    keys = ["id", "item"] + (["wave"] if "wave" in long else [])
    long = long[["id", "item", "resp"] + keys[2:] + covs]
    long = long.sort_values(keys).reset_index(drop=True)
    assert not long.duplicated(keys).any()
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, (table, [(c.name, c.detail) for c in bad])
    path = os.path.join(OUTDIR, f"{table}.csv")
    long.to_csv(path, index=False)
    print(f"{path}: {long['id'].nunique()} people x "
          f"{long['item'].nunique()} items = {len(long):,} responses")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df, basic = load()
    assert len(df) == len(basic) == 11224 and df["id"].nunique() == 122
    assert (df["id"].values == basic["KANDI_ID"].values).all()
    assert (df["discrete_time"].values == basic["DTIME"].values).all()
    assert not df.duplicated(["id", "discrete_time"]).any()
    seen = df["time_elapsed"].notna()
    assert np.allclose(df.loc[seen, "time_elapsed"], basic.loc[seen, "aika"])

    ema_cols = [c for s in EMA.values() for c, _ in s["items"]]
    assert df[ema_cols].notna().any(axis=1).sum() == 4637

    p = basic.groupby("KANDI_ID").first()
    trait_cols = [c for c in basic.columns
                  if c.startswith(("AVO_", "ANX_", "NEUR_"))]
    for c in trait_cols + ["SEX", "AGE", "opiskelu"]:
        assert (basic.groupby("KANDI_ID")[c].nunique() == 1).all(), c
    for prefix, total in (("AVO_", "TRAIT_AVOIDANCE"),
                          ("ANX_", "TRAIT_ANXIETY"),
                          ("NEUR_", "TRAIT_NEUROTICISM")):
        cols = [c for c in trait_cols if c.startswith(prefix)]
        assert np.allclose(p[cols].mean(axis=1), p[total]), prefix
    assert len(p) == 122 and p[trait_cols].notna().all().all()

    cov = pd.DataFrame({"id": p.index,
                        "cov_sex": p["SEX"].map(SEX).values,
                        "cov_age": p["AGE"].astype(int).values,
                        "cov_student": p["opiskelu"].map(STUDENT).values})
    covs = [c for c in cov.columns if c != "id"]
    assert cov[covs].notna().all().all()
    assert (cov["cov_sex"] == "female").sum() == 108

    df = df.rename(columns={"discrete_time": "wave"})
    for table, spec in EMA.items():
        tcols = [c for c, _ in spec["items"]]
        long = df.melt(id_vars=["id", "wave"], value_vars=tcols,
                       var_name="item", value_name="resp").dropna(
                           subset=["resp"])
        long = long.merge(cov, on="id", how="left", validate="m:1")
        finish(table, long, covs, spec["scale"])
        ipath, k = write_items(table, spec)
        print(f"  {ipath}: {k} item text rows")

    wide = p[trait_cols].rename_axis("id").reset_index()
    for table, (prefixes, scale) in TRAIT.items():
        tcols = [c for c in trait_cols if c.startswith(prefixes)]
        long = wide.melt(id_vars="id", value_vars=tcols, var_name="item",
                         value_name="resp")
        long = long.merge(cov, on="id", how="left", validate="m:1")
        finish(table, long, covs, scale)


if __name__ == "__main__":
    main()
