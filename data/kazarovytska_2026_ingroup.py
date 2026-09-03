from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "kazarovytska_2026_ingroup"
SRC = (BASE / "osfstorage-archive (1)" / "01_Data and Analysis Codes" /
       "01.1_Confirmatory Analyses")
DATA = SRC / "data"
PREP_R = SRC / "analysis code" / "script I_data_preparation.R"


SCALE_ITEMS = [
    "national_identification_1", "national_identification_2", "national_identification_3",
    "collective_narcissism_1", "collective_narcissism_2", "collective_narcissism_3", "collective_narcissism_4",
    "continuity_1", "continuity_2", "continuity_3",
    "pivo_1", "pivo_2", "pivo_3",
]

EVENT_RESP_MEASURES = {
    "social_relevance_remembrance_1":   "srr_1",
    "social_relevance_remembrance_2":   "srr_2",
    "social_relevance_remembrance_3":   "srr_3",
    "social_relevance_remembrance_4":   "srr_4",
    "social_relevance_remembrance_5":   "srr_5",
    "social_relevance_remembrance_6":   "srr_6",
    "social_relevance_remembrance_7":   "srr_7",
    "personal_relevance_remembrance_1": "prr_1",
    "personal_relevance_remembrance_2": "prr_2",
    "threat_symbolic_1":  "threat_sym_1",
    "threat_symbolic_2":  "threat_sym_2",
    "threat_realistic_1": "threat_real_1",
    "threat_realistic_2": "threat_real_2",
    "valence_event_positive":    "valence_event_pos",
    "valence_event_negative":    "valence_event_neg",
    "valence_outcomes_positive": "valence_outcome_pos",
    "valence_outcomes_negative": "valence_outcome_neg",
    "ingroup_morality":       "morality",
    "ingroup_agency":         "agency",
    "ingroup_responsibility": "responsibility",
    "presence_politics": "presence_politics",
    "presence_media":    "presence_media",
}

EVENT_COV_MEASURES = ["domestic", "ingroup_role", "subjective_temporal_distance",
                     "knowledge", "relevance_world_history"]

CONSTRUCT_GROUPS = {
    "srr":         ["srr_1","srr_2","srr_3","srr_4","srr_5","srr_6","srr_7"],
    "prr":         ["prr_1","prr_2"],
    "threat":      ["threat_sym_1","threat_sym_2","threat_real_1","threat_real_2"],
    "valence":     ["valence_event_pos","valence_event_neg","valence_outcome_pos","valence_outcome_neg"],
    "attribution": ["morality","agency","responsibility"],
    "presence":    ["presence_media","presence_politics"],
}

THREAT_SUBTYPE = {"threat_sym_1": "symbolic",  "threat_sym_2": "symbolic",
                  "threat_real_1": "realistic","threat_real_2": "realistic"}
VALENCE_TARGET = {"valence_event_pos": "event",  "valence_event_neg": "event",
                  "valence_outcome_pos": "outcome","valence_outcome_neg": "outcome"}
VALENCE_SIGN   = {"valence_event_pos": "positive","valence_event_neg": "negative",
                  "valence_outcome_pos": "positive","valence_outcome_neg": "negative"}
PRESENCE_CHANNEL = {"presence_media": "media", "presence_politics": "politics"}
INGROUP_ROLE_LABELS = {1: "cause", 2: "recipient", 3: "uninvolved"}

EXCLUSIONS = {
    "US":        {"a1": 7, "a2": 6,    "honest": 1},
    "Australia": {"a1": 7, "a2": 6,    "honest": 1},
    "Germany":   {"a1": 7, "a2": 6,    "honest": 1},
    "Iceland":   {"a1": 7, "a2": 3,    "honest": 1},
    "India":     {"a1": 7, "a2": None, "honest": 1},
    "Chile":     {"a1": 7, "a2": 5,    "honest": 1},
    "Kenya":     {"a1": 2, "a2": 3,    "honest": 1},
}

COUNTRY_FILES = [
    ("1_data_US.xlsx",        "US"),
    ("2_data_Australia.xlsx", "Australia"),
    ("3_data_Germany.xlsx",   "Germany"),
    ("4_data_Iceland.xlsx",   "Iceland"),
    ("5_data_India.xlsx",     "India"),
    ("6_data_Chile.xlsx",     "Chile"),
    ("7_data_Kenya.xlsx",     "Kenya"),
]


def _india_blacklist(section_header: str, end_marker: str) -> set[str]:
    txt = PREP_R.read_text()
    start = txt.find(section_header)
    end = txt.find(end_marker, start)
    return set(re.findall(r'ResponseId != "(R_[A-Za-z0-9]+)"', txt[start:end]))


def _event_year_table() -> dict[str, dict[int, int]]:
    txt = PREP_R.read_text()
    years: dict[str, dict[int, int]] = {}
    for c in EXCLUSIONS:
        start = txt.find(f"# years {c}")
        end_search = txt.find("# years ", start + 1)
        if end_search == -1:
            end_search = txt.find("# attention checks US", start)
        block = txt[start:end_search]
        pairs = re.findall(r"Event_number == (\d+) ~ (\d+)", block)
        years[c] = {int(n): int(y) for n, y in pairs}
    return years


def _participant_filter(df: pd.DataFrame, country: str, blacklist: set[str]) -> pd.DataFrame:
    rules = EXCLUSIONS[country]
    kept = df[(df["attention_check1"] == rules["a1"]) &
              (df["honest"] == rules["honest"])].copy()
    if rules["a2"] is not None:
        kept = kept[kept["attention_check2"] == rules["a2"]]
    if country == "India":
        kept = kept[~kept["ResponseId"].isin(blacklist)]
    return kept


def build_scales() -> None:
    blacklist = _india_blacklist("# attention checks India", "data_long <- data_long %>%")
    parts = []
    for filename, country in COUNTRY_FILES:
        df = pd.read_excel(DATA / filename)
        kept = _participant_filter(df, country, blacklist)
        pol = kept["political_orientation"] if "political_orientation" in kept.columns else pd.NA
        sel = kept[["ResponseId"] + SCALE_ITEMS].copy()
        sel["cov_political_orientation"] = pol
        sel["cov_country"] = country
        parts.append(sel)

    wide = pd.concat(parts, ignore_index=True).rename(columns={"ResponseId": "id"})
    long = wide.melt(
        id_vars=["id", "cov_country", "cov_political_orientation"],
        value_vars=SCALE_ITEMS, var_name="item", value_name="resp",
    ).dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_country", "cov_political_orientation"]]
    long = long.sort_values(["cov_country", "id", "item"], kind="stable").reset_index(drop=True)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "kazarovytska_2026_ingroup_scales.csv"
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, resp_range=[{long['resp'].min()},{long['resp'].max()}]")


def _wide_to_event_long(df: pd.DataFrame) -> pd.DataFrame:
    measures = list(EVENT_RESP_MEASURES) + EVENT_COV_MEASURES
    pattern = re.compile(r"^(\d{2})_event_(.+)$")
    rows_per_event: dict[int, pd.DataFrame] = {}
    for col in df.columns:
        m = pattern.match(col)
        if not m:
            continue
        ev, name = int(m.group(1)), m.group(2)
        if name not in measures:
            continue
        rows_per_event.setdefault(ev, df[["ResponseId"]].copy())
        rows_per_event[ev][name] = df[col].values

    pieces = []
    for ev, sub in rows_per_event.items():
        sub = sub.copy()
        sub["event_number"] = ev
        pieces.append(sub)
    return pd.concat(pieces, ignore_index=True)


def _build_event_long(year_tbl: dict[str, dict[int, int]],
                      blacklist: set[str]) -> pd.DataFrame:
    parts = []
    for filename, country in COUNTRY_FILES:
        raw = pd.read_excel(DATA / filename)
        kept = _participant_filter(raw, country, blacklist)
        long = _wide_to_event_long(kept)

        long = long[long["domestic"].notna()].copy()
        long = long[long["knowledge"] > 2].copy()

        for col in EVENT_RESP_MEASURES:
            if col in long.columns:
                long.loc[(long[col] < 1) | (long[col] > 7), col] = pd.NA

        long["cov_country"] = country
        if "political_orientation" in kept.columns:
            pol = kept.set_index("ResponseId")["political_orientation"]
            long["cov_political_orientation"] = long["ResponseId"].map(pol)
        else:
            long["cov_political_orientation"] = pd.NA
        long["cov_event_year"] = long["event_number"].map(year_tbl[country])
        long["cov_event_domestic"] = long["domestic"].astype("Int64")
        long["cov_event_ingroup_role"] = long["ingroup_role"].map(INGROUP_ROLE_LABELS)
        long["cov_event_temporal_distance"] = long["subjective_temporal_distance"] * -1 + 100
        long["cov_event_knowledge"] = long["knowledge"].astype("Int64")
        long["cov_event_world_history"] = long["relevance_world_history"].astype("Int64")
        parts.append(long)
    return pd.concat(parts, ignore_index=True)


BASE_COVS = ["cov_country","cov_political_orientation","cov_event_year",
             "cov_event_domestic","cov_event_ingroup_role","cov_event_temporal_distance",
             "cov_event_knowledge","cov_event_world_history"]


def _emit_construct(long: pd.DataFrame, construct: str, raw_items: list[str],
                    extra_covs: dict[str, dict[str, str]] | None = None) -> None:
    raw_to_clean = {r: c for r, c in EVENT_RESP_MEASURES.items() if c in raw_items}
    cols_present = [r for r in raw_to_clean if r in long.columns]
    keep = long[["ResponseId", "event_number"] + BASE_COVS + cols_present].copy()
    melted = keep.melt(id_vars=["ResponseId","event_number"] + BASE_COVS,
                       value_vars=cols_present, var_name="raw_item", value_name="resp")
    melted = melted.dropna(subset=["resp"])
    melted["item"] = melted["raw_item"].map(raw_to_clean)
    melted["resp"] = melted["resp"].astype(int)
    melted = melted.rename(columns={"ResponseId": "id", "event_number": "wave"})

    if extra_covs:
        for cov_name, mapping in extra_covs.items():
            melted[cov_name] = melted["item"].map(mapping)

    cols = (["id","item","resp","wave"] + BASE_COVS +
            (list(extra_covs.keys()) if extra_covs else []))
    out = melted[cols].sort_values(["cov_country","id","wave","item"], kind="stable").reset_index(drop=True)

    path = OUT / f"kazarovytska_2026_ingroup_event_{construct}.csv"
    out.to_csv(path, index=False)
    print(f"{path.name}: rows={len(out):,}, ids={out['id'].nunique()}, "
          f"items={out['item'].nunique()}, "
          f"resp_range=[{out['resp'].min()},{out['resp'].max()}]")


def build_event() -> None:
    blacklist = _india_blacklist("# attention checks India", "data_long <- data_long %>%")
    years = _event_year_table()
    long = _build_event_long(years, blacklist)
    OUT.mkdir(parents=True, exist_ok=True)

    _emit_construct(long, "srr", CONSTRUCT_GROUPS["srr"])
    _emit_construct(long, "prr", CONSTRUCT_GROUPS["prr"])
    _emit_construct(long, "threat", CONSTRUCT_GROUPS["threat"],
                    extra_covs={"cov_threat_subtype": THREAT_SUBTYPE})
    _emit_construct(long, "valence", CONSTRUCT_GROUPS["valence"],
                    extra_covs={"cov_valence_target": VALENCE_TARGET,
                                "cov_valence_sign":   VALENCE_SIGN})
    _emit_construct(long, "attribution", CONSTRUCT_GROUPS["attribution"])
    _emit_construct(long, "presence", CONSTRUCT_GROUPS["presence"],
                    extra_covs={"cov_presence_channel": PRESENCE_CHANNEL})


def main() -> None:
    build_scales()
    build_event()


if __name__ == "__main__":
    main()
