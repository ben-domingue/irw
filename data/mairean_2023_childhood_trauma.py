#!/usr/bin/env python3
# Source: https://zenodo.org/records/7668169
# DOI: none found. The deposit has no related identifiers or description
#   beyond one sentence, and Crossref/Europe PMC title and author searches
#   (2026-10-02) found no paper for this sample.
#   Mairean, C. (2023). "Childhood trauma and psychological well-being. The
#   mediating role of psychological flexibility." Zenodo.
#   https://doi.org/10.5281/zenodo.7668169
# Data: Database.sav (261 rows x 143 columns; Romanian adults 17-63).
#   No other dataset by this author is in ../data/, dictionary_auto.csv or
#   metadata/biblio.csv (grep, 2026-10-02).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: the variable labels are
#   block names only, on the first item of each block ("trauma din
#   copilarie", "flexibilitatea psihologica", ...); the value labels carry
#   the Romanian response anchors for every item. No stems at either level.
#   The stems are in the published instruments (CTQ-SF, MPFI, SCS-SF,
#   PWB-PTCQ) and their Romanian versions, which are not in the deposit.
#
# Instrument identities: no paper, so these rest on the deposit's own block
# labels, item counts, value labels and score columns, which line up with
# published instruments as follows:
#   CTQ1-25   childhood trauma ("trauma din copilarie"): 25 items, five
#             5-item scores (emotional/physical/sexual abuse, emotional/
#             physical neglect) -- the 25 clinical items of the Childhood
#             Trauma Questionnaire-Short Form. 1 niciodata adevarat ..
#             5 de foarte multe ori adevarat.
#   MPFI1-30  psychological flexibility ("flexibilitatea psihologica"): 30
#             items whose sum is the "flexibility" score (30-180), the
#             flexibility half of the Multidimensional Psychological
#             Flexibility Inventory. 1 niciodata .. 6 intotdeauna adevarat.
#   SCS1-12   self-compassion ("auto-compasiunea"), 12 items = SCS-SF.
#             1 aproape niciodata .. 5 aproape intotdeauna.
#   PWB1-18   psychological well-being, 18 items rated as change since the
#             event (1 cu mult mai putin acum "much less now" .. 5 cu mult
#             mai mult acum "much more now") with six 3-item scores
#             (self-acceptance, autonomy, purpose, relationship, mastery,
#             growth) = the Psychological Well-Being Post-Traumatic Changes
#             Questionnaire (PWB-PTCQ).
#   LEC1-10   life events ("evenimente din viata"), 10 items, 0 nu / 1 da.
#             The checklist is not identified further.
# Permitted values are the value-label sets above (asserted to be attached
# to every item of the block). Each block's total equals the raw sum of its
# items (asserted: CTQ, flexibility, self.compassion, PWB, and the six PWB
# and five CTQ sub-scores' sums), so any reverse-keyed items are stored as
# they entered those totals; the deposit does not say which.
#
# Tables (item codes are the source column names):
#   mairean_2023_ctq          CTQ1-CTQ25
#   mairean_2023_mpfi         MPFI1-MPFI30
#   mairean_2023_scs_sf       SCS1-SCS12
#   mairean_2023_pwb_ptcq     PWB1-PWB18
#   mairean_2023_life_events  LEC1-LEC10
#
# Dropped: all computed columns (sub-scores, totals, z-scores and their
#   products: 44 columns, listed in COMPOSITES).
# id: row index (no respondent id in the file).
# Covariates: cov_education (Studii: 1 gimnaziale .. 5 postuniversitare),
#   cov_religion (Orientare_rel: 1 Orthodox, 2 Catholic, 3 non-religious,
#   4 other), cov_gender (Genul: 1 male, 2 female), cov_age (Varsta),
#   cov_residence (Mediu_prov: 1 rural, 2 urban).

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
URL = "https://zenodo.org/api/records/7668169/files/Database.sav/content"


def block(p, n):
    return [f"{p}{i}" for i in range(1, n + 1)]


TABLES = {
    "mairean_2023_ctq": block("CTQ", 25),
    "mairean_2023_mpfi": block("MPFI", 30),
    "mairean_2023_scs_sf": block("SCS", 12),
    "mairean_2023_pwb_ptcq": block("PWB", 18),
    "mairean_2023_life_events": block("LEC", 10),
}
LABELS = {
    "mairean_2023_ctq": {1.0: "niciodata adevarat", 2.0: "rareori adevarat",
                         3.0: "uneori adevarat", 4.0: "deseori adevarat",
                         5.0: "de foarte multe ori adevarat"},
    "mairean_2023_mpfi": {1.0: "niciodata adevarat",
                          2.0: "rareori adevarat", 3.0: "uneori adevarat",
                          4.0: "deseori adevarat",
                          5.0: "de foarte multe ori adevarat",
                          6.0: "intotdeauna adevarat"},
    "mairean_2023_scs_sf": {1.0: "aproape niciodata", 2.0: "rareori",
                            3.0: "uneori", 4.0: "deseori",
                            5.0: "aproape intotdeauna"},
    "mairean_2023_pwb_ptcq": {1.0: "cu mult mai putin acum",
                              2.0: "un pic mai putin acum",
                              3.0: "simt la fel ca inainte",
                              4.0: "un pic mai mult acum",
                              5.0: "cu mult mai mult acum"},
    "mairean_2023_life_events": {0.0: "nu", 1.0: "da"},
}
COMPOSITES = {
    "self.acceptance", "autonomy", "purpose", "relationship", "mastery",
    "growth", "PWB", "emotional.abuse", "physical.abuse", "sexual.abuse",
    "emotional.neglect", "physical.neglect", "self.compassion",
    "flexibility", "Zemotional.abuse", "Zphysical.abuse", "Zsexual.abuse",
    "Zemotional.neglect", "Zphysical.neglect", "Zself.compassion",
    "Zflexibility", "FelxibilityxEA", "FelxibilityxPA", "FelxibilityxSA",
    "FelxibilityxEN", "FelxibilityxPN", "CompassionxEA", "CompassionxPA",
    "CompassionxSA", "CompassionxEN", "CompassionxPN", "CTQ", "ZCTQ",
    "CTQxcomps", "CTQxflexibility", "Abuse", "neglect", "ZAbuse",
    "Zneglect", "abusexflexib", "neglectxflexib", "neglectxcompas",
    "abusexcompas"}
COVS = {"Studii": "cov_education", "Orientare_rel": "cov_religion",
        "Genul": "cov_gender", "Varsta": "cov_age",
        "Mediu_prov": "cov_residence"}


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
    assert d.shape == (261, 143), d.shape

    # Balance the books.
    items = [c for its in TABLES.values() for c in its]
    known = set(items) | COMPOSITES | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(COMPOSITES) == 143 - len(items) - len(COVS)

    assert not d.duplicated().any()
    assert not d[items].T.duplicated().any()
    for table, its in TABLES.items():
        for c in its:
            assert meta.variable_value_labels[c] == LABELS[table], c
    assert (d[TABLES["mairean_2023_ctq"]].sum(axis=1) == d["CTQ"]).all()
    assert (d[["emotional.abuse", "physical.abuse", "sexual.abuse",
               "emotional.neglect", "physical.neglect"]].sum(axis=1)
            == d["CTQ"]).all()
    assert (d[TABLES["mairean_2023_mpfi"]].sum(axis=1)
            == d["flexibility"]).all()
    assert (d[TABLES["mairean_2023_scs_sf"]].sum(axis=1)
            == d["self.compassion"]).all()
    assert (d[TABLES["mairean_2023_pwb_ptcq"]].sum(axis=1) == d["PWB"]).all()
    assert (d[["self.acceptance", "autonomy", "purpose", "relationship",
               "mastery", "growth"]].sum(axis=1) == d["PWB"]).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        allowed = {int(k) for k in LABELS[table]}
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
