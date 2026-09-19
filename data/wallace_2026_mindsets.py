"""Wallace et al. (2026) mindsets converter.

Recode: Study S2c stored its certainty items (certain1-3) reverse-anchored
(1 = very certain, 7 = very uncertain), the opposite of the other studies
(1 = not at all, 7 = very much). Those rows are rewritten as 8 - resp so that
higher always means more certain, and are flagged with itemcov_recoded = 1 in
wallace_2026_certain.

Treatment: the source column Mindset is the randomly assigned condition, coded
+1 / -1 with no value labels. -1 is the fixed-mindset condition and +1 is the
growth-mindset condition (confirmed in all seven studies: the fixed-belief
manipulation-check items are agreed with more strongly at -1). It is written as
treat = 1 for growth (+1) and treat = 0 for fixed (-1).
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import pyreadstat

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "dqw9f-osfstorage-archive"
OUT = BASE / "wallace_2026_mindsets"

STUDY_FILES = {
    "s2":  "Studies In Main Text/Study 2 Data and Code/Study 2 Data no ID.sav",
    "s1a": "Supplemental Studies/Study S1a Data and Code/Study S1a Data.sav",
    "s1b": "Supplemental Studies/Study S1b Data and Code/Study S1b Data.sav",
    "s1c": "Supplemental Studies/Study S1c Data and Code/Study S1c Data.sav",
    "s2a": "Supplemental Studies/Study S2a Data and Code/Study S2a Data.sav",
    "s2b": "Supplemental Studies/Study S2b Data and Code/Study S2b Data.sav",
    "s2c": "Supplemental Studies/Study S2c Data and Code/Study S2c Data.sav",
}

STUDY_NUM = {"s2": 1, "s1a": 2, "s1b": 3, "s1c": 4, "s2a": 5, "s2b": 6, "s2c": 7}
STUDY_LABEL = {"s2": "S2", "s1a": "S1a", "s1b": "S1b", "s1c": "S1c",
               "s2a": "S2a", "s2b": "S2b", "s2c": "S2c"}

COV_MAP = {
    "age": "cov_age",
    "gender": "cov_gender",
    "educationlevel": "cov_education_level",
    "firstlang": "cov_first_language",
    "politicalorientation": "cov_political_orientation",
    "similarstudy": "cov_similar_study",
}


def _dweck3(study):
    return [("IQbelief1T1", "IQbelief1", 1, 0),
            ("IQbelief2T1", "IQbelief2", 1, 0),
            ("IQbelief3T1", "IQbelief3", 1, 0)]

def _dweck1(study):
    return [("IQbelief1T1", "IQbelief1", 1, 0),
            ("IQbelief1T2", "IQbelief2", 1, 0),
            ("IQbelief1T3", "IQbelief1", 2, 0),
            ("IQbelief2T3", "IQbelief2", 2, 0)]

def _cert3(study, flip=False):
    p = "-" if flip else ""
    return [(f"{p}certain1", "certain1", None, 0),
            (f"{p}certain2", "certain2", None, 0),
            (f"{p}certain3", "certain3", None, 0)]

def _cert1(study, first="certain1"):
    return [(first, "certain_item1", None, 0),
            ("certain2", "certain_item2", None, 0)]

_MCM_FM = [("fixed1_MCM", "fixed1_MCM", None, 0), ("fixed2_MCM", "fixed2_MCM", None, 0),
           ("malleable1_MCM", "malleable1_MCM", None, 1), ("malleable2_MCM", "malleable2_MCM", None, 1)]
_MCM_MANIP = [("MCMmanip1", "MCMmanip1", None, 0), ("MCMmanip2R", "MCMmanip2R", None, 1),
              ("MCMmanip3", "MCMmanip3", None, 0), ("MCMmanip4R", "MCMmanip4R", None, 1)]
_MCM_IQB = [("IQB1", "IQB1", None, 0), ("IQB2R", "IQB2R", None, 1),
            ("IQB3", "IQB3", None, 0), ("IQB4", "IQB4", None, 0)]

_CULTURE = ["practices_MCM", "values1_MCM", "bemyself_MCM",
            "effort1_MCM", "colleagues_MCM", "effort2_MCM", "supervisor_MCM",
            "management_MCM", "values2_MCM", "environment_MCM"]

SCALES = {
    "iqbelief.csv": {
        "s2": _dweck3("s2"), "s1c": _dweck3("s1c"), "s2c": _dweck3("s2c"),
        "s1a": _dweck1("s1a"), "s1b": _dweck1("s1b"),
        "s2a": _dweck1("s2a"), "s2b": _dweck1("s2b"),
    },
    "certain.csv": {
        "s2": _cert3("s2"), "s1c": _cert3("s1c"), "s2c": _cert3("s2c", flip=True),
        "s1a": _cert1("s1a"), "s1b": _cert1("s1b"),
        "s2a": _cert1("s2a"), "s2b": _cert1("s2b", first="cert1"),
    },
    "mcm_check.csv": {
        "s1a": _MCM_FM, "s1b": _MCM_FM, "s2a": _MCM_FM, "s2b": _MCM_FM,
        "s1c": _MCM_MANIP, "s2c": _MCM_MANIP, "s2": _MCM_IQB,
    },
    "mcm_culture.csv": {
        "s1a": [(c, c, None, 0) for c in _CULTURE],
        "s1b": [(c, c, None, 0) for c in _CULTURE],
    },
    "climate.csv": {
        "s2a": [("effective1", "effective", None, 0), ("efficient", "efficient", None, 0),
                ("goodplace", "goodplace", None, 0)],
        "s2b": [("effective1", "effective", None, 0), ("efficient", "efficient", None, 0),
                ("goodplace", "goodplace", None, 0)],
        "s2c": [("effective", "effective", None, 0), ("efficient", "efficient", None, 0),
                ("organized", "organized", None, 0), ("good_place", "goodplace", None, 0)],
    },
    "belong.csv": {
        s: [("belong1", "belong1", None, 0), ("belong2", "belong2", None, 0),
            ("belong3", "belong3", None, 0),
            ("belong4R" if s != "s2" else "belong4", "belong4R", None, 1),
            ("belong5", "belong5", None, 0)]
        for s in ("s1c", "s2", "s2c")
    },
    "fit.csv": {s: [(f"fit{i}", f"fit{i}", None, 0) for i in (1, 2, 3)]
               for s in ("s1c", "s2", "s2c")},
    "cengage.csv": {
        "s1c": [(f"Cengage{i}", f"cengage{i}", None, 0) for i in (1, 2, 3)],
        "s2c": [(f"Cengage{i}", f"cengage{i}", None, 0) for i in (1, 2, 3)],
        "s2":  [(f"Cengage{i}", f"cengage{i}", None, 0) for i in (1, 2, 3, 4)],
    },
    "concern.csv": {s: [(f"concern{i}", f"concern{i}", None, 0) for i in range(1, 6)]
                    for s in ("s1c", "s2c")},
    "interest.csv": {s: [(f"interest{i}", f"interest{i}", None, 0) for i in (1, 2, 3)]
                     for s in ("s1c", "s2")},
    "interest_org.csv": {
        "s1a": [("interestwork_MCM", "interest_org", None, 0)],
        "s1b": [("interestwork_MCM", "interest_org", None, 0)],
        "s2a": [("interestwork_MCM", "interest_org", None, 0)],
        "s2b": [("interestwork_MCM", "interest_org", None, 0)],
        "s2c": [("interest", "interest_org", None, 0)],
    },
    "learn.csv": {s: [(f"learn{i}", f"learn{i}", None, 0) for i in (1, 2, 3)]
                  for s in ("s1c", "s2c")},
    "apply.csv": {s: [(f"apply{i}", f"apply{i}", None, 0) for i in (1, 2)]
                  for s in ("s1c", "s2c")},
    "rec.csv": {s: [(f"rec{i}", f"rec{i}", None, 0) for i in (1, 2)]
                for s in ("s1c", "s2c")},
    "reflection.csv": {
        s: [(f"{m}{k}", f"{m}_item{k}", None, 0)
            for k in (1, 2) for m in ("elaborate", "know", "values", "important")]
        for s in ("s1a", "s2b")
    },
}

MCM_VERSION = {
    "fixed1_MCM": "fixed_malleable", "fixed2_MCM": "fixed_malleable",
    "malleable1_MCM": "fixed_malleable", "malleable2_MCM": "fixed_malleable",
    "MCMmanip1": "mcmmanip4", "MCMmanip2R": "mcmmanip4",
    "MCMmanip3": "mcmmanip4", "MCMmanip4R": "mcmmanip4",
    "IQB1": "iqb4", "IQB2R": "iqb4", "IQB3": "iqb4", "IQB4": "iqb4",
}

SINGLE = {
    "s2_profcert.csv":  ("s2",  [(f"profcert{i}", f"profcert{i}", 0) for i in (1, 2, 3)], None),
    "s2_like.csv":      ("s2",  [(f"like{i}", f"like{i}", 0) for i in (1, 2)], None),
    "s2_engage.csv":    ("s2",  [(f"engage{i}", f"engage{i}", 0) for i in (1, 2)], None),
    "s2_perf.csv":      ("s2",  [(f"perf{i}", f"perf{i}", 0) for i in (1, 2, 3)], None),
    "s2_warmcomp.csv":  ("s2",  [("warm1", "warm1", 0), ("warm2", "warm2", 0), ("warm3R", "warm3R", 1),
                                 ("comp1", "comp1", 0), ("comp2", "comp2", 0)],
                         {"warm1": "warmth", "warm2": "warmth", "warm3R": "warmth",
                          "comp1": "competence", "comp2": "competence"}),
    "s2_verbalmath.csv": ("s2", [("verbal1", "verbal1", 0), ("verbal2", "verbal2", 0),
                                 ("math1", "math1", 0), ("math2", "math2", 0)],
                          {"verbal1": "verbal", "verbal2": "verbal",
                           "math1": "math", "math2": "math"}),
    "s2c_metacog.csv":  ("s2c", [(f"MetaCog{i}", f"metacog{i}", 0) for i in (1, 2)], None),
    "s2c_desirecert.csv": ("s2c", [("desireforcert1", "desireforcert1", 0),
                                   ("desireforcert", "desireforcert2", 0)], None),
    "s2c_selfcert.csv": ("s2c", [(f"selfcert{i}", f"selfcert{i}", 0) for i in (1, 2)], None),
    "s2c_mc.csv":       ("s2c", [(f"MC{i}", f"mc{i}", 0) for i in (1, 2, 3, 4)], None),
    "s2c_uncertmind.csv": ("s2c", [(f"uncertmind{i}", f"uncertmind{i}", 0) for i in (1, 2, 3)], None),
    "s2c_intoluncert.csv": ("s2c", [(f"intoluncert{i}", f"intoluncert{i}", 0) for i in range(1, 6)], None),
    "s2c_covidcert.csv": ("s2c", [(f"COVIDcert{i}", f"covidcert{i}", 0) for i in range(1, 7)], None),
    "s2c_pfi.csv":      ("s2c", [(c, c, 0) for c in
                                 ["pfi_1_a", "pfi_2_a", "pfi_3_a", "pfi_4_a",
                                  "pfi_av_5_nr_a", "pfi_av_6_nr_a", "pfi_av_7_nr_a", "pfi_av_8_nr_a",
                                  "pfi_av_9_nr_a", "pfi_ac_10_a", "pfi_ac_11_a", "pfi_ac_12_a",
                                  "pfi_ac_13_a", "pfi_ac_14_a", "pfi_h_15_a", "pfi_h_16_a",
                                  "pfi_h_17_a", "pfi_h_18_a", "pfi_h_19_a"]], None),
}

COL_ORDER = ["id", "item", "resp", "wave", "treat", "rt", "date"]


def _load(study: str) -> pd.DataFrame:
    df, _ = pyreadstat.read_sav(str(ARCHIVE / STUDY_FILES[study]), apply_value_formats=False)
    df = df.reset_index(drop=True)
    df.insert(0, "id", STUDY_NUM[study] * 100_000 + df.index + 1)
    return df


def _covariates(study: str, df: pd.DataFrame) -> pd.DataFrame:
    out = df[["id"]].copy()
    for src, dst in COV_MAP.items():
        if src in df.columns and df[src].notna().any() and df[src].dropna().nunique() > 1:
            out[dst] = df[src]
    out["treat"] = (df["Mindset"] == 1).astype(int)
    out["cov_study"] = STUDY_NUM[study]
    return out


def _order(df: pd.DataFrame) -> pd.DataFrame:
    lead = [c for c in COL_ORDER if c in df.columns]
    itemcov = sorted(c for c in df.columns if c.startswith("itemcov_"))
    cov = sorted(c for c in df.columns if c.startswith("cov_"))
    rest = [c for c in df.columns if c not in lead + itemcov + cov]
    return df[lead + rest + itemcov + cov]


def _write(df: pd.DataFrame, out_name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out_name = f"wallace_2026_{out_name}"
    if "cov_study" in df.columns and df["cov_study"].nunique() == 1:
        df = df.drop(columns=["cov_study"])
    df = _order(df).sort_values([c for c in ("id", "wave", "item") if c in df.columns],
                                kind="stable").reset_index(drop=True)
    assert df["id"].notna().all() and df["item"].notna().all()
    assert pd.api.types.is_numeric_dtype(df["resp"]) and df["resp"].notna().all()
    df.to_csv(OUT / out_name, index=False)
    rng = f"[{df['resp'].min():g},{df['resp'].max():g}]"
    print(f"{out_name:26s} rows={len(df):>6,} ids={df['id'].nunique():>5} "
          f"items={df['item'].nunique():>2} resp={rng}")


def _collect(spec_by_study, dfs, cov_by_study, reverse_map=None, version_map=None):
    parts = []
    for study, entries in spec_by_study.items():
        df = dfs[study]
        for src, item, wave, rev in entries:
            flip = src.startswith("-")
            col = src[1:] if flip else src
            if col not in df.columns:
                continue
            s = pd.to_numeric(df[col], errors="coerce")
            sub = pd.DataFrame({"id": df["id"], "resp": (8 - s) if flip else s})
            sub = sub.dropna(subset=["resp"])
            sub["item"] = item
            if wave is not None:
                sub["wave"] = wave
            if reverse_map is not None:
                sub["itemcov_reverse_keyed"] = rev
            if version_map is not None:
                sub["itemcov_scale_version"] = version_map.get(item)
            sub = sub.merge(cov_by_study[study], on="id", how="left")
            parts.append(sub)
    return pd.concat(parts, ignore_index=True) if parts else None


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dfs = {s: _load(s) for s in STUDY_FILES}
    cov = {s: _covariates(s, dfs[s]) for s in STUDY_FILES}

    for out_name, spec in SCALES.items():
        need_rev = out_name in ("mcm_check.csv", "belong.csv")
        version = MCM_VERSION if out_name == "mcm_check.csv" else None
        long = _collect(spec, dfs, cov,
                        reverse_map=(True if need_rev else None),
                        version_map=version)
        if long is not None and out_name == "certain.csv":
            long["itemcov_recoded"] = (long["cov_study"] == STUDY_NUM["s2c"]).astype(int)
            long["itemcov_design"] = long["item"].map(
                lambda i: "per_response" if i.startswith("certain_item") else "three_item_scale")
        if long is not None:
            _write(long, out_name)

    for out_name, (study, entries, extra) in SINGLE.items():
        df = dfs[study]
        spec = {study: [(src, item, None, rev) for src, item, rev in entries]}
        has_rev = any(rev for _, _, rev in entries)
        long = _collect(spec, dfs, cov, reverse_map=(True if has_rev else None))
        if long is None:
            continue
        if extra:
            key = "itemcov_domain" if "verbalmath" in out_name else "itemcov_dimension"
            long[key] = long["item"].map(extra)
        _write(long, out_name)


if __name__ == "__main__":
    build()
