#!/usr/bin/env python3
"""Build item text for li_2023_self_efficacy and li_2023_social_support from
the article's Supporting Information workbook, whose item column HEADERS are
the stems.

The item code is parsed off the header's own leading number -- the same
derivation data/li_2023_achievement_motivation.py uses to name the items -- so
code and wording come from one string and cannot drift apart.

The administration was in Chinese and the deposit holds only the depositors'
own English rendering of the stems, so this is the ruled fallback: English in
the base fields, `language=Chinese`, the `_translated` fields empty, and
`text_source=translated_substitute` with a `translation_source` in provenance.

li_2023_achievement_motivation is deliberately NOT built here: the Achievement
Motives Scale is registered `hold` (no grant located), so its stems do not
ship even though they are in the same file.

Usage: make_itemtext_li_2023.py <Table_1 ... .xlsx> <irw_output dir> <out dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

SRC, RESP_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])

BLOCKS = {
    "li_2023_self_efficacy": dict(
        marker="General self-efficacy", n=10, prefix="gse",
        instrument="General Self-Efficacy Scale (GSE), Schwarzer & Jerusalem "
                   "(1995), Chinese version"),
    "li_2023_social_support": dict(
        marker="Perceived social support", n=12, prefix="mspss",
        instrument="Multidimensional Scale of Perceived Social Support "
                   "(MSPSS), Zimet et al. (1988), Chinese version"),
}
# Every block in this workbook, needed to find where each one ends.
ALL_MARKERS = ["General self-efficacy", "Achievement motivation",
               "Perceived social support"]


def item_number(header: str) -> int:
    h = header.split("—")[-1].strip()
    m = re.match(r"(\d+)\s*[.,]", h)
    assert m, f"no leading item number in {header!r}"
    return int(m.group(1))


def item_stem(header: str) -> str:
    """The header with the block name and the leading item number stripped;
    the wording itself is verbatim."""
    h = header.split("—")[-1].strip()
    h = re.sub(r"^\d+\s*[.,]\s*", "", h)
    # One header carries a stray trailing variable tag in the source.
    h = re.sub(r"\.S10$", ".", h)
    return " ".join(h.split())


def main() -> None:
    cols = list(pd.read_excel(SRC, sheet_name="Sheet1", nrows=0).columns)
    starts = {}
    for marker in ALL_MARKERS:
        hits = [c for c in cols if c.startswith(marker)]
        assert len(hits) == 1, (marker, hits)
        starts[marker] = cols.index(hits[0])
    order = sorted(starts.items(), key=lambda kv: kv[1])
    bounds = {m: (s, order[i + 1][1] if i + 1 < len(order) else len(cols))
              for i, (m, s) in enumerate(order)}

    for table, spec in BLOCKS.items():
        start, end = bounds[spec["marker"]]
        bcols = cols[start:end]
        assert len(bcols) == spec["n"], (table, len(bcols))
        nums = [item_number(c) for c in bcols]
        assert nums == list(range(1, spec["n"] + 1)), (table, nums)

        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        values = sorted(resp["resp"].unique())

        rows = []
        for header, k in zip(bcols, nums):
            item = f"{spec['prefix']}_{k}"
            text = item_stem(header)
            assert text, header
            for v in values:
                rows.append({
                    "table": table,
                    "section_id": f"{table}_1",
                    "item": item,
                    "instrument": spec["instrument"],
                    "language": "Chinese",
                    "instructions": "",
                    "section_prompt": "",
                    "item_text": text,
                    "correct_response": "",
                    # The deposit states no anchor labels for either scale, so
                    # the option text is left blank rather than invented.
                    "option_text": "",
                    "resp": v,
                    "instructions_translated": "",
                    "section_prompt_translated": "",
                    "item_text_translated": "",
                    "option_text_translated": "",
                })
        out = pd.DataFrame(rows)
        assert set(out["item"]) == set(resp["item"].unique()), table
        assert set(out["resp"]) == set(resp["resp"].unique()), table
        assert out["item_text"].nunique() == spec["n"], "two items share a stem"
        path = OUT / f"{table}__items.csv"
        out.to_csv(path, index=False)
        print(f"{path.name}: {len(out)} rows, {spec['n']} items x "
              f"{len(values)} options")


if __name__ == "__main__":
    main()
