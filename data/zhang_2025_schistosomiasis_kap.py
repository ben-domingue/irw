#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/List_of_raw_questionnaire_data_/29847179
# DOI: 10.1371/journal.pntd.0013388
#   Zhang, J., Lin, D., Hu, F., Li, D., Chen, J., Xie, H., Li, Y., & Ding, S. (2025).
#   Research on health education and health promotion during the process of
#   schistosomiasis elimination III: new approaches for student health education. PLOS
#   Neglected Tropical Diseases, 19(8), e0013388.
# Data: S4 Data, "List of raw questionnaire data" (figshare 29847179, file
#       pntd.0013388.s004.xlsx) -- 622 questionnaires from sixth-grade pupils in six
#       classes, at baseline (1) and post-intervention (2), in three education groups
#       (traditional lectures, curriculum-integrated infiltration, stepwise; coded 1-3):
#       Q1-Q13 knowledge, Behaviors1-7 practices, Judgment1-7 attitude judgments, each
#       scored 1 = correct / desirable, 0 = not (the paper reports these as accuracy rates).
# License: CC BY 4.0 (PLOS article and its supplementary data).
#
# Item text: not shipped. Plain xlsx with positional codes and no labels; the questionnaire
#   is not in the supplement.
#
# Tables (0/1 as scored):
#   zhang_2025_schisto_knowledge  Q1-Q13
#   zhang_2025_schisto_practice   Behaviors1-Behaviors7
#   zhang_2025_schisto_attitude   Judgment1-Judgment7
# id: row index. The file has no pupil identifier, so a pupil's baseline and post-test rows
#   cannot be linked; each questionnaire is its own id and the occasion is cov_timepoint
#   (1 baseline, 2 post), not wave.
# Covariates: cov_timepoint, cov_group (1-3 as coded; the paper's three arms), cov_class
#   (e.g. "6(1)").

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "pntd"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/56974670"
P = "zhang_2025_"
RANGE = range(0, 2)
TABLES = {"schisto_knowledge": [f"Q{i}" for i in range(1, 14)],
          "schisto_practice": [f"Behaviors{i}" for i in range(1, 8)],
          "schisto_attitude": [f"Judgment{i}" for i in range(1, 8)]}
COVS = {"pre- and post-intervention": "cov_timepoint", "Group": "cov_group", "Classes": "cov_class"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    items = [c for v in TABLES.values() for c in v]
    assert d.shape == (622, 30) and set(d.columns) == set(items) | set(COVS)
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
