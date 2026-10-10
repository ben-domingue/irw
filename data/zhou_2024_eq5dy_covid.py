#!/usr/bin/env python3
# Source: https://doi.org/10.17632/w4xxkf7brg.1
# DOI: 10.17632/w4xxkf7brg.1 (dataset; the record names no paper)
#   Zhou, Wenjing (2024). Psychometric Validation of the Chinese Versions of EQ-5D-Y-3L and
#   EQ-TIPS In Children and Adolescents with COVID-19 [Data set]. Mendeley Data, V1.
# Data: "All data_Mendeley.xlsx" ("The entire data for total sample"), three sheets:
#       Infected_baseline (861 children with COVID-19, ids C001...), infected_follow-up
#       (311 of them again, same ids), healthy (231 healthy children, ids H001...). Each
#       sheet holds, per child: the parent-proxy EQ-5D-Y-3L (Y-3L-proxy-M/S/U/P/F),
#       the self-complete EQ-5D-Y-3L (Y-3L-Sc-*), EQ-TIPS (6 items), the parent's own
#       EQ-5D-5L and EQ-HWB-S (9 items), EQ VAS ratings, overall-health ratings and
#       background. The column names carry the instrument and dimension; there is no
#       codebook beyond the codes written into a few headers.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- rights. Headers name the dimension only, and every
#   instrument here is EuroQol's (EQ-5D is a `block` row in
#   itemtext/instrument_rights_register.csv; EQ-TIPS, EQ-5D-Y and EQ-HWB-S are
#   EuroQol instruments under the same licence).
#
# Code -3 appears only where an instrument did not apply (the self-complete EQ-5D-Y-3L
#   for 353 of 861 baseline children, EQ-TIPS for 42) and is dropped as a
#   non-response; every other stored value is a level of the instrument's scale.
# Tables (item = the dimension code shared by the three sheets; 1 = no problems):
#   zhou_2024_eq5dy3l_proxy  M S U P F (mobility, self-care, usual activities, pain,
#                            feeling worried/sad/unhappy), 1-3, parent report
#   zhou_2024_eq5dy3l_self   M S U P F, 1-3, the child's own report
#   zhou_2024_eq_tips        M Play Pain S I E (EQ-TIPS: movement, play, pain, social
#                            interaction, communication, eating), 1-3, parent report
#   zhou_2024_eq5d5l_parent  M S U P A, 1-5, the parent's own EQ-5D-5L
#   zhou_2024_eq_hwb_s       UA Mo pain exhaustion loneliness concentration anxiety
#                            sadness control, 1-5, the parent's own EQ-HWB-S (the
#                            infected sheets spell concentration "consentration")
#   The two parent instruments describe the parent; `id` is the child's (one parent per
#   child), so a row is the family's.
# wave: 1 = baseline (infected) or the single assessment (healthy), 2 = follow-up.
# Skipped: the *_b.1 columns (proxy minus self-report differences, -2..2), EQ VAS and
#   OHA single ratings, symptom/treatment checklists, carer burden items (single
#   questions on caring time, work impact, finances, sleep), parent demographics.
# Covariates (codes as in the headers): cov_group (infected / healthy), cov_sex (1 male,
#   2 female), cov_residence (1 urban, 2/3 suburb), cov_education (child's education,
#   1-6 as stored), cov_severity (baseline disease severity: 1 mild, 2 moderate,
#   3 severe; healthy children blank).
# id: the deposit's child code (C... infected, H... healthy).

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.17632_w4xxkf7brg"
FNAME = "All data_Mendeley.xlsx"
P = "zhou_2024_"
# table -> (item codes, {sheet: column template}, valid codes)
DIMS = {
    "eq5dy3l_proxy": (["M", "S", "U", "P", "F"],
                      {"b": "Y-3L-proxy-{}_b", "f": "Y-3L-proxy-{}_f", "h": "Y-3L-proxy-{}"}, range(1, 4)),
    "eq5dy3l_self": (["M", "S", "U", "P", "F"],
                     {"b": "Y-3L-Sc-{}_b", "f": "Y-3L-Sc-{}_f", "h": "Y-3L-Sc-{}"}, range(1, 4)),
    "eq_tips": (["M", "Play", "Pain", "S", "I", "E"],
                {"b": "EQ-TIPS-{}_b", "f": "EQ-TIPS-{}_f", "h": "TIPS-{}"}, range(1, 4)),
    "eq5d5l_parent": (["M", "S", "U", "P", "A"],
                      {"b": "EQ-5D-5L-{}_b", "f": "EQ-5D-5L-{}_f", "h": "EQ-5D-5L-{}"}, range(1, 6)),
    "eq_hwb_s": (["UA", "Mo", "pain", "exhaustion", "loneliness", "concentration", "anxiety",
                  "sadness", "control"],
                 {"b": "EQ-HWB-S-{}-b", "f": "EQ-HWB-S-{}-f", "h": "HWB-{}"}, range(1, 6)),
}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        j = requests.get("https://data.mendeley.com/public-api/datasets/w4xxkf7brg/files"
                         "?folder_id=root&version=1", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j if f["filename"] == FNAME][0]
        download(url, p)
    return p


def main() -> None:
    x = pd.ExcelFile(fetch())
    b = pd.read_excel(x, "Infected_baseline")
    f = pd.read_excel(x, "infected_follow-up")
    h = pd.read_excel(x, "healthy")
    assert (len(b), len(f), len(h)) == (861, 311, 231)
    assert b["Number"].is_unique and f["Number"].is_unique and h["number"].is_unique
    assert set(f["Number"]) <= set(b["Number"])
    sev = [c for c in b.columns if c.startswith("Disease severity_b")][0]
    res = [c for c in b.columns if c.startswith("residence")][0]
    sex = [c for c in b.columns if c.startswith("child's sex")][0]
    cov_b = pd.DataFrame({"id": b["Number"], "cov_group": "infected", "cov_sex": b[sex],
                          "cov_residence": b[res], "cov_education": b["child's education"],
                          "cov_severity": b[sev]})
    cov_h = pd.DataFrame({"id": h["number"], "cov_group": "healthy", "cov_sex": h["child's sex"],
                          "cov_residence": h["residence"], "cov_education": h["child's education"],
                          "cov_severity": pd.NA})
    cov = pd.concat([cov_b, cov_h], ignore_index=True)
    assert cov["id"].is_unique
    covs = ["cov_group", "cov_sex", "cov_residence", "cov_education", "cov_severity"]
    for c in covs[1:]:
        cov[c] = cov[c].astype("Int64")
    sheets = {"b": (b, "Number", 1), "f": (f, "Number", 2), "h": (h, "number", 1)}
    out = {}
    for suf, (dims, tmpl, valid) in DIMS.items():
        parts = []
        for key, (df, idc, wave) in sheets.items():
            # the infected sheets spell this dimension "consentration"
            spell = {"concentration": "consentration"} if key in "bf" else {}
            cols = {tmpl[key].format(spell.get(dim, dim)): dim for dim in dims}
            assert set(cols) <= set(df.columns), (suf, key, set(cols) - set(df.columns))
            w = df[[idc] + list(cols)].rename(columns={idc: "id", **cols})
            w = w.melt(id_vars="id", var_name="item", value_name="resp")
            w["wave"] = wave
            parts.append(w)
        t = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        na = t["resp"] == -3
        bad = t[~na & ~t["resp"].isin(list(valid))]
        assert bad.empty, (suf, bad["resp"].value_counts().to_dict())
        print(f"  [{suf}] dropped {na.sum()} code -3 (not applicable) responses")
        t = t[~na].merge(cov, on="id", how="left", validate="many_to_one")
        assert t["cov_group"].notna().all()
        t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
        out[P + suf] = (t.reset_index(drop=True), {i: set(valid) for i in dims})
    emit(out)


if __name__ == "__main__":
    main()
