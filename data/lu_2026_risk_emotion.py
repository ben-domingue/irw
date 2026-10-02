#!/usr/bin/env python3
# Source: https://osf.io/t5kz9/
# DOI: 10.1037/pspp0000586
#   Lu, Efendic & Feldman (2026). "Associations of fear, anger, happiness, and
#   hope with risk judgments: Revisiting appraisal-tendency framework with a
#   replication and extensions registered report of Lerner and Keltner
#   (2001)." Journal of Personality and Social Psychology 131(4).
# Data: OSF t5kz9, "PCIRR Stage 2/Data and code/RRR-Lerner-Keltner-2001-WITH-
#       order.sav" (Qualtrics export, 826 rows x 296 columns; US MTurk sample,
#       June 2022). Item wording from CODEBOOK.csv in the same folder and the
#       .sav variable/value labels.
# License: CC BY 4.0 (OSF node licence, api.osf.io/v2/nodes/t5kz9, public).
#
# Item text: not shipped. The wording is cheap -- stems in the .sav variable
#   labels and CODEBOOK.csv's "Question Choice" column, options in the .sav
#   value labels (both levels checked: present on every item) -- but rights
#   hold it back: STAI is `block` in itemtext/instrument_rights_register.csv
#   (Mind Garden), Spielberger Trait-Anger is the PAR-sold STAXI, and the
#   Mood Survey, FSS-II, Adult Hope Scale and Weinstein (1980) event list are
#   not in the register yet. Needs a ruling per instrument, not extraction.
#
# Tables (one per instrument; item codes are the source column names):
# (Instrument names from the Qualtrics .pdf block headers.)
#   lu_2026_anger       10 items, 1-4  Spielberger Trait-Anger Scale
#   lu_2026_fss         14 items, 1-7  Fear Survey Schedule-II (14 items)
#   lu_2026_stai        20 items, 1-4  Spielberger Trait-Anxiety (STAI-T)
#   lu_2026_happiness   16 items, 1-6  Underwood & Froming Mood Survey.
#                        irw-validate's rights_register warns that the
#                        happiness_* codes match the SHS row; that is a
#                        code-pattern hit only -- this is not the 4-item SHS
#                        and the codes are not item wording.
#   lu_2026_hope         8 items, 1-8  Snyder Adult Hope Scale (scored items)
#   lu_2026_optimism    23 items, -4..4 Weinstein (1980) comparative risk
#                        judgments of life
#                        events ("your chances relative to the average ...";
#                        -4 = very much less likely, 0 = equal, 4 = very much
#                        more likely). These are the paper's risk-judgment
#                        DV, answered on one bipolar scale per event.
#   lu_2026_certainty   23 items, 1-6  how certain/predictable each of the
#                        same 23 events seems (appraisal extension)
#   lu_2026_control     23 items, 1-6  how controllable each event seems
#   Certainty and control were randomly split: every respondent answered one
#   of the two, never both (asserted), so they are two tables, ~390 each.
#   The same event wording appears in all three event tables, so the three
#   use distinct item codes (optimism__k, certain_k, control_k) as in source.
#
# Dropped as items:
#   - Five embedded attention checks, one per trait block ("Check: Please
#     answer 'Almost never'" etc.): anger_11, fear_FSS_II_17, fear_STAI__21,
#     happiness_18, hope_13. Their pass count (0-5) is carried as
#     cov_attn_checks_passed; the paper does not exclude on them.
#   - Hope Scale fillers hope_3, hope_5, hope_7, hope_11 (Snyder's AHS has 4
#     filler items; the paper's analysis .Rmd keeps only hope_1,2,4,6,8,9,10,
#     12). Fillers measure nothing on the hope construct.
#   - gain_frame_ / loss_frame_ (Asian-disease pair): two single items under
#     different framings, not a scale.
#   - All 96 *_DO_* display-order columns (Qualtrics randomisation
#     bookkeeping; not responses).
# Responses are unreversed. The paper reverses STAI 1,3,6,7,10,13,14,16,19 and
#   happiness 1,2,6,8,11,12,13,15 in analysis; the .sav holds the raw codes.
#
# Respondents: all 781 rows with trait-block data are kept (45 rows of the 826
#   stopped before the first block). The analysis .Rmd's exclusion rule
#   (Duration > 0, consent, both outline checks == 1, native US English
#   speaker, age >= 18, funnel_pay >= 0) is NOT applied; it is carried as
#   cov_analysis_sample (1 = retained in the paper's analysis; 780 of 781).
#   IRW keeps everyone and lets the user apply the authors' rule.
# id: row index. assignmentId / hitId (MTurk platform IDs) are dropped per the
#   2026-09-20 platform-ID ruling. Recipient name/email, PROLIFIC_PID and
#   location fields are empty in every row (checked by non-blank count). No
#   IP or GPS columns exist. Free-text columns (country, funnel comments,
#   *_TEXT) are not carried.
# Covariates: cov_age, cov_gender (1 male, 2 female, 3 other, 4 rather not
#   disclose), cov_soc_class (1 lower .. 6 upper), cov_married (1 not married,
#   2 married/engaged), cov_parent (1 yes, 2 no), cov_serious (self-rated
#   seriousness 1-5), cov_attn_checks_passed, cov_analysis_sample.

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://osf.io/download/hmn4u/"

CHECKS = {"anger_11": 1, "fear_FSS_II_17": 1, "fear_STAI__21": 1,
          "happiness_18": 1, "hope_13": 1}
HOPE_FILLERS = ["hope_3", "hope_5", "hope_7", "hope_11"]

TABLES = {
    "lu_2026_anger": ([f"anger_{i}" for i in range(1, 11)], range(1, 5)),
    "lu_2026_fss": ([f"fear_FSS_II_{i}" for i in range(1, 15)], range(1, 8)),
    "lu_2026_stai": ([f"fear_STAI__{i}" for i in range(1, 21)], range(1, 5)),
    "lu_2026_happiness": ([f"happiness_{i}" for i in range(1, 17)],
                          range(1, 7)),
    "lu_2026_hope": ([f"hope_{i}" for i in (1, 2, 4, 6, 8, 9, 10, 12)],
                     range(1, 9)),
    "lu_2026_optimism": ([f"optimism__{i}" for i in range(1, 24)],
                         range(-4, 5)),
    "lu_2026_certainty": ([f"certain_{i}" for i in range(1, 24)], range(1, 7)),
    "lu_2026_control": ([f"control_{i}" for i in range(1, 24)], range(1, 7)),
}

COVS = {"age": "cov_age", "gender": "cov_gender", "soc_class": "cov_soc_class",
        "marital_": "cov_married", "parent_": "cov_parent",
        "serious": "cov_serious"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, _ = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (826, 296), d.shape

    # Nothing identifying may be present beyond the MTurk ids we drop.
    for c in ["RecipientLastName", "RecipientFirstName", "RecipientEmail",
              "PROLIFIC_PID", "CountryCode", "CountryName"]:
        assert (d[c].astype(str).str.strip() != "").sum() == 0, c
    assert not any(c.lower().startswith(("ipaddress", "location"))
                   for c in d.columns)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    keep = (d["Duration__in_seconds_"] > 0) & (d["consentagree_1"] == 1) \
        & (d["outline1"] == 1) & (d["outline2"] == 1) & (d["native"] == 1) \
        & (d["age"] >= 18) & (d["funnel_pay"] >= 0)
    d["cov_analysis_sample"] = keep.astype(int)
    d["cov_attn_checks_passed"] = sum((d[c] == v).astype(int)
                                      for c, v in CHECKS.items())
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values()) + ["cov_attn_checks_passed",
                                      "cov_analysis_sample"]

    # Rows that never reached the trait blocks carry no responses at all.
    d = d[d["anger_1"].notna()].reset_index(drop=True)
    assert len(d) == 781 and d["cov_analysis_sample"].sum() == 780
    assert not (d["certain_1"].notna() & d["control_1"].notna()).any()

    # Balance the books: every response-bearing column is shipped or named.
    shipped = {c for items, _ in TABLES.values() for c in items}
    dropped = set(CHECKS) | set(HOPE_FILLERS) | {"gain_frame_", "loss_frame_"}
    blocks = ("anger_", "fear_", "happiness_", "hope_", "optimism_",
              "certain_", "control_")
    resp_cols = {c for c in d.columns if c.startswith(blocks)
                 and "_DO_" not in c}
    assert resp_cols - shipped - dropped == set(), resp_cols - shipped - dropped

    names = []
    for table, (items, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        # Per-item check against the documented response set.
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in ["cov_age", "cov_gender", "cov_soc_class", "cov_married",
                  "cov_parent", "cov_serious"]:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(items) > 1
        pv = {i: set(allowed) for i in items}
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
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
