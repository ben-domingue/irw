#!/usr/bin/env python3

# Source: https://ssh.datastations.nl/dataset.xhtml?persistentId=doi:10.17026/DANS-ZP9-WWM7
# DOI: 10.17026/dans-zp9-wwm7
#   Peerdeman, K. J. (2019). Pre-consultation information about one's
#   physician can affect trust and treatment outcome expectations [Dataset].
#   DANS Data Station Social Sciences and Humanities. Published as Peerdeman,
#   Hinnen, van Vliet & Evers (2020), Patient Education and Counseling,
#   doi:10.1016/j.pec.2020.07.021.
# Data: "data_analyses.tab" -- the paper's analysis sample, 237 of the 256
#   respondents in the deposit's raw .sav, each shown one vignette about a
#   physician in a 2x2x2 design (severity, competence, empathy).
#   data_analyses.tab is read rather than data_raw.sav because it is the only
#   file that carries BOTH the items and the three manipulated factors as
#   columns; in the raw file the manipulation survives only as Qualtrics
#   block-randomiser flow flags.
# License: CC BY 4.0 (verified on the DANS record, 2026-10-19).
# Item text: NOT shipped, extraction solved -- the raw .sav's variable labels
#   carry every item's administered Dutch wording ("GTS - 1) De meeste mensen
#   zijn in principe eerlijk."). The ECR-M16 is a published attachment
#   measure with no rights-register verdict, so its text waits on a ruling;
#   the vignette trust items are the study's own.
#
# THREE tables, 237 respondents, complete:
#   peerdeman_2020_ecr              16 items, 1-5 (ECR-M16 attachment)
#   peerdeman_2020_general_trust     6 items, 1-5 (general trust in people)
#   peerdeman_2020_vignette_trust    5 items, 1-5 (trust in the physician
#                                    described in the vignette)
#
# NOT SHIPPED: the seven `expectations_*` items (each a single global rating
#   of a different thing -- treatment success, negative outcomes, the
#   physician's competence and empathy, severity), the four
#   birthmark/melanoma history questions and their expectation ratings, the
#   deposit's own reverse-scored copies (`*_re`) and composites
#   (`ecr_m16_anxiety`, `ecr_m16_avoidance`, `gts_total`,
#   `phystrustscale_mean`), and the Qualtrics metadata. The `*_re` columns are
#   the scored direction; the plain columns are as administered, which is what
#   ships.
#
# id: the row index. `responseid` is the Qualtrics platform id, replaced under
#   the 2026-09-20 narrowing.
# Covariates: cov_age, cov_sex, cov_language_fluency, cov_education,
#   cov_study, cov_works_healthcare, plus the design: cov_vignette_severity,
#   cov_vignette_competence, cov_vignette_empathy, each 1/2 as the deposit
#   codes it. Three two-level factors do not fit `treat`, which is one 0/1
#   column, so they ship as covariates with the source's own coding.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "zp9wwm7" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOI, BASE = "10.17026/dans-zp9-wwm7", "https://ssh.datastations.nl"
FNAME = "data_analyses.tab"
ECR = [f"ecr_m16_{i}" for i in range(1, 17)]
GTS = [f"gts_{i}" for i in range(1, 7)]
TRUST = [f"phystrustscale{i}" for i in range(1, 6)]
COVS = {"age": "cov_age", "sex": "cov_sex",
        "languagefluency": "cov_language_fluency",
        "educationlevel": "cov_education", "study": "cov_study",
        "workhealthcare": "cov_works_healthcare",
        "severity": "cov_vignette_severity",
        "competence": "cov_vignette_competence",
        "empathy": "cov_vignette_empathy"}
SCALE = set(range(1, 6))
TABLES = {"peerdeman_2020_ecr": ECR,
          "peerdeman_2020_general_trust": GTS,
          "peerdeman_2020_vignette_trust": TRUST}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"{BASE}/api/datasets/:persistentId/",
                         params={"persistentId": f"doi:{DOI}"},
                         headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"]["filename"] == FNAME][0]
        r = requests.get(f"{BASE}/api/access/datafile/{fid}",
                         headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch(), sep="\t")
    assert len(df) == 237, len(df)
    items = ECR + GTS + TRUST
    assert not df[items].isna().any().any(), "the analysis sample is complete"
    # The reverse-scored copies exist and are NOT what ships.
    for plain in ("ecr_m16_3", "phystrustscale1"):
        assert f"{plain}_re" in df.columns, plain
        assert (df[f"{plain}_re"] == 6 - df[plain]).all(), plain
    print("not shipped: the deposit's *_re reverse-scored copies, its "
          "composites, the seven single expectation items and the "
          "birthmark/melanoma history questions")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")
    for c in ("cov_vignette_severity", "cov_vignette_competence",
              "cov_vignette_empathy"):
        assert set(df[c].dropna()) == {1, 2}, (c, sorted(set(df[c].dropna())))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, cols in TABLES.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the administered 1-5: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 237 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:140]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
