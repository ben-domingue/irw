#!/usr/bin/env python3
# Source: https://zenodo.org/records/15699015
# DOI: 10.5281/zenodo.15699015 (data)
#   Ilham NA, Alexandra MJ, Inasius F (2025). Millennials Voluntary Tax Compliance Behavior: TPB Framework [Data set].
#   Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: sheet "Tabulasi Data", 438 Indonesian millennial taxpayers (English-language form). Each item header begins
#   with its code in brackets, e.g. "[TR1] I believe that the tax authorities act fairly ..."; item = that code.
#   Eight constructs, four items each, every item observed within 1-5: trust (TR), tax morale (TM), tax simplicity
#   (TS), tax knowledge (TK), social media (SM), peer influence (PI), compliance intention (ITC), voluntary tax
#   compliance behaviour (VTCB). ITC2 ("I do not intend to pay ...") is worded against its block; stored as given.
#   The "Full Name" column holds only "Respondent 1".."Respondent 438" (checked) and is dropped; id = row order.
# Tables, one per construct: _trust, _tax_morale, _tax_simplicity, _tax_knowledge, _social_media, _peer_influence,
#   _compliance_intention, _voluntary_compliance.
# Covariates: cov_gender, cov_occupation (formal / informal worker).
# Item text: not shipped -- the English stems are the headers, but no anchor labels in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/15699015/files/Data_Millennials%20Voluntary%20Tax%20Compliance%20Behavior-%20TPB%20Framework.xlsx/content'
N_ROWS = 438
ID_COL = None
COVS = {'Gender': 'cov_gender', 'Occupation': 'cov_occupation'}
COV_MAPS = {'cov_gender': {'Male': 'male', 'Female': 'female'}, 'cov_occupation': {'Formal workers (employees, etc.).': 'formal', 'Informal workers (freelancers, casual workers, etc.).': 'informal'}}
RENAME = {'[TR1] I believe that the tax authorities act fairly in enforcing the tax laws': 'TR1', '[TR2] I believe that the tax funds I pay are used for the public interest in a transparent manner': 'TR2', '[TR3] I feel that tax authorities are honest and trustworthy in managing taxes': 'TR3', '[TR4] I believe that the tax authorities have effectively enforced the tax rules': 'TR4', '[TM1] I think I should report all my tax liabilities honestly': 'TM1', "[TM2] I don't think taxpayers should underreport their tax liabilities": 'TM2', '[TM3] I think avoiding taxes is wrong': 'TM3', '[TM4] I always obey and follow tax laws': 'TM4', '[TS1] I feel that the tax system in Indonesia is easy to understand': 'TS1', '[TS2] I have no difficulty in calculating the amount of tax I have to pay': 'TS2', '[TS3] Online tax reporting forms and procedures in Indonesia make it easier and faster': 'TS3', '[TS4] I need a fast time to pay taxes': 'TS4', '[TK1] I understand the basic rules of taxation that apply to me as a taxpayer': 'TK1', '[TK2] I know the deadline for reporting and paying my taxes': 'TK2', '[TK3] I understand the sanctions that can be imposed if I do not pay taxes on time': 'TK3', '[TK4] I actively seek the latest information related to tax policy': 'TK4', '[SM1] I often see tax content shared on social media': 'SM1', '[SM2] I feel social media helps me get information related to tax reporting procedures': 'SM2', '[SM3] I feel more motivated to pay taxes after seeing others on social media discuss taxes positively': 'SM3', '[SM4] I tend to understand tax rules better after seeing tax education content on social media': 'SM4', '[PI1] I often discuss taxes with friends or coworkers': 'PI1', '[PI2] I am more likely to pay taxes if my friends are also tax compliant': 'PI2', "[PI3] My friends' opinions influence my attitude towards tax compliance": 'PI3', '[PI4] I have been influenced by people around me to avoid or delay paying taxes': 'PI4', '[ITC1] I always try to calculate my taxes based on actual income': 'ITC1', '[ITC2] I do not intend to pay taxes that differ from the actual amount': 'ITC2', '[ITC3] I plan to pay my taxes by March 31st of each year': 'ITC3', '[ITC4] I plan to submit my tax returns by March 31st of each year': 'ITC4', '[VTCB1] I pay taxes voluntarily without coercion from the authorities': 'VTCB1', '[VTCB2] I pay taxes on time because it is my responsibility as a citizen': 'VTCB2', '[VTCB3] I will still pay taxes correctly even if there are no incentives or rewards': 'VTCB3', '[VTCB4] I am happy to pay taxes because the cost is not high': 'VTCB4'}
BLOCKS = {'ilham_2025_trust': ['TR1', 'TR2', 'TR3', 'TR4'], 'ilham_2025_tax_morale': ['TM1', 'TM2', 'TM3', 'TM4'], 'ilham_2025_tax_simplicity': ['TS1', 'TS2', 'TS3', 'TS4'], 'ilham_2025_tax_knowledge': ['TK1', 'TK2', 'TK3', 'TK4'], 'ilham_2025_social_media': ['SM1', 'SM2', 'SM3', 'SM4'], 'ilham_2025_peer_influence': ['PI1', 'PI2', 'PI3', 'PI4'], 'ilham_2025_compliance_intention': ['ITC1', 'ITC2', 'ITC3', 'ITC4'], 'ilham_2025_voluntary_compliance': ['VTCB1', 'VTCB2', 'VTCB3', 'VTCB4']}
LO, HI = 1, 5
DROP_COLS = ['Full Name']


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Tabulasi Data')


def keep_rows(d):
    return d


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    d = d.drop(columns=[c for c in DROP_COLS if c in d.columns])
    d = keep_rows(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        d[cov] = d[src].map(COV_MAPS[cov]) if cov in COV_MAPS else d[src]
        if cov in COV_MAPS:
            assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    shipped = set()
    for name, items in BLOCKS.items():
        assert all(c in d for c in items), [c for c in items if c not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(LO, HI).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert name not in shipped
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    used = set(sum(BLOCKS.values(), [])) | set(COVS) | {ID_COL}
    print("source columns not shipped:", [c for c in d.columns if c not in used and c != "id" and c not in covs])


if __name__ == "__main__":
    main()
