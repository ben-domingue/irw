"""Italian Sensorimotor Norms (Repetto, Rodella, Conca, Santi & Catricalà 2022, Behavior
Research Methods, 10.3758/s13428-022-02004-1): 959 Italian words rated 0-5 on eleven
sensorimotor dimensions, six perceptual (vision, audition, touch, taste, smell,
interoception) and five action effectors (head, mouth, hand, foot, torso).

Source: OSF rcsnm, `DATA/data all participants_.xlsx`, sheet `ratings_` (CC BY-NC 4.0 on
the OSF node). A wide Qualtrics export: one row per participant (N = 1..391), one column
per list x word x dimension, named `<list>_<n><WORD>-<dimension>` (a few with spaces or an
extra underscore). The list prefix in a header is not reliable: for some control-word
columns it names the wrong list (e.g. `1_59 NEGARE - head` holds list-2 participants'
ratings, complementary to `2_59 NEGARE - interoception`), so the participant's own `List`
column is used for `trial_list` and the header prefix is ignored. Each participant rated one of 19 lists (~50 words + the 10 control words
51-60 that appear in every list). The `control words` sheet re-extracts those control-word
cells with Italian dimension labels and adds summary rows, so it is not read; the
`additional verbs` sheet (72 verbs rated on affective dimensions by 43 participants) is a
different instrument under the 100-stimulus floor and is not built.

Stimulus-norms shape (irw#2983): id = word (upper-cased, as in the headers), item = the
dimension, rater = participant N, `trial_list` = the list the participant rated and
`trial_position` = the word's position in that list. Blank cells are unrated (the
participant's list did not hold the word) and produce no row. Words that appear in several
lists are one `id`; DECOMPORSI sits at positions 44 and 45 of list 3, so those raters
rated it twice and `trial_position` separates the two.

    Rscript -e 'library(readxl); x<-read_excel("data all participants_.xlsx","ratings_",col_names=FALSE,.name_repair="minimal"); write.csv(x,"ratings_.csv",row.names=FALSE,na="")'
    python3 data/sensorimotor_repetto_2022.py --src ratings_.csv -o <out>
"""
import argparse
import collections
import csv
import pathlib
import re

TABLE = "sensorimotor_repetto_2022"
PAT = re.compile(r"^(\d+)_(\d+)_?\s*([^-]+?)\s*-\s*(\w+)$")
DIMS = {"head", "foot", "hand", "mouth", "torso", "interoception",
        "taste", "smell", "touch", "audition", "vision"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="ratings_ sheet exported to CSV, header row 2")
    p.add_argument("-o", "--out-dir", required=True)
    a = p.parse_args()
    out = pathlib.Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(a.src, encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = rows[1]
    assert hdr[0] == "N", hdr[:3]
    cols = []
    for j, h in enumerate(hdr):
        m = PAT.match(h)
        if m:
            word = m.group(3).strip().upper()
            dim = m.group(4).lower()
            assert dim in DIMS, h
            cols.append((j, word, dim, int(m.group(2))))
    out_rows = []
    for r in rows[2:]:
        rater = r[0].strip()
        if not rater:
            continue
        lst = int(r[1])
        for j, word, dim, pos in cols:
            v = r[j].strip()
            if v == "":
                continue
            assert v in {"0", "1", "2", "3", "4", "5"}, (rater, word, dim, v)
            out_rows.append({"id": word, "item": dim, "resp": v, "trial_list": lst,
                             "trial_position": pos, "rater": rater})
    dup = collections.Counter((x["id"], x["item"], x["rater"], x["trial_position"]) for x in out_rows)
    assert max(dup.values()) == 1, "duplicate word x dimension x rater x position"
    repeats = sum(1 for k, v in collections.Counter(
        (x["id"], x["item"], x["rater"]) for x in out_rows).items() if v > 1)
    out_rows.sort(key=lambda x: (x["id"], x["item"], int(x["rater"]), x["trial_position"]))
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "item", "resp", "trial_list", "trial_position", "rater"])
        w.writeheader()
        w.writerows(out_rows)
    words = {x["id"] for x in out_rows}
    per_word = collections.Counter(x["id"] for x in out_rows if x["item"] == "vision")
    print(f"{len(out_rows)} rows, {len(words)} words, {len({x['item'] for x in out_rows})} dims, "
          f"{len({x['rater'] for x in out_rows})} raters; raters per word (vision): "
          f"min {min(per_word.values())}, median {sorted(per_word.values())[len(per_word)//2]}, "
          f"max {max(per_word.values())}; {repeats} repeated word x dimension x rater cells")


if __name__ == "__main__":
    main()
