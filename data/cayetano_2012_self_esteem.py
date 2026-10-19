"""Self-esteem, Peruvian 6th-grade pupils (Cayetano 2012 thesis).

Source: https://zenodo.org/records/21054
DOI: 10.5281/zenodo.21054
Data: 2012_Cayetano_Autoestima_en_estudiantes_de_sexto_grado.sav (112 x 30)
License: CC0 1.0 (Zenodo record reports licence id `cc-zero`)
Item text: not shipped. Both label levels checked: the 19 item columns carry no
  variable label and no value labels; only `Edad` and `Ins.Ed` have one. So the
  file holds neither the questions nor the options.

The same Peruvian thesis family as `calla_2010_self_esteem` (zenodo.20654, 16
binary self-esteem items) and handled identically. The six columns named for
the instrument's dimensions -- Conducta, Estatus, fisica, Ansiedad, Popularidad,
Felicidad, Neutro -- are thesis-derived subscale scores, not items, and are
skipped with the rest of the derived columns.

RIGHTS: those dimension names are the Piers-Harris dimensions, but this is a
19-item binary instrument where the Piers-Harris is 60 or 80 items, so the
deposit does not identify its scale and no register row matches. No item text
is shipped, so no wording is exposed either way.
"""
import glob
import os

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAWDIR = os.environ.get(
    "CAYETANO_RAWDIR",
    str(_RAW_BASE / "zenodo.21054"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")
ITEMS = [f"I.{i}" for i in range(1, 20)]


def main():
    path = glob.glob(os.path.join(RAWDIR, "*.sav"))[0]
    d, meta = pyreadstat.read_sav(path, apply_value_formats=False)
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    missing = [c for c in ITEMS if c not in d.columns]
    assert not missing, f"missing items {missing}"
    for c in d.columns:
        if c not in ITEMS:
            print(f"  skip {c!r}: derived subscale/total or covariate")
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_age"] = d["Edad"].values
    d["cov_school"] = d["Ins.Ed"].values
    long = d.melt(id_vars=["id", "cov_age", "cov_school"], value_vars=ITEMS,
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
    long[["id", "item", "resp", "cov_age", "cov_school"]].to_csv(
        os.path.join(OUT, "cayetano_2012_self_esteem.csv"), index=False)
    print(f"  cayetano_2012_self_esteem: {long['id'].nunique()} ids x "
          f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
