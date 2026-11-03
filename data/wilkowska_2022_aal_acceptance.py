#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269642
# DOI: 10.1371/journal.pone.0269642
# Paper: Wilkowska W, Offermann J, Spinsante S, Poli A, Ziefle M (2022).
#   Analyzing technology acceptance and perception of privacy in ambient
#   assisted living for using sensor-based technologies. PLOS ONE 17(7):
#   e0269642.
# Data: S1 Data (journal.pone.0269642.s001, semicolon-separated CSV), 312
#   German adults, online survey, 2021.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# EIGHT output tables, every item 1 "fully disagree" .. 6 "fully agree" ("All
# acceptance items were assessed on six-point Likert type scales"). Each block
# ships its RAW items; the deposit's *_rec columns (its own reverse codes) and
# sum scores are dropped, so reverse-keyed items are as answered:
#   wilkowska_2022_tech_affinity     Tech_Aff_1-5  affinity for technology
#   wilkowska_2022_tech_control      KUT_1-6  control beliefs in dealing with
#     technology (KUT, Beier)
#   wilkowska_2022_aal_benefits      All_Pros_1-6  perceived benefits of
#     sensor-based ambient technology
#   wilkowska_2022_aal_barriers      Allg_Cons_1-6  perceived barriers
#   wilkowska_2022_aal_intention     Allg_ItU_1-3  general intention to use
#   wilkowska_2022_privacy_health    to_priv_heal_1-4  relevance of health to
#     privacy perception
#   wilkowska_2022_tam               TAM_1-6  perceived usefulness, ease of use
#     and intention to use, adapted from TAM
#   wilkowska_2022_privacy           Privacy_1-5
# NOT SHIPPED: Activity_Priv_1..13 (0-100 sliders whose prompt and anchors the
#   paper does not describe), LLErf_1-5, Wohnsituation_1-6, Pflegeerfahrung_*
#   (check-all indicators), Chr_Krankheit, Krankheit_Art,
#   Pflege_Unterst_tzung, Gesundheit_Subj, Wohnlage, Wohnstatus,
#   Familienstand, Bildungsstand (bare codes, no codebook), SC0, and
#   RecordedDate / UserLanguage / Datenschutz (survey metadata and consent).
# PII: Krankheit_Art is a free-typed "type of chronic disease" follow-up (59
#   answers, a few words each, e.g. "Asthma", "Diabetes Mellitus Typ 1"). No
#   names, emails or identifiers anywhere. Under the 2026-10-21 ruling (a short
#   free-text condition answer is a drop-the-column case) it is DROPPED, in no
#   form; the binary Chr_Krankheit it follows up has no value labels and is
#   dropped too. RecordedDate (survey completion timestamp) is dropped.
# Covariates: age (years), gender (1 male / 2 female / 3 diverse: 115/196/1
#   reproduces the paper's 62.8% female, n = 196).
# `id` is the row index.
#
# Item text: NOT SHIPPED. Column codes only (a CSV, no labels); the German
#   wording is not in the article (Table 1 is an image; the benefit and
#   barrier items appear only in Figs 4-5).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WILKOWSKA_RAW", "journal.pone.0269642.s001.csv")
BLOCKS = {
    "tech_affinity": ("Tech_Aff_", 5), "tech_control": ("KUT_", 6), "aal_benefits": ("All_Pros_", 6),
    "aal_barriers": ("Allg_Cons_", 6), "aal_intention": ("Allg_ItU_", 3), "privacy_health": ("to_priv_heal_", 4),
    "tam": ("TAM_", 6), "privacy": ("Privacy_", 5),
}


def convert():
    df = pd.read_csv(RAW, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    assert df.shape == (312, 96), df.shape
    df = df.apply(lambda s: s.str.strip())
    txt_like = [c for c in df.columns if not pd.to_numeric(df[c].replace("", None), errors="coerce").notna()
                .eq(df[c].ne("")).all()]
    print(f"PII screen: {len(txt_like)} non-numeric columns of {len(df.columns)} examined: {txt_like}")
    assert len(df.columns) > 0 and txt_like == ["RecordedDate", "UserLanguage", "Krankheit_Art"]
    num = df.drop(columns=txt_like).replace("", None).apply(pd.to_numeric)
    assert num["Geschlecht"].value_counts().to_dict() == {2: 196, 1: 115, 3: 1}
    num["id"] = range(1, len(num) + 1)
    num["cov_age"] = num["Alter"]
    num["cov_gender"] = num["Geschlecht"].map({1: "male", 2: "female", 3: "diverse"})
    covs = ["cov_age", "cov_gender"]
    used = {"Alter", "Geschlecht"} | set(txt_like)
    total = 0
    for block, (pfx, k) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = num[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(range(1, 7))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(1, 7)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"wilkowska_2022_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    not_shipped = [c for c in df.columns if c not in used]
    assert all(("_rec" in c) or c.startswith(("Activity_Priv_", "LLErf_", "Wohn", "Pflege", "TAM_", "Priv_heal"))
               or c in {"Datenschutz", "Bildungsstand", "Familienstand", "Gesundheit_Subj", "Chr_Krankheit",
                        "Krankheit_Art", "SC0"} for c in not_shipped), not_shipped
    print(f"total responses {total}; not shipped ({len(not_shipped)}): {not_shipped}")


if __name__ == "__main__":
    convert()
