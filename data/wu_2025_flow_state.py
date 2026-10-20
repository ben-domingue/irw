#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/96k3fd6xym
# DOI: 10.17632/96k3fd6xym (v1, 10.17632/96k3fd6xym.1)
#   Wu, Hetianze (2025). "The Multidimensional Manifestations of Flow: A Comparative
#   Study of Cognitive and Embodied Tasks" [Data set]. Mendeley Data.
#   (The deposit record names Hetianze Wu as its only contributor; the companion
#   deposit 10.17632/5yrz5r62wz is a different study by a different depositor.)
# Data: "Breathing task.sav" (154 rows) and "Game task.sav" (100 rows). Each file is a
#       pretest/posttest stack of a 33-item flow questionnaire: 33 item columns whose
#       SPSS *variable labels* are the numbered Chinese stems ("14.我不关心别人可能会
#       如何评价自己。"), a 分组 column value-labelled 前测 (pretest) = 1 and 后测
#       (posttest) = 2, and nine subscale means F1-F9.
# License: CC BY 4.0 (the Mendeley Data record's `data_licence` is CC BY 4.0).
#
# Item text: not shipped, deliberately, although it is cheap here -- the Chinese stems
#   are in the SPSS variable labels (checked both levels: variable labels carry the
#   full numbered stems; value labels exist only on 分组, not on any item). The stems
#   are the Flow State Scale-2 / Dispositional Flow Scale-2 (Jackson & Eklund 2002),
#   whose wording is distributed under licence by Mind Garden, and the Chinese
#   adaptation ("CDFS-2" in the deposit description) has its own unestablished terms.
#   Neither has a row in itemtext/instrument_rights_register.csv, and silence does not
#   ship. Where the text actually is: the variable labels of these two .sav files, plus
#   the deposit's own "CDFS-2 and DFSS-2 (translation).docx".
#
# Item codes: fss_<k>, where k is the leading number of each column's variable label
#   ("14.我不关心..." -> fss_14). The column *names* are mangled (the first is literally
#   "@1", several drop punctuation), so the label's own number is the reversible tie --
#   not the column position. Verified below: the 33 extracted numbers are exactly 1-33,
#   and the two files agree stem-for-stem on every code.
#
# id and wave: neither file carries a respondent identifier. Each is a block layout --
#   all 前测 rows, then all 后测 rows, 77/77 in the breathing file and 50/50 in the game
#   file -- so participant k of a file is row k of its pretest block paired with row k of
#   its posttest block. That positional pairing is an assumption the file forces; it is
#   corroborated by 77 + 50 = 127, the analytic N the deposit description states. wave
#   is 1 (pretest) / 2 (posttest). Game-task ids are offset past the breathing-task max,
#   and cov_task keeps the sample label.
#
# Columns skipped: F1-F9 in both files -- subscale means over the item columns
#   (fractional, e.g. 1.333...), i.e. derived composites, not responses.
# Table:
#   wu_2025_flow_state  33 items, 1-5, 127 participants x 2 waves
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "wu_2025_flow_state"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://data.mendeley.com/public-files/datasets/96k3fd6xym/files"
FILES = {
    "breathing": f"{BASE}/d2ce9864-cdaf-46b4-99f2-52afff05d91b/file_downloaded",
    "game": f"{BASE}/ac90c69d-15fe-4e79-988c-6736f1a8701f/file_downloaded",
}
NAME = "wu_2025_flow_state"
SENTINEL = -2  # out-of-range code used for a handful of missing cells


def fetch(label: str, url: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    p = RAW_DIR / f"{label}.sav"
    if not p.exists():
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def screen_for_pii(df: pd.DataFrame, label: str) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] {label}: examined {df.shape[1]} columns, "
          f"{len(text_cols)} of them string-typed")
    assert df.shape[1] > 0
    pats = [r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", r"\+?\d[\d \-()]{8,}",
            r"^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$", r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"]
    hits = [(c, p) for c in text_cols for p in pats
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits


def read_one(label: str, url: str) -> tuple[pd.DataFrame, dict[str, str]]:
    df, meta = pyreadstat.read_sav(str(fetch(label, url)))
    screen_for_pii(df, label)
    labels = meta.column_names_to_labels
    codes: dict[str, str] = {}
    for c in df.columns:
        lab = str(labels.get(c) or "")
        m = re.match(r"\s*(\d+)\s*[.．、 ]", lab)
        if m and c not in ("分组",) and not re.fullmatch(r"F\d", str(c)):
            k = int(m.group(1))
            code = f"fss_{k}"
            assert code not in codes.values(), (label, code, c)
            codes[c] = code
    assert sorted(int(v.split("_")[1]) for v in codes.values()) == list(range(1, 34)), \
        (label, sorted(codes.values()))
    skipped = [c for c in df.columns if c not in codes and c != "分组"]
    assert all(re.fullmatch(r"F\d", str(c)) for c in skipped), skipped
    print(f"[books] {label}: 33 item columns + 分组 kept; "
          f"skipped {skipped} (subscale means over those items)")
    return df, codes


def build() -> pd.DataFrame:
    parts = []
    offset = 0
    stem_check: dict[str, str] = {}
    for label, url in FILES.items():
        df, codes = read_one(label, url)
        _, meta = pyreadstat.read_sav(str(fetch(label, url)))
        for c, code in codes.items():
            stem = re.sub(r"\s+", "", str(meta.column_names_to_labels[c]))
            stem_check.setdefault(code, stem)
        wave = df["分组"].astype(int)
        n_pre = int((wave == 1).sum())
        assert n_pre == int((wave == 2).sum()), label
        assert (wave.values[:n_pre] == 1).all() and (wave.values[n_pre:] == 2).all(), label
        # Block layout: participant k is row k of each block.
        pid = pd.Series(list(range(1, n_pre + 1)) * 2, index=df.index) + offset
        offset += n_pre
        w = df[list(codes)].rename(columns=codes)
        w = w.assign(id=pid.values, wave=wave.values, cov_task=label)
        long = w.melt(id_vars=["id", "wave", "cov_task"],
                      var_name="item", value_name="resp")
        parts.append(long)
    t = pd.concat(parts, ignore_index=True)
    t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
    n_sent = int((t["resp"] == SENTINEL).sum())
    t = t[t["resp"] != SENTINEL]
    print(f"[clean] dropped {n_sent} cell(s) coded {SENTINEL} (out-of-scale missing code)")
    t = t.dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    return t[["id", "item", "resp", "wave", "cov_task"]].reset_index(drop=True)


def main() -> None:
    t = build()
    pv = [1, 2, 3, 4, 5]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:180]}")
    rep = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
    for f in rep.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:180]}")
    assert len({NAME}) == 1
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"waves={sorted(t['wave'].unique())} resp={t['resp'].min():g}-{t['resp'].max():g}")


if __name__ == "__main__":
    main()
