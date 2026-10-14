"""PSACR001 (Dorison et al. 2022, Affective Science 3, 10.1007/s42761-022-00128-3): loss- vs
gain-framed COVID-19 health messages, 15,929 online participants in 84 countries.

Source: OSF 3g7vq, data component m6q8f, `Data/psacr001_data_clean.csv` (CC0). id = unique_id.
treat = frame (1 loss framing, 0 gain framing; the two message frames, no untreated arm).
cov_country = participant country (3-letter), cov_panel = 1 if recruited through a panel.

Tables (7-point items unless noted):
  psacr001_dorison_2022_behint   behavioural intentions, behint_it1-4
  psacr001_dorison_2022_policy   policy support, policy_it1-5
  psacr001_dorison_2022_anxiety  anxiety, anxiety_it1-3 (1-5)

    python3 data/psacr001_dorison_2022.py --src psacr001_data_clean.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

TABLES = [("psacr001_dorison_2022_behint", [f"behint_it{i}" for i in range(1, 5)], 7),
          ("psacr001_dorison_2022_policy", [f"policy_it{i}" for i in range(1, 6)], 7),
          ("psacr001_dorison_2022_anxiety", [f"anxiety_it{i}" for i in range(1, 4)], 5)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    with open(a.src, encoding="utf-8") as fh:
        data = list(csv.DictReader(fh))
    assert len({r["unique_id"] for r in data}) == len(data)
    for table, items, hi in TABLES:
        rows = [{"id": r["unique_id"], "item": it, "resp": int_in(r[it], 1, hi),
                 "treat": {"loss": "1", "gain": "0"}[r["frame"]],
                 "cov_country": r["country"], "cov_panel": "1" if r["where"] == "panel" else "0"}
                for r in data for it in items]
        write_long(a.out_dir, table, rows, ["id", "item", "resp", "treat", "cov_country", "cov_panel"])


if __name__ == "__main__":
    main()
