"""
A three-level Turkish maths-anxiety study: 413 students nested in 12 teachers,
with a matched parent questionnaire.

Source: Demirdelen, Z., Özer Özkan, Y., & Acar Güvendir, M. (2023).
        Predicting Mathematics Anxiety and Achievement: Unveiling the
        Significance of Student and Teacher Attributes through Hierarchical
        Linear Modeling [Dataset]. Zenodo.
DOI: 10.5281/zenodo.8072287
Data: https://zenodo.org/records/8072287 ("ANKET VERİLERİ.xlsx", five sheets)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: NOT shipped and NOT in the deposit. The item columns are bare
        `m1..m20` and `M1..M16`, the workbook has no label level, and there is
        no codebook sheet for the items -- only the covariate legend described
        below. The two instruments are a student maths-anxiety scale and a
        parent questionnaire, neither named by the deposit, so no published
        instrument is identified and there is nothing to check a rights
        register against. Where to look: the article this deposit supports,
        which the Zenodo record does not link.

**`cluster_id` is the teacher, and that is the point of the dataset.** The
deposit is explicitly a hierarchical-linear-modelling study: every sheet
carries `Öğretmen ID`, the 413 students fall into 12 teachers with 11 to 87
students each, and the script asserts that the teacher id agrees row-for-row
across all three level-1 sheets. Shipping `cluster_id` is what lets anyone
reproduce the nesting without re-reading the workbook.

**The student and parent tables are row-matched, and share `id` accordingly.**
Sheet 1's row labels run `öğrenci-1..öğrenci-413` and sheet 3's
`ebeveyn-1..ebeveyn-413`, in the same order and with the same teacher on every
row -- parent N is student N's parent. The respondent differs between the two
tables (a child in one, their parent in the other), but the row index is the
family, so the same `id` in both tables is the link and is deliberate.

**The teacher questionnaire is NOT shipped: 12 respondents.** Sheet 4 holds a
29-item teacher instrument answered by all 12 teachers, which is a genuine
battery and well below the flat N>=100 floor, so it is skipped outright. Its
level-2 DEMOGRAPHICS do ship, as `cov_teacher_*` on both student tables, which
is where they are usable.

**The covariate codings come from an inline legend in the workbook.** Columns
`Unnamed: 12`..`Unnamed: 16` of the variables sheet, and `Unnamed: 6`..`9` of
the teacher sheet, are not data -- they are a hand-written key sitting beside
it: `kadın:1`/`Erkek:2` (female/male), `ilkokul:1`/`Ort. Okul:2`/`lise:3`/
`üni:4` (primary/middle/high/university), `Yetersiz:1`/`Yeterli:2`
(insufficient/sufficient), `hayır:1`/`Evet:2` (no/yes), and for teachers
`18-30:1`/`31-40:2`/`41+:3`, `Evli:1`/`Bekar:2` (married/single),
`0-5 yıl:1`/`6-10 yıl:2`/`11+:3` (years of service),
`Lisans:1`/`Y. Lisans:2`/`Doktora:3` (bachelor/master/doctorate). They are
recorded here because the legend names only two of the variables it codes
(`cinsiyet`, `Eğitim Düz`), so which of the yes/no and sufficient/insufficient
pairs belongs to `Okul Memn.`, `Sınıf Memn.`, `oda`, `Mat. Yetk` and `Hobi` is
NOT stated by the deposit and is not guessed at here. The codes ship as the
deposit has them.

PII: none. The only text columns are the `öğrenci-N`/`ebeveyn-N` row labels,
which the script checks are exactly that shape before replacing them with the
row index. No names, no dates, no geography.

Output: two tables, 14,868 responses.
  * demirdelen_2023_math_anxiety          -- 20 items, resp 1-5, 413 students
  * demirdelen_2023_parent_questionnaire  -- 16 items, resp 1-5, 413 parents
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ANKET VERILERI.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5]
TEACHER = "Öğretmen ID"
LABEL = "Unnamed: 0"

STUDENT_SHEET = "Düzey-1-ÖĞRENCİ Kaygı D."
PARENT_SHEET = "Düzey-1-EBEVEYN K."
VARS_SHEET = "Düzey-1-Değişkenler"
TEACHER_SHEET = "Düzey-2-ÖĞRETMEN"
TEACHER_VARS_SHEET = "Düzey-2- Değişkenler"

BLOCKS = {
    "demirdelen_2023_math_anxiety": (STUDENT_SHEET,
                                     [f"m{i}" for i in range(1, 21)],
                                     "öğrenci"),
    "demirdelen_2023_parent_questionnaire": (PARENT_SHEET,
                                             [f"M{i}" for i in range(1, 17)],
                                             "ebeveyn"),
}

COV_MAP = {
    "BAŞARI NOTU": "cov_achievement_grade",
    "Öğrenci cinsiyet": "cov_student_gender",
    "Veli Cinsiyet": "cov_parent_gender",
    "Veli Eğitim d.": "cov_parent_education",
    "Okul Memn.": "cov_school_satisfaction",
    "Sınıf Memn.": "cov_class_satisfaction",
    "oda": "cov_own_room",
    "Mat. Yetk": "cov_math_self_efficacy",
    "Hobi": "cov_hobby",
}
TEACHER_COV_MAP = {
    "Cinsiyet": "cov_teacher_gender",
    "Yaş": "cov_teacher_age_band",
    "Medeni Durum": "cov_teacher_marital_status",
    "Mesleki Kıdem": "cov_teacher_years_service",
    "Eğitim Düzeyi": "cov_teacher_education",
}


def row_number(col: pd.Series, prefix: str) -> pd.Series:
    s = col.astype(str)
    assert s.str.fullmatch(rf"{prefix}-\d+").all(), \
        sorted(set(s[~s.str.fullmatch(rf'{prefix}-\d+')]))[:5]
    return s.str.extract(r"-(\d+)$")[0].astype(int)


def main() -> None:
    x = pd.ExcelFile(SRC)
    st = pd.read_excel(x, sheet_name=STUDENT_SHEET)
    pa = pd.read_excel(x, sheet_name=PARENT_SHEET)
    va = pd.read_excel(x, sheet_name=VARS_SHEET)
    te = pd.read_excel(x, sheet_name=TEACHER_SHEET)
    tv = pd.read_excel(x, sheet_name=TEACHER_VARS_SHEET)
    print(f"sheets: student {st.shape}, parent {pa.shape}, "
          f"level-1 vars {va.shape}, teacher {te.shape}, "
          f"level-2 vars {tv.shape}")

    # The row-matching and nesting claims, asserted before anything is written.
    sn = row_number(st[LABEL], "öğrenci")
    pn = row_number(pa[LABEL], "ebeveyn")
    vn = row_number(va[LABEL], "öğrenci")
    assert list(sn) == list(range(1, 414)), "student numbering is not 1..413"
    assert (sn == pn).all() and (sn == vn).all(), \
        "the three level-1 sheets are not in the same row order"
    assert (st[TEACHER] == pa[TEACHER]).all() and (st[TEACHER] == va[TEACHER]).all(), \
        "the teacher id disagrees between level-1 sheets"
    counts = st[TEACHER].value_counts().sort_index()
    print(f"nesting: {len(counts)} teachers, {counts.min()}-{counts.max()} "
          f"students each -> ships as cluster_id")

    # Level-2 demographics, joined on the teacher id.
    tv = tv.dropna(subset=[TEACHER])
    assert len(tv) == 12, len(tv)
    assert set(tv[TEACHER]) == set(st[TEACHER]), "teacher id sets differ"
    tcov = tv.set_index(TEACHER)[list(TEACHER_COV_MAP)].rename(
        columns=TEACHER_COV_MAP)

    print(f"skipped sheet {TEACHER_SHEET!r}: a 29-item teacher instrument "
          f"answered by {len(te)} teachers -- a real battery, but far below the "
          "flat N>=100 floor. Its level-2 demographics ship as cov_teacher_*.")
    legend = [c for c in list(va.columns) + list(tv.columns)
              if str(c).startswith("Unnamed:") and c != LABEL]
    print(f"skipped {len(legend)} inline-legend column(s) across the two "
          "variable sheets: a hand-written code key beside the data, not data "
          "-- transcribed into this script's header instead")

    covs = list(COV_MAP.values()) + list(TEACHER_COV_MAP.values())
    for table, (sheet, cols, prefix) in BLOCKS.items():
        d = pd.read_excel(x, sheet_name=sheet)
        assert all(c in d.columns for c in cols), (table, cols)
        leftover = [c for c in d.columns
                    if c not in set(cols) | {LABEL, TEACHER}]
        assert not leftover, (table, leftover)
        frame = pd.DataFrame({"id": row_number(d[LABEL], prefix),
                              "cluster_id": d[TEACHER].astype(int)})
        for src, dst in COV_MAP.items():
            frame[dst] = va[src].values
        for dst in TEACHER_COV_MAP.values():
            frame[dst] = frame["cluster_id"].map(tcov[dst])
            assert frame[dst].notna().all(), dst
        long = pd.concat([frame, d[cols].rename(
            columns={c: c.lower() for c in cols})], axis=1)
        long = long.melt(id_vars=["id", "cluster_id"] + covs,
                         var_name="item", value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(PERMITTED)]
        assert before == len(long), \
            f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cluster_id"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} clusters={long['cluster_id'].nunique()} "
          f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
