#!/usr/bin/env python3
# Voter Autrement in situ voting experiments (French presidential elections
# 2007, 2012, 2017, 2022) -> 26 IRW core tables of approval and evaluative
# ballots, one row per participant x candidate.
#
# Source: the "Voter Autrement" programme (Baujard, Blanch, Bouveret, Delemazure,
#   Durand, Gavrel, Igersheim, Lang, Laruelle, Laslier, Lebon, Merlin). On the
#   day of the first round, voters leaving the official booth in selected
#   polling stations were invited to vote again, on paper, under one or two
#   alternative rules, then answer a short questionnaire. The candidates are
#   the official first-round candidates. PrefLib 00071 carries part of these
#   data; the tables here are rebuilt from the originators' own Zenodo deposits:
#   2007  doi:10.5281/zenodo.15007006 (concept 14990024), Baujard, Igersheim,
#         Delemazure, "Voter Autrement 2007 - Dataset of the In Situ
#         Experiments" (2025-03-11). ODbL 1.0. Files read: approval.csv,
#         scores.csv, voters.csv (the polling station). 2,836 participants in
#         Cigne, Illkirch-Graffenstaden (stations 3, 8, 10) and Louvigny
#         (stations 1, 2); every participant had both ballots.
#   2012  doi:10.5281/zenodo.17351816 (concept 15007144), Baujard, Igersheim,
#         Lebon, Gavrel, Delemazure, "Voter Autrement 2012 - Dataset of the In
#         Situ Experiments" (2025-10-14). ODbL 1.0. Files read, per city
#         (louvigny, saintetienne, strasbourg): <city>_approval.csv,
#         <city>_scores.csv, <city>_voters.csv, <city>_weights.csv.
#   2017  five per-city records by Laslier (2019-11-19), each CC BY 4.0 on
#         Zenodo: Allevard 10.5281/zenodo.3547607, Crolles 3547605, Grenoble
#         3547599, Herouville-Saint-Clair 3547593, Strasbourg 3547588; one
#         semicolon-separated file each (<City>Data_2017_Presid+.csv). The
#         codebook is the companion record 10.5281/zenodo.3548677 (Bouveret et
#         al., "Voter Autrement 2017 ... The data of the In Situ Experiment",
#         CC BY 4.0), whose section 4.1 says the dataset is under ODbL 1.0
#         (contents DbCL 1.0). The tables are labelled ODbL 1.0, which meets
#         both the record's CC BY and the codebook's ODbL.
#   2022  doi:10.5281/zenodo.18841758 (concept 18841757), Igersheim, Baujard,
#         Lebon, Delemazure, "Voter Autrement 2022 - Dataset of the In Situ
#         Experiment in Strasbourg" (2026-03-02, v1.0). ODbL 1.0. Files read:
#         approval.csv, scores.csv, majority_judgement.csv, voters.csv,
#         weights.csv. Not in PrefLib 00071; the same protocol, the same
#         authors, and the same licence, so built with the others.
#   ODbL 1.0 was accepted for IRW by Ben on 2026-10-15 (the Voter Autrement
#   online rankings tables, data/rankings/voter_autrement.py).
#
# Grain: one table per (year x city x ballot), where a ballot is one rule on one
#   grade scale. The deposits are split that way (2012, 2017: one file or file
#   set per city, and a city tested different scales; 2017 cities randomised
#   participants across scale variants by ballot-number range, so a variant is
#   its own table). 2007 is the exception: one file set for three towns that all
#   used the same two ballots, so it is two tables with the polling station as a
#   covariate. A participant who saw two ballots (approval, then an evaluative
#   ballot) has the same id in both of that city-year's tables; ids do not link
#   across cities or years (the deposits say a number in one file is a
#   different person in another). id = the deposit's voter number re-keyed
#   1..n in file order.
#
# item: the candidate code c01..cNN: the official candidates' printed names
#   sorted case-insensitively (key (name.casefold(), name)), names never stored
#   (data/rankings/README.md, "Candidate codes"; the same rule as
#   data/rankings/voter_autrement.py and farvaque_2007_faches_irv.py). The code
#   is per year: 12 candidates in 2007 and 2022, 10 in 2012, 11 in 2017, and a
#   code means the same candidate in every table of that year.
#   cov_official_vote, the participant's reported first-round vote, carries the
#   same code; "blank" for a reported blank (2022: blank or spoiled) vote;
#   empty for no answer.
#
# resp: the grade as the deposit records it.
#   approval tables: 1 = approved, 0 = not. On a paper approval ballot an
#     unticked box is the only way to withhold approval, so an empty cell is 0
#     (the 2017 codebook: "In case of no response, the 0 grade is assigned by
#     default"; the 2007/2012/2022 deposits already hold 0). A participant who
#     ticked no one is kept with all 0s.
#   evaluative tables: the number on the ballot's scale. Where the deposit
#     leaves a candidate ungraded the row is absent (2007 scores.csv, the 2017
#     files, Grenoble's "None"). The 2012 deposit already records an ungraded
#     candidate as 0 (its section 2, even on the -1/0/1 scale) and the 2022
#     deposit as -1 (scores.csv) or "A rejeter" (majority_judgement.csv); those
#     cannot be told from a given grade and are kept as recorded. The rules
#     counted an ungraded candidate at the lowest grade; IRW does not impute.
#   majority judgement (2022): the six grades in their French order, A rejeter
#     = 0, Insuffisant = 1, Passable = 2, Assez Bien = 3, Bien = 4, Excellent
#     = 5. The deposit's PDF lists "Tres Bien" where the file has "Passable";
#     the file is followed.
#   Grenoble 2017: a mark on a continuous line from "contre" to "pour", coded
#     in [0, 1] by the authors; kept as recorded, including 40 values below 0
#     (down to -0.225) and 16 above 1 (up to 1.074), marks drawn past the ends
#     of the line (asserted below).
#   Crolles 2017 opinion grades 0-20 with 21 = "without opinion": 21 is not a
#     grade and becomes no row.
#   A 2017 cell that is not a value of its ballot's scale (Strasbourg "1-",
#   "0-1", "_1"; 4 cells) becomes no row; the count is asserted.
#
# Covariates (cov_*, constant within id in a table). Codes are decoded from the
#   2017 codebook (zenodo 3548677, appendix A) to the labels below; a code the
#   codebook does not list, a multiple answer to a single-answer question, and
#   "no answer" become empty.
#   all years but 2007 (whose deposit has no reported vote): cov_official_vote.
#   2007: cov_city, cov_polling_station (deposit voters.csv "City", e.g.
#     Illkirch3 = Illkirch-Graffenstaden station 3).
#   2012: cov_gender (male/female), cov_age (years), cov_situation,
#     cov_favorite_rule (approval/evaluative/both/neither), cov_strategic_1,
#     cov_strategic_2 (0/1; the two questionnaire items quoted in the deposit
#     PDF: took candidates' chances into account; voted with the second round in
#     mind), cov_weight (the deposit's suggested weight for that ballot,
#     <city>_weights.csv; 0 for no reported vote).
#   2017 HSC: cov_gender, cov_age (band), cov_av_feasible, cov_ev_feasible
#     (could the rule be adopted for the presidential election? 1/0), cov_mode
#     (paper/tablet, from the codebook's ballot-number ranges),
#     cov_blank_ballot, cov_spoiled_ballot (the ballot's own blank/spoiled
#     boxes, 1/0).
#   2017 Strasbourg: cov_gender, cov_age, cov_educ, cov_work, cov_religion,
#     cov_sociability, cov_pol_position (1 = extreme left .. 10 = extreme
#     right), cov_to_vote_is (multiple choice, the digits ticked: 1 right,
#     2 duty, 3 chance, 4 useful, 5 useless), cov_liked (1 approval, 2 range,
#     3 both, 4 neither), cov_blank_ballot, cov_spoiled_ballot.
#   2017 Grenoble: cov_gender, cov_age, cov_educ, cov_work, cov_opinion_av,
#     cov_opinion_ev, cov_opinion_official (0 very bad .. 4 very good).
#   2017 Crolles: cov_arm (one_round = ballots 1-1321, approval then the 0-20
#     opinion grades; two_round = ballots 1322-2617, approval as a first round
#     then a ranking, which is not carried here), cov_gender, cov_age, cov_educ,
#     cov_work (from the codebook's one-hot columns).
#   2017 Allevard: cov_gender, cov_age, cov_educ, cov_work.
#   2022: cov_gender, cov_age (band), cov_rule_tested (approval table only:
#     scores or majority_judgement), cov_understand_useless / _desirable /
#     _important / _fundamental (1/0, "Understanding the voting rule is..."),
#     cov_weight (weights.csv, the column for that ballot).
# Not carried: free-text comments (2022 comments.csv, Crolles WHAT_OTHER), the
#   2022 opinions.csv ballot preferences, and the Crolles two-round ranking
#   (RANK_*; a ranking belongs in the rankings family and is not built here).
# No participant is excluded: the 2012 and 2022 weights' zero for "no reported
#   vote" is kept as a covariate, not applied.
#
# Usage: python3 voterautrement_insitu.py <raw dir> <out dir>
#   <raw dir>/<zenodo record id>/<file>, e.g. raw/15007006/approval.csv, from
#   https://zenodo.org/api/records/<id>/files/<file>/content

import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)


def codes_for(names):
    distinct = sorted(set(names), key=lambda n: (n.casefold(), n))
    return {n: f"c{i:02d}" for i, n in enumerate(distinct, start=1)}


def melt(wide, cands, codes, covs):
    """wide: one row per participant with 'id', candidate columns and covs."""
    long = wide.melt(id_vars=["id"] + covs, value_vars=cands, var_name="item", value_name="resp")
    long = long[long.resp.notna()].copy()
    long["item"] = long["item"].map(codes)
    return long[["id", "item", "resp"] + covs]


TABLES = {}


def put(name, long, permitted):
    TABLES[name] = (long, permitted)


# ---- 2007 ------------------------------------------------------------------
d = os.path.join(RAW, "15007006")
a = pd.read_csv(os.path.join(d, "approval.csv"))
s = pd.read_csv(os.path.join(d, "scores.csv"))
v = pd.read_csv(os.path.join(d, "voters.csv"))
cands = list(a.columns[1:])
assert len(cands) == 12
# scores.csv spells one header "GerardSchivardi"; same order as approval.csv.
assert [c.replace(" ", "") for c in s.columns[1:]] == [c.replace(" ", "") for c in cands]
s.columns = ["id"] + cands
assert (a.id == s.id).all() and (a.id == v.id).all() and len(a) == 2836
codes = codes_for(cands)
station = v.City.astype(str)
cov = pd.DataFrame({"id": np.arange(1, len(a) + 1),
                    "cov_city": station.str.replace(r"\d+$", "", regex=True),
                    "cov_polling_station": station})
covs = ["cov_city", "cov_polling_station"]
put("baujard_2007_approval", melt(pd.concat([cov, a[cands]], axis=1), cands, codes, covs), [0, 1])
long = melt(pd.concat([cov, s[cands]], axis=1), cands, codes, covs)
long["resp"] = long.resp.astype(int)
put("baujard_2007_ev_0to2", long, [0, 1, 2])

# ---- 2012 ------------------------------------------------------------------
d = os.path.join(RAW, "17351816")
CANDS12 = None
SCALE12 = {"louvigny": ("ev_m1to1", [-1, 0, 1]), "saintetienne": ("ev_0to2", [0, 1, 2]),
           "strasbourg": ("ev_0to20", list(range(21)))}
FAV = {"Approval Voting": "approval", "Evaluative Voting": "evaluative", "Both": "both",
       "None of them": "neither"}
for city, (slug, scale) in SCALE12.items():
    rd = lambda k: pd.read_csv(os.path.join(d, f"{city}_{k}.csv"))
    v, a, s, w = rd("voters"), rd("approval"), rd("scores"), rd("weights")
    cands = list(a.columns[1:])
    CANDS12 = CANDS12 or cands
    assert cands == CANDS12 == list(s.columns[1:]) and len(cands) == 10
    assert (v.id == a.id).all() and (v.id == s.id).all() and (v.id == w.id).all()
    codes = codes_for(cands)
    ov = v.actual_vote.map(lambda x: "blank" if x == "Blanc" else codes.get(x, np.nan) if isinstance(x, str) else np.nan)
    assert ov.notna().sum() == v.actual_vote.notna().sum()
    base = pd.DataFrame({
        "id": np.arange(1, len(v) + 1),
        "cov_official_vote": ov,
        "cov_gender": v.gender.str.strip().map({"M": "male", "F": "female"}),
        "cov_age": v.age.astype("Int64"),
        "cov_situation": v.situation,
        "cov_favorite_rule": v.favorite.map(FAV),
        "cov_strategic_1": v.question_strategic_1.astype("Int64"),
        "cov_strategic_2": v.question_strategic_2.astype("Int64"),
    })
    covs = list(base.columns[1:]) + ["cov_weight"]
    for kind, grid, name, perm in (("approval", a, f"baujard_2012_{city}_approval", [0, 1]),
                                   ("scores", s, f"baujard_2012_{city}_{slug}", scale)):
        wide = pd.concat([base.assign(cov_weight=w[kind].values), grid[cands]], axis=1)
        long = melt(wide, cands, codes, covs)
        long["resp"] = long.resp.astype(int)
        put(name, long, perm)

# ---- 2022 ------------------------------------------------------------------
d = os.path.join(RAW, "18841758")
v = pd.read_csv(os.path.join(d, "voters.csv"))
a = pd.read_csv(os.path.join(d, "approval.csv"))
s = pd.read_csv(os.path.join(d, "scores.csv"))
m = pd.read_csv(os.path.join(d, "majority_judgement.csv"))
w = pd.read_csv(os.path.join(d, "weights.csv"))
cands = list(a.columns[1:])
assert len(cands) == 12 and list(s.columns[1:]) == cands == list(m.columns[1:])
assert (v.id == a.id).all() and (v.id == w.id).all() and v.id.is_monotonic_increasing
codes = codes_for(cands)
rekey = {old: i for i, old in enumerate(v.id, start=1)}
ov = v.official_vote.map(lambda x: "blank" if x == "Blanc / nul" else codes.get(x, np.nan) if isinstance(x, str) else np.nan)
assert ov.notna().sum() == v.official_vote.notna().sum()
base = pd.DataFrame({
    "id": v.id.map(rekey), "cov_official_vote": ov,
    "cov_gender": v.gender.map({"f": "female", "h": "male"}), "cov_age": v.age,
    "cov_rule_tested": v.rule_tested,
    **{f"cov_{c}": v[c] for c in ["understand_useless", "understand_desirable",
                                  "understand_important", "understand_fundamental"]},
})
assert set(s.id) == set(v.id[v.rule_tested == "scores"])
assert set(m.id) == set(v.id[v.rule_tested == "majority_judgement"])
MJ = {"A rejeter": 0, "Insuffisant": 1, "Passable": 2, "Assez Bien": 3, "Bien": 4, "Excellent": 5}
for kind, grid, name, perm in (("approval", a, "igersheim_2022_strasbourg_approval", [0, 1]),
                               ("scores", s, "igersheim_2022_strasbourg_ev_m1to4", [-1, 0, 1, 2, 3, 4]),
                               ("majority_judgement", m, "igersheim_2022_strasbourg_mj", list(range(6)))):
    grid = grid.copy()
    if kind == "majority_judgement":
        assert set(np.unique(grid[cands].values)) == set(MJ)
        grid[cands] = grid[cands].apply(lambda c: c.map(MJ))
    b = base if kind == "approval" else base.drop(columns="cov_rule_tested")
    b = b.assign(cov_weight=w[kind].values)
    wide = grid.assign(id=grid.id.map(rekey)).merge(b, on="id", how="left", validate="1:1")
    covs = list(b.columns[1:])
    long = melt(wide, cands, codes, covs)
    long["resp"] = long.resp.astype(int)
    put(name, long, perm)

# ---- 2017 ------------------------------------------------------------------
NAMES17 = {"NDA": "Nicolas Dupont-Aignan", "MLP": "Marine Le Pen", "EM": "Emmanuel Macron",
           "BH": "Benoît Hamon", "NA": "Nathalie Arthaud", "PP": "Philippe Poutou",
           "JC": "Jacques Cheminade", "JL": "Jean Lassalle", "JLM": "Jean-Luc Mélenchon",
           "FA": "François Asselineau", "FF": "François Fillon"}
# Names as printed on the official ballot. The codebook's numeric vote order, 1..11:
ORDER17 = ["NDA", "MLP", "EM", "BH", "NA", "PP", "JC", "JL", "JLM", "FA", "FF"]
C17 = codes_for(NAMES17.values())
CODE17 = {k: C17[n] for k, n in NAMES17.items()}
VOTE_NUM = {str(i + 1): CODE17[k] for i, k in enumerate(ORDER17)} | {"12": "blank"}
WORK = {"1": "artisan_liberal", "2": "private_employee", "3": "public_employee", "4": "unemployed",
        "5": "retired", "6": "student", "7": "other"}
EDUC = {"1": "primary", "2": "secondary", "3": "tertiary"}
GENDER12 = {"1": "male", "2": "female"}
BANDS = ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]
BAD = {"n": 0}


def read17(rec):
    d = os.path.join(RAW, rec)
    f = [x for x in os.listdir(d) if x.endswith(".csv")]
    assert len(f) == 1
    t = pd.read_csv(os.path.join(d, f[0]), sep=";", dtype=str, encoding="latin-1",
                    keep_default_na=False)
    t.columns = [c.strip() for c in t.columns]
    t = t.loc[:, [c for c in t.columns if c and not c.startswith("Unnamed")]]
    t = t.apply(lambda c: c.str.strip())
    t = t.replace({"": np.nan, "None": np.nan, "#N/A": np.nan})  # Crolles: 605 "#N/A" OPI cells
    blank = t.VOTER.isna()
    assert t[blank].isna().all(axis=None), rec  # spacer rows only
    t = t[~blank].reset_index(drop=True)
    t["VOTER"] = t.VOTER.astype(int)
    assert t.VOTER.is_unique
    t["id"] = np.arange(1, len(t) + 1)
    return t


def grade(col, scale):
    """Parse one ballot column; a value off the scale is counted and dropped."""
    x = pd.to_numeric(col.str.replace(",", ".", regex=False), errors="coerce")
    bad = col.notna() & (x.isna() | (~x.isin(scale) if scale is not None else False))
    BAD["n"] += int(bad.sum())
    return x.where(~bad)


def one(code_map, col):
    return col.map(code_map)


def onehot(t, cols, labels):
    """One-hot block -> label; none or several ticked -> empty."""
    x = t[cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    k = x.sum(axis=1)
    lab = pd.Series([labels[i] for i in x.values.argmax(axis=1)], index=t.index)
    return lab.where(k == 1)


def ballot17(t, prefix, keys, scale, approval):
    cols = [f"{prefix}{k}" for k in keys]
    g = pd.DataFrame({CODE17[k]: grade(t[c], scale) for k, c in zip(keys, cols)})
    if approval:
        g = g.fillna(0)
    return g


def emit17(name, t, g, covs, scale, keep):
    """keep: boolean mask of participants who had this ballot."""
    wide = pd.concat([t[["id"]], covs, g], axis=1)[keep]
    cands = list(g.columns)
    long = wide.melt(id_vars=["id"] + list(covs.columns), value_vars=cands,
                     var_name="item", value_name="resp")
    long = long[long.resp.notna()]
    if scale is not None and all(float(x).is_integer() for x in scale):
        long["resp"] = long.resp.astype(int)
    put(name, long[["id", "item", "resp"] + list(covs.columns)], scale)


def flag(t, col):
    return pd.to_numeric(t[col], errors="coerce").fillna(0).astype(int) if col in t else None


# Herouville-Saint-Clair: approval, then {0..3} (ballots 1-374) or {0..5} (375-711).
t = read17("3547593")
assert len(t) == 711
cov = pd.DataFrame({
    "cov_official_vote": t.OFFIC.map(VOTE_NUM),
    "cov_gender": t.GENDER.map(GENDER12),
    "cov_age": onehot(t, BANDS, BANDS),
    "cov_av_feasible": pd.to_numeric(t.AV_OPINION, errors="coerce").astype("Int64"),
    "cov_ev_feasible": pd.to_numeric(t.EV_OPINION, errors="coerce").astype("Int64"),
    "cov_mode": np.where(t.VOTER.between(293, 374) | t.VOTER.between(644, 711), "tablet", "paper"),
})
for prefix, slug, scale, rng, appr in (("AV_", "approval", [0, 1], (1, 711), True),
                                       ("EV03_", "ev_0to3", [0, 1, 2, 3], (1, 374), False),
                                       ("EV05_", "ev_0to5", list(range(6)), (375, 711), False)):
    g = ballot17(t, prefix, ORDER17, scale, appr)
    keep = t.VOTER.between(*rng)
    # every participant in a variant's range filled that variant and no other
    if not appr:
        assert (g.notna().any(axis=1) == keep).all(), slug
    blank = "BLANCK" if appr else "BLANK"
    c = cov.assign(cov_blank_ballot=flag(t, f"{prefix}{blank}"), cov_spoiled_ballot=flag(t, f"{prefix}SPOILED"))
    emit17(f"laslier_2017_herouville_{slug}", t, g, c, scale, keep)

# Strasbourg: approval, then {0,1,2} (1-263), {-1,0,1} (264-526), {0..3}
# (527-823) or {-1,0,1,2} (824-1071). Empty = not graded.
t = read17("3547588")
assert len(t) == 1071
ok_multi = lambda s: s.where(s.str.fullmatch(r"[1-5]+", na=False) & s.map(
    lambda z: isinstance(z, str) and len(set(z)) == len(z)))
cov = pd.DataFrame({
    "cov_official_vote": t.OFFIC.map(VOTE_NUM),
    "cov_gender": t.GENDER.map(GENDER12),
    "cov_age": t.AGE.map({str(i + 1): b for i, b in enumerate(BANDS)}),
    "cov_educ": t.EDUC.map(EDUC),
    "cov_work": t.WORK.map(WORK),
    "cov_religion": t.RELIG.map({"1": "regularly", "2": "sometimes", "3": "never"}),
    "cov_sociability": t.SOCIA.map({"1": "out_a_lot", "2": "out_a_little", "3": "rather_lonely"}),
    "cov_pol_position": pd.to_numeric(t.POL_POSITION.str.replace(",", "."), errors="coerce").where(
        lambda x: x.between(1, 10)),
    "cov_to_vote_is": ok_multi(t.TO_VOTE_IS),
    "cov_liked": t.OPI_EXPE.map({"1": "approval", "2": "range", "3": "both", "4": "neither"}),
})
SB = (("AV_", "approval", [0, 1], (1, 1071), True),
      ("EV02_", "ev_0to2", [0, 1, 2], (1, 263), False),
      ("EV-11_", "ev_m1to1", [-1, 0, 1], (264, 526), False),
      ("EV03_", "ev_0to3", [0, 1, 2, 3], (527, 823), False),
      ("EV-12_", "ev_m1to2", [-1, 0, 1, 2], (824, 1071), False))
BAD["n"] = 0
for prefix, slug, scale, rng, appr in SB:
    g = ballot17(t, prefix, ORDER17, scale, appr)
    keep = t.VOTER.between(*rng)
    if not appr:
        assert not (g.notna().any(axis=1) & ~keep).any(), slug  # no grades outside the range
    blank = "BLANCK" if appr else "BLANK"
    c = cov.assign(cov_blank_ballot=flag(t, f"{prefix}{blank}"), cov_spoiled_ballot=flag(t, f"{prefix}SPOILED"))
    emit17(f"laslier_2017_strasbourg_{slug}", t, g, c, scale, keep)
assert BAD["n"] == 4, BAD  # "1-", "0-1", "1-", "_1"

# Grenoble: approval and a continuous [0, 1] line.
t = read17("3547599")
assert len(t) == 1069
NSPP = lambda m: (lambda s: s.map(m))
cov = pd.DataFrame({
    "cov_official_vote": t.OFFIC.map(CODE17 | {"B": "blank"}),
    "cov_gender": t.GENDER.map({"M": "male", "F": "female"}),
    "cov_age": t.AGE.map(dict(zip(["18", "30", "40", "50", "60", "70"], BANDS))),
    "cov_educ": t.EDUC.map({"1": "primary", "2": "secondary", "S": "tertiary"}),
    "cov_work": t.WORK.map({"ART": WORK["1"], "PRI": WORK["2"], "PUB": WORK["3"], "CHO": WORK["4"],
                            "RET": WORK["5"], "ETU": WORK["6"], "AUT": WORK["7"]}),
    **{f"cov_opinion_{k}": pd.to_numeric(t[c], errors="coerce").astype("Int64")
       for k, c in (("av", "AV_OPINION"), ("ev", "EV_OPINION"), ("official", "OFFIC_OPINION"))},
})
g = ballot17(t, "AV_", ORDER17, [0, 1], False)
assert g.notna().all(axis=None)
emit17("laslier_2017_grenoble_approval", t, g.astype(int), cov, [0, 1], t.id > 0)
BAD["n"] = 0
g = ballot17(t, "EV_", ORDER17, None, False)
assert BAD["n"] == 0
vals = g.stack()
assert (vals < 0).sum() == 40 and (vals > 1).sum() == 16 and vals.min() > -0.23 and vals.max() < 1.08
emit17("laslier_2017_grenoble_ev_cont", t, g, cov, None, g.notna().any(axis=1))

# Crolles: approval for everyone; opinion grades 0-20 (21 = no opinion) for
# ballots 1-1321; ranking for 1322-2617 (not carried).
t = read17("3547605")
assert len(t) == 2617
cov = pd.DataFrame({
    "cov_official_vote": onehot(t, [f"OFFI_{k}" for k in ORDER17] + ["OFFI_BLANK"],
                                [CODE17[k] for k in ORDER17] + ["blank"]),
    "cov_arm": np.where(t.VOTER <= 1321, "one_round", "two_round"),
    "cov_gender": onehot(t, ["MAN", "WOMAN"], ["male", "female"]),
    "cov_age": onehot(t, BANDS, BANDS),
    "cov_educ": onehot(t, ["PRIM_EDUC", "SEC_EDUC", "TERT_EDUC"], ["primary", "secondary", "tertiary"]),
    "cov_work": onehot(t, ["LIB_WORK", "PRIV_WORK", "PUB_WORK", "UNEMPLOY", "RETIRED", "STUDENT", "OTHER"],
                       [WORK[str(i)] for i in range(1, 8)]),
})
g = ballot17(t, "AV_", ORDER17, [0, 1], True)
emit17("laslier_2017_crolles_approval", t, g.astype(int), cov, [0, 1], t.id > 0)
BAD["n"] = 0
g = ballot17(t, "OPI_", ORDER17, list(range(22)), False)
assert BAD["n"] == 0
assert not (g.notna().any(axis=1) & (t.VOTER > 1321)).any()
g = g.where(g != 21)
emit17("laslier_2017_crolles_opinion_0to20", t, g.astype("Int64"), cov.drop(columns="cov_arm"),
       list(range(21)), g.notna().any(axis=1))

# Allevard: one of three for/neutral/against scales, randomised.
t = read17("3547607")
assert len(t) == 836
cov = pd.DataFrame({
    "cov_official_vote": t.OFFIC.map(VOTE_NUM),
    "cov_gender": t.GENDER.map(GENDER12),
    "cov_age": t.AGE.map({"1": "18-30", "2": "31-40", "3": "41-50", "4": "51-60", "5": "61-70", "6": "71+"}),
    "cov_work": t.WORK.map(WORK),
    "cov_educ": t.EDUC.map(EDUC),
})
seen = pd.Series(0, index=t.index)
BAD["n"] = 0
for tag, slug, scale in (("{-0,5;0;1}", "ev_m05to1", [-0.5, 0, 1]), ("{-1;0;1}", "ev_m1to1", [-1, 0, 1]),
                         ("{-2;0;1}", "ev_m2to1", [-2, 0, 1])):
    g = pd.DataFrame({CODE17[k]: grade(t[f"{k}_{tag}"], scale) for k in ORDER17})
    keep = g.notna().any(axis=1)
    seen += keep
    emit17(f"laslier_2017_allevard_{slug}", t, g, cov, scale, keep)
assert BAD["n"] == 0 and (seen == 1).all()

# ---- QC + write --------------------------------------------------------------
for name, (t, permitted) in sorted(TABLES.items()):
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    for c in t.columns:
        if c.startswith("cov_"):
            assert (t.groupby("id")[c].nunique(dropna=False) == 1).all(), (name, c)
    checks = run_qc(t, permitted_values=permitted) if permitted is not None else run_qc(t)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    assert t.id.nunique() >= 100, name
    t.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(f"{name}: {len(t)} rows, {t.id.nunique()} participants, {t.item.nunique()} items, "
          f"resp {t.resp.min()}..{t.resp.max()}")
