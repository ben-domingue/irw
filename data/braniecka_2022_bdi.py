#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/9rc79r8nyw/1
# DOI: 10.1038/s41598-022-11515-y
#   "Differential effects of stress-related and stress-unrelated humor in
#   remitted depression" (Braniecka, Hanc, Wolkowicz, Chrzczonowicz-Stepien,
#   Mikolajek-Bedner & Lukasik, 2022), Scientific Reports 12:7946.
# Data DOI: 10.17632/9rc79r8nyw.1 (Mendeley Data, "Humor types and emotion
#   regulation in remitted depression"), one SPSS file
#   "Braniecka_Dataset_Humor types and emotion regulation in remitted
#   depression_Mendeley.sav": 122 outpatients x 113 columns.
# License: CC BY 4.0 (Mendeley Data record's data_licence).
#
# Sample: 122 outpatients in full or partial remission from depression
#   (82 women, 40 men, aged 18-65), recruited in Poland; the paper's analysis
#   sample (N = 94) excludes outliers on the experimental measures, but the
#   BDI-II was administered to all 122 at intake, so all 122 ship.
#
# Table:
#   braniecka_2022_bdi   BDI1-BDI21  0-3   Beck Depression Inventory-II
#     (paper Methods, "Depressive symptoms": 21 items, past two weeks).
#     BDItotal is the deposit's stored total (checked, then not shipped).
#
# DATA NOTE -- STORED TOTAL vs ITEM SUM: the stored BDItotal differs from the
#   sum of the 21 item columns in 20 of 122 rows (by -2 to +6). Six item sums
#   exceed 16, although the paper's inclusion rule was a BDI-II score of at
#   most 16, and the stored totals max out at exactly 16. So either the items
#   or the totals were mis-entered for those rows, and the deposit does not
#   say which. The item responses ship as deposited (they are the raw record;
#   the total is derived). Held 2026-11-10 (overnight lane D), ruled ship by
#   Ben 2026-11-11.
#   Items are the source column names BDI1..BDI21; the SPSS variable labels
#   give a short descriptor for each ("BDI 1 sadness", "BDI 9 suicidal
#   ideation", ...), which match the BDI-II item order.
#
# Not shipped:
#   - d2 Test of Attention scores (WS raw, RP percentile, SN standard scores):
#     derived test scores, not item responses.
#   - The single-item emotion ratings (NEGAT_EM_T1..T4, POSIT_EM_T1..T4,
#     MAGNIT_DISS_*, DISTANCE_*, EFFORT_T3) and manipulation checks: one
#     repeated rating per construct, no item structure.
#   - DescrComorbidity: a short free-text diagnosis field ("OCD"); dropped in
#     no form under the 2026-10-21 short-clinical-free-text ruling. The coded
#     comorbidity categories and per-drug medication flags are not carried.
#
# Covariates: gender (1 female, 2 male), age, the randomised emotion-regulation
#   condition (HRD / HUD / SER; assigned after the BDI was taken), remission
#   type, comorbidity yes/no, number of depressive episodes, age at first
#   depression, number of hospitalisations, medicated yes/no, education,
#   employment. Education/employment 999 and the unlabelled 0 are missing.
#   The participant code column `No` (e.g. "10Agn") is replaced by the row index.
#
# Item text: not shipped. Levels checked: SPSS variable labels carry a 1-3 word
#   descriptor per BDI item, not the wording; no value labels on the items.
#   The BDI-II is Pearson-copyrighted and the Polish adaptation is not in the
#   deposit; the text would need the published instrument.

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = os.environ.get("BRANIECKA2022_RAW")
UA = {"User-Agent": "IRW-Finder/1.0"}
URL = ("https://data.mendeley.com/public-files/datasets/9rc79r8nyw/files/"
       "20b6255f-5bac-4f49-b356-643e0ebd09f0/file_downloaded")
NAME = "braniecka_2022_bdi"


def fetch() -> Path:
    if RAW:
        return Path(RAW)
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    p = Path(tempfile.mkdtemp()) / "braniecka_2022.sav"
    p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (122, 113), d.shape
    items = [f"BDI{i}" for i in range(1, 22)]
    assert all(c in d.columns for c in items)
    lab = meta.column_names_to_labels
    for i, c in enumerate(items, 1):
        assert lab[c].startswith(f"BDI {i} "), (c, lab[c])
    assert d[items].notna().all().all()
    assert d[items].isin([0, 1, 2, 3]).all().all()
    # DATA NOTE (header): the stored BDItotal differs from the item sum in 20 of 122 rows
    # (by -2..+6), and 6 item sums exceed 16 although the paper's inclusion
    # criterion was a BDI-II score of at most 16 (stored totals max out at 16).
    mism = (d[items].sum(axis=1) != d["BDItotal"]).sum()
    print(f"  [data note] BDItotal != item sum in {mism} rows; item sum > 16 in "
          f"{(d[items].sum(axis=1) > 16).sum()} rows")
    assert (d["Gender"] == 1).sum() == 82 and (d["Gender"] == 2).sum() == 40

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cond = {1: "HRD", 2: "HUD", 3: "SER"}
    out = pd.DataFrame({
        "id": d["id"],
        "cov_gender": d["Gender"].map({1: "female", 2: "male"}),
        "cov_age": d["Age"],
        "cov_condition": d["CONDITION"].map(cond),
        "cov_remission": d["Remission"].map({1: "full", 2: "partial"}),
        "cov_comorbidity": d["Comorbidity"],
        "cov_n_depressive_episodes": d["NrDepressions"],
        "cov_age_first_depression": d["FirstDeprAge"],
        "cov_n_hospitalizations": d["NrHospital"],
        "cov_medicated": d["Medication"],
        "cov_education": d["Education"].map(
            {1: "primary", 2: "secondary", 3: "higher", 4: "postgraduate"}),
        "cov_employment": d["Employment"].map(
            {1: "employed", 2: "disability pension", 3: "unemployed"}),
    })
    covs = [c for c in out.columns if c.startswith("cov_")]
    wide = pd.concat([out, d[items]], axis=1)
    t = wide.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 122

    pv = {i: {0, 1, 2, 3} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail}")
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
