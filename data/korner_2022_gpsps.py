#!/usr/bin/env python3
# Source: https://osf.io/jf9dz/  (German Personal Sense of Power Scale (GPSPS))
#   Study 1/Data Study 1.sav  https://osf.io/download/cs3kt/
#   Study 1/Data Retest.sav   https://osf.io/download/cgdj7/
#   Study 2/Data Study 2.sav  https://osf.io/download/rsxcd/
#   Study 3/Data Study 3.sav  https://osf.io/download/q23bm/
#   Study 4/Data Study 4.sav  https://osf.io/download/x65us/
#   Study 5/Data Study 5.sav  https://osf.io/download/fhme4/
# Paper DOI: 10.1027/1015-5759/a000642
#   Körner, R., Heydasch, T., & Schütz, A. (2022). It's all about power:
#   Validation of the German Personal Sense of Power Scale. European Journal of
#   Psychological Assessment, 38(1), 36-48.
# Data DOI: 10.17605/OSF.IO/JF9DZ
# License: CC BY 4.0 (OSF node jf9dz, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Instrument: German translation of the Personal Sense of Power Scale (Anderson,
#   John & Keltner 2012), 1 = stimme gar nicht zu ... 7 = stimme völlig zu. Items
#   are matched to one canonical numbering by their German wording (every .sav
#   carries the wording as the variable label), using Study 1's order:
#     gpsps_1 "Ich bekomme Menschen dazu, mir zuzuhören."
#     gpsps_2 "Meine Wünsche haben nicht viel Gewicht."                 (neg.)
#     gpsps_3 "Ich kann Menschen dazu bringen zu tun, was ich will."
#     gpsps_4 "Auch wenn ich meine Ansichten ausspreche, haben diese wenig Einfluss." (neg.)
#     gpsps_5 "Ich habe viel Macht."
#     gpsps_6 "Meine Ideen und Meinungen werden oft ignoriert."          (neg.)
#     gpsps_7 "Selbst wenn ich es versuche, kann ich mich nicht durchsetzen." (neg.)
#     gpsps_8 "Wenn ich will, dann treffe ich die Entscheidungen."
#   The final 6-item GPSPS drops gpsps_3 and gpsps_8 (Studies 4 and 5 use it).
#   Study 3 presented the items in a different order (its PS01_03 is gpsps_4 and
#   PS01_07 is gpsps_3), which the wording match resolves.
#
# Reverse keying: the four negatively worded items are ALREADY REVERSE-SCORED in
#   every file. All inter-item correlations are positive within each study
#   (asserted below), which raw negatively worded items could not produce, and
#   e.g. "Meine Wünsche haben nicht viel Gewicht" has a mean of 5.1-5.6 in the
#   general samples. Kept as deposited: higher = more sense of power on every item.
#
# Tables (one per study, as the samples and administrations differ):
#   korner_2022_gpsps_s1: Study 1, general adult sample, 8 items, with the
#     retest file as waves: wave 1 = Study 1, wave 2 = retest ~6 weeks later
#     (median interval 42 days), wave 3 = second retest. Waves are linked by the
#     participant's self-generated code, which is not output (id = row index of
#     Study 1). The retest file's t1 block is asserted identical to Study 1.
#     16 retest rows whose code matches no Study 1 participant (and who have no
#     t1 data) are dropped: they cannot be linked and may be mistyped codes.
#   korner_2022_gpsps_s2_partner: Study 2, 435 people in relationships answering
#     a partner-specific wording ("Ich bekomme ihn/sie dazu, mir zuzuhören").
#   korner_2022_gpsps_s3_clinical: Study 3, the clinical sample (sample == 2,
#     N = 183). The file's sample == 1 rows are the Study 1 participants with no
#     GPSPS responses and are not used. Six non-integer cells (e.g. 3.035,
#     4.474) are imputed values and are dropped.
#   korner_2022_gpsps_s4: Study 4, 175 adults, 6-item GPSPS after an
#     autobiographical recall manipulation (cov_condition high_power / low_power).
#   korner_2022_gpsps_s5: Study 5, 120 adults, 6-item GPSPS after a role
#     scenario manipulation (cov_condition high_power / low_power).
#   Covariates: age, gender (value labels), plus relationship status in Study 2.
#   -9 ("nicht beantwortet") and -99 are missing codes.
#
# Not taken: Study 1 also holds its validation battery (BIS/BAS, NARQ-S, pride,
#   PANAS, NPI-15, locus of control, and others). Those are outside this issue.
#   Free-text columns (job, recalled essays in Study 4, diagnoses in Study 3) and
#   the self-generated codes are never output.

import sys
import time
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
URLS = {
    "s1": "https://osf.io/download/cs3kt/",
    "retest": "https://osf.io/download/cgdj7/",
    "s2": "https://osf.io/download/rsxcd/",
    "s3": "https://osf.io/download/q23bm/",
    "s4": "https://osf.io/download/x65us/",
    "s5": "https://osf.io/download/fhme4/",
}
# wording fragment -> canonical item
KEYS = [("zuzuhören", 1), ("Wünsche", 2), ("zu tun, was ich will", 3),
        ("Ansichten", 4), ("viel Macht", 5), ("ignoriert", 6),
        ("durchsetzen", 7), ("Entscheidungen", 8)]
MISSING = [-9, -99]


def fetch(key: str):
    tmp = OUT_DIR / f".tmp_gpsps_{key}.sav"
    for attempt in range(5):
        r = requests.get(URLS[key], headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            tmp.write_bytes(r.content)
            try:
                return pyreadstat.read_sav(str(tmp))
            finally:
                tmp.unlink()
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{URLS[key]} failed after 5 attempts")


def item_map(meta, cols) -> dict:
    """source column -> gpsps_k, by the German wording in the variable label."""
    out = {}
    for c in cols:
        lab = meta.column_names_to_labels[c]
        hits = [k for frag, k in KEYS if frag in lab]
        assert len(hits) == 1, (c, lab, hits)
        out[c] = f"gpsps_{hits[0]}"
    assert len(set(out.values())) == len(out), out
    return out


def gender(s: pd.Series, meta, col: str) -> pd.Series:
    labels = meta.variable_value_labels[col]
    return s.map({k: v for k, v in labels.items() if k > 0})


def age(s: pd.Series) -> pd.Series:
    return s.where(s.between(10, 100))


def to_long(d: pd.DataFrame, cmap: dict, covs: list, wave=None) -> pd.DataFrame:
    x = d[["id"] + list(cmap) + covs].rename(columns=cmap)
    x = x.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    x = x[~x["resp"].isin(MISSING)].dropna(subset=["resp"])
    if wave is not None:
        x["wave"] = wave
    return x


def check_positive(d: pd.DataFrame, cols: list, what: str) -> None:
    x = d[cols].where(~d[cols].isin(MISSING))
    assert x.corr().values.min() > 0, what


def finish(t: pd.DataFrame, name: str) -> None:
    frac = t["resp"] != t["resp"].round()
    if frac.any():
        print(f"  {name}: dropping {int(frac.sum())} non-integer (imputed) cell(s)")
        t = t[~frac]
    t = t.copy()
    t["resp"] = t["resp"].astype(int)
    keys = ["id", "item"] + (["wave"] if "wave" in t else [])
    lead = ["id", "item", "resp"] + (["wave"] if "wave" in t else [])
    t = t[lead + [c for c in t.columns if c.startswith("cov_")]]
    t = t.sort_values(keys).reset_index(drop=True)
    assert not t.duplicated(keys).any()
    assert t["id"].nunique() >= 100
    items = sorted(t["item"].unique())
    pv = {i: set(range(1, 8)) for i in items}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {i: "personal_sense_of_power" for i in items}
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    extra = (f" waves={t.groupby('wave')['id'].nunique().to_dict()}"
             if "wave" in t else "")
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}{extra}")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Study 1 + retest
    s1, m1 = fetch("s1")
    rt, mr = fetch("retest")
    assert s1.shape == (573, 227) and s1["code"].is_unique and rt["code"].is_unique
    c1 = [f"GPSPS_{i}" for i in range(1, 9)]
    cmap1 = item_map(m1, c1)
    assert cmap1 == {f"GPSPS_{i}": f"gpsps_{i}" for i in range(1, 9)}
    check_positive(s1, c1, "s1")
    s1 = s1.reset_index(drop=True)
    s1["id"] = s1.index + 1
    s1["cov_age"] = age(s1["age"])
    s1["cov_gender"] = gender(s1["gender"], m1, "gender")
    covs = ["cov_age", "cov_gender"]
    unl = ~rt["code"].isin(s1["code"])
    assert unl.sum() == 16 and rt.loc[unl, c1].isna().all().all()
    print(f"  s1: dropping {int(unl.sum())} retest rows with no Study 1 match")
    rt = rt[~unl].merge(s1[["code", "id"] + covs], on="code", how="left")
    chk = s1.set_index("code")[c1].sort_index()
    assert (rt.set_index("code")[c1].sort_index() == chk).all().all()
    parts = [to_long(s1, cmap1, covs, wave=1)]
    for w, pre in ((2, "GPSPS_t2_"), (3, "GPSPS_t3_")):
        cols = [f"{pre}{i}" for i in range(1, 9)]
        cmap = item_map(mr, cols)
        assert list(cmap.values()) == [f"gpsps_{i}" for i in range(1, 9)]
        parts.append(to_long(rt, cmap, covs, wave=w))
    finish(pd.concat(parts, ignore_index=True), "korner_2022_gpsps_s1")

    # ---- Study 2 (partner wording)
    s2, m2 = fetch("s2")
    assert s2.shape == (435, 15)
    c2 = [f"PS01_0{i}" for i in range(1, 9)]
    check_positive(s2, c2, "s2")
    s2 = s2.reset_index(drop=True)
    s2["id"] = s2.index + 1
    s2["cov_age"] = age(s2["age"])
    s2["cov_gender"] = gender(s2["gender"], m2, "gender")
    s2["cov_relationship"] = gender(s2["relationship"], m2, "relationship")
    finish(to_long(s2, item_map(m2, c2), ["cov_age", "cov_gender", "cov_relationship"]),
           "korner_2022_gpsps_s2_partner")

    # ---- Study 3 (clinical sample only)
    s3, m3 = fetch("s3")
    assert s3.shape == (756, 22)
    assert (s3["sample"] == 1).sum() == 573
    c3 = [f"PS01_0{i}" for i in range(1, 9)]
    assert s3.loc[s3["sample"] == 1, c3].isna().all().all()
    s3 = s3[s3["sample"] == 2].reset_index(drop=True)
    assert len(s3) == 183
    check_positive(s3, c3, "s3")
    s3["id"] = s3.index + 1
    s3["cov_age"] = age(s3["age"])
    s3["cov_gender"] = gender(s3["gender"], m3, "gender")
    finish(to_long(s3, item_map(m3, c3), ["cov_age", "cov_gender"]),
           "korner_2022_gpsps_s3_clinical")

    # ---- Study 4 and 5 (6-item version, experimental manipulations)
    for key, tcol, gcol, acol, pre, cond in (
            ("s4", "treatment", "gender", "age", "GPSPS_",
             {1: "high_power", 2: "low_power"}),
            ("s5", "Treatment", "Gender", "Age", "PSOP_0",
             {1: "low_power", 2: "high_power"})):
        d, m = fetch(key)
        assert m.variable_value_labels[tcol] in (
            {1.0: "High Power", 2.0: "Low Power"}, {1.0: "Low Power", 2.0: "High Power"})
        assert {k: v.lower().replace(" ", "_") for k, v in
                m.variable_value_labels[tcol].items()} == cond
        cols = [f"{pre}{i}" for i in range(1, 7)]
        cmap = item_map(m, cols)
        assert sorted(cmap.values()) == [f"gpsps_{i}" for i in (1, 2, 4, 5, 6, 7)]
        check_positive(d, cols, key)
        d = d.reset_index(drop=True)
        d["id"] = d.index + 1
        d["cov_age"] = age(d[acol])
        d["cov_gender"] = gender(d[gcol], m, gcol)
        d["cov_condition"] = d[tcol].map(cond)
        assert d["cov_condition"].notna().all()
        finish(to_long(d, cmap, ["cov_age", "cov_gender", "cov_condition"]),
               f"korner_2022_gpsps_{key}")


if __name__ == "__main__":
    convert()
