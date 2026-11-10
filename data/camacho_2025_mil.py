#!/usr/bin/env python3
# Source: https://zenodo.org/records/17102406
# DOI: 10.5281/zenodo.17102406 (data; no paper DOI on the record). The same
#   two files are also deposited, anonymously, as 10.5281/zenodo.17821828;
#   this script uses the named record.
#   Camacho Inda, D., Mears Delgado, B., Hernandez Hernandez, J. I., et al.
#   (2025). "Evaluacion de la Alfabetizacion Mediatica e Informacional en las
#   Instituciones de Educacion Superior." Zenodo.
# Data: two Google Forms exports from a Mexican university (name withheld as
#   "Anonimo" in the file): students (188) and teachers (173). Each has 8
#   background questions, then 42 self-ratings of media and information
#   literacy (MIL) competencies following UNESCO's framework, grouped under
#   questions 9-20, each rated Malo / Regular / Bueno / Alto.
# License: CC BY 4.0 (Zenodo record).
# Codebook: none (headers carry the wording; the anonymous twin record adds a
#   variable-alignment PDF).
#
# Item text: not shipped -- the Spanish stems are the headers, but no
#   rights-register row exists; left for an itemtext pass.
#
# Tables (the two forms word the stems differently, so they stay separate):
#   camacho_2025_mil_students  43 items
#   camacho_2025_mil_teachers  43 items
# resp: Malo = 1, Regular = 2, Bueno = 3, Alto = 4.
# Item codes: "q<question number>_<k>", k = the sub-item's order within its
#   question's grid (each header is "<n>. <competency> [<statement>]"; the
#   number is read from the header, and the per-question sub-item counts are
#   asserted).
# Covariates: cov_age_band, cov_gender, cov_degree (degree studied, students;
#   highest degree, teachers), cov_field. Course-taught free text (teachers)
#   and the yes/no screening questions are not carried. id = row index.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
BASE = "https://zenodo.org/api/records/17102406/files/"
FILES = {
    "camacho_2025_mil_students": (
        "Nivel%20de%20Alfabetizaci%C3%B3n%20Medi%C3%A1tica%20e%20"
        "Informacional%20Estudiantes.xlsx/content", 188),
    "camacho_2025_mil_teachers": (
        "Nivel%20de%20Alfabetizaci%C3%B3n%20Medi%C3%A1tica%20e%20"
        "Informacional%20Docentes.xlsx/content", 173),
}
LEVEL = {"Malo": 1, "Regular": 2, "Bueno": 3, "Alto": 4}
COUNTS = {9: 2, 10: 3, 11: 3, 12: 2, 13: 4, 14: 4, 15: 6, 16: 5, 17: 3,
          18: 6, 19: 2, 20: 3}  # 43 statements
GENDER = {"Femenino": "female", "Masculino": "male"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (path, n) in FILES.items():
        r = requests.get(BASE + path, headers=UA, timeout=300)
        r.raise_for_status()
        d = pd.read_excel(io.BytesIO(r.content))
        assert d.shape == (n, 51), d.shape
        cols = list(d.columns)
        codes, seen = {}, {}
        for c in cols[8:]:
            q = int(re.match(r"^(\d+)\.", str(c)).group(1))
            seen[q] = seen.get(q, 0) + 1
            codes[c] = f"q{q}_{seen[q]}"
        assert seen == COUNTS, seen
        d["id"] = range(1, len(d) + 1)
        d["cov_age_band"] = d[cols[0]]
        d["cov_gender"] = d[cols[1]].map(GENDER)
        d["cov_degree"] = d[cols[3]]
        d["cov_field"] = d[cols[4]]
        covs = ["cov_age_band", "cov_gender", "cov_degree", "cov_field"]
        x = d[["id"] + covs + list(codes)].rename(columns=codes)
        long = x.melt(id_vars=["id"] + covs, var_name="item",
                      value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].map(LEVEL)
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: set(LEVEL.values())
                                                for c in codes.values()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
