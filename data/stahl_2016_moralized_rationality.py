#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0166332
# DOI: 10.1371/journal.pone.0166332
# Paper: Stahl T, Zaal MP, Skitka LJ (2016). Moralized Rationality: Relying on
#   Logic and Evidence in the Formation and Evaluation of Belief Can Be Seen
#   as a Moral Issue. PLoS ONE 11(11): e0166332.
# Data: PLOS SI S1-S8 File (journal.pone.0166332.s001-s008, one .sav per
#   study; US online samples). Each study's `Filter` (duplicate IPs /
#   extremely fast responders; 0 = Not Selected) is applied as the authors
#   did; Study 8 has no Filter. S5 Text lists all variables.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A; scouted by
#   overnight-1110 lane A).
#
# THREE output tables, items as answered, studies stacked (same items,
#   same wording -- variable labels checked identical across studies -- and
#   same response format; labels compared on their first 30 letters, since
#   study 4 has a one-word typo in MR4; MFQ labels that hold only the
#   truncated section stem are skipped), `cov_study` = study number, id = study*10000 + row:
#   stahl_2016_moralized_rationality  Moralized Rationality Scale, final
#     9-item form, 1-7: mr_1..mr_7 and the reverse-worded mr_8r, mr_9r (the
#     deposit's MR8R/MR9R, raw answers). Studies 3-8.
#   stahl_2016_importance_rationality  Importance of Rationality Scale,
#     6 items (IR1-IR6), 1-7. Studies 3-8.
#   stahl_2016_mfq30  Moral Foundations Questionnaire (30 items: harm,
#     fairness, loyalty, authority, purity x 6; catch items not in the
#     deposit), coded 1-6. Studies 1, 3, 6, 7, 8.
#   Study 1 (15/14-item development pool) and Study 2 (8/6-item interim
#   versions) MR/IR items are different item sets and are not shipped.
# Covariates: study, gender (1 male / 2 female), age.

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0166332.s{:03d}"
RAW_DIR = os.environ.get("STAHL2016_RAW_DIR")  # holds s1.sav .. s8.sav

MFQ = [f"{f}{i}" for i in range(1, 7) for f in ("Harm", "Fairness", "Loyalty", "Authority", "Purity")]
MR = [f"MR{i}" for i in range(1, 8)] + ["MR8R", "MR9R"]
IR = [f"IR{i}" for i in range(1, 7)]


def load(study):
    if RAW_DIR:
        path = os.path.join(RAW_DIR, f"s{study}.sav")
    else:
        r = requests.get(URL.format(study), headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"_stahl2016_s{study}_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW_DIR:
        os.remove(path)
    if "Filter" in df.columns:
        df = df[df["Filter"] == 1]
    df = df.reset_index(drop=True).copy()
    df["id"] = study * 10000 + df.index + 1
    df["cov_study"] = study
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_age"] = pd.to_numeric(df["Age"], errors="coerce")
    labels = {c: " ".join((meta.column_names_to_labels.get(c) or "").replace("?", "'").replace("’", "'").split())
              for c in df.columns}
    return df, labels


def stack(studies, cols, rename, name, values):
    parts, ref = [], None
    covs = ["cov_study", "cov_gender", "cov_age"]
    for s in studies:
        df, labels = load(s)
        lab = [re.sub(r"[^a-z]", "", labels[c].lower())[:30] for c in cols]
        if ref is None:
            ref = lab
        stems = ("whenyoudecide", "pleasereadthe")  # truncated stem-only labels
        assert all(a == b or a.startswith(stems) or b.startswith(stems)
                   for a, b in zip(lab, ref)), (s, name)
        sub = df[["id"] + covs + cols].rename(columns=rename)
        parts.append(sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp"))
    long = pd.concat(parts, ignore_index=True)
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    mr = {c: re.sub(r"^MR(\d)(R?)$", lambda m: f"mr_{m.group(1)}{m.group(2).lower()}", c) for c in MR}
    stack(range(3, 9), MR, mr, "stahl_2016_moralized_rationality", range(1, 8))
    stack(range(3, 9), IR, {c: f"ir_{c[2:]}" for c in IR}, "stahl_2016_importance_rationality", range(1, 8))
    stack([1, 3, 6, 7, 8], MFQ, {c: re.sub(r"(\D+)(\d)", lambda m: f"{m.group(1).lower()}_{m.group(2)}", c) for c in MFQ},
          "stahl_2016_mfq30", range(1, 7))


if __name__ == "__main__":
    convert()
