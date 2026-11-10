#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9070319
# DOI: 10.7717/peerj.13288
#   "Stress coping strategies used by nurses during the COVID-19 pandemic"
#   (Sierakowska et al., 2022), PeerJ 10:e13288.
# Data: the article's supplementary file peerj-10-13288-s001.xlsx (Europe PMC
#   supplementaryFiles zip), first sheet: 223 rows x 159 columns, one row per
#   online-survey submission (Dec 2020 - Jan 2021). Responses are stored as
#   text labels with a leading code ("2 = często tak postępuję", "3 – raczej
#   tak"); a few cells carry the English translation of the same label. The
#   code is the leading digit. The Polish-header columns at the right are empty
#   duplicates of the English-header columns and are not read.
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: rows 0-2 hold demographics only (no scale responses), leaving 220
#   nurses, the paper's n = 220 (96.4% women; here 212 women, 8 men).
#   id = row index (the only per-row key is a submission timestamp, not shipped).
#
# Tables (paper Methods: GSES 10-40, Mini-COPE 0-3, PSS-10 0-40):
#   sierakowska_2022_minicope  cope_1..cope_28  0-3  Mini-COPE (Polish Brief COPE,
#       Juczynski & Oginska-Bulik): 0 = I hardly ever do this .. 3 = I almost always
#   sierakowska_2022_pss10     pss_1..pss_10    0-4  Perceived Stress Scale:
#       0 = never .. 4 = very often
#   sierakowska_2022_gses      gses_1..gses_10  1-4  Generalized Self-Efficacy
#       Scale (Polish GSES): 1 = no .. 4 = yes
#   Item numbers are the questionnaire's own, read from each header's leading
#   number ("2. When I am in a very difficult situation ..."); the one COPE header
#   without a number ("When I am ... solace in religion") sits between 21 and 23
#   and is the Brief COPE's religion item 22. Item 1 of COPE and of GSES sit
#   apart from the rest of their blocks in the sheet; their headers identify them.
#   Responses are kept as administered (no reverse-coding).
#
# Covariates: age, sex, place of residence, nursing role ("8. Workplace"),
#   education, self-rated health (1-5), feeling of workplace safety (1-5),
#   peer-support atmosphere (1-5). Free-text work-experience/hours columns and the
#   timestamp are not carried.
#
# Item text: not shipped. Levels checked: xlsx headers carry an English rendering
#   of each stem (the administered Polish stems are the headers of the empty
#   right-hand columns); no value labels beyond the inline anchors. The Mini-COPE
#   and Polish GSES/PSS-10 are published adaptations (PTP test lab); English
#   headers are the authors' back-translation, not the administered wording.

import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "sierakowska_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9070319/supplementaryFiles"
FILE = "peerj-10-13288-s001.xlsx"


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


def lead_num(h: str):
    m = re.match(r"\s*(\d+)\.", h)
    return int(m.group(1)) if m else None


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name=0)
    assert d.shape == (223, 159), d.shape
    cols = list(d.columns)
    english = cols[:88]  # the Polish-header duplicates start at column 89
    assert all(d[c].isna().all() for c in cols[89:]), "Polish-header columns not empty"

    cope, pss, gses = {}, {}, {}
    for c in english:
        h = str(c)
        if "When I am in a very difficult situation" in h or "When I'm in a very difficult" in h:
            n = 1 if h.startswith("1. 1.") else lead_num(h)
            if n is None:
                assert "religion" in h
                n = 22
            cope[n] = c
        elif re.search(r"(past|last) month, how often", h, re.I) or "How often in the last month" in h:
            pss[lead_num(h)] = c
        elif re.match(r"\s*\d+\.\s*(I |If someone|It's easy|Thanks to|When I struggle|When I am in a difficult|No matter)", h):
            gses[lead_num(h)] = c
    assert sorted(cope) == list(range(1, 29)), sorted(cope)
    assert sorted(pss) == list(range(1, 11)), sorted(pss)
    assert sorted(gses) == list(range(1, 11)), sorted(gses)

    blocks = {
        "sierakowska_2022_minicope": ("cope", cope, {0, 1, 2, 3}),
        "sierakowska_2022_pss10": ("pss", pss, {0, 1, 2, 3, 4}),
        "sierakowska_2022_gses": ("gses", gses, {1, 2, 3, 4}),
    }
    all_items = [c for _, m, _ in blocks.values() for c in m.values()]
    has = d[all_items].notna().any(axis=1)
    assert has.sum() == 220 and not has.iloc[:3].any()
    d = d[has].reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    covs = {
        "1.Age": "cov_age",
        "2. Sex": "cov_sex",
        "3. The place where you live": "cov_residence",
        "8. Workplace": "cov_role",
        "5. Education": "cov_education",
        "17. How do you rate your health - choose a value on a scale from 1 to 5": "cov_health_self",
        "15. How safe do you feel in your workplace? - select a value on a scale from 1 to 5": "cov_work_safety",
    }
    peer = [c for c in english if str(c).startswith("16. How do you evaluate the atmosphere")]
    assert len(peer) == 1
    covs[peer[0]] = "cov_peer_support"
    cv = d[["id"] + list(covs)].rename(columns=covs)
    for c in ["cov_sex", "cov_residence", "cov_role", "cov_education"]:
        cv[c] = cv[c].astype("string").str.strip().str.lower()
    assert (cv["cov_sex"] == "woman").sum() == 212

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (prefix, m, pv_set) in blocks.items():
        parts = []
        for n, c in sorted(m.items()):
            raw = d[c].astype("string").str.strip()
            code = raw.str.extract(r"^(\d)\s*[=–-]")[0]
            bad = raw.notna() & code.isna()
            assert not bad.any(), (name, c, raw[bad].unique()[:5])
            parts.append(pd.DataFrame({"id": d["id"], "item": f"{prefix}_{n}",
                                       "resp": pd.to_numeric(code)}))
        t = pd.concat(parts).dropna(subset=["resp"]).merge(cv, on="id", how="left")
        t["resp"] = t["resp"].astype(int)
        items = [f"{prefix}_{n}" for n in sorted(m)]
        assert set(t["resp"]) <= pv_set, (name, set(t["resp"]))
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: pv_set for i in items}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
