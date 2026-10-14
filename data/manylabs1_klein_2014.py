"""Many Labs 1 (Klein et al. 2014, Social Psychology 45(3), 10.1027/1864-9335/a000178):
the multi-item dependent measures of four replicated experiments, 6,344 participants at 36 sites.

Source: OSF wx7ck, data component pqf9r, `Datasets.zip` ->
`Data/Tab.delimited.Cleaned.dataset.WITH.variable.values.dat` (tab-separated; the file
"Data released under CC0 license.txt" sits beside it). `session_id` is unique per participant.

Tables (id = session_id, cluster_id = `sample`, the site):
  manylabs1_klein_2014_sysjust          sysjust1-8 (1-7), treat = MoneyGroup (1 currency prime, 0 control)
  manylabs1_klein_2014_flagdv           flagdv1-8 (1-7, scored so higher = more conservative),
                                        treat = flagGroup (1 flag prime, 0 no prime; a third code, 2,
                                        appears for 92 rows with no codebook label and is stored as treat NA)
  manylabs1_klein_2014_math_attitude    iatexplicitmath1-6 (1-6 as coded in the file: good..bad)
  manylabs1_klein_2014_art_attitude     iatexplicitart1-6 (2-7 as coded in the file; the file's coding
                                        of the art items is offset by one from the math items and is kept)
  manylabs1_klein_2014_imagined_contact imaginedexplicit1-4 (1-9), treat = ContactGroup (1 imagined
                                        contact, 0 control)
The IAT, anchoring, gambler's fallacy, allowed/forbidden and other single-item measures are not built.

    python3 data/manylabs1_klein_2014.py --src <...WITH.variable.values.dat> -o <out>
"""
import argparse
import csv
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _multisite_common import write_long, int_in

TABLES = [
    ("manylabs1_klein_2014_sysjust", [f"sysjust{i}" for i in range(1, 9)], 1, 7, "MoneyGroup"),
    ("manylabs1_klein_2014_flagdv", [f"flagdv{i}" for i in range(1, 9)], 1, 7, "flagGroup"),
    ("manylabs1_klein_2014_math_attitude", [f"iatexplicitmath{i}" for i in range(1, 7)], 1, 6, None),
    ("manylabs1_klein_2014_art_attitude", [f"iatexplicitart{i}" for i in range(1, 7)], 2, 7, None),
    ("manylabs1_klein_2014_imagined_contact", [f"imaginedexplicit{i}" for i in range(1, 5)], 1, 9, "ContactGroup"),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    with open(a.src, encoding="latin-1") as fh:
        data = list(csv.DictReader(fh, delimiter="\t"))
    assert len({r["session_id"] for r in data}) == len(data)
    for table, items, lo, hi, group in TABLES:
        rows = []
        for r in data:
            treat = ""
            if group:
                g = r[group].strip()
                treat = g if g in ("0", "1") else ""
            for it in items:
                rows.append({"id": r["session_id"], "item": it, "resp": int_in(r[it], lo, hi),
                             "treat": treat, "cluster_id": r["sample"].strip()})
        cols = ["id", "item", "resp"] + (["treat"] if group else []) + ["cluster_id"]
        write_long(a.out_dir, table, rows, cols)


if __name__ == "__main__":
    main()
