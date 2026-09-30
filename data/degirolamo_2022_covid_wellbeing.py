#!/usr/bin/env python3
# Source: https://doi.org/10.5281/zenodo.5040719
# DOI: 10.1038/s41598-022-22994-4
#   de Girolamo G, Ferrari C, Candini V, Buizza C, Calamandrei G, Caserotti M,
#   Gavaruzzi T, Girardi P, Habersaat KB, Lotto L, Scherzer M, Starace F,
#   Tasso A, Zamparini M, Zarbo C (2022). "Psychological well-being during the
#   COVID-19 pandemic in Italy assessed in a four-waves survey." Scientific
#   Reports 12, 17945.
# Data: Zenodo 5040719, Valide_DATA_1W.csv .. Valide_DATA_4W.csv (';'-separated,
#   ',' decimals). The Italian arm of the WHO/Europe COVID-19 behavioural
#   insights survey (COSMO), fielded online to a quota sample of adults 18-70,
#   January, February, March and May 2021. Variable and value labels from
#   WaveN_DICTIONARY.xls in the same record.
# License: CC BY 4.0 (Zenodo record licence). The paper's statement adds "Data
#   should be requested to the first author", but the deposit is public under
#   CC BY; the deposit's licence governs.
#
# FOUR INDEPENDENT SAMPLES, NOT A PANEL. The paper: "Each wave surveyed
#   different individuals" (2504 + 2502 + 2507 + 2500 = 10,013, its N).
#   responseid restarts in each file, and the same number in two waves is two
#   different people (1,783 wave-1 ids recur in wave 2 by coincidence). So:
#   id = "w<wave>_<responseid>", and the wave is cov_survey_wave, not `wave`
#   (datastandard: `wave` means the same focal unit measured again).
#   `date` is the interview day (interview_start, e.g. "08-gen-21"), as Unix
#   seconds at 00:00 UTC.
#
# Tables (item codes are the source column names):
#   degirolamo_2022_who5   WHO-5 Well-Being Index, 5 items (pag20_1_1..5),
#                          stored 1-6 as deposited: 1 = "Tutto il tempo"
#                          (all of the time) .. 6 = "In nessun momento" (at no
#                          time). REVERSED and shifted against standard WHO-5
#                          scoring (0 = at no time .. 5 = all of the time), so
#                          a high resp is LOW well-being. Not recoded; see
#                          metadata/data_notes.csv.
#   degirolamo_2022_brs    Brief Resilience Scale, the 3 items the survey
#                          carried (pag15_1_1..3), rated 1 (molto in
#                          disaccordo) to 7 (molto d'accordo) -- 7 points, not
#                          the BRS's 5. pag15_1_1 = BRS 2 "I have a hard time
#                          making it through stressful events" (negative),
#                          pag15_1_2 = BRS 3 "It does not take me long to
#                          recover from a stressful event" (positive),
#                          pag15_1_3 = BRS 4 "It is hard for me to snap back
#                          when something bad happens" (negative).
#                          Unreversed.
#   The paper calls the resilience measure "three items of the five that
#   compose the Brief Resilience Scale"; the BRS has six. Either way these
#   are 3 of them.
#
# Item text: not shipped. WHO-5 is `block` in
#   itemtext/instrument_rights_register.csv (WHO, CC BY-NC-SA 3.0 IGO, item
#   text withdrawn 2026-09-08); the source item codes are kept, so the
#   register's ^who5 item-code pattern does not fire. BRS is not in the
#   register.
#
# No missing responses on either block in any wave (checked below). All
#   10,013 respondents are kept.
# Covariates, identical coding in all four dictionaries:
#   cov_weight          peso, the survey's post-stratification weight
#   cov_age             pag2_2, years (18-70)
#   cov_sex             pag2_3: 1 male, 2 female
#   cov_education       pag2_4: 1 0-8 yrs, 2 9-13 yrs, 3 more than 13 yrs
#   cov_region          pag2_9: 1-20, the Italian regions (1 Piemonte ..
#                       20 Sardegna, in the dictionary's order)
#   cov_urban           pag2_8: 1 rural (<= 100,000 inhabitants), 2 urban
#   cov_employed        pag2_5: 1 yes, 2 no
#   cov_health_worker   pag2_6: 1 yes, 2 no; asked only of the employed, so
#                       missing exactly when cov_employed = 2 (asserted; wave
#                       1 codes the skip "#NULL!", waves 2-4 leave it blank)
#   cov_chronic_illness pag2_7: 1 yes, 2 no, 3 don't know
#   cov_survey_wave     1-4 (Jan, Feb, Mar, May 2021); separate samples

import io
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/records/5040719/files/Valide_DATA_{w}W.csv?download=1"
N_ROWS = {1: 2504, 2: 2502, 3: 2507, 4: 2500}

TABLES = {
    "degirolamo_2022_who5": ([f"pag20_1_{i}" for i in range(1, 6)],
                             range(1, 7)),
    "degirolamo_2022_brs": ([f"pag15_1_{i}" for i in range(1, 4)],
                            range(1, 8)),
}

COVS = {"peso": "cov_weight", "pag2_2": "cov_age", "pag2_3": "cov_sex",
        "pag2_4": "cov_education", "pag2_9": "cov_region",
        "pag2_8": "cov_urban", "pag2_5": "cov_employed",
        "pag2_6": "cov_health_worker", "pag2_7": "cov_chronic_illness"}
COV_RANGES = {"cov_age": range(18, 71), "cov_sex": range(1, 3),
              "cov_education": range(1, 4), "cov_region": range(1, 21),
              "cov_urban": range(1, 3), "cov_employed": range(1, 3),
              "cov_chronic_illness": range(1, 4)}

MONTHS = {"gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
          "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12}


def unix_day(s: str) -> int:
    day, mon, yy = s.split("-")
    dt = datetime(2000 + int(yy), MONTHS[mon], int(day), tzinfo=timezone.utc)
    return int(dt.timestamp())


def load_wave(w: int) -> pd.DataFrame:
    r = requests.get(URL.format(w=w), headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), sep=";", decimal=",",
                    encoding="utf-8-sig", dtype=str)
    assert len(d) == N_ROWS[w], (w, len(d))
    assert d["responseid"].is_unique
    d.insert(0, "id", "w" + str(w) + "_" + d["responseid"])
    d["cov_survey_wave"] = w
    d["date"] = d["interview_start"].map(unix_day)
    return d


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.concat([load_wave(w) for w in N_ROWS], ignore_index=True)
    assert len(d) == 10013 and d["id"].is_unique

    d = d.rename(columns=COVS)
    d["cov_weight"] = d["cov_weight"].str.replace(",", ".").astype(float)
    for c, allowed in COV_RANGES.items():
        d[c] = d[c].astype(int)
        assert d[c].isin(allowed).all(), c
    hw = d["cov_health_worker"].replace("#NULL!", pd.NA)
    assert (hw.isna() == (d["cov_employed"] == 2)).all()
    assert hw.dropna().isin(["1", "2"]).all()
    d["cov_health_worker"] = hw.astype("Int64")
    cov_cols = list(COVS.values()) + ["cov_survey_wave"]

    # The four fieldwork windows do not overlap, in wave order.
    spans = d.groupby("cov_survey_wave")["date"].agg(["min", "max"])
    assert (spans["min"].shift(-1).dropna() > spans["max"].iloc[:-1]).all()

    for table, (items, allowed) in TABLES.items():
        assert d[items].notna().all().all(), table
        long = d.melt(id_vars=["id", "date"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp", "date"] + cov_cols]
        long = long.sort_values(["cov_survey_wave", "id", "item"]) \
            .reset_index(drop=True)
        assert len(long) == 10013 * len(items)
        assert not long.duplicated(["id", "item"]).any()
        pv = {i: set(allowed) for i in items}
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


if __name__ == "__main__":
    convert()
