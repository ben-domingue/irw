"""Reading comprehension, Peruvian 6th-grade pupils (Rojas 2012 thesis).

Source: https://zenodo.org/records/22609
DOI: 10.5281/zenodo.22609
Data: 2012_Rojas_Comprension_lectora_en_alumnos_de_6_grado.sav (128 x 39)
License: CC0 1.0 (Zenodo record reports licence id `cc-zero`)
Item text: not shipped. Both label levels checked: the 28 item columns carry
  NO variable label and NO value labels (only the institution column has one),
  so the file holds neither the questions nor the options. The instrument is
  the thesis's own reading-comprehension test; the wording is in the thesis
  PDF, which this record does not deposit.

One of the Peruvian thesis deposits already represented in the IRW by
`arista_2010_achievement_motivation`, `vasquez_2013_reading_comprehension` and
`calla_2010_self_esteem`, and handled the same way: a binary scored test, items
shipped as-is, the thesis's derived subscale and level columns skipped.

IT1..IT28 are 0/1 scored responses. The source stores them out of order
(IT4, IT16, IT9, ...); they are emitted in numeric order so `item` sorts
sensibly, which changes nothing about the mapping since each code names itself.
"""
import os

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAW = os.environ.get(
    "ROJAS_RAW",
    str(_RAW_BASE / "2012_Rojas_Comprension_lectora_en_alumnos_de_6_grado_de_instituciones_educativas_publicas_de_Ventanilla.sav"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")
ITEMS = [f"IT{i}" for i in range(1, 29)]


def main():
    import glob
    path = RAW if os.path.exists(RAW) else glob.glob(
        os.path.join(os.path.dirname(RAW), "*.sav"))[0]
    d, meta = pyreadstat.read_sav(path, apply_value_formats=False)
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    missing = [c for c in ITEMS if c not in d.columns]
    assert not missing, f"missing items {missing}"
    for c in d.columns:
        if c not in ITEMS:
            print(f"  skip {c!r}: thesis-derived subscale/level or covariate")
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_school"] = d["VAR00001"].values
    long = d.melt(id_vars=["id", "cov_school"], value_vars=ITEMS,
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"].unique()) - {0, 1}
        assert not bad, f"{it}: {sorted(bad)} outside 0/1"
    assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
    os.makedirs(OUT, exist_ok=True)
    # The shared checks, which the script's own assertions are not
    # (irw_validate.contract `no_validator`). Fails block; the
    # warnings here are legitimate and are printed.
    _checks = run_qc(long)
    _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
    assert not _fails, _fails
    for _c in _checks:
        if _c.status == "warn":
            print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
    long[["id", "item", "resp", "cov_school"]].to_csv(
        os.path.join(OUT, "rojas_2012_reading_comprehension.csv"), index=False)
    print(f"  rojas_2012_reading_comprehension: {long['id'].nunique()} ids x "
          f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
