#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/30178486
# DOI: 10.6084/m9.figshare.30178486
#   Liu, X., Zhang, K., Cao, Y., & Chen, S. (2025). Social Media Use, Body
#   Image, and Self-Esteem Among Chinese Adolescents: Experimental and Survey
#   Data (N = 1,113) [Dataset]. figshare.
# Data: three .sav files -- a 961-student survey (study 2), a 152-student
#   image-exposure experiment with a pre/post self-esteem measure (study 1),
#   and a 39-row file of study-1 totals only.
# License: CC BY 4.0 (verified on the figshare record, 2026-10-19).
# Item text: NOT shipped. Only the FIRST column of each block carries a label,
#   and it names the instrument rather than the item ("Self-Esteem Scale",
#   "BAS", "SE"); the other nine are blank. So the deposit names its scales
#   but not its items, and the wording is in the published instruments.
#   Self-esteem is almost certainly the RSES (register verdict `ship`) and the
#   Body Appreciation Scale has no register row -- both worth a later pass,
#   neither resolvable from this file.
#
# THREE tables:
#   liu_2025_body_appreciation      961 students, 10 items, 1-7 (study 2)
#   liu_2025_self_esteem_study2     961 students, 10 items, 1-5 (study 2)
#   liu_2025_self_esteem_study1     152 students, 10 items, 1-4, TWO WAVES
#                                   (study 1's pre/post measure)
#
# THE TWO STUDY-1 BLOCKS ARE ONE SCALE MEASURED TWICE, which is why they share
#   a table and differ on `wave`: `B1-B10` and `G1-G10` both carry the label
#   "Self-Esteem Scale", both use the same four value labels (1 strongly
#   disagree .. 4 strongly agree), and the deposit's own
#   Pre_/Post_test_self_esteem_total_score equal the B and G sums respectively
#   for all 152 respondents -- which is the arithmetic check that B is the
#   pre-test and G the post-test. Items ship as SE1-SE10 so one item links
#   across the waves.
#
# TWO CELLS HOLD 7 ON A 1-4 SCALE, both in the pre-test block, against value
#   labels that stop at 4. Out of range and undocumented, so those two
#   item-responses are dropped rather than recoded; everything else in the
#   block is 1-4. The deposit's totals were computed INCLUDING them, which is
#   one more reason no total is shipped.
#
# NOT SHIPPED: "Study 1 self-esteem.sav", which is 39 rows of pre/post TOTAL
#   scores split by image condition -- aggregates, and below the N floor
#   either way; the study-2 sums (BASsum, SEsum) and the study-1 totals; and
#   the cultural-confidence, residence and weight questions, which are single
#   items of their own content.
#
# id: the row index, per study. Neither file carries a usable respondent id
#   (study 1's 编号 is 1-7 repeated, study 2's `number` is a row counter).
# Covariates: cov_age, cov_gender, cov_grade, cov_origin and cov_social_media
#   _use in both studies; study 1 adds cov_group, its 2x2 image condition
#   (11/12/21/22, 38 respondents each), which does not fit `treat` because
#   that is one 0/1 column.
import os
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "30178486" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 30178486
S1_FILE = "Study 1 middle school student survey-images(1-152).sav"
S2_FILE = "study2-961students.sav"
N_ITEMS = 10


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == name][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def ship(t, name, scale, cov_cols, n_ids, wave=False):
    key = ["id", "item", "wave"] if wave else ["id", "item"]
    cols = ["id", "item", "resp"] + (["wave"] if wave else []) + cov_cols
    t = t[cols]
    assert not t.duplicated(key).any(), name
    assert t["id"].nunique() == n_ids and t["item"].nunique() == N_ITEMS, name
    checks = run_qc(t, permitted_values=scale)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
    report = irw_validate.validate_frame(t, label=name, profile="upload",
                                         context={"permitted_values": scale})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()}"
          + (f" waves={t['wave'].nunique()}" if wave else "")
          + f" resp={t['resp'].min()}-{t['resp'].max()}")


def main():
    # ---- study 2: Body Appreciation Scale and self-esteem -----------------
    s2, m2 = pyreadstat.read_sav(str(fetch(S2_FILE)), apply_value_formats=False)
    assert len(s2) == 961, len(s2)
    bas = [f"R{i}" for i in range(1, N_ITEMS + 1)]
    se2 = [f"Q{i}" for i in range(1, N_ITEMS + 1)]
    assert (m2.column_names_to_labels.get("R1") or "").strip() == "BAS"
    assert (m2.column_names_to_labels.get("Q1") or "").strip() == "SE"
    assert not s2[bas + se2].isna().any().any()
    assert (s2[bas].sum(axis=1) == s2["BASsum"]).all(), "BASsum is not the sum"
    assert (s2[se2].sum(axis=1) == s2["SEsum"]).all(), "SEsum is not the sum"
    print("study 2: BASsum and SEsum both equal their block sums for all 961")
    s2 = s2.rename(columns={"age": "cov_age", "gender": "cov_gender",
                            "grade": "cov_grade", "from": "cov_origin",
                            "SMU": "cov_social_media_use"})
    covs2 = ["cov_age", "cov_gender", "cov_grade", "cov_origin",
             "cov_social_media_use"]
    for c in covs2:
        s2[c] = pd.to_numeric(s2[c]).astype("Int64")
    s2["id"] = range(1, len(s2) + 1)
    for name, cols, scale in (
            ("liu_2025_body_appreciation", bas, set(range(1, 8))),
            ("liu_2025_self_esteem_study2", se2, set(range(1, 6)))):
        t = (s2[["id", *covs2, *cols]]
             .rename(columns={c: f"SE{i}" if cols is se2 else f"BAS{i}"
                              for i, c in enumerate(cols, 1)})
             .melt(id_vars=["id", *covs2],
                   value_vars=[f"SE{i}" if cols is se2 else f"BAS{i}"
                               for i in range(1, N_ITEMS + 1)],
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"]).astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the observed scale: {bad}"
        ship(t, name, scale, covs2, 961)

    # ---- study 1: the same self-esteem scale, pre and post ---------------
    s1, m1 = pyreadstat.read_sav(str(fetch(S1_FILE)), apply_value_formats=False)
    assert len(s1) == 152, len(s1)
    pre = [f"B{i}" for i in range(1, N_ITEMS + 1)]
    post = [f"G{i}" for i in range(1, N_ITEMS + 1)]
    for first in ("B1", "G1"):
        assert (m1.column_names_to_labels.get(first) or "").strip() == \
            "Self-Esteem Scale", first
    assert set(m1.variable_value_labels.get("B1", {})) == {1, 2, 3, 4}
    assert (s1[pre].sum(axis=1) == s1["Pre_test_self_esteem_total_score"]).all()
    assert (s1[post].sum(axis=1) == s1["Post_test_self_esteem_total_score"]).all()
    print("study 1: the pre and post totals equal the B and G sums for all 152,"
          " which is what identifies B as pre-test and G as post-test")
    s1 = s1.rename(columns={"age": "cov_age", "gender": "cov_gender",
                            "grade": "cov_grade", "from": "cov_origin",
                            "social_media_browsing": "cov_social_media_use",
                            "group": "cov_group"})
    covs1 = ["cov_age", "cov_gender", "cov_grade", "cov_origin",
             "cov_social_media_use", "cov_group"]
    for c in covs1:
        s1[c] = pd.to_numeric(s1[c]).astype("Int64")
    s1["id"] = range(1, len(s1) + 1)
    frames = []
    for wave, cols in ((1, pre), (2, post)):
        part = (s1[["id", *covs1, *cols]]
                .rename(columns={c: f"SE{i}" for i, c in enumerate(cols, 1)})
                .melt(id_vars=["id", *covs1],
                      value_vars=[f"SE{i}" for i in range(1, N_ITEMS + 1)],
                      var_name="item", value_name="resp"))
        part["wave"] = wave
        frames.append(part)
    t = pd.concat(frames, ignore_index=True)
    t["resp"] = pd.to_numeric(t["resp"])
    scale = set(range(1, 5))
    out_of_range = int((~t["resp"].isin(scale)).sum())
    assert out_of_range == 2, out_of_range
    t = t[t["resp"].isin(scale)].copy()
    t["resp"] = t["resp"].astype(int)
    print(f"study 1: dropped {out_of_range} responses coded 7 on a 1-4 scale")
    ship(t, "liu_2025_self_esteem_study1", scale, covs1, 152, wave=True)


if __name__ == "__main__":
    main()
