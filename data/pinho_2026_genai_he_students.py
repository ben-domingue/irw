#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/33296244
# DOI: 10.6084/m9.figshare.33296244.v1 (dataset; no paper DOI on the record)
#   Pinho, Claudia Sofia Borges (2026). "Generative AI Use, AI Literacy and
#   Self-Efficacy among Portuguese Higher-Education Students" [data set]. figshare.
# Data: Dados_IA_limpos.csv (Latin-1 with a few UTF-8 strings; see fix_text): 204
#       students of Portuguese HEIs, Dec 2025 - Jun 2026 x id, six demographic strings,
#       82 items on 7-point Likert scales in 22 code-prefixed blocks. No codebook; the
#       record names the constructs: "AI literacy (awareness, usage, evaluation,
#       ethics), performance expectancy, effort expectancy, social influence,
#       facilitating conditions, habit, AI self-efficacy, behavioural intention, and
#       self-reported generative AI usage patterns (writing-related, task-related,
#       reliance)".
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: CSV headers are codes only (no labels, no
#   codebook); the European-Portuguese wording is not in the deposit.
#
# Tables -- only the blocks whose construct the record names:
#   pinho_2026_ai_literacy       AWA1-3, USA1-3, EVA1-3, ETH1-3 (awareness, usage,
#                                evaluation, ethics: one AI-literacy scale, 12 items).
#                                AWA2_R, USA2_R, ETH2_R are STORED REVERSE-SCORED (each
#                                correlates positively, r = .19-.32, with its block's
#                                item 1), kept as stored under their own names.
#   pinho_2026_performance_expectancy  PE1-4
#   pinho_2026_effort_expectancy       EE1-4
#   pinho_2026_social_influence        SI1-3
#   pinho_2026_facilitating_conditions FC1-4
#   pinho_2026_habit                   HT1-4
#   pinho_2026_ai_self_efficacy        SE1-6
#   pinho_2026_behavioral_intention    BI1-3
#   pinho_2026_genai_writing_use       WRIT1-7
#   pinho_2026_genai_task_use          TASK1-4
#   pinho_2026_genai_reliance          REL1-4
#   All 1-7, no missing cells.
# Not shipped: PU1-3, PEOU1-5, PINT1-3, AI1-3, PT1-3, PR1-3, PI1-4, HM1-3 -- the record
#   does not name these constructs (TAM/UTAUT2-style abbreviations, but undocumented).
# Covariates (Portuguese strings as recorded): cov_gender, cov_age (Idade, years),
#   cov_study_year, cov_field, cov_prior_ai_experience, cov_ai_use_frequency.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "pinho_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/67697751"
P = "pinho_2026_"
TABLES = {
    "ai_literacy": ["AWA1", "AWA2_R", "AWA3", "USA1", "USA2_R", "USA3",
                    "EVA1", "EVA2", "EVA3", "ETH1", "ETH2_R", "ETH3"],
    "performance_expectancy": [f"PE{i}" for i in range(1, 5)],
    "effort_expectancy": [f"EE{i}" for i in range(1, 5)],
    "social_influence": [f"SI{i}" for i in range(1, 4)],
    "facilitating_conditions": [f"FC{i}" for i in range(1, 5)],
    "habit": [f"HT{i}" for i in range(1, 5)],
    "ai_self_efficacy": [f"SE{i}" for i in range(1, 7)],
    "behavioral_intention": [f"BI{i}" for i in range(1, 4)],
    "genai_writing_use": [f"WRIT{i}" for i in range(1, 8)],
    "genai_task_use": [f"TASK{i}" for i in range(1, 5)],
    "genai_reliance": [f"REL{i}" for i in range(1, 5)],
}
UNDOCUMENTED = (["PU1", "PU2", "PU3"] + [f"PEOU{i}" for i in range(1, 6)]
                + ["PINT1", "PINT2", "PINT3", "AI1", "AI2", "AI3", "PT1", "PT2", "PT3",
                   "PR1", "PR2", "PR3", "PI1", "PI2", "PI3", "PI4", "HM1", "HM2", "HM3"])
COVS = ["cov_gender", "cov_age", "cov_study_year", "cov_field",
        "cov_prior_ai_experience", "cov_ai_use_frequency"]


def fetch() -> Path:
    p = RAW_DIR / "Dados_IA_limpos.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def fix_text(v):
    """The file is Latin-1, but a few values were written as UTF-8 bytes."""
    if isinstance(v, str):
        try:
            return v.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return v
    return v


def main() -> None:
    d = pd.read_csv(fetch(), encoding="latin-1")
    assert d.shape == (204, 89) and d["id"].is_unique
    demo = list(d.columns[1:7])
    d = d.rename(columns=dict(zip(demo, COVS)))
    for c in COVS:
        d[c] = d[c].map(fix_text)
    items = [c for v in TABLES.values() for c in v]
    assert set(d.columns) == {"id"} | set(COVS) | set(items) | set(UNDOCUMENTED)
    print(f"  [skip] {UNDOCUMENTED}: constructs not named in the record")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for suf, its in TABLES.items():
        name = P + suf
        assert len(name) <= 40
        t = d.melt(id_vars=["id"] + COVS, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].notna().all() and t["resp"].isin(range(1, 8)).all(), name
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: set(range(1, 8)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
