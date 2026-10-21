#!/usr/bin/env python3
"""Build the three huebner_2021_weightlifting_* item text tables from the
deposit's own codebook (wldat_dictionary.xlsx).

The codebook's `Item` column NAMES each response-table column, so the
item-to-text tie is given by the source rather than inferred from order: this
script joins on that name and asserts the join is total in both directions.

Usage: make_itemtext_huebner_2021.py <wldat_dictionary.xlsx> <irw_output dir> <out dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DICT, RESP_DIR, OUT = (Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

INSTRUMENTS = {
    "huebner_2021_weightlifting_attraction": (
        "Masters weightlifting survey (Huebner 2021): attractions",
        "The following aspects attract me to Masters weightlifting"),
    "huebner_2021_weightlifting_barriers": (
        "Masters weightlifting survey (Huebner 2021): barriers",
        "The following aspects have been barriers / obstacles to my "
        "weightlifting."),
    "huebner_2021_weightlifting_pandemic": (
        "Masters weightlifting survey (Huebner 2021): the pandemic",
        "How much do you agree with the following statements"),
}
# The codebook's own five labelled scale points, verbatim apart from its typo
# "neither agree not disagree", kept as the source spells it.
OPTIONS = {1: "strongly agree", 2: "agree", 3: "neither agree not disagree",
           4: "disagree", 5: "strongly disagree"}


def stem(question: str, prompt: str) -> str:
    """The per-item wording: the codebook's question split from the block's
    shared stem at the first ' - '. The left side is asserted to BE the shared
    stem, so a row belonging to another block cannot slip through.

    The codebook misspells the pandemic block's stem as "withthe" on one row
    (pan_alone); that one typo is tolerated in the match and the item wording
    itself is taken verbatim."""
    q = " ".join(str(question).split())
    head, sep, tail = q.partition(" - ")
    assert sep, f"no ' - ' separator in {q!r}"
    norm = lambda t: " ".join(t.replace("withthe", "with the").split()).lower()
    assert norm(head) == norm(prompt), (head, prompt)
    return tail.strip()


def main() -> None:
    cb = pd.read_excel(DICT)
    cb["Item"] = cb["Item"].astype(str).str.strip()
    by_item = dict(zip(cb["Item"], cb["Question/Variable"]))

    for table, (instrument, prompt) in INSTRUMENTS.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = sorted(resp["item"].unique())
        values = sorted(resp["resp"].unique())
        assert set(values) <= set(OPTIONS), values
        missing = [i for i in items if i not in by_item]
        assert not missing, f"{table}: codebook has no row for {missing}"

        rows = []
        for item in items:
            text = stem(by_item[item], prompt)
            assert text, (table, item)
            for v in values:
                rows.append({
                    "table": table,
                    "section_id": f"{table}_1",
                    "item": item,
                    "instrument": instrument,
                    "instructions": prompt,
                    "section_prompt": "",
                    "item_text": text,
                    "correct_response": "",
                    "option_text": OPTIONS[v],
                    "resp": v,
                })
        out = pd.DataFrame(rows)
        # The join key must match the response table exactly, both ways.
        assert set(out["item"]) == set(resp["item"].unique())
        assert set(out["resp"]) == set(resp["resp"].unique())
        assert out["item_text"].nunique() == len(items), "two items share a stem"
        path = OUT / f"{table}__items.csv"
        out.to_csv(path, index=False)
        print(f"{path.name}: {len(out)} rows, {len(items)} items x "
              f"{len(values)} options")


if __name__ == "__main__":
    main()
