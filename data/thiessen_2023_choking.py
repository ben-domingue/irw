#!/usr/bin/env python3
# Source: https://zenodo.org/records/7552142
# DOI: 10.2174/18743501-v16-e230116-2022-75
#   Thiessen, B., Sullivan, P., Gammage, K., & Dithurbide, L. (2023). Choking
#   Susceptibility and the Big Five Personality Traits. The Open Psychology
#   Journal, 16, e187435012301130. (CC BY 4.0; read in full. Not linked from
#   the deposit; found by Crossref title search.)
#   Deposit: Thiessen, B. et al. (2023). Zenodo.
#   https://doi.org/10.5281/zenodo.7552142
# Data: P&CS - Full Dataset.sav (177 rows x 117 columns; Canadian university
#       students 18+, online Qualtrics survey). The paper's N is 177.
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: each item's variable
#   label is the Qualtrics block prompt followed by " - <full English stem>"
#   (e.g. "... - I'm always trying to figure myself out"), and value labels
#   carry the anchors (BFI, SAS, CSIA). So it is cheap by extraction, but
#   held for a rights call: BFI-10, the Self-Consciousness Scale, the Sport
#   Anxiety Scale and the CSIA have no rows in the rights register, and the
#   SAS/CSIA wording was altered for this study ("competition" ->
#   "performance situation", per the paper). The SCS value labels are
#   shifted (1 = "0" .. 5 = "4") relative to the stored 0-4 codes, so only
#   the paper's 0-4 statement should be used for SCS options.
#
# Tables (item codes are the source column names; ranges from the paper's
# Measures section, cross-checked with the value labels):
#   thiessen_2023_bfi10  BFI1-BFI10  BFI-10, 5-point (1 disagree strongly ..
#       5 agree strongly). Stored as answered (BFI1R/3R/4R/5_1R/7R are the
#       reversed copies, = 6 - x, asserted and dropped).
#   thiessen_2023_scs    SCS1-SCS23  Self-Consciousness Scale (Fenigstein et
#       al. 1975), 0 extremely uncharacteristic .. 4 extremely
#       characteristic. Stored as answered; SCS3R/9R/12R (= 4 - x) dropped.
#   thiessen_2023_sas    SAS1-SAS21  Sport Anxiety Scale (Smith et al. 1990),
#       1 not at all .. 4 very much so, reworded to general performance
#       situations.
#   thiessen_2023_csia   CSIA1-CSIA16  Coping Style Inventory for Athletes,
#       1 very untrue .. 5 very true.
#
# Dropped:
#   - *_1 columns (BFI2_1, BFI5_1, SCS15_1, SAS1_1, SAS4_1, SAS5_1, SAS17_1,
#     CSIA1_1, CSIA3_1, CSIA5_1, CSIA13_1): copies of the item with its
#     missing cells mean-filled ("MEAN(x,2)" in the variable label; the paper
#     says missing data were "filled using means of nearby points"). Each
#     equals its source item wherever that is present (asserted); the 13
#     filled cells are fractional or imputed, so the original items ship
#     with those cells missing. BFI5_1R is the reversed copy of BFI5_1.
#   - Reversed copies listed above; totals and subscales (BFI_O..BFI_N,
#     SCS_Pub, SCS_Pri, SCS_SocialA, SCS_Total, SAS_SomA, SAS_W, SAS_CD,
#     SAS_Total, CSIA_Avoid, CSIA_App, CSIA_Diff); the choking-susceptibility
#     classification intermediates CS_SC, CS_SAnxiety, CS_Cope, CS_Total,
#     CS1_SCS, CS1_SAS, CS1_CSIA. SCS_Total equals the sum of SCS1-23 with
#     SCS15_1 and the three R copies (asserted).
# id: row index. ParticipantID (1-227, unique) is a study sequence number
#   and is not shipped. The paper says e-mail addresses were deleted; none
#   are in the file, and there is no free text.
# Covariates: cov_gender (1 male, 2 female), cov_age (years),
#   cov_varsity_athlete (1 yes, 2 no), cov_choking_susceptible (0/1, the
#   paper's classification "CS").

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/7552142/files/"
       "P%26CS%20-%20Full%20Dataset.sav/content")

TABLES = {
    "thiessen_2023_bfi10": [f"BFI{i}" for i in range(1, 11)],
    "thiessen_2023_scs": [f"SCS{i}" for i in range(1, 24)],
    "thiessen_2023_sas": [f"SAS{i}" for i in range(1, 22)],
    "thiessen_2023_csia": [f"CSIA{i}" for i in range(1, 17)],
}
PERMITTED = {"thiessen_2023_bfi10": set(range(1, 6)),
             "thiessen_2023_scs": set(range(0, 5)),
             "thiessen_2023_sas": set(range(1, 5)),
             "thiessen_2023_csia": set(range(1, 6))}
IMPUTED = ["BFI2", "BFI5", "SCS15", "SAS1", "SAS4", "SAS5", "SAS17", "CSIA1",
           "CSIA3", "CSIA5", "CSIA13"]
REVERSED = {"BFI1R": ("BFI1", 6), "BFI3R": ("BFI3", 6), "BFI4R": ("BFI4", 6),
            "BFI5_1R": ("BFI5_1", 6), "BFI7R": ("BFI7", 6),
            "SCS3R": ("SCS3", 4), "SCS9R": ("SCS9", 4),
            "SCS12R": ("SCS12", 4)}
TOTALS = {"BFI_O", "BFI_C", "BFI_E", "BFI_A", "BFI_N", "SCS_Pub", "SCS_Pri",
          "SCS_SocialA", "SCS_Total", "SAS_SomA", "SAS_W", "SAS_CD",
          "SAS_Total", "CSIA_Avoid", "CSIA_App", "CSIA_Diff", "CS_SC",
          "CS_SAnxiety", "CS_Cope", "CS_Total", "CS1_SCS", "CS1_SAS",
          "CS1_CSIA"}
COVS = {"Gender": "cov_gender", "Age": "cov_age",
        "AthleticStatus": "cov_varsity_athlete",
        "CS": "cov_choking_susceptible"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (177, 117), d.shape

    item_cols = [c for its in TABLES.values() for c in its]
    imputed_copies = {f"{c}_1" for c in IMPUTED}
    known = (set(item_cols) | imputed_copies | set(REVERSED) | TOTALS
             | set(COVS) | {"ParticipantID"})
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["ParticipantID"].is_unique

    for c in IMPUTED:
        cp = d[f"{c}_1"]
        ok = d[c].notna()
        assert (cp[ok] == d.loc[ok, c]).all(), c
        assert d[c].isna().sum() >= 1, c
        assert "MEAN(" in meta.column_names_to_labels[f"{c}_1"], c
    for r, (src, k) in REVERSED.items():
        ok = d[src].notna()
        assert (d.loc[ok, r] == k - d.loc[ok, src]).all(), r
    scs = d[TABLES["thiessen_2023_scs"]].copy()
    scs["SCS15"] = d["SCS15_1"]
    for i in (3, 9, 12):
        scs[f"SCS{i}"] = d[f"SCS{i}R"]
    assert np.allclose(scs.sum(axis=1), d["SCS_Total"])
    # SCS value labels are shifted relative to the stored codes; the paper's
    # 0-4 is used instead.
    assert meta.variable_value_labels["SCS1"][1.0] == "0"
    assert not d.drop(columns="ParticipantID").duplicated().any()
    assert not d[item_cols].T.duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = PERMITTED[table]
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
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
