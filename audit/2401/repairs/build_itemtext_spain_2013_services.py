#!/usr/bin/env python3
"""Rebuild spain_2013_services_{complaints,internet,purpose} item text after the #2401 data fix.

The response tables were recoded in PR #2577 and released in IRW v484:
  complaints  p27c code 3 ("Todavía está tramitándose") -> missing; p27c/p27d code 0
              ("No procede") was already missing on live before that release.
  internet    p19 code 0 -> missing; p2101-p2110 (mark-all-that-apply) recoded to
              1 = marked, 0 = asked but not marked, missing = not asked.
  purpose     p1101-p1111, the same recode.

So the item text's option rows for values that no longer occur are removed, and on the
mark-all-that-apply items the resp 0 row, which was labelled "No procede" / "Not
applicable", now means "not marked". CIS prints no word for an unmarked line (the
questionnaire prints only the code 1; 'Sí' for 1 is the ES2986 value label), so that
row's option_text and option_text_translated are left NA rather than given wording
IRW would have to invent. The public_note explains the coding.

Reads the live copies fetched with irw::irw_itemtext() into
/home/ben/irw-stage/spain-2013-services-itemtext-live/<table>__live.csv and writes
/home/ben/irw-stage/spain-2013-services-itemtext/<table>__items.csv. Nothing is
uploaded. Text is handled as strings at the csv level so IRW's literal "NA" survives.
"""
import csv
from pathlib import Path

STAGE = Path("/home/ben/irw-stage/spain-2013-services-itemtext")
LIVE = Path("/home/ben/irw-stage/spain-2013-services-itemtext-live")
P11 = [f"p11{i:02d}" for i in range(1, 12)]
P21 = [f"p21{i:02d}" for i in range(1, 11)]


def read(t):
    with open(LIVE / f"{t}__live.csv", newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        return r.fieldnames, list(r)


def write(t, cols, rows):
    with open(STAGE / f"{t}__items.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)


def build(t, drop, unlabel):
    """drop: {(item, resp)} rows removed; unlabel: items whose resp 0 row loses its label."""
    cols, rows = read(t)
    out, dropped, relabelled = [], set(), set()
    for r in rows:
        k = (r["item"], r["resp"])
        if k in drop:
            dropped.add(k)
            continue
        if r["resp"] == "0" and r["item"] in unlabel:
            assert r["option_text"] == "No procede", (t, k, r["option_text"])
            assert r["option_text_translated"] == "Not applicable", (t, k)
            r = dict(r, option_text="NA", option_text_translated="NA")
            relabelled.add(r["item"])
        out.append(r)
    assert dropped == drop, (t, drop - dropped)
    assert relabelled == set(unlabel), (t, set(unlabel) - relabelled)
    # every other field of every surviving row is unchanged
    kept = [r for r in rows if (r["item"], r["resp"]) not in drop]
    for a, b in zip(kept, out):
        diff = {c for c in cols if a[c] != b[c]}
        assert diff <= {"option_text", "option_text_translated"}, (t, a["item"], diff)
    write(t, cols, out)
    print(f"{t}: {len(rows)} -> {len(out)} rows; dropped {sorted(drop)}; "
          f"resp 0 unlabelled on {len(relabelled)} items")


build("spain_2013_services_complaints",
      drop={("p27c", "0"), ("p27c", "3"), ("p27d", "0")}, unlabel=[])
build("spain_2013_services_internet", drop={("p19", "0")}, unlabel=P21)
build("spain_2013_services_purpose", drop=set(), unlabel=P11)
