#!/usr/bin/env python3
# Source: Open-Source Psychometrics Project raw data, https://openpsychometrics.org/_rawdata/
#   MGKT_data.zip   (Multifactor General Knowledge Test, 2017-2018; codebook.txt + data.csv)
#   FSIQ_0.1_data.zip (the "Full Scale IQ Test": vocabulary, mental rotation and
#                      short-term memory subtests; codebook.txt + data.csv + demo/*.js)
# Licence: as the existing score tables (IRW dictionary rows for mgkt and fullscaleiq_*):
#   MGKT Original "Permission via Email", FSIQ Original "Missing (NA)"; Derived CC BY 4.0.
# Issues: ben-domingue/irw#2662 (MGKT) and #2660 (fullscaleiq). Ruled by Ben 2026-10-01.
#
# WHAT IT IS. Every question in these tests is a multi-select: the respondent sees a
#   list of options (MGKT 10, of which 5 are correct; FSIQ 8, of which 3-5 are
#   correct) and ticks as many as they are sure of. The source stores the ticked set
#   in click order (MGKT `QXA`, e.g. "A0A2A1"; FSIQ `XQna`, e.g. "2,4,3,1") and a
#   hits-minus-false-alarms score (`QXS` / `XQns`), which is what the existing score
#   tables (mgkt, fullscaleiq_vocab/_mentalrotation/_memory) carry as resp.
#
# THE RULING (#2660/#2662): unfold each question into one binary row per person x
#   option. item = <question>_opt<k>; resp = 1 if the option was ticked, 0 if not.
#   Click order is dropped. These are NEW companion tables; the score tables stay.
#   item_family = the question, since the options of one question share a stem.
#   The key (which options are correct) is in metadata/data_notes.csv and, once the
#   tables are live, in their item text; it is not a column.
#
# id = row index of data.csv (1-based), exactly as data/mgkt.r and data/fullscaleiq.R
#   assign it, so a person's id is the same in the score table and its _options
#   companion (checked against live mgkt on 2026-10-01: ids 1507 and 2116 match).
#   mgkt_options carries the same four covariates as mgkt; the FSIQ score tables carry
#   none. cov_age over 120 is blanked (see mgkt()). Response time (per question,
#   not per option) stays in the score tables.
#
# Option numbering <k>:
#   MGKT: the codebook's own answer codes A0..A9 -> opt0..opt9. Option texts are in
#     the codebook's question block.
#   FSIQ vocabulary (VQ1-VQ7): the stored code 1..8, which indexes the word list
#     `vitems` in demo/subtest-V.js (e.g. VQ1 "big": 1 large ... 8 crumbled).
#   FSIQ mental rotation (RQ1-RQ6): stored code 10q+k -> opt<k>, k = 1..8 (the
#     option images are shapes.json keys "10q+k" in demo/subtest-MRT.js).
#   FSIQ memory (MQ1-MQ6): stored codes are icon ids (icons.json "I<id>"); opt<k> is
#     the icon's position, 1..8, in that question's option list `seq_key[q][1]` in
#     demo/subtest-ISM.js (MEMORY_OPTIONS below).
#
# THE KEY IS DERIVED, AND CHECKED. Neither codebook lists the correct options outright
#   (MGKT's says A0-A4 are correct only implicitly; FSIQ's not at all). For every
#   question the script solves score = sum(weight x ticked) by least squares over all
#   respondents, asserts every weight is exactly +1 (correct) or -1 (incorrect) and
#   that the weights reproduce every stored score. For MGKT that gives A0-A4 = +1 for
#   all 32 questions; for FSIQ memory it reproduces the demo's seq_key (the icons that
#   were in the sequence).
#
# No ticks at all is a real response (the person saw the question and ticked none;
#   its score is 0), so it unfolds to all-zero rows. Neither file has a missing score.

import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://openpsychometrics.org/_rawdata/"

MEMORY_OPTIONS = {          # demo/subtest-ISM.js seq_key[q][1]; correct = seq_key[q][0]
    1: [1, 2, 3, 4, 51, 52, 53, 54],
    2: [5, 6, 7, 55, 56, 57, 58, 59],
    3: [8, 9, 10, 11, 60, 61, 62, 63],
    4: [12, 13, 14, 15, 16, 64, 65, 66],
    5: [17, 18, 19, 20, 21, 67, 68, 69],
    6: [22, 23, 24, 25, 26, 70, 71, 72],
}
MEMORY_SEQUENCE = {1: {1, 2, 3, 4}, 2: {5, 6, 7}, 3: {8, 9, 10, 11},
                   4: {12, 13, 14, 15, 16}, 5: {17, 18, 19, 20, 21}, 6: {22, 23, 24, 25, 26}}


def fetch_zip(name: str) -> zipfile.ZipFile:
    r = requests.get(BASE + name, headers=UA, timeout=300)
    r.raise_for_status()
    return zipfile.ZipFile(BytesIO(r.content))


def read_data(z: zipfile.ZipFile) -> pd.DataFrame:
    (path,) = [n for n in z.namelist() if n.endswith("/data.csv")]
    return pd.read_csv(z.open(path), dtype=str, keep_default_na=False)


def derive_key(ticks: np.ndarray, score: np.ndarray, label: str) -> np.ndarray:
    """Weights w with score == ticks @ w; asserted to be exactly +/-1."""
    w, *_ = np.linalg.lstsq(ticks.astype(float), score.astype(float), rcond=None)
    w = np.rint(w)
    assert set(w) <= {-1.0, 1.0}, (label, w)
    assert (ticks @ w == score).all(), label
    return w.astype(int)


def unfold(ids, ticks, question, opts, family):
    """ticks: n x K 0/1 matrix -> long rows id, item, resp, item_family."""
    n, k = ticks.shape
    return pd.DataFrame({
        "id": np.repeat(ids, k),
        "item": np.tile([f"{question}_opt{o}" for o in opts], n),
        "resp": ticks.reshape(-1),
        "item_family": family,
    })


def finish(table: str, long: pd.DataFrame, n_ids: int, n_items: int, keys: dict):
    assert long["id"].nunique() == n_ids and long["item"].nunique() == n_items
    assert len(long) == n_ids * n_items
    assert not long.duplicated(["id", "item"]).any()
    assert long["resp"].isin([0, 1]).all()
    pv = {i: {0, 1} for i in long["item"].unique()}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{table}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} ticked={long['resp'].mean():.3f}")
    for q, (opts, w) in keys.items():
        print(f"    key {q}: correct = {[o for o, x in zip(opts, w) if x == 1]}")


def mgkt():
    d = read_data(fetch_zip("MGKT_data.zip"))
    assert len(d) == 19218
    ids = np.arange(1, len(d) + 1)
    parts, keys = [], {}
    for q in range(1, 33):
        sel = d[f"Q{q}A"].map(lambda s: re.findall(r"A(\d)", s))
        assert (d[f"Q{q}A"].str.replace(r"A\d", "", regex=True) == "").all()
        assert sel.map(lambda x: len(x) == len(set(x))).all()
        ticks = np.array([[int(str(o) in s) for o in range(10)] for s in sel], dtype=int)
        w = derive_key(ticks, d[f"Q{q}S"].astype(int).to_numpy(), f"Q{q}")
        assert list(w) == [1] * 5 + [-1] * 5, (q, w)   # A0-A4 correct, A5-A9 not
        keys[f"Q{q}"] = (list(range(10)), w)
        parts.append(unfold(ids, ticks, f"Q{q}", range(10), f"Q{q}"))
    long = pd.concat(parts, ignore_index=True)
    # covariates exactly as data/mgkt.r reads them (read.csv: "" and "NA" -> NA)
    cov = pd.DataFrame({"id": ids,
                        "cov_age": pd.to_numeric(d["age"].replace("NA", ""), errors="coerce"),
                        "cov_gender": pd.to_numeric(d["gender"].replace("NA", ""), errors="coerce"),
                        "cov_engnat": pd.to_numeric(d["engnat"].replace("NA", ""), errors="coerce"),
                        "cov_country": d["country"].replace("NA", np.nan).replace("", np.nan)})
    # ages over 120 (up to 67998) are typing errors or birth years; blank them, as the
    # validator requires (#1779). The mgkt score table still carries them.
    print(f"    cov_age > 120 blanked for {(cov['cov_age'] > 120).sum()} people")
    cov.loc[cov["cov_age"] > 120, "cov_age"] = np.nan
    long = long.merge(cov, on="id", how="left", validate="many_to_one")
    long = long[["id", "item", "resp", "cov_age", "cov_gender", "cov_engnat",
                 "cov_country", "item_family"]]
    long = long.sort_values(["id"], kind="stable")   # per person: Q1 opt0..9, Q2 ...
    finish("mgkt_options", long.reset_index(drop=True), 19218, 320, keys)


def fsiq():
    d = read_data(fetch_zip("FSIQ_0.1_data.zip"))
    assert len(d) == 3194
    ids = np.arange(1, len(d) + 1)
    for prefix, nq, table in (("V", 7, "fullscaleiq_vocab_options"),
                              ("R", 6, "fullscaleiq_mentalrotation_options"),
                              ("M", 6, "fullscaleiq_memory_options")):
        parts, keys = [], {}
        for q in range(1, nq + 1):
            if prefix == "V":
                codes = list(range(1, 9))
            elif prefix == "R":
                codes = [10 * q + k for k in range(1, 9)]
            else:
                codes = MEMORY_OPTIONS[q]
            sel = d[f"{prefix}Q{q}a"].map(lambda s: [int(c) for c in s.split(",") if c])
            assert sel.map(lambda x: len(x) == len(set(x)) and set(x) <= set(codes)).all()
            ticks = np.array([[int(c in s) for c in codes] for s in sel], dtype=int)
            w = derive_key(ticks, d[f"{prefix}Q{q}s"].astype(int).to_numpy(), f"{prefix}Q{q}")
            if prefix == "M":
                assert {c for c, x in zip(codes, w) if x == 1} == MEMORY_SEQUENCE[q], q
            opts = list(range(1, 9))
            keys[f"{prefix}Q{q}"] = (opts, w)
            parts.append(unfold(ids, ticks, f"{prefix}Q{q}", opts, f"{prefix}Q{q}"))
        long = pd.concat(parts, ignore_index=True).sort_values(
            ["id"], kind="stable").reset_index(drop=True)
        finish(table, long, 3194, nq * 8, keys)


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fsiq()
    mgkt()
