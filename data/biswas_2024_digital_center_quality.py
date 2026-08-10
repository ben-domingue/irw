from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0304178
# DOI: 10.1371/journal.pone.0304178
# Biswas, Nur Ullah, Rahman & Al Masud (2024), "Service quality,
# satisfaction, and intention to use Pourasava Digital Center in
# Bangladesh: The moderating effect of citizen participation". S1 Dataset
# (.sav). CC0 1.0. N=332. Structured questionnaire (originally English,
# translated to Bangla) covering 7 constructs, 5-point Likert (1=strongly
# disagree .. 5=strongly agree). Shipped as one table -- all item blocks
# are sub-constructs of a single structural-equation-model survey
# administered together, not independently distinct published instruments:
#   ACCS (3): Accumulative Satisfaction
#   SPES (3): Specific Satisfaction
#   INFQ (4): Information Quality
#   SYSQ (3): System Quality
#   SERQ (3): Service Quality
#   PAR  (3): Citizen Participation
#   CONI (7): Continuous use Intention
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0304178.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "PDC": "cov_digital_center",
    "Age": "cov_age",
    "Sex": "cov_sex",
    "Education": "cov_education",
    "Occupation": "cov_occupation",
    "Income": "cov_income",
}

ITEM_PREFIXES = ["ACCS", "SPES", "INFQ", "SYSQ", "SERQ", "PAR", "CONI"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_COLS)

    item_cols = [c for c in df.columns if any(c.startswith(p) and c[len(p):].isdigit()
                                                for p in ITEM_PREFIXES)]
    cov_cols = list(COV_COLS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "biswas_2024_digital_center_quality"
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
