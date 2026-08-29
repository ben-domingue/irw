"""Estevez et al. (2021), Zenodo -- intrinsic motivation, perceived competence
and negative feelings about mathematics homework in Spanish primary school.

Source: https://zenodo.org/records/5156068
DOI: 10.5281/zenodo.5156068
Data: BASE_DATOS_PERFILES.sav
License: CC BY 4.0
Item text: not shipped -- the .sav carries no variable labels and no value
    labels for any item, and the deposit has no codebook. The wording is in the
    paper's instrument appendix (Estevez, Valle, Rodriguez, Pineiro, Vieites,
    Gonzalez-Suarez & Rodriguez-Llorente); only the four Z-score columns carry
    any label at all.

863 primary school students (ages 9-13) across 7 schools, all items on a
1-5 format.

Tables written
--------------
estevez_2021_homework_engagement    863 x 5 items   (Cantid/Tiemp/Aprov.deb + EDE4-5)
estevez_2021_motiv                  863 x 12 items
estevez_2021_gest                   863 x 4 items
estevez_2021_inter                  863 x 3 items
estevez_2021_actitu                 863 x 4 items
estevez_2021_feepr                  863 x 6 items
estevez_2021_feepad                 863 x 5 items
estevez_2021_math_attitudes         863 x 43 items  (IAM1-43)

Coding notes
------------
* Tables are split on the source column prefixes, which are the only grouping
  the deposit provides. `MOITV`/`MOYIV` are typos for `MOTIV` in the source
  and are folded into that block; the item names are kept exactly as the file
  spells them, so `MOITV1`, `MOYIV2` and `MOTIV3` sit side by side in
  `estevez_2021_motiv`.
* `Cantid.deb`, `Tiemp.deb` and `Aprov.tiem.deb` are shipped as items 1-3 of
  the homework block that `EDE4` and `EDE5` complete: the EDE numbering starts
  at 4, all five are on the same 1-5 format, and the three named columns are
  the homework amount/time/time-use items the paper's abstract describes.
  That is a structural inference from the numbering, recorded here rather than
  hidden.
* **`ALUMNO` is not a usable id**: 863 rows carry 862 distinct values, and the
  two rows sharing `ALUMNO=4` differ on age and on nearly every response, so
  they are two students with a collided code rather than one student twice.
  `id` is therefore row position (1-863) and `ALUMNO` is not shipped.
* Dropped as derived, not observed: `IAM9_recod`, `IAM16_recod`,
  `IAM19_recod`, `IAM39_recod` (reverse-scored copies -- the raw `IAM9`,
  `IAM16`, `IAM19`, `IAM39` are shipped instead), the composites
  `perceived.competence`, `anxiety`, `intrinsic.motivation`,
  `negative.feelings`, `academic.performance`, and the two Z-scores.
* The composites decode four IAM subscales exactly, recorded here for whoever
  writes the item text later: perceived competence = mean(IAM1..IAM4);
  anxiety = mean(IAM9_recod, IAM10, IAM11); intrinsic motivation =
  mean(IAM35..IAM39_recod); negative feelings = mean(IAM40, IAM42, IAM43).
  IAM is shipped as one 43-item table because the remaining 28 items are not
  assigned to any named subscale by anything in the deposit.
* Covariates: `cov_school` (CENTRO, 1-7), `cov_age` (EDAD, 9-13),
  `cov_gender` (GENERO, 1/2 -- the deposit does not say which is which),
  `cov_grade` (CURSO, 1/2).
"""

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
REC = "5156068"
FILENAME = "BASE_DATOS_PERFILES.sav"

SCALES = [
    ("homework_engagement",
     ["Cantid.deb", "Tiemp.deb", "Aprov.tiem.deb", "EDE4", "EDE5"]),
    ("motiv", ["MOITV1", "MOYIV2", "MOTIV3", "MOTIV4", "MOTIV5", "MOITV6",
               "MOTIV7", "MOITV8", "MOTIV9", "MOTIV10", "MOTIV11", "MOTIV12"]),
    ("gest", [f"GEST{i}" for i in range(1, 5)]),
    ("inter", [f"INTER{i}" for i in range(1, 4)]),
    ("actitu", [f"ACTITU{i}" for i in range(1, 5)]),
    ("feepr", [f"FEEPR{i}" for i in range(1, 7)]),
    ("feepad", [f"FEEPAD{i}" for i in range(1, 6)]),
    ("math_attitudes", [f"IAM{i}" for i in range(1, 44)]),
]
COVS = {"CENTRO": "cov_school", "EDAD": "cov_age",
        "GENERO": "cov_gender", "CURSO": "cov_grade"}
DERIVED = {"ALUMNO": "collided respondent code, replaced by row position",
           "IAM9_recod": "reverse-scored copy of IAM9",
           "IAM16_recod": "reverse-scored copy of IAM16",
           "IAM19_recod": "reverse-scored copy of IAM19",
           "IAM39_recod": "reverse-scored copy of IAM39",
           "academic.performance": "derived outcome",
           "perceived.competence": "composite of IAM1-4",
           "anxiety": "composite of IAM9_recod/10/11",
           "intrinsic.motivation": "composite of IAM35-39",
           "negative.feelings": "composite of IAM40/42/43",
           "Zperceived.competence": "z-scored composite",
           "Zintrinsic.motivation": "z-scored composite",
           "LPA3": "latent profile assignment, derived"}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{FILENAME}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    df, _ = pyreadstat.read_sav(path)
    return df


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    d = load()
    assert len(d) == 863, len(d)
    assert d["ALUMNO"].nunique() == 862  # the documented collision
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1

    shipped, total = set(), 0
    for suffix, cols in SCALES:
        for c in cols:
            assert c in d.columns, c
        shipped.update(cols)
        long = d[["id"] + cols + list(COVS)].melt(
            id_vars=["id"] + list(COVS), value_vars=cols,
            var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).rename(columns=COVS)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + list(COVS.values())]

        assert long["resp"].between(1, 5).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() >= 2
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"estevez_2021_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        total += len(long)
        print(f"{path}: {long['id'].nunique()} students x "
              f"{long['item'].nunique()} items = {len(long)} responses")

    for c in d.columns:
        if c == "id":
            continue
        assert c in shipped or c in COVS or c in DERIVED, (
            f"unaccounted source column: {c}")
    for c, why in DERIVED.items():
        print(f"  [dropped] {c}: {why}")
    print(f"\n{len(SCALES)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
