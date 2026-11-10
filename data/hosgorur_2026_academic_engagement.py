#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.22063031
# DOI: 10.3390/bs16101806
#   "Fair Learning Environment and Financial Well-Being as Resources for
#   Students' Academic Engagement: Basic Psychological Need Satisfaction as a
#   Common Motivational Pathway" (Hosgorur & Yorulmaz, 2026), Behavioral
#   Sciences 16:1806.
# Data: Zenodo 22063031, five xlsx files ("analytic datasets"): four Sample 1
#   files, one per scale, and Sample2_AnalyticData_SEM.xlsx with all four scales.
#   Each file also carries the authors' scale means, z-scores and Mahalanobis
#   distances, which are derived and not shipped.
# License: CC BY-NC-SA 4.0 (Zenodo record). NC proceeds under the 2026-10-01
#   ruling; the derived licence carries it.
#
# Sample: university students in Turkiye, two non-overlapping samples (paper):
#   Sample 1 (scale evaluation, 278 students; after the paper's outlier screening
#   271 / 278 / 259 / 268 for the four scales, exactly the files' row counts),
#   Sample 2 (structural model, 741 students). Same instruments in both, so one
#   table per scale with cov_sample (1, 2); Sample 2 ids are offset by 1000 (the
#   deposit's IDs run 1-278 and 1-755).
#
# Tables (paper section 2.3; items keep the deposit's codes):
#   hosgorur_2026_fair_learning  FA1-FA8, FA10-FA16 (FA9 absent from both
#       files)  1-5 (1 disagree .. 5 strongly agree)  perceived fair learning
#       environment
#   hosgorur_2026_financial_wb   FWB1-FWB10  1-5  subjective financial well-being
#   hosgorur_2026_need_sat       PNS1-PNS12  1-5 (strongly disagree .. strongly
#       agree)  basic psychological need satisfaction (autonomy, relatedness,
#       competence), adapted to the academic context
#   hosgorur_2026_uwes9s         WE1-WE9  1-5 (1 never .. 5 always)  Turkish
#       UWES-9 student form (Capri et al. 2017)
#
# Item text: not shipped. Levels checked: xlsx headers are codes, no labels; the
#   paper quotes one sample item per scale. The wording is in the cited Turkish
#   adaptations, not in the deposit.

import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "hosgorur_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/22063031/files/{}/content"
S1 = {
    "FA": ("Sample1_AnalyticData_Fair Learning Environment.xlsx", 271),
    "FWB": ("Sample1_AnalyticData_Subjective Financial Well-Being.xlsx", 278),
    "PNS": ("Sample1_AnalyticData_Basic Psychological Need Satisfaction.xlsx", 259),
    "WE": ("Sample1_AnalyticData_Academic Engagement.xlsx", 268),
}
S2 = "Sample2_AnalyticData_SEM.xlsx"
TABLES = {"FA": "hosgorur_2026_fair_learning", "FWB": "hosgorur_2026_financial_wb",
          "PNS": "hosgorur_2026_need_sat", "WE": "hosgorur_2026_uwes9s"}
NITEMS = {"FA": 15, "FWB": 10, "PNS": 12, "WE": 9}


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        r = requests.get(BASE.format(requests.utils.quote(name)), headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def items_of(df: pd.DataFrame, prefix: str) -> list:
    return [c for c in df.columns if re.fullmatch(prefix + r"\d+", c)]


def main() -> None:
    s2 = pd.read_excel(fetch(S2))
    assert len(s2) == 741 and s2["ID"].is_unique
    for prefix, name in TABLES.items():
        f, n = S1[prefix]
        s1 = pd.read_excel(fetch(f))
        assert len(s1) == n and s1["ID"].is_unique and s1["ID"].max() < 1000
        its = items_of(s1, prefix)
        assert its == items_of(s2, prefix) and len(its) == NITEMS[prefix], (prefix, its)
        parts = []
        for sample, df, off in ((1, s1, 0), (2, s2, 1000)):
            t = df.melt(id_vars="ID", value_vars=its, var_name="item", value_name="resp")
            t["id"] = t["ID"] + off
            t["cov_sample"] = sample
            parts.append(t)
        t = pd.concat(parts).dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all()
        t = t[["id", "item", "resp", "cov_sample"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(x.check, x.message) for x in report.errors])
        for x in report.findings:
            print(f"    [{x.severity}] {x.check}: {x.message[:150]}")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
