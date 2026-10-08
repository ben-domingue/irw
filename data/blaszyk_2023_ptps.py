#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/x2rxtpzg4v/1
# DOI: 10.17632/x2rxtpzg4v.1 (dataset; no paper DOI on the record)
#   Blaszyk, Marta Adrianna & Kroemeke, Aleksandra (2023). "Polish adaptation of
#   Physician's Trust in the Patient Scale (PTPS) - psychometric properties and
#   validation" [data set]. Mendeley Data, V1.
# Data: "Database - PTPS - Mendeley .sav" (the same data are also deposited as .csv,
#       .xlsx and .sas7bdat): 307 Polish physicians (online Qualtrics survey) x Age,
#       Specialty, eight instruments' items, reverse-scored copies (*R) and factor
#       scores. SPSS variable labels carry each item's Polish wording, value labels the
#       options. Record: "The missing data is signed with the 9 (all items), 99 (for
#       medical specialty), or 999 (for age)". Gender and other identifying
#       demographics were removed by the depositors.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped. Levels checked: SPSS variable labels carry the full Polish
#   item wording and value labels the Polish options for all eight instruments (cheap:
#   data_labels + study_materials); held only because every English _translated
#   column would be IRW-generated (75 items) -- left for a later pass.
#
# Tables (codes and coding as stored; several instruments are stored with 1 = the
#   AGREE/positive end -- GTS 1 = Zdecydowanie sie zgadzam, OLBI 1 = Zgadzam sie,
#   S_E 1 = Calkowicie pasuje, JS 1 = Bardzo zadowolona/y -- not reversed):
#   blaszyk_2023_ptps        PTPS_1-12  1-5 (completely unsure ... completely sure)
#   blaszyk_2023_dtt         DtT_1-9    1-7 disposition to trust (McKnight et al. 2002)
#   blaszyk_2023_tbm         TBM_1-11   1-7 trusting beliefs (McKnight et al. 2002)
#   blaszyk_2023_gts         GTS_1-7    1-6 General Trust Scale (Yamagishi)
#   blaszyk_2023_olbi        OLBI_1-16  1-4 Oldenburg Burnout Inventory
#   blaszyk_2023_copsoq_se   S_E_1-6    1-4 COPSOQ II self-efficacy
#   blaszyk_2023_copsoq_js   JS_1-4     1-4 COPSOQ II job satisfaction (5 = "Nie
#                                           dotyczy"/not applicable would be dropped;
#                                           none occur)
#   blaszyk_2023_tipi        TIPI_1-10  1-7 Ten-Item Personality Inventory
# Dropped cells: code 9 (missing) everywhere; and every NON-INTEGER cell in PTPS and
#   DtT -- mean imputation: the same fractional value recurs for 19 (PTPS) / 29 (DtT)
#   respondents on an item, i.e. the item mean filled in for those respondents.
# Not shipped: *R columns (reversed copies), FAC*_EFA/CFA (factor scores).
# Covariates: cov_age (999 -> missing), cov_specialty (Specialty code, 99 -> missing;
#   labels in the .sav and the deposit's Appendix A). id = row index.

import re
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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "blaszyk_2023"
UA = {"User-Agent": "Mozilla/5.0 (IRW-Finder/1.0; ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/x2rxtpzg4v"
FNAME = "Database - PTPS - Mendeley .sav"
TABLES = {"PTPS": ("blaszyk_2023_ptps", 12, range(1, 6)),
          "DtT": ("blaszyk_2023_dtt", 9, range(1, 8)),
          "TBM": ("blaszyk_2023_tbm", 11, range(1, 8)),
          "GTS": ("blaszyk_2023_gts", 7, range(1, 7)),
          "OLBI": ("blaszyk_2023_olbi", 16, range(1, 5)),
          "S_E": ("blaszyk_2023_copsoq_se", 6, range(1, 5)),
          "JS": ("blaszyk_2023_copsoq_js", 4, range(1, 5)),
          "TIPI": ("blaszyk_2023_tipi", 10, range(1, 8))}


def fetch() -> Path:
    p = RAW_DIR / "ptps.sav"
    if not p.exists():
        meta = requests.get(API, headers=UA, timeout=120).json()
        assert meta["data_licence"]["short_name"] == "CC BY 4.0"
        (f,) = [f for f in meta["files"] if f["filename"] == FNAME]
        r = requests.get(f["content_details"]["download_url"], headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (307, 94)
    items = {p: [f"{p}_{i}" for i in range(1, n + 1)] for p, (_, n, _) in TABLES.items()}
    allit = {c for v in items.values() for c in v}
    skipped = [c for c in d.columns if c not in allit | {"Age", "Specialty"}]
    assert all(c.endswith("R") or c.startswith("FAC") for c in skipped), skipped
    print(f"  [skip] {len(skipped)} columns (reversed copies, factor scores): {skipped}")
    d.insert(0, "id", range(1, len(d) + 1))
    d["cov_age"] = d["Age"].where(d["Age"] != 999)
    d["cov_specialty"] = d["Specialty"].where(d["Specialty"] != 99)
    covs = ["cov_age", "cov_specialty"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for pre, (name, n, rng) in TABLES.items():
        its = items[pre]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        n9 = (t["resp"] == 9).sum()
        frac = (t["resp"] % 1 != 0)
        t = t[(t["resp"] != 9) & ~frac]
        print(f"  {name}: dropped {n9} missing-code 9 cells, {frac.sum()} imputed (fractional) cells")
        assert t["resp"].isin(list(rng)).all(), (name, sorted(t["resp"].unique()))
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
