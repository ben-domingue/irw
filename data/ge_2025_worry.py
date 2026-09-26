#!/usr/bin/env python3
# Source: https://osf.io/h7nes/
# DOI: 10.3390/jintelligence13080090
#   "Pathways of Worry During the Transition to Adolescence: An Exploration of
#   Students' Emotion Regulation, Metacognitive Beliefs and Coping" (Ge &
#   Tolmie, 2025), Journal of Intelligence 13(8):90. PMC12387488.
# Data: osf.io/h7nes "Data.sav" (338 x 47, SPSS; https://osf.io/download/p5nfh/).
#       The node's "Supplementary Material.docx" holds the five coping scenarios.
# License: CC BY 4.0 on the OSF node (public; licence id 563c1cf88c5e4a3877f9e96a
#          resolves via api.osf.io/v2/licenses/ to "CC-By Attribution 4.0
#          International"); the article is also CC BY 4.0.
#
# Item text: available, not shipped here. SPSS variable labels carry the English
#   stem of every general-question item (e.g. inhibition_2 "I hold my worried
#   feelings in") and value labels carry the anchors; the coping items are
#   labelled only by strategy ("emotion-coping school scene"), and the scenario
#   texts are in the OSF Supplementary Material.docx. Administered in Mandarin
#   (translated and back-translated by the authors); only English is deposited.
#
# Sample: 338 sixth-grade pupils (ages 11-15) at two elementary schools in
# southeast China. `code` is a row number, used as id.
#
# Tables (all items 1-5):
#   ge_2025_cwms     Children's Worry Management Scale items: inhibition 1-4,
#                    dysregulation 1-3 (1 = Strongly disagree ... 5 = Strongly agree)
#   ge_2025_eesc     Emotion Expression Scale for Children, poor-awareness
#                    subscale, 8 items (worded for worry)
#   ge_2025_mcqcr    Metacognitions Questionnaire for Children-Revised, negative
#                    beliefs (controllability) 1-6 and cognitive
#                    self-consciousness 1-6
#   ge_2025_coping   scenario-based coping: 5 scenarios (school, peer, health,
#                    appearance, family) x 3 strategies (emotion-focused, social,
#                    problem-focused), 1 = Extremely unlikely ... 5 = Extremely likely
#
# inhibition_1 ("I show my worried feelings"): the file's value labels run
# 1 = Strongly agree ... 5 = Strongly disagree, the reverse of every other item,
# but the stored values follow the administered 1 = Strongly disagree order: the
# item correlates negatively with inhibition_2-4 and positively with
# dysregulation_1 (asserted below). It is shipped as stored, i.e. as
# administered, not reverse-keyed. inhibition_1rc is exactly 6 - inhibition_1
# (asserted) and is skipped as derived.
#
# No imputation (every item cell is an integer), no exact-duplicate rows, no PII.

import io
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/p5nfh/"


def load() -> pd.DataFrame:
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


def main() -> None:
    d = load()
    assert d.shape == (338, 47), d.shape
    assert d["code"].is_unique

    # inhibition_1 orientation (see header)
    assert (d["inhibition_1rc"] == 6 - d["inhibition_1"]).all()
    cor = d[["inhibition_1", "inhibition_2", "inhibition_3", "inhibition_4",
             "dysregulation_1"]].corr()["inhibition_1"]
    assert (cor[["inhibition_2", "inhibition_3", "inhibition_4"]] < 0).all()
    assert cor["dysregulation_1"] > 0

    scenes = ["School_1", "Peer_2", "Health_3", "Appear_4", "Family_5"]
    tables = {
        "ge_2025_cwms": [f"inhibition_{i}" for i in range(1, 5)]
                        + [f"dysregulation_{i}" for i in range(1, 4)],
        "ge_2025_eesc": [f"poorawareness_{i}" for i in range(1, 9)],
        "ge_2025_mcqcr": [f"negbelief_{i}" for i in range(1, 7)]
                         + [f"csc_{i}" for i in range(1, 7)],
        "ge_2025_coping": [f"Coping{s}{sc}" for sc in scenes
                           for s in ("Emo", "Social", "Prob")],
    }
    assert len(tables) == len(set(tables))

    # covariates: age is stored 1-5 with value labels 11-15
    d["cov_age"] = d["age"].map({1: 11, 2: 12, 3: 13, 4: 14, 5: 15})
    assert d["cov_age"].notna().all()
    d["cov_gender"] = d["gender"].map({1: "male", 2: "female"})
    cov_cols = ["cov_age", "cov_gender"]

    skipped = {
        "inhibition_1rc": "reverse-scored copy of inhibition_1 (= 6 - inhibition_1)",
        "grade": "constant in practice (337 of 338 = 2) and the codes 2/4 do not "
                 "match its value labels (1 = 5th, 2 = 6th); the paper says all "
                 "pupils were sixth graders",
    }
    item_cols = [c for items in tables.values() for c in items]
    assert len(item_cols) == len(set(item_cols))
    accounted = {"code", "age", "gender"} | set(item_cols) | set(skipped)
    orig = set(d.columns) - set(cov_cols)
    assert orig == accounted, orig ^ accounted
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")

    d = d.rename(columns={"code": "id"})
    d["id"] = d["id"].astype(int)
    for name, items in tables.items():
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: {1, 2, 3, 4, 5} for i in items}
        for i, s in pv.items():
            assert set(t.loc[t["item"] == i, "resp"]) <= s, (name, i)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
