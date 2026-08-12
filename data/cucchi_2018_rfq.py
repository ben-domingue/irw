#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6211265
# DOI: 10.7717/peerj.5756
#
# Cucchi, Hampton & Moulton-Perkins (2018), "Using the validated
# Reflective Functioning Questionnaire to investigate mentalizing in
# individuals presenting with eating disorders with and without
# self-harm." PeerJ. CC BY 4.0. N=229.
#
# A full 162-column read (the deferred-candidate note had only inspected
# the first 25) confirms the paper's Questionnaires section describes six
# distinct raw-item instruments, each shipped as its own file:
#   - RFQ (Reflective Functioning Questionnaire, RFQ1-8), 7-point Likert
#     (1=strongly disagree .. 7=strongly agree). The file's RFQc1-6 /
#     RFQu2,4,5,6,7,8 columns are NOT additional raw items -- per the
#     paper's own Table 2, they are the nonlinearly *recoded* (0-3)
#     values used to compute the RFQc/RFQu subscale means (e.g. RFQ2 is
#     rescored 3,2,1,0,0,0,0 for RFQc), a derived transformation of the
#     same 8 raw items, not a second measurement. Excluded, along with
#     RFQ_c/RFQ_u (the subscale means themselves).
#   - SCOFF (5-item eating-disorder screen, SCOFF1-5), binary yes/no,
#     mapped yes=1/no=0 from the file's own value labels.
#   - PTS (7-item Perspective Taking subscale of the Interpersonal
#     Reactivity Index, PTS1-7), 5-point Likert ("does not describe me
#     well" .. "describes me very well").
#   - KIMS (18-item Kentucky Inventory of Mindfulness Skills,
#     Describing + Acting with Awareness subscales, KIMS1-18), 5-point
#     Likert ("never or very rarely" .. "very often or always true").
#   - TAS-20 (Toronto Alexithymia Scale, TAS1-20), 5-point Likert
#     (already numeric in the file; 5 items are reverse-scored per the
#     paper but datastandard.md does not require un-reversing).
#   - RMET (Reading the Mind in the Eyes Test, 36 items). The raw
#     `EYES1-36` columns record which of 4 multiple-choice words was
#     selected -- a categorical label, not an ordinal response, so not
#     usable as `resp`. The paper scores RMET by correctness, and the
#     file separately provides `eyes1t-36t` (per-item correct/incorrect),
#     which is the actual scored item response for this test (paralleling
#     a lexical-decision/cognitive-task item, per datastandard.md's `id`
#     examples) -- mapped correct=1, incorrect=0.
#
# No PII (Gender/Age/Relationship/Ethnicity/EmpStat/EduAtt/Occupation are
# ordinary coded demographic covariates, no free text).

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6211265/supplementaryFiles"
MEMBER = "peerj-06-5756-s003.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Group": "cov_group",
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Relationship": "cov_relationship",
    "Ethnicity": "cov_ethnicity",
    "EmpStat": "cov_employment",
    "EduAtt": "cov_education",
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

    df = df.rename(columns={"Participant": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df)

    cov_lookup = {c.lower(): c for c in df.columns}
    cov_cols = []
    for src, out in COV_RENAME.items():
        match = cov_lookup.get(src.lower())
        if match:
            df = df.rename(columns={match: out})
            cov_cols.append(out)

    def ship(out_name, items, lo, hi):
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    ship("cucchi_2018_rfq", [f"RFQ{i}" for i in range(1, 9)], 1, 7)

    # SCOFF: value labels are 1=YES, 2=NO -- remap to yes=1/no=0.
    scoff_items = [f"SCOFF{i}" for i in range(1, 6)]
    for c in scoff_items:
        df[c] = df[c].map({1.0: 1, 2.0: 0})
    ship("cucchi_2018_scoff", scoff_items, 0, 1)

    ship("cucchi_2018_pts", [f"PTS{i}" for i in range(1, 8)], 1, 5)
    ship("cucchi_2018_kims", [f"KIMS{i}" for i in range(1, 19)], 1, 5)
    ship("cucchi_2018_tas20", [f"TAS{i}" for i in range(1, 21)], 1, 5)

    eyes_items = [f"eyes{i}t" for i in range(1, 37)]
    for c in eyes_items:
        df[c] = df[c].map({1.0: 1, 2.0: 0})
    ship("cucchi_2018_rmet", eyes_items, 0, 1)


if __name__ == "__main__":
    convert()
