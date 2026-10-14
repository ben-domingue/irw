"""EmoBank (Buechel & Hahn 2017): 10,548 sentences rated on valence, arousal and dominance
from the writer's and the reader's perspective, five or more annotators per sentence.

Source: https://github.com/JULIELab/EmoBank, corpus/individual_{writer,reader}_ratings.csv
(CC BY-SA 4.0). Each row of those files is one annotator's V/A/D rating of one sentence;
the files carry no annotator identifier, so `trial_annotation` is the row's position
within its sentence (1..k), which is what tells the k ratings of one sentence apart
(datastandard.md, `trial_*`). The same index links a row's three dimensions, since one
annotator gave all three.

Shape (irw#2983, #1443): id = sentence, item = dimension x perspective
(valence-writer, ..., dominance-reader), resp = 1..5. The earlier build dropped the
annotator axis and stored ~5 rows per id x item with nothing to separate them.

    python3 data/emobank_buechel_2017.py -o /some/dir
"""
import argparse
import csv
import pathlib
import urllib.request

RAW = "https://raw.githubusercontent.com/JULIELab/EmoBank/master/corpus/"
DIMS = {"V": "valence", "A": "arousal", "D": "dominance"}


def rows_for(perspective: str, src_dir: pathlib.Path | None):
    name = f"individual_{perspective}_ratings.csv"
    if src_dir is not None:
        text = (src_dir / name).read_text(encoding="utf-8")
    else:
        text = urllib.request.urlopen(RAW + name).read().decode("utf-8")
    seen: dict[str, int] = {}
    for r in csv.DictReader(text.splitlines()):
        k = seen[r["id"]] = seen.get(r["id"], 0) + 1
        for col, dim in DIMS.items():
            v = r[col].strip()
            yield {"id": r["id"], "item": f"{dim}-{perspective}", "resp": v,
                   "trial_annotation": k}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("-o", "--out-dir", required=True)
    p.add_argument("--src-dir", help="local copy of EmoBank/corpus (default: fetch)")
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    src = pathlib.Path(a.src_dir) if a.src_dir else None
    rows = list(rows_for("writer", src)) + list(rows_for("reader", src))
    assert {r["resp"] for r in rows} <= {"1", "2", "3", "4", "5"}, "unexpected rating value"
    rows.sort(key=lambda r: (r["id"], r["item"], r["trial_annotation"]))
    with open(out / "emobank_buechel_2017.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "item", "resp", "trial_annotation"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows, {len({r['id'] for r in rows})} ids, "
          f"{len({r['item'] for r in rows})} items")


if __name__ == "__main__":
    main()
