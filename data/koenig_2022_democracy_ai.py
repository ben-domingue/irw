#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/226PMX
# DOI: 10.7910/DVN/226PMX
#   König, P. (2022). Replication Data for: Citizen Conceptions of Democracy
#   and Support for Artificial Intelligence in Government and Politics
#   [Dataset]. Harvard Dataverse.
# Data: "Data_Conceptions_Demmocracy.RData" -- 1,115 German survey
#   respondents, 160 columns of a SoSci Survey export. The deposit also ships
#   "Questionnaire - English translation.pdf", which is what makes any of this
#   nameable: the data's column prefixes are opaque codes (PL04, PS04, VT04),
#   and that PDF's overview table maps each code to its construct.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped. The questionnaire PDF carries the item wording in
#   ENGLISH TRANSLATION of a German administration, which under the existing
#   convention is `translated_substitute` text, not the administered wording,
#   and the German original is in neither the data nor the deposit. A text
#   pass needs the German questionnaire, so it is a fetch, not an extraction.
#
# THREE tables ship, and the reason the rest does not is a count that does not
#   match. The PDF's overview names sixteen codes; for three of them the
#   number of items in the PDF equals the number of columns in the data, so
#   the mapping is certain:
#     koenig_2022_ai_in_government    PL04, 6 items, 1-5  (six named uses of
#                                     AI in public administration/politics)
#     koenig_2022_ambiguity_intolerance  PS04, 6 items, 1-5 (six bipolar
#                                     statement pairs; the data's suffixes run
#                                     01-04, 06, 08, i.e. the retained six of
#                                     eight positions)
#     koenig_2022_institutional_trust VT04, 5 items, 1-7  (parliament, justice
#                                     system, federal government, parties,
#                                     public administration)
#
# DEFERRED, not rejected -- four more blocks are plainly item responses but
#   cannot be named from this deposit without guessing:
#     DE05/DE06/DE07/DE08  36 columns at 1-7, against the PDF's single "DE5
#                          Conceptions of democracy" entry listing 21
#                          statements. Four data blocks, one questionnaire
#                          entry, and 36 != 21.
#     PL05                 10 columns at 1-5, a code the PDF's overview does
#                          not list at all.
#     PL06                 8 columns at 1-5 against 7 listed statements.
#     TE06                 8 columns at 1-5 against 7 listed statements, and
#                          792 missing cells, so one column is also mostly
#                          unanswered.
#   In each case shipping would mean choosing which column is the extra one,
#   and nothing in the deposit says. Recorded in the batch's leads file.
#
# NOT SHIPPED, the rest: 21 TIME* page timers and the survey's own quality
#   indices (TIME_SUM, TIME_RSI, DEG_TIME, MISSING, MISSREL, LASTPAGE,
#   MAXPAGE, FINISHED, Q_VIEWER, QUESTNNR, MODE, KO01, SERIAL, MAILSENT), the
#   four all-empty blocks DE01/DE02/DE03/DE04 and the two PL07 columns.
#
# The categorical covariates are NOT shipped because their text is corrupt in
#   the deposit: KE03's categories read "MÃƒÂ¤ÃƒÂŸig gute Kenntnisse" -- a
#   double mojibake of "Mäßig" that cannot be reliably reversed, and DG15,
#   DG03 and VT05 are stored the same way. Shipping a guessed de-mojibake as a
#   covariate label would be worse than leaving them out.
#
# id: the row index. The export's SERIAL column is empty for all 1,115 rows.
# Covariates: cov_age (years, 18+), cov_left_right (1-7), cov_economic_policy
#   (1-7), cov_immigration_policy (1-7), cov_ai_evaluation (1-7, missing for
#   93), cov_satisfaction_democracy (1-7, missing for 4) -- the PDF documents
#   each one's endpoints.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadr
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "226pmx" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 6330254, "Data_Conceptions_Demmocracy.RData"
TABLES = {
    "koenig_2022_ai_in_government": (
        ["PL04_01", "PL04_02", "PL04_03", "PL04_04", "PL04_05", "PL04_06"],
        set(range(1, 6))),
    "koenig_2022_ambiguity_intolerance": (
        ["PS04_01", "PS04_02", "PS04_03", "PS04_04", "PS04_06", "PS04_08"],
        set(range(1, 6))),
    "koenig_2022_institutional_trust": (
        ["VT04_01", "VT04_02", "VT04_03", "VT04_04", "VT04_05"],
        set(range(1, 8))),
}
COVS = {"age": "cov_age", "PL01_01": "cov_left_right",
        "PL02_01": "cov_economic_policy", "PL03_01": "cov_immigration_policy",
        "TE04_01": "cov_ai_evaluation",
        "VT06_01": "cov_satisfaction_democracy"}
DEFERRED = ["DE05", "DE06", "DE07", "DE08", "PL05", "PL06", "TE06"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pyreadr.read_r(str(fetch()))["df"]
    assert df.shape == (1115, 160), df.shape

    # The deferred blocks are still here; assert the counts this header cites
    # so a later pass starts from a checked statement, not a remembered one.
    counts = {p: sum(c.startswith(p) for c in df.columns) for p in DEFERRED}
    assert counts == {"DE05": 12, "DE06": 8, "DE07": 8, "DE08": 8,
                      "PL05": 10, "PL06": 8, "TE06": 8}, counts
    print(f"deferred, unnameable from this deposit: {counts}")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")
    assert df["cov_age"].min() >= 18

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols, scale) in TABLES.items():
        missing = [c for c in cols if c not in df.columns]
        assert not missing, (name, missing)
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 1000 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:140]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
