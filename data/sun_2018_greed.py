#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/csgs546vxy (version 2)
# DOI: 10.1016/j.paid.2018.08.012
#   Liu, Z., Sun, X., Ding, X., Hu, X., Xu, Z., & Fu, Z. (2019).
#   "Psychometric properties of the Chinese version of the Dispositional
#   Greed Scale and a portrait of greedy people." Personality and Individual
#   Differences, 137, 101-109. (Elsevier bot-walls automated fetches; read
#   2026-10-02 from a PDF Ben supplied.)
#   Dataset: Sun, X. (2018). Data for: Psychometric properties of the Chinese
#   version of the Dispositional Greed Scale and a portrait of greedy people.
#   Mendeley Data, v2. https://doi.org/10.17632/csgs546vxy.2
# Data: Mendeley Data csgs546vxy v2, four .sav files, one per sample, as the
#       deposit description lists them: "Study 1-Sample A-133" (EFA, 133 x
#       20), "Study 1-Sample B-303" (CFA, 303 x 29), "Study 2-303" (303 x 30)
#       and "Study 3-309" (309 x 84). The description gives the total as
#       1,048 participants = 133 + 303 + 303 + 309, i.e. four separate
#       samples. Checked: no (age, gender, education, greed-vector) tuple
#       recurs in more than 2-5 rows between any two files, consistent with
#       chance matches on a 7-item 1-7 scale, not a re-used sample.
# License: CC BY 4.0 (Mendeley Data API, data_licence short_name).
#
# Item text: not shipped. Both label levels checked: the variable labels are
#   positional ("greed1", "self-esteem3", "Belief in a just world 2"), and
#   the value labels carry only the English response anchors. Lead: the
#   paper's Table 1 prints all seven DGSC items, English with the Chinese as
#   administered, under the codes G1-G7 (a paper_explicit mapping, so it
#   needs a verify_<table>.R). The other scales' stems are in their
#   published Chinese versions.
#
# Scale identities and ranges are confirmed by the paper (sections 2.3, 3.2,
# 4.2): DGSC 7 items; Psychological Entitlement Scale (Campbell et al. 2004)
# 9 items, sample A; Material Values Scale (Richins & Dawson 1992) 18 items,
# sample B; Zero-Sum Game Belief Scale 8 items and subjective socio-economic
# insecurity 10 items (1 not at all likely .. 7 very likely), Study 2;
# Rosenberg Self-Esteem 10, Chinese GSE 10, Levenson IPC 24, EPQ-RS
# neuroticism 12, Rosenberg Faith in People 4, benevolent world 6, PBJWS 7,
# Study 3. Every scale is rated 1-7 (1 strongly disagree .. 7 strongly
# agree, SSEI as above), which the value labels match and the script
# asserts. The paper drops self-esteem item 8 from its own analysis on
# cultural grounds (Tian 2006); it was administered, so SE8 ships. Gender
# (0 female, 1 male) and education (1-6) codes are from section 3.2.5.
# Items are stored as answered: several scales still carry their
# negatively worded items unreversed (negative inter-item correlations in
# self-esteem, materialism, entitlement, trust and benevolent-world), and
# there are no reverse-coded copy columns.
#
# Tables (item codes are the source column names):
#   sun_2018_greed          G1-G7    Dispositional Greed Scale, Chinese
#                                    (DGSC); all four samples, cov_study.
#   sun_2018_entitlement    E1-E9    psychological entitlement (Study 1A)
#   sun_2018_materialism    M1-M18   materialism (Study 1B)
#   sun_2018_ssei           SSEI1-10 subjective socio-economic insecurity
#                                    (Study 2)
#   sun_2018_bzsg           BZSG1-8  Belief in a Zero-Sum Game (Study 2)
#   sun_2018_self_esteem    SE1-SE10 self-esteem (Study 3)
#   sun_2018_gse            GSE1-10  generalized self-efficacy (Study 3)
#   sun_2018_ipc            IPC1-24  locus of control (24 items; Study 3)
#   sun_2018_neuroticism    N1-N12   neuroticism (Study 3)
#   sun_2018_trust          TIP1-4   trust in people (Study 3)
#   sun_2018_bbw            BBW1-6   belief in a benevolent world (Study 3)
#   sun_2018_bjw            BJW1-7   belief in a just world (Study 3)
#
# Dropped: ID (a per-file sequence number; it repeats across files and 31
#   values repeat within Study 3 on rows with different demographics, so it
#   is not a person key). MTS (money allocated to self in a dictator game,
#   0-10, Study 2) is a single behavioural measure, kept as a covariate on
#   the Study 2 tables.
# id: row index over the four files stacked in the order above (1-1048), so
#   one person keeps one id across the greed table and their own sample's
#   other tables.
# Covariates: cov_study (1A, 1B, 2, 3), cov_gender (0 female, 1 male),
#   cov_age, cov_education (1 primary or lower .. 6 postgraduate),
#   cov_money_to_self (Study 2 tables only).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/csgs546vxy"

# study label, filename, expected shape
FILES = [("1A", "Study 1-Sample A-133.sav", (133, 20)),
         ("1B", "Study 1-Sample B-303.sav", (303, 29)),
         ("2", "Study 2-303.sav", (303, 30)),
         ("3", "Study 3-309.sav", (309, 84))]
DEMOS = {"GENDER": "cov_gender", "AGE": "cov_age", "EDU": "cov_education"}


def block(prefix, n):
    return [f"{prefix}{i}" for i in range(1, n + 1)]


# table -> (items, studies it comes from)
TABLES = {
    "sun_2018_greed": (block("G", 7), ["1A", "1B", "2", "3"]),
    "sun_2018_entitlement": (block("E", 9), ["1A"]),
    "sun_2018_materialism": (block("M", 18), ["1B"]),
    "sun_2018_ssei": (block("SSEI", 10), ["2"]),
    "sun_2018_bzsg": (block("BZSG", 8), ["2"]),
    "sun_2018_self_esteem": (block("SE", 10), ["3"]),
    "sun_2018_gse": (block("GSE", 10), ["3"]),
    "sun_2018_ipc": (block("IPC", 24), ["3"]),
    "sun_2018_neuroticism": (block("N", 12), ["3"]),
    "sun_2018_trust": (block("TIP", 4), ["3"]),
    "sun_2018_bbw": (block("BBW", 6), ["3"]),
    "sun_2018_bjw": (block("BJW", 7), ["3"]),
}
ALLOWED = set(range(1, 8))
LIKERT7 = {1.0: "strongly disagree", 2.0: "disagree",
           3.0: "disagree somewhat", 4.0: "neutral", 5.0: "agree somewhat",
           6.0: "agree", 7.0: "strongly agree"}
SSEI_LABELS = {1.0: "not at all likely", 7.0: "very likely"}


def load():
    meta = requests.get(API, headers=UA, timeout=60).json()
    assert meta["data_licence"]["short_name"] == "CC BY 4.0"
    urls = {f["filename"]: f["content_details"]["download_url"]
            for f in meta["files"]}
    assert set(urls) == {f for _, f, _ in FILES}, set(urls)
    out = {}
    for study, fn, shape in FILES:
        r = requests.get(urls[fn], headers=UA, timeout=120)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
            f.write(r.content)
            path = f.name
        try:
            df, m = pyreadstat.read_sav(path)
        finally:
            os.unlink(path)
        assert df.shape == shape, (fn, df.shape)
        out[study] = (df, m)
    return out


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = load()

    # Balance the books, per file.
    frames = []
    for study, _, _ in FILES:
        df, m = files[study]
        items = [c for t, (its, st) in TABLES.items() if study in st
                 for c in its]
        known = {"ID"} | set(DEMOS) | set(items)
        if study == "2":
            known |= {"MTS"}
        assert set(df.columns) == known, (study, set(df.columns) ^ known)
        for c in items:
            want = SSEI_LABELS if c.startswith("SSEI") else LIKERT7
            assert m.variable_value_labels[c] == want, (study, c)
        df = df.drop(columns=["ID"]).rename(columns=DEMOS)
        df = df.rename(columns={"MTS": "cov_money_to_self"})
        df.insert(0, "cov_study", study)
        frames.append(df)
    d = pd.concat(frames, ignore_index=True)
    assert len(d) == 1048
    d.insert(0, "id", d.index + 1)
    demo_cols = ["cov_study"] + list(DEMOS.values())

    names = []
    for table, (its, studies) in TABLES.items():
        cov_cols = demo_cols + (["cov_money_to_self"] if studies == ["2"]
                                else [])
        sub = d[d["cov_study"].isin(studies)]
        if len(studies) == 1:
            cov_cols = [c for c in cov_cols if c != "cov_study"]
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=its,
                        var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - ALLOWED
            assert not bad, (table, it, bad)
        pv = {i: ALLOWED for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            if c != "cov_study":
                long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(
            str(out), profile="upload", context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
