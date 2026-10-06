#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/U7Z8AS
# DOI: 10.7819/rbgn.v27i4.4326
#   Rammelt Sauerbronn, Cavazotte & Ferreira (2025), "The influence of authentic
#   leadership and interactional justice on the well-being of employees in the
#   financial sector: the role of the leader's affective presence", Review of
#   Business Management (RBGN) 27(4).
# Data: Harvard Dataverse DVN/U7Z8AS, "Supplementary Data 1 - Dataset and
#       Codebook.xlsx" (file id 13172315): sheet "Dados" (193 bank employees x 57
#       columns) and sheet "Codebook" (Portuguese item stems per column). The
#       deposit's .sav (13173391) carries the same 193 rows plus regression
#       residuals and no variable or value labels. Questionnaire (English and
#       Portuguese .docx) in the same deposit.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: the .sav has no variable labels and no
#   value labels; the xlsx "Codebook" sheet gives the Portuguese stem for every
#   item column (and the deposit's English .docx gives the English wording and
#   anchors), so the text is cheap and tied to the column name. Held because the
#   16 authentic-leadership items are the Authentic Leadership Questionnaire
#   (Walumbwa et al. 2008; Mind Garden, proprietary) -- a rights call, as with
#   the other proprietary instruments in TODO.md. The other three tables'
#   wording is in the same Codebook sheet if wanted.
#
# Scales (questionnaire .docx anchors):
#   authentic_leadership  Autocons1-4, Transp1-4, Moral1-4, Equil1-4   1-5 (strongly disagree..strongly agree)
#   affective_presence    Afetopositivo1-4, Afetonegativo1-4           1-5 (not at all..a great deal)
#                         ("how do YOU feel when interacting with your boss": happy,
#                         enthusiastic, calm, relaxed / bored, sad, stressed, angry);
#                         negative items not reversed (resp direction varies across items)
#   job_satisfaction      Satisf1-4                                    1-7 (strongly disagree..strongly agree)
#   interactional_justice Justinter1-3, Justinfor1-3                   1-6; the .docx prints six
#                         options labelled 1,2,3,5,6,7 (no neutral point); the data
#                         store them as 1-6.
# Dropped: subscale/scale means (Autocons, Transp, Moral, Equil, LIDAUT, Afpos,
#   Afneg, AFETO, Satisf, Justinter, Justinfor, JUST) and TempB ("tempo banco",
#   derived tenure).
# Sample: 193 employees of Brazilian financial institutions; Portuguese administration.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "sauerbronn_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/13172315"

TABLES = {
    "sauerbronn_2025_authentic_leadership": (
        [f"{p}{i}" for i in range(1, 5) for p in ("Autocons", "Transp", "Moral", "Equil")],
        range(1, 6)),
    "sauerbronn_2025_affective_presence": (
        [f"Afetopositivo{i}" for i in range(1, 5)] + [f"Afetonegativo{i}" for i in range(1, 5)],
        range(1, 6)),
    "sauerbronn_2025_job_satisfaction": ([f"Satisf{i}" for i in range(1, 5)], range(1, 8)),
    "sauerbronn_2025_interactional_justice": (
        [f"Justinter{i}" for i in range(1, 4)] + [f"Justinfor{i}" for i in range(1, 4)],
        range(1, 7)),
}
COVS = {
    "Sexo": "cov_sex",               # 1 female, 2 male
    "Idade": "cov_age",
    "Estcivil": "cov_marital_status",  # 1 single 2 married 3 partnership 4 separated 5 other
    "Filhos": "cov_children",        # 1 yes 2 no
    "Instrucao": "cov_education",    # 1 high school .. 6 post-doctorate
    "Anoinicio": "cov_year_started",
    "Tempeq": "cov_team_tenure",
    "Tempofuncao": "cov_role_tenure",
    "Tempolider": "cov_supervisor_tenure",
    "Lider": "cov_leader",           # 1 yes 2 no
}
SKIP = ["Autocons", "Transp", "Moral", "Equil", "LIDAUT", "Afpos", "Afneg", "AFETO",
        "Satisf", "Justinter", "Justinfor", "JUST", "TempB"]


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Dados")
    assert d.shape == (193, 57), d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    assert len(items) == len(set(items)) == 34
    accounted = set(items) | set(COVS) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c in SKIP:
        print(f"  [skip] {c}: derived score")

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), (name, sorted(t["resp"].unique()))
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
