#!/usr/bin/env python3
# Mon Programme 2022 (France) and Brazucracia (Brazil) -> 2 IRW core tables of
# approval responses to presidential candidates' policy proposals, one row per
# participant x proposal shown.
#
# Source: Navarrete C, Macedo M, Colley R, Zhang J, Ferrada N, Mello ME, Lira R,
#   Bastos-Filho C, Grandi U, Lang J, Hidalgo CA, "Data collection of two
#   real-world digital democracy systems", Harvard Dataverse,
#   doi:10.7910/DVN/8E0EA4 (V1, 2023-09-18). Licence CC0 1.0 (Dataverse record,
#   checked 2026-11-15). Paper: Navarrete et al. (2023), "Understanding political
#   divisiveness using online participation data from the 2022 French and
#   Brazilian presidential elections", Nature Human Behaviour 8, 137-148,
#   doi:10.1038/s41562-023-01755-x (arXiv:2211.04577). PrefLib 00076 carries the
#   approval part only; these tables are rebuilt from the Dataverse original.
#   The deposit has no README; the screens are described in the paper's
#   Supplementary Information (SI) sections 1.1-1.4 and Tables S3-S8, and in the
#   platform template the authors published (github.com/CenterForCollectiveLearning
#   /opencracia: modules/Approval.jsx, components/CardAgree.jsx, tables.sql).
#
# Files read (Dataverse "original format" downloads):
#   Dataset 1, approval_screen_{brazil,france}.csv  -> the responses
#   Dataset 3, {brazil,france}_participation.csv    -> the authors' per-user
#       suspicious and pre_launch flags only (the file is otherwise the pairwise
#       comparisons the authors derived from Datasets 1 and 2)
#   Dataset 4, popup_screen_{brazil,france}.csv     -> self-reported demographics
#   Dataset 6, intention_screen_brazil.csv          -> Brazil vote intention
#   Dataset 5 (set_proposals_*) holds the proposal text (item text; not built
#   into an item-text table here). Dataset 2 (rank screen) is not built: see
#   the PR for why.
#
# The approval screen. Participants saw the candidates' proposals (120 in France,
#   67 in Brazil) in panels of k proposals; k ("universe", cov_panel_size) was
#   assigned at random per participant: 4, 5 or 6 in France (3 in 267 rows, a
#   value outside the design that the SI's bot criterion 1 flags), 5 in Brazil.
#   For each proposal the participant pressed approve (tick), disapprove (cross)
#   or "blank" (fr "blanc"); the panel could not be submitted until every card
#   had one of the three. In France the approval panel alternated with a rank
#   panel (fallback voting); in Brazil all proposals were shown in repeated
#   approval panels first. A participant could stop at any point, so most saw
#   only some proposals (median 50 of 72 ids in Brazil, 110 of 120 in France).
#
# id: the deposit's user_id (a random UUID stored in the participant's browser)
#   re-keyed 1..n per country in order of the participant's first approval row
#   (created_at, then the deposit's row id). The UUID is not stored. ids do not
#   link France and Brazil.
#
# item: the deposit's issue_id (proposal id). The proposal text in French or
#   Portuguese, English and Spanish, its category and (Brazil) the candidates
#   who proposed it are in Dataset 5, keyed by the same id. Brazil has 5 ids
#   that Dataset 5 does not list (64, 69, 89, 93, 103; 1 to 5 responses each);
#   they are kept as recorded.
#
# resp: 1 = approve, 0 = disapprove, empty = "blank". The deposit's `agree` is
#   1 / -1 / 0; the SI (Table S3) calls 0 "absent" and the platform's button
#   reads "blank", and the authors omit those rows from their pairwise data
#   ("We omit abstentions from approval screens", SI 1.2). A blank is a
#   non-response, not a midpoint between approve and disapprove
#   (datastandard.md, step 6), so its row is kept with resp empty and
#   resp_raw = "blank". resp_raw: approve / disapprove / blank, the button
#   pressed, so nothing the deposit recorded is lost.
#
# Rows are kept as recorded, including repeats of one id x item: 55 pairs in
#   Brazil and 527 in France come almost all from a whole panel stored twice a
#   fraction of a second apart (a double submission), and some from a proposal
#   answered again later (123 French pairs carry two different answers). `date`
#   (Unix seconds, from created_at, microseconds kept) orders them; a user who
#   wants one answer per pair can keep the first or the last.
#
# Covariates (constant within id; empty where the participant has no record):
#   cov_panel_size   the participant's universe (panel size k).
#   cov_locale       platform language of the participant's first approval row
#                    (fr/en/es in France, pt/en/es in Brazil; 9 French and 3
#                    Brazilian participants switched language part-way).
#   cov_suspicious   the authors' bot flag (Dataset 3 `suspicious`, 1 = flagged
#                    by at least one of the six criteria of SI 1.4); the authors
#                    dropped these participants, IRW keeps them. Constant per
#                    user in the file; empty for participants absent from it.
#   cov_pre_launch   Dataset 3 `pre_launch` (1 = took part before public
#                    launch); max over the user's rows (10 Brazilian users have
#                    both values).
#   From the optional popup questionnaire (Dataset 4), the participant's latest
#   record (the SI's rule, "keeping the last record"); codes as recorded. What
#   the codes mean, from SI Tables S7/S8 and the platform's form labels:
#   cov_politics     political orientation 1-5 from left to right (the form's
#                    five options: left, centre-left, centre, centre-right,
#                    right; SI: 1, 2 = liberal, 4, 5 = conservative); 99 = no
#                    answer.
#   cov_age_group    age range 1-7 (SI: 1-4 "young", 5-7 "old"; the deposit
#                    does not give the cut points); 98, 99 non-substantive.
#   cov_sex          1 = female, 2 = male (SI); 98, 99 non-substantive (the form
#                    offered "other" and "prefer not to answer"; the deposit
#                    does not say which code is which).
#   cov_zone         1 = urban, 2 = rural, 99 = no answer.
#   cov_education    1-7, did not finish high school .. PhD (SI: 1-3 less than
#                    undergraduate, 4-7 undergraduate or more); 99 = no answer.
#   cov_location     France: department code (75 = Paris; 972, 973 overseas;
#                    998, 999 non-substantive). Brazil: the platform's
#                    municipality id (the deposit gives no key; SI names 3516
#                    Rio de Janeiro, 2699 Sao Paulo, 2392 Brasilia).
#   cov_state        Brazil only: the popup's `region`, a state abbreviation.
#   Brazil only, from the vote-intention screen (Dataset 6, latest record):
#   cov_vote_intention   1 = will vote, 2 = will not, 3 = does not know (the
#                        screen's three options in order); 98, 99 non-substantive.
#   cov_vote_candidate   the deposit's candidate_id, as recorded (0-13); the
#                        deposit gives no key to candidates, and IRW would store
#                        a code, not a name, in any case.
#
# Not carried: the reCAPTCHA `score` of each row (the per-user flag above is the
#   authors' use of it); `multichoice`, the level picked for the few proposals
#   that offered one once approved (e.g. "20%", "1500EUR net par mois"; 3,582
#   French rows, 1 Brazilian); the deposit's row id; the popup's own universe and
#   score. No participant is excluded: suspicious, pre-launch and
#   non-questionnaire participants are all kept.
#
# Usage: python3 navarrete_2023_policy.py <raw dir> <out dir>
#   <raw dir> holds the Dataverse original-format files renamed
#   approval_{brazil,france}.csv, participation_{brazil,france}.csv,
#   popup_{brazil,france}.csv, intention_brazil.csv (datafile ids 7363173,
#   7363177, 7363175, 7363181, 7363180, 7363174, 7363182).

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

LABEL = {1: "approve", -1: "disapprove", 0: "blank"}
RESP = {1: 1.0, -1: 0.0, 0: np.nan}


def latest(df, cols):
    """One row per user_id: the latest record (created_at, then row id)."""
    df = df.sort_values(["user_id", "created_at", "id"])
    return df.groupby("user_id").tail(1).set_index("user_id")[cols]


def build(country):
    a = pd.read_csv(os.path.join(RAW, f"approval_{country}.csv"))
    assert set(a.agree.unique()) <= {1, 0, -1}, a.agree.unique()
    assert a.groupby("user_id").universe.nunique().max() == 1
    a = a.sort_values(["created_at", "id"]).reset_index(drop=True)
    order = a.drop_duplicates("user_id").user_id.tolist()
    key = {u: i for i, u in enumerate(order, start=1)}

    out = pd.DataFrame({
        "id": a.user_id.map(key),
        "item": a.issue_id.astype(int),
        "resp": a.agree.map(RESP).astype("Int64"),
        "resp_raw": a.agree.map(LABEL),
        "date": (pd.to_datetime(a.created_at, utc=True, format="ISO8601")
                 - pd.Timestamp(0, tz="UTC")).dt.total_seconds().round(6),
    })

    cov = pd.DataFrame(index=pd.Index(order, name="user_id"))
    first = a.drop_duplicates("user_id").set_index("user_id")
    cov["cov_panel_size"] = first.universe
    cov["cov_locale"] = first.locale

    p = pd.read_csv(os.path.join(RAW, f"participation_{country}.csv"),
                    usecols=["user_id", "suspicious", "pre_launch"])
    assert p.groupby("user_id").suspicious.nunique().max() == 1
    flags = p.groupby("user_id")[["suspicious", "pre_launch"]].max()
    cov["cov_suspicious"] = flags.suspicious.reindex(cov.index).astype("Int64")
    cov["cov_pre_launch"] = flags.pre_launch.reindex(cov.index).astype("Int64")

    pop = pd.read_csv(os.path.join(RAW, f"popup_{country}.csv"))
    pcols = {"politica": "cov_politics", "age": "cov_age_group", "sex": "cov_sex",
             "zone": "cov_zone", "education": "cov_education", "location": "cov_location"}
    if country == "brazil":
        pcols["region"] = "cov_state"
    lp = latest(pop, list(pcols)).rename(columns=pcols)
    for c in lp.columns:
        cov[c] = lp[c].reindex(cov.index)
        if c != "cov_state":
            cov[c] = cov[c].astype("Int64")

    if country == "brazil":
        it = pd.read_csv(os.path.join(RAW, "intention_brazil.csv"))
        li = latest(it, ["intention", "candidate_id"])
        cov["cov_vote_intention"] = li.intention.reindex(cov.index).astype("Int64")
        cov["cov_vote_candidate"] = li.candidate_id.reindex(cov.index).astype("Int64")

    cov.index = cov.index.map(key)
    out = out.join(cov, on="id")
    out = out.sort_values(["id", "date", "item"], kind="stable").reset_index(drop=True)

    # counts asserted so a changed deposit is noticed
    n_ids, n_rows = out.id.nunique(), len(out)
    expect = {"brazil": (606, 25266), "france": (1629, 120755)}[country]
    assert (n_ids, n_rows) == expect, (country, n_ids, n_rows)
    assert out.groupby("id")[[c for c in out if c.startswith("cov_")]].nunique().max().max() <= 1
    return out


TABLES = {
    "navarrete_2023_policy_approval_france": build("france"),
    "navarrete_2023_policy_approval_brazil": build("brazil"),
}

for name, t in TABLES.items():
    checks = run_qc(t, permitted_values=[0, 1])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(f"{name}: {t.id.nunique()} ids, {t.item.nunique()} items, {len(t)} rows, "
          f"resp {t.resp.value_counts(dropna=False).to_dict()}")
