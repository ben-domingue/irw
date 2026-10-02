#!/usr/bin/env python3
# Source: https://zenodo.org/records/14870714
# DOI: 10.1371/journal.pone.0346573
#   Sanchez-Garcia, J., Cebrian, J., Fernandez-del-Rio, E., &
#   Ramos-Villagrasa, P. J. (2026). "The role of personality traits and
#   moral disengagement in academic dishonesty: An analysis of the big five
#   and dark tetrad." PLOS One. (Read from Europe PMC full text,
#   PMC13052905; its data statement cites zenodo.14870713, the concept DOI
#   of this record. The deposit itself has no related identifiers.)
#   Dataset: Sanchez-Garcia, J., Cebrian, J., Fernandez-Rios, E., &
#   Ramos-Villagrasa, P. J. (2025). Dataset for The Role of Personality
#   Traits and Moral Disengagement in Academic Dishonesty. Zenodo.
#   https://doi.org/10.5281/zenodo.14870714
# Data: Dataset_VASSIP.sav (175 rows x 119 columns): the paper's final
#   sample of 175 Spanish university students (13 attention-check failures
#   and 2 "other"-gender respondents already removed by the authors).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: variable labels are
#   block names only ("BIG FIVE", "DARK TETRAD", "MORAL DISENGAGEMENT",
#   "ACAMEDIC DISHONESTY"); no value labels on any item. The BFI-2 family is
#   a rights-register block. The SD4, moral-disengagement and academic-
#   dishonesty stems are in their Spanish versions (refs 83, 85, 87 of the
#   paper), not in the deposit.
#
# Scale identities and ranges (paper, "Instruments"):
#   - VASSIP: a gamified administration of the BFI-2-S, 30 items, 1 strongly
#     disagree .. 5 strongly agree.
#   - Short Dark Tetrad (SD4), Spanish version: 28 items, 1-5, 7 per
#     dimension (Machiavellianism, narcissism, psychopathy, sadism).
#   - Moral disengagement (Moore et al. 2012), 8 items, 1-7.
#   - Academic dishonesty (Marsden et al.; Spanish adaptation by
#     Dominguez-Lara & Lingan-Huaman), 14 items in three dimensions
#     (cheating 4, plagiarism 5, falsification 5), 1 never .. 5 many times.
#     Column numbers (EDA_04 .. EDA_19) are the source numbering.
#
# Tables (item codes are the source column names):
#   sanchezgarcia_2025_vassip_bfi2s          BFI_1-BFI_30 (N 174)
#   sanchezgarcia_2025_sd4                   SD4_Maq_01 .. SD4_Sad_28
#   sanchezgarcia_2025_moral_disengagement   MoralDis_01-08
#   sanchezgarcia_2025_academic_dishonesty   EDA_04_Trampas .. (14)
#   The four non-BFI blocks were answered by 164 of the 175 (11 rows have
#   only the VASSIP block); one row has no VASSIP answers.
#
# Dropped:
#   - BFI_*_inv (15 columns): reverse-coded copies, BFI_k_inv = 6 - BFI_k in
#     every row (asserted).
#   - AttentionCheck ("score this a 2"): 2 in every answered row (asserted).
#   - DataPrivacy, Participate: consent flags, 1 in every answered row
#     (asserted) and identical to each other.
#   - The experience free-text field ("Pensando en toda su vida laboral...")
#     and Sector_Cualitativo: free text on work experience and sector
#     (checked: no names, contacts or clinical content); Sector: a numeric
#     sector code with no labels.
#   - Composites: MoralDis, the four SD4 means, EDA_Traps/Plag/Fals and the
#     five BFI domain scores.
# id: row index. "ID" (31-219, unique) is a study sequence number and is
#   not shipped.
# Covariates: cov_sex (0 women, 1 men), cov_age, cov_education
#   (0 primary .. 6 doctorate), cov_working (0 no, 1 yes).

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/14870714/files/"
       "Dataset_VASSIP.sav/content")

BFI = [f"BFI_{i}" for i in range(1, 31)]
SD4 = ([f"SD4_Maq_{i:02d}" for i in range(1, 8)]
       + [f"SD4_Nar_{i:02d}" for i in range(8, 15)]
       + [f"SD4_Psi_{i:02d}" for i in range(15, 22)]
       + [f"SD4_Sad_{i:02d}" for i in range(22, 29)])
MD = [f"MoralDis_{i:02d}" for i in range(1, 9)]
EDA = ["EDA_04_Trampas", "EDA_06_Trampas", "EDA_07_Trampas",
       "EDA_08_Trampas", "EDA_09_Plagio", "EDA_10_Plagio", "EDA_11_Plagio",
       "EDA_12_Falsificacion", "EDA_13_Falsificacion", "EDA_14_Plagio",
       "EDA_15_Plagio", "EDA_17_Falsificacion", "EDA_18_Falsificacion",
       "EDA_19_Falsificacion"]
TABLES = {
    "sanchezgarcia_2025_vassip_bfi2s": (BFI, range(1, 6)),
    "sanchezgarcia_2025_sd4": (SD4, range(1, 6)),
    "sanchezgarcia_2025_moral_disengagement": (MD, range(1, 8)),
    "sanchezgarcia_2025_academic_dishonesty": (EDA, range(1, 6)),
}
REVERSED = {f"BFI_{k}_inv": f"BFI_{k}"
            for k in (1, 21, 26, 7, 17, 27, 3, 8, 28, 14, 19, 24, 10, 20,
                      30)}
COMPOSITES = {"MoralDis", "SD4_Machiavellianism", "SD4_Narcissism",
              "SD4_Psychopathy", "SD4_Sadism", "EDA_Traps", "EDA_Plag",
              "EDA_Fals", "Extraversion", "Agreeableness",
              "Conscientiousness", "NegativeEmotionality", "OpenMindedness"}
OTHER_DROPPED = {"ID", "AttentionCheck", "DataPrivacy", "Participate",
                 "PensandoentodasuvidalaboralcuántaexperienciatieneInd",
                 "Sector", "Sector_Cualitativo"}
COVS = {"Sex": "cov_sex", "Edad": "cov_age",
        "EducationLevel": "cov_education", "Working": "cov_working"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (175, 119), d.shape

    # Balance the books.
    items = [c for its, _ in TABLES.values() for c in its]
    known = set(items) | set(REVERSED) | COMPOSITES | OTHER_DROPPED \
        | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(items) == len(set(items)) == 80

    assert d["ID"].is_unique
    assert not d.drop(columns="ID").duplicated().any()
    assert not d[items].T.duplicated().any()
    for alt, src in REVERSED.items():
        ok = (d[alt] == 6 - d[src]) | (d[alt].isna() & d[src].isna())
        assert ok.all(), alt
    assert set(d["AttentionCheck"].dropna()) == {2}
    for c in ("DataPrivacy", "Participate"):
        assert set(d[c].dropna()) == {1}, c
    assert (d[MD].sum(axis=1, min_count=1).dropna()
            == d["MoralDis"].dropna()).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        allowed = set(allowed)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
