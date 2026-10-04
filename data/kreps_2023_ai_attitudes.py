#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/EOYDJR
# DOI: 10.1371/journal.pone.0288109
#   Kreps, S., George, J., Lushenko, P., & Rao, A. (2023). "Exploring the
#   artificial intelligence 'Trust paradox': Evidence from a survey
#   experiment in the United States." PLOS ONE, 18(7), e0288109.
#   (PMC10353804; CC BY 4.0.)
#   Dataset: Kreps, S., George, J., Lushenko, P., & Rao, A. (2023).
#   Replication Data for: Exploring the Artificial Intelligence "Trust
#   Paradox". Harvard Dataverse.
# Data: Dataverse datafile 7213122, "MasterData2 (2).csv" (format=original;
#       the raw Qualtrics export: 2 header rows + 1,008 completed responses x
#       104 columns; Lucid quota sample of US adults, October 7-21, 2022).
#       The deposit's Datav3.csv is the same file cut down to the 21 survey
#       questions for one respondent fewer (the one with Q6 missing); the
#       master file is used because it carries the item stems and age.
# License: CC0 1.0 (Dataverse dataset licence).
#
# What ships: the paper's second experiment (a 3 x 2 between-subjects design
# plus a control). Each respondent read one vignette -- control (generic AI),
# or cars / social-media content moderation / armed drones x AI that
# enhances / substitutes for human judgment -- and answered ten items about
# it: support (Q7), trust (Q8), self-assessed understanding (Q9) and seven
# mechanism statements (Q12-Q18: fear of missing out, risk-benefit
# calculation, substitution, optimism about safety, opt-out, transparency,
# acceptance). `treat` is 1 for any of the six treatment vignettes and 0 for
# the control ("Control Scenario"). Which vignette is cov_domain x
# cov_purpose: the replication code (Tables 4A-4C kit) maps the deposit's
# "Scenario #k, Treatment" to T1 Cars/Enhance, T2 Cars/Substitute, T3
# Online/Enhance, T4 Online/Substitute, T5 Drones/Enhance, T6
# Drones/Substitute (cov_domain/cov_purpose = "none" for the control).
# Response range: the paper's Methods give support and trust, and the
# mechanism statements, "a 5-point Likert scale ... 1 corresponds to
# 'strongly disagree' and 5 to 'strongly agree'", so {1..5} is asserted for
# Q7, Q8 and Q12-Q18. Q9 (understanding) uses the same "To what extent do you
# agree" stem but the paper states no scale for it, so no permitted set is
# asserted for Q9 (its observed values are whole numbers 1-5).
#
# Not shipped: the first experiment, a conjoint (conjoint_dv_k_1/2 with the
# F-* attribute columns): every respondent rated randomly generated
# profiles, so the same column is a different stimulus for every person.
#
# Item text: shipped (itemtext_output/kreps_2023_ai_attitudes__items.csv).
#   The stems are the Qualtrics question text in the file's first header row
#   (keyed by column name); there are no value labels in a CSV, so the
#   option text is the paper's endpoint labels and the unlabelled midpoints
#   are left blank. English, administered in English (UserLanguage = EN).
#
# PII check: Recipient name/email, IP address, latitude/longitude and
#   ExternalReference are all masked ("*******") in the source. The free-text
#   answers (Q10, Q11: what respondents considered) were read and hold
#   opinions about AI only. The file also has a 5-digit ZIP code and US
#   state; neither is carried (ZIP is a quasi-identifier, cf. the talayero
#   postal code, batch 3).
# id: row index. ResponseId and rid (Qualtrics / Lucid respondent ids) are
#   not carried.
# Covariates: cov_age (Lucid-supplied age in years), cov_domain, cov_purpose.
#   The other demographics (Q1-Q4, Q19-Q23 and Lucid's gender/hhi/ethnicity/
#   education/party/region) are numeric codes with no codebook in the
#   deposit and are not carried.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://dataverse.harvard.edu/api/access/datafile/7213122"
       "?format=original")

TABLE = "kreps_2023_ai_attitudes"
ITEMS = ["Q7", "Q8", "Q9", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18"]
DOCUMENTED = [i for i in ITEMS if i != "Q9"]
ARMS = {"Control Scenario": (0, "none", "none"),
        "Scenario #1, Treatment": (1, "cars", "enhance"),
        "Scenario #2, Treatment": (2, "cars", "substitute"),
        "Scenario #3, Treatment": (3, "social_media", "enhance"),
        "Scenario #4, Treatment": (4, "social_media", "substitute"),
        "Scenario #5, Treatment": (5, "drones", "enhance"),
        "Scenario #6, Treatment": (6, "drones", "substitute")}
MASKED = ["IPAddress", "RecipientLastName", "RecipientFirstName",
          "RecipientEmail", "ExternalReference", "LocationLatitude",
          "LocationLongitude"]


def load():
    r = requests.get(URL, headers=UA, timeout=180)
    r.raise_for_status()
    raw = pd.read_csv(io.BytesIO(r.content), dtype=str, keep_default_na=False)
    stems = raw.iloc[0]
    return raw.iloc[2:].reset_index(drop=True), stems


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, stems = load()
    assert d.shape == (1008, 104), d.shape
    assert (d["Finished"] == "1").all()
    assert d["ResponseId"].is_unique
    for c in MASKED:
        assert set(d[c]) == {"*******"}, c
    assert set(d["Respondent Group"]) == set(ARMS)
    assert not d.drop(columns=["ResponseId", "rid"]).duplicated().any()

    d.insert(0, "id", range(1, len(d) + 1))
    arm = d["Respondent Group"].map(ARMS)
    d["treat"] = (arm.str[0] > 0).astype(int)
    d["cov_domain"] = arm.str[1]
    d["cov_purpose"] = arm.str[2]
    d["cov_age"] = pd.to_numeric(d["age"])
    assert d["cov_age"].between(18, 100).all()
    covs = ["treat", "cov_age", "cov_domain", "cov_purpose"]

    long = d.melt(id_vars=["id"] + covs, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long[long["resp"] != ""].copy()
    long["resp"] = pd.to_numeric(long["resp"])
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = set(range(1, 6))
    for it, g in long.groupby("item"):
        if it in DOCUMENTED:
            bad = set(g["resp"]) - allowed
            assert not bad, (it, bad)
    pv = {i: allowed for i in DOCUMENTED}
    long = long[["id", "item", "resp"] + covs]
    long["cov_age"] = long["cov_age"].astype(int)
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(ITEMS)
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
    write_itemtext(stems)


def write_itemtext(stems):
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for it in ITEMS:
        stem = " ".join(stems[it].split())
        for k in range(1, 6):
            opt = {1: "Strongly disagree", 5: "Strongly agree"}.get(k, "")
            rows.append({
                "table": TABLE, "section_id": f"{TABLE}_1", "item": it,
                "instrument": "AI trust paradox survey experiment, second "
                              "experiment (Kreps, George, Lushenko & Rao "
                              "2023)",
                "instructions": "", "section_prompt": "",
                "item_text": stem, "correct_response": "",
                "option_text": opt, "resp": k})
    pd.DataFrame(rows).to_csv(TEXT_DIR / f"{TABLE}__items.csv", index=False)


if __name__ == "__main__":
    convert()
