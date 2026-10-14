"""Many Labs 3 (Ebersole et al. 2016, JESP 67, 10.1016/j.jesp.2015.10.012): individual-difference
measures and multi-item dependent measures, 3,759 participants at 20 university pools plus MTurk.

Source: OSF ct89g (CC BY 4.0), `ML3 Final Data.zip` -> `ML3 Final Data/ML3AllSitesandmTurk.csv`
(identical in shape to `ML3 PPool and MTurk Data.csv`); item text in `ML3 Variable Codebook.xlsx`.
`session_id` is missing for 314 rows, so id = Site + RowNumber (RowNumber is unique). cluster_id = Site.

Tables:
  manylabs3_ebersole_2016_tipi        big5_01-10, TIPI (1-7)
  manylabs3_ebersole_2016_nfc         nfc_01-06, Need for Cognition short items (1-5)
  manylabs3_ebersole_2016_intrinsic   intrinsic_01-15, Work Preference Inventory intrinsic items (1-4;
                                      a handful of out-of-range entries stored as missing)
  manylabs3_ebersole_2016_stress      stress_01-04, Perceived Stress Scale 4-item (1-5, as coded)
  manylabs3_ebersole_2016_elm         elm_01-05, persuasion ratings of a message (1-9); treat = 1 strong
                                      arguments (elmstrong_order filled), 0 weak (elmweak_order filled)
  manylabs3_ebersole_2016_sexism_most mcmost1-5, Monin & Miller items worded "most women" (1 = agree,
                                      2 = disagree, as coded)
  manylabs3_ebersole_2016_sexism_some mcsome1-5, the "some women" wording (1/2 as coded); each
                                      participant saw one wording, so these are separate tables.

    python3 data/manylabs3_ebersole_2016.py --src ML3AllSitesandmTurk.csv -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

TABLES = [
    ("manylabs3_ebersole_2016_tipi", [f"big5_{i:02d}" for i in range(1, 11)], 1, 7, None),
    ("manylabs3_ebersole_2016_nfc", [f"nfc_{i:02d}" for i in range(1, 7)], 1, 5, None),
    ("manylabs3_ebersole_2016_intrinsic", [f"intrinsic_{i:02d}" for i in range(1, 16)], 1, 4, None),
    ("manylabs3_ebersole_2016_stress", [f"stress_{i:02d}" for i in range(1, 5)], 1, 5, None),
    ("manylabs3_ebersole_2016_elm", [f"elm_{i:02d}" for i in range(1, 6)], 1, 9, "elm"),
    ("manylabs3_ebersole_2016_sexism_most", [f"mcmost{i}" for i in range(1, 6)], 1, 2, None),
    ("manylabs3_ebersole_2016_sexism_some", [f"mcsome{i}" for i in range(1, 6)], 1, 2, None),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    with open(a.src, encoding="latin-1") as fh:
        data = list(csv.DictReader(fh))
    assert len({r["RowNumber"] for r in data}) == len(data)
    for table, items, lo, hi, kind in TABLES:
        rows = []
        for r in data:
            pid = f"{r['Site']}_{r['RowNumber']}"
            treat = ""
            if kind == "elm":
                strong = r["elmstrong_order"] not in ("", "NA")
                weak = r["elmweak_order"] not in ("", "NA")
                if strong == weak:
                    continue
                treat = "1" if strong else "0"
            for it in items:
                rows.append({"id": pid, "item": it, "resp": int_in(r[it], lo, hi), "treat": treat,
                             "cluster_id": r["Site"]})
        cols = ["id", "item", "resp"] + (["treat"] if kind else []) + ["cluster_id"]
        write_long(a.out_dir, table, rows, cols)


if __name__ == "__main__":
    main()
