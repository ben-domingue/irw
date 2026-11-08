#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259445
# DOI: 10.1371/journal.pone.0259445
# Paper: Burghartswieser D, Rothmund T (2021). Conservative bias, selective
#   political exposure and truly false consensus beliefs in political
#   communication about the 'refugee crisis' in Germany. PLoS ONE 16(11):
#   e0259445.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0259445.s003,
#   SoSci Survey CSV export), the paper's final sample of N = 897 German
#   internet users surveyed March-April 2016 (also on OSF mpqgb). The SI S2
#   Text (s002) is the full SoSci questionnaire with every variable code,
#   item wording (German) and response labels.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 5.
#
# TEN output tables, item codes the deposit's own (lower-cased):
#   _refugee_attitudes  GG02_01-08 (eight normative beliefs about asylum
#     policy, 1 "stimme ueberhaupt nicht zu" - 6 "stimme voll und ganz zu")
#     and GG01_01-08 (eight factual beliefs about refugees, e.g. that they
#     take jobs, 1 "stimmt ueberhaupt nicht" - 6 "stimmt voll und ganz"). The
#     paper combines the 16 into one attitude measure (alpha = .89), so they
#     ship as one table. All stored as answered: GG02_04/05/06/08 are
#     refugee-friendly, every other item restrictive. Reversing those four and
#     averaging the 16 gives M = 4.06, SD = 0.97 against the paper's
#     M = 4.08, SD = 0.96 (asserted to within 0.03).
#   _refugee_threat   PG02_01, 02, 04, 05, worry about society's handling of
#     the crisis and its consequences, 1-6. PG02_06/07 (anger at a
#     "welcome culture" / at a dismissive stance) are two single anger items
#     keyed in opposite directions; dropped.
#   _political_info   PE03_01-05, how often informed about foreign, national,
#     local politics, talked politics, searched for information, 1 never -
#     6 daily.
#   _participation    PE04_01-05, boycott, petition, demonstration,
#     spreading information, active membership, 1 never - 5 very often.
#   _refugee_news     NK01_01-04, how often informed about the refugee crisis
#     on TV / newspapers / internet / in conversations, 1 never - 6 daily.
#   _opinion_exposure PG01_01-03, how often hears statements by people
#     strongly against / undecided / strongly for taking in refugees, 1-6.
#   _facebook_exposure NK02_01-05, how often sees refugee news and comments on
#     Facebook (asked of Facebook users), 1-6.
#   _authoritarianism SO01_01-09, the 9-item KSA-3 short authoritarianism
#     scale (aggression, submission, conventionalism), 1-5.
#   _sdo              GP01_02, 05-09 and GP02_01-06, two consecutive
#     social-dominance-orientation item pages, 1-7. Both pages were shown to
#     every respondent; GP02_01/03/06 repeat GP01_07/08/09 word for word and
#     are kept as their own items (they are separate answers).
#   _pvq              the 25 portrait-values items PV01-03 (women's wording)
#     and PV04-06 (men's wording), shown by gender (SD01). The two versions
#     are the same 25 portraits in the same order, so they are pooled as
#     pvq01-pvq25; 1 "ist mir ueberhaupt nicht aehnlich" - 6 "sehr aehnlich".
# Covariates: gender (SD01: 1 female, 2 male), age (SD02_01; the paper
#   reports 13-87), education (SD03, the questionnaire's five labels).
# Dropped: the panel provider's participant code IV02_01 (replaced by the
#   row index), CASE/REF/timestamps/TIME*, the free-text fields (SD07_09,
#   ZE01_*), the engagement items PE06/PE07 (asked only after the pro/contra
#   filter FI01, each with a write-in "other" slot), the 2+2 justice
#   sensitivity items UG01/UG02 (two-item subscales), the share estimates
#   AN01 (0-100 percentages), single items (life satisfaction, left-right,
#   party identification, political interest, Facebook time and groups).
# No sentinel codes occur in the export (-9 "not answered" is stored blank).
# `id` is the row index.
#
# Item text: NOT SHIPPED. The S2 questionnaire carries the German wording of
#   every item; the KSA-3, SDO and PVQ are published third-party instruments.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259445.s003"
RAW = os.environ.get("BURGHARTSWIESER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
EDU = {1: "no degree", 2: "still in education", 3: "Volks-/Hauptschule",
       4: "Real-/Oberschule", 5: "Fachhochschule/Hochschulreife"}


def cols(prefix, nums):
    return [f"{prefix}_{n:02d}" for n in nums]


BLOCKS = {
    "refugee_attitudes": (cols("GG02", range(1, 9)) + cols("GG01", range(1, 9)), 6),
    "refugee_threat": (cols("PG02", [1, 2, 4, 5]), 6),
    "political_info": (cols("PE03", range(1, 6)), 6),
    "participation": (cols("PE04", range(1, 6)), 5),
    "refugee_news": (cols("NK01", range(1, 5)), 6),
    "opinion_exposure": (cols("PG01", range(1, 4)), 6),
    "facebook_exposure": (cols("NK02", range(1, 6)), 6),
    "authoritarianism": (cols("SO01", range(1, 10)), 5),
    "sdo": (cols("GP01", [2, 5, 6, 7, 8, 9]) + cols("GP02", range(1, 7)), 7),
}
PV_F = cols("PV01", range(1, 9)) + cols("PV02", range(1, 9)) + cols("PV03", range(1, 10))
PV_M = cols("PV04", range(1, 9)) + cols("PV05", range(1, 9)) + cols("PV06", range(1, 10))


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, sep=None, engine="python", encoding="utf-8")


def emit(name, long, top):
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        assert g["resp"].between(1, top).all(), (name, it, sorted(g["resp"].unique()))
    assert not long.duplicated(["id", "item"]).any()
    items = sorted(long["item"].unique())
    checks = run_qc(long, permitted_values={c: list(range(1, top + 1)) for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
    out = f"burghartswieser_2021_{name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
    print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={len(items)}")


def convert():
    df = load()
    assert df.shape == (897, 212), df.shape
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    assert set(df["SD01"]) <= {1, 2}
    df["cov_gender"] = df["SD01"].map({1: "female", 2: "male"})
    df["cov_age"] = df["SD02_01"]
    assert df["cov_age"].between(13, 87).all()
    df["cov_education"] = df["SD03"].map(EDU)
    assert df["cov_education"].notna().all()
    covs = ["cov_gender", "cov_age", "cov_education"]

    # The paper's 16-item asylum-attitude score, refugee-friendly items reversed.
    g = df[cols("GG02", range(1, 9)) + cols("GG01", range(1, 9))].copy()
    for c in cols("GG02", [4, 5, 6, 8]):
        g[c] = 7 - g[c]
    att = g.mean(axis=1)
    assert abs(att.mean() - 4.08) < 0.03 and abs(att.std() - 0.96) < 0.03, (att.mean(), att.std())

    for name, (cs, top) in BLOCKS.items():
        sub = df[["id"] + covs + cs].rename(columns={c: c.lower() for c in cs})
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        emit(name, long[["id", "item", "resp"] + covs], top)

    # PVQ: women saw PV01-03, men PV04-06; no one answered both.
    f = df[PV_F].notna().any(axis=1)
    m = df[PV_M].notna().any(axis=1)
    assert not (f & m).any()
    assert (df.loc[f, "SD01"] == 1).all() and (df.loc[m, "SD01"] == 2).all()
    parts = []
    for src in (PV_F, PV_M):
        sub = df[["id"] + covs + src].rename(columns={c: f"pvq{i + 1:02d}" for i, c in enumerate(src)})
        parts.append(sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"]))
    emit("pvq", pd.concat(parts)[["id", "item", "resp"] + covs], 6)


if __name__ == "__main__":
    convert()
