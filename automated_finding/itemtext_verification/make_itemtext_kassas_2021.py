#!/usr/bin/env python3
"""Item text for kassas_2021_covid_exposure and kassas_2021_covid_mitigation (Harvard
Dataverse 10.7910/DVN/VR7OND). English administration (US).

Cheap case: the .dta variable labels are the questions and the value labels the anchors;
data/kassas_2021_covid_risk.py exposes labels() -> (variable labels, value labels) and the
item lists EXP / MIT, so the item code is the deposit's own column name. The deposit's label
for "cleaning" duplicates the "delivery" label (a label slip in the .dta); that item's text
is left blank rather than shipped wrong.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "kassas_2021_covid_risk.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def main():
    spec = importlib.util.spec_from_file_location("kassas", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    varlab, vallab = mod.labels()
    for table, items, instrument in [
        ("kassas_2021_covid_exposure", mod.EXP, "Perceived likelihood of COVID-19 exposure by setting (study-specific)"),
        ("kassas_2021_covid_mitigation", mod.MIT, "Household COVID-19 mitigation behaviours (study-specific)"),
    ]:
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert set(items) == set(resp["item"]), table
        rows = []
        for code in items:
            opts = {int(k): v for k, v in vallab[code].items()}
            assert set(resp.loc[resp["item"] == code, "resp"].unique()) <= set(opts), code
            text = "" if code == "cleaning" else varlab[code]
            for r, o in sorted(opts.items()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                             "instructions": "", "section_prompt": "", "item_text": text,
                             "correct_response": "", "option_text": o, "resp": r})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(items)} items")


if __name__ == "__main__":
    main()
