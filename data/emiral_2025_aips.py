"""Artificial Intelligence in Psychotherapy Scale (AIPS), Turkish sample.

Source: Emiral (2025), Zenodo 10.5281/zenodo.14901927, CC BY 4.0. Single file
`AIPS.sav`, 729 respondents x 160 columns. The instrument is described in
Emiral et al., "Attitudes towards Artificial intelligence (AI) in
psychotherapy: Artificial Intelligence in Psychotherapy Scale (AIPS)",
Clinical Psychologist 29(2), 2025 (n=723 analysed there vs 729 rows here).

ONLY the 23-item AIPS block ships. The deposit carries four further item
blocks -- PYAYT (18), TBO (35), TKO (45) and IBO (12) -- which are the study's
convergent-validity measures. The Zenodo record has an empty description, no
codebook, and the paper is paywalled, so there is no source that names those
instruments. They are deliberately NOT shipped rather than named on a guess:
an IRW table's name is a claim about what the items measure.

(The TKO block is *probably* the Basic Personality Traits Inventory -- 45
items and six factors, and its composite columns are named TKODIS, TKOSor,
TKOUyum, TKODTu, TKOGAciklik and TKOOlDeger, which read as the BPTI's
extraversion / conscientiousness / agreeableness / emotional-instability /
openness / negative-valence dimensions. That is an inference from column
names, not a source, so it is recorded here and in TODO.md rather than acted
on.)

Composite columns are dropped throughout. AIPSOlumlu and AIPSOlumsuz are the
positive/negative subscale scores for the shipped block; the remaining
PYAOlumlu/PYAOlumsuz, SMO*, YIBToplam and TKO* columns are subscale scores for
the blocks that do not ship.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 14901927
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "emiral_2025_aips"

COVARIATES = {
    "Yaş": "cov_age",
    "Cinsiyet": "cov_gender",
    "Gelir": "cov_income",
    "Eğitim": "cov_education",
    "EkranSüresi": "cov_screen_time",
    "SosyalMedyaTutum": "cov_social_media_use",
    "TerapiNiyeti": "cov_therapy_intention",
    "AIDeneyim": "cov_ai_experience",
}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    # The file is written by a localised SPSS build whose declared encoding is
    # not honoured; read it the way the triage pipeline learned to.
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    items = [c for c in df.columns if re.match(r"^AIPS\d+$", c)]
    assert len(items) == 23, f"expected 23 AIPS items, found {len(items)}"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    missing = [c for c in covs if c not in df.columns]
    assert not missing, f"missing covariate columns: {missing}"
    df["id"] = df["Protokol"].astype(int)
    assert df["id"].is_unique, "Protokol is not one row per respondent"

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() > 1
    assert long["resp"].between(1, 5).all(), "AIPS is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
