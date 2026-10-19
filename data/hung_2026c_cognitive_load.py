#!/usr/bin/env python3

# Source: https://zenodo.org/records/19951727
# DOI: 10.5281/zenodo.19951727
#   Hung (2026). Temporal Associations Between Teacher Support and Academic
#   Procrastination [Dataset]. Zenodo.
# Data: "506.sav" -- 506 students, one administration, four instruments on a
#       shared 1-7 agreement scale.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: shipped. BOTH label levels checked -- SPSS variable labels carry the
#   authors' own ENGLISH stems for all 28 item columns, and value labels carry all
#   seven anchors ("Strongly disagree" .. "Strongly agree") for 30 columns. No
#   IRW-generated translation is involved, so nothing is owed on the issues page.
# Naming: this author already has hung_2026_* (zenodo.19784064 et al.) and
#   hung_2026b_* (zenodo.19784338, worked earlier in this same batch run), so this
#   deposit takes hung_2026c_*.
#
# Four tables, all 1-7:
#   hung_2026c_cognitive_load          10 items. IL1-3 intrinsic, EL4-6 extraneous,
#                                      GL7-10 germane -- Klepsch et al.'s three-factor
#                                      cognitive-load scale, one instrument.
#   hung_2026c_teacher_support          3 items (TS1, TS2, TS4; TS3 is absent from
#                                      the deposit, and the gap is the source's).
#   hung_2026c_procrastination          7 items. APP1/2/4/9 plus AP3R/AP5R/AP6R, which
#                                      the author's own codes mark reverse-keyed; the
#                                      deposit stores them already reversed (its APRmean
#                                      equals their plain mean), so resp ships as-is.
#   hung_2026c_academic_self_efficacy   8 items (ASE1-ASE8).
# Not shipped: the nine *mean columns (ILmean, ELmean, GLmean, CLmean, TSmean,
#   APPmean, APRmean, APmean, ASEmean) -- derived scale scores, not items.
# id: the deposit's 序号 is a 1..506 serial and is unique, so it is used directly.
# Covariates: cov_gender, cov_age, cov_grade.
# Rights: none of these four is in the instrument rights register. Checked by reading
#   the stems, not only the code prefixes -- the register's code matchers miss
#   subscale-named items (154 of its 243 block rows match nothing at all).
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "19951727"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 19951727, "506.sav"

BLOCKS = {
    "hung_2026c_cognitive_load": ["IL1", "IL2", "IL3", "EL4", "EL5", "EL6",
                                  "GL7", "GL8", "GL9", "GL10"],
    "hung_2026c_teacher_support": ["TS1", "TS2", "TS4"],
    "hung_2026c_procrastination": ["APP1", "APP2", "APP4", "APP9",
                                   "AP3R", "AP5R", "AP6R"],
    "hung_2026c_academic_self_efficacy": ["ASE1", "ASE2", "ASE3", "ASE4",
                                          "ASE5", "ASE6", "ASE7", "ASE8"],
}
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Grade": "cov_grade"}
DERIVED = ["ILmean", "ELmean", "GLmean", "CLmean", "TSmean", "APPmean",
           "APRmean", "APmean", "ASEmean"]
SCALE = list(range(1, 8))


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    df = df.rename(columns={"序号": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].is_unique, "序号 does not identify a respondent"

    # Balance the books: every source column is the id, a covariate, an item in
    # one of the four blocks, or a named derived column.
    items = {c for cols in BLOCKS.values() for c in cols}
    accounted = {"id"} | set(COVS) | items | set(DERIVED)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    for c in DERIVED:
        print(f"  skipped {c}: derived scale mean, not an item")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *COVS, *cols]]
             .melt(id_vars=["id", *COVS], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"])
             .rename(columns=COVS))
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - set(SCALE))
        assert not bad, f"{name}: resp outside the documented 1-7 scale: {bad}"
        for c in COVS.values():
            t[c] = t[c].astype("Int64")
        t = t[["id", "item", "resp", *COVS.values()]]

        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100, f"{name}: N below the floor"
        assert t["item"].nunique() >= 2, f"{name}: single-item table"
        assert name not in written, f"duplicate output name {name}"

        pv = set(SCALE)   # the seven anchors the SPSS value labels document
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:180]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")

        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
