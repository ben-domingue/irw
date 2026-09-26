#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6086079
# DOI: 10.7717/peerj.5414
#   "Mindfulness and autonomous sensory meridian response (ASMR)" (Fredborg,
#   Clark & Smith, 2018), PeerJ 6:e5414.
# Data: PeerJ supplementary files, fetched from the Europe PMC supplementaryFiles
#       zip: peerj-06-5414-s001.xlsx, sheet "Data" (563 x 67, one row per
#       respondent: 284 with ASMR, 279 age/sex-matched controls) and sheet
#       "Data Legend" (item wording + response options). s002.pdf is the ASMR
#       Checklist form. SPSS system-missing arrives as the string "#NULL!".
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: available, not shipped here. The "Data Legend" sheet carries the
#   full English wording of all 13 TMS and 15 MAAS items and the label of each
#   of the 14 ASMR Checklist stimuli; s002.pdf carries the checklist's
#   instructions and the 0-6 / "Unknown" intensity anchors. English online
#   survey.
#
# Tables:
#   fredborg_2018_tms           Toronto Mindfulness Scale, 13 items, 0-4 (paper:
#                               0 "not at all" - 4 "very much"; the legend's
#                               "0, 2, 3, 4, 5" anchor list is a typo, the data
#                               are 0-4). Both groups.
#   fredborg_2018_maas          Mindful Attention Awareness Scale, 15 items, 1-6
#                               (paper: six-point, "almost always" - "almost
#                               never"; the legend's 5-point agree list does not
#                               match the data). 10 cells coded 0 (8 people,
#                               scattered over 7 items) are outside the
#                               six-point format and are dropped. Both groups.
#   fredborg_2018_asmr_triggers ASMR Checklist, 14 stimuli rated 0 ("no
#                               tingles") - 6 ("most intense"); 7 = "Unknown"
#                               is dropped. ASMR group only (N = 284); the paper
#                               analysed these 14 (two rarely known stimuli,
#                               items 7 and 9, are not in the deposit).
#
# ID is a Qualtrics ResponseID (R_...), a platform identifier: it is replaced
# with the row index. About ten control-group respondents straight-line the
# TMS (all 0) and MAAS (all 1); they differ in age/gender and are kept as
# deposited (no exact-duplicate rows in the file).

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6086079/supplementaryFiles"

TMS = [f"TMS_{i}" for i in range(1, 14)]
MAAS = [f"M_{i}" for i in range(1, 16)]
TRIG = ["Whisper", "S_2__I", "S_3__I", "S_4__I", "S_5__I", "S_6__I", "S_8__I",
        "S_10__I", "S_11__I", "S_12__I", "S_13__I", "S_14__I", "S_15__I",
        "S_16__I"]
COV = {"Group": "cov_group",   # 1 = ASMR, 2 = control
       "Age": "cov_age",
       "Gend": "cov_gender"}   # 1 = female, 2 = male
SKIP = {
    "ID": "Qualtrics ResponseID (platform id) -> replaced by row index",
    "Tcur": "TMS Curiosity subscale score (composite)",
    "tdec": "TMS Decentering subscale score (composite)",
    "Ttotal": "TMS total (composite)",
    "MAASmean": "MAAS mean (composite)",
    "stim1": "ASMR stimulus factor score (composite)",
    "stim2": "ASMR stimulus factor score (composite)",
    "stim3": "ASMR stimulus factor score (composite)",
    "stim4": "ASMR stimulus factor score (composite)",
    "stim5": "ASMR stimulus factor score (composite)",
    "intens": "mean intensity over the 14 stimuli (composite)",
    "Frisson": "single-item ASMR phenomenology question, not a scale",
    "Relax": "single-item ASMR usage frequency, not a scale",
    "Pleasure": "single-item ASMR phenomenology question, not a scale",
    "Toward": "single-item ASMR phenomenology question, not a scale",
    "Away": "single-item ASMR phenomenology question, not a scale",
    "Sleep": "single-item ASMR usage frequency, not a scale",
    "Relax.1": "second copy of the Relax question in the deposit",
    "DiffChills": "single-item ASMR phenomenology question, not a scale",
    "Percent1": "branching single item (pleasurable), not a scale",
    "Percent2": "branching single item (not pleasurable), not a scale",
    "EarlAge": "age at first ASMR experience, free numeric entry",
}


def fetch():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_excel(io.BytesIO(z.read("peerj-06-5414-s001.xlsx")),
                         sheet_name="Data")


def gate(long, name, pv):
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        long, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")


def convert():
    d = fetch()
    assert d.shape == (563, 67), d.shape
    assert d["ID"].is_unique
    cols = set(d.columns)
    accounted = set(TMS) | set(MAAS) | set(TRIG) | set(COV) | set(SKIP)
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c!r}: {why}")

    d = d.replace("#NULL!", np.nan)
    d.insert(0, "id", np.arange(1, len(d) + 1))
    d = d.rename(columns=COV)
    covs = list(COV.values())

    specs = [
        ("fredborg_2018_tms", TMS, [0, 1, 2, 3, 4], None),
        ("fredborg_2018_maas", MAAS, [1, 2, 3, 4, 5, 6], "0 outside 1-6"),
        ("fredborg_2018_asmr_triggers", TRIG, [0, 1, 2, 3, 4, 5, 6],
         "7 = Unknown"),
    ]
    names = [s[0] for s in specs]
    assert len(set(names)) == len(names)
    for name, items, pv, why in specs:
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        nn = long["resp"].notna()
        bad = nn & ~long["resp"].isin(pv)
        if bad.any():
            print(f"  {name}: dropped {int(bad.sum())} cells "
                  f"({why}): {sorted(long.loc[bad, 'resp'].unique())}")
        long = long[nn & ~bad].copy()
        long["item"] = long["item"].str.lower().str.rstrip("_i").str.rstrip("_")
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(items)
        gate(long, name, pv)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
