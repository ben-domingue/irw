#!/usr/bin/env python3
# Source: https://zenodo.org/records/18365911
# DOI: 10.1080/14664208.2026.2646706
#   Prilyasinta, N. W., & Purnawan, I. K. (2026). Beyond pride: a tripartite motivation
#   framework for language planning in the Balinese context. Current Issues in Language
#   Planning.
# Data: Zenodo 10.5281/zenodo.18365911 (Prilyasinta, Purnawan; 2026-01-25).
#       "Data for EFA - Total 126.csv" -- pilot sample, 126 respondents x 8 background
#       questions and all 39 pilot items; "Data for CFA - Total 259.csv" -- main sample,
#       259 respondents x 11 background questions and the 23 retained items. Item headers
#       are the full Indonesian stems. "Full questionnaire items for pilot and main
#       Study.pdf" lists the 39 pilot items numbered 1-39 (Indonesian, then English) and the
#       main study's five subscales with their items. Responses 1-6.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for all six tables (administered Indonesian stems from the CSV
#   headers, English from the questionnaire PDF, the authors' own; option text blank -- the
#   deposit and record do not label the 1-6 points). Built by
#   automated_finding/itemtext_verification/make_itemtext_prilyasinta_2026.py. Label levels
#   checked: the CSV headers carry the stems; no value labels exist (CSV).
#
# Item codes: bali_<k>, k = the item's number in the questionnaire PDF's pilot list; each
#   CSV header is matched to exactly one numbered PDF item by its Indonesian text
#   (asserted), so the code is reversible from the PDF.
# Same items, two independent samples -> pooled with cov_study (pilot / main); ids are
#   prefixed by sample.
# Tables (1-6):
#   prilyasinta_2026_identity        bali_1-3        (sense of identity)
#   prilyasinta_2026_responsibility  bali_5,6,8,9    (sense of responsibility)
#   prilyasinta_2026_connectedness   bali_11-14      (socio-cultural connectedness)
#   prilyasinta_2026_multilingualism bali_23-25      (multilingualism goals)
#   prilyasinta_2026_intensity       bali_26,27,30,32,33,34,36,37,39 (motivation intensity)
#   prilyasinta_2026_pilot_items     the 16 pilot items dropped before the main study
#                                    (pilot sample only; kept rather than discarded)
#   Subscale membership is the PDF's main-study section (asserted against the CFA columns).
# Covariates (Indonesian answers as stored): cov_study, cov_residence, cov_tourist_area,
#   cov_home_language, cov_understands_balinese, cov_speaks_balinese, cov_sex, cov_religion,
#   cov_ethnicity; main sample only: cov_age_band, cov_education, cov_profession.
# id: "<pilot|main>_<row>" (no identifier in either file).

import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z18365911"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
Z = "https://zenodo.org/api/records/18365911/files/"
FILES = {"efa.csv": Z + "Data%20for%20EFA%20-%20Total%20126.csv/content",
         "cfa.csv": Z + "Data%20for%20CFA%20-%20Total%20259.csv/content",
         "questionnaire.pdf": Z + "Full%20questionnaire%20items%20for%20pilot%20and%20main%20Study.pdf/content"}
P = "prilyasinta_2026_"
RANGE = range(1, 7)
SUB = {"identity": [1, 2, 3], "responsibility": [5, 6, 8, 9], "connectedness": [11, 12, 13, 14],
       "multilingualism": [23, 24, 25], "intensity": [26, 27, 30, 32, 33, 34, 36, 37, 39]}
HEAD = {"identity": "Sense of Identity", "responsibility": "Sense of Responsibility",
        "connectedness": "Socio-cultural Connectedness", "multilingualism": "Multilingualism Goals",
        "intensity": "Motivation Intensity"}
COV_COMMON = {"Di mana tempat tinggal Anda?": "cov_residence",
              "Apakah Anda tinggal di kawasan pariwisata": "cov_tourist_area",
              "Apa bahasa sehari-hari": "cov_home_language",
              "Dalam komunikasi sehari-hari, menurut Anda, apakah Anda mengerti": "cov_understands_balinese",
              "Dalam komunikasi sehari-hari, apakah Anda bisa berbicara": "cov_speaks_balinese",
              "Jenis kelamin": "cov_sex", "Agama": "cov_religion", "Apa etnis/suku Anda?": "cov_ethnicity"}
COV_MAIN = {"Berapa usia Anda saat ini?": "cov_age_band",
            "Apa jenjang pendidikan Anda yang terakhir?": "cov_education", "Profesi": "cov_profession"}
norm = lambda s: " ".join(str(s).split())  # noqa: E731


def fetch() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, url in FILES.items():
        p = RAW_DIR / name
        if not p.exists():
            r = requests.get(url, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
        out[name] = p
    return out


def pdf_items(pdf: Path) -> tuple:
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True,
                         check=True).stdout
    pil = txt[txt.index("For Pilot Study"):txt.index("For Main Study")]
    blocks = re.split(r"\n(\d+)\.\s", pil)
    items = {int(blocks[i]): norm(blocks[i + 1]) for i in range(1, len(blocks), 2)}
    assert sorted(items) == list(range(1, 40))
    main = txt[txt.index("For Main Study"):]
    return items, main


def code_columns(cols, items) -> dict:
    out = {}
    for c in cols:
        k = [k for k, v in items.items() if v.startswith(norm(c))]
        assert len(k) == 1, (c, k)
        out[c] = f"bali_{k[0]}"
    return out


def rename_covs(x, spec):
    ren = {}
    for pre, new in spec.items():
        hit = [c for c in x.columns if norm(c).startswith(pre)]
        assert len(hit) == 1, (pre, hit)
        ren[hit[0]] = new
    return x.rename(columns=ren)


def main() -> None:
    paths = fetch()
    pdf, main_txt = pdf_items(paths["questionnaire.pdf"])
    e = pd.read_csv(paths["efa.csv"])
    c = pd.read_csv(paths["cfa.csv"])
    assert e.shape == (126, 47) and c.shape == (259, 34)
    ce, cc = code_columns(e.columns[8:], pdf), code_columns(c.columns[11:], pdf)
    assert sorted(ce.values(), key=lambda s: int(s[5:])) == [f"bali_{k}" for k in range(1, 40)]
    kept = sorted(int(v[5:]) for v in cc.values())
    assert kept == sorted(k for v in SUB.values() for k in v)
    # subscale membership = the PDF's main-study sections
    secs = list(HEAD.values())
    for k, head in HEAD.items():
        i = main_txt.index(head)
        nxt = [main_txt.index(h) for h in secs if main_txt.index(h) > i]
        body = norm(main_txt[i:min(nxt) if nxt else len(main_txt)])
        found = sorted(n for n in range(1, 40) if pdf[n].split(". ")[0][:40] in body)
        assert set(SUB[k]) - {5} <= set(found), (k, found)   # item 5 is missing from the PDF list
    e = rename_covs(e.rename(columns=ce), COV_COMMON)
    c = rename_covs(rename_covs(c.rename(columns=cc), COV_COMMON), COV_MAIN)
    e.insert(0, "id", [f"pilot_{i + 1:03d}" for i in range(len(e))])
    c.insert(0, "id", [f"main_{i + 1:03d}" for i in range(len(c))])
    e["cov_study"], c["cov_study"] = "pilot", "main"
    d = pd.concat([e, c], ignore_index=True)
    assert d["id"].is_unique
    covs = ["cov_study"] + list(COV_COMMON.values()) + list(COV_MAIN.values())
    pilot_only = [f"bali_{k}" for k in range(1, 40) if k not in kept]
    TABLES = {**{k: [f"bali_{n}" for n in v] for k, v in SUB.items()}, "pilot_items": pilot_only}
    items = [x for v in TABLES.values() for x in v]
    assert len(items) == 39 == len(set(items))
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + [c for c in covs if t[c].notna().any()]].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
