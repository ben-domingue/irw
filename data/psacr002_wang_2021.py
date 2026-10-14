"""PSACR002 (Wang et al. 2021, Nature Human Behaviour 5, 10.1038/s41562-021-01173-x): brief
reappraisal interventions on COVID-19 emotions, 21,645 participants in 88 countries.

Source: OSF 3g7vq -> 4yf9d -> jeu73, `Processed/Data/data_wide_exclusion_12.23.2020.csv` (CC0).
id = unique_id (one duplicated row dropped). Sixteen emotion items (1-5), eight negative (sadness,
stress, loneliness_1-3, anger, fear, distrust) and eight positive (serenity, gratitude,
socialconnected_1-3, inspiration, love, hope), were answered at baseline (wave 0) and again after the
intervention (wave 1, the `_state_` columns). Per-photo single ratings and the covid19 summary items
are not built. treat = 1 for the two reappraisal arms (Reconstrual, Repurposing), 0 for Passive and
Active Control; cov_condition names the arm. cov_country = ISO-3 code taken from the source label,
cov_month = data-collection month.

    python3 data/psacr002_wang_2021.py --src data_wide_exclusion_12.23.2020.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

NEG = ["sadness", "stress", "loneliness_1", "loneliness_2", "loneliness_3", "anger", "fear", "distrust"]
POS = ["serenity", "gratitude", "socialconnected_1", "socialconnected_2", "socialconnected_3",
       "inspiration", "love", "hope"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    seen, rows = set(), []
    with open(a.src, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["unique_id"] in seen:
                continue
            seen.add(r["unique_id"])
            cond = r["condition"]
            treat = "1" if cond in ("Reconstrual", "Repurposing") else "0" if cond.endswith("Control") else ""
            country = r["country"].rsplit(" - ", 1)[-1].strip()
            for wave, tag in (("0", "baseline"), ("1", "state")):
                for val, items in (("negative", NEG), ("positive", POS)):
                    for it in items:
                        rows.append({"id": r["unique_id"], "item": f"{val}_{it}",
                                     "resp": int_in(r[f"C2_{val}emotion_{tag}_{it}"], 1, 5),
                                     "wave": wave, "treat": treat, "cov_condition": cond,
                                     "cov_country": country, "cov_month": r["month"]})
    write_long(a.out_dir, "psacr002_wang_2021_emotion", rows,
               ["id", "item", "resp", "wave", "treat", "cov_condition", "cov_country", "cov_month"])


if __name__ == "__main__":
    main()
