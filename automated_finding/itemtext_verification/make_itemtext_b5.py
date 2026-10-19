"""Item text for the two batch-B deposits whose own labels carry stems AND anchors.

Both are `data_labels`: the SPSS variable label is the stem and the value labels are
the options, so the item-to-text tie is the source file's, not a reconstruction.

  19951727 -> hung_2026c_*               English throughout. Treated as an ENGLISH
                                         administration, so `language` and the
                                         `_translated` columns are omitted entirely
                                         (itemtext_standard: left out rather than
                                         emitted empty). Reasoning is in the
                                         provenance note.
  7011528  -> estevespairazaman_2022_*   Spanish administration (Peru; the deposit
                                         also ships Spanish CSVs), and the authors
                                         supplied their own file named "SPSS DATA 1
                                         ENGLISH VERSION.sav". The administered
                                         Spanish wording is NOT in the deposit -- the
                                         Spanish CSVs carry only short codes -- so
                                         this is the standard's fallback: English in
                                         the base fields, `_translated` empty,
                                         `language=Spanish`, and
                                         text_source=translated_substitute.

Source typos are kept verbatim ("activitywas", "fifinished"), following
xue_2025_academic_procrastination.

Written to automated_finding/itemtext_output/<table>__items.csv. Gated afterwards by
normalize_nulls.R -> validate_items.R --resp-csv -> audit_batch.R, plus irw-validate.
"""
import csv
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
RAW = REPO_ROOT / "automated_finding" / "runs" / "b5_raw"
RESP = REPO_ROOT / "automated_finding" / "irw_output"
OUT = REPO_ROOT / "automated_finding" / "itemtext_output"

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

JOBS = [
    # (sav path, {table: (instrument, [item codes])}, language or None)
    (RAW / "19951727" / "506.sav", {
        "hung_2026c_cognitive_load": (
            "Cognitive load (intrinsic, extraneous and germane load items as "
            "administered by Hung 2026)",
            ["IL1", "IL2", "IL3", "EL4", "EL5", "EL6", "GL7", "GL8", "GL9", "GL10"]),
        "hung_2026c_teacher_support": (
            "Teacher support items as administered by Hung 2026",
            ["TS1", "TS2", "TS4"]),
        "hung_2026c_procrastination": (
            "Academic procrastination items as administered by Hung 2026",
            ["APP1", "APP2", "APP4", "APP9", "AP3R", "AP5R", "AP6R"]),
        "hung_2026c_academic_self_efficacy": (
            "Academic self-efficacy items as administered by Hung 2026",
            ["ASE1", "ASE2", "ASE3", "ASE4", "ASE5", "ASE6", "ASE7", "ASE8"]),
    }, None),
    (RAW / "7011528" / "SPSS DATA 1 ENGLISH VERSION.sav", {
        "estevespairazaman_2022_anxiety_symptoms": (
            "COVID-19 anxiety symptom items (Esteves Pairazaman et al. 2022)",
            [f"P{i}" for i in range(1, 10)]),
        "estevespairazaman_2022_self_medication": (
            "Self-medication behaviour items (Esteves Pairazaman et al. 2022)",
            [f"S{i}" for i in range(1, 14)]),
    }, "Spanish"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for sav, tables, language in JOBS:
        df, meta = pyreadstat.read_sav(str(sav), apply_value_formats=False)
        labels = meta.column_names_to_labels or {}
        vlabels = meta.variable_value_labels or {}
        for table, (instrument, items) in tables.items():
            resp_csv = RESP / f"{table}.csv"
            assert resp_csv.exists(), f"{table}: response CSV not staged yet"
            live = pd.read_csv(resp_csv)
            live_items = set(live["item"].astype(str))
            live_resp = set(live["resp"].astype(int))
            assert live_items == set(items), (
                f"{table}: item set mismatch\n  only in response table: "
                f"{sorted(live_items - set(items))}\n  only here: "
                f"{sorted(set(items) - live_items)}")

            rows = []
            for it in items:
                stem = (labels.get(it) or "").strip()
                assert stem and stem != it, (
                    f"{table}/{it}: variable label is empty or echoes the code")
                opts = vlabels.get(it) or {}
                assert opts, f"{table}/{it}: no value labels to build option_text"
                for val, otext in sorted(opts.items()):
                    v = int(val)
                    if v not in live_resp:
                        continue    # an anchor nobody in this table endorsed
                    r = {c: "" for c in COLS}
                    r.update(table=table, section_id=f"{table}_1", item=it,
                             instrument=instrument, item_text=stem,
                             option_text=str(otext).strip(), resp=v)
                    if language:
                        r["language"] = language
                    rows.append(r)

            # Every resp value present in the response table must have an option.
            covered = {r["resp"] for r in rows}
            assert covered == live_resp, (
                f"{table}: resp set mismatch -- response table has "
                f"{sorted(live_resp - covered)} with no option_text")

            use = [c for c in COLS
                   if language or c not in ("language", "instructions_translated",
                                            "section_prompt_translated",
                                            "item_text_translated",
                                            "option_text_translated")]
            dest = OUT / f"{table}__items.csv"
            with open(dest, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=use, quoting=csv.QUOTE_ALL,
                                   lineterminator="\n", extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)
            total += len(rows)
            print(f"{dest.name}: {len(rows)} rows, {len(items)} items x "
                  f"{len(rows)//len(items)} options"
                  + (f", language={language}" if language else ", English administration"))
    print(f"\n{total} item-text rows written")


if __name__ == "__main__":
    main()
