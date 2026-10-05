#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11237108
# DOI: 10.1038/s41598-024-66646-1
#   "Longitudinal associations between intergroup contact and intergroup trust
#   among adolescents in ethnic regions of China" (Yuan, Lei, Su, Li & Zhu,
#   2024), Scientific Reports 14:15942.
# Data: the article's only supplementary data file, 41598_2024_66646_MOESM1_ESM.sav
#       (679 x 81, SPSS), fetched from the Europe PMC supplementaryFiles zip.
#       Codebook: the .sav's own variable labels plus the paper's Supplementary
#       Information 1 appendix (item wording and endpoint anchors).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary file.
#
# Item text: shipped. SPSS variable labels carry the English stem of every item
#   (e.g. UCLA02T1 "2.How often do you feel that you lack companionship?"); no
#   value labels exist on any item (checked: value labels only on grade, gender,
#   nation, na01). Endpoint anchors come from the paper's appendix (UCLA 1
#   never - 4 always; contact items per-item endpoints; trust 1 never feel this
#   way - 7 always feel this way). The survey was administered in Mandarin
#   Chinese; no Chinese wording is in the .sav (zero CJK characters in any
#   label) or the paper, so the authors' English ships as a translated
#   substitute with language = Chinese.
#
# Design: two waves one year apart (May-June 2022, then 2023), 679 adolescents
# (grades 7-11) who took part in both, at one ethnic school each in Liangshan
# Yi and Aba Tibetan & Qiang prefectures, Sichuan. `wave` = 1 (T1), 2 (T2).
# The T2 loneliness items are named GD01T2..GD20T2 in the file but carry the
# same labels as UCLA01T1..UCLA20T1 (asserted); item codes drop the T1/T2
# suffix and use UCLA for both waves, so one item code spans both waves.
#
# id: the file's ID column is NOT unique (10150700 appears twice, on a male aged
# 18 and a female aged 16 -- two different students), so id is the row number.
#
# Tables (item codes = source column names minus the wave suffix):
#   yuan_2024_ucla      UCLA Loneliness Scale, 20 items, 1 never - 4 always
#   yuan_2024_contact   Intergroup Contact Experience Scale (Yang et al. rev.),
#                       9 items (quantity 1-5, quality 6-9), 1-7
#   yuan_2024_trust     Intergroup Trust Scale, 4 items (trust, reliability,
#                       lack of trust, suspicion), 1-7
#
# Missing item cells are blank in the file (267 cells) and are dropped; every
# non-missing item value is an integer in range (no imputation). UCLAT1 ..
# TrustT2 are the per-wave scale means (UCLAT1 reproduces the item mean,
# asserted) and are skipped as composites.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
CACHE = REPO_ROOT / "automated_finding" / "runs" / "raw" / "yuan_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11237108/supplementaryFiles"
FNAME = "41598_2024_66646_MOESM1_ESM.sav"


def load():
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / FNAME
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FNAME))
    return pyreadstat.read_sav(str(p))


def main():
    d, meta = load()
    assert d.shape == (679, 81), d.shape
    lab = meta.column_names_to_labels

    blocks = {  # table -> (T1 prefix, T2 prefix, item prefix, n items, permitted)
        "yuan_2024_ucla": ("UCLA", "GD", "UCLA", 20, [1, 2, 3, 4]),
        "yuan_2024_contact": ("QJJC", "QJJC", "QJJC", 9, list(range(1, 8))),
        "yuan_2024_trust": ("XR", "XR", "XR", 4, list(range(1, 8))),
    }
    composites = ["UCLAT1", "ContactT1", "TrustT1", "UCLAT2", "ContactT2", "TrustT2"]
    u = d[[f"UCLA{i:02d}T1" for i in range(1, 21)]].mean(axis=1)
    assert ((u - d["UCLAT1"]).abs().fillna(0) < 1e-9).all()

    # T2 columns carry the same wording as T1
    for t1p, t2p, _, n, _ in blocks.values():
        for i in range(1, n + 1):
            assert lab[f"{t1p}{i:02d}T1"] == lab[f"{t2p}{i:02d}T2"], (t1p, i)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    assert d["ID"].nunique() == 678   # one duplicated source ID (see header)

    cov = {
        "school": "cov_school",
        "grade": "cov_grade",        # 1 = Grade 7 ... 5 = Grade 11 (value labels)
        "class": "cov_class",
        "gender": "cov_gender",      # 1 male, 2 female
        "age": "cov_age",
        "nation": "cov_han_or_minority",  # 1 Han Chinese, 2 ethnic minority
        "na01": "cov_ethnicity",     # 1 Han 2 Tibetan 3 Yi 4 Qiang 5 Hui ...
        "EDUstage": "cov_edu_stage",  # 1 junior high (313), 2 senior high (366)
    }
    skipped = {"ID": "non-unique source id (row number used instead)"}
    skipped.update({c: "per-wave scale mean (composite)" for c in composites})
    item_cols = [f"{p}{i:02d}T{w}" for (t1p, t2p, _, n, _) in blocks.values()
                 for w, p in ((1, t1p), (2, t2p)) for i in range(1, n + 1)]
    assert len(item_cols) == len(set(item_cols)) == 66
    accounted = set(cov) | set(item_cols) | set(skipped) | {"id"}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")
    d = d.rename(columns=cov)
    cov_cols = list(cov.values())
    assert len(blocks) == len(set(blocks))

    for name, (t1p, t2p, ip, n, pv_list) in blocks.items():
        parts = []
        for w, p in ((1, t1p), (2, t2p)):
            cols = {f"{p}{i:02d}T{w}": f"{ip}{i:02d}" for i in range(1, n + 1)}
            t = d[["id"] + cov_cols + list(cols)].rename(columns=cols)
            t = t.melt(id_vars=["id"] + cov_cols, value_vars=list(cols.values()),
                       var_name="item", value_name="resp")
            t["wave"] = w
            parts.append(t)
        t = pd.concat(parts).dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        assert set(t["resp"]) <= set(pv_list), (name, set(t["resp"]))
        t = t[["id", "item", "resp", "wave"] + cov_cols].sort_values(
            ["id", "wave", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item", "wave"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: set(pv_list) for i in t["item"].unique()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
