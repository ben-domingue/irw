"""PSA001 (Jones et al. 2021, Nature Human Behaviour 5, 10.1038/s41562-020-01007-2): 120 Chicago
Face Database faces rated on 13 traits by 13,571 raters in 40 labs (Psychological Science Accelerator).

Source: OSF f7v3n, data component jfwtr, `data/psa001_ratings_raw.csv` (CC BY 4.0). Each rater rated
all 120 faces on ONE trait, twice (block 1 and block 2); `psa001_ind.csv` averages the two blocks and
is not used. Stimulus-norms shape (irw#2983): id = face (`stim_id`), item = trait, rater = user_id,
trial_block = block (1/2), trial_order = presentation order within the block, rt in seconds
(source milliseconds / 1000; a negative or non-numeric rt is stored as missing). Rows with a missing block or rating are dropped. The small number of
exact repeats of (rater, face, trait, block, order) are collapsed to one row.

    python3 data/psa001_jones_2021_face_traits.py --src psa001_ratings_raw.csv -o <out>
"""
import argparse
import csv
import pathlib


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    seen = set()
    n = dup = 0
    ids, raters = set(), set()
    with open(a.src, encoding="utf-8") as fh, \
            open(out / "psa001_jones_2021_face_traits.csv", "w", newline="", encoding="utf-8") as oh:
        w = csv.writer(oh)
        w.writerow(["id", "item", "resp", "rt", "trial_block", "trial_order", "rater"])
        for r in csv.DictReader(fh):
            if r["block"] not in ("1", "2") or r["rating"] not in [str(k) for k in range(1, 10)]:
                continue
            key = (r["user_id"], r["stim_id"], r["trait"], r["block"], r["order"])
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            rt = ""
            try:
                ms = float(r["rt"])
                rt = f"{ms / 1000:.3f}" if ms >= 0 else ""
            except ValueError:
                pass
            w.writerow([r["stim_id"], r["trait"], r["rating"], rt, r["block"], r["order"], r["user_id"]])
            n += 1
            ids.add(r["stim_id"])
            raters.add(r["user_id"])
    print(f"psa001_jones_2021_face_traits: {n} rows, {len(ids)} faces, {len(raters)} raters, "
          f"{dup} exact repeats dropped")


if __name__ == "__main__":
    main()
