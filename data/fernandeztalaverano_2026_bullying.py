#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/r3kwfdb84d/2
# DOI: 10.17632/r3kwfdb84d.2 (data; no paper)
#   Fernandez Talaverano J, Colca Cruz P (2026). Inteligencia emocional como moderador entre
#   bullying escolar e ideacion suicida en adolescentes de Lima, Peru. Mendeley Data, V2.
# License: CC BY 4.0 (Mendeley Data record)
# Data: "Visor de Datos SPSS.sav" (311 secondary-school students aged 11-17, two schools in Lima;
#   non-probability sample). Variable labels carry the Spanish item stems, value labels the
#   anchors. Every item cell is filled.
#
# Tables (the deposit's three instruments, per the record's description):
#   fernandeztalaverano_2026_eqim20 -- Inventario Breve de Inteligencia Emocional para Mayores
#     (EQ-i-M20), 20 items, 1 nunca me pasa - 4 siempre me pasa, five 4-item dimensions (INP
#     intrapersonal, INT interpersonal, MAN stress management, ADP adaptability, ANI mood). The
#     MAN items are worded as problems ("Tengo mal genio") and are stored as answered: the file's
#     own DIM3_MAN equals their raw sum in all 311 rows, so nothing was reversed.
#   fernandeztalaverano_2026_vei -- Escala de Victimizacion Escolar entre Iguales (VE-I), 11 items,
#     1 nunca me ha pasado - 5 me pasa muy a menudo; relational (VR), physical (VF), verbal (VV).
#   fernandeztalaverano_2026_pss -- Paykel Suicide Scale, 5 items, 0 no / 1 si.
#   Every stored dimension and total (DIM*, Inteligencia_Emocional, Bullying_Escolar,
#   Ideacion_Suicida) equals the sum of its items in all 311 rows; the totals are not shipped.
# Item codes: the .sav names with the accent dropped ("Item3_INP" for "Ítem3_INP"); the number is
#   the item's position in the instrument and the suffix its dimension.
# id: row index. Covariates: cov_sex (Genero), cov_age (Edad), cov_grade (grade from
#   Grado_Seccion, the section letter dropped), cov_school (IE, 1/2 as coded).
# Item text: not shipped -- Spanish stems and anchors are in the .sav variable/value labels, but
#   all three are published third-party instruments (EQ-i-M20 from BarOn's EQ-i:YV; VE-I, Cava et
#   al.; Paykel) with no rights-register ruling.
import sys
import tempfile
import unicodedata
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/r3kwfdb84d/files/"
       "e7af83ef-32ed-4650-80ac-3c11276e7ff7/file_downloaded")


def ascii_name(c):
    return unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode()


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    assert len(d) == 311
    d = d.rename(columns={c: ascii_name(c) for c in d.columns})
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = d["Genero"].map({"F": "female", "M": "male"})
    d["cov_age"] = d["Edad"].astype(int)
    d["cov_grade"] = d["Grado_Seccion"].str.extract(r"^(\d)")[0].astype(int)
    d["cov_school"] = d["IE"].astype(int)
    covs = ["cov_sex", "cov_age", "cov_grade", "cov_school"]
    assert d[covs].notna().all().all()
    item_cols = [c for c in d.columns if c.startswith("Item")]
    blocks = {
        "fernandeztalaverano_2026_eqim20": (("_INP", "_INT", "_MAN", "_ADP", "_ANI"), 1, 4, 20),
        "fernandeztalaverano_2026_vei": (("_VR", "_VF", "_VV"), 1, 5, 11),
        "fernandeztalaverano_2026_pss": (("_IS",), 0, 1, 5),
    }
    used = []
    for name, (suf, lo, hi, k) in blocks.items():
        items = [c for c in item_cols if c.endswith(suf)]
        assert len(items) == k, (name, items)
        used += items
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all() and len(t) == 311 * k
        assert not t.duplicated(["id", "item"]).any()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        gate(t)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    assert sorted(used) == sorted(item_cols), set(item_cols) - set(used)


if __name__ == "__main__":
    main()
