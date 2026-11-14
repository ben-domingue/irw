#!/usr/bin/env python3
# Source: https://zenodo.org/records/10672568
# DOI: 10.5281/zenodo.10672568 (data)
#   Mitchell A, Oberman T, Aletta F, Erfanian M, Kachlicka M, Lionello M, Fang X et al. (2024).
#   The International Soundscape Database: An integrated multimedia database of urban soundscape
#   surveys -- questionnaires with acoustical and contextual information (v1.0) [Data set]. Zenodo.
#   Protocol paper: Mitchell et al. (2020), Applied Sciences 10(7), 2397, 10.3390/app10072397.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: ISD v1.0 Data.csv, 3,589 in-situ soundscape questionnaires (SSID Protocol, after ISO/TS
#   12913-2) from 26 locations across Europe and China, each matched to a binaural recording. One
#   row = one participant's questionnaire; there is no participant id, so id = row order.
#
# Tables (item = the database's column name):
#   mitchell_2024_isd_paq           -- the eight ISO 12913-2 perceived affective quality attributes
#     (pleasant, chaotic, vibrant, uneventful, calm, annoying, eventful, monotonous), 1-5 agreement.
#   mitchell_2024_isd_sound_sources -- ssi01-ssi04, how much the participant heard traffic noise,
#     other noise, human sounds and natural sounds, 1-5.
#   mitchell_2024_isd_who5          -- who01-who05, WHO-5 Well-Being Index items, 0-5.
# Not shipped: sss01-sss05 (five single questions with different response scales: overall quality,
#   appropriateness, loudness, visit frequency, return intention), and all acoustic indices.
# Covariates: cov_location (LocationID, the survey site), cov_survey_version (language + protocol
#   version), cov_age (age00, as recorded), cov_gender (gen00 where recorded as a word; the two
#   Chinese versions store 1/2 with no key in the deposit, left missing rather than guessed).
# Not carried: latitude/longitude (the survey point), start/end times, free-text fields
#   (eth00_other, occ00_other, misc01, misc03_other).
# Item text: not shipped -- column names only; the wording is ISO/TS 12913-2's (and WHO-5), set out in
#   the SSID protocol paper, not in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/10672568/files/ISD%20v1.0%20Data.csv/content"
BLOCKS = {
    "mitchell_2024_isd_paq": (["pleasant", "chaotic", "vibrant", "uneventful", "calm", "annoying", "eventful",
                               "monotonous"], (1, 5)),
    "mitchell_2024_isd_sound_sources": (["ssi01", "ssi02", "ssi03", "ssi04"], (1, 5)),
    "mitchell_2024_isd_who5": (["who01", "who02", "who03", "who04", "who05"], (0, 5)),
}


def main():
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), low_memory=False)
    d = d[["LocationID", "Survey_Version", "age00", "gen00"] + sum((v[0] for v in BLOCKS.values()), [])].copy()
    assert len(d) == 3589
    d["id"] = range(1, len(d) + 1)
    d["cov_location"] = d["LocationID"]
    d["cov_survey_version"] = d["Survey_Version"]
    d["cov_age"] = d["age00"]
    words = {"Female": "female", "Male": "male", "Non-conforming": "non-conforming", "RatherNotSay": "rather not say"}
    assert set(d["gen00"].dropna()) <= set(words) | {"1", "2"}
    d["cov_gender"] = d["gen00"].map(words)
    covs = ["cov_location", "cov_survey_version", "cov_age", "cov_gender"]
    for name, (items, (lo, hi)) in BLOCKS.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
