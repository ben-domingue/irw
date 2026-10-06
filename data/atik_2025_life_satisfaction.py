#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/L3KAA2
# DOI: 10.1186/s40359-025-03246-2
#   Atik & Erdemir (2025). "Validity and reliability analysis of the Turkish life
#   satisfaction scale developed through artificial intelligence", BMC Psychology.
#   (Article CC BY-NC-ND; the data deposit is separately CC0.)
# Data: Harvard Dataverse DVN/L3KAA2, EFA.tab and CFA.tab downloaded as
#       format=original (SPSS .sav, file ids 10797848 / 10797849): two independent
#       samples of Turkish university students, EFA n=503 and CFA n=301, same 33
#       columns. No variable or value labels; no codebook.
# License: CC0 1.0 (Dataverse record).
#
# Column blocks, identified from the paper's Methods ("Data collection tools") and
# checked against it:
#   B1-B5  the ChatGPT-generated Turkish Life Satisfaction Scale: 5 items, 7-point
#          (the paper's prompt and Methods say 7-point; B1-B5 are the only 1-7 block)
#   A1-A5  Satisfaction With Life Scale, Turkish adaptation (Dagli & Baysal): 5 items,
#          1-5 in the deposit; mean(A) correlates .74/.75 with mean(B) in EFA/CFA,
#          the paper's reported criterion correlation with life satisfaction (.74)
#   C1-C14 Scales of General Well-Being short form (Longo et al.; Turkish adaptation):
#          14 items, 1-5
# Out-of-set cells dropped as entry errors: C1 = 6 or 7 (6 + 4 cells -- isolated to C1,
#   whose 1-5 bulk matches the other 13 items), C10 = 6 (1 cell), and
#   0s in A4 (1), C9 (1), C10 (2), C11 (2).
# The two samples are stacked with cov_sample (efa/cfa) and ids prefixed by sample
#   ("efa_12"), since both use ScaleNo 1..n.
# Covariates not shipped: the demographic columns (Cinsiyet, Lisans, Sinif,
#   Isteyerek, AKOrt, KS, Anne, Baba, Ekonomik) carry no labels, and "Cinsiyet"
#   (gender) holds five codes, so their coding cannot be read from the deposit.
#
# Item text: not shipped. Levels checked: both files have no variable labels and
#   no value labels. The AI scale's Turkish items are the article's Appendix I
#   (article CC BY-NC-ND -- ND makes it a rights question); SWLS/SGWB wording is
#   in the cited adaptations.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "atik"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"efa": 10797848, "cfa": 10797849}

TABLES = {
    "atik_2025_ai_life_satisfaction": ([f"B{i}" for i in range(1, 6)], range(1, 8)),
    "atik_2025_swls": ([f"A{i}" for i in range(1, 6)], range(1, 6)),
    "atik_2025_gwb": ([f"C{i}" for i in range(1, 15)], range(1, 6)),
}


def fetch(sample: str) -> Path:
    p = RAW_DIR / f"{sample}.orig"
    if not p.exists():
        r = requests.get(f"https://dataverse.harvard.edu/api/access/datafile/{FILES[sample]}"
                         "?format=original", headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    parts = []
    for s, n in (("efa", 503), ("cfa", 301)):
        d, _ = pyreadstat.read_sav(str(fetch(s)))
        assert d.shape == (n, 34), d.shape
        assert d["ÖlçekNo"].is_unique
        d["id"] = s + "_" + d["ÖlçekNo"].astype(int).astype(str)
        d["cov_sample"] = s
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    assert d["id"].is_unique
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id", "cov_sample"], value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        bad = ~t["resp"].isin(list(rng))
        if bad.any():
            print(f"  {name}: dropped {bad.sum()} out-of-set cells: "
                  f"{t.loc[bad].groupby(['item', 'resp']).size().to_dict()}")
            assert bad.sum() <= 20
            t = t[~bad]
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp", "cov_sample"]].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
