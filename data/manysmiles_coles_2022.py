"""Many Smiles Collaboration (Coles et al. 2022, Nature Human Behaviour 6, 10.1038/s41562-022-01458-9):
facial-feedback test, 5,856 participants in 27 labs across 19 countries.

Source: OSF ac3t2, `Main study/data.zip` -> `data/raw/MSC_data_raw.csv` with
`data/codebooks/MSC_codebook_raw.xlsx` (CC0). id = Qualtrics ResponseId. cluster_id = `lab`
(ISO country + join order, e.g. USA_01); the 103 rows with no lab are dropped. The between-participant
factor `condition` (pentask / directd / mimicry: which facial-feedback method) has no control arm, so it
is carried as cov_condition rather than `treat`; cov_image = present/absentt (whether positive images
accompanied the task).

Tables:
  manysmiles_coles_2022_emotion         nine self-reported emotion items (ang, hap, nrv, sat, enj, lke,
                                        tir, con, wor; 1-7) reported after each of four trials. The
                                        trial is `trial_pose`: fil1 (first filler), neutral, happy,
                                        fil4 (last filler); it is what separates a participant's four
                                        answers to one item.
  manysmiles_coles_2022_body_awareness  18 body-awareness items indiv_body_001-018 (1-7).

    python3 data/manysmiles_coles_2022.py --src MSC_data_raw.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

TRIALS = [("fil.1", "fil1"), ("neutr", "neutral"), ("happy", "happy"), ("fil.4", "fil4")]
EMOT = ["ang", "hap", "nrv", "sat", "enj", "lke", "tir", "con", "wor"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    with open(a.src, encoding="utf-8") as fh:
        data = [r for r in csv.DictReader(fh) if r["lab"].strip()]
    assert len({r["ResponseId"] for r in data}) == len(data)
    cov = lambda r: {"cluster_id": r["lab"], "cov_condition": r["condition"], "cov_image": r["image"]}
    emo = [{"id": r["ResponseId"], "item": f"emot_{e}", "resp": int_in(r[f"{src}_emot_{e}"], 1, 7),
            "trial_pose": pose, **cov(r)} for r in data for src, pose in TRIALS for e in EMOT]
    write_long(a.out_dir, "manysmiles_coles_2022_emotion", emo,
               ["id", "item", "resp", "trial_pose", "cluster_id", "cov_condition", "cov_image"])
    body = [{"id": r["ResponseId"], "item": f"body_{i:02d}", "resp": int_in(r[f"indiv_body_{i:03d}"], 1, 7),
             **cov(r)} for r in data for i in range(1, 19)]
    write_long(a.out_dir, "manysmiles_coles_2022_body_awareness", body,
               ["id", "item", "resp", "cluster_id", "cov_condition", "cov_image"])


if __name__ == "__main__":
    main()
