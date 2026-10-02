#!/usr/bin/env python3
# Source: https://osf.io/ztxcd/
# DOI: 10.1037/pspp0000608
#   Zhang, Jacobson, Hardin & Sun (2026). "Virtue trade-offs in everyday
#   life." Journal of Personality and Social Psychology 131(4).
# Data: OSF ztxcd, S1/data/Moral_dilemma_S1_cleaned.csv (12,385 episode rows x
#       203; 377 people, ID 1-389). Day Reconstruction Method diary study:
#       one intake survey of trait scales, then up to 8 nightly diaries, each
#       reconstructing the day's episodes. Codebook: S1/data/Codebook Virtue
#       Dilemma - S1.xlsx. Wording/response options also checked against
#       S1/materials/Virtue_Affordances_Baseline.qsf.
# License: CC BY 4.0 (OSF node licence, api.osf.io/v2/nodes/ztxcd, public).
#
# Item text: shipped for the four zhang_2026_ipip_* tables and the two
#   episode tables (data_labels + study_materials: the codebook's "Item"
#   column gives each item's stem keyed by its column name; response anchors
#   from the codebook "Values" column and the .qsf answer labels). Not
#   shipped for the rest: the wording is in the same codebook, but BFI-2 and
#   HEXACO are `block` in itemtext/instrument_rights_register.csv, and MCQ
#   (Furr et al.), Moral Attentiveness (Reynolds 2008), the courage items,
#   TCS and the wisdom items are not in the register yet.
#
# Trait tables (one row per person: trait items repeat identically on every
# episode row -- asserted -- so the file is deduplicated to one row per ID):
#   zhang_2026_mcq_morality        MCQ_General1-4        1-5
#   zhang_2026_mcq_loyalty         MCQ_Loyal1-4          1-5
#   zhang_2026_moral_attentiveness Attentiveness1-12     1-7
#   zhang_2026_bfi2_neuroticism    BFI_N1-3              1-5
#   zhang_2026_bfi2_compassion     BFI_Compassion1-4     1-5
#   zhang_2026_bfi2_respect        BFI_Respect1-4        1-5
#   zhang_2026_bfi2_responsibility BFI_Responsibility1-4 1-5
#   zhang_2026_courage             Brave1-5              1-4
#   zhang_2026_tcs_honesty         TCS1-6                1-5
#   zhang_2026_hexaco_modesty      HH_Modesty1-4         1-5
#   zhang_2026_wisdom              Wise1-4               1-6
#   zhang_2026_ipip_fairness       IPIP_Fairness1-4      1-5
#   zhang_2026_ipip_forgiveness    IPIP_Forgiveness1-4   1-5
#   zhang_2026_ipip_gratitude      IPIP_Gratitude1-4     1-5
#   zhang_2026_ipip_patience       IPIP_Patience1-4      1-5
#   Grouping: one file per construct. The paper scores each block as its own
#   trait virtue (tr_* composites), and datastandard.md puts a subscale
#   treated as a distinct construct in its own file. The IPIP items come from
#   four different IPIP scales, and the three BFI-2 facets sit in three
#   different domains (N; Agreeableness; Conscientiousness), so neither
#   instrument is one construct. No table has fewer than 3 items.
#   Ranges: the codebook says 1-7 for HH_Modesty and Wise. The .qsf shows
#   HH_Modesty administered 1-5 and Wise 1-6, and observed values agree, so
#   the .qsf ranges are used.
#   Reverse-keyed items are UNREVERSED here. The deposit stores them only as
#   R.<name> = 6 - raw (8 - raw for Attentiveness2), per
#   Virtuetradeoff_S1_cleaning.Rmd lines 771-789 and 888-889; raw is
#   recovered with the same constant and the R. prefix is dropped from the
#   item code. The authors' constant is 6 for HH_Modesty too, which is
#   correct for its administered 1-5 scale.
#
# Episode tables (repeated measures; wave = episode order within person,
# ordered by diary day then the diary's own episode number E1, E2, ...):
#   zhang_2026_virtue_states   12 items, 1-7: "How <virtue> were you during
#     this episode?" for fairness, patience, courage, humility, honesty,
#     gratitude, wisdom, responsibility, compassion, forgiveness, loyalty,
#     respect. Asked on every episode, whether or not the virtue was marked
#     relevant (op_*), so each episode is a complete administration.
#   zhang_2026_episode_affect  3 items, 1-7: happiness, social connection,
#     meaning during the episode. A different construct from the virtue
#     states, so its own file.
#   (ID, day, Episode) is unique (asserted), so (id, item, wave) is unique.
#   Not carried: op_* opportunity checkboxes and conflict* pair checkboxes
#   (multi-select checklists, not rated items); episode clock times/length.
#
# Respondents: the deposit is the authors' cleaned file -- the cleaning .Rmd
#   already dropped test runs, diaries done in <= 240 s, sleeping episodes and
#   incoherent diaries. No further exclusion is applied.
# Study 2 (S2/data/Moral_dilemma_S2b_cleaned_wide.csv, N = 988) is NOT merged.
#   Its Current_* block rates 10 of S1's 12 virtues (no gratitude, no wisdom)
#   for one tradeoff episode chosen for the respondent, not every diary
#   episode, so it fails the same-instrument test. It also carries free-text
#   episode narratives, and Prolific-demographic.csv holds platform IDs.
# id: the deposit's randomly assigned participant ID (1-389). No names,
#   emails, IP/GPS or platform IDs in the S1 file; it has no text columns.
# Covariates: cov_age; cov_gender (1 male, 2 female, 3 self-describe, 4 prefer
#   not to say); cov_ethnicity (multi-select, stored as the digits of the
#   chosen codes concatenated, e.g. "134" = White + Asian + Native American;
#   1 White, 2 Black, 3 Asian, 4 Native American/Alaska Native, 5 Hispanic/
#   Latino, 6 Pacific Islander, 7 Other, 8 Prefer not to say);
#   cov_religiosity (1-7); cov_religion (1 Christian, 2 Jewish, 3 Muslim,
#   4 Buddhist, 5 Hindu, 6 Sikh, 8 Agnostic, 9 Atheist, 10 Other, 11 Prefer
#   not to say); cov_politics (raw code: 1-7 run very liberal to very
#   conservative, 8-9 are off-scale. The .qsf labels 8 Other, 9 Don't know,
#   10 Libertarian, while the cleaning .Rmd reads 8 as libertarian and 9 as
#   other, so treat 8/9 as non-ordinal and unresolved.)

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://osf.io/download/68e08b1b6e1d93e810e474c2/"


def items(prefix, n):
    return [f"{prefix}{i}" for i in range(1, n + 1)]


# table -> (source item columns without the R. prefix, allowed values)
TRAIT = {
    "zhang_2026_mcq_morality": (items("MCQ_General", 4), range(1, 6)),
    "zhang_2026_mcq_loyalty": (items("MCQ_Loyal", 4), range(1, 6)),
    "zhang_2026_moral_attentiveness": (items("Attentiveness", 12),
                                       range(1, 8)),
    "zhang_2026_bfi2_neuroticism": (items("BFI_N", 3), range(1, 6)),
    "zhang_2026_bfi2_compassion": (items("BFI_Compassion", 4), range(1, 6)),
    "zhang_2026_bfi2_respect": (items("BFI_Respect", 4), range(1, 6)),
    "zhang_2026_bfi2_responsibility": (items("BFI_Responsibility", 4),
                                       range(1, 6)),
    "zhang_2026_courage": (items("Brave", 5), range(1, 5)),
    "zhang_2026_tcs_honesty": (items("TCS", 6), range(1, 6)),
    "zhang_2026_hexaco_modesty": (items("HH_Modesty", 4), range(1, 6)),
    "zhang_2026_wisdom": (items("Wise", 4), range(1, 7)),
    "zhang_2026_ipip_fairness": (items("IPIP_Fairness", 4), range(1, 6)),
    "zhang_2026_ipip_forgiveness": (items("IPIP_Forgiveness", 4),
                                    range(1, 6)),
    "zhang_2026_ipip_gratitude": (items("IPIP_Gratitude", 4), range(1, 6)),
    "zhang_2026_ipip_patience": (items("IPIP_Patience", 4), range(1, 6)),
}
# Constant the cleaning .Rmd subtracted from to build each R. column.
REVERSE_CONST = {"Attentiveness2": 8}

EPISODE = {
    "zhang_2026_virtue_states": (
        ["fairness", "patience", "courage", "humility", "honesty",
         "gratitude", "wisdom", "responsibility", "compassion",
         "forgiveness", "loyalty", "respect"], range(1, 8)),
    "zhang_2026_episode_affect": (
        ["happiness", "socialconnection", "meaning"], range(1, 8)),
}

COVS = {"age": "cov_age", "gender": "cov_gender",
        "ethnicity": "cov_ethnicity", "religiosity": "cov_religiosity",
        "religion": "cov_religion", "politics": "cov_politics"}
COMPOSITES = {"morality", "attentiveness", "neuroticism"}


def write(long, table, item_list, allowed, extra):
    cov_cols = list(COVS.values())
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - set(allowed)
        assert not bad, (table, it, bad)
    long = long[["id", "item", "resp"] + extra + cov_cols]
    long = long.sort_values(["id"] + extra + ["item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"] + extra).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(item_list) > 1
    pv = {i: set(allowed) for i in item_list}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{table}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), low_memory=False)
    assert d.shape == (12385, 203) and d["ID"].nunique() == 377, d.shape
    assert not [c for c in d.columns if d[c].dtype == object
                and c != "Episode"], "unexpected text column"

    d = d.rename(columns={"ID": "id"}).rename(columns=COVS)
    d["cov_ethnicity"] = d["cov_ethnicity"].astype(str)
    d["cov_religion"] = d["cov_religion"].astype("Int64")

    # --- trait tables: one row per person ---------------------------------
    src = {}  # item code -> source column
    for item_list, _ in TRAIT.values():
        for it in item_list:
            src[it] = it if it in d.columns else f"R.{it}"
            assert src[it] in d.columns, it
    trait_src = list(src.values())
    per = d[["id"] + list(COVS.values()) + trait_src]
    assert per.groupby("id").nunique(dropna=False).max().max() == 1
    per = per.drop_duplicates("id").reset_index(drop=True)
    assert len(per) == 377
    for it, col in src.items():
        if col.startswith("R."):
            per[it] = REVERSE_CONST.get(it, 6) - per[col]
            per = per.drop(columns=col)

    # Balance the books against the trait block of the source file.
    first = d.columns.get_loc("BFI_N1")
    trait_cols = set(d.columns[first:])
    assert trait_cols == set(trait_src), trait_cols ^ set(trait_src)
    dropped = {c for c in d.columns if c.startswith("tr_")} | COMPOSITES
    assert dropped <= set(d.columns)

    names = []
    for table, (item_list, allowed) in TRAIT.items():
        long = per.melt(id_vars=["id"] + list(COVS.values()),
                        value_vars=item_list, var_name="item",
                        value_name="resp")
        assert len(long.dropna(subset=["resp"])) == 377 * len(item_list)
        write(long, table, item_list, allowed, [])
        names.append(table)

    # --- episode tables ----------------------------------------------------
    assert not d.duplicated(["id", "day", "Episode"]).any()
    d = d.copy()
    d["_ep"] = d["Episode"].str.extract(r"^E(\d+)$", expand=False).astype(int)
    d = d.sort_values(["id", "day", "_ep"]).reset_index(drop=True)
    d["wave"] = d.groupby("id").cumcount() + 1
    for table, (item_list, allowed) in EPISODE.items():
        long = d.melt(id_vars=["id", "wave"] + list(COVS.values()),
                      value_vars=item_list, var_name="item",
                      value_name="resp")
        write(long, table, item_list, allowed, ["wave"])
        names.append(table)
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
