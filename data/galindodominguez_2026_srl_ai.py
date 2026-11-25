#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/FDVOTW
# DOI: 10.7910/DVN/FDVOTW (data)
#   Galindo Dominguez H (2026). The Gap Between What Students Say and Do: Unpacking Self-Regulation and Delegation in Artificial Intelligence Assisted Learning [Data set]. Dataverse. https://doi.org/10.7910/DVN/FDVOTW
# License: CC0 1.0 (record metadata)
# Data: 'Main DataBase.sav', 130 Basque education students (University of the Basque Country); id = row order. Variable labels
#   carry the Basque stems tagged [PLN]/[SMT]/[EVA]/[RFL]/[EFT]/[OVR]; items 1-5. Prompt-log codings are counts, not items.
# SMT11 is not shipped: its stored values run to 10 on a 1-5 scale.
# One age of 1 set missing.
# Covariates: faculty, age, gender.
# Dropped: prompt-log counts/ratios, scale totals, participation flag.
# PII: none.
# Item text: Basque stems in the .sav variable labels (cheap later build).
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://dataverse.harvard.edu/api/access/datafile/14466614?format=original'
N_ROWS = 130
ID_COL = None
COVS = {'ZureFakultatea': 'cov_faculty', 'Edad': 'cov_age', 'Género': 'cov_gender'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'galindodominguez_2026_planning': ['PLN1.Arazobatkonpontzekomoduaerabakitzenduthasiaurretik',
                                    'PLN2.Jarraitubehardudanplanarenurratsakburuanberrikustenditut',
                                    'PLN4.Arazobatekinsartubainolehennireburuarigaldetzendiothonekzer',
                                    'PLN5.Osatzekogeratzenzaizkidanarazobatenatalakirudikatzenditut',
                                    'PLN6.Arretazplanifikatzendutarazobatkonpontzekojarraitukodudanja',
                                    'PLN7.Nirehelburuaketahorieklortzekozereginbehardudanzehaztenditu',
                                    'PLN8.Argiplanifikatzendutarazobatkonpontzekojarraitukoditudanpau',
                                    'PLN9.Arazobatenkonponbiderakoplanbatgaratzendut'],
 'galindodominguez_2026_self_monitoring': ['SMT12.Lanaegitenarinaizenbitarteanegitenarinaizenaegiaztatzendut',
                                           'SMT13.Zereginbategitenarinaizeneannireburuarigaldetzendiotnolaar',
                                           'SMT15.Nireakatsakkonpontzenditut',
                                           'SMT16.Eginkizuneanaurreraeginahalanirezuzentasunaegiaztatzendut',
                                           'SMT17.Nirelanarenzuzentasunaepaitzendut'],
 'galindodominguez_2026_evaluation': ['EVA18.Atzerabegiratzendutetaegindakoazuzenaizandenalaezegiaztatz',
                                      'EVA19.Berriroegiaztatzendutdenaondoegindudalaziurtatzeko',
                                      'EVA20.Nirekalkuluakzuzenakdirenegiaztatzendut',
                                      'EVA21.Atzerabegiratzendutprozeduraegokiakjarraituditudanikusteko',
                                      'EVA22.Arazoosoanzeharnirelanaegiaztatzendut',
                                      'EVA23.Arazoabegiratzendutnireerantzunakzentzudunakdirenikusteko',
                                      'EVA24.Beharrezkoadeneangelditzennaizetadagoenekoegindakourratsba',
                                      'EVA25.Pausuguztiakbeteditudalaziurtatzennaiz'],
 'galindodominguez_2026_reflection': ['RFL26.Nireesperientziakberrizaztertzendituthaietatikikasteko',
                                      'RFL27.Nireindarguneetanetaahulguneetanpentsatzensaiatzennaiz',
                                      'RFL28.Nireekintzetanpentsatzendutikustekonolahobetuditzakedan',
                                      'RFL29.Iraganekoesperientzietanpentsatzendutideiaberriakulertzeko',
                                      'RFL30.Hurrengoangauzakhobetonolaeginditzakedanpentsatzensaiatzen'],
 'galindodominguez_2026_effort': ['EFT31.Zereginzailetanerelaneanjarraitzendut',
                                  'EFT32.Nireahaleginikonenaegitendutzereginakegitean',
                                  'EFT33.Erabatkontzentratzennaizzereginbategitendudanean',
                                  'EFT34.Nahizetazereginazailaizanezdutamoreematen',
                                  'EFT35.Zereginbateangogoregitendutlangarrantzitsuaezizanarren',
                                  'EFT36.Ahaliketagogorrenlanegitendutzereginguztietan',
                                  'EFT37.Zereginakondoegitekogogoregitenduthaugustukoezbadutere',
                                  'EFT38.Zereginbateanosoonaeznaizeneangogorlaneginezkonpentsadezak',
                                  'EFT39.Zereginbatieustendiodaneanazkeneanarrakastaizangodut',
                                  'EFT40.Prestnagozereginetanlangehiagoegitekogehiagoikastekoasmoz'],
 'galindodominguez_2026_overreliance': ['OVR07.IazereginguztiakAdimenArtifizialaridelegatzendizkiotnibain',
                                        'OVR09.AdimenArtifizialarenfuntzioetankonfidantzadaukatadibidezer',
                                        'OVR10.EzinditutjadazereginakademikokonplexuakkudeatuAdimenArtifi',
                                        'OVR11.NikbakarrikeginbeharreannahiagodutAdimenArtifizialarideleg',
                                        'OVR12.NireikasketetangehiegizkokonfidantzadutAdimenArtifizialake',
                                        'OVR13.DesegokisentitzennaiznireikasketetanAdimenArtifizialarenla',
                                        'OVR14.SarritanzuzeneanAdimenArtifizialarieskatzendizkioterantzun',
                                        'OVR15.Adimenartifizialaerabiliondorennireabileziamoduautonomoana',
                                        'OVR16.ErronkaakademikobatenaurreannagoeneanAdimenArtifizialazgeh',
                                        'OVR17.AdimenArtifizialaepeluzeanerabiliondorenmentalkialferbihur',
                                        'OVR18.AdimenArtifizialaknireordezbalorazioaketaerabakiakhartzera']}
# (lo, hi) response range per table
RANGES = {'galindodominguez_2026_planning': (1, 5),
 'galindodominguez_2026_self_monitoring': (1, 5),
 'galindodominguez_2026_evaluation': (1, 5),
 'galindodominguez_2026_reflection': (1, 5),
 'galindodominguez_2026_effort': (1, 5),
 'galindodominguez_2026_overreliance': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'¿Participacion': 'participation flag / filter',
 'SMT11.Zereginbategitenarinaizeneannirejardunanolakoadenegiaztatz': 'self-monitoring item stored on a different '
                                                                     'range (119 of 130 values above 5); not shipped',
 'Numero_prompts': 'prompt-log count, ratio or scale total',
 'Totalcategories_codified': 'prompt-log count, ratio or scale total',
 'Planning_prompts': 'prompt-log count, ratio or scale total',
 'InformationSeeking_prompts': 'prompt-log count, ratio or scale total',
 'Monitoring_prompts': 'prompt-log count, ratio or scale total',
 'Evaluation_Prompts': 'prompt-log count, ratio or scale total',
 'Revision_Prompts': 'prompt-log count, ratio or scale total',
 'Reflection_Prompts': 'prompt-log count, ratio or scale total',
 'Delegation_Prompts': 'prompt-log count, ratio or scale total',
 'SRL_Density': 'prompt-log count, ratio or scale total',
 'DelegationRatio': 'prompt-log count, ratio or scale total',
 'Balance': 'prompt-log count, ratio or scale total',
 'SRL_Coverage': 'prompt-log count, ratio or scale total',
 'Tasks_Mark': 'prompt-log count, ratio or scale total',
 'filter_$': 'participation flag / filter',
 'PLN_TT': 'prompt-log count, ratio or scale total',
 'SMT_TT': 'prompt-log count, ratio or scale total',
 'EVA_TT': 'prompt-log count, ratio or scale total',
 'RFL_TT': 'prompt-log count, ratio or scale total',
 'EFT_TT': 'prompt-log count, ratio or scale total',
 'SRL_TT': 'prompt-log count, ratio or scale total',
 'SRL_Prompts_TT': 'prompt-log count, ratio or scale total',
 'OVR_FD_TT': 'prompt-log count, ratio or scale total',
 'OVR_CD_TT': 'prompt-log count, ratio or scale total',
 'OVR_TT': 'prompt-log count, ratio or scale total',
 'Planning_prompts_perc': 'prompt-log count, ratio or scale total',
 'infseek_prompts_perc': 'prompt-log count, ratio or scale total',
 'Monitoring_prompts_perc': 'prompt-log count, ratio or scale total',
 'Evaluation_prompts_perc': 'prompt-log count, ratio or scale total',
 'Revision_prompts_perc': 'prompt-log count, ratio or scale total',
 'Reflection_prompts_perc': 'prompt-log count, ratio or scale total',
 'Delegation_prompts_perc': 'prompt-log count, ratio or scale total'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d.loc[d["Edad"] < 15, "Edad"] = np.nan   # one age of 1
    d["ZureFakultatea"] = d["ZureFakultatea"].map(slug)
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
