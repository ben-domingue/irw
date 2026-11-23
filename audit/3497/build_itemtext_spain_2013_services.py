#!/usr/bin/env python3
"""Drop the resp 0 'No procede' option rows from four spain_2013_services item-text tables (#3497).

In IRW 471 (2026-09-29, item_response_warehouse_2 v27.0) the response tables
importance, inpersonsat, internetout and othercontact had resp 0 ('No procede',
the CIS not-asked routing code) recoded to missing; table_changes records it
(PR #3689). The live item text still carries an option row for resp 0 on 26
items. Those rows describe a value that no longer occurs, so they are removed.
Nothing else changes: every surviving row is written field-for-field as
the live row.

Reads live copies fetched with irw::irw_itemtext() into
/home/ben/irw-stage/3497-live/<table>__live.csv and writes
/home/ben/irw-stage/3497-up/<table>__items.csv. Nothing is uploaded. Text is
handled as strings at the csv level so IRW's literal "NA" survives.
"""
import csv
from pathlib import Path

LIVE = Path("/home/ben/irw-stage/3497-live")
STAGE = Path("/home/ben/irw-stage/3497-up")

DROP = {
    "spain_2013_services_importance": ["p6a"],
    "spain_2013_services_inpersonsat": ["p12", "p13", "p15"] + [f"p14{i:02d}" for i in range(1, 10)],
    "spain_2013_services_internetout": ["p22", "p22b", "p23"] + [f"p24{i:02d}" for i in range(1, 7)],
    "spain_2013_services_othercontact": ["p16a", "p17a", "p18a", "p18b"],
}


def build(t, items):
    with open(LIVE / f"{t}__live.csv", newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        cols, rows = r.fieldnames, list(r)
    out, dropped = [], []
    for row in rows:
        if row["resp"] == "0":
            assert row["item"] in items, (t, row["item"])
            assert row["option_text"] == "No procede", (t, row["item"], row["option_text"])
            assert row["option_text_translated"] == "Not applicable", (t, row["item"])
            dropped.append(row["item"])
            continue
        assert "procede" not in row["option_text"], (t, row["item"], row["resp"])
        out.append(row)
    assert sorted(dropped) == sorted(items), (t, set(items) ^ set(dropped))
    STAGE.mkdir(exist_ok=True)
    with open(STAGE / f"{t}__items.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(out)
    print(f"{t}: {len(rows)} -> {len(out)} rows; dropped resp 0 on {len(dropped)} items; "
          f"{len({r['item'] for r in out})} items")
    return len(dropped)


n = sum(build(t, items) for t, items in DROP.items())
assert n == 26, n
print(f"total dropped: {n}")
