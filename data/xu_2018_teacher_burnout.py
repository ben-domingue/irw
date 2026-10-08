#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SUKK1K
# DOI: 10.7910/DVN/SUKK1K (dataset; no paper on the record)
#   Xu, Zhihua (2018). "burnout" [data set], Harvard Dataverse. Record description:
#   "leadership, empowerment and burnou[t]".
# Data: burnout.sav (file 3109231): 378 Chinese school teachers x 63 columns with Chinese
#       headers: school number, five coded demographics, then four item blocks. No variable
#       labels, no value labels, no codebook.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: .sav variable labels (empty) and value labels
#   (empty); the Chinese headers name only the subscale and item number.
#
# Item codes: the Chinese headers transliterated reversibly to an English subscale slug +
#   the header's own number (e.g. 透明1 -> transparency_1); the map is SUB below.
# Tables (all 1-5; constructs read from the subscale names, which match the standard
#   instruments' subscales item-for-item in count):
#   xu_2018_authentic_leadership  透明1-5, 道德1-4, 平衡1-3, 自意1-4 (16): transparency,
#                                 moral, balanced processing, self-awareness -- the ALQ
#                                 structure
#   xu_2018_psych_empowerment     工作意义, 自主, 自我效能, 工作影响 1-3 (12): meaning,
#                                 autonomy, self-efficacy, impact (Spreitzer)
#   xu_2018_emotional_exhaustion  精力枯竭1-9 and 精力枯竭10反 (10). The header marks item 10
#                                 反 (reverse-keyed); it correlates positively with items
#                                 1-9 (r = .23-.38), i.e. it is stored reverse-scored.
#   xu_2018_structural_empowerment 信息, 支持, 资源, 机会, 正式权力 1-3, 非正式权力 1-4 (19):
#                                 information, support, resources, opportunity, formal and
#                                 informal power (CWEQ-II structure)
# Rows: 12 rows duplicate another row on all 63 columns (not straight-liners: 3-5 distinct
#   values each, in runs of nearby rows from the same school), i.e. entered twice; they are
#   dropped, leaving 366 teachers. id = row order after dropping.
# Covariates (codes, no labels in the deposit): cluster_id = 学校编号 (school number),
#   cov_gender (性别 0/1), cov_education (教育水平 1-4), cov_school_level (小初高 1-3:
#   primary / junior / senior high by its name), cov_teaching_years (教龄 1-5, banded),
#   cov_married (婚姻 0/1).

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "xu_2018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/3109231?format=original"

SUB = {"透明": "transparency", "道德": "moral", "平衡": "balanced", "自意": "self_awareness",
       "工作意义": "meaning", "自主": "autonomy", "自我效能": "self_efficacy",
       "工作影响": "impact", "精力枯竭": "exhaustion", "信息": "information", "支持": "support",
       "资源": "resources", "机会": "opportunity", "正式权力": "formal_power",
       "非正式权力": "informal_power"}
TABLES = {"xu_2018_authentic_leadership": ["透明", "道德", "平衡", "自意"],
          "xu_2018_psych_empowerment": ["工作意义", "自主", "自我效能", "工作影响"],
          "xu_2018_emotional_exhaustion": ["精力枯竭"],
          "xu_2018_structural_empowerment": ["信息", "支持", "资源", "机会", "正式权力", "非正式权力"]}
COUNTS = {"xu_2018_authentic_leadership": 16, "xu_2018_psych_empowerment": 12,
          "xu_2018_emotional_exhaustion": 10, "xu_2018_structural_empowerment": 19}
COVS = {"学校编号": "cluster_id", "性别": "cov_gender", "教育水平": "cov_education",
        "小初高": "cov_school_level", "教龄": "cov_teaching_years", "婚姻": "cov_married"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def code(col: str) -> str:
    m = re.fullmatch(r"(\D+?)(\d+)(反?)", col)
    stem, n, rev = m.groups()
    return f"{SUB[stem]}_{n}{'_rev' if rev else ''}"


def main() -> None:
    d, _ = pyreadstat.read_sav(fetch())
    assert d.shape == (378, 63), d.shape
    cols = {t: [c for c in d.columns if re.fullmatch(r"(\D+?)\d+反?", c) and
                re.match(r"\D+?(?=\d)", c).group(0) in stems] for t, stems in TABLES.items()}
    for t, cs in cols.items():
        assert len(cs) == COUNTS[t], (t, len(cs))
    assert set(d.columns) == set(COVS) | {c for cs in cols.values() for c in cs}
    nd = int(d.duplicated().sum())
    d = d[~d.duplicated()].reset_index(drop=True)
    print(f"  dropped {nd} rows duplicating another row on every column")
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, cs in cols.items():
        cmap = {c: code(c) for c in cs}
        assert len(set(cmap.values())) == len(cmap)
        t = d[["id"] + covs + cs].rename(columns=cmap).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "cluster_id"] + covs[1:]]
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in cmap.values()}
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
