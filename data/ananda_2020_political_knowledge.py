#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/BTEIDE
# DOI: 10.7910/DVN/BTEIDE (data); paper 10.1093/ijpor/edaa012
#   Ananda A, Bol D (2020). Does knowing democracy affect answers to democratic support questions?
#   A survey experiment in Indonesia. International Journal of Public Opinion Research.
# License: CC0 1.0 (Harvard Dataverse)
# Data: main_survey.dta, an online survey of Indonesian adults (3,836 rows, incl. break-offs). The
#   .dta has non-UTF-8 bytes in some labels, so it is read as latin-1 and only the numeric columns
#   used here are loaded. The platform's name/e-mail/IP fields are empty in the file.
#
# Table: ananda_2020_political_knowledge -- the survey's 8 political-knowledge questions (Indonesian,
#   multiple choice). The authors do not score them (Knowing Democracy Replication.do never uses
#   q0015-q0019), so the key below is IRW's, set from public record, and it agrees with the modal
#   answer on every item:
#     q0015  party with the most DPR seats 2014-2019: PDI-P (q0015_0004)
#     q0016  Joko Widodo's office just before the presidency: Gubernur Jakarta (4)
#     q0017  what "RKP" is: Rencana Kerja Pemerintah (3)
#     q0018_1..4  party of Megawati Soekarnoputri (4 PDI-P), Susilo Bambang Yudhoyono (3 Partai
#       Demokrat), Aburizal Bakrie (1 Golkar), Hatta Rajasa (8 PAN)
#     q0019  court that hears presidential election disputes: Mahkamah Konstitusi (1)
#   resp = 1 correct, 0 incorrect or "Tidak tahu" (don't know). "Tidak ingin menjawab" (prefer not
#   to answer) and unanswered are not rows. q0015 was a tick-all checkbox list: correct = PDI-P
#   ticked and no other party; it is answered if anything was ticked. resp_raw = the option code
#   chosen (for q0015, the ticked code when exactly one box was ticked, else blank).
# Sample: Indonesian citizens only (q0002 = 1; 8 non-citizens dropped, as the authors do).
# id: row index (RespondentID is a survey-platform id).
# Covariates: cov_sex (q0003; "don't know"/"prefer not" -> NA), cov_age_band (q0004 labels; 9 ->
#   NA), cov_democracy_info (the experiment, asked BEFORE the quiz: q0011_question 2 = shown a list
#   of characteristics of democracy, 1 = not). City of residence (q0007) is not carried.
# Item text: not shipped -- Indonesian stems are in the .dta variable labels, options in the value
#   labels; the questions are study-authored but the key is IRW-derived, and that would need an
#   issues-page note first.
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/5014142?format=original"
Q15 = [f"q0015_{i:04d}" for i in range(1, 12)]  # 1-9 parties, 10 tidak tahu, 11 tidak ingin menjawab
# item -> (column, correct code, don't-know code, refuse code)
SINGLE = {
    "q0016": ("q0016", 4, 5, 6),
    "q0017": ("q0017", 3, 5, 6),
    "q0018_1": ("q0018_0001_0001", 4, 11, 12),
    "q0018_2": ("q0018_0002_0001", 3, 11, 12),
    "q0018_3": ("q0018_0003_0001", 1, 11, 12),
    "q0018_4": ("q0018_0004_0001", 8, 11, 12),
    "q0019": ("q0019", 1, 5, 6),
}
AGE = {1: "17-24", 2: "25-34", 3: "35-44", 4: "45-54", 5: "55-64", 6: "65-74", 7: "75+"}


def main():
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    cols = ["q0002", "q0003", "q0004", "q0011_question"] + Q15 + [c for c, *_ in SINGLE.values()]
    with tempfile.NamedTemporaryFile(suffix=".dta") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_dta(f.name, usecols=cols, encoding="latin1")
    assert len(d) == 3836
    d = d[d["q0002"] == 1].reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_sex"] = d["q0003"].map({1: "female", 2: "male"})
    d["cov_age_band"] = d["q0004"].map(AGE)
    d["cov_democracy_info"] = d["q0011_question"].map({1: 0, 2: 1})
    covs = ["cov_sex", "cov_age_band", "cov_democracy_info"]

    rows = []
    for item, (col, key, dk, refuse) in SINGLE.items():
        x = d[["id"] + covs].copy()
        x["item"], x["resp_raw"] = item, d[col]
        x = x[x["resp_raw"].notna() & (x["resp_raw"] != refuse)]
        assert x["resp_raw"].between(1, dk).all(), item
        x["resp"] = (x["resp_raw"] == key).astype(int)
        rows.append(x)
    ticks = d[Q15].notna()
    parties = ticks.iloc[:, :9]
    answered = ticks.any(axis=1) & ~(ticks["q0015_0011"] & ~ticks.iloc[:, :10].any(axis=1))
    x = d.loc[answered, ["id"] + covs].copy()
    x["item"] = "q0015"
    x["resp"] = (parties.loc[answered, "q0015_0004"] & (parties.loc[answered].sum(axis=1) == 1)).astype(int)
    one = ticks.loc[answered].sum(axis=1) == 1
    x["resp_raw"] = ticks.loc[answered].idxmax(axis=1).str[-2:].astype(int).where(one)
    rows.append(x)

    t = pd.concat(rows, ignore_index=True)
    assert not t.duplicated(["id", "item"]).any()
    t = t[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"])
    p = t.groupby("item")["resp"].mean().round(2)
    print(p.to_dict())
    assert (p > 0.5).all()  # the key agrees with the modal answer on every item
    gate(t)
    t.to_csv(OUT / "ananda_2020_political_knowledge.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
