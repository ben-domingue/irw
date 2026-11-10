#!/usr/bin/env python3
# Source: https://osf.io/s9xug/
# DOI: 10.1038/s41598-026-58879-z
#   "Affective reactivity to upward social comparisons rather than social media
#   use predicts increases in early adolescents' depressive symptoms" (Irmer &
#   Schmiedek, 2026), Scientific Reports 16:19189 (zEbra study).
# Data: OSF s9xug (CC BY 4.0), "Data and Analyses/zEbra_short.dat": the Mplus
#   analysis file, tab-separated, no header, "." = missing; its column names are
#   the NAMES line of zEbra_change_upcomp-na-depr_lat.inp in the same folder.
#   2,382 child-day rows for 200 children over up to 14 diary days. The
#   pretest/posttest depression items are repeated on every day row (constant
#   within child, checked).
#   Codebook: "zEbra codebook.xlsx" (osf.io/rjg83), sheets "Child pretest",
#   "Child daily", "Child posttest": item wording (German original + English),
#   source, and coding 1 'not at all true' .. 5 'completely true'.
# License: CC BY 4.0 (OSF project licence).
#
# Tables (id = SERIAL, the child):
#   irmer_2026_childs        childs_1..childs_8  1-5  wave 1 = pretest
#       (DS01_*), wave 2 = posttest (DP01_*). Children's Depression Screener
#       (ChilD-S; Fruehe et al. 2012), "how you have been feeling for the last 2
#       weeks". Items 1 ("I am happy") and 7 ("I am doing fine") are stored
#       REVERSE-SCORED in this file (DS01_1_r, DS01_7_r, DP01_1_r, DP01_7_r);
#       the other six are as answered.
#   irmer_2026_daily_upward  uc01_1..uc01_6      1-5  wave = diary day 1-14.
#       Daily upward social comparison on social media ("Today, I had the
#       feeling ... that others have a better life than me", ...), developed by
#       the authors from Boer et al. 2021, Vogel et al. 2014, Schmuck et al. 2019.
#   irmer_2026_daily_negaffect  ak_2, ak_4, ak_5, ak_8  1-5  wave = diary day.
#       Daily negative affect ("Today, I felt unhappy / sad / miserable /
#       afraid"; Leonhardt et al. 2015, Schmidt et al. 2019); the positive-affect
#       items are not in this file.
#
# Not shipped: msns_pmc / msns_gmc (person-mean-centred social-media use, derived).
#   Covariate: cov_female from sexc (1 for 103 children, 0 for 95, 2 missing;
#   the paper reports "200 early adolescents (103 female; ages 10-14)", so
#   1 = female).
#
# Item text: not shipped. The codebook carries German original and English
#   wording for every item (cheap), but the ChilD-S is a published screener
#   (Fruehe et al.) with no register row; the two daily blocks are
#   study-authored/adapted and could ship under the OSF CC BY once someone reads
#   the stems against their cited sources.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "irmer_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://osf.io/download/kmyhj/"
NAMES = ("SERIAL day sexc msns_pmc msns_gmc AK_02 AK_04 AK_05 AK_08 UC01_01 UC01_02 "
         "UC01_03 UC01_04 UC01_05 UC01_06 DS01_1_r DS01_02 DS01_03 DS01_04 DS01_05 "
         "DS01_06 DS01_7_r DS01_08 DP01_1_r DP01_02 DP01_03 DP01_04 DP01_05 DP01_06 "
         "DP01_7_r DP01_08").split()


def fetch() -> Path:
    p = RAW_DIR / "zEbra_short.dat"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def check_and_write(t: pd.DataFrame, name: str, items: list, sex: pd.Series) -> None:
    t = t.dropna(subset=["resp"]).copy()
    t["cov_female"] = t["id"].map(sex).astype("Int64")
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    pv = {i: {1, 2, 3, 4, 5} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    report = irw_validate.validate_frame(t, label=name, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def main() -> None:
    d = pd.read_csv(fetch(), sep="\t", header=None, na_values=".")
    assert d.shape == (2382, 31), d.shape
    d.columns = NAMES
    assert d["SERIAL"].nunique() == 200 and d["day"].between(1, 14).all()
    assert not d.duplicated(["SERIAL", "day"]).any()
    pre = [c for c in NAMES if c.startswith("DS01")]
    post = [c for c in NAMES if c.startswith("DP01")]
    assert (d.groupby("SERIAL")[pre + post].nunique(dropna=False) <= 1).all().all()

    person = d.drop_duplicates("SERIAL")
    assert person["sexc"].value_counts().to_dict() == {1.0: 103, 0.0: 95}
    sex = person.set_index("SERIAL")["sexc"]
    parts = []
    for wave, cols in ((1, pre), (2, post)):
        for k, c in enumerate(cols, 1):
            parts.append(pd.DataFrame({"id": person["SERIAL"], "item": f"childs_{k}",
                                       "resp": person[c], "wave": wave}))
    check_and_write(pd.concat(parts), "irmer_2026_childs", [f"childs_{k}" for k in range(1, 9)], sex)

    for name, cols, code in (("irmer_2026_daily_upward", [f"UC01_0{i}" for i in range(1, 7)],
                              lambda c: "uc01_" + c[-1]),
                             ("irmer_2026_daily_negaffect", ["AK_02", "AK_04", "AK_05", "AK_08"],
                              lambda c: "ak_" + c[-1])):
        t = d.melt(id_vars=["SERIAL", "day"], value_vars=cols, var_name="item", value_name="resp")
        t["item"] = t["item"].map(code)
        t = t.rename(columns={"SERIAL": "id", "day": "wave"})[["id", "item", "resp", "wave"]]
        check_and_write(t, name, sorted(t["item"].unique()), sex)


if __name__ == "__main__":
    main()
