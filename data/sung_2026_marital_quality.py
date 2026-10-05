#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13066615
# DOI: 10.1038/s41598-026-41697-8
#   "Discordance in gender role attitudes between spouses and its relationship
#   with the risk biomarkers of cardiovascular diseases: a couple-level
#   analysis" (Sung, Kim, Park, Kim & Youm, 2026), Scientific Reports 16:11881.
# Data: figshare 10.6084/m9.figshare.30814394, kshap_apim_public_v1.xlsx
#       (308 couples x 70 columns, one row per couple, h_* husband and w_* wife).
# License: CC BY 4.0 (figshare record, checked via api.figshare.com/v2/articles/30814394).
#
# Item text: not shipped. Levels checked: the xlsx has no variable labels; the six
#   marital-quality columns carry label STRINGS rather than codes, and those
#   strings contradict the paper's coding (see below), so they cannot serve as
#   option text. The question wording and the 3-point coding are printed in the
#   paper's Methods ("Marital quality is measured using six questions ..."); the
#   column names tie to them by content (p_open = "How often can you open up to
#   your spouse?"), which is paper_explicit, not data_labels.
#
# Sample: 308 married couples (616 individuals) aged 60+ from two rural cohorts
# of the Korean Social Life, Health, and Aging Project (KSHAP).
#
# Table: sung_2026_marital_quality -- the six perceived-marital-quality questions
#   (NSHAP-derived), coded 1-3 as in the paper:
#     p_feel       closeness (1 = not very / somewhat close, 2 = very close, 3 = extremely close)
#     p_freetime   free time together or apart (1 = mostly apart ... 3 = mostly together)
#     p_open, p_rely, p_demand, p_criticize
#                  how often (1 = never/hardly ever/rarely, 2 = some of the time, 3 = often)
#   One row per spouse: id = 2*couple-1 (husband) / 2*couple (wife); the couple
#   is cluster_id and cov_spouse says which partner answered.
#
# Coding of the label strings. p_feel is numeric 1-3 in the deposit. The other
# five are strings ("Never" / "Hardly ever of rarely" / "Some of the time";
# "Different/seperate things" / "Some together, some different" / "Together").
# Read literally they give "often" to nobody of 616 on any of four items and put
# 54% of couples' free time "apart". The deposit's own composites settle it:
# h_/w_positive (mean of items 1-4) and h_/w_negative (mean of items 5-6) are
# reproduced exactly, for all 616 spouses, only by Never=1, Hardly ever=2, Some
# of the time=3 and Different/separate=3, Some together=2, Together=1 (all 36
# permutation pairs tried; asserted below). So the strings are shifted labels on
# the authors' 1-3 codes, and the codes, not the strings, are shipped.
#
# Not shipped: the single gender-role-attitude item (h_/w_gender; one item),
# CES-D (only a total score), biomarkers, health behaviours, ADL/IADL bands.
# No PII: ages, years of education, an anonymised cohort letter.

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "sung_2026_marital_quality"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/60165671"
NAME = "sung_2026_marital_quality"

FREQ = ["Never", "Hardly ever of rarely", "Some of the time"]
FREE = ["Different/seperate things", "Some together, some different", "Together"]
FREQ_CODE = dict(zip(FREQ, (1, 2, 3)))
FREE_CODE = dict(zip(FREE, (3, 2, 1)))
ITEMS = ["p_feel", "p_freetime", "p_open", "p_rely", "p_demand", "p_criticize"]
# per-spouse covariates carried (source suffix -> cov name)
COVS = {"age": "cov_age", "eduy": "cov_education_years", "work": "cov_working"}


def fetch() -> Path:
    p = RAW_DIR / "kshap_apim_public_v1.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def code(d: pd.DataFrame, s: str, freq: dict, free: dict) -> pd.DataFrame:
    out = pd.DataFrame({"p_feel": d[f"{s}_p_feel"], "p_freetime": d[f"{s}_p_freetime"].map(free)})
    for it in ITEMS[2:]:
        out[it] = d[f"{s}_{it}"].map(freq)
    return out


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (308, 70), d.shape
    assert d["id"].is_unique and d["id"].tolist() == list(range(1, 309))
    used = {"id", "myeon_c"} | {f"{s}_{c}" for s in "hw" for c in ITEMS + list(COVS)}
    skipped = [c for c in d.columns if c not in used]
    print(f"  [skip] {len(skipped)} columns: gender-role item, CES-D total, biomarkers, "
          f"health behaviours, ADL/IADL, income, composites: {skipped}")
    assert len(skipped) == 70 - len(used)

    for s in "hw":
        assert set(d[f"{s}_p_feel"]) == {1, 2, 3}
        assert set(d[f"{s}_p_freetime"]) == set(FREE)
        for it in ITEMS[2:]:
            assert set(d[f"{s}_{it}"]) <= set(FREQ), (s, it)
        # only one string->code assignment reproduces the authors' composites
        hits = []
        for pm in itertools.permutations((1, 2, 3)):
            for fm in itertools.permutations((1, 2, 3)):
                x = code(d, s, dict(zip(FREQ, pm)), dict(zip(FREE, fm)))
                pos = x[ITEMS[:4]].mean(axis=1)
                neg = x[ITEMS[4:]].mean(axis=1)
                if np.allclose(pos, d[f"{s}_positive"]) and np.allclose(neg, d[f"{s}_negative"]):
                    hits.append((pm, fm))
        assert hits == [((1, 2, 3), (3, 2, 1))], (s, hits)
    print("  [coding] composites reproduced exactly only by Never=1/Hardly=2/Some=3, "
          "Different=3/Some together=2/Together=1 (both spouses)")

    parts = []
    for k, (s, role) in enumerate((("h", "husband"), ("w", "wife"))):
        x = code(d, s, FREQ_CODE, FREE_CODE)
        x.insert(0, "id", 2 * d["id"] - 1 + k)
        x["cluster_id"] = d["id"]
        x["cov_spouse"] = role
        for src, cov in COVS.items():
            x[cov] = d[f"{s}_{src}"]
        x["cov_cohort"] = d["myeon_c"]
        parts.append(x)
    w = pd.concat(parts, ignore_index=True)
    assert w["id"].is_unique and len(w) == 616
    cov_cols = ["cov_spouse"] + list(COVS.values()) + ["cov_cohort"]
    t = w.melt(id_vars=["id", "cluster_id"] + cov_cols, value_vars=ITEMS,
               var_name="item", value_name="resp")
    assert t["resp"].notna().all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "cluster_id"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 616 and set(t["item"]) == set(ITEMS)
    pv = {i: {1, 2, 3} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
