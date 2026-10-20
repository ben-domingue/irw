"""
Attachment security (CaMir-R security dimension), DASS-21 and body esteem
(BESAA-S) in Spanish-speaking young adults.

Source: Anónimo. "El papel mediador de la autoestima corporal." (2026)
DOI: 10.5281/zenodo.22766055
Data: https://zenodo.org/records/22766055
      (Papel mediador de la autoestima corporal.sav)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license = cc-by-4.0)
Item text: NOT shipped in this pass, although the text IS in hand — the SPSS
        variable labels carry the full Spanish stems (e.g. Seguridad21
        "[Siento confianza en mis seres queridos]", DASS21_13 "[Me sentía
        desanimado/a y triste]", BESAA_S_5 "[Desearía verme mejor]") and the
        value labels carry the response anchors. It is held because all three
        instruments (CaMir-R, DASS-21, BESAA-S) need a named check against
        itemtext/instrument_rights_register.csv first, which this pass did not
        have time to do. Nothing else is missing: a later pass can take the
        stems straight from meta.column_names_to_labels on this .sav.

The deposit's creator field is literally "Anónimo", so the author slug in this
file name is a placeholder — a human should decide whether to rename the tables
once the matching paper is identified.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1])
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

COV_MAP = {
    "Edad": "cov_age",
    "Pareja": "cov_partner_status",
    "OrientaciónSexual": "cov_sexual_orientation",
}

SEGURIDAD = ["Seguridad3", "Seguridad6", "Seguridad7", "Seguridad11",
             "Seguridad13", "Seguridad21", "Seguridad30"]
DASS21 = [f"DASS21_{i}" for i in range(1, 22)]
BESAA = [f"BESAA_S_{i}" for i in range(1, 15)]

SCALES = [
    (SEGURIDAD, (1, 5), "camir_security_2026_22766055"),
    (DASS21,    (0, 3), "dass21_2026_22766055"),
    (BESAA,     (0, 4), "besaa_s_2026_22766055"),
]
AGG = ["PTSeguridadApego", "PTDepresión", "PTAnsiedad", "PTEstrés",
       "PTAutoestimaCoporal"]


def main() -> None:
    df, meta = pyreadstat.read_sav(str(SRC))
    print("raw shape", df.shape)
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected free-text columns: {text_cols}"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1   # no respondent identifier is published
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    used = {"id"} | set(COV_MAP) | set(covs)
    written: set[str] = set()
    for cols, (lo, hi), table in SCALES:
        for c in cols:
            assert c in df.columns, c
        used.update(cols)
        long = df[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all(), "fractional Likert value"
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), f"outside {lo}-{hi}"
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        assert table not in written
        written.add(table)
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, (table, _fails)
        for _c in _checks:
            if _c.status == "warn":
                print(f"  [qc warn] {table} {_c.name}: {_c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")

    skipped = {c: "person-level composite (subscale total)" for c in AGG}
    used.update(skipped)
    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"skipped column {c}: {why}")


if __name__ == "__main__":
    main()
