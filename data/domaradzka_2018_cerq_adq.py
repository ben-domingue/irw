#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/r45ht8hrnb (version 1)
# DOI: 10.3389/fpsyg.2018.00856
#   Domaradzka, E., & Fajkowska, M. (2018). "Cognitive Emotion Regulation
#   Strategies in Anxiety and Depression Understood as Types of
#   Personality." Frontiers in Psychology, 9, 856. (Read from Europe PMC
#   full text, PMC6005992; the deposit's related link points at it.)
#   Dataset: Domaradzka, E., & Fajkowska, M. (2018). Cognitive emotion
#   regulation strategies in types of anxiety and depression. Mendeley Data,
#   v1. https://doi.org/10.17632/r45ht8hrnb.1
# Data: "CERQ ADQ database raw publish.sav" (1,632 rows x 277 columns; Polish
#       online-panel sample, 18-65). The deposit's SPSS syntax file ("CERQ ADQ
#       syntax publish.sps") states the items are NOT recoded and gives every
#       subscale's item list.
# License: CC BY 4.0 (Mendeley Data API, data_licence short_name).
#
# Item text: not shipped. Both label levels checked. CERQ01-36 carry the
#   full English CERQ stems as variable labels and English anchors as value
#   labels ((almost) never .. (almost) always). The study was administered
#   in Polish (Marszal-Wisniewska & Fajkowska 2010 adaptation) and no Polish
#   wording is in the deposit, so it would be a translated_substitute
#   fallback for an instrument not in the rights register -- left as a lead.
#   ADQ items: no variable labels; value labels only "I agree"/"I disagree".
#   ADQ stems are in Fajkowska et al. (2018) (not in this deposit).
#
# Scale identities and ranges (paper, Materials and methods): the CERQ is 36
# items rated 1 (almost) never .. 5 (almost) always; the Anxiety and
# Depression Questionnaire (ADQ; Fajkowska et al. 2018) has four scales,
# each answered Agree/Disagree. Both value-label sets match (asserted) and
# are the permitted sets. Arousal Anxiety is 45 items "including 4 fillers";
# the file holds the 41 scored ones (ArA04/17/21/34 absent). The .sps scores
# every remaining item into a subscale.
#
# Tables (item codes are the source column names; responses as stored,
# 1 = I agree, 2 = I disagree for the ADQ, unreversed per the .sps):
#   domaradzka_2018_cerq                   CERQ01-CERQ36 (1-5)
#   domaradzka_2018_adq_valence_depression    VD02-VD40, 36 items (1-2)
#   domaradzka_2018_adq_anhedonic_depression  AD01-AD64, 64 items (1-2)
#   domaradzka_2018_adq_apprehension_anxiety  ApA01-ApA48, 48 items (1-2)
#   domaradzka_2018_adq_arousal_anxiety       ArA01-ArA45, 41 items (1-2)
#   The four ADQ types are scored and analysed as separate scales, so each
#   is its own table.
#
# Dropped: every computed column (ADQ subscale/type scores, raw "2" counts,
#   per-scale filters, CERQ_var, the nine CERQ strategy scores and three
#   means). Their definitions are re-derived and asserted where cheap.
# Kept in full: the paper removed 286 low-variance "click-through"
#   respondents. They are kept here and flagged with cov_paper_excluded
#   (ADQ_CERQ_filter: 1 = removed from the paper's analysis; 286 asserted).
# id: row index. "Id" is a permutation of 1..1632 (asserted), a study
#   sequence number, and is not shipped.
# Covariates: cov_sex (1 female, 2 male), cov_age, cov_paper_excluded.

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/r45ht8hrnb/files/"
       "8ffefd75-8969-4caf-9203-89c1e9df9715/file_downloaded")

CERQ = [f"CERQ{i:02d}" for i in range(1, 37)]
VD = [f"VD{i:02d}" for i in range(2, 41) if i not in (13, 32, 37)]
AD = [f"AD{i:02d}" for i in range(1, 65)]
APA = [f"ApA{i:02d}" for i in range(1, 49)]
ARA = [f"ArA{i:02d}" for i in range(1, 46) if i not in (4, 17, 21, 34)]
TABLES = {
    "domaradzka_2018_cerq": CERQ,
    "domaradzka_2018_adq_valence_depression": VD,
    "domaradzka_2018_adq_anhedonic_depression": AD,
    "domaradzka_2018_adq_apprehension_anxiety": APA,
    "domaradzka_2018_adq_arousal_anxiety": ARA,
}
CERQ_LABELS = {1.0: "(almost) never", 2.0: "sometimes", 3.0: "regularly",
               4.0: "often", 5.0: "(almost) always"}
ADQ_LABELS = {1.0: "I agree", 2.0: "I disagree"}
COMPOSITES = {
    "VD_NA", "VD_AA", "VD", "AD_MD1", "AD_MD2", "AD_MD", "AD_PA", "AD_NA",
    "AD_AC", "AD", "ArA_SR1", "ArA_SR2", "ArA_SR", "ArA_PP1", "ArA_PP2",
    "ArA_PP", "ArA_AA", "ArA", "ApA_WT1", "ApA_WT2", "ApA_WT", "ApA_AC1",
    "ApA_AC2", "ApA_AC", "ApA_SR1", "ApA_SR2", "ApA_SR", "ApA",
    "ApA_raw_2", "ArA_raw_2", "VD_raw_2", "AD_raw_2", "ApA_filter",
    "ArA_filter", "AD_filter", "CERQ_var", "SelfBlame", "Acceptance",
    "Rumination", "PosRefocus", "RefocusPlan", "PosReappr", "PuttingPersp",
    "Catastroph", "OtherBlame", "AdaptStrat", "MaladaptStrat", "CERQ_mean"}
COVS = {"sex": "cov_sex", "age": "cov_age",
        "ADQ_CERQ_filter": "cov_paper_excluded"}


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
    assert d.shape == (1632, 277), d.shape

    # Balance the books.
    items = {c for its in TABLES.values() for c in its}
    known = items | COMPOSITES | set(COVS) | {"Id"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(items) == 36 + 36 + 64 + 48 + 41

    assert sorted(d["Id"]) == list(range(1, 1633))
    assert not d.duplicated().any()
    assert not d[sorted(items)].T.duplicated().any()
    for c in CERQ:
        assert meta.variable_value_labels[c] == CERQ_LABELS, c
    for c in items - set(CERQ):
        assert meta.variable_value_labels[c] == ADQ_LABELS, c
    # Raw "2" counts in the .sps cover exactly these item sets.
    for prefix, its in (("VD", VD), ("AD", AD), ("ApA", APA), ("ArA", ARA)):
        assert (d[f"{prefix}_raw_2"] == (d[its] == 2).sum(axis=1)).all()
    assert (d["VD"] == (d[VD] == 1).sum(axis=1)).all()
    assert int(d["ADQ_CERQ_filter"].sum()) == 286

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(range(1, 6)) if table.endswith("cerq") else {1, 2}
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
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
