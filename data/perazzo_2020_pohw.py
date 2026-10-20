#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/jm85b93kzs
# DOI: 10.17632/jm85b93kzs
#   Perazzo, M. (2020). Dataset - Brazilian version of Positive Oral Health
#   and Well-Being (B-POHW): cross-cultural adaptation and psychometric
#   analysis [Dataset]. Mendeley Data, v1.
# Data: "Dataset_B-POHW.sav" -- 209 respondents, the cross-cultural
#   adaptation sample for the Brazilian Portuguese B-POHW.
# License: CC BY 4.0 (verified via the DOI's DataCite record, which carries
#   rightsIdentifier cc-by-4.0 and the CC BY 4.0 legalcode URI, 2026-10-20).
#
# Item text: NOT shipped, and the two label levels differ -- which level says
#   what matters here, so both are named rather than summarised:
#     - VARIABLE labels (the stems): ABSENT for all 19 shipped items.
#       pyreadstat's column_names_to_labels is None for every one of them.
#       The only labels in the file sit on the four all-blank section-header
#       columns ("First application" / "Second application"). So the file
#       gives bare codes POHW1..POHW15 and PWell_Being1..4 and no wording.
#     - VALUE labels (the response options): PRESENT for all 19, and for all
#       20 retest items too. Every item carries the same four Portuguese
#       anchors, 0 = "Discordo totalmente", 1 = "Discordo parcialmente",
#       2 = "Concordo parcialmente", 3 = "Concordo totalmente". This is the
#       administered wording, not a translation of ours.
#   So the options are in hand and the stems are not. That is precisely the
#   option-only case that is already ruled out: option_text must not ship
#   alone when the stems are one hop away, and here they are -- they are
#   printed in the published B-POHW adaptation paper this deposit supports.
#   Shipping the anchors by themselves would produce an item text table that
#   joins to every response and says nothing about what was asked.
#   The stems additionally need the usual two rulings when someone does fetch
#   them, because B-POHW is a Brazilian Portuguese adaptation of a
#   third-party instrument (the English POHW): the original's terms and the
#   adaptation's. Recorded so a later pass starts from an answer rather than
#   re-deriving this one.
#   NOTE: an earlier draft of this header claimed both levels were empty,
#   written from the variable-label level alone. The assertion below is what
#   caught it, and it is kept deliberately -- it is the estevez_2021 (#1770)
#   failure shape, where 82 items were skipped on "no value labels" and the
#   file carried value labels for all of them.
#
# ONE table. The instrument's own name is "Positive Oral Health AND
# WELL-BEING", so the 15 oral-health items and the 4 well-being items are
# two blocks of one questionnaire, not two instruments: they were
# administered together, on one identical 0-3 response scale, to the same
# 209 respondents. They are kept in one file and the source's own block
# prefixes are preserved in the item codes, so the structure is recoverable
# without splitting. The deposit does report a separate POHW_total and
# Well_Being_total, which is why this decision is recorded rather than
# assumed; if the published paper turns out to treat them as two distinct
# scales, this table should be split and nothing else about it changes.
#
# NOT shipped -- the retest (second application), deliberately:
#   The file carries a second administration, RPOHW1..RPOHW16 and
#   RBem_estar1..4, answered by only 54 of the 209 respondents. It is left
#   out for two independent reasons. First, 54 respondents is below the
#   N>=100 floor, so it cannot ship as its own table. Second, it cannot be
#   folded into this one as a `wave`, because the item correspondence is
#   unestablished: the retest block has SIXTEEN oral-health items where the
#   first application has fifteen, so RPOHW1..16 cannot be matched onto
#   POHW1..15 by position without guessing which item the extra one is. The
#   deposit documents neither the mapping nor the discrepancy. Matching them
#   by number would produce a plausible, silently wrong longitudinal file,
#   which is worse than no wave column at all.
#
# Dropped as composites, not responses: POHW_total, Well_Being_total,
#   RPOHW_TOTAL, RGood_feelings_TOTAL, RPositive_impact_TOTAL,
#   RWell_Being_TOTAL. Also dropped: POHW, PWell_Being, RPOHW and
#   RBem_estar, four columns that are entirely empty -- they are section
#   headers that survived the SPSS export, carrying a label and no data --
#   and Good_feelings / Positive_impact, likewise empty, which name the
#   POHW's two documented subscales.
#
# id: the file has NO identifier column of any kind, so `id` is the row
#   index (1..209), one row per respondent. This is the standard IRW
#   treatment and loses nothing: the rows are already de-identified and the
#   row order is the only link the deposit itself provides.
#
# Covariates: none. The deposit ships no demographics, no clinical variables
#   and no group indicator -- only the item blocks and their totals.
#
# PII: none, and there is nothing in the file that could be. Zero
#   string-dtype columns (screened with pd.api.types.is_string_dtype, never
#   dtype == object, with the denominator printed below); every column is a
#   numeric 0-3 item response or a numeric total. No identifier column, no
#   free-text field, no date.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "mendeley" / "jm85b93kzs"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI = "10.17632/jm85b93kzs"
FNAME = "Dataset_B-POHW.sav"
TABLE = "perazzo_2020_pohw"

ITEMS = ([f"POHW{i}" for i in range(1, 16)]
         + [f"PWell_Being{i}" for i in range(1, 5)])
SCALE = {0, 1, 2, 3}
N_RESP = 209


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
        from irw_batch_updated import resolve_data_files
        files, _lic, _ov = resolve_data_files(
            {"source": "mendeley", "doi": DOI,
             "url": f"https://data.mendeley.com/datasets/{DOI.split('/')[1]}",
             "title": ""})
        url = next(u for u, name, _sz in files if name == FNAME)
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()))
    assert len(df) == N_RESP, len(df)
    missing = [c for c in ITEMS if c not in df.columns]
    assert not missing, missing

    # PII screen -- print the denominator so an empty selection is visible.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] columns examined for PII: {len(df.columns)} total, "
          f"{len(text_cols)} of them string-dtype")
    assert len(df.columns) > 0, "PII screen selected no columns"

    # Re-check the item-text verdict on every run, per label level, so the
    # header cannot drift from the file. Stems absent, anchors present.
    assert all(meta.column_names_to_labels.get(c) is None for c in ITEMS), \
        "an item gained a variable label (a stem); revisit the item-text verdict"
    anchors = {0.0: "Discordo totalmente", 1.0: "Discordo parcialmente",
               2.0: "Concordo parcialmente", 3.0: "Concordo totalmente"}
    for c in ITEMS:
        assert meta.variable_value_labels.get(c) == anchors, \
            f"value labels for {c} are not the expected four anchors"
    print(f"[itemtext] stems: absent for all {len(ITEMS)} items; "
          f"response anchors: present for all {len(ITEMS)} "
          f"(0-3, Portuguese). Option-only, so not shipped.")

    # The retest exists but is deliberately not shipped (see header).
    retest = [f"RPOHW{i}" for i in range(1, 17)]
    assert all(c in df.columns for c in retest), "retest block changed shape"
    n_retest = int(df[retest].notna().any(axis=1).sum())
    print(f"[note] retest block present for {n_retest} respondents with "
          f"{len(retest)} items vs {15} in the first application; not shipped")

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    t = (df[["id", *ITEMS]]
         .melt(id_vars=["id"], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the observed 0-3 scale: {bad}"

    t = t[["id", "item", "resp"]]
    assert not t.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert t["id"].nunique() == N_RESP, t["id"].nunique()
    assert t["item"].nunique() == len(ITEMS), t["item"].nunique()

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
