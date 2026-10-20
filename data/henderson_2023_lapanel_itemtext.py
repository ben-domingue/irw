"""
Item text for the henderson_2023_lapanel_* response tables.

Companion to `data/henderson_2023_lapanel.py` — read that header first for the
source, licence, geographic-column drops and the QIEEJU/1IWRQA duplication
finding. Licence is CC0 1.0, so the item wording redistributes freely.

Stems: taken from the SPSS variable labels of the wave-1 survey file in the
    project depository 10.7910/DVN/1IWRQA (datafile 7047437,
    `format=original`), NOT from the Stata variable labels of
    `masterfile_wide.dta`. Reason: Stata caps a variable label at 80
    characters and 317 of the master file's labels sit exactly at that cap,
    truncated mid-word ("...will get sick from the coronavirus ("). The SPSS
    labels of the same questions are the full question text. Both files are
    the same survey from the same deposit family, and the join is by question
    number (q20 <-> q20_w1), which is how the two files name the same item.
    The battery-level prompt is the part of the label before " -- " and the
    per-item wording the part after; `item_text` is the label verbatim.

Options: from the SPSS value labels of the same variables. Codes 8 ("skipped")
    and 9 ("not asked") are sentinels, not scale points, and are not emitted;
    they do not appear in the response tables either.

Instrument identification: the author-written LSU Manship School / Public
    Policy Research Lab Louisiana coronavirus panel survey. Verbatim searches
    on the stems ("Your local hospital will run out of necessary equipment
    like beds or ventilators", "comfortable or uncomfortable with -- Going to
    a retail clothing store", "Limiting the number of workers or customers
    businesses can have on site") return only this survey programme's own
    releases and match no published psychometric instrument — the same
    determination `data/henderson_2023_louisiana_covid.py` recorded for the
    identical batteries. These seven therefore need no third-party rights
    register row.

NOT covered here, deliberately:
    racial_resent -- Kinder & Sanders racial resentment scale. No row in
        itemtext/instrument_rights_register.csv; silence does not ship.
    tipi          -- Gosling, Rentfrow & Swann Ten-Item Personality Inventory.
        Needs a by-name register check that has not been done.
    Their response tables ship; their item text is held.

Scope note: the stems come from the wave-1 file, and the item text is emitted
    once per item (not per wave). The wording of these batteries is identical
    across waves in the master file's own labels, so one row set covers all
    five waves.
"""

import os
import sys


import pandas as pd

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from irw_validate import validate_file  # noqa: E402
import pyreadstat

SAV = sys.argv[1]          # 1IWRQA wave1.sav, format=original
OUTDIR = sys.argv[2]       # .../stage_2026-10-20_s6/items

# Must mirror BATTERIES in data/henderson_2023_lapanel.py exactly.
BATTERIES = {
    "health_emotion": {
        2: "anxious", 3: "worried", 4: "afraid", 5: "angry", 6: "outraged",
        7: "annoyed", 8: "relaxed", 9: "hopeful", 10: "optimistic",
        164: "skeptical", 165: "convinced",
    },
    "econ_emotion": {
        11: "anxious", 12: "worried", 13: "afraid", 14: "angry", 15: "outraged",
        16: "annoyed", 17: "relaxed", 18: "hopeful", 19: "optimistic",
    },
    "worry": {
        20: "family_sick", 21: "family_die", 22: "hospital_equipment",
        23: "health_system_overrun", 24: "pay_bills", 25: "lose_income",
        26: "local_business_close", 27: "economy_recession",
    },
    "health_threat": {
        29: "you", 30: "blacks", 31: "whites", 32: "over60", 33: "under40",
        34: "wealthy", 35: "poor", 36: "rural", 37: "cities",
    },
    "fin_threat": {
        43: "you", 44: "blacks", 45: "whites", 46: "over60", 47: "under40",
        48: "wealthy", 49: "poor", 50: "rural", 51: "cities",
    },
    "comfort": {
        80: "retail_store", 81: "restaurant", 82: "bar", 83: "workplace",
        84: "salon", 85: "large_event", 86: "visit_friends",
        87: "religious_service", 88: "group_meeting", 89: "campaign_rally",
        90: "protest", 91: "public_meeting", 92: "vote_in_person",
        93: "children_school",
    },
    "policy_support": {
        95: "unemployment_funding", 96: "mask_requirement",
        97: "limit_workers_customers", 98: "vaccine_requirement",
        99: "quarantine_positive", 100: "business_relief",
        101: "vote_by_mail", 102: "contact_info_collection",
        103: "eviction_ban",
    },
}
HELD = {
    "racial_resent": "Kinder & Sanders racial resentment scale -- no rights register row",
    "tipi": "TIPI (Gosling, Rentfrow & Swann) -- by-name register check not done",
}
SENTINELS = {8, 9}
INSTRUMENT = ("LSU Manship School Public Policy Research Lab Louisiana "
              "coronavirus panel survey (Henderson, NSF #2031591), waves 1-5")

df, meta = pyreadstat.read_sav(SAV, apply_value_formats=False)
labels = meta.column_names_to_labels
vlab_of = meta.variable_to_label

written = []
for battery, qmap in BATTERIES.items():
    table = f"henderson_2023_lapanel_{battery}"
    rows = []
    for q, suffix in qmap.items():
        col = next((c for c in (f"q{q}", f"Q{q}") if c in labels), None)
        if col is None:
            raise SystemExit(f"{table}: q{q} absent from the wave-1 SPSS file")
        stem = (labels[col] or "").strip()
        assert stem, f"{table}: q{q} has an empty SPSS variable label"
        assert len(stem) < 80 or " -- " in stem, f"{table}: q{q} looks truncated: {stem!r}"
        prompt = stem.split(" -- ")[0].strip() if " -- " in stem else None
        opts = meta.value_labels.get(vlab_of.get(col), {})
        opts = {int(k): v for k, v in opts.items() if int(k) not in SENTINELS}
        assert opts, f"{table}: q{q} has no usable value labels"
        for code, text in sorted(opts.items()):
            rows.append({
                "table": table,
                "section_id": f"{table}_1",
                # Prime commandment: `item` must be identical to the `item`
                # value in the response table, which carries the bare suffix
                # (no battery prefix). Do not prefix it here.
                "item": suffix,
                "instrument": INSTRUMENT,
                "instructions": None,
                "section_prompt": prompt,
                "item_text": stem,
                "correct_response": None,
                "option_text": text,
                "resp": code,
            })
    out = pd.DataFrame(rows)
    assert not out[["item", "resp"]].duplicated().any(), f"{table}: duplicate item/resp"
    assert out["item"].nunique() == len(qmap), f"{table}: item code collision"
    # An __items.csv is item text, not a response table. run_qc and
    # validate_frame are both the WRONG gate here: they classify a frame with
    # no `id` column as kind="responses" and error on the missing column.
    # validate_file detects kind="item_text" from the __items name, so the gate
    # has to see a correctly-named file -- hence write-validate-move, which
    # keeps it a gate rather than a check after the fact. An earlier version
    # asserted on a `failures` attribute Report does not have, so it passed
    # unconditionally; assert on .ok/.errors.
    path = os.path.join(OUTDIR, f"{table}__items.csv")
    staging = os.path.join(OUTDIR, ".gate")
    os.makedirs(staging, exist_ok=True)
    tmp = os.path.join(staging, f"{table}__items.csv")
    out.to_csv(tmp, index=False)
    _report = validate_file(tmp, profile="upload")
    assert _report.kind == "item_text", (table, _report.kind)
    assert _report.ok, (table, _report.errors)
    os.replace(tmp, path)
    written.append((table, out["item"].nunique(), len(out)))
    print(f"{table}__items.csv: {out['item'].nunique()} items, {len(out)} rows")

print(f"\n{len(written)} item text table(s) written to {OUTDIR}")
for b, why in HELD.items():
    print(f"HELD (no item text): henderson_2023_lapanel_{b} -- {why}")
