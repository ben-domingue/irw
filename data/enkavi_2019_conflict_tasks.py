from __future__ import annotations

import gzip
import io
from pathlib import Path

import pandas as pd
import requests

# Source (raw data): https://github.com/IanEisenberg/Self_Regulation_Ontology/tree/master/Data
# Paper: Enkavi, Eisenberg, Bissett, Mazza, MacKinnon, Marsch & Poldrack
# (2019), "Large-scale analysis of test-retest reliabilities of
# self-regulation measures", PNAS 116(12):5472-5477.
# DOI: 10.1073/pnas.1818430116
#
# License: no LICENSE file/field exists on the GitHub repo or an OSF
# companion (checked automated_finding/license_blocked_candidates.csv,
# "user-directed" 2026-07-17 row) -- ben-domingue emailed the authors
# (zenkavi@stanford.edu) requesting permission and received explicit
# confirmation the data is released under CC BY. See
# automated_finding/BATCH_LOG.md's "User-directed lead" entry for the full
# discovery/licensing trail.
#
# STRUCTURE: this is the Self Regulation Ontology (SRO) behavioral battery.
# Each task has its own Individual_Measures/<task>.csv.gz file, released
# twice -- once for the "Complete" (baseline) sample and once for the
# "Retest" sample (worker_id is stable across both, ~150 of 522 baseline
# workers also did a retest session) -- giving a genuine wave=1/wave=2
# structure for test-retest reliability analysis. Only conflict/interference
# -type tasks are processed here (Stroop, Simon, ANT-flanker, go/no-go,
# AX-CPT-style dot-pattern-expectancy, Navon/global-local, stop-signal,
# task-switching) -- the SRO battery also includes ~50 other measures
# (survey instruments, n-back, discounting tasks, etc.) not covered by this
# script.
#
# ITEM CONSTRUCTION: `item` is the actual stimulus/trial-type identity for
# each task (the specific combination of perceptual + response-mapping
# attributes that recurs across trials and across people), NOT a bare
# positional trial index -- e.g. Stroop's item is (word, color) ("red_red",
# "red_blue", ...; 9 combinations), not "trial 5". This makes each task's
# itemcov_* columns genuinely invariant within an item (a stable attribute
# of that stimulus), not merely invariant by construction. One wrinkle:
# Simon's color-to-response-key mapping is counterbalanced *across*
# participants (confirmed empirically -- the same stim_color+stim_side
# combination is "congruent" for roughly half the sample and "incongruent"
# for the other half, but always consistent *within* a given participant),
# so `condition` has to be folded into Simon's item key itself, not left as
# a derived itemcov_. Every other task's congruency/condition label is
# fully derivable from its stimulus columns and is exposed as an itemcov_
# column for convenience even though it's redundant with the item key.
#
# Because the same stimulus repeats many times per person (e.g. each of
# Stroop's 9 word/color combos appears ~16 times in the test phase), a
# separate `position` column holds the repetition index (1, 2, 3, ... in
# chronological order) -- id+item+wave is therefore NOT unique on its own
# here; id+item+wave+position is. This is a deliberate extension beyond
# datastandard.md's default (which only sanctions id+item duplicates via
# wave) for this trial-repeated-stimulus design.
#
# `resp` is trial accuracy (`correct`, already 0/1 in the source, with
# go_nogo/threebytwo stored as bool -- coerced explicitly since
# pd.to_numeric leaves bool dtype untouched and later breaks on NaN
# assignment). Response time in the source is milliseconds, with -1 marking
# a non-response (timeout, or a successfully withheld go/no-go or
# stop-signal trial) -- converted to seconds, -1 mapped to missing (blank),
# row kept (accuracy is still meaningful on a non-response trial in these
# designs). dot_pattern_expectancy's `correct` column additionally has a
# genuine -1 *sentinel* (not a real accuracy code) on timeout trials --
# filtered out entirely (both accuracy and rt are missing there, unlike the
# go_nogo/stop_signal non-response case where accuracy is still valid).
#
# NOT covered: SRO's SSRT/drift-diffusion derived-parameter files
# (meaningful_variables*.csv etc.), demographics/questionnaire files, and
# the ~50 non-conflict tasks in Individual_Measures/ are left for a
# follow-up pass if wanted.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

RAW_BASE = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/master/Data"
SAMPLES = {1: "Complete_02-16-2019", 2: "Retest_02-16-2019"}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Common cleanup shared by every task: test-stage rows, rt in seconds
    with non-response mapped to missing, resp = accuracy with sentinels
    dropped."""
    df = df[df["exp_stage"] == "test"].copy()

    df["rt"] = pd.to_numeric(df["rt"], errors="coerce") / 1000.0
    df.loc[df["rt"] <= 0, "rt"] = float("nan")

    correct = df["correct"]
    if correct.dtype == bool:
        correct = correct.astype(int)
    df["resp"] = pd.to_numeric(correct, errors="coerce").astype(float)
    df.loc[~df["resp"].isin([0, 1]), "resp"] = float("nan")

    return df.dropna(subset=["resp", "worker_id"]).reset_index(drop=True)


# Each prep function takes the cleaned test-stage frame and returns
# (item_key_cols, itemcov_map) where item_key_cols is the ordered list of
# columns whose combined values define `item`, and itemcov_map is
# {itemcov_name: source_column} for columns to carry through unchanged
# (a subset of, or fully derivable from, item_key_cols).

def _prep_stroop(df):
    return ["stim_word", "stim_color"], {"itemcov_condition": "condition"}


def _prep_simon(df):
    # condition must be IN the key: color-to-key mapping is counterbalanced
    # across participants, so (stim_color, stim_side) alone doesn't
    # determine congruency.
    return ["stim_color", "stim_side", "condition"], {"itemcov_condition": "condition"}


def _prep_ant(df):
    return (
        ["cue", "flanker_type", "flanker_middle_direction", "flanker_location"],
        {"itemcov_condition": "flanker_type", "itemcov_cue": "cue"},
    )


def _prep_gonogo(df):
    df["stim_id"] = df["stimulus"].str.extract(r"id\s*=\s*(stim\d)")
    return ["condition", "stim_id"], {"itemcov_condition": "condition"}


def _prep_dpx(df):
    df["probe_id"] = df["stimulus"].str.extract(r"(probe\d+)\.png")
    return ["condition", "probe_id"], {"itemcov_condition": "condition"}


def _prep_navon(df):
    return (
        ["condition", "global_shape", "local_shape"],
        {"itemcov_level": "condition", "itemcov_conflict": "conflict_condition"},
    )


def _prep_stopsignal(df):
    df["shape_id"] = df["stimulus"].str.extract(r"/(\w+)\.png")
    return (
        ["condition", "SS_trial_type", "shape_id"],
        {"itemcov_delay": "condition", "itemcov_trial_type": "SS_trial_type"},
    )


def _prep_taskswitch(df):
    # `cue` is finer-grained than `task` (2 cues map to each of the 3
    # tasks, confirmed 1:1 -- e.g. cue in {"Parity","Odd-Even"} both mean
    # task=="parity") and is itself part of the classic cued task-switching
    # design, so it's used in the key instead of `task`.
    return (
        ["cue", "stim_number", "stim_color", "task_switch"],
        {"itemcov_task": "task", "itemcov_switch": "task_switch"},
    )


# out_name -> (source_file_stem, prep_function)
TASKS = {
    "enkavi_2019_stroop": ("stroop", _prep_stroop),
    "enkavi_2019_simon": ("simon", _prep_simon),
    "enkavi_2019_ant_flanker": ("attention_network_task", _prep_ant),
    "enkavi_2019_gonogo": ("go_nogo", _prep_gonogo),
    "enkavi_2019_dpx_axcpt": ("dot_pattern_expectancy", _prep_dpx),
    "enkavi_2019_navon": ("local_global_letter", _prep_navon),
    "enkavi_2019_stopsignal": ("stop_signal", _prep_stopsignal),
    "enkavi_2019_taskswitch": ("threebytwo", _prep_taskswitch),
}


def fetch_task(sample_dir: str, task_file: str) -> pd.DataFrame:
    url = f"{RAW_BASE}/{sample_dir}/Individual_Measures/{task_file}.csv.gz"
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as gz:
        return pd.read_csv(gz)


def build_table(task_file: str, prep) -> pd.DataFrame:
    waves = []
    for wave, sample_dir in SAMPLES.items():
        raw = fetch_task(sample_dir, task_file)
        df = _clean(raw)

        item_key_cols, itemcov_map = prep(df)
        df["item"] = df[item_key_cols].astype(str).agg("_".join, axis=1)

        df["id"] = df["worker_id"].astype(str)
        df["wave"] = wave
        df["position"] = df.groupby(["id", "item"]).cumcount() + 1

        out_cols = ["id", "item", "resp", "wave", "position", "rt"]
        for itemcov_name, src_col in itemcov_map.items():
            df[itemcov_name] = df[src_col]
            out_cols.append(itemcov_name)

        waves.append(df[out_cols])

    out = pd.concat(waves, ignore_index=True)

    dup = out.duplicated(subset=["id", "item", "wave", "position"])
    assert not dup.any(), f"duplicate id+item+wave+position rows: {dup.sum()}"

    # Verify every itemcov_* column is actually invariant within item, per
    # datastandard.md's definition -- not merely assumed to be.
    for c in out.columns:
        if c.startswith("itemcov_"):
            nun = out.groupby("item")[c].nunique()
            assert (nun <= 1).all(), f"{c} is not invariant within item ({(nun > 1).sum()} items violate it)"

    return out


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, (task_file, prep) in TASKS.items():
        long = build_table(task_file, prep)
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(
            f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} waves={sorted(long['wave'].unique())} "
            f"max_position={long['position'].max()} "
            f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
