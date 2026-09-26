#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11214741
# DOI: 10.7717/peerj.17522
#   "Factors associated with poor sleep quality among dental students in
#   Malaysia" (Jie, Mohamad, Mohd Adnan, Mohd Nor, Abdul Hamid & Abllah, 2024),
#   PeerJ 12:e17522.
# Data: Supplemental File peerj-12-17522-s003.sav (384 x 96), fetched from the
#       Europe PMC supplementaryFiles zip. The other supplements are the
#       questionnaire (s001.docx, Malay) and the STROBE checklist (s002.docx).
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: available, not shipped here -- the .sav variable labels carry
#   English stems for items 6/7 and the value labels give the anchors
#   (0 "Not during the past month" ... 3 "Three or more times a week"; item 6
#   0 "Very good" ... 3 "Very bad"); the recoded new_d5a-j/new_d8/new_d9
#   columns carry no variable labels. The administered Malay wording (PSQI-M)
#   is in s001.docx, Bahagian D. The English PSQI is Buysse et al. (1989).
#
# Table: jie_2024_psqi -- the 14 frequency/rating items of the Pittsburgh Sleep
#   Quality Index (Malay version), all 0-3:
#     psqi_5a..psqi_5j  "during the past month, how often have you had trouble
#                        sleeping because you ..." (5a cannot get to sleep
#                        within 30 min ... 5j other reasons)
#     psqi_6            subjective sleep quality
#     psqi_7            sleep medication frequency
#     psqi_8            trouble staying awake frequency
#     psqi_9            problem keeping up enthusiasm
#   The open-response items 1-4 (bed time, minutes to fall asleep, rise time,
#   hours slept) are clock times/quantities, not ordinal responses, and are
#   skipped along with every component/total score derived from them.
#   Checks: psqi_6 == PSQI_SlpQual, psqi_7 == PSQI_Meds and psqi_8 + psqi_9 ==
#   d8_d9_Daytime for every row, so the "new_" columns are the scored items,
#   not a transformation of them.
# No missing cells, all integers. 26 respondents share an item pattern with
#   another respondent (floor patterns, e.g. all zeros); no two rows agree on
#   all 96 columns, so this is low-variance responding, not duplication.
# No PII: age, gender, ethnicity, institution only; no names or contact data.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11214741/"
           "supplementaryFiles")
FNAME = "peerj-12-17522-s003.sav"
TABLE = "jie_2024_psqi"

ITEMS = {**{f"new_d5{x}": f"psqi_5{x}" for x in "abcdefghij"},
         "d6": "psqi_6", "d7": "psqi_7", "new_d8": "psqi_8", "new_d9": "psqi_9"}
COVS = {"a1": "cov_age", "a2": "cov_academic_year", "a3": "cov_gender",
        "a4": "cov_ethnicity", "a6": "cov_marital_status",
        "a8_study_place": "cov_university", "a9_accomodation": "cov_residence"}

SKIP = {
    **{c: "dichotomised/recoded copy of a covariate"
       for c in ["new_age", "new_academic", "new_ethnic",
                 "new_a5_cat_parents_income", "new_BMI_group"]},
    "a5.1": "parents' income category (financial detail, not needed)",
    "a5.2": "parents' income amount (financial detail, not needed)",
    **{c: "anthropometrics / derived BMI, not a questionnaire response"
       for c in ["a7.1", "a7.2", "a7.2_in_meter", "a7_BMI"]},
    "a10.1_med_prob": "health-history yes/no, single item",
    **{c: "lifestyle single item (Section B), not part of a scale"
       for c in ["b1", "b2", "b3", "b4", "b5", "b6.1", "new_b6.1_Smoking",
                 "b7", "new_b7_Alcohol", "b8", "new_b8_Caffeinated_drink",
                 "new_freq_drink"]},
    **{c: "academic-performance single item / GPA (Section C), not a scale"
       for c in ["c1", "new_aca_performance", "c2", "c3", "new_fallen_asleep",
                 "c4_skip_class", "c6_come_late", "c8", "new_freq_kok"]},
    "d1": "PSQI item 1, bed time (clock time, not an ordinal response)",
    "d2_new": "PSQI item 2 minutes-to-sleep binned by the authors (derived)",
    "new_d2": "copy of d2_new",
    "d3": "PSQI item 3, rise time (clock time)",
    "newtib_hours": "derived time in bed",
    "d4_hours": "PSQI item 4, hours of sleep (quantity, not ordinal)",
    "tmphse": "derived sleep efficiency percentage",
    "score5b_5j": "sum score", "Q5_new": "sum score",
    "d8_d9_Daytime": "sum score",
    "d10": "PSQI item 10 roommate/bed-partner status (not scored)",
    **{f"d11{x}": "PSQI item 10a-e, reported by the roommate/bed partner "
                  "(not scored; a different informant)" for x in "abcde"},
    **{c: "PSQI component score"
       for c in ["PSQI_Durati", "New_PSQI_Duration", "PSQI_Distub",
                 "new_PSQI_Disturb", "PSQI_Laten", "d2_d5a_PSQI_Laten",
                 "new_PSQI_Laten", "PSQI_Daydys", "new_PSQI_Daydys",
                 "PSQI_Hse", "new_PSQI_Hse", "PSQI_SlpQual", "PSQI_Meds"]},
    **{c: "PSQI global score / good-poor classification"
       for c in ["PSQI_Total", "new_PSQI_Total", "PSQI_Quality_cat",
                 "new_PSQI_quality_cat", "newMLR_PSQI_outcome"]},
    **{f"PRE_{i}": "model-predicted probability" for i in range(1, 9)},
}


def load() -> pd.DataFrame:
    r = requests.get(ZIP_URL, headers=UA, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        blob = z.read(FNAME)
    with tempfile.NamedTemporaryFile(suffix=".sav") as tf:
        tf.write(blob)
        tf.flush()
        d, _ = pyreadstat.read_sav(tf.name)
    return d


def convert() -> None:
    d = load()
    assert d.shape == (384, 96), d.shape

    # ---- books ---------------------------------------------------------
    acc = set(ITEMS) | set(COVS) | set(SKIP)
    assert set(d.columns) == acc and len(d.columns) == len(acc), \
        set(d.columns) ^ acc
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")

    # the new_ columns are the scored items (see header)
    assert (d["d6"] == d["PSQI_SlpQual"]).all()
    assert (d["d7"] == d["PSQI_Meds"]).all()
    assert (d["new_d8"] + d["new_d9"] == d["d8_d9_Daytime"]).all()
    assert not d.duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={**ITEMS, **COVS})
    cov_cols = list(COVS.values())
    items = list(ITEMS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                  var_name="item", value_name="resp")
    assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for c in cov_cols:
        long[c] = long[c].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100

    pv = {i: {0, 1, 2, 3} for i in items}
    assert not set(long["resp"]) - {0, 1, 2, 3}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
