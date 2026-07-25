from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

# Source (raw data): https://gitlab.com/a-bc/your-covid-19-risk-data
# Source (site/code): https://gitlab.com/a-bc/your-covid-19-risk
# Paper: Peters, Kwasnicka, ten Hoor et al. (2025), "Collecting behavioural
# data across countries during pandemics: Development of the COVID-19 Risk
# Assessment Tool", Behav Res 57, 223. https://doi.org/10.3758/s13428-025-02743-x
# GitHub issue: https://github.com/ben-domingue/irw/issues/1093
#
# License: the data repo's README states R scripts are CC0, and ".csv data
# sets... are anonymized, and as such, defined as facts and existing in the
# public domain by definition" -- the aspirational "CC-BY-NC-SA" mentioned
# elsewhere in that README applies to the site/branding, not the data files.
#
# STRUCTURE: this is a LimeSurvey deployment split into 50 raw export files
# across 21 survey IDs (sids) -- confirmed empirically that all 21 sids share
# (almost) the same ~577-585 column schema, i.e. this is ONE instrument
# fielded across ~21 countries/languages, not 21 different item sets. Also
# confirmed the raw "id" column is only unique WITHIN a sid (resets to 1 for
# every sid), so a global id is built as f"{sid}-{orig_id}".
#
# ITEM MAPPING: the bulk of the survey (276 of ~585 columns) is built from a
# Reasoned Action Approach (RAA) belief-item mechanism, documented in the
# project's own rendered build script at
# https://your-risk.com/v1-translation-results-limesurvey (their R Markdown
# source for generating the LimeSurvey import file). Each belief statement is
# three raw columns:
#   <Item>Seq   -- the item's randomization-order slot within its array
#                  question. NOT a response (empirically confirmed: holds
#                  arbitrary integers like the position 10-155, not a scale
#                  value) -- excluded entirely.
#   <Item>Ex... -- "expectancy": belief strength
#   <Item>Ev... -- "evaluation": belief evaluation
# (norms and PBC families reuse the same mechanism with different component
# names -- see FAMILIES below.) Each item is scored on one of two scales,
# per the answer-option code found in that same build script:
#   "uni" (unipolar): valid codes 1-5
#   "bi"  (bipolar):  valid codes 1-7
#   code 0 in both cases = "don't know/NA" -- a non-response sentinel that
#   sits inside what would otherwise look like a valid numeric range, per
#   datastandard.md's sentinel-filtering guidance. Confirmed empirically:
#   NrmDeIdFamily (bi) has real 0.0 values in the raw data.
#
# Ex and Ev are different psychological dimensions of the same belief
# statement (not the same scale answered twice), so each family is split
# into two separate output tables, one per component -- confirmed with the
# user rather than assumed.
#
# NOT covered by this script: demographic/intake covariates are included as
# cov_*, but the ~300 remaining raw columns (risk-estimate/checkbox-array
# items like siCurrent*/siIntention*/hwFrequency*/work*/DMQslider* and their
# paired *Est columns) use a different, not-yet-decoded response mechanism
# and are left for a follow-up pass -- see automated_finding/TODO.md.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

RAW_BASE = "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FILES = [
    "YCR-dataPipeline--sid-100101--rids-1-4849.csv",
    "YCR-dataPipeline--sid-100101--rids-14548-19396.csv",
    "YCR-dataPipeline--sid-100101--rids-19397-24245.csv",
    "YCR-dataPipeline--sid-100101--rids-24246-29094.csv",
    "YCR-dataPipeline--sid-100101--rids-29095-33943.csv",
    "YCR-dataPipeline--sid-100101--rids-33944-38790.csv",
    "YCR-dataPipeline--sid-100101--rids-4850-9698.csv",
    "YCR-dataPipeline--sid-100101--rids-9699-14547.csv",
    "YCR-dataPipeline--sid-100102--rids-1-141.csv",
    "YCR-dataPipeline--sid-100103--rids-1-1479.csv",
    "YCR-dataPipeline--sid-100104--rids-1-254.csv",
    "YCR-dataPipeline--sid-100104--rids-1286-2448.csv",
    "YCR-dataPipeline--sid-100104--rids-255-1285.csv",
    "YCR-dataPipeline--sid-100105--rids-1-2450.csv",
    "YCR-dataPipeline--sid-100105--rids-2451-3888.csv",
    "YCR-dataPipeline--sid-100106--rids-1-439.csv",
    "YCR-dataPipeline--sid-100107--rids-1-455.csv",
    "YCR-dataPipeline--sid-100108--rids-1-586.csv",
    "YCR-dataPipeline--sid-100109--rids-1-162.csv",
    "YCR-dataPipeline--sid-100110--rids-1-2583.csv",
    "YCR-dataPipeline--sid-100110--rids-13027-13135.csv",
    "YCR-dataPipeline--sid-100110--rids-2584-5166.csv",
    "YCR-dataPipeline--sid-100110--rids-5167-9096.csv",
    "YCR-dataPipeline--sid-100110--rids-9097-13026.csv",
    "YCR-dataPipeline--sid-100111--rids-1-3616.csv",
    "YCR-dataPipeline--sid-100111--rids-11542-11662.csv",
    "YCR-dataPipeline--sid-100111--rids-3617-7231.csv",
    "YCR-dataPipeline--sid-100111--rids-7232-11541.csv",
    "YCR-dataPipeline--sid-100112--rids-1-225.csv",
    "YCR-dataPipeline--sid-100113--rids-1-915.csv",
    "YCR-dataPipeline--sid-100114--rids-1-2227.csv",
    "YCR-dataPipeline--sid-100115--rids-1-1374.csv",
    "YCR-dataPipeline--sid-100116--rids-1-2035.csv",
    "YCR-dataPipeline--sid-100116--rids-2036-2170.csv",
    "YCR-dataPipeline--sid-100117--rids-1-2034.csv",
    "YCR-dataPipeline--sid-100117--rids-2035-2625.csv",
    "YCR-dataPipeline--sid-100117--rids-2626-4138.csv",
    "YCR-dataPipeline--sid-100117--rids-4139-4246.csv",
    "YCR-dataPipeline--sid-100118--rids-1-560.csv",
    "YCR-dataPipeline--sid-100119--rids-1-1337.csv",
    "YCR-dataPipeline--sid-100120--rids-1-307.csv",
    "YCR-dataPipeline--sid-100121--rids-1-783.csv",
    "YCR-dataPipeline--sid-100121--rids-12635-16197.csv",
    "YCR-dataPipeline--sid-100121--rids-16198-16374.csv",
    "YCR-dataPipeline--sid-100121--rids-1815-3144.csv",
    "YCR-dataPipeline--sid-100121--rids-3145-4111.csv",
    "YCR-dataPipeline--sid-100121--rids-4112-4450.csv",
    "YCR-dataPipeline--sid-100121--rids-4451-8542.csv",
    "YCR-dataPipeline--sid-100121--rids-784-1814.csv",
    "YCR-dataPipeline--sid-100121--rids-8543-12634.csv",
]

# Raw question code -> answer-scale polarity, extracted from the project's
# own LimeSurvey-generation build script (see module docstring above).
ITEM_POLARITY = {
    "AtInEvLoseRespect": "bi", "AtInEvWasteTime": "bi",
    "AtInExLoseRespect": "bi", "AtInExWasteTime": "bi",
    "AttExEvAltruistic": "bi", "AttExEvComfort": "bi", "AttExEvConnected": "bi",
    "AttExEvEmbarr": "bi", "AttExEvFreakedOut": "bi", "AttExEvGood": "bi",
    "AttExEvInControl": "bi", "AttExEvLeftOut": "bi", "AttExEvLonely": "bi",
    "AttExEvSafe": "bi", "AttExEvSilly": "bi", "AttExEvSocResp": "bi",
    "AttExEvThreatened": "bi", "AttExEvUpset": "bi", "AttExEvVulnerable": "bi",
    "AttExEvWeird": "uni",
    "AttExExAltruistic": "bi", "AttExExComfort": "bi", "AttExExConnected": "bi",
    "AttExExEmbarr": "bi", "AttExExFreakedOut": "bi", "AttExExGood": "bi",
    "AttExExInControl": "bi", "AttExExLeftOut": "bi", "AttExExLonely": "bi",
    "AttExExSafe": "bi", "AttExExSilly": "bi", "AttExExSocResp": "bi",
    "AttExExThreatened": "bi", "AttExExUpset": "bi", "AttExExVulnerable": "bi",
    "AttExExWeird": "uni",
    "AttInEvActEasy": "bi", "AttInEvApprop": "uni", "AttInEvBi": "bi",
    "AttInEvBiFl": "bi", "AttInEvChildFeel": "bi", "AttInEvChildReject": "bi",
    "AttInEvCitizen": "bi", "AttInEvContactFam": "bi", "AttInEvCoward": "bi",
    "AttInEvDiscon": "bi", "AttInEvFamInf": "uni", "AttInEvFamRelax": "bi",
    "AttInEvFamilyHappy": "bi", "AttInEvFamilySafe": "bi", "AttInEvFined": "uni",
    "AttInEvFriendsHappy": "bi", "AttInEvFriendsInf": "uni",
    "AttInEvFriendsRelax": "bi", "AttInEvHealth": "bi", "AttInEvHouse": "uni",
    "AttInEvHybridUni": "uni", "AttInEvHybridUniFl": "uni",
    "AttInEvImplComp": "bi", "AttInEvImplCompFl": "bi", "AttInEvInApprop": "bi",
    "AttInEvInfFamLong": "uni", "AttInEvInfFamShort": "uni",
    "AttInEvInfFrieLong": "uni", "AttInEvInfFrieShort": "uni",
    "AttInEvInfNeigh": "uni", "AttInEvInfPeople": "uni", "AttInEvInfPop": "uni",
    "AttInEvInformRspns": "bi", "AttInEvLeftOut": "bi", "AttInEvNeglRspns": "bi",
    "AttInEvOthCool": "bi", "AttInEvOthCrazy": "uni", "AttInEvOthDist": "bi",
    "AttInEvOthHappy": "bi", "AttInEvOthJudge": "bi", "AttInEvOthOffend": "bi",
    "AttInEvOthThinkInf": "uni", "AttInEvOthUpset": "bi",
    "AttInEvOtherInf": "uni", "AttInEvOutsideInf": "bi",
    "AttInEvProfRspns": "bi", "AttInEvReasBi": "bi", "AttInEvReasBiFl": "bi",
    "AttInEvReasUni": "uni", "AttInEvReasUniFl": "uni", "AttInEvSocEasy": "bi",
    "AttInEvTradFl": "uni", "AttInEvTradUni": "uni", "AttInEvUni": "uni",
    "AttInEvUniFl": "uni", "AttInEvWeak": "bi",
    "AttInExActEasy": "bi", "AttInExApprop": "uni", "AttInExBi": "bi",
    "AttInExBiFl": "bi", "AttInExChildFeel": "bi", "AttInExChildReject": "bi",
    "AttInExCitizen": "bi", "AttInExContactFam": "bi", "AttInExCoward": "bi",
    "AttInExDiscon": "bi", "AttInExFamInf": "uni", "AttInExFamRelax": "bi",
    "AttInExFamilyHappy": "bi", "AttInExFamilySafe": "bi", "AttInExFined": "uni",
    "AttInExFriendsHappy": "bi", "AttInExFriendsInf": "uni",
    "AttInExFriendsRelax": "bi", "AttInExHealth": "bi", "AttInExHouse": "uni",
    "AttInExHybridUni": "uni", "AttInExHybridUniFl": "uni",
    "AttInExImplComp": "bi", "AttInExImplCompFl": "bi", "AttInExInApprop": "bi",
    "AttInExInfFamLong": "uni", "AttInExInfFamShort": "uni",
    "AttInExInfFrieLong": "uni", "AttInExInfFrieShort": "uni",
    "AttInExInfNeigh": "uni", "AttInExInfPeople": "uni", "AttInExInfPop": "uni",
    "AttInExInformRspns": "bi", "AttInExLeftOut": "bi", "AttInExNeglRspns": "bi",
    "AttInExOthCool": "bi", "AttInExOthCrazy": "uni", "AttInExOthDist": "bi",
    "AttInExOthHappy": "bi", "AttInExOthJudge": "bi", "AttInExOthOffend": "bi",
    "AttInExOthThinkInf": "uni", "AttInExOthUpset": "bi",
    "AttInExOtherInf": "uni", "AttInExOutsideInf": "bi",
    "AttInExProfRspns": "bi", "AttInExReasBi": "bi", "AttInExReasBiFl": "bi",
    "AttInExReasUni": "uni", "AttInExReasUniFl": "uni", "AttInExSocEasy": "bi",
    "AttInExTradFl": "uni", "AttInExTradUni": "uni", "AttInExUni": "uni",
    "AttInExUniFl": "uni", "AttInExWeak": "bi",
    "CIBERliteAttExp": "bi", "CIBERliteAttIns": "bi", "CIBERliteInt": "uni",
    "CIBERlitePbcAut": "uni", "CIBERlitePbcCap1": "uni",
    "CIBERlitePbcCap2": "uni", "CIBERlitePnDes": "uni", "CIBERlitePnInj": "bi",
    "GenEvDie": "uni", "GenEvHospital": "uni", "GenEvSymptoms": "uni",
    "GenExDie": "uni", "GenExHospital": "uni", "GenExSymptoms": "uni",
    "NrmDeBehDoctor": "uni", "NrmDeBehFamily": "uni", "NrmDeBehFriends": "uni",
    "NrmDeBehGeneral": "uni", "NrmDeBehLikeYou": "uni", "NrmDeBehNeighb": "uni",
    "NrmDeBehOther": "uni", "NrmDeBehRole": "uni",
    "NrmDeIdDoctor": "bi", "NrmDeIdFamily": "bi", "NrmDeIdFriends": "bi",
    "NrmDeIdLikeGeneral": "bi", "NrmDeIdLikeNeighb": "bi",
    "NrmDeIdLikeYou": "bi", "NrmDeIdOther": "bi", "NrmDeIdRole": "bi",
    "NrmInApBoss": "bi", "NrmInApColleagues": "bi", "NrmInApDoctor": "bi",
    "NrmInApFamily": "bi", "NrmInApFriends": "bi", "NrmInApGeneral": "bi",
    "NrmInApGovernment": "bi", "NrmInApHousehold": "bi", "NrmInApLikeMe": "bi",
    "NrmInApNeighbrhd": "bi",
    "NrmInMcBoss": "uni", "NrmInMcColleagues": "uni", "NrmInMcDoctor": "uni",
    "NrmInMcFamily": "uni", "NrmInMcFriends": "uni", "NrmInMcGeneral": "uni",
    "NrmInMcGovernment": "uni", "NrmInMcHousehold": "uni",
    "NrmInMcLikeMe": "uni", "NrmInMcNeighbrhd": "uni",
    "PbcCnPrBored": "uni", "PbcCnPrBusyPlace": "uni", "PbcCnPrDistrac": "uni",
    "PbcCnPrEnoughRoom": "uni", "PbcCnPrForgExer": "uni",
    "PbcCnPrForget": "uni", "PbcCnPrLonely": "uni", "PbcCnPrLotMind": "uni",
    "PbcCnPrNormClose": "uni", "PbcCnPrOthAppr": "uni",
    "PbcCnPrOthDist": "uni", "PbcCnPrPayAtt": "uni", "PbcCnPrShopping": "uni",
    "PbcCnPrSignposts": "uni", "PbcCnPrSitClose": "uni",
    "PbcCnPrSocialise": "uni", "PbcCnPrSomeCare": "uni",
    "PbcCnPrSprmrkt": "uni", "PbcCnPrTechTouch": "uni", "PbcCnPrTired": "uni",
    "PbcCnPrUsualAct": "uni", "PbcCnPrWork": "uni",
    "PbcCnPwBored": "bi", "PbcCnPwBusyPlace": "bi", "PbcCnPwDistrac": "bi",
    "PbcCnPwEnoughRoom": "bi", "PbcCnPwForgExer": "bi", "PbcCnPwForget": "bi",
    "PbcCnPwLonely": "bi", "PbcCnPwLotMind": "bi", "PbcCnPwNormClose": "bi",
    "PbcCnPwOthAppr": "bi", "PbcCnPwOthDist": "bi", "PbcCnPwPayAtt": "bi",
    "PbcCnPwShopping": "bi", "PbcCnPwSignposts": "bi", "PbcCnPwSitClose": "bi",
    "PbcCnPwSocialise": "bi", "PbcCnPwSomeCare": "bi", "PbcCnPwSprmrkt": "bi",
    "PbcCnPwTechTouch": "bi", "PbcCnPwTired": "bi", "PbcCnPwUsualAct": "bi",
    "PbcCnPwWork": "bi",
    "PbcSkImChildBad": "uni", "PbcSkImChildReject": "uni",
    "PbcSkImDecCont": "uni", "PbcSkImDecHugs": "uni",
    "PbcSkImDeclGreeting": "uni", "PbcSkImDeclHug": "uni",
    "PbcSkImEstDist": "uni", "PbcSkImMeetCare": "uni", "PbcSkImRemExer": "uni",
    "PbcSkImRemWalk": "uni", "PbcSkImRemem": "uni", "PbcSkImTechTouch": "uni",
    "PbcSkImTellOthers": "uni", "PbcSkImWalkFast": "uni",
    "PbcSkPrChildBad": "uni", "PbcSkPrChildReject": "uni",
    "PbcSkPrDecCont": "uni", "PbcSkPrDecHugs": "uni",
    "PbcSkPrDeclGreeting": "uni", "PbcSkPrDeclHug": "uni",
    "PbcSkPrEstDist": "uni", "PbcSkPrMeetCare": "uni", "PbcSkPrRemExer": "uni",
    "PbcSkPrRemWalk": "uni", "PbcSkPrRemem": "uni", "PbcSkPrTechTouch": "uni",
    "PbcSkPrTellOthers": "uni", "PbcSkPrWalkFast": "uni",
    "gnrcContract": "uni", "gnrcHoax": "uni", "gnrcInfctReqInsd": "uni",
    "gnrcInfctReqOutIn": "uni", "gnrcInfctReqSympt": "uni",
    "gnrcInfctReqTouch": "uni",
}

# (family regex, component-group -> output name suffix)
FAMILY_PATTERNS = [
    ("AttEx", re.compile(r"^AttEx(Ex|Ev)(.+)$"), {"Ex": "att_exp_strength", "Ev": "att_exp_eval"}),
    ("AttIn", re.compile(r"^At?tIn(Ex|Ev)(.+)$"), {"Ex": "att_instr_strength", "Ev": "att_instr_eval"}),
    ("Gen", re.compile(r"^Gen(Ex|Ev)(.+)$"), {"Ex": "gen_risk_strength", "Ev": "gen_risk_eval"}),
    ("NrmDe", re.compile(r"^NrmDe(Beh|Id)(.+)$"), {"Beh": "nrm_desc_behavior", "Id": "nrm_desc_ident"}),
    ("NrmIn", re.compile(r"^NrmIn(Ap|Mc)(.+)$"), {"Ap": "nrm_inj_approval", "Mc": "nrm_inj_motivation"}),
    ("PbcSk", re.compile(r"^PbcSk(Pr|Im)(.+)$"), {"Pr": "pbc_skill_prob", "Im": "pbc_skill_import"}),
    ("PbcCn", re.compile(r"^PbcCn(Pw|Pr)(.+)$"), {"Pw": "pbc_cond_power", "Pr": "pbc_cond_presence"}),
    ("CIBERlite", re.compile(r"^CIBERlite(.+)$"), {None: "ciberlite"}),
    ("gnrc", re.compile(r"^gnrc(.+)$"), {None: "gnrc_beliefs"}),
]

COV_MAP = {
    "country": "cov_country",
    "age": "cov_age_band",
    "gender": "cov_gender",
    "lastpage": "cov_lastpage",
    "startlanguage": "cov_language",
}


def fetch_data() -> pd.DataFrame:
    frames = []
    for fname in FILES:
        r = requests.get(RAW_BASE + fname, headers=UA, timeout=120)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content), low_memory=False)
        df = df.rename(columns={df.columns[0]: "orig_id"})
        m = re.search(r"sid-(\d+)", fname)
        df["sid"] = m.group(1)
        frames.append(df)
    full = pd.concat(frames, ignore_index=True, sort=False)
    full["id"] = full["sid"] + "-" + full["orig_id"].astype(str)
    assert full["id"].nunique() == len(full)
    return full


def build_scales() -> dict[str, list[tuple[str, str, str]]]:
    """Map output table name -> list of (raw_column, item_label, polarity)."""
    scales: dict[str, list[tuple[str, str, str]]] = {}
    for raw_col, polarity in ITEM_POLARITY.items():
        for family, pattern, out_map in FAMILY_PATTERNS:
            m = pattern.match(raw_col)
            if not m:
                continue
            if family in ("CIBERlite", "gnrc"):
                comp = None
                item = m.group(1)
            else:
                comp = m.group(1)
                item = m.group(2)
            out_name = f"peters_2025_{out_map[comp]}"
            scales.setdefault(out_name, []).append((raw_col, item.lower(), polarity))
            break
    return scales


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    parsed = pd.to_datetime(raw["datestamp"], format="%Y-%m-%d %H:%M:%S", utc=True)
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    # unit-agnostic: pandas may store datetimes at us or ns resolution
    # depending on version, so divide by a Timedelta rather than assume ns
    raw["date"] = ((parsed - epoch) / pd.Timedelta(seconds=1)).astype("int64")
    cov_cols = list(COV_MAP.values())

    scales = build_scales()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, items in sorted(scales.items()):
        raw_cols = [c for c, _, _ in items]
        long = raw[["id", "date"] + cov_cols + raw_cols].melt(
            id_vars=["id", "date"] + cov_cols,
            value_vars=raw_cols,
            var_name="raw_item",
            value_name="resp",
        )
        item_label = {c: label for c, label, _ in items}
        polarity = {c: pol for c, label, pol in items}
        long["item"] = long["raw_item"].map(item_label)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        valid_max = long["raw_item"].map(polarity).map({"uni": 5, "bi": 7})
        long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
        long = long.drop(columns=["raw_item"]).dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        out_cols = ["id", "item", "resp", "date"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_path.name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
