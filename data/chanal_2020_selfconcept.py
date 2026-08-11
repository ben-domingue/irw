#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0230103
# DOI: 10.1371/journal.pone.0230103
# SI file (S1 Dataset): https://doi.org/10.1371/journal.pone.0230103.s001
#
# Chanal J, Paumier D (2020) The school-subject-specificity hypothesis:
# Implication in the relationship with grades. PLoS ONE 15(4): e0230103.
#
# The raw file contains a 33-item-per-domain autonomous/controlled-motivation
# questionnaire (7-point Likert, 1=Totally disagree to 7=Totally agree)
# administered separately for five contexts: general school ("Ecole"),
# mathematics, French, English, and physical education. The paper's Methods
# describes a reduced 29-item/7-subscale final scoring version but gives no
# item-to-subscale mapping table, so subscales are NOT split here -- each
# domain is shipped as a single scale using all administered items (raw
# per-item response, not the paper's derived subscale composites).
#
# The file also contains: computed subscale-composite columns (CS1..CS6 per
# domain), a Big Five-looking 32-item block ("Big1".."Big32") that is never
# once mentioned or described anywhere in this paper's text, an
# approach/avoidance-goal-looking block ("Ev*"/"App*") with no documented
# item-to-construct mapping either, and end-of-year grade columns
# ("Note_*"). None of those blocks have any textual description in this
# paper to confirm what they are or how to score them, so per the "no
# reliable mapping -> skip rather than guess" rule they are dropped
# entirely rather than shipped.
#
# "Date de naissance" (date of birth) is PII and is dropped. There is no
# person-id column ("NuméroClasse" is a class id, not a person id) so the
# row index is used as `id`.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?id=10.1371/journal.pone.0230103.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DOMAINS = {
    "ecole": "chanal_2020_ecole.csv",
    "maths": "chanal_2020_maths.csv",
    "francais": "chanal_2020_francais.csv",
    "anglais": "chanal_2020_anglais.csv",
    "educphy": "chanal_2020_educphy.csv",
}
# map lowercase domain key -> source column prefix
PREFIX = {
    "ecole": "Ecole",
    "maths": "Maths",
    "francais": "Francais",
    "anglais": "Anglais",
    "educphy": "EducPhy",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    import io
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw = fetch_raw()

    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)

    cov = raw[["id"]].copy()
    cov["cov_gender"] = raw["Sexe"].astype(str).str.strip()

    for key, out_name in DOMAINS.items():
        prefix = PREFIX[key]
        item_cols = [c for c in raw.columns if c.startswith(prefix) and c[len(prefix):].isdigit()]
        # sort by the numeric suffix so item order is stable
        item_cols = sorted(item_cols, key=lambda c: int(c[len(prefix):]))

        d = raw[["id"] + item_cols].merge(cov, on="id")
        long = d.melt(
            id_vars=["id", "cov_gender"],
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        long["item"] = long["item"].str.replace(prefix, f"{key}_", regex=False)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # scale is documented as 1-7; drop anything outside that range as a
        # data-entry/sentinel guard
        long = long[(long["resp"] >= 1) & (long["resp"] <= 7)].reset_index(drop=True)

        out_cols = ["id", "item", "resp", "cov_gender"]
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        out_path = os.path.join(OUT_DIR, out_name)
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
