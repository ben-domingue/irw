"""German CEFSA validation: anomalous experiences, altered sense of self, and
the full criterion battery that accompanied it.

Source: https://zenodo.org/records/14774618
DOI: 10.5281/zenodo.14774618
Data: cefsa_1.csv (130 x 41) and cefsa_2.csv (243 x 141)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped. Both files are bare CSVs with no label level at all --
  the column names are the only metadata, and they are construct-and-position
  codes (an_exp_self_1 .. gse_3). No codebook or questionnaire is deposited.
  The CEFSA wording is in Heekerens's validation paper; PHQ-9, GAD-7, DES,
  BFI-10, LPFS-BF and GSE wording is in their own published sources.

TWO SAMPLES, MERGED WHERE THEY OVERLAP. cefsa_1 and cefsa_2 are independent
samples: they share 39 columns and **zero** response vectors. The CEFSA blocks
themselves (`an_exp_*`, `alt_sense_*`) were administered in both, so those two
tables merge the samples on `cov_study` with sample 2's ids offset past sample
1's observed max. Everything else exists only in cefsa_2 and ships from there.

cefsa_1 spells two columns `an_exp_emot_1_r` and `an_exp_emot_5r` where cefsa_2
has `an_exp_emot_1` and `an_exp_emot_5`. They are NOT reverse-scored relative
to cefsa_2 -- the means are 0.86 vs 0.87 and 0.31 vs 0.50, same direction and
magnitude, where a reversal on this 0-4 scale would put sample 1 near 3.1. So
the suffix is naming noise and the columns are merged under the cefsa_2 name.

SCALE RANGES ARE ASSERTED PER TABLE, NOT INHERITED. This deposit is the reason
why: its PHQ-9 is scored **1-4**, not the 0-3 that the PHQ-9 almost always
uses, while the GAD-7 beside it IS 0-3. Nothing but a per-table permitted set
catches that.

The DES block is the DES-II percentage format: 0-100 in steps of 10. Kept as
deposited -- `datastandard.md` admits a continuous/ordinal response, and
rescaling it would invent a scale the source does not use.

The eight trauma-exposure columns are a check-all-that-apply exposure
checklist, each a genuine 0/1 item, so they ship as one 8-item table (two
response categories belong in core, not nominal).

RIGHTS. PHQ-9 and GAD-7 both carry the register verdict `ship` (the "PHQ and
GAD screener family" row). None of DES, BFI-10, LPFS-BF, CEQ, PAQ or GSE
matches any register row. No item text is shipped for any of them, so no
instrument wording is exposed; register-row requests for DES, BFI-10 and
LPFS-BF are noted in TODO.
"""
import os

import numpy as np
import pandas as pd

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAWDIR = os.environ.get(
    "HEEKERENS_RAWDIR",
    str(_RAW_BASE / "zenodo.14774618"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

RENAME_S1 = {"an_exp_emot_1_r": "an_exp_emot_1",
             "an_exp_emot_5r": "an_exp_emot_5"}

AN_EXP = ([f"an_exp_self_{i}" for i in range(1, 6)]
          + [f"an_exp_body_{i}" for i in range(1, 6)]
          + [f"an_exp_emot_{i}" for i in range(1, 6)])
ALT_SENSE = ([f"alt_sense_fam_{i}" for i in range(1, 6)]
             + [f"alt_sense_connect_{i}" for i in range(1, 6)]
             + [f"alt_sense_agency_{i}" for i in range(1, 6)]
             + [f"alt_sense_real_{i}" for i in range(1, 6)])
DES = ["des_6", "des_7", "des_10", "des_11", "des_16", "des_18", "des_20",
       "des_21", "des_23", "des_25", "des_26", "des_29", "des_32", "des_34",
       "des_35", "des_38", "des_39", "des_40", "des_41", "des_42"]
TRAUMA = ["life_threatening_illness", "physical_assault", "sexual_assault",
          "combat_exposure_war_zone", "child_abuse", "serious_accident",
          "torture_captivity", "natural_disaster"]
BFI10 = [f"{t}_{i}" for t in ("extraversion", "agreeableness",
                              "conscientiousness", "neuroticism", "openness")
         for i in (1, 2)]
LPFS = ([f"lpfs_self_{i}" for i in range(1, 7)]
        + [f"lpfs_inter_{i}" for i in range(1, 7)])
CEQ = [f"ceq_{i}" for i in range(1, 26)]
PAQ = [f"paq_{i}" for i in range(1, 7)]
GSE = [f"gse_{i}" for i in range(1, 4)]

BOTH = {"anomalous_experiences": (AN_EXP, set(range(0, 5))),
        "altered_sense_of_self": (ALT_SENSE, set(range(0, 5)))}
S2_ONLY = {"des": (DES, set(range(0, 101, 10))),
           "trauma_exposure": (TRAUMA, {0, 1}),
           "gad7": ([f"gad_{i}" for i in range(1, 8)], {0, 1, 2, 3}),
           "phq9": ([f"phq_{i}" for i in range(1, 10)], {1, 2, 3, 4}),
           "bfi10": (BFI10, set(range(1, 8))),
           "lpfs_bf": (LPFS, {1, 2, 3, 4}),
           "ceq": (CEQ, {0, 1}),
           "paq": (PAQ, set(range(1, 8))),
           "gse": (GSE, set(range(1, 6)))}
COVS = {"age": "cov_age", "gender": "cov_gender", "country": "cov_country",
        "education": "cov_education"}


def emit(long, table, scale, written, covs):
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"].unique()) - scale
        assert not bad, f"{table}/{it}: {sorted(bad)} outside {sorted(scale)}"
    assert long["id"].nunique() >= 100, (table, long["id"].nunique())
    assert long["item"].nunique() > 1, table
    assert table not in written, table
    written.add(table)
    # The shared checks, which the script's own assertions are not
    # (irw_validate.contract `no_validator`). Fails block; the
    # warnings here are legitimate and are printed.
    _checks = run_qc(long)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, _fails
    for _c in _checks:
        if _c.status == "warn":
            print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
    long[["id", "item", "resp"] + covs].to_csv(
        os.path.join(OUT, f"{table}.csv"), index=False)
    print(f"  {table}: {long['id'].nunique()} ids x "
          f"{long['item'].nunique()} items = {len(long)} responses")


def main():
    s1 = pd.read_csv(os.path.join(RAWDIR, "cefsa_1.csv")).rename(
        columns=RENAME_S1)
    s2 = pd.read_csv(os.path.join(RAWDIR, "cefsa_2.csv"))
    print(f"cefsa_1 {s1.shape}  cefsa_2 {s2.shape}")

    # Books: every cefsa_2 column is an item of a shipped table or a covariate.
    used = set(COVS) | {"country_mother", "country_father"}
    for cols, _ in list(BOTH.values()) + list(S2_ONLY.values()):
        used |= set(cols)
    print("  skip 'country_mother','country_father': parental origin, kept out of the covariate set as it is not a respondent attribute")
    unaccounted = [c for c in s2.columns if c not in used]
    for c in unaccounted:
        print(f"  UNACCOUNTED {c!r}")
    assert not unaccounted, f"{len(unaccounted)} cefsa_2 column(s) unaccounted"

    s1 = s1.reset_index(drop=True)
    s2 = s2.reset_index(drop=True)
    s1["id"] = s1.index + 1
    offset = int(s1["id"].max())
    s2["id"] = s2.index + 1 + offset
    print(f"  sample 2 ids offset past sample 1's observed max ({offset})")
    s1["cov_study"] = "cefsa_1"
    s2["cov_study"] = "cefsa_2"

    os.makedirs(OUT, exist_ok=True)
    written = set()

    for name, (cols, scale) in BOTH.items():
        parts = []
        for s in (s1, s2):
            missing = [c for c in cols if c not in s.columns]
            assert not missing, f"{name}: missing {missing}"
            parts.append(s.melt(id_vars=["id", "cov_study"], value_vars=cols,
                                var_name="item", value_name="resp"))
        emit(pd.concat(parts, ignore_index=True), f"heekerens_2025_{name}",
             scale, written, ["cov_study"])

    covs = list(COVS.values())
    s2r = s2.rename(columns=COVS)
    for name, (cols, scale) in S2_ONLY.items():
        missing = [c for c in cols if c not in s2r.columns]
        assert not missing, f"{name}: missing {missing}"
        long = s2r.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
        emit(long, f"heekerens_2025_{name}", scale, written, covs)


if __name__ == "__main__":
    main()
