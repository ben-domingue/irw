"""Age-related valence ratings for 3,600 English words during COVID-19 (Kyröläinen,
Keuleers & Kuperman 2021, Behavior Research Methods, 10.3758/s13428-021-01740-0).

Source: OSF e6px8, `older_adult_trial_data.txt` and `younger_adult_trial_data.txt`
(tab-separated; id, stimulus_word, rating, rt). CC BY-NC-SA 4.0 (README.txt). 545 older
(65+) and 886 younger (18-65) adults each rated a subset of the 3,600 Warriner et al. (2013)
words on a 1 (unhappy) to 9 (happy) scale; 'n' marked a word the participant did not know,
and a small number of trials carry NA (no rating recorded).
Participant ids are already distinct across the two cohorts (the combined file carries
1,431 ids and 1,431 id x group pairs), so they are used as given.

Stimulus-norms shape (irw#2983): id = word, item = `valence` (the single dimension),
rater = participant, rt in seconds as supplied. An unknown-word response is stored as
resp NA with resp_raw = 'n'; an NA trial is resp NA with resp_raw blank; every other
resp_raw is the rating itself.

    python3 data/valence_kyrolainen_2021.py --src-dir <dir with the two txt files> -o <out>
"""
import argparse
import csv
import pathlib

TABLE = "valence_kyrolainen_2021"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src-dir", required=True)
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    src, out = pathlib.Path(a.src_dir), pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for cohort in ("older", "younger"):
        with open(src / f"{cohort}_adult_trial_data.txt", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                raw = r["rating"].strip()
                assert raw in ("n", "NA") or raw in {str(k) for k in range(1, 10)}, raw
                rows.append({"id": r["stimulus_word"], "item": "valence",
                             "resp": "" if raw in ("n", "NA") else raw,
                             "resp_raw": "" if raw == "NA" else raw,
                             "rt": r["rt"], "rater": r["id"]})
    rows.sort(key=lambda r: (r["id"], int(r["rater"])))
    assert len({(r["id"], r["rater"]) for r in rows}) == len(rows), "duplicate word x rater"
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "item", "resp", "resp_raw", "rt", "rater"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows, {len({r['id'] for r in rows})} words, "
          f"{len({r['rater'] for r in rows})} raters, "
          f"{sum(1 for r in rows if r['resp_raw'] == 'n')} unknown-word, "
          f"{sum(1 for r in rows if r['resp_raw'] == '')} NA responses")


if __name__ == "__main__":
    main()
