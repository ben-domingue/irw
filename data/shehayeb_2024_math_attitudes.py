#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/5cgmcxmp3y
# DOI: 10.17632/5cgmcxmp3y
#   Shehayeb, Sanaa; Annouti, Mohammad (2024). "Data collection of teachers'
#   practices through social and cognitive interaction, content of
#   mathematics." Mendeley Data.
# Data: Data entry.sav (450 rows x 35 columns; school students reporting on
#       their own mathematics anxiety and on their mathematics teacher).
# License: CC BY 4.0 (Mendeley public API, data_licence.short_name).
#
# Item text: SHIPPED. Both label levels checked. Every one of the 35
#   variable labels is the full English stem, and every item carries value
#   labels giving all five anchors (1 = Strongly Disagree ... 5 = Strongly
#   Agree) -- so unlike most deposits this one supplies option_text too.
#   The item codes are the source's own Q<n>A / Q<n>B headers.
#
# Tables (item codes are the source column names):
#   shehayeb_2024_math_anxiety   Q1A-Q13A, 1-5. The student's own security,
#       understanding and anxiety about mathematics.
#   shehayeb_2024_math_teacher   Q1B-Q22B, 1-5. The student's report on the
#       mathematics teacher's practices and manner.
#   Two tables rather than one: the A block measures the respondent and the
#       B block measures a third party (the teacher), which are different
#       constructs on the same 1-5 format.
#
# Two single-cell data-entry errors, dropped rather than kept or allowed to
#   widen the scale -- checked per item, not on the merged range:
#     Q4A one response of 6, against 448 in 1-5
#     Q9A one response of 24, against 448 in 1-5
#   Both items' own value labels define exactly five points, so these are
#   typos in two cells, not evidence of a wider scale. The cells are
#   dropped; the items ship. 9 cells are already blank in the source.
# id: row index (the source has no respondent identifier).
# Covariates: none -- the deposit carries no demographics at all.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/5cgmcxmp3y"
FILENAME = "Data entry.sav"

A = [f"Q{i}A" for i in range(1, 14)]
B = [f"Q{i}B" for i in range(1, 23)]
TABLES = {
    "shehayeb_2024_math_anxiety": (A, "Mathematics anxiety and "
                                      "self-perception items (study-authored)"),
    "shehayeb_2024_math_teacher": (B, "Mathematics teacher practices and "
                                      "manner items (study-authored)"),
}
ALLOWED = {1, 2, 3, 4, 5}


def fetch():
    meta = requests.get(API, headers=UA, timeout=60).json()
    lic = (meta.get("data_licence") or {}).get("short_name")
    assert lic == "CC BY 4.0", lic
    url = next(f["content_details"]["download_url"] for f in meta["files"]
               if f["filename"] == FILENAME)
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    p = OUT_DIR.parent / "runs" / "_shehayeb.sav"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(r.content)
    df, m = pyreadstat.read_sav(str(p), apply_value_formats=False)
    p.unlink()
    return df, m


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, m = fetch()
    assert d.shape == (450, 35), d.shape

    items = A + B
    assert set(d.columns) == set(items), set(d.columns) ^ set(items)
    print(f"dropped 0 column(s): all {len(items)} are items, no "
          f"demographics or composites in this deposit")

    # Every item must carry five anchors; that is what makes the two
    # out-of-range cells typos rather than a wider scale.
    for it in items:
        vl = m.variable_value_labels.get(it) or {}
        assert set(vl) == {1.0, 2.0, 3.0, 4.0, 5.0}, (it, vl)

    d.insert(0, "id", range(1, len(d) + 1))

    names = []
    for table, (its, instrument) in TABLES.items():
        long = d.melt(id_vars=["id"], value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        before = len(long)
        long = long[long["resp"].isin(ALLOWED)]
        dropped = before - len(long)
        if dropped:
            print(f"  {table}: dropped {dropped} cell(s) outside 1-5 "
                  f"(single-cell data-entry errors; each item's own value "
                  f"labels define exactly five points)")
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(its) > 1
        pv = {i: ALLOWED for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        rows = []
        for it in its:
            stem = " ".join(str(m.column_names_to_labels[it]).split())
            assert stem
            anchors = m.variable_value_labels[it]
            for r in sorted(ALLOWED):
                rows.append({
                    "table": table, "section_id": f"{table}_1", "item": it,
                    "instrument": instrument, "language": "",
                    "instructions": "", "section_prompt": "",
                    "item_text": stem, "correct_response": "",
                    "option_text": anchors[float(r)], "resp": r,
                })
        it_df = pd.DataFrame(rows)
        assert set(it_df["item"]) == set(its)
        assert set(it_df["resp"]) == ALLOWED
        assert it_df["option_text"].ne("").all()
        tp = TEXT_DIR / f"{table}__items.csv"
        it_df.to_csv(tp, index=False)
        print(f"  {tp.name}: {len(it_df)} rows, "
              f"{it_df['item'].nunique()} items x {len(ALLOWED)} options "
              f"(anchors from the source's value labels)")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
