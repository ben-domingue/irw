#!/usr/bin/env python3
# Source: https://osf.io/avwxs/  (EVACH-C-2021.sav, https://osf.io/download/7p8za/)
# Paper DOI: 10.1007/s11135-021-01311-7
#   Viñas-Velázquez, B. M., Mejía-Ramírez, M. A., Mendoza, M. E., Islas-Limón,
#   J. Y., & Capafons, A. (2022). Psychometric properties of the Valencia Scale
#   of Attitudes and Beliefs toward Hypnosis Client version (VSABH-C) in a
#   Mexican sample. Quality & Quantity, 56, 3685-3697.
# Data DOI: 10.17605/OSF.IO/AVWXS
# License: CC BY 4.0 (OSF node avwxs, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Table: vinasvelazquez_2022_vsabhc -- Valencia Scale of Attitudes and Beliefs
#   toward Hypnosis, Client version (Spanish, "EVACH-C"), 37 items T1-T37,
#   1 = completamente en desacuerdo ... 6 = completamente de acuerdo, 1,166
#   Mexican university students. wave 1 = test; wave 2 = the retest two months
#   later (RT1-RT37, the 139 participants flagged `retest`),
#   stored in the same row of the deposit, so ids link across waves.
#   Items are named by the source variable (T1_ayu ... T37_ctm); the retest
#   columns carry the same wording and map to the same names.
#   Factor keys (the authors' analysis code, Capafons et al. 2015 model):
#   interest 26/27/28, memory 3/30/31/32/33, help 1/10/12/17/23/29/37,
#   control 14/15/21/22/24/25, cooperation 2/8/13, marginal 34/35/36,
#   fear 4/7/16/18/19/20, magic 5/6/9. Item 11 (T11_pas) is in no factor; it
#   was administered and is kept.
#
# Reverse keying: the T*/RT* columns are RAW responses. The deposit's reversed
#   copies (T3_TRANR ... RT36_DISCR) are not used, nor the totals.
# Covariates: age, sex (hombre/mujer as labelled), country (value labels; 1,119
#   México). Occupation/degree text fields and the random-subsample flags
#   (`sel_random`, `filter_$`) are not carried. `codigo` (questionnaire number)
#   is replaced by the row index.

import sys
import time
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/7p8za/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "vinasvelazquez_2022_vsabhc"

FACTORS = {
    "interest": (26, 27, 28), "memory": (3, 30, 31, 32, 33),
    "help": (1, 10, 12, 17, 23, 29, 37), "control": (14, 15, 21, 22, 24, 25),
    "cooperation": (2, 8, 13), "marginal": (34, 35, 36),
    "fear": (4, 7, 16, 18, 19, 20), "magic": (5, 6, 9), "unassigned": (11,),
}


def fetch() -> tuple:
    tmp = OUT_DIR / ".tmp_evach.sav"
    for attempt in range(5):
        r = requests.get(URL, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            tmp.write_bytes(r.content)
            try:
                return pyreadstat.read_sav(str(tmp))
            finally:
                tmp.unlink()
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{URL} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, m = fetch()
    assert d.shape == (1166, 173), d.shape
    assert d["codigo"].is_unique
    T = list(d.columns[39:76])
    RT = [f"R{c}" for c in T]
    assert T[0] == "T1_ayu" and T[-1] == "T37_ctm" and len(T) == 37
    assert all(c in d.columns for c in RT)
    for a, b in zip(T, RT):   # same wording, "t01." vs "r01." prefix
        la, lb = m.column_names_to_labels[a], m.column_names_to_labels[b]
        assert la.split(".", 1)[1].strip()[:30] == lb.split(".", 1)[1].strip()[:30], (a, b)
    num = {c: int(c.split("_")[0][1:]) for c in T}
    assert sorted(num.values()) == list(range(1, 38))
    assert d.loc[d["retest"] != 1, RT].isna().all().all()

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_age"] = d["edad"]
    d["cov_sex"] = d["sexo"].map(m.variable_value_labels["sexo"])
    d["cov_country"] = d["país"].map(m.variable_value_labels["país"])
    covs = ["cov_age", "cov_sex", "cov_country"]
    parts = []
    for w, cols in ((1, T), (2, RT)):
        x = d[["id"] + cols + covs].rename(columns=dict(zip(cols, T)))
        x = x.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        x["wave"] = w
        parts.append(x)
    t = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    assert (t["resp"] == t["resp"].round()).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(
        ["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() >= 100

    pv = {c: set(range(1, 7)) for c in T}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {c: f for f, idx in FACTORS.items() for c in T if num[c] in idx}
    assert len(cl) == 37
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()} "
          f"waves={t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    convert()
