#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/33106967
# DOI: 10.6084/m9.figshare.33106967.v2 (dataset; the associated article is not linked)
#   Tangarife, Viviana, Osorio-Andrade, Carlos & Lopez Herrera, Paula Andrea (2026).
#   "Determinantes de la adopcion de inteligencia artificial generativa en la
#   investigacion academica: Un modelo de ecuaciones estructurales desde
#   universidades colombianas" [data set]. figshare.
# Data: BD_IA_Investigacion_Codificada.xlsx -- sheet "Datos": 167 researcher-teachers
#       at three Colombian HEIs (Valle del Cauca), March-June 2026 x ID, six coded
#       demographics, 32 items (BAR1-4, ETI1-4, BEN1-3, INF1-7, FAC1-3, INT1-5,
#       USO1-6), all "1 = Totalmente en desacuerdo ... 5 = Totalmente de acuerdo";
#       sheet "Diccionario": per variable the construct, form item number, literal
#       Spanish statement, scale, code labels and source scale. No missing cells.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped (sheet "Diccionario" ties each variable name to its literal
#   statement and option labels; built by automated_finding/itemtext_verification/
#   make_itemtext_tangarife_2026.py). English *_translated is IRW's own translation.
#
# Tables (one per construct named in the Diccionario; all 32 published items kept,
# including BAR2, BAR4, ETI2, ETI4, which the article's measurement model dropped):
#   tangarife_2026_research_barriers   BAR1-4  individual research-resource barriers
#                                              (formative construct in the article)
#   tangarife_2026_ai_reservations     ETI1-4  challenges and ethical issues / doubts
#                                              about AI output quality
#   tangarife_2026_ai_benefits         BEN1-3  perceived benefits
#   tangarife_2026_social_influence    INF1-7
#   tangarife_2026_ease_of_use         FAC1-3  perceived ease of use
#   tangarife_2026_use_intention       INT1-5
#   tangarife_2026_ai_use              USO1-6  current use of AI
# Covariates (codes as deposited, labels in the Diccionario): cov_institution
#   (1 INTEP, 2 Univalle Buga, 3 UCEVA), cov_age_band (1 <30 ... 5 60+), cov_gender
#   (1 male, 2 female), cov_education (1 undergraduate ... 4 doctorate),
#   cov_field (1-6), cov_appointment (1 full-time, 2 half-time, 3 hourly).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "tangarife_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/67071953"
TABLES = {"BAR": "tangarife_2026_research_barriers", "ETI": "tangarife_2026_ai_reservations",
          "BEN": "tangarife_2026_ai_benefits", "INF": "tangarife_2026_social_influence",
          "FAC": "tangarife_2026_ease_of_use", "INT": "tangarife_2026_use_intention",
          "USO": "tangarife_2026_ai_use"}
COVS = {"Institucion": "cov_institution", "Edad": "cov_age_band", "Genero": "cov_gender",
        "NivelEduc": "cov_education", "AreaGran": "cov_field",
        "Vinculacion": "cov_appointment"}


def fetch() -> Path:
    p = RAW_DIR / "BD_IA_Investigacion_Codificada.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Datos")
    dic = pd.read_excel(fetch(), sheet_name="Diccionario")
    assert d.shape == (167, 39) and d["ID"].is_unique
    assert dic["Variable"].tolist() == d.columns.tolist()
    items = [c for c in d.columns if c[:3] in TABLES]
    assert len(items) == 32 and set(d.columns) == {"ID"} | set(COVS) | set(items)
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for pre, name in TABLES.items():
        its = [c for c in items if c.startswith(pre)]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].isin(range(1, 6)).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
