#!/usr/bin/env python3
# Source: https://zenodo.org/records/14244844
# DOI: 10.5281/zenodo.14244844
#   Kasali, Kamber (2024). "Validity and Reliability Study of Anatomy Attitude
#   Scale in Dental Students". Zenodo (2024-11-29).
# Data: data.folder.sav -- 292 dental students x 29 columns: Item1-Item14
#       (5-point attitude items, grouped in the file under three factor-name
#       header columns that hold no data), five demographic columns, and two
#       sets of three subscale totals, "ilk_*" (first administration) and
#       "Ikinci_*" (retest).
# License: CC BY 4.0 (Zenodo record, license id cc-by-4.0).
#
# Item text: not shipped. The .sav has variable labels on only two columns
#   (the two Turkish demographic questions) and none on any Item* column, and
#   there are no value labels in the file; the deposit holds just this .sav.
#   What the file does give is the factor each item loads on, via the position
#   of the three empty "faktor1_Value_of_anatomy" / "faktor2_Hating_anatomy" /
#   "faktor3_Allocating_Time_to_Anatomy" header columns -- recorded here but
#   not item wording: factor 1 = Item2,3,5,6,12,13,14; factor 2 = Item1,4,7,8;
#   factor 3 = Item9,10,11.
#
# One table: kasali_2024_anatomy_attitude -- Item1-Item14, 1-5.
#   The Item* columns are the FIRST administration: the three "ilk_*" totals
#   equal the plain sums of those factor groups (99.3%, 99.7% and 100.0% of
#   rows, the exceptions being the four cells dropped/missing below), whereas
#   the "Ikinci_*" retest totals match only 20-33% of rows. The retest has no
#   item-level data in the deposit, so there is no `wave` column and no retest
#   rows -- one administration only.
# NOT shipped: the six ilk_*/Ikinci_* subscale totals (composites), the three
#   all-empty factor header columns, and the one Item4 cell holding 11 (out of
#   the 1-5 range, a single isolated cell -> data-entry error, not a scale
#   point).
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR", REPO_ROOT / "automated_finding" / "irw_output"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/14244844/files/"
            "data.folder.sav/content")

COVS = {"cinsiyet": "cov_gender", "sınıf": "cov_class_term", "yaş": "cov_age",
        "dişhekimliğifakültesininedenseçtiniz": "cov_reason_chose_dentistry",
        "GelecekteDUSkazanıpuzmanolmakistiyormusnuz":
            "cov_wants_specialisation"}
ITEMS = [f"Item{i}" for i in range(1, 15)]
NAME = "kasali_2024_anatomy_attitude"


def main() -> None:
    raw = Path(os.environ.get("IRW_RAW_DIR", "/tmp")) / "kasali_2024.sav"
    if not raw.exists():
        r = requests.get(DATA_URL, headers=UA, timeout=300)
        r.raise_for_status()
        raw.write_bytes(r.content)
    d, _meta = pyreadstat.read_sav(raw, apply_value_formats=False)

    drop = {c: "empty factor-name header column" for c in d.columns
            if c.startswith("faktör")}
    drop.update({c: "subscale total (composite)" for c in d.columns
                 if c.startswith(("ilk_", "İkinci_"))})
    accounted = {"pno"} | set(COVS) | set(ITEMS) | set(drop)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in drop.items():
        print(f"  skipped {c}: {why}")

    assert d["pno"].nunique() == len(d)
    d = d.rename(columns={"pno": "id", **COVS})
    covs = sorted(COVS.values())

    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp -> imputation?"
    bad = t[~t["resp"].between(1, 5)]
    print(f"  dropped {len(bad)} out-of-range cell(s): "
          f"{bad[['item', 'resp']].to_dict('records')}")
    assert len(bad) <= 1 and set(bad["item"]) <= {"Item4"}, bad
    t = t[t["resp"].between(1, 5)]
    t["resp"] = t["resp"].astype(int)
    t["id"] = t["id"].astype(int)
    t = t[["id", "item", "resp"] + covs].reset_index(drop=True)

    assert len(NAME) <= 40
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
    checks = run_qc(t, permitted_values={i: [1, 2, 3, 4, 5] for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:180]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
