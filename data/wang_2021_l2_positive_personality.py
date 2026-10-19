#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MWIV98
# DOI: 10.7910/DVN/MWIV98
#   Wang, S. (2021). Positive Personalities and L2 Achievement: The Mediating
#   Role of Positive Emotions [Dataset]. Harvard Dataverse.
# Data: "70058475_2_raw.xlsx" -- 368 Chinese university EFL learners. The raw
#   web-questionnaire export, whose COLUMN HEADERS ARE THE ITEM STEMS, each
#   prefixed by its questionnaire number ("19、既然我决定学习英语，...").
#   Those numbers are the item codes used here, so the naming is the
#   source's.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped, extraction solved. Every stem is a column header in
#   the administered Chinese. The deposit states the tolerance-of-ambiguity
#   scale was built from Herman et al. (2010) by translation and
#   back-translation, so that block's text carries a rights question the
#   others do not; the enjoyment, grit and self-rating blocks are either the
#   study's own or standard L2 instruments. None was checked against the
#   register here -- this slice is response tables.
#
# THE RAW FILE IS WHAT SHIPS, not the author's two .sav working files. The
#   deposit also carries data_TA_original.sav (368 rows, which silently omits
#   Q19-Q27) and data_368_TA_final.sav (318 rows, with the blocks already
#   renamed Joy1-9 and TA1-TA12 and no longer equal to any raw column, so
#   they have been recoded). A screened, recoded subset is not the
#   administration; the raw export is.
#
# SIX tables, 368 respondents (339 for the emotion block, see below):
#   wang_2021_positive_emotions      6 items, 1-7  (Q9a-Q9f)
#   wang_2021_enjoyment              9 items, 1-9  (Q10-Q18)
#   wang_2021_grit_perseverance      5 items, 1-9  (Q19-Q23)
#   wang_2021_grit_interest          4 items, 1-9  (Q24-Q27)
#   wang_2021_tolerance_ambiguity   12 items, 1-9  (Q28-Q30, Q32-Q40)
#   wang_2021_self_rated_english     4 items, 1-6  (Q41 listen/speak/read/write)
#
# -3 IS A NON-RESPONSE CODE, not a scale point. It appears only in the six
#   emotion columns, in exactly 29 rows, and in those rows it is the answer to
#   ALL SIX -- a respondent who skipped the block. A bipolar -3..3 scale would
#   show -2, -1 and 0 somewhere; none appears, and every other value is 1-7.
#   Dropped, which is why that table has 339 respondents and the others 368.
#
# Q31 IS NOT SHIPPED, and the count is the reason. "我不喜欢上英语课" ("I do
#   not like English class") sits between the ambiguity items but is about
#   liking a class, not about tolerating the unfamiliar. Excluding it leaves
#   twelve items in that block, which is exactly what the deposit's own
#   description says the TA scale has ("including 12 items on a nine-point"
#   scale) and what the author's own final file numbers TA1-TA12. Content and
#   count agree, so it is left out of the ambiguity table rather than guessed
#   into it; it is not added to the enjoyment table either, whose nine items
#   (Q10-Q18) the author's Joy1-Joy9 already matches one-for-one.
#
# id: the row index. The export carries no respondent id.
# Covariates: cov_gender, cov_age, cov_abroad_experience,
#   cov_eng_course_frequency, cov_eng_tutoring_frequency,
#   cov_academic_standing, cov_extracurricular_standing,
#   cov_eng_study_frequency -- Q1-Q8, as the deposit's own codes. cov_age is
#   in years (18-32); the rest are unlabelled ordinal codes.
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "mwiv98" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 4868602, "70058475_2_raw.xlsx"
MISSING = -3
COV_Q = {1: "cov_gender", 2: "cov_age", 3: "cov_abroad_experience",
         4: "cov_eng_course_frequency", 5: "cov_eng_tutoring_frequency",
         6: "cov_academic_standing", 7: "cov_extracurricular_standing",
         8: "cov_eng_study_frequency"}
SKILLS = {"听": "Q41_listening", "说": "Q41_speaking",
          "读": "Q41_reading", "写": "Q41_writing"}
TABLES = {
    "wang_2021_positive_emotions": (None, set(range(1, 8))),   # Q9a-f
    "wang_2021_enjoyment": (range(10, 19), set(range(1, 10))),
    "wang_2021_grit_perseverance": (range(19, 24), set(range(1, 10))),
    "wang_2021_grit_interest": (range(24, 28), set(range(1, 10))),
    "wang_2021_tolerance_ambiguity": ([*range(28, 31), *range(32, 41)],
                                      set(range(1, 10))),
    "wang_2021_self_rated_english": (None, set(range(1, 7))),  # Q41*
}
NOT_SHIPPED_Q = 31


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
    df = pd.read_excel(fetch())
    assert df.shape == (368, 49), df.shape

    # The questionnaire number that prefixes every header is the item code.
    by_q, emotions, skills = {}, [], []
    for col in df.columns:
        m = re.match(r"^(\d+)、", str(col))
        assert m, f"header without a questionnaire number: {col!r}"
        q = int(m.group(1))
        if q == 9:
            code = f"Q9{chr(ord('a') + len(emotions))}"
            emotions.append(code)
            by_q[code] = col
        elif q == 41:
            zh = re.search(r"[（(](.)[）)]", str(col)).group(1)
            code = SKILLS[zh]
            skills.append(code)
            by_q[code] = col
        else:
            assert f"Q{q}" not in by_q, q
            by_q[f"Q{q}"] = col
    assert emotions == [f"Q9{c}" for c in "abcdef"], emotions
    assert skills == list(SKILLS.values()), skills
    assert {f"Q{q}" for q in range(1, 41) if q != 9} <= set(by_q)

    renames = {col: code for code, col in by_q.items()}
    df = df.rename(columns=renames)
    cov_map = {f"Q{q}": name for q, name in COV_Q.items()}
    df = df.rename(columns=cov_map)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COV_Q.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all() and (v > 0).all(), cov
        df[cov] = v.astype("Int64")

    # -3 occurs only in the emotion block, and only as a whole-block skip.
    elsewhere = [c for c in by_q
                 if c not in emotions and c not in cov_map]
    assert not (df[elsewhere] == MISSING).any().any(), \
        f"{MISSING} outside the emotion block"
    skipped = (df[emotions] == MISSING)
    assert (skipped.any(axis=1) == skipped.all(axis=1)).all(), \
        "a partial -3 row: it is not a whole-block skip after all"
    print(f"{MISSING} dropped as non-response: {int(skipped.all(axis=1).sum())} "
          f"respondents skipped the six emotion items")
    print(f"not shipped: Q{NOT_SHIPPED_Q} (see the header note)")

    plan = {}
    for name, (qs, scale) in TABLES.items():
        if name.endswith("positive_emotions"):
            cols = emotions
        elif name.endswith("self_rated_english"):
            cols = skills
        else:
            cols = [f"Q{q}" for q in qs]
            assert NOT_SHIPPED_Q not in list(qs) or name == "", name
        plan[name] = (cols, scale)
    shipped = {c for cols, _ in plan.values() for c in cols}
    assert f"Q{NOT_SHIPPED_Q}" not in shipped
    assert len(shipped) == 40, len(shipped)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols, scale) in plan.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        t = t[t["resp"] != MISSING]
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the administered scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() == len(cols)
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
