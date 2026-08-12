#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7519719
# DOI: 10.7717/peerj.9990
#
# Dalky et al. (2020), "The health-related quality of life of Syrian
# refugee women in their reproductive age." PeerJ. CC BY 4.0. N=523.
#
# The raw file is a wide (190-column) survey combining SF-36 Health
# Survey items with demographic/reproductive-history covariates. Per the
# paper's Measures section, the instrument is the (Arabic-translated)
# SF-36, scored into 8 subscales via the RAND 0-100 transformation. The
# file's `factor_1`-`factor_36` and the named subscale columns
# (physical_Functioning, Role_limitation_physical, ..., total_score_for_
# health) are that RAND-transformed/aggregated scoring output, not raw
# items -- excluded. The genuine raw SF-36 items are the text/ordinal-
# coded columns identified from the file's own SPSS value-label metadata
# (each already numerically coded 1..k with an explicit, internally
# consistent value-label set per item group):
#   - physical1-physical9 (SF-36 physical functioning; 9 of the standard
#     10 PF items are present in this file), 3-point (1=restricts a lot,
#     3=doesn't restrict at all).
#   - L8_1-L8_4 (role limitations - physical), L9_1-L9_3 (role
#     limitations - emotional), yes/no (1=yes, 2=no).
#   - L10, L14 (extent/frequency physical or emotional problems
#     interfered with social activities), 5-point.
#   - pain4wks (bodily pain magnitude, 6-point), paineffect (pain
#     interference, 5-point).
#   - L13_1-L13_9 (the combined vitality + mental-health 9-item block),
#     6-point frequency scale.
#   - L15_1-L15_4 (general health perceptions, true/false), 5-point.
#   - H1hlthgeneral (general health, 1 item, 5-point).
#   - H2healthcomplastyr (reported health transition, SF-36's own item 2
#     -- not scored into any of the 8 subscales, but still a genuine
#     administered SF-36 item), 5-point.
# All value scales come directly from the SPSS file's embedded value
# labels (`convert_categoricals=False` numeric codes), no text parsing
# needed.
#
# Covariate kept minimal (mothers_age only) to avoid unnecessary PII
# exposure risk from the wide reproductive-history/geographic block; no
# PII in what's carried through (age is not identifying).

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7519719/supplementaryFiles"
MEMBER = "peerj-08-9990-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_GROUPS = {
    "physical": ([f"physical{i}" for i in [1]] + ["physcial2"] +
                 [f"physical{i}" for i in range(3, 10)], (1, 3)),
    "role_phys": ([f"L8_{i}_L8" for i in range(1, 5)], (1, 2)),
    "role_emot": ([f"L9_{i}_L9" for i in range(1, 4)], (1, 2)),
    "social": (["L10", "L14"], (1, 5)),
    "pain_magnitude": (["pain4wks"], (1, 6)),
    "pain_interference": (["paineffect"], (1, 5)),
    "vitality_mh": ([f"L13_{i}_L13" for i in range(1, 10)], (1, 6)),
    "genhealth_perception": ([f"L15_{i}_L15" for i in range(1, 5)], (1, 5)),
    "genhealth_single": (["H1hlthgeneral"], (1, 5)),
    "health_transition": (["H2healthcomplastyr"], (1, 5)),
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_spss(tmp.name, convert_categoricals=False)

    df = df.rename(columns={"Respondent_Serial": "id", "mothers_age": "cov_age"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df)

    frames = []
    for group, (items, (lo, hi)) in ITEM_GROUPS.items():
        sub = df.melt(id_vars=["id", "cov_age"], value_vars=items,
                       var_name="item", value_name="resp")
        sub["resp"] = pd.to_numeric(sub["resp"], errors="coerce")
        sub = sub.dropna(subset=["resp"])
        sub = sub[(sub["resp"] >= lo) & (sub["resp"] <= hi)]
        frames.append(sub)

    long = pd.concat(frames, ignore_index=True)
    long = long[["id", "item", "resp", "cov_age"]]

    out_path = OUT_DIR / "dalky_2020_sf36.csv"
    long.to_csv(out_path, index=False)
    print(f"dalky_2020_sf36: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
