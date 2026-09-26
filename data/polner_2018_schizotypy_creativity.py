#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6147126
# DOI: 10.7717/peerj.5615
#   "Insomnia and intellect mask the positive link between schizotypal traits
#   and creativity" (Polner, Simor & Kéri, 2018), PeerJ 6:e5615.
# Data: PeerJ supplementary files, fetched from the Europe PMC supplementaryFiles
#       zip: peerj-06-5615-s001.csv (182 x 195, one row per participant, no id
#       column), peerj-06-5615-s003.csv (codebook: names the composites only;
#       item columns carry no wording) and peerj-06-5615-s002.zip (the authors'
#       R scripts, which give the O-LIFE / REI subscale keys).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. The deposit has bare codes (olife_1, ais_1, ghq_12_1,
#   cra_0_acc, rei_1) and no wording; the survey was administered in Hungarian
#   (Hungarian sO-LIFE, GHQ-12 (Balajti et al. 2007), AIS (Novak 2004), REI
#   (Bognar, Orosz & Buki 2014), CRA (Simor & Polner 2017)), whose wording is
#   not in the deposit.
#
# Sample: Hungarian university students recruited from courses in Budapest.
#
# Tables (all 182 participants; id = row index):
#   polner_2018_olife  short O-LIFE, 43 yes/no items, 0/1 as deposited
#                      (verified: the four subscale sums in the file equal the
#                      item sums under the authors' keys)
#   polner_2018_ais    Athens Insomnia Scale, 8 items, 0-3
#   polner_2018_ghq12  GHQ-12, 12 items, 1-4 (Likert coding)
#   polner_2018_cra    Compound Remote Associates, 50 Hungarian problems,
#                      accuracy 0/1 (3 participants have no CRA data - the paper
#                      reports computer error)
#   polner_2018_rei    Rational-Experiential Inventory, all 40 items, 1-5 (the
#                      paper analyses the 20 rationality items; the deposit has
#                      the full inventory)
# Covariates on every table: age, sex, education (years), hours slept before the
# session, smoker, forward digit span, and the four exclusion flags the authors
# apply per analysis (psychiatric/neurological disorder, dyslexia, medication,
# caffeine) - kept, since the deposit is the full sample.

import sys
from pathlib import Path
import io
import zipfile

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
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6147126/supplementaryFiles"

OLIFE = [f"olife_{i}" for i in range(1, 44)]
AIS = [f"ais_{i}" for i in range(1, 9)]
GHQ = [f"ghq_12_{i}" for i in range(1, 13)]
CRA = [f"cra_{i}_acc" for i in range(0, 50)]
REI = [f"rei_{i}" for i in range(1, 41)]
OLIFE_KEYS = {
    "olife_ue": [7, 9, 12, 14, 15, 16, 20, 30, 33, 34, 35, 38],
    "olife_cd": [2, 10, 17, 18, 19, 22, 28, 29, 36, 39, 43],
    "olife_ia": [3, 4, 5, 13, 21, 23, 27, 31, 37, 41],
    "olife_in": [1, 6, 8, 11, 24, 25, 26, 32, 40, 42],
}
COV = {
    "age": "cov_age",
    "sex_0male": "cov_female",          # 1 = female, 0 = male
    "edu": "cov_education_years",
    "sleep_hours": "cov_sleep_hours",
    "smoke_1yes": "cov_smoker",         # recoded 1 = smoker, 0 = non-smoker
    "digitspan": "cov_digit_span",
    "exclude_neurol_psych_disord": "cov_psych_neuro_disorder",
    "exclude_dyslexia": "cov_dyslexia",
    "exclude_medication": "cov_medication",
    "exclude_coffee_4plus": "cov_caffeine_4plus",
}
COMPOSITES = ["olife_ia", "olife_cd", "olife_in", "olife_ue", "ais_total",
              "ghq_12_total", "dt_mean_1", "dt_mean_2", "dtfluency_1",
              "dtfluency_2", "dt_flu", "dt_mean", "caq_vis", "caq_mus",
              "caq_dan", "caq_arch", "caq_wr", "caq_hum", "caq_inv", "caq_sci",
              "caq_th", "caq_ga", "caq_total", "caq_perf", "caq_expr",
              "caq_sciga", "cra_total", "rei_rata", "rei_ratp", "rei_rat",
              "dt_1_mean_orig", "dt_2_mean_orig"]
SKIP = {c: "composite / rater-scored summary (subscale, total, CAQ domain "
           "score or divergent-thinking rating mean)" for c in COMPOSITES}


def fetch():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_csv(io.BytesIO(z.read("peerj-06-5615-s001.csv")))


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
    assert d.shape == (182, 195), d.shape
    assert not d.duplicated().any()
    cols = set(d.columns)
    accounted = (set(OLIFE) | set(AIS) | set(GHQ) | set(CRA) | set(REI)
                 | set(COV) | set(SKIP))
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c!r}: {why}")

    # sanity: the deposited totals are sums of the deposited items
    for sub, idx in OLIFE_KEYS.items():
        assert (d[[f"olife_{i}" for i in idx]].sum(axis=1) == d[sub]).all(), sub
    assert (d[AIS].sum(axis=1) == d["ais_total"]).all()
    assert (d[GHQ].sum(axis=1) == d["ghq_12_total"]).all()
    ok = d["cra_total"].notna()
    assert (d.loc[ok, CRA].sum(axis=1) == d.loc[ok, "cra_total"]).all()

    d = d.copy()
    d["smoke_1yes"] = d["smoke_1yes"].map({"smoker": 1, "non-smoker": 0})
    d.insert(0, "id", np.arange(1, len(d) + 1))
    d = d.rename(columns=COV)
    covs = list(COV.values())

    specs = [
        ("polner_2018_olife", OLIFE, [0, 1]),
        ("polner_2018_ais", AIS, [0, 1, 2, 3]),
        ("polner_2018_ghq12", GHQ, [1, 2, 3, 4]),
        ("polner_2018_cra", CRA, [0, 1]),
        ("polner_2018_rei", REI, [1, 2, 3, 4, 5]),
    ]
    names = [s[0] for s in specs]
    assert len(set(names)) == len(names)
    for name, items, pv in specs:
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert long["resp"].isin(pv).all(), name
        long["resp"] = long["resp"].astype(int)
        if name == "polner_2018_cra":
            long["item"] = long["item"].str.replace("_acc", "", regex=False)
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
