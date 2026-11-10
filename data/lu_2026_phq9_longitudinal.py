#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13333126
# DOI: 10.7717/peerj.21498
#   "Intensity-specific leisure-time physical activity and depressive symptoms
#   among first-year university students: a four-wave longitudinal study"
#   (Lu, Zhu, Chen, Wen & Yao, 2026), PeerJ 14:e21498.
# Data: the article's supplementary files (Europe PMC supplementaryFiles zip):
#   peerj-14-21498-s003.xlsx, sheet "DS-36": id + y1..y36, the PHQ-9 item scores
#   at four waves; its "explanation" sheet: "y1-y9 correspond to the scores of
#   each question on the depression scale in the first round of testing;
#   y10-y18 ... second round; y19-y27 ... third round; ... y28-y36 ... fourth
#   round. The scoring range for each question is from 0 (not at all) to 3
#   (nearly every day). 999 indicates a missing value. No reverse scoring
#   items." peerj-14-21498-s001.xlsx holds gender, age and the wave totals
#   DS1..DS4 (= the item sums, checked below); s002.xlsx is its codebook
#   ("gender 1 = Male; 2 = Female").
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: 456 first-year university students in China (ages 17-22), four waves.
#   The two sheets are row-aligned (every complete wave's item sum equals that
#   row's DS total in s001); DS-36's last row repeats the id of its 0-based row 79 (a typo: s001
#   has ...111 there), so rows are joined by position and `id` is the row index.
#
# Dropped: two rows whose 36 PHQ-9 responses exactly copy another row's (row 81
#   = row 68, sum 32; row 455 = row 79, sum 37), while their physical-activity
#   records differ (0-based row numbers) - a copied item block, not a duplicate person. The later row
#   of each pair is dropped, as ruled for exact-copy pairs on Csibra 2025
#   (BATCH_LOG 2026-09-26). The other exact matches are all-zero or all-missing
#   patterns, which occur by chance.
#
# Table:
#   lu_2026_phq9  phq9_1..phq9_9  0-3  wave 1-4   PHQ-9 (Kroenke et al. 2001)
#   999 cells are dropped.
#   Not shipped: the leisure-time physical activity frequencies (0-7 days per
#   intensity, s003 "Frequency-LTPA") and the MET scores - activity counts, not
#   item responses.
#
# Covariates: gender, age.
#
# Item text: not shipped. Levels checked: xlsx headers are positional (y1..y36),
#   no value labels; the paper names the PHQ-9 but the deposit carries no wording.
#   Administered in Chinese; the official Chinese PHQ-9 would be a stand-in.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "lu_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13333126/supplementaryFiles"
FILES = ["peerj-14-21498-s001.xlsx", "peerj-14-21498-s003.xlsx"]
NAME = "lu_2026_phq9"


def fetch() -> dict:
    paths = {f: RAW_DIR / f for f in FILES}
    if not all(p.exists() for p in paths.values()):
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for f in FILES:
            paths[f].write_bytes(z.read([n for n in z.namelist() if n.endswith(f)][0]))
    return paths


def main() -> None:
    p = fetch()
    ds = pd.read_excel(p["peerj-14-21498-s003.xlsx"], sheet_name="DS-36")
    s = pd.read_excel(p["peerj-14-21498-s001.xlsx"])
    assert ds.shape == (456, 37) and s.shape == (456, 26)
    y = [f"y{i}" for i in range(1, 37)]
    assert list(ds.columns) == ["id"] + y
    assert (ds["id"].values == s["id"].values).sum() == 455  # all but DS-36's last row
    for w in range(4):
        cols = y[w * 9:(w + 1) * 9]
        ok = (ds[cols] != 999).all(axis=1)
        assert (ds.loc[ok, cols].sum(axis=1).values == s.loc[ok, f"DS{w + 1}"].values).all(), w
    assert ds[y].isin([0, 1, 2, 3, 999]).all().all()
    for keep, drop in [(68, 81), (79, 455)]:
        assert (ds.loc[keep, y] == ds.loc[drop, y]).all()
    keep_rows = [i for i in range(456) if i not in (81, 455)]

    w = pd.DataFrame({"id": range(1, 457), "cov_gender": s["gender"].map({1: "male", 2: "female"}),
                      "cov_age": s["age"]})
    assert w["cov_gender"].notna().all()
    long = []
    for wave in range(1, 5):
        for k in range(1, 10):
            long.append(pd.DataFrame({"id": w["id"], "item": f"phq9_{k}", "resp": ds[f"y{(wave - 1) * 9 + k}"],
                                      "wave": wave, "cov_gender": w["cov_gender"], "cov_age": w["cov_age"]}))
    t = pd.concat(long)
    t = t[t["id"].isin([i + 1 for i in keep_rows])]
    t = t[t["resp"] != 999]
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    print(f"  {t['id'].nunique()} ids; rows per wave {t.groupby('wave').size().to_dict()}")

    items = [f"phq9_{k}" for k in range(1, 10)]
    pv = {i: {0, 1, 2, 3} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
