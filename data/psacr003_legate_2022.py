"""PSACR003 (Legate, Nguyen, Weinstein et al. 2022, PNAS 119(22), 10.1073/pnas.2111091119): a
global experiment on motivating social distancing, 20,035 participants in 49 languages.

Source: OSF myxzk (project) -> gvw56 (data, CC BY 4.0), `processed_data/study3_data.csv.zip`: a
long formr export, one row per participant x item (`unique_id`, `item_name`, `answer`). id = unique_id.
Participants read an autonomy-supportive message, a controlling message, or no message (`C3_group`
1/2/3; about 1% of participants lack the matching message page in the export, and the group
code is taken as authoritative). treat = 1 if any message
was read, 0 for no message; cov_condition = autonomy / controlling / none. cov_language = survey
language; cov_recruit = recruitment route (`where`: pool, ZPID, nudge, prolific, qualtrics).

Tables (all 1-7):
  psacr003_legate_2022_motivation  eight motivation-to-distance items (C3_motiv_*)
  psacr003_legate_2022_reactance   four defiance items (C3_defy_*)
  psacr003_legate_2022_manipcheck  three perceived-message items (C3_manipcheck_*)
  psacr003_legate_2022_avoidance   six items: how much the participant currently avoids crowds, friends,
                                   non-essential shopping (`_current`) and how likely they are to next
                                   week (`_week`)

    python3 data/psacr003_legate_2022.py --src study3_data.csv.zip -o <out>
"""
import argparse
import collections
import csv
import io
import sys
import zipfile
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

TABLES = {
    "psacr003_legate_2022_motivation": {f"C3_motiv_{k}": f"motiv_{k}" for k in
        ["criticized", "disapprove", "guilty", "important", "meaningful", "pressure", "understand", "values"]},
    "psacr003_legate_2022_reactance": {f"C3_defy_{k}": f"defy_{k}" for k in
        ["aggravating", "intrusion", "opposite", "resist"]},
    "psacr003_legate_2022_manipcheck": {f"C3_manipcheck_{k}": f"message_{k}" for k in ["choices", "needs", "pressure"]},
    "psacr003_legate_2022_avoidance": {**{f"C3_avoid_{k}c": f"avoid_{k}_current" for k in ["crowds", "friends", "shopping"]},
                                       **{f"C3_avoid_{k}w": f"avoid_{k}_week" for k in ["crowds", "friends", "shopping"]}},
}
WANT = {k for m in TABLES.values() for k in m} | {"C3_group", "C3_autonomy_message_1", "C3_controlling_message_1"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    ans = collections.defaultdict(dict)
    meta = {}
    with zipfile.ZipFile(a.src).open("study3_data.csv") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8")):
            if r["item_name"] in WANT:
                ans[r["unique_id"]][r["item_name"]] = r["answer"]
                meta[r["unique_id"]] = (r["language"], r["where"])
    grp = {"1": "autonomy", "2": "controlling", "3": "none"}
    bad = 0
    for uid, d in ans.items():
        g = grp.get(d.get("C3_group", ""))
        saw = ("C3_autonomy_message_1" in d, "C3_controlling_message_1" in d)
        if (g == "autonomy") != saw[0] or (g == "controlling") != saw[1]:
            bad += 1
    # ~200 participants (1%) carry a group code without the matching message page in the export
    # (dropouts before the message, or pages not logged); C3_group, the study's own assignment, governs.
    assert bad < 400, f"{bad} participants whose group disagrees with the message pages shown"
    for table, items in TABLES.items():
        rows = []
        for uid, d in ans.items():
            g = grp.get(d.get("C3_group", ""))
            if g is None:
                continue
            for src, it in items.items():
                rows.append({"id": uid, "item": it, "resp": int_in(d.get(src, ""), 1, 7),
                             "treat": "0" if g == "none" else "1", "cov_condition": g,
                             "cov_language": meta[uid][0], "cov_recruit": meta[uid][1]})
        write_long(a.out_dir, table, rows, ["id", "item", "resp", "treat", "cov_condition", "cov_language", "cov_recruit"])
    print("group/page disagreements:", bad)


if __name__ == "__main__":
    main()
