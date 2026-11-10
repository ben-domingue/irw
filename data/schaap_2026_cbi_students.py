#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32964434
# DOI: 10.3390/bs16101723
#   "The Dimensionality of the 19-Item Copenhagen Burnout Inventory Adapted for
#   Students: A Bifactor Penalised SEM Analysis" (Schaap & van der Ross, 2026),
#   Behavioral Sciences 16:1723.
# Data: figshare 32964434 (CC BY 4.0), Data_F.xlsx. Sheet "Items": 1,938 rows x
#   42 columns (V1-V5, R1-R18, B1-B19); sheet "Notes" maps the blocks: V = Study
#   Demands, R = Study Resources, B = CBI. Sheet "Demographical data" holds
#   gender, language, age band and ethnic group, but its note says "selected
#   demographical data were randomly reordered and separated from the CBI item
#   responses to reduce the risk of secondary analyses beyond the scope of the
#   present study" - so its rows do not belong to the item rows and it is NOT
#   joined or shipped.
# License: CC BY 4.0 (figshare record).
#
# Sample: 1,938 South African undergraduates (the paper's full sample, collected
#   for van der Ross 2021). id = row index; no covariates (see above).
#
# Tables (paper section 3.4):
#   schaap_2026_cbi              B1-B19  1-5  Copenhagen Burnout Inventory,
#       student adaptation (van der Ross 2021): personal, study and peer burnout
#       items; "anchored at 1 = always/very high degree and 5 =
#       never/very low degree", so a HIGHER resp is LESS burnout.
#   schaap_2026_study_demands    V1-V5   1-4 (1 never .. 4 always)  SDRS Study
#       Demands subscale (Mokgele 2014), module-specific wording
#   schaap_2026_study_resources  R1-R18  1-4 (1 never .. 4 always)  SDRS Study
#       Resources: growth (6), peer support (3), lecturer support (5),
#       information accessibility (4)
#
# Item text: not shipped. Levels checked: xlsx headers are codes, no labels; the
#   paper points to Supplementary File S2 for the items (not in the deposit).

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "schaap_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/67015763"
TABLES = {
    "schaap_2026_cbi": ([f"B{i}" for i in range(1, 20)], {1, 2, 3, 4, 5}),
    "schaap_2026_study_demands": ([f"V{i}" for i in range(1, 6)], {1, 2, 3, 4}),
    "schaap_2026_study_resources": ([f"R{i}" for i in range(1, 19)], {1, 2, 3, 4}),
}


def fetch() -> Path:
    p = RAW_DIR / "Data_F.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Items")
    assert d.shape == (1938, 42), d.shape
    allits = [c for its, _ in TABLES.values() for c in its]
    assert set(d.columns) == set(allits) and len(allits) == 42
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, pv_set) in TABLES.items():
        t = d.melt(id_vars="id", value_vars=its, var_name="item", value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert set(t["resp"]) <= pv_set, (name, set(t["resp"]))
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: pv_set for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
