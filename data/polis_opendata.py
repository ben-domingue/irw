#!/usr/bin/env python3
# Polis open data (The Computational Democracy Project) -> 19 IRW core tables of
# agree / disagree / pass votes on participant-written statements, one row per
# vote cast, one table per Polis conversation.
#
# Source: github.com/compdemocracy/openData (cloned 2026-11-15, commit
#   3be5785c3f5975d31f4578ee8bbf4426d45b7bf2, 2026-03-08). Licence: the README's
#   Licensing section, "All Polis data is licensed under a Creative Commons
#   Attribution 4.0 International license", with this required attribution:
#   "Data was gathered using the Polis software (compdemocracy.org/polis) and is
#   sub-licensed under CC BY 4.0 with Attribution to The Computational Democracy
#   Project. The data and more information about how the data was collected can
#   be found at the following link(s): <case study URLs>". The statement and the
#   conversation's case-study URL go into every dictionary row. The export
#   format is documented at compdemocracy.org/export/ (the codebook used here).
#   PrefLib 00069 carries 20 of these conversations; the tables are rebuilt from
#   the originals.
#
# What a conversation is. A facilitator opens a Polis conversation on a topic;
#   participants write short statements ("comments") and vote on other
#   participants' statements, which Polis shows one at a time, with three
#   buttons: agree, disagree, pass/unsure. Statements enter during the
#   conversation, so who saw which statement depends on when they took part and
#   on Polis's routing; most participants vote on a fraction of the statements.
#
# Files read per conversation directory: votes.csv (the complete vote history:
#   timestamp, comment-id, voter-id, vote) and comments.csv (comment-id,
#   author-id, moderated, comment-body). participants-votes.csv (the latest-vote
#   matrix) was checked against votes.csv: for every conversation it equals the
#   last vote per voter x comment exactly, so it adds nothing and is not read.
#   comments.csv's agrees column equals the count of vote = 1 among latest votes
#   (r >= 0.999 in every conversation; it is a snapshot, not always exact), which
#   confirms the export page's coding: 1 = agree, -1 = disagree, 0 = pass.
#   stats-history.csv and summary.csv are conversation-level and not read.
#   bg2050-volunteers holds participant-votes.csv and comment-groups.csv instead
#   of the usual names; only votes.csv and comments.csv are read there too.
#   scoop-hivemind.taxes/ holds a nested copy of itself
#   (scoop-hivemind.taxes.5sw7wa5dep.2020-12-11/), byte-identical; the top-level
#   files are read.
#
# Tables (conversation directory -> table; year = the case-study year, which
#   is the year of the first vote):
CONVERSATIONS = {
    "15-per-hour-seattle": "polis_2014_seattle_min_wage",
    "american-assembly.bowling-green": "polis_2018_bowling_green",
    "austria-climate.2vkxcncppn.2022-07-07": "polis_2022_klimarat_energy",
    "austria-climate.5twd2jsnkf.2022-08-08": "polis_2022_klimarat_production",
    "austria-climate.5tzfrp5eaa.2022-07-07": "polis_2022_klimarat_mobility",
    "austria-climate.7z7ejpbmv5.2022-08-08": "polis_2022_klimarat_housing",
    "austria-climate.9xnndurbfm.2022-07-07": "polis_2022_klimarat_food_land_use",
    "bg2050-volunteers": "polis_2025_bowling_green_2050",
    "brexit-consensus": "polis_2017_brexit_consensus",
    "canadian-electoral-reform": "polis_2016_canada_electoral_reform",
    "football-concussions": "polis_2015_football_concussions",
    "march-on.operation-marchin-orders": "polis_2018_march_on",
    "scoop-hivemind.affordable-housing": "polis_2017_scoop_housing",
    "scoop-hivemind.biodiversity": "polis_2019_scoop_biodiversity",
    "scoop-hivemind.freshwater": "polis_2017_scoop_freshwater",
    "scoop-hivemind.taxes": "polis_2018_scoop_taxes",
    "scoop-hivemind.ubi": "polis_2017_scoop_ubi",
    "ssis.land-bank-farmland.2rumnecbeh.2021-08-01": "polis_2021_san_juan_land_use",
    "vtaiwan.uberx": "polis_2015_vtaiwan_uberx",
}
#   Not built: london.youth.policing (26 voters, 39 statements), under the
#   ~50-participant floor.
#   Naming: the data have an organisation, not a person, as creator; the tables
#   follow the corpus's source-name + year form for organisation-made data
#   (spain_<year>_*, enem_*, lichess_*, lmarena_*) with "polis" as the source.
#
# id: the deposit's voter-id (an integer unique within one conversation)
#   re-keyed 1..n in ascending voter-id order. ids do not link conversations.
#
# item: the deposit's comment-id, unchanged. The statement text is in
#   comments.csv (comment-body), keyed by the same id; no item-text table is
#   built. Statements are participant-written, often seeded by the facilitator.
#
# resp: 1 = agree, 0 = disagree, empty = pass. The deposit codes 1 / -1 / 0
#   (compdemocracy.org/export/: "A vote of 1 represents agree, a vote of -1
#   represents disagree, and a vote of 0 represents a pass"); the button reads
#   "pass / unsure". A pass is declining to take a side, not a midpoint between
#   agree and disagree (datastandard.md, step 6), so its row is kept with resp
#   empty and resp_raw = "pass" -- the same handling as the "blank" of
#   data/navarrete_2023_policy.py. resp_raw: agree / disagree / pass, the button
#   pressed.
#
# Rows: every row of votes.csv, as recorded. votes.csv is the full vote history,
#   so a participant who voted on a statement more than once has one row per
#   vote (in most repeated pairs the same vote again, in some a changed vote;
#   a few rows are exact duplicates down to the timestamp). date (Unix seconds,
#   from the export's timestamp; milliseconds in every conversation except
#   bg2050-volunteers, which exports seconds) orders them; the latest per id x
#   item is the participant's standing vote, the one Polis's own matrix holds.
#   Some conversations kept collecting votes long after the event (the demo
#   conversations 15-per-hour-seattle and football-concussions to 2019); kept.
#
# Item-level columns (constant within item):
#   itemcov_moderated   the statement's moderation status at export, as the
#                       deposit codes it: 1 = accepted, 0 = unmoderated, -1 =
#                       moderated out (export page). Votes on moderated-out
#                       statements are real votes, cast before moderation or
#                       under permissive moderation; they are kept, and this
#                       column lets a user drop them.
#   itemcov_author_id   the IRW id of the participant who wrote the statement;
#                       empty when the author cast no vote at all in the
#                       conversation (1-2 statements in a few conversations).
#                       Polis records an agree for the author on submission in
#                       most conversations (the vote seconds after the
#                       statement), so this column also lets a user drop
#                       authors' votes on their own statements. Many
#                       statements (most of them in polis_2018_march_on and
#                       polis_2022_klimarat_mobility, where the median item has
#                       one voter) carry only that vote: they were moderated
#                       out or never moderated, so Polis never routed them to
#                       other participants. They are kept.
#
# Not carried: group-id in participants-votes.csv, the k-means opinion-group
#   assignment Polis computed at export time -- an output of the authors'
#   analysis of these votes, not a participant attribute; n-comments / n-votes /
#   n-agree / n-disagree, counts derivable from the table and itemcov_author_id;
#   the statement text. No participant or vote is excluded (other than the
#   floor above, which drops a whole conversation).
#
# Usage: python3 polis_opendata.py <openData checkout> <out dir>

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from irw_validate._checks import run_qc  # noqa: E402

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

LABEL = {1: "agree", -1: "disagree", 0: "pass"}
RESP = {1: 1.0, -1: 0.0, 0: np.nan}

# (ids, items, rows) asserted so a changed deposit is noticed
EXPECT = {
    "polis_2014_seattle_min_wage": (339, 54, 2995),
    "polis_2018_bowling_green": (2031, 896, 226148),
    "polis_2022_klimarat_energy": (1756, 1039, 133082),
    "polis_2022_klimarat_production": (1116, 522, 61936),
    "polis_2022_klimarat_mobility": (3142, 2138, 307778),
    "polis_2022_klimarat_housing": (1503, 611, 80208),
    "polis_2022_klimarat_food_land_use": (3616, 1452, 270366),
    "polis_2025_bowling_green_2050": (7886, 7378, 1034363),
    "polis_2017_brexit_consensus": (204, 50, 5312),
    "polis_2016_canada_electoral_reform": (448, 174, 12018),
    "polis_2015_football_concussions": (1487, 298, 14924),
    "polis_2018_march_on": (6289, 2161, 536984),
    "polis_2017_scoop_housing": (381, 165, 15076),
    "polis_2019_scoop_biodiversity": (536, 314, 29802),
    "polis_2017_scoop_freshwater": (117, 80, 3979),
    "polis_2018_scoop_taxes": (334, 148, 17379),
    "polis_2017_scoop_ubi": (234, 70, 7174),
    "polis_2021_san_juan_land_use": (404, 293, 33530),
    "polis_2015_vtaiwan_uberx": (1921, 197, 49997),
}


def build(conv):
    d = os.path.join(RAW, conv)
    v = pd.read_csv(os.path.join(d, "votes.csv"))
    c = pd.read_csv(os.path.join(d, "comments.csv"))
    assert set(v.vote.unique()) <= {1, 0, -1}, v.vote.unique()
    assert c["comment-id"].is_unique
    assert set(v["comment-id"]) <= set(c["comment-id"])
    assert set(c.moderated.unique()) <= {1, 0, -1}

    key = {u: i for i, u in enumerate(sorted(v["voter-id"].unique()), start=1)}
    ms = v.timestamp.max() > 1e11  # milliseconds (all but bg2050-volunteers)
    out = pd.DataFrame({
        "id": v["voter-id"].map(key),
        "item": v["comment-id"].astype(int),
        "resp": v.vote.map(RESP).astype("Int64"),
        "resp_raw": v.vote.map(LABEL),
        "date": (v.timestamp / 1000.0).round(3) if ms else v.timestamp.astype(float),
    })
    cc = c.set_index("comment-id")
    out["itemcov_moderated"] = out.item.map(cc.moderated).astype("Int64")
    out["itemcov_author_id"] = out.item.map(cc["author-id"].map(key)).astype("Int64")
    out = out.sort_values(["id", "date", "item"], kind="stable").reset_index(drop=True)
    return out


for conv, name in CONVERSATIONS.items():
    assert len(name) <= 40, name
    t = build(conv)
    got = (t.id.nunique(), t.item.nunique(), len(t))
    assert got == EXPECT[name], (name, got)
    checks = run_qc(t, permitted_values=[0, 1])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    rr = t.resp_raw.value_counts().to_dict()
    print(f"{name}: {got[0]} ids, {got[1]} items, {got[2]} rows, "
          f"agree {rr.get('agree', 0)} disagree {rr.get('disagree', 0)} pass {rr.get('pass', 0)}, "
          f"moderated-out items {(t.drop_duplicates('item').itemcov_moderated == -1).sum()}",
          flush=True)
