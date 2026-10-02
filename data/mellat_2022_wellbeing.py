#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/nr9388gbzf (version 2)
# DOI: 10.1080/19349637.2022.2121239
#   Mellat, N., Ebrahimi Ghavam, S., Gholamali Lavasani, M., Moradi, M., &
#   Sadipour, E. (2023). "The role of cognitive, emotional, and spiritual
#   development in adult psychological well-being." Journal of Spirituality
#   in Mental Health, 25(1), 31-54 (online 2022). (Not linked from the deposit; found by Crossref title search.
#   Paywalled (closed per Unpaywall), so not read.)
#   Deposit: Mellat, N., Ebrahimi Qavam, S., Gholamali Lavasani, M.,
#   Sadipour, E., & Moradi, M. (2022). The Role of Different Levels of
#   Cognitive, Emotional, and Spiritual Development in Adults Psychological
#   Well-being. Mendeley Data. https://doi.org/10.17632/nr9388gbzf.2
# Data: DATA.mellat.sav (700 rows x 241 columns; Iranian adults aged 20-60
#   per the deposit description; Allameh Tabataba'i University).
# License: CC BY 4.0 (Mendeley Data API licence record).
#
# Item text: not shipped. Both label levels checked: no variable labels and
#   no value labels on any of the 226 item columns (labels exist only on the
#   15 composite means and the demographics). Item codes are positional
#   block letters (AQ1 .., BQ1 ..), so the published Persian instruments are
#   needed; they are named only in the paywalled paper.
#
# Tables. The deposit stores one composite per block, each variable-labelled
# with its construct and each equal to the MEAN of its block's items in
# every row (asserted). Those labels are the only identification of the 15
# instruments; the instrument names and response formats are in the
# paywalled paper, so NO permitted-value set is asserted for any table and
# resp is the stored code. Item codes are the source column names.
#   mellat_2022_absolute_thought        AQ1-AQ28  (composite AA "absolute")
#   mellat_2022_relativistic_thought    BQ1-BQ14  (BB "relativistic")
#   mellat_2022_dialectical_thought     CQ1-CQ14  (CC "Dialectical")
#   mellat_2022_egocentrism             DQ1-DQ11  (DD "Egocentrism")
#   mellat_2022_stress                  EQ1-EQ7   (EE "Stress")
#   mellat_2022_emotion_regulation      FQ1-FQ18  (FF "emotion regulation
#                                                   difficulties")
#   mellat_2022_empathy                 GQ1-GQ27  (GG "Empathy")
#   mellat_2022_spiritual_weakness      HQ1-HQ15  (HH "spiritual weakness")
#   mellat_2022_spiritual_wellbeing     IQ1-IQ19  (II "Spiritual well-being")
#   mellat_2022_aggression              JQ1-JQ7, JQ10-JQ14 (JJ "aggression";
#                                                   no JQ8/JQ9 in the file)
#   mellat_2022_depression              KQ1-KQ13  (KK "depression")
#   mellat_2022_hedonism                LQ1-LQ8   (LL "hedonism")
#   mellat_2022_resilience              MQ1-MQ10  (MM "resilience")
#   mellat_2022_gratitude               NQ1-NQ6   (NN "Gratitude")
#   mellat_2022_altruism                OQ1-OQ15  (QQ "Altruistic")
# Cells worth knowing about (all kept as stored except the first, since no
# document gives the response sets):
#   - CQ5 holds one 0.4: a non-integer cannot be a response, so it is set to
#     NA (the deposit's CC mean includes it).
#   - single isolated codes outside the rest of their block's span: DQ9 and
#     DQ10 one 0 each (block otherwise 1-4), FQ12 one 0 (block 1-5), GQ12
#     and GQ15 one 5 each (block 0-4), LQ1/LQ4/LQ5/LQ8 two or three 5s each
#     (block otherwise 0-4). Likely keying errors, but undocumented.
#
# Dropped: the 15 composite means AA .. QQ (asserted = block means).
# id: row index. The source "id" (1-700) has two duplicated values (421,
#   655) on rows that differ in demographics and items, so it is not a
#   person key.
# Covariates: cov_sex (1 men, 2 women), cov_age_band (1 20-29, 2 30-39,
#   3 40-49, 4 50-60), cov_education (1 diploma, 2 bachelor's, 3 master's+),
#   cov_religion (1 Islam, 2 Christian, 3 Jewish), cov_economic (1 weak ..
#   4 excellent), cov_job (1 unemployed, 2 self-employed, 3 employee,
#   4 worker, 5 doctor, 6 master), cov_life_event (0 none, 1 death,
#   2 divorce, 3 illness, 4 bankruptcy, 5 medication, 6 more than one),
#   cov_degree (1 completely, 2 normal, 3 not at all; the file does not say
#   degree of what).

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/nr9388gbzf/files/"
       "9afdf6b8-ea01-4bbd-8632-9a2a251dc296/file_downloaded")


def block(prefix, idx):
    return [f"{prefix}{i}" for i in idx]


# table suffix -> (item columns, composite column, composite label)
BLOCKS = {
    "absolute_thought": (block("AQ", range(1, 29)), "AA", "absolute"),
    "relativistic_thought": (block("BQ", range(1, 15)), "BB",
                             "relativistic"),
    "dialectical_thought": (block("CQ", range(1, 15)), "CC", "Dialectical"),
    "egocentrism": (block("DQ", range(1, 12)), "DD", "Egocentrism"),
    "stress": (block("EQ", range(1, 8)), "EE", "Stress"),
    "emotion_regulation": (block("FQ", range(1, 19)), "FF",
                           "emotion regulation difficulties"),
    "empathy": (block("GQ", range(1, 28)), "GG", "Empathy"),
    "spiritual_weakness": (block("HQ", range(1, 16)), "HH",
                           "spiritual weakness"),
    "spiritual_wellbeing": (block("IQ", range(1, 20)), "II",
                            "Spiritual well-being"),
    "aggression": (block("JQ", list(range(1, 8)) + list(range(10, 15))),
                   "JJ", "aggression"),
    "depression": (block("KQ", range(1, 14)), "KK", "depression"),
    "hedonism": (block("LQ", range(1, 9)), "LL", "hedonism"),
    "resilience": (block("MQ", range(1, 11)), "MM", "resilience"),
    "gratitude": (block("NQ", range(1, 7)), "NN", "Gratitude"),
    "altruism": (block("OQ", range(1, 16)), "QQ", "Altruistic"),
}
COVS = {"sex": "cov_sex", "age": "cov_age_band",
        "education": "cov_education", "religen": "cov_religion",
        "economic": "cov_economic", "job": "cov_job",
        "experience": "cov_life_event", "degree": "cov_degree"}


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
    assert d.shape == (700, 241), d.shape

    # Balance the books.
    items = {c for its, _, _ in BLOCKS.values() for c in its}
    comps = {c for _, c, _ in BLOCKS.values()}
    known = items | comps | set(COVS) | {"id"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not d.duplicated().any()
    assert not d.drop(columns="id").duplicated().any()
    assert d["id"].duplicated().sum() == 2

    for its, comp, lab in BLOCKS.values():
        assert meta.column_names_to_labels[comp] == lab, comp
        assert np.allclose(d[its].mean(axis=1), d[comp]), comp
        for c in its:
            assert not meta.column_names_to_labels.get(c), c
            assert c not in meta.variable_value_labels, c

    # The single non-integer cell.
    frac = (d[list(items)] % 1 != 0) & d[list(items)].notna()
    assert frac.values.sum() == 1 and frac["CQ5"].sum() == 1
    d["CQ5"] = d["CQ5"].mask(frac["CQ5"])

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for suffix, (its, _, _) in BLOCKS.items():
        table = f"mellat_2022_{suffix}"
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload")
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
