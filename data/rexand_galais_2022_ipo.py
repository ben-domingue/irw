#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/tv6w6yyfy8/4
# DOI: 10.17632/tv6w6yyfy8.4 (dataset; first version 2022; no paper linked on the record)
#   Rexand-Galais, Franck & Pithon, Lucas (2022-2024). "Dataset assessing three
#   samples of French university students to 5 personality tests: IPO, PDQ-4+,
#   PANAS, AQ and HADS" [data set]. Mendeley Data, V4.
# Data (Angers University students, 2021-2022; French administration):
#   Study 1 Sample 1.xlsx -- 269 first-year psychology students x the 57-item
#     Inventory of Personality Organization (Kernberg & Clarkin; French
#     translation): PD1-16 primitive defenses, ID1-21 identity diffusion, RT1-20
#     reality testing (the record's text says RT = 21 items; the file has 20, as
#     the original IPO-57 does), plus Age, Gender. Title row above the header.
#   Study 1 Sample 2.xlsx -- 333 second-year psychology students, the same 57
#     items (columns in a different order), Age, Gender.
#   Study 2_V4.xlsx -- 305 students: SCALE TOTALS ONLY (IPO, HADS, PANAS, AQ
#     subscales, a PDQ-4+ group) -- no item responses, not shipped.
#   Study 3 V4.xlsx -- 607 students x the 40-item IPO-fr (the authors' French
#     short form, Pithon & Rexand-Galais 2023): "IPO PD/ID1-30" + "IPO RT1-10",
#     the three IPO-fr totals (not shipped), "GROUPS PDQ-4+", Age, Gender.
#   IPO Codebook V2.pdf -- the IPO-fr in French and in the authors' English
#     translation, each item followed by its data-file code, and the 1-5 options
#     (1 = Jamais vrai ... 5 = Toujours vrai; "Il n'y a pas d'item inverse").
# License: CC BY 4.0 (Mendeley record, data_licence).
#
# Tables:
#   rexand_galais_2022_ipo    Study 1, both samples pooled (same 57 items, same
#                             1-5 format): 602 students, cov_study 1 = first-year
#                             sample, 2 = second-year sample; id = row index,
#                             sample 2 offset past sample 1.
#   rexand_galais_2022_ipofr  Study 3: 607 students x 40 IPO-fr items, 1-5. Item
#                             codes derived reversibly from the headers: drop the
#                             "IPO " prefix and the "/" ("IPO PD/ID7" -> "PDID7",
#                             "IPO RT3" -> "RT3"). cov_pdq4_group = the deposit's
#                             PDQ-4+ classification (Cluster A/B/C, No PD).
#   The IPO-57 and the IPO-fr are different item sets (the IPO-fr is a selected,
#   re-worded, re-numbered 40-item form), so they are not pooled.
#
# Item text: rexand_galais_2022_ipofr shipped (deposit codebook PDF, which prints
#   each French stem and the authors' English translation followed by its data
#   code; built by automated_finding/itemtext_verification/
#   make_itemtext_rexand_galais_2022.py). rexand_galais_2022_ipo not shipped: the
#   xlsx has codes only (no variable or value labels) and the codebook covers only
#   the IPO-fr; the IPO-57 French wording used in Study 1 is not in the deposit.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "rexand_galais_2022"
UA = {"User-Agent": "Mozilla/5.0 (IRW-Finder/1.0; ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/tv6w6yyfy8"   # latest = V4 (asserted)
FILES = ["Study 1 Sample 1.xlsx", "Study 1 Sample 2.xlsx", "Study 2_V4.xlsx",
         "Study 3 V4.xlsx", "IPO Codebook V2.pdf"]
IPO57 = ([f"PD{i}" for i in range(1, 17)] + [f"ID{i}" for i in range(1, 22)]
         + [f"RT{i}" for i in range(1, 21)])
IPOFR_SRC = [f"IPO PD/ID{i}" for i in range(1, 31)] + [f"IPO RT{i}" for i in range(1, 11)]
IPOFR = {c: c.replace("IPO ", "").replace("/", "") for c in IPOFR_SRC}


def fetch() -> dict:
    out = {f: RAW_DIR / f for f in FILES}
    if not all(p.exists() for p in out.values()):
        meta = requests.get(API, headers=UA, timeout=120).json()
        assert meta["data_licence"]["short_name"] == "CC BY 4.0" and meta["version"] == 4
        urls = {f["filename"]: f["content_details"]["download_url"] for f in meta["files"]}
        assert set(urls) == set(FILES), urls
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for f in FILES:
            r = requests.get(urls[f], headers=UA, timeout=300)
            r.raise_for_status()
            out[f].write_bytes(r.content)
    return out


def finish(t, name, items, covs):
    t = t.dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 6)).all(), name
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(items) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    pv = {i: {1, 2, 3, 4, 5} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=name, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def main() -> None:
    p = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("  [skip] Study 2_V4.xlsx: scale totals only (IPO, HADS, PANAS, AQ, PDQ-4+ group)")

    # Study 1: two samples, same 57 items
    frames, offset = [], 0
    for k, f in enumerate(FILES[:2], start=1):
        d = pd.read_excel(p[f], header=1)
        d.columns = [c.strip() for c in d.columns]
        assert sorted(d.columns) == sorted(IPO57 + ["Age", "Gender"]), d.columns
        d["id"] = range(offset + 1, offset + len(d) + 1)
        offset = int(d["id"].max())
        d["cov_study"] = k
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    assert len(d) == 602
    d = d.rename(columns={"Age": "cov_age", "Gender": "cov_gender"})
    d["cov_gender"] = d["cov_gender"].str.strip()
    covs = ["cov_study", "cov_age", "cov_gender"]
    t = d.melt(id_vars=["id"] + covs, value_vars=IPO57, var_name="item", value_name="resp")
    finish(t, "rexand_galais_2022_ipo", IPO57, covs)

    # Study 3: IPO-fr
    d = pd.read_excel(p[FILES[3]], header=1).dropna(axis=1, how="all")
    totals = ["IPO-fr Tot", "IPO PD/ID", "IPO RT"]
    assert d.columns.tolist() == totals + IPOFR_SRC + ["GROUPS PDQ-4+", "Age", "Gender"]
    assert len(d) == 607
    print(f"  [skip] Study 3 totals {totals}: sums of the shipped items")
    d.insert(0, "id", range(1, len(d) + 1))
    d = d.rename(columns={"GROUPS PDQ-4+": "cov_pdq4_group", "Age": "cov_age",
                          "Gender": "cov_gender", **IPOFR})
    covs = ["cov_age", "cov_gender", "cov_pdq4_group"]
    t = d.melt(id_vars=["id"] + covs, value_vars=list(IPOFR.values()),
               var_name="item", value_name="resp")
    finish(t, "rexand_galais_2022_ipofr", list(IPOFR.values()), covs)


if __name__ == "__main__":
    main()
