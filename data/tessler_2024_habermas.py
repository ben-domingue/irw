#!/usr/bin/env python3
# Habermas Machine deliberation experiments (Tessler, Bakker et al. 2024) -> 1 IRW
# core table: the fixed five-question survey participants answered after each
# deliberation round, one row per participant x round x question.
#
# Source: Google DeepMind, "Habermas Machine dataset",
#   github.com/google-deepmind/habermas_machine (README, analysis/readme.md,
#   analysis/types.py), data files at
#   https://storage.googleapis.com/habermas_machine/datasets/. Licence: the
#   README's "License and disclaimer" puts the software under Apache 2.0 and
#   "All other materials ... under the Creative Commons Attribution 4.0
#   International License (CC-BY)"; the data files are such materials, so
#   CC BY 4.0 (checked 2026-11-15). Paper: Tessler MH, Bakker MA, Jarrett D,
#   Sheahan H, Chadwick MJ, Koster R, Evans G, Campbell-Gillingham L, Collins T,
#   Parkes DC, Botvinick M, Summerfield C (2024), "AI can help humans find
#   common ground in democratic deliberation", Science 386(6719), eadq2852,
#   doi:10.1126/science.adq2852. PrefLib 00070 carries a derived version (the
#   per-group rankings as 5-voter .soc files); nothing here is read from it.
#
# File read: hm_all_round_survey_responses.parquet (21,608 rows, one per
#   participant x deliberation round; downloaded 2026-11-15, 69,494,354 bytes).
#   Also read, for two columns only (metadata.participant_id, launch_id):
#   hm_all_position_statement_ratings.parquet and
#   hm_all_candidate_comparisons.parquet, to map each session participant id to
#   its group; see trial_group.
#   The other two files of the deposit are not built (see the PR):
#   hm_all_candidate_comparisons.parquet (each participant's ranking and 7-point
#   agreement/quality ratings of the 2-5 statements generated for their own
#   group; every statement set is seen by one group of about five, so neither
#   the statements nor the rankings recur across groups) and
#   hm_all_final_preference_rankings.parquet (a final choice between two
#   statements of the participant's own group).
#
# Design (paper; deposit README): UK participants, recruited online, met in
#   groups of up to five ("launch"). In each round the group was given one
#   question from a bank of policy questions (trial_question_id); each member
#   wrote an opinion, the Habermas Machine (an LLM) wrote candidate group
#   statements, members ranked and rated them, critiqued the winner and ranked
#   a revised set. After each round every member answered the five questions
#   below about the group statement chosen in that round. Sessions usually had
#   three rounds; a person could take part in more than one session and so
#   answers up to 45 rounds here. The deposit's `metadata.version` names the
#   data-collection cohort: five training-data collections (TRAINING_DATA_V1-V5)
#   and the paper's evaluation studies (ablations, critique exclusion, opinion
#   exposure, human mediator, and the virtual citizens' assembly weeks 3-5). In
#   EVAL_COHORT5_OPINION_EXPOSURE the statement asked about is a fellow
#   member's opinion rather than a machine statement and in
#   EVAL_COHORT6_HUMAN_MEDIATOR it is, in some rounds, a human mediator's
#   (trial_statement_source).
#
# The five items, named as the deposit's columns. The deposit gives the
#   variable names and response labels but not the question wording (it is in
#   the paper's supplementary materials, which were not reachable); the glosses
#   are read from the names and labels:
#   best_expression    which better expresses your view: the group statement
#                      (FINAL_CONSENSUS, resp 1) or your own opinion
#                      (OWN_OPINION, resp 0)
#   own_influence      did you have influence on the group statement (YES 1, NO 0)
#   unwanted_pressure  did you feel unwanted pressure (YES 1, NO 0)
#   view_change        did your view change (YES 1, NO 0)
#   view_movement      how did your view move: NO_CHANGE 0,
#                      CLOSER_TO_CONSENSUS 1, SOME_OTHER_WAY 2. The three
#                      categories are UNORDERED: the codes are labels, not a
#                      scale. Treat this item as nominal (resp_raw has the label).
#   resp_raw holds the recorded label for every row. The free-text
#   `view_explanation` is not carried.
#
# Rows dropped: rows whose metadata.provenance is BOT_CITIZEN (2,686) or MOCK
#   (137). These are not responses: the platform put a bot in the seat of a
#   participant who dropped out or timed out, and every answer of those rows is
#   the placeholder "MOCK" (types.py: MOCK "used for testing"); no HUMAN_CITIZEN
#   row carries MOCK. No human participant is excluded (the authors' own
#   exclusions, e.g. of incomplete groups, are not applied).
#
# id: the deposit's worker_id (a persistent pseudonymous participant key),
#   re-keyed 1..n in order of the person's first survey row (timestamp). 4,925
#   rows, mostly from TRAINING_DATA_V1, have no worker_id; for them the session
#   participant id (metadata.participant_id) is the key. Such a person cannot be
#   linked to their other sessions, so they may appear under more than one id.
#   No session participant id carries two worker ids, and no participant id
#   without a worker_id has one in any other file.
#
# Response-level columns:
#   wave   order of the round within the person (1 = their first survey),
#          by timestamp; one id answers each item once per wave.
#   date   the row's `timestamp` as Unix seconds (taken as UTC; the deposit's
#          timestamps are naive and its `metadata.created` strings are UTC).
#   trial_cohort          metadata.version, as recorded (see Design).
#   trial_group           the session group (launch_id), re-keyed 1..n in
#                         order of first appearance; from the two files that
#                         carry launch_id beside each session participant id
#                         (every surveyed participant is in one of them, and
#                         no participant id has two launch_ids).
#   trial_question_id     the deliberation question's id in the deposit's bank
#                         (question.id, e.g. S173961439); the question text is
#                         in the deposit.
#   trial_question_split  question.split as recorded (TRAIN / IID_TEST /
#                         OOD_TEST): the authors' split of the question bank.
#   trial_statement_source  candidate.metadata.provenance, who wrote the
#                         statement the survey is about: MODEL_MEDIATOR (the
#                         machine), HUMAN_MEDIATOR, HUMAN_CITIZEN (a member's
#                         opinion, cohort 5).
#   trial_options_no_to_yes  survey_likert_no_to_yes as 0/1. The deposit does
#                         not document it; by its name it is whether the
#                         response options were shown from No to Yes. It is
#                         constant within a session.
#   No cov_ column: the deposit holds no demographics.
#
# Usage: python3 tessler_2024_habermas.py <raw dir> <out dir>

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TABLE = "tessler_2024_habermas_round_survey"

CODES = {
    "best_expression": {"FINAL_CONSENSUS": 1, "OWN_OPINION": 0},
    "own_influence": {"YES": 1, "NO": 0},
    "unwanted_pressure": {"YES": 1, "NO": 0},
    "view_change": {"YES": 1, "NO": 0},
    "view_movement": {"NO_CHANGE": 0, "CLOSER_TO_CONSENSUS": 1, "SOME_OTHER_WAY": 2},
}
COLS = ["worker_id", "metadata.participant_id", "metadata.provenance",
        "metadata.version", "question.id", "question.split",
        "candidate.metadata.provenance", "survey_likert_no_to_yes",
        "timestamp"] + list(CODES)

d = pd.read_parquet(os.path.join(RAW, "hm_all_round_survey_responses.parquet"),
                    columns=COLS)
assert len(d) == 21608, len(d)
bots = d["metadata.provenance"] != "HUMAN_CITIZEN"
assert set(d.loc[bots, "metadata.provenance"]) == {"BOT_CITIZEN", "MOCK"}
for c in CODES:
    assert (d.loc[bots, c] == "MOCK").all(), c
    assert set(d.loc[~bots, c]) == set(CODES[c]), (c, set(d.loc[~bots, c]))
d = d[~bots].copy()
assert len(d) == 18785, len(d)

pid = d["metadata.participant_id"]
assert d.dropna(subset=["worker_id"]).groupby("metadata.participant_id").worker_id.nunique().max() == 1
assert not set(pid[d.worker_id.isna()]) & set(pid[d.worker_id.notna()])
d["key"] = d.worker_id.where(d.worker_id.notna(), "pid:" + pid)
d = d.sort_values(["timestamp", "key"], kind="stable").reset_index(drop=True)
d["id"] = d.key.map({k: i for i, k in enumerate(d.key.drop_duplicates(), start=1)})
d["wave"] = d.groupby("id").cumcount() + 1
assert not d.duplicated(["id", "timestamp"]).any()

# session participant -> group (launch_id)
p = pd.concat([pd.read_parquet(os.path.join(RAW, f), columns=["metadata.participant_id", "launch_id"])
               for f in ("hm_all_position_statement_ratings.parquet",
                         "hm_all_candidate_comparisons.parquet")]).dropna().drop_duplicates()
assert p.groupby("metadata.participant_id").launch_id.nunique().max() == 1
launch = p.set_index("metadata.participant_id").launch_id
d["launch"] = d["metadata.participant_id"].map(launch)
order = d.launch.dropna().drop_duplicates()
d["trial_group"] = d.launch.map({k: i for i, k in enumerate(order, start=1)})
assert d.trial_group.notna().all()
d["trial_group"] = d.trial_group.astype(int)
assert d.groupby("metadata.participant_id").survey_likert_no_to_yes.nunique().max() == 1

base = pd.DataFrame({
    "id": d.id,
    "wave": d.wave,
    "date": ((d.timestamp - pd.Timestamp(0)).dt.total_seconds()).round(6),
    "trial_cohort": d["metadata.version"],
    "trial_group": d.trial_group,
    "trial_question_id": d["question.id"],
    "trial_question_split": d["question.split"],
    "trial_statement_source": d["candidate.metadata.provenance"],
    "trial_options_no_to_yes": d.survey_likert_no_to_yes.astype(int),
})
parts = []
for item, code in CODES.items():
    t = base.copy()
    t.insert(1, "item", item)
    t.insert(2, "resp", d[item].map(code).astype(int))
    t.insert(3, "resp_raw", d[item])
    parts.append(t)
out = pd.concat(parts, ignore_index=True)
out = out.sort_values(["id", "wave", "item"], kind="stable").reset_index(drop=True)
out = out[["id", "item", "resp", "resp_raw", "wave", "date"]
          + [c for c in out if c.startswith("trial_")]]

n_ids, n_rows = out.id.nunique(), len(out)
assert (n_ids, n_rows) == (4824, 93925), (n_ids, n_rows)
assert not out.duplicated(["id", "item", "wave"]).any()

checks = run_qc(out, permitted_values={i: list(c.values()) for i, c in CODES.items()})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
for c in checks:
    if c.status == "warn":
        print("warn:", c.name, c.detail)
out.to_csv(os.path.join(OUT, TABLE + ".csv"), index=False)
print(f"{TABLE}: {n_ids} ids, {out.item.nunique()} items, {n_rows} rows, "
      f"{out.trial_group.nunique()} groups")
print(out.groupby("item").resp.value_counts().unstack())
