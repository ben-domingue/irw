#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/2gwnjx729x/3
# DOI: 10.17632/2gwnjx729x.3 (dataset; no paper DOI on the record)
#   Fernandez-Prados, Juan Sebastian & Lozano Diaz, Antonia (2025). "Actitudes hacia la
#   Inteligencia Artificial, Ansiedad Digital y Competencias Digitales entre estudiantes
#   universitarios"
#   [data set]. Mendeley Data, V3.
# Data: DATOS_DEPURADOS_COMPLETOSC.sav: 235 education and social-studies undergraduates
#       (University of Almeria, Spain) x 124 columns, with SPSS variable labels (each
#       item's Spanish statement in [brackets], then the question stem) and value
#       labels (the options). Cuestionario.docx: the questionnaire (blocks, instructions,
#       source of each scale).
# License: CC BY 4.0 (Mendeley record).
#
# Item text: shipped (SPSS variable + value labels, instructions from Cuestionario.docx;
#   built by automated_finding/itemtext_verification/make_itemtext_fernandez_prados_2025.py).
#   English *_translated is IRW's own translation.
#
# Tables (item codes = the .sav column names):
#   fernandez_prados_2025_attari      Astein_SQ001-012   attitudes towards AI (Stein et al.
#                                     2024, ATTARI-12), 1-7 agreement
#   fernandez_prados_2025_gaais       Aschepam_SQ002-009 General Attitudes towards AI Scale,
#                                     8-item form (Schepman & Rodway 2022), 1-7
#   fernandez_prados_2025_aias        ANwang_SQ001-014   AI Anxiety Scale (Wang & Wang 2019;
#                                     learning and job-replacement dimensions), 1-7
#   fernandez_prados_2025_digcomp_comm  DigComp_HabilidadesComunicación_1-6 } DigComp-based
#   fernandez_prados_2025_digcomp_info  DigComp_InformacionAlfabetizacion_1-7 } internet-
#                                     activity frequency, 0 Nunca ... 4 Varias veces al dia
#   fernandez_prados_2025_ai_uses     Uia_SQ002-007      frequency of six uses of AI, 0-4
#   Items stored as answered (the source's reverse-scored copies RecASTEIN_*, REC_SHEPAM_*
#   are not shipped).
# Not shipped: Udispositivos_SQ002-007 (frequency of using a laptop, mobile, internet,
#   social media, office tools, AI products -- device-use descriptors, not a scale; mobile
#   and internet are near-constant); Uiasutilizado_*/Uiapagocual_* (tools used / paid
#   for: multiple-choice checkboxes); DIC_* dichotomised items; all totals, recodes and
#   score columns (DigComp_HCC/IAD, TOTAL_*, ANSIEDAD_*, ACTITUD_*, EDAD, CLASE,
#   IDEOLOGIA, DIC_ESTUDIOS, TIC_USUARIO, IA_USUARIO, SEXO duplicate); Sestudios_other,
#   Uiapagocual_other (empty text); Sedad (birth-year code; EDAD band kept instead).
# Covariates: cov_female (Ssexo 1 Femenino, 2 Masculino), cov_age_band (EDAD 1 18-20,
#   2 21-23, 3 24+), cov_degree (Sestudios 1-7, labelled), cov_social_class
#   (Sclasesocial 1 Baja ... 5 Alta), cov_ideology (Sideologia 1 left ... 10 right).
# Missing cells (respondents who stopped part-way: 9-28 per block) are dropped.

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "fernandez_prados_2025"
UA = {"User-Agent": "Mozilla/5.0 (IRW-Finder/1.0; ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/2gwnjx729x"
FILES = ["DATOS DEPURADOS_COMPLETOSC.sav", "Cuestionario.docx"]
TABLES = {
    "fernandez_prados_2025_attari": (r"^Astein_SQ\d+$", range(1, 8)),
    "fernandez_prados_2025_gaais": (r"^Aschepam_SQ\d+$", range(1, 8)),
    "fernandez_prados_2025_aias": (r"^ANwang_SQ\d+$", range(1, 8)),
    "fernandez_prados_2025_digcomp_comm": (r"^DigComp_HabilidadesComunicación_\d$", range(0, 5)),
    "fernandez_prados_2025_digcomp_info": (r"^DigComp_InformacionAlfabetizacion_\d$", range(0, 5)),
    "fernandez_prados_2025_ai_uses": (r"^Uia_SQ\d+$", range(0, 5)),
}
COVS = {"Ssexo": "cov_female", "EDAD": "cov_age_band", "Sestudios": "cov_degree",
        "Sclasesocial_SQ001": "cov_social_class", "Sideologia_SQ001": "cov_ideology"}


def fetch() -> Path:
    paths = {f: RAW_DIR / f for f in FILES}
    if not all(p.exists() for p in paths.values()):
        meta = requests.get(API, headers=UA, timeout=120).json()
        assert meta["data_licence"]["short_name"] == "CC BY 4.0" and meta["version"] == 3
        urls = {f["filename"]: f["content_details"]["download_url"] for f in meta["files"]}
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for f in FILES:
            r = requests.get(urls[f], headers=UA, timeout=300)
            r.raise_for_status()
            paths[f].write_bytes(r.content)
    return paths[FILES[0]]


def table_items(columns) -> dict:
    out = {name: [c for c in columns if re.match(pat, c)] for name, (pat, _) in TABLES.items()}
    assert [len(v) for v in out.values()] == [12, 8, 14, 6, 7, 6], out
    return out


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (235, 124) and d["id"].is_unique
    tabs = table_items(d.columns)
    shipped = {c for v in tabs.values() for c in v}
    skipped = [c for c in d.columns if c not in shipped | set(COVS) | {"id"}]
    print(f"  [skip] {len(skipped)} columns (device-use, checkboxes, recodes, totals): {skipped}")
    d["id"] = d["id"].astype(int)
    d["cov_social_class"] = pd.to_numeric(d.pop("Sclasesocial_SQ001"))
    d = d.rename(columns={k: v for k, v in COVS.items() if k != "Sclasesocial_SQ001"})
    d["cov_female"] = d["cov_female"].map({1.0: 1, 2.0: 0})   # Ssexo 1 Femenino, 2 Masculino
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in tabs.items():
        rng = TABLES[name][1]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
