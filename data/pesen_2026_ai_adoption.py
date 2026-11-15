#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_Supporting_Modeling_Educators_Artificial_Intelligence_Adoption_Behaviors_through_Psychometric_and_Latent_Profile_Analysis_/34868748
# DOI: 10.6084/m9.figshare.34868748.v1 (data; no paper DOI on the record)
#   Pesen A, Elcicek M (2026). Dataset Supporting "Modeling Educators'
#   Artificial Intelligence Adoption Behaviors through Psychometric and Latent
#   Profile Analysis". figshare.
# Data: DFA.sav, the CFA sample (352 Turkish teachers x 29 columns). The
#   deposit's other file, EFA.omv.zip, is a jamovi workspace for the separate
#   591-teacher EFA sample on the 25-item pool; not shipped (different form,
#   jamovi binary).
# License: CC BY 4.0 (figshare record).
# Codebook: none; SPSS variable labels carry each item's full Turkish stem.
#
# Counts: 352 rows = the description's "independent sample of 352".
# Instrument: the authors' own AI-adoption scale built on Rogers' Diffusion of
#   Innovations: relative advantage, compatibility, complexity, trialability,
#   observability (description); 22 items as retained after the EFA, 1-5. The
#   stems put items 1-5 / 6-9 / 10-13 / 14-17 / 18-22 in those five
#   dimensions; complexity items 10-13 are negatively worded. No value labels
#   on the items, so anchors are not in the file; kept as deposited.
# Table: pesen_2026_ai_adoption (Item1-Item22). One table, one instrument.
# id = row index (the file has no id).
# Covariates: gender, age band, school level, subject, seniority band, AI use
#   frequency, in-service AI training (Turkish text categories as deposited).
# Item text: not shipped -- the Turkish stems are in the SPSS variable labels
#   (value labels: none), study-authored under the deposit's CC BY; left for an
#   itemtext pass since the response anchors are not in the file.

import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70927716"
TABLE = "pesen_2026_ai_adoption"
COVS = {
    "Cinsiyet": "cov_gender",
    "Yaş": "cov_age_group",
    "GörevYapılanOkulKademesi": "cov_school_level",
    "Branş": "cov_subject",
    "MeslekiKıdem": "cov_seniority",
    "ÖğretimSürecindeYapayZekâTeknolojileriniKullanmaDüzeyi": "cov_ai_use",
    "YapayZekâKullanımınaYönelikHerhangiBirHizmetİçiEğitimAlma": "cov_ai_training",
}
ITEMS = [f"Item{i}" for i in range(1, 23)]


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert d.shape == (352, 29), d.shape
    assert set(d.columns) == set(COVS) | set(ITEMS)
    labels = meta.column_names_to_labels
    for i, c in enumerate(ITEMS, start=1):  # stem number matches the code
        assert labels[c].strip().startswith(f"{i}."), (c, labels[c][:10])
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    allowed = set(range(1, 6))
    long = d[["id"] + ITEMS + covs].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp"
    ).dropna(subset=["resp"])
    assert not set(long["resp"]) - allowed
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: allowed for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {TABLE} {c.name}: {c.detail[:120]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
