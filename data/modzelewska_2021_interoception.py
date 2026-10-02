#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8706328
# DOI: 10.7717/peerj.12542
#   "Interoceptive awareness and beliefs about health and the body as
#   predictors of the intensity of emotions experienced at the beginning of the
#   pandemic" (Modzelewska & Imbir, 2021), PeerJ 9:e12542.
# Data: Supplemental File peerj-09-12542-s001.sav (299 x 103), fetched from the
#       Europe PMC supplementaryFiles zip. Polish adults, Qualtrics online
#       survey, spring 2020.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. Checked both .sav label levels. Variable labels: the
#   20 emotion items carry the English emotion word ("Suffering",
#   "Helplessness", ...), the 10 belief items carry full English stems ("I
#   believe that my health is in danger."), the 32 MAIA items carry only a
#   subscale tag ("Noticing1"). Value labels: numeric only ("1".."7",
#   "0".."5"), no anchors. The administered wording was Polish (paper: emotion
#   words given with Polish originals in Methods; MAIA = Polish MAIA; anchors
#   "1 = to a small extent ... 7 = to a significant extent"), not in the deposit.
#
# Tables:
#   modzelewska_2021_emo_neg   10 negative emotions (Emo_neg_aut1-5,
#                              Emo_neg_ref1-5), current intensity 1-7
#   modzelewska_2021_emo_pos   10 positive emotions (Emo_pos_aut1-5,
#                              Emo_pos_ref1-5), current intensity 1-7
#     The paper splits the 20-emotion list by valence (and origin); the two
#     valences are analysed as separate constructs, so they ship separately.
#   modzelewska_2021_maia      MAIA, 32 items. Stored codes 1-6 carry value
#                              labels "0".."5"; resp is the labelled 0-5 score
#                              (asserted label == code - 1).
#   modzelewska_2021_hbeliefs  10 beliefs about health and the body in the
#                              epidemic, 1-5 agreement
# The *_rek columns are reverse-coded copies of MAIA5-9 and are skipped, as are
# all means, z-scores and recoded demographics. No missing cells, no PII (age,
# gender, place size, education, income, health yes/no only).

import io
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8706328/"
           "supplementaryFiles")
FNAME = "peerj-09-12542-s001.sav"

NEG = [f"Emo_neg_aut{i}" for i in range(1, 6)] + [f"Emo_neg_ref{i}" for i in range(1, 6)]
POS = [f"Emo_pos_aut{i}" for i in range(1, 6)] + [f"Emo_pos_ref{i}" for i in range(1, 6)]
MAIA = [f"MAIA{i}" for i in range(1, 33)]
BEL = ["Beliefs1"] + [f"Beliefs1{i}" for i in range(2, 11)]
TABLES = {
    "modzelewska_2021_emo_neg": (NEG, set(range(1, 8))),
    "modzelewska_2021_emo_pos": (POS, set(range(1, 8))),
    "modzelewska_2021_maia": (MAIA, set(range(0, 6))),
    "modzelewska_2021_hbeliefs": (BEL, set(range(1, 6))),
}
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Place": "cov_place",
        "Education": "cov_education", "income_source": "cov_income_stable",
        "income_evaluation": "cov_income_eval",
        "illnesses": "cov_chronic_illness",
        "knowing_COVID_illed": "cov_knows_covid_case",
        "COVID_experience": "cov_had_covid"}
SKIP = {
    "Duration__in_seconds_": "whole-survey completion time",
    "time_in_minutes": "whole-survey completion time",
    "Log_reaction_time": "derived from completion time",
    "ZLog_reaction_time": "derived from completion time",
    **{c: "reverse-coded copy of a MAIA item"
       for c in ["NotDistracting5_rek", "NotDistracting6_rek",
                 "NotDistracting7_rek", "NotWorrying8_rek", "NotWorrying9_rek"]},
    **{c: "scale/subscale mean" for c in [
        "Mean_emo_neg_tot", "Mean_emo_neg_aut", "Mean_emo_neg_ref",
        "Mean_emo_pos_tot", "Mean_emo_pos_aut", "Mean_emo_pos_ref",
        "Mean_noticing", "Mean_distracting", "Mean_Not_worrying",
        "Mean_Regulation", "Mean_Awareness", "Mean_Self_Regulation",
        "Mean_Listenning", "Mean_Trusting", "emo_pos_1", "emo_pos_2",
        "emo_MAIA_tot", "beliefs1_mean", "beliefs2_mean"]},
    **{c: "recoded (dichotomised) copy of a covariate" for c in [
        "gender_reversed", "perceived_financial_status_final",
        "source_income_final", "perceived_status_final"]},
}


def fetch_zip() -> bytes:
    # Europe PMC's REST endpoint returns intermittent 502/503s; retry.
    for attempt in range(6):
        try:
            r = requests.get(ZIP_URL, headers=UA, timeout=300)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(20 * (attempt + 1))


def load():
    content = fetch_zip()
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        blob = z.read(FNAME)
    with tempfile.NamedTemporaryFile(suffix=".sav") as tf:
        tf.write(blob)
        tf.flush()
        return pyreadstat.read_sav(tf.name)


def convert() -> None:
    d, meta = load()
    assert d.shape == (299, 103), d.shape

    items_all = NEG + POS + MAIA + BEL
    acc = set(items_all) | set(COVS) | set(SKIP)
    assert set(d.columns) == acc and len(d.columns) == len(acc), \
        set(d.columns) ^ acc
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert not d.duplicated().any()

    # MAIA: stored 1..6, labelled "0".."5"
    for c in MAIA:
        vl = meta.variable_value_labels[c]
        assert all(str(int(k) - 1) == v for k, v in vl.items()), (c, vl)
        d[c] = d[c] - 1

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    names = []
    for table, (items, allowed) in TABLES.items():
        assert table not in names
        names.append(table)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        bad = set(long["resp"]) - allowed
        assert not bad, (table, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: allowed for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            (table, [(f.check, f.message) for f in rep.errors])
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
