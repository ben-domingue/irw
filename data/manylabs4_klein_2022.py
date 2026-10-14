"""Many Labs 4 (Klein et al. 2022, Collabra: Psychology 8(1), 10.1525/collabra.35271): mortality
salience replication, 2,281 participants at 21 lab sources (18 locations).

Source: OSF 8ccnw, data component ua2nb, `merged_deidentified_full.csv` (CC0); key in `data.key.docx`
(jd8xh). `participantnum` is assigned per site and is blank for 443 rows, so id = source + row
position in the file. cluster_id = `source` (the lab, with in-house and expert-protocol runs of one
location kept separate); cov_expert = 1 if the site ran the expert-designed protocol. treat =
ms_condition (1 mortality salience, 0 television control).

Tables:
  manylabs4_klein_2022_panasx  PANAS-X, 60 adjective items (1-5), 1,536 rows carry any of them.
  manylabs4_klein_2022_essay   pro-US (prous1-5) and anti-US (antius1-5) essay/author ratings, 1-9.
                               Site-specific entry errors (negative values, >9, non-integers) are
                               stored as missing.

    python3 data/manylabs4_klein_2022.py --src merged_deidentified_full.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    with open(a.src, encoding="utf-8") as fh:
        data = list(csv.DictReader(fh))
    hdr = list(data[0].keys())
    panas = hdr[hdr.index("cheerful"):hdr.index("dissatisfiedwithself") + 1]
    assert len(panas) == 60, len(panas)
    essay = [f"prous{i}" for i in range(1, 6)] + [f"antius{i}" for i in range(1, 6)]
    cols = ["id", "item", "resp", "treat", "cluster_id", "cov_expert"]
    base = []
    for k, r in enumerate(data, start=1):
        base.append((f"{r['source']}_{k}", {"ms": "1", "tv": "0"}.get(r["ms_condition"], ""),
                     r["source"], r["expert"], r))
    for table, items, lo, hi in [("manylabs4_klein_2022_panasx", panas, 1, 5),
                                 ("manylabs4_klein_2022_essay", essay, 1, 9)]:
        rows = [{"id": i, "item": it, "resp": int_in(r[it], lo, hi), "treat": t,
                 "cluster_id": c, "cov_expert": e} for i, t, c, e, r in base for it in items]
        write_long(a.out_dir, table, rows, cols)


if __name__ == "__main__":
    main()
