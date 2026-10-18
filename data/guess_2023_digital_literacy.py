#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XOIM0F (Harvard Dataverse)
# DOI: 10.7910/DVN/XOIM0F (dataset, 2022; Guess, Andrew M. & Munger, Kevin). "Replication Data for: Digital
#   Literacy and Online Political Behavior" (Political Science Research and Methods, 2023).
# Data: fb.tab, high.tab, low.tab, mturk.tab (Qualtrics exports; row 1 = question text, row 2 = import ids, data
#   from row 3). Four samples with the same 137-column instrument: Facebook-ad recruits (fb), tech-savvy
#   recruits (high), library-patron recruits (low), MTurk. lucid.tab is NOT used: a different, shorter
#   instrument (7 familiarity items, no Q98 block, no Q99 block), so it cannot share the item set.
#   Only respondents who answered the Q53 block are kept (the authors' own filter, 01a_clean_data.R).
# Tables:
#   guess_2023_web_skills      21 items, 1-5: self-rated understanding of computer/Internet terms (Hargittai-style
#                              web-use skills; Q53_1-11 + Q98_1-10). Q98_9 (Proxypod) and Q98_10 (Fitibly) are
#                              invented terms (overclaiming probes) and correlate ~0 with the rest; shipped as is.
#   guess_2023_tech_attitudes  12 items, 1-9 (Qualtrics codes of -4..+4 agree/disagree, 9 = strongly agree; the
#                              correlations confirm higher = more agreement): Q54_1-6 + Q99_1-6. Q54_1 ("gadgets
#                              are complicated") and Q99_1 ("prefer to ask friends") are reverse-worded and
#                              correlate -0.1 to -0.4 with the others; left unreversed per datastandard.md.
# Not shipped: Q100 (5 items, below the 8-item floor), the 3 CRT items (free text, would need scoring), Q60-Q93
#   knowledge items (4 free text), rumor ratings, demographics.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: the raw files carry MTurkCode (worker ID), Random ID and ResponseId; none is read. id = sample label plus
#   row index. Timing, browser and location columns are not read.
# cov_sample is fb / high / low / mturk. 1,080 respondents have the Q53 block.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_D_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (ingested .tab form for tabular files)."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", headers=UA, timeout=300)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert len(name) <= 40, name
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


SAMPLES = ["fb", "high", "low", "mturk"]
WEB = {f"Q53_{i}": f"web_{n}" for i, n in enumerate(
    ["phishing", "preference_setting", "app", "hashtag", "social_media", "status_update", "spyware", "selfie",
     "wiki", "advanced_search", "pdf"], 1)}
WEB.update({f"Q98_{i}": f"web_{n}" for i, n in enumerate(
    ["tagging", "tablet", "smartphone", "jpg", "malware", "cache", "bcc", "rss", "proxypod", "fitibly"], 1)})
ATT = {f"Q54_{i}": f"tech_q54_{i}" for i in range(1, 7)}
ATT.update({f"Q99_{i}": f"tech_q99_{i}" for i in range(1, 7)})


def long_table(d: pd.DataFrame, cols: dict, lo: int, hi: int) -> pd.DataFrame:
    x = d[["id", "cov_sample", *cols]].melt(id_vars=["id", "cov_sample"], var_name="item", value_name="resp")
    x["item"] = x["item"].map(cols)
    x["resp"] = pd.to_numeric(x["resp"], errors="coerce")
    x = x[x["resp"].notna()]
    assert x["resp"].between(lo, hi).all() and (x["resp"] % 1 == 0).all()
    x["resp"] = x["resp"].astype(int)
    x["o"] = x["item"].map({v: k for k, v in enumerate(cols.values())})
    x = x.sort_values(["id", "o"]).drop(columns="o").reset_index(drop=True)
    return x[["id", "item", "resp", "cov_sample"]]


def main() -> None:
    frames = []
    for s in SAMPLES:
        p = dv_fetch("10.7910/DVN/XOIM0F", f"{s}.tab", RAW_ROOT / "xoim0f")
        d = pd.read_csv(p, sep="\t", dtype=str).iloc[2:]
        d = d[d["Q53_1"].notna()].copy()
        d["cov_sample"] = s
        d["id"] = [f"{s}_{i}" for i in range(1, len(d) + 1)]
        frames.append(d[["id", "cov_sample", *WEB, *ATT]])
    d = pd.concat(frames, ignore_index=True)
    assert len(d) == 1080, len(d)
    web = long_table(d, WEB, 1, 5)
    att = long_table(d, ATT, 1, 9)
    emit({
        "guess_2023_web_skills": (web, {i: {1, 2, 3, 4, 5} for i in WEB.values()}),
        "guess_2023_tech_attitudes": (att, {i: set(range(1, 10)) for i in ATT.values()}),
    })


if __name__ == "__main__":
    main()
