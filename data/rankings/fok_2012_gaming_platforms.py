#!/usr/bin/env python3
##Ranking of six gaming platforms by 91 Dutch students -> one IRW rankings table.
##Source: Fok, D., Paap, R. and van Dijk, B. "A Rank-Ordered Logit Model With Unobserved Heterogeneity
##in Ranking Capabilities", Journal of Applied Econometrics 27(5), 831-846, 2012 (doi
##10.1002/jae.1223). Data: JAE Data Archive at ZBW, doi:10.15456/jae.2022320.0727246821, CC BY 4.0
##(the licence printed on the archive's resource pages; the dataset's CKAN record leaves license_id
##empty, so the resource page is the source). Files read: game_data.csv (91 rows, `;`-separated) and
##readme.fpd.txt (the variable labels, transcribed into the dicts below).
##
##The authors ran the survey themselves ("a short survey that we conducted ourselves among 91
##students"); the readme states no fielding date (the data file is dated October 2010). Each student
##ranked the six platforms from 1 (most preferred) to 6 (least preferred). The file holds one row per
##student with v1_1..v1_6 giving the RANK of each platform, so the platform is the column and the value
##is the position -- candidate-major.
##
##The same data ship in the R package mlogit as `Game`/`Game2`; this table is built from the authors'
##deposit, not from mlogit, because mlogit keeps only the ranks, ownership, age and hours, and because
##it changes one ranking: student 49 gives rank 5 to both Xbox and GameCube and no platform rank 2, and
##mlogit's copy gives GameCube rank 2. Here that ranking is kept as recorded (a tie at position 5 and a
##gap at 2, README "Rules").
##
##Layout: id = the student's row number in the file (the file has no id column), task = 1, item = the
##platform as the readme names it, resp = the rank given, 1 = most preferred. Covariates, all
##respondent-level and as recorded except gender, which the readme codes 1 = female, 0 = male:
##cov_gender (female/male), cov_age (years), cov_hours_gaming (hours per week spent on gaming),
##cov_owns_<platform> (1 = owns it, 0 = not), cov_importance_<feature> (how important the feature is for
##a gaming platform, 1 = not important at all .. 5 = very important), cov_likes_<genre> (1 = likes that
##genre of games, 0 = not). The readme labels the RPG column v5_5; the file names it v4_5, the fifth of
##the genre block, and that is how it is read here.
##
##The readme's second dataset (political goals, CV'04) is not distributed by the authors and is not
##part of this table.
##
##Usage: python3 fok_2012_gaming_platforms.py build <raw dir> <out dir>
##Table: fok_2012_gaming_platforms.
from __future__ import annotations

import csv
import sys
from pathlib import Path

from rank_common import design_counts, fetch, upsert_design, write_table

TABLE = "fok_2012_gaming_platforms"
COLLECTION = "10.15456/jae.2022320.0727246821"
DATA_URL = ("https://journaldata.zbw.eu/dataset/72b44cc5-1a3e-4037-98c4-c62c3bc3843b/resource/"
            "634c8374-dfa0-4fe3-8abc-96292edc6f8c/download/game_data.csv")

##readme.fpd.txt, blocks v1 (rank) and v2 (ownership): the same six platforms in the same order.
PLATFORMS = ["Xbox", "Playstation", "Playstation portable", "GameCube", "GameBoy", "PC"]
OWN_NAMES = ["xbox", "playstation", "playstation_portable", "gamecube", "gameboy", "pc"]
##block v3: "how important are the following items for a gaming platform"
IMPORTANCE = ["price_hardware", "price_software", "exchangeability_games", "availability_games",
              "graphical_capabilities", "portability", "multiplayer_capabilities", "other_capabilities"]
##block v4: "which genre of games do you like"
GENRES = ["shooting_action", "strategy", "puzzle", "sports_race", "rpg"]
GENDER = {"1": "female", "0": "male"}


def build(raw_dir: Path, out_dir: Path) -> None:
    src = fetch(DATA_URL, raw_dir / "game_data.csv")
    with open(src, newline="", encoding="utf-8") as f:
        data = list(csv.DictReader(f, delimiter=";"))
    expected = ([f"v1_{k}" for k in range(1, 7)] + [f"v2_{k}" for k in range(1, 7)]
                + [f"v3_{k}" for k in range(1, 9)] + [f"v4_{k}" for k in range(1, 6)] + ["v5", "v6", "v7"])
    if list(data[0]) != expected:
        raise ValueError(f"unexpected columns {list(data[0])}")
    rows, non_perm = [], []
    for i, r in enumerate(data, start=1):
        if r["v5"] not in GENDER:
            raise ValueError(f"unknown gender code {r['v5']!r} in row {i}")
        cov = {"cov_gender": GENDER[r["v5"]], "cov_age": r["v6"], "cov_hours_gaming": r["v7"]}
        cov.update({f"cov_owns_{n}": r[f"v2_{k}"] for k, n in enumerate(OWN_NAMES, start=1)})
        cov.update({f"cov_importance_{n}": r[f"v3_{k}"] for k, n in enumerate(IMPORTANCE, start=1)})
        cov.update({f"cov_likes_{n}": r[f"v4_{k}"] for k, n in enumerate(GENRES, start=1)})
        ranks = [int(r[f"v1_{k}"]) for k in range(1, 7)]
        if sorted(ranks) != list(range(1, 7)):
            non_perm.append(i)
        for platform, rank in zip(PLATFORMS, ranks):
            if not 1 <= rank <= 6:
                raise ValueError(f"rank {rank} out of 1..6 in row {i}")
            rows.append({"id": i, "task": 1, "item": platform, "resp": rank, **cov})
    rows.sort(key=lambda x: (x["id"], x["resp"], PLATFORMS.index(x["item"])))
    write_table(out_dir / f"{TABLE}.csv", rows)
    counts = design_counts(rows)
    upsert_design({
        "table": TABLE, "source_file": "game_data.csv", "collection": COLLECTION,
        "jurisdiction": "Netherlands (survey of students)",
        "date": "unknown",
        "office": "six gaming platforms ranked from 1 (most preferred) to 6 (least preferred)",
        "method": "survey", "seats": "na", **counts,
        "n_ballots_cast": len(data), "n_ballots_eligible_est": len(data),
        "write_in_allowed": "no", "candidate_order": "unknown",
        "evidence": (f"JAE Data Archive (ZBW) {COLLECTION}, file game_data.csv, CC BY 4.0 as printed on the "
                     f"archive's resource page; variable labels from readme.fpd.txt; paper Fok, Paap & van Dijk, "
                     f"Journal of Applied Econometrics 27(5) 2012, 10.1002/jae.1223; date unknown (the readme "
                     f"states no fielding date; the data file is dated 2010-10-14); seats na (a survey); "
                     f"{len(data)} students, every one ranks all six platforms; rows not a permutation of 1..6, "
                     f"kept as recorded: {non_perm} (row 49: Xbox and GameCube both 5, no platform 2; the R "
                     f"package mlogit's copy changes GameCube to 2); candidate_order unknown (the readme lists "
                     f"the platforms in the order Xbox, Playstation, Playstation portable, GameCube, GameBoy, "
                     f"PC but does not say how the questionnaire presented them); counts computed by "
                     f"fok_2012_gaming_platforms.py"),
    })
    print(f"{TABLE}: {len(rows)} rows, {counts['n_ballots_with_marks']} students, "
          f"{counts['n_candidates']} platforms, rankings not a permutation: {non_perm}")


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] != "build":
        print("usage: fok_2012_gaming_platforms.py build <raw dir> <out dir>")
        return 2
    build(Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
