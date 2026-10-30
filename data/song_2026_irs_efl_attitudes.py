#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0360411
# DOI: 10.1371/journal.pone.0360411
# Paper: Song, G., Halili, S. H., & Zainuddin, Z. (2026). Beyond engagement:
#   interactive response systems, student attitudes, and technology
#   acceptance in university EFL classrooms. PLOS ONE 21(10): e0360411.
# Data: journal.pone.0360411.s001 (S1 Data, .xlsx), sheet 'ItemData',
#   102 rows x 101 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 102 non-English-major undergraduates at a Chinese university, two intact
# classes of 51, measured before and after a four-week intervention.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 40 items, 8,160 responses, zero missing cells. The
# paper: 5-point, 1 "strongly disagree" to 5 "strongly agree", higher = more
# positive. Five-point, eight dimensions, five items each, administered TWICE.
#
# THIS IS THE FIRST TABLE IN THE BATCH WITH BOTH A `wave` AND A `treat`
# COLUMN, and both are real rather than cosmetic:
#   wave  -- "pre" and "post", a four-week quasi-experimental pre/post design.
#            The deposit stores it in the column NAME (LA1_Pre, LA1_Post), so
#            melting on the name alone would put the same item twice in one
#            table with no way to tell the occasions apart. wave is its own
#            column, never cov_wave, per datastandard.
#   treat -- 1 for the IRS (interactive response system) group, 0 for the
#            traditional-instruction control. Two arms only, so the control
#            code is unambiguous -- unlike lin_2026_advertising_literacy
#            earlier in this batch, whose three arms left the control unknown
#            and whose arm column was therefore omitted.
#
# CLASS AND CONDITION ARE FULLY CONFOUNDED, which the paper says itself: the
# two arms are two intact classes of 51, not randomised individuals. So
# `treat` identifies the condition and the classroom at once, and a user
# modelling the treatment effect is also modelling a class effect. Stated in
# the description, because nothing in the data reveals it.
#
# THE EIGHT ABBREVIATIONS ARE NOT DEFINED BY THE ARTICLE and are resolved by
# order AND initials agreeing, which is stronger than either alone. The
# article names eight dimensions with five items each, in this order:
# learning atmosphere, participation, attention, confidence, teacher-student
# interaction, peer interaction, learning support, achievement/satisfaction.
# The deposit's blocks appear in the order LA, PA, AT, CF, IT, IP, LS, AC --
# same position, and the initials match each name (IT = interaction-teacher,
# IP = interaction-peer). Two independent agreements, so the mapping ships;
# the description says the article does not state it.
#
# SIXTEEN DERIVED MEANS DROPPED: LA_PreMean ... AC_PostMean, one per
# construct per occasion. Each is asserted to be the mean of its own five
# items before being discarded, which doubles as a check that the block
# membership above is right -- if LA_PreMean were not the mean of LA1_Pre..
# LA5_Pre the whole block assignment would be wrong, and the script would
# stop.
#
# `id` needs no prefixing for once: the deposit already names respondents
# Exp_01..Exp_51 and Ctrl_01..Ctrl_51.
#
# COVARIATES: age in years, gender as the deposit's own F/M labels (a rare
# case in this batch where the codes are letters rather than unexplained
# integers, so nothing has to be pinned), and the student's previous English
# score, a 0-100 mark that is a genuine continuous covariate rather than a
# band index.
#
# Item text: NOT SHIPPED. The article's Table 2 is said to show ONE
# representative item per dimension and is an image in any case; the other 32
# items are published nowhere. Eight of forty is not a table.
#
# PII: screened over all 101 columns. Three string columns -- Group, ID and
# Gender -- all closed vocabularies or study-assigned codes.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SONG_RAW", "journal.pone.0360411_S1_Data.xlsx")

N_ROWS = 102
LO, HI = 1, 5

CONSTRUCTS = {
    "LA": ("song_2026_irs_learning_atmosphere", "Learning atmosphere"),
    "PA": ("song_2026_irs_participation", "Participation"),
    "AT": ("song_2026_irs_attention", "Attention"),
    "CF": ("song_2026_irs_confidence", "Confidence"),
    "IT": ("song_2026_irs_teacher_interaction", "Teacher-student interaction"),
    "IP": ("song_2026_irs_peer_interaction", "Peer interaction"),
    "LS": ("song_2026_irs_learning_support", "Learning support"),
    "AC": ("song_2026_irs_achievement", "Achievement and satisfaction"),
}
WAVES = ["Pre", "Post"]
COVS = {"Age": "cov_age", "Gender": "cov_gender",
        "Previous_English_Score": "cov_previous_english_score"}
ITEM = re.compile(r"^(LA|PA|AT|CF|IT|IP|LS|AC)(\d)_(Pre|Post)$")
MEAN = re.compile(r"^(LA|PA|AT|CF|IT|IP|LS|AC)_(Pre|Post)Mean$")


def convert():
    df = pd.read_excel(RAW, sheet_name="ItemData")
    assert len(df) == N_ROWS, len(df)

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert set(strings) == {"Group", "ID", "Gender"}, strings
    assert set(df["Group"]) == {"Experimental", "Control"}, \
        sorted(set(df["Group"]))
    assert set(df["Gender"]) <= {"F", "M"}, sorted(set(df["Gender"]))
    print(f"PII screen: 3 string columns of {len(df.columns)} -- Group "
          f"(2 levels), Gender (F/M) and ID, a study-assigned code "
          f"(Exp_01.., Ctrl_01..). No names, emails, dates or free text")

    items, means = {}, {}
    for c in df.columns:
        m = ITEM.match(str(c))
        if m:
            items[(m.group(1), int(m.group(2)), m.group(3))] = c
        elif MEAN.match(str(c)):
            mm = MEAN.match(str(c))
            means[(mm.group(1), mm.group(2))] = c
    assert len(items) == 8 * 5 * 2, len(items)
    assert len(means) == 16, len(means)

    # every derived mean must BE the mean of its own five items -- which also
    # re-proves the block membership the construct names rest on
    for (pre, wave), col in means.items():
        cols = [items[(pre, i, wave)] for i in range(1, 6)]
        assert (df[cols].mean(axis=1).round(6) ==
                df[col].round(6)).all(), (
            f"{col} is not the mean of {cols} -- the block assignment this "
            f"script relies on is wrong, so stop")
    print("all 16 derived means reproduce as the mean of their own five "
          "items, which re-proves the block membership; dropped")

    accounted = {"Group", "ID"} | set(COVS) | set(items.values()) | \
        set(means.values())
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    assert df["ID"].nunique() == len(df), "ID is not unique"
    d = df.rename(columns=COVS)
    d["id"] = d["ID"]
    d["treat"] = (d["Group"] == "Experimental").astype(int)
    assert d["treat"].sum() == 51 and (1 - d["treat"]).sum() == 51, \
        "the two arms are no longer 51 and 51"
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, label) in CONSTRUCTS.items():
        frames = []
        for wave in WAVES:
            cols = {items[(prefix, i, wave)]: f"{prefix}{i}"
                    for i in range(1, 6)}
            sub = d.rename(columns=cols)
            long = sub.melt(id_vars=["id", "treat"] + cov_cols,
                            value_vars=list(cols.values()),
                            var_name="item", value_name="resp")
            long["wave"] = wave.lower()
            frames.append(long)
        long = pd.concat(frames, ignore_index=True)
        assert long["resp"].notna().all(), (name, "a missing response")
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(LO, HI).all(), \
            (name, sorted(long["resp"].unique()))
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == 5
        assert set(long["wave"]) == {"pre", "post"}
        assert not long.duplicated(["id", "item", "wave"]).any()
        assert len(long) == 5 * 2 * N_ROWS, (name, len(long))
        assert len(name) <= 40, name
        long = long[["id", "item", "resp", "wave", "treat"] + cov_cols]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items=5 "
              f"waves=2 resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label}]")

    assert total == 40 * 2 * N_ROWS, total
    print(f"8 tables, {total} responses (40 items x {N_ROWS} students x "
          f"2 occasions)")


if __name__ == "__main__":
    convert()
