"""Correct two live item-text tables after the response-table fixes released 2026-09-27.

Inputs are the published CSVs, downloaded with the read token from irw_text_2 v9.0
(`table.download`, so the literal "NA" nulls survive). Edits are made at the row level with
the csv module; nothing else in either table changes (asserted).

- iandolo_2021_asq__items (#2099, PR #2464): ASQ_20/21/33 were stored reverse-scored for the
  Italian and Japanese subsamples, so batch_048 left their option text blank. The response
  table now ships all three subsamples raw (item_response_warehouse_3 v10.0), so these items
  take the same anchors as the other 37: option_text_translated "Strongly disagree" at resp 1
  and "totally agree" at resp 6 (the paper's own description of the scale). option_text
  (Spanish) stays blank, as for every item.
- liu_2025_ydcy__items (#2117, PR #2463): the 58 YDCY3 zeros are back in the response table
  (item_response_warehouse_4 v9.0: resp 0 n=58). They are the PARS-3 duration item's lowest
  level, so YDCY3 gains an option row at resp 0, "Under 10 minutes", verbatim from the same
  Frontiers supplementary that supplied the other four duration anchors (Chen et al. 2022,
  Front Psychol 13:964169, Data Sheet 1; cached as pars3_frontiers.pdf).

Writes the two corrected __items.csv files to OUT (default: ./out).
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        return next(r), list(r)


def write(p, header, rows):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


# iandolo
h, rows = read(os.path.join(HERE, "iandolo_2021_asq__items.live_irw_text_2_v9.0.csv"))
I, R, OT = h.index("item"), h.index("resp"), h.index("option_text_translated")
before = [list(r) for r in rows]
ANCH = {"1": "Strongly disagree", "6": "totally agree"}
# the other 37 items must already carry exactly these anchors
for r in rows:
    if r[I] not in {"ASQ_20", "ASQ_21", "ASQ_33"} and r[R] in ANCH:
        assert r[OT] == ANCH[r[R]], r
n = 0
for r in rows:
    if r[I] in {"ASQ_20", "ASQ_21", "ASQ_33"} and r[R] in ANCH:
        assert r[OT] == "NA", r
        r[OT] = ANCH[r[R]]
        n += 1
assert n == 6 and len(rows) == 240
changed = [i for i, (a, b) in enumerate(zip(before, rows)) if a != b]
assert len(changed) == 6
write(os.path.join(OUT, "iandolo_2021_asq__items.csv"), h, rows)

# liu
h, rows = read(os.path.join(HERE, "liu_2025_ydcy__items.live_irw_text_2_v9.0.csv"))
I, R, O = h.index("item"), h.index("resp"), h.index("option_text")
assert not any(r[I] == "YDCY3" and r[R] == "0" for r in rows)
src = [r for r in rows if r[I] == "YDCY3" and r[R] == "1"]
assert len(src) == 1 and src[0][O] == "11 to 20 minutes"
new = list(src[0]); new[R] = "0"; new[O] = "Under 10 minutes"
pos = rows.index(src[0])
rows.insert(pos, new)
assert len(rows) == 18
write(os.path.join(OUT, "liu_2025_ydcy__items.csv"), h, rows)
print("ok: iandolo 6 cells filled (240 rows); liu +1 row (18 rows)")
