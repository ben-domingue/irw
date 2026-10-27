"""baumann_2023_distractions, baumann_2023_satisfaction, baumann_2023_strategy.

Source: Baumann, J., Danilov, A., & Stavrova, O. (2023). Self-control and
performance while working from home. PLOS ONE, 18(3), e0282862,
doi:10.1371/journal.pone.0282862.
Data: OSF node ur2km, selfcontrol_wfh_data_final_long_3t.csv, with the
deposit's Codebook.xlsx for the response formats (both pinned by sha256).

Licence: the OSF node carries CC BY Attribution 4.0 International. The article
is separately CC BY 4.0, but the deposit is what governs the data.

262 employees recruited on Prolific, surveyed in three waves and randomly
assigned at wave 1 to one of four self-control strategy conditions (situation
modification, goal reminder, give in later, control). The file is long over
waves, 262 x 3 = 786 rows, with the wave-specific values also held in
wave-suffixed columns that are constant within a person.

What is NOT shippable: every published instrument in this study is deposited
only as a scale score, never as items -- the Brief Self-Control Scale
(SCS_score_1), intrinsic work motivation (IWM_score), perceived organizational
support (PEO_score), the depression scale (dep_score), all five Big Five
scores and the performance measure (prod_score) are averages on 1-5, as the
deposit's own codebook states. Nothing item-level survives for them.

What ships is the three item-level batteries the codebook does describe, with
each item carrying the deposit's wave suffix so the repeated administration is
explicit:

- baumann_2023_distractions  31 items, 1-5. "How distracting is X while
  working from home", 13 sources at wave 1 (colleagues, children, partner,
  housemate, pets, social media, messages, news, noise, mind wandering,
  worries, chores, doorbell) and the same 13 plus smartphone, TV, shopping,
  games and ads at wave 3. These are the components the deposit averages into
  distr_score.
- baumann_2023_satisfaction  27 items, 0-10. Nine satisfaction domains (life,
  health, sleep, job, income, free time, WFH, chores, childcare) at each of
  the three waves. sat_child is missing for respondents without children,
  which is the bulk of the 677 missing cells.
- baumann_2023_strategy      12 items, 1-5. Six self-control strategy-use
  reports (removed distractions, reminded of goals, gave in later, recalled
  why distraction was bad, used willpower, gave in) at waves 2 and 3.

sat_work_org_3 is excluded: the codebook puts it on 0-5, not 0-10, and it was
asked once, so including it would mix response formats in the table. The four
treatment dummies, the attention checks and the assigned-strategy follow-ups
are experimental design and manipulation-check columns, not responses.

Mapping
- id          = respondent index 1..262 over PROLIFIC_PID sorted. Neither
                PROLIFIC_PID nor ResponseId is shipped: a Prolific ID is a
                stable identifier for a real person across studies.
- item        = the deposit's column name, wave suffix included
- cov_age     = age, years
- cov_sex     = screen_sex, assigned sex at birth, 0 = male, 1 = female
- cov_educ    = educ, the deposit's education code
- cov_income  = income, the deposit's pre-tax personal income band
- cov_children = children_1, number of children at wave 1

Item text: the deposit's codebook gives a one-line description of each item
rather than its administered wording, so no item text is shipped.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

URL = "https://osf.io/download/egc59/"
SHA256 = "24faf72444a59c18aca2620a9fd7215cc61fca5248c241ef40f6617221a25bb2"
CACHE = Path.home() / ".cache" / "irw-plos" / "baumann_2023_long3t.csv"

if not CACHE.exists():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    CACHE.write_bytes(urllib.request.urlopen(req).read())
assert hashlib.sha256(CACHE.read_bytes()).hexdigest() == SHA256

d = pd.read_csv(CACHE, low_memory=False)
assert d.shape == (786, 166)
assert d["PROLIFIC_PID"].nunique() == 262
assert (d["PROLIFIC_PID"].value_counts() == 3).all()

DISTR = ([f"distr_{s}_1" for s in ("coll", "child", "partner", "housemate", "pet",
                                   "social", "messages", "news", "noise", "mind",
                                   "worries", "chores", "bell")]
         + [f"distr_{s}_3" for s in ("coll", "child", "partner", "housemate", "pet",
                                     "social", "messages", "news", "noise", "mind",
                                     "worries", "chores", "bell", "smartphone",
                                     "tv", "shopping", "games", "ads")])
SAT_DOMAINS = ("life", "health", "sleep", "job", "income", "free", "wfh", "chores", "child")
SAT = [f"sat_{s}_{w}" for w in (1, 2, 3) for s in SAT_DOMAINS]
STRAT = [f"strategy_use_{s}_{w}" for w in (2, 3)
         for s in ("distr", "goal", "later", "bad", "will", "givein")]
assert (len(DISTR), len(SAT), len(STRAT)) == (31, 27, 12)

## the wave-suffixed columns are person-level: one value per respondent
cols = DISTR + SAT + STRAT
assert (d.groupby("PROLIFIC_PID")[cols].nunique(dropna=False).max() <= 1).all().all()

COVS = {"age": "cov_age", "screen_sex": "cov_sex", "educ": "cov_educ",
        "income": "cov_income", "children_1": "cov_children"}
w = (d.sort_values(["PROLIFIC_PID", "t"])
      .groupby("PROLIFIC_PID", as_index=False)
      .first()
      .sort_values("PROLIFIC_PID", kind="stable")
      .reset_index(drop=True))
w = w.rename(columns=COVS)
covs = list(COVS.values())
w.insert(0, "id", range(1, len(w) + 1))
assert len(w) == 262

SCALES = {
    "baumann_2023_distractions": (DISTR, {1, 2, 3, 4, 5}),
    "baumann_2023_satisfaction": (SAT, set(range(0, 11))),
    "baumann_2023_strategy": (STRAT, {1, 2, 3, 4, 5}),
}
for table, (items, ok) in SCALES.items():
    df = w.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    df = df.dropna(subset=["resp"])
    df["resp"] = df["resp"].astype(int)
    permitted = {i: ok for i in items}
    assert all(df.loc[df["item"] == i, "resp"].isin(v).all() for i, v in permitted.items()), table
    df = df[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")

    checks = run_qc(df, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    df.to_csv(f"{table}.csv", index=False)
    print(f"{table}: rows={len(df)} ids={df['id'].nunique()} items={df['item'].nunique()}")
