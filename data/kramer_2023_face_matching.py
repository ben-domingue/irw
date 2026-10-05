#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9884031
# DOI: 10.7717/peerj.14821
#   "Face matching and metacognition: investigating individual differences and a
#   training intervention" (Kramer, 2023), PeerJ 11:e14821.
# Data: PeerJ supplementary file peerj-11-14821-s001.xlsx from the Europe PMC
#       supplementaryFiles zip. Four sheets: "Training" (220 x 6, per-person
#       proportion correct / d' scores), "Training and metacognition" (36,960 rows
#       = 220 people x 168 EFCT trials), "Predicting GFMT2-SA responses" (8,800 =
#       220 x 40 GFMT2-SA trials) and "Predicting EFCT responses" (18,480 = the
#       pre-training half of the EFCT sheet again).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary file.
#
# Item text: not shipped. Both tests are photograph pairs ("same person or two
#   different people?"); the stimuli are the GFMT2-SA (White et al. 2022) and the
#   EFCT (White et al. 2015) image sets, not in the deposit. Picture-stimulus
#   tasks ship with item_text blank, so there is nothing cheap to add. No
#   variable or value labels exist (xlsx).
#
# Item identity. `Trial number` is the stimulus, not the presentation position:
#   the paper randomised trial order per participant yet models trials as a
#   crossed random effect, and in the EFCT sheet each person's pre-training half
#   is trials 1-84 (subtest A) or 85-168 (subtest B) with the other half
#   post-training, following the paper's counterbalancing of A/B (asserted).
#   Per-trial accuracy also spreads far beyond what position would give
#   (GFMT2-SA 0.44-0.95, EFCT 0.25-0.92).
#
# Sample: 220 online participants. `PID` is the testing platform's participant
#   number; it is replaced by a row index (1..220, in PID order), never hashed.
#
# Tables (resp = trial accuracy, 1 correct / 0 incorrect, two-alternative
# same/different choice):
#   kramer_2023_gfmt2sa  Glasgow Face Matching Test 2 short version A, 40 trials,
#                        items gfmt2sa_1..gfmt2sa_40
#   kramer_2023_efct     Expertise in Facial Comparison Test, 168 trials, items
#                        efct_1..efct_168; wave 1 = before, 2 = after the
#                        training course; treat 1 = diagnostic feature training,
#                        0 = control course (randomly allocated)
#
# Skipped: the 0-5 confidence rating given after each trial (a metacognitive
# judgement about the response, not a second response to the item); the
# per-person PI20 and GFMT2-SA scores (standardised composites); the "Training"
# sheet (per-person summary scores); the "Predicting EFCT responses" sheet
# (identical to the pre-training rows of the EFCT sheet -- asserted).
# The two attention-check trials per test are not in the deposit.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9884031/supplementaryFiles"


def load() -> dict:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_excel(io.BytesIO(z.read("peerj-11-14821-s001.xlsx")), sheet_name=None)


def gate(t: pd.DataFrame, name: str) -> None:
    pv = {i: {0, 1} for i in t["item"].unique()}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    report = irw_validate.validate_frame(
        t, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")


def main() -> None:
    x = load()
    assert set(x) == {"Training", "Training and metacognition",
                      "Predicting GFMT2-SA responses", "Predicting EFCT responses"}, set(x)
    tr, ef = x["Training"], x["Training and metacognition"]
    gf, ef_pre = x["Predicting GFMT2-SA responses"], x["Predicting EFCT responses"]
    assert tr.shape == (220, 6) and ef.shape == (36960, 6)
    assert gf.shape == (8800, 6) and ef_pre.shape == (18480, 6)
    assert list(ef.columns) == ["PID", "Test", "Training", "Trial number",
                                "Trial accuracy", "Trial confidence"]
    assert list(gf.columns) == ["PID", "Self-assessed ability (PI20)",
                                "Objective ability (GFMT2-SA)", "Trial number",
                                "Trial accuracy", "Trial confidence"]
    print("  [skip] Trial confidence: metacognitive rating of the response")
    print("  [skip] Self-assessed ability (PI20), Objective ability (GFMT2-SA): standardised composites")
    print("  [skip] sheet 'Training': per-person summary scores")
    print("  [skip] sheet 'Predicting EFCT responses': duplicate of EFCT pre-training rows")

    pids = sorted(set(tr["PID"]))
    assert len(pids) == 220 and set(ef["PID"]) == set(pids) == set(gf["PID"])
    idmap = {p: i + 1 for i, p in enumerate(pids)}

    # the redundant sheet really is the pre-training half
    m = ef[ef["Test"] == "pre-training"].merge(ef_pre, on=["PID", "Trial number"],
                                                suffixes=("", "_p"))
    assert len(m) == 18480 and (m["Trial accuracy"] == m["Trial accuracy_p"]).all()

    # item identity: each person's pre half is exactly subtest A (1-84) or B (85-168)
    halves = ef.groupby(["PID", "Test"])["Trial number"].agg(["min", "max", "count"])
    assert set(map(tuple, halves.values.tolist())) == {(1, 84, 84), (85, 168, 84)}
    assert (ef.groupby("PID")["Trial number"].nunique() == 168).all()
    assert (gf.groupby("PID")["Trial number"].nunique() == 40).all()
    assert ef.groupby("PID")["Training"].nunique().max() == 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    name = "kramer_2023_gfmt2sa"
    t = pd.DataFrame({
        "id": gf["PID"].map(idmap),
        "item": "gfmt2sa_" + gf["Trial number"].astype(int).astype(str),
        "resp": gf["Trial accuracy"].astype(int),
    }).sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["item"].nunique() == 40
    gate(t, name)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")

    name = "kramer_2023_efct"
    assert set(ef["Test"]) == {"pre-training", "post-training"}
    assert set(ef["Training"]) == {"diagnostic feature", "control"}
    t = pd.DataFrame({
        "id": ef["PID"].map(idmap),
        "item": "efct_" + ef["Trial number"].astype(int).astype(str),
        "resp": ef["Trial accuracy"].astype(int),
        "wave": ef["Test"].map({"pre-training": 1, "post-training": 2}),
        "treat": (ef["Training"] == "diagnostic feature").astype(int),
    }).sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any() and t["item"].nunique() == 168
    gate(t, name)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
