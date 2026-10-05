"""lsbq_maleki_2025: Persian Language and Social Background Questionnaire (LSBQ).

Source: RAW Data.LSBQ.sav, github.com/maleki1404/Bilingualism_LSBQ (Maleki et
al., 2025, Behav Res 57, 346, doi 10.3758/s13428-025-02831-y).

    python3 lsbq_maleki_2025.py ["raw_data/RAW Data.LSBQ.sav"] [raw_data]

Five tables, one per LSBQ section:

  persian_comprehension     16.1.S/U/R/W  Persian proficiency sliders, 0-10
  non_persian_proficiency   17.1.S/U/R/W  other-language proficiency sliders, 0-10
  dominant_language_home_community  19.1-19.7, 20.1-20.8
  non_persian_use           17.2.S/U/R/W, 21.1-21.9
  persian_switching         22.1-22.3

Rebuilt 2026-10-05 (irw#2839). The file is now read with pyreadstat and the
numeric codes are used directly. The old build read value labels and mapped
them back to numbers, and two things went wrong there:
  * its map keyed the top category as '1all persin' while the .sav's label is
    'all persin', so every "all Persian" answer became NA and was dropped
    (31% of dominant_language_home_community, 38% of 21.x);
  * the 17.2.* labels (NONE/little/some/most/all) had no entry at all, so the
    four 17.2 items never reached non_persian_use.
It also asked for '.L' (listening) codes where the .sav uses '.U'
(understanding), so 16.1.U and 17.1.U were missing too.

Codes: every 0-4 categorical item is shipped as code + 1, i.e. 1-5, which is
what the old label map produced for the categories it did match:
  19-21: 1 = all Persian ... 5 = only the other language
  17.2:  1 = none ... 5 = all (of the time in the other language)
  22:    1 = never ... 5 = always
Codes outside 0-4 (19.7 has one 5, 20.1 one 44) are typing errors and are
dropped, as before. Slider values outside 0-10 (one 75 on 16.1.S and 16.1.U,
one 107.5 on 17.1.U) are dropped, not recoded (#1700).

The `.retest` and `*100` columns (a retest subsample; sliders x100) are not used.
"""
import os
import sys

import pandas as pd
import pyreadstat

SAV = sys.argv[1] if len(sys.argv) > 1 else "raw_data/RAW Data.LSBQ.sav"
OUT = sys.argv[2] if len(sys.argv) > 2 else "raw_data"
PREFIX = "lsbq_maleki_2025_"

##covariate -> source column; labelled ones ship as their value label
COVS = {
    "cov_mono_or_bi_or_multi_selfreport": "mono.or.bi.or.multi.SELFREPORT",
    "cov_tabriz_tehran": "tabriz.tehran",
    "cov_gender": "gender",
    "cov_age": "age",
    "cov_age_group": "age.group",
    "cov_occupation_stu": "occupation.stu",
    "cov_handedness": "handedness",
    "cov_infancy": "question18.1",
    "cov_preschool_age": "question18.2",
    "cov_primary_school_age": "question18.3",
    "cov_high_school_age": "question18.4",
}

SLIDER = (0, 10)
CATEGORICAL = (0, 4)
TABLES = {
    "persian_comprehension": (["16.1.S", "16.1.U", "16.1.R", "16.1.W"], SLIDER),
    "non_persian_proficiency": (["17.1.S", "17.1.U", "17.1.R", "17.1.W"], SLIDER),
    "dominant_language_home_community": (
        [f"19.{i}" for i in range(1, 8)] + [f"20.{i}" for i in range(1, 9)], CATEGORICAL),
    "non_persian_use": (
        ["17.2.S", "17.2.U", "17.2.R", "17.2.W"] + [f"21.{i}" for i in range(1, 10)], CATEGORICAL),
    "persian_switching": ([f"22.{i}" for i in range(1, 4)], CATEGORICAL),
}


def label_column(s, labels):
    ##value label where there is one (the source's 'persin' typo corrected),
    ##else the bare code; NA stays NA
    labels = {k: v.replace("persin", "persian") for k, v in (labels or {}).items()}
    def one(x):
        if pd.isna(x):
            return pd.NA
        if x in labels:
            return labels[x]
        return str(int(x)) if float(x).is_integer() else str(x)
    return s.map(one)


def main():
    df, meta = pyreadstat.read_sav(SAV)
    assert df["record.number"].is_unique
    os.makedirs(OUT, exist_ok=True)

    covs = pd.DataFrame({"id": df["record.number"].astype(int)})
    for new, src in COVS.items():
        if src == "age":
            covs[new] = df[src].astype("Int64")
        else:
            covs[new] = label_column(df[src], meta.variable_value_labels.get(src))

    for table, (items, (lo, hi)) in TABLES.items():
        cols = {f"question{it}": it for it in items}
        missing = [c for c in cols if c not in df.columns]
        assert not missing, (table, missing)
        wide = pd.concat([covs, df[list(cols)].rename(columns=cols)], axis=1)
        long = wide.melt(id_vars=list(covs.columns), value_vars=items,
                         var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].copy()
        if (lo, hi) == CATEGORICAL:
            assert (long["resp"] % 1 == 0).all(), table
            long["resp"] = (long["resp"] + 1).astype(int)
        long = long[["id", "item", "resp"] + list(COVS)]
        long = long.sort_values(["id", "item"], kind="stable")
        assert not long.duplicated(["id", "item"]).any(), table
        path = os.path.join(OUT, f"{PREFIX}{table}.csv")
        long.to_csv(path, index=False)
        print(f"{PREFIX}{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    main()
