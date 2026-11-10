#!/usr/bin/env python3
# Source: https://doi.org/10.23668/psycharchives.21746
# DOI: 10.23668/psycharchives.21746 (data; the article is not yet linked)
#   Brouwer, C., Bolderdijk, J. W., & Cornelissen, G. (2026). "Datasets for:
#   'Communicating meat-free principles without coming across as the veg*n
#   judge - Is demonstrating self-compassion the antidote?'" PsychArchives.
# Data: the two semicolon-separated study files + their codebooks
#   (Study 1: 456 omnivores, video vignettes; Study 2: 446 omnivores,
#   written-text vignettes). Qualtrics exports, all rows Finished = 1.
# License: CC BY-SA 4.0 (dc.rights.uri on the PsychArchives item).
#
# Item text: not shipped -- the codebooks carry the full English stems and
#   anchors for every item (cheap), but this pass builds response tables
#   only; the state self-regard list and the meat-justification statements
#   are adapted from published scales (rights not yet checked).
#
# SCALE: 1-7 on every shipped item (codebook: 1 = totally not applicable /
#   not at all / strongly disagree .. 7).
#
# Tables (codes are the Qualtrics names in the codebooks):
#   brouwer_2026_state_self_regard  Study 1, Q19_1-Q19_15 ("At this moment I
#       feel ___": happy with myself ... defective in some way), as answered
#   brouwer_2026_reading_emotions   Study 2, Q25_1-Q25_8 (anxiety, sadness,
#       nervousness, excitement, tension, pleasure, discomfort, boredom felt
#       while reading the text)
#   brouwer_2026_meat_justification Study 2, Q28_1-Q28_6 (animals don't
#       suffer ... we need meat for a healthy diet)
# Each carries cov_condition (the codebook's 4 vignette conditions:
#   morally-neutral / morally-motivated / self-compassionate /
#   self-judgmental), assigned between persons; not `treat` (4 arms).
# Not shipped: attention checks, 1- and 2-item measures (target liking,
#   Q20/Q26 anticipated moral judgment, anticipated respect, challenge
#   likelihoods, consumption frequencies), Q4 activity list (Study 1, with an
#   embedded instructed-response item), computed scale scores, timings.
# Covariates: cov_condition, cov_gender (codebook labels), cov_age.
# id: row index + 1 within each study (no respondent id in the files).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
PA = "https://www.psycharchives.org/rest/bitstreams/"
STUDY1 = PA + "6214e84f-7004-4572-991f-f32105ce98aa/retrieve"
STUDY2 = PA + "476cb3ca-72b8-4d41-88cc-24c97b4f5f94/retrieve"
COND = {1: "morally-neutral", 2: "morally-motivated", 3: "self-compassionate",
        4: "self-judgmental"}
GENDER = {1: "female", 2: "male", 3: "prefer not to say"}
TABLES = [
    ("brouwer_2026_state_self_regard", 1, [f"Q19_{i}" for i in range(1, 16)]),
    ("brouwer_2026_reading_emotions", 2, [f"Q25_{i}" for i in range(1, 9)]),
    ("brouwer_2026_meat_justification", 2, [f"Q28_{i}" for i in range(1, 7)]),
]
ALLOWED = set(range(1, 8))


def load(url, shape):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), sep=";")
    assert d.shape == shape, d.shape
    assert (d["Finished"] == 1).all()
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_condition"] = d["Condition"].map(COND)
    d["cov_gender"] = d["Gender"].map(GENDER)
    d["cov_age"] = d["Age"]
    assert d["cov_condition"].notna().all()
    return d


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    studies = {1: load(STUDY1, (456, 66)), 2: load(STUDY2, (446, 60))}
    cov_cols = ["cov_condition", "cov_gender", "cov_age"]
    for table, st, cols in TABLES:
        d = studies[st]
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED, (table, set(long["resp"]))
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: ALLOWED for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
