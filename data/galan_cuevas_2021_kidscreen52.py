#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/s9g2zmc2zn/1
# DOI: 10.17632/s9g2zmc2zn.1 (dataset; no paper linked on the record)
#   Galan Cuevas, Sergio & Diaz Garcia, Davin Eduardo (2021). "Kidscreen-52 en
#   estudiantes mexicanos de 11 a 16 anos de edad" [data set]. Mendeley Data, V1.
# Data: SECS_SLP.xlsx (one sheet): 2,257 secondary-school students from seven
#       public schools on the periphery of San Luis Potosi, Mexico x 55 columns
#       (Grado, Sexo, Edad, KY52PHY1 ... KY52BUL3). Paper-and-pencil, Mexican
#       standardised KIDSCREEN-52 (Hidalgo-Rasmussen et al. 2014). The record's
#       "method" field is the codebook: Sexo 1 = Hombre, 0 = Mujer; the ten
#       dimension prefixes (PHY physical well-being, PWB psychological well-being,
#       EMO moods and emotions, SEL self-perception, AUT autonomy, PAR parent
#       relations, FIN financial resources, SOC peers and social support, SCH school
#       environment, BUL social acceptance/bullying) and the 52 Spanish stems.
# License: CC BY 4.0 (Mendeley record, data_licence).
#
# Item text: not shipped. Levels checked: xlsx headers are codes only (no
#   variable/value labels); the record's "method" field ties every code to its
#   Spanish stem (cheap), but the KIDSCREEN questionnaires are blocked in
#   itemtext/instrument_rights_register.csv ("Distribution or transfer to third
#   parties ... of the KIDSCREEN questionnaires is not permitted"). The record also
#   disagrees with itself on the options: the description says a 5-point
#   "Nunca ... Siempre" scale, the method field lists "Totalmente en desacuerdo ...
#   Totalmente de acuerdo".
#
# Shipped: galan_cuevas_2021_kidscreen52 -- all 52 items, 1-5, one table (one
#   instrument; the dimension is the item-code infix). Negatively worded items
#   (EMO1-7, SEL3-5, BUL1-3) are STORED REVERSE-SCORED by the source: every one
#   correlates positively with PWB3 ("satisfied with your life"), r = .07-.19, so
#   higher = better on every item. Not re-reversed (the stored coding is the
#   source's).
# Covariates: cov_grade (Grado 1-3, secondary year), cov_male (Sexo 1 = Hombre,
#   0 = Mujer), cov_age (Edad; two 0s set to missing).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "galan_cuevas_2021"
UA = {"User-Agent": "Mozilla/5.0 (IRW-Finder/1.0; ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/s9g2zmc2zn"
NAME = "galan_cuevas_2021_kidscreen52"
DIMS = {"PHY": 5, "PWB": 6, "EMO": 7, "SEL": 5, "AUT": 5, "PAR": 6, "FIN": 3,
        "SOC": 6, "SCH": 6, "BUL": 3}
ITEMS = [f"KY52{k}{i}" for k, n in DIMS.items() for i in range(1, n + 1)]
COVS = {"Grado": "cov_grade", "Sexo": "cov_male", "Edad": "cov_age"}


def fetch() -> Path:
    p = RAW_DIR / "SECS_SLP.xlsx"
    if not p.exists():
        meta = requests.get(API, headers=UA, timeout=120).json()
        assert meta["data_licence"]["short_name"] == "CC BY 4.0"
        (f,) = [f for f in meta["files"] if f["filename"] == "SECS_SLP.xlsx"]
        r = requests.get(f["content_details"]["download_url"], headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert len(ITEMS) == 52 and d.shape == (2257, 55), d.shape
    assert d.columns.tolist() == list(COVS) + ITEMS
    d = d.rename(columns=COVS)
    d.insert(0, "id", range(1, len(d) + 1))      # no id column in the deposit
    d.loc[d["cov_age"] == 0, "cov_age"] = pd.NA
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(ITEMS) and not t.duplicated(["id", "item"]).any()
    pv = {i: {1, 2, 3, 4, 5} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
