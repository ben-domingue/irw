#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/2IBBMG
# DOI: 10.1037/aca0000439
#   Zabelina, D. L., Zaonegina, E., Revelle, W., & Condon, D. M. (2022). "Creative
#   achievement and individual differences: Associations across and within the
#   domains of creativity", Psychology of Aesthetics, Creativity, and the Arts.
#   Preprint: PsyArXiv 10.31234/osf.io/h2rp8 (its Appendix, pp. 47-57, prints the
#   expanded CAQ and its scoring instructions).
# Data: Harvard Dataverse 10.7910/DVN/2IBBMG, "Reproducibility Data for: Creative
#       Achievement and Individual Differences" (Condon, David; Zabelina, Darya; ...
#       deposited 2021-03-22). CAQ.csv (file 10993748, format=original): 5651 SAPA
#       respondents x RID + 140 CAQ columns. CAQTAIE.rdata (file 10993749) holds the
#       same CAQ frame (CAQ052013) plus TAIE: 63486 SAPA-Project respondents
#       (20 May 2013 - 10 Jun 2014) x RID, gender, age band and 770 SAPA
#       personality/ICAR/ORVIS items. sapaData20may2013thru10jun2014 (10993755) is
#       the same TAIE frame as a CSV.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Neither data file has labels (CSV, and an .rdata
#   data.frame with no variable or value labels); item codes are the depositor's
#   CA<domain><k>. The wording of every item and the six frequency options is in
#   the preprint's Appendix (PsyArXiv h2rp8, pp. 47-56), item k = the k-th
#   numbered statement of the domain; tying it needs a Step 5b verification
#   (the frequency-follow-up pattern per domain pins it), so it was left for a
#   later pass. Originator: Carson, Peterson & Higgins (2005) CAQ, expanded by the
#   authors with frequency options.
#
# Table:
#   zabelina_2022_caq  81 items, CA<domain><k> for domains inv (inventions, 10),
#     music (8), ttvf (theater/TV/film, 8), sci (scientific discovery, 8), cw
#     (creative writing, 8), dance (8), cook (culinary, 8), art (visual arts, 7),
#     humor (8), ad (architectural design, 8). Scored per the Appendix's own
#     scoring instructions: an item with frequency options is 0 = not checked,
#     1..6 = 1 time / 2 times / 3-5 / 6-9 / 10-19 / 20+ times (from the
#     CAFreq<domain><k> column); an item without them is 0/1 (checked). Item 1 of
#     every domain is "I don't have much talent in this area" (0/1, as stored).
#   In the CSV a checkbox is 1 (checked) or 999 (not checked). Per the scoring
#   instructions a domain where nothing at all is checked (not even item 1) is NA,
#   so all of that domain's items are dropped for that person. A checked
#   frequency item whose CAFreq is 999 (no frequency given) is dropped; a CAFreq
#   given where the base box is unchecked keeps the frequency (counts printed).
# Not shipped: the TAIE / sapaData SAPA items -- the same 2013-2014 SAPA release
#   already in the IRW as sapa_personality / icar_sapa (DVN/SD7SVE, DVN/AD9RVY);
#   only gender and age are carried from it, as covariates.
# Covariates (joined from TAIE on RID; 424 CAQ respondents are not in TAIE and
#   carry NA): cov_gender (TAIE 1/0; 1 = female, since 57.9% of TAIE is 1 and the
#   paper reports the SAPA sample as 58% female), cov_age_band (TAIE's bands).
# id: RID, SAPA's random respondent id (unique). One row in CSV is entirely blank
#   and is dropped; 255 respondents checked nothing in any domain and drop out.

import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadr
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw" / "zabelina_2022"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"CAQ.csv": "https://dataverse.harvard.edu/api/access/datafile/10993748?format=original",
         "CAQTAIE.rdata": "https://dataverse.harvard.edu/api/access/datafile/10993749"}
NAME = "zabelina_2022_caq"
DOMAINS = {"inv": 10, "music": 8, "ttvf": 8, "sci": 8, "cw": 8, "dance": 8,
           "cook": 8, "art": 7, "humor": 8, "ad": 8}
GENDER = {1: "female", 0: "male"}


def fetch() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, url in FILES.items():
        p = RAW_DIR / name
        if not p.exists():
            r = requests.get(url, headers=UA, timeout=600)
            r.raise_for_status()
            p.write_bytes(r.content)
        out[name] = p
    return out


def main() -> None:
    paths = fetch()
    d = pd.read_csv(paths["CAQ.csv"], dtype={"RID": str})
    assert d.shape == (5651, 141) and d["RID"].is_unique, d.shape
    blank = d.drop(columns="RID").isna().all(axis=1)
    assert blank.sum() == 1 and d.drop(columns="RID")[~blank].notna().all().all()
    print(f"  [skip] {blank.sum()} entirely blank row")
    d = d[~blank].reset_index(drop=True)

    base = {k: [f"CA{k}{i}" for i in range(1, n + 1)] for k, n in DOMAINS.items()}
    freq = [c for c in d.columns if c.startswith("CAFreq")]
    used = {"RID"} | {c for v in base.values() for c in v} | set(freq)
    assert set(d.columns) == used, set(d.columns) ^ used
    for c in freq:  # every frequency column follows a base item of the same domain/number
        m = re.fullmatch(r"CAFreq([a-z]+?)(\d+)", c)
        assert m and f"CA{m.group(1)}{m.group(2)}" in base[m.group(1)], c

    cov = pyreadr.read_r(str(paths["CAQTAIE.rdata"]))
    taie = cov["TAIE"][["RID", "gender", "age"]].copy()
    assert taie["RID"].is_unique
    caq_r = cov["CAQ052013"]
    assert caq_r.shape == (5651, 141) and set(d["RID"]) <= set(caq_r["RID"].astype(str))
    print("  [skip] TAIE's 770 SAPA items: same 2013-14 SAPA release as sapa_personality/icar_sapa")
    taie["RID"] = taie["RID"].astype(str)
    taie["cov_gender"] = taie["gender"].map(GENDER)
    taie["cov_age_band"] = taie["age"].astype(str).where(taie["age"].notna())
    assert taie.loc[taie["gender"].notna(), "cov_gender"].notna().all()

    rows = []
    n_dom_na = n_checked_nofreq = n_freq_unchecked = 0
    for k, items in base.items():
        checked = d[items].eq(1)
        assert d[items].isin([1, 999]).all().all(), k
        answered = checked.any(axis=1)  # scoring rule: nothing checked in a domain -> NA
        n_dom_na += int((~answered).sum())
        for it in items:
            fcol = it.replace("CA", "CAFreq", 1)
            r = pd.Series(checked[it].astype(float), index=d.index)
            if fcol in d.columns:
                f = d[fcol]
                assert f.isin([1, 2, 3, 4, 5, 6, 999]).all(), fcol
                r = pd.Series(0.0, index=d.index)
                has_f = f.ne(999)
                r[has_f] = f[has_f]
                bad = checked[it] & ~has_f
                n_checked_nofreq += int((bad & answered).sum())
                n_freq_unchecked += int((has_f & ~checked[it] & answered).sum())
                r[bad] = float("nan")
            r[~answered] = float("nan")
            rows.append(pd.DataFrame({"RID": d["RID"], "item": it, "resp": r}))
    print(f"  domain-person cells with nothing checked (NA by scoring rule): {n_dom_na}")
    print(f"  checked frequency items with no frequency given (dropped): {n_checked_nofreq}")
    print(f"  frequency given but base box unchecked (frequency kept): {n_freq_unchecked}")

    t = pd.concat(rows).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t = t.merge(taie[["RID", "cov_gender", "cov_age_band"]], on="RID", how="left")
    t = t.rename(columns={"RID": "id"})
    t = t[["id", "item", "resp", "cov_gender", "cov_age_band"]]
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    allitems = [c for v in base.values() for c in v]
    assert set(t["item"]) == set(allitems), set(allitems) - set(t["item"])
    freq_items = {c.replace("CAFreq", "CA", 1) for c in freq}
    pv = {i: set(range(7)) if i in freq_items else {0, 1} for i in allitems}
    for i in allitems:
        assert set(t.loc[t["item"] == i, "resp"]) <= pv[i], i

    names = [NAME]
    assert len(set(names)) == len(names)
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
