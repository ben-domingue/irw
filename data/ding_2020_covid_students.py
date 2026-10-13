"""ding_2020_covid_knowledge and ding_2020_covid_risk_perception.

Source: Ding, Y., Du, X., Li, Q., Zhang, M., Zhang, Q., Tan, X., & Liu, Q.
(2020). Risk perception of coronavirus disease 2019 (COVID-19) and its
related factors among college students in China during quarantine. PLOS
ONE, 15(8), e0237626, doi:10.1371/journal.pone.0237626.
Data: Supporting Information S1 Data, journal.pone.0237626.s003 (.xls,
pinned by sha256). S1 File is the questionnaire in Chinese, S2 File the
authors' English version. Licence: the article is CC BY 4.0, which covers
its SI.

1,461 Chinese college students, online survey (WeChat/QQ), 4-7 February
2020, during home quarantine. Questionnaire written by the authors.

Tables
- ding_2020_covid_knowledge  24 binary items, scored 1 = correct, 0 = not,
    from Part three "Knowledge of COVID-19". The deposit records every
    option of each tick-all-that-apply question as its own 0/1 column, so
    each option is an item (Q10A..Q10E transmission routes, Q12A..Q12F
    symptoms, Q13A..Q13I preventive measures, Q16A..Q16C incubation period)
    and Q11 (susceptible population, single choice 1-6) is one item. The
    key is the questionnaire's own (S1/S2 File): Q10 A,B; Q11 option 5 (E);
    Q12 A-E; Q13 A,B,C,D,E,H,I; Q16 A,B. An option item scores 1 when the
    respondent's tick matches the key (keyed-correct option ticked, or
    distractor left unticked). resp_raw holds the tick (1/0) and, for Q11,
    the option chosen (1-6).
    Not shipped from this part: Q14 and Q15 (self-rated knowledge of hand
    washing and mask wearing, 1-5, not knowledge items; the paper scores
    them 1-3 points).
- ding_2020_covid_risk_perception  Q17..Q20, Part four "Risk Perception",
    1-5 (1 = not at all .. 5 = very likely / very worried), as deposited.

Mapping (column headers checked in the script, not positions)
- id                 = ID (unique, 1..1461)
- cov_gender         = "1.Gender", 1 male, 2 female (S2 File)
- cov_age            = "2.Age", years
- cov_grade          = "5.Grade", 1-4 undergraduate years 1-4, 5 fifth year,
                       6-8 master's years 1-3, 9-11 doctoral years 1-3
- cov_major          = "6.Major", 1 liberal arts, 2 science, 3 engineering,
                       4 agriculture, 5 medicine, 6 art
- cov_parent_health  = Q9 parents' general health, 1 healthy .. 4 very poor
- cov_known_case     = 1 if Q7 ticks any of A-D (self, family, friend or
                       acquaintance diagnosed), else 0
- cov_known_contact  = same for Q8 (contact with a confirmed or suspected case)
- cov_school_hubei, cov_home_hubei = 1 if the free-text school / home
                       location (province-city) starts with 湖北 (Hubei),
                       else 0. The free text itself is not shipped.

Item text: shipped for both tables -- the questionnaire is in the deposit
(S1 File, Chinese, administered; S2 File, the authors' English). Built by
automated_finding/itemtext_verification/make_itemtext_ding_2020.py.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0237626.s003")
SHA256 = "81b0150adfb81dcd6a3d287308e7b991ce1625a8a4272164c08d8b3d15a865e7"
CACHE = Path.home() / ".cache" / "irw-plos" / "ding_2020.xls"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

raw = pd.read_excel(CACHE, header=None)
top = raw.iloc[0].ffill().astype(str).str.strip()
sub = raw.iloc[1].fillna("").astype(str).str.strip()
# Code = question number from the top header (+ option letter from the second row).
qnum = top.str.extract(r"^(\d+)\.")[0]
codes = []
for t, s, q in zip(top, sub, qnum):
    if t == "ID":
        codes.append("ID")
    elif t == "risk perception":
        codes.append("Q" + s.split(".")[0])
    elif s:
        codes.append(f"Q{q}{s}")
    else:
        codes.append(f"Q{q}")
w = raw.iloc[2:].copy()
w.columns = codes
assert len(w) == 1461 and w["ID"].is_unique
# Guard the header-derived codes against the labels they came from.
labels = dict(zip(codes, top))
assert labels["Q10A"].startswith("10.Transmission") and labels["Q11"].startswith("11.Susceptible")
assert labels["Q12A"].startswith("12.Symptoms") and labels["Q13I"].startswith("13.Preventive")
assert labels["Q16C"].startswith("16.Incubation") and labels["Q17"] == "risk perception"
assert labels["Q7A"].startswith("7.") and labels["Q8E"].startswith("8.") and labels["Q9"].startswith("9.")
assert labels["Q3"].startswith("3.School") and labels["Q4"].startswith("4.H")

w = w.rename(columns={"ID": "id", "Q1": "cov_gender", "Q2": "cov_age", "Q5": "cov_grade",
                      "Q6": "cov_major", "Q9": "cov_parent_health"})
for c in ["id", "cov_gender", "cov_age", "cov_grade", "cov_major", "cov_parent_health"]:
    w[c] = w[c].astype(int)
assert set(w["cov_gender"]) == {1, 2} and w["cov_age"].between(15, 40).all()
w["cov_known_case"] = (w[[f"Q7{x}" for x in "ABCD"]].astype(int).sum(axis=1) > 0).astype(int)
w["cov_known_contact"] = (w[[f"Q8{x}" for x in "ABCD"]].astype(int).sum(axis=1) > 0).astype(int)
w["cov_school_hubei"] = w["Q3"].astype(str).str.startswith("湖北").astype(int)
w["cov_home_hubei"] = w["Q4"].astype(str).str.startswith("湖北").astype(int)
covs = ["cov_gender", "cov_age", "cov_grade", "cov_major", "cov_parent_health",
        "cov_known_case", "cov_known_contact", "cov_school_hubei", "cov_home_hubei"]

# --- knowledge: option items scored against the questionnaire's key -------
KEY = {"Q10": "AB", "Q12": "ABCDE", "Q13": "ABCDEHI", "Q16": "AB"}
OPTS = {"Q10": "ABCDE", "Q12": "ABCDEF", "Q13": "ABCDEFGHI", "Q16": "ABC"}
opt_items = [f"{q}{o}" for q in OPTS for o in OPTS[q]]
know = w[["id"] + covs].copy()
for it in opt_items:
    tick = w[it].astype(int)
    assert set(tick) <= {0, 1}
    keyed = it[-1] in KEY[it[:-1]]
    know[it] = (tick == int(keyed)).astype(int)
    know[it + "__raw"] = tick
q11 = w["Q11"].astype(int)
assert q11.between(1, 6).all()
know["Q11"] = (q11 == 5).astype(int)
know["Q11__raw"] = q11
items = opt_items + ["Q11"]
long = know.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
rawl = know.melt(id_vars=["id"], value_vars=[i + "__raw" for i in items], var_name="item", value_name="resp_raw")
rawl["item"] = rawl["item"].str.replace("__raw", "", regex=False)
df = long.merge(rawl, on=["id", "item"], validate="one_to_one")
df = df[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"], kind="stable")
checks = run_qc(df, permitted_values={i: {0, 1} for i in items})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
print("knowledge warns:", [(c.name, c.detail[:80]) for c in checks if c.status == "warn"])
df.to_csv("ding_2020_covid_knowledge.csv", index=False)
print(f"ding_2020_covid_knowledge: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")

# --- risk perception -------------------------------------------------------
rp = ["Q17", "Q18", "Q19", "Q20"]
df = w.melt(id_vars=["id"] + covs, value_vars=rp, var_name="item", value_name="resp")
df["resp"] = df["resp"].astype(int)
assert df["resp"].between(1, 5).all()
df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")
checks = run_qc(df, permitted_values={i: {1, 2, 3, 4, 5} for i in rp})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
print("risk warns:", [(c.name, c.detail[:80]) for c in checks if c.status == "warn"])
df.to_csv("ding_2020_covid_risk_perception.csv", index=False)
print(f"ding_2020_covid_risk_perception: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
