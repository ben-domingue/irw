#!/usr/bin/env python3
# Source: https://zenodo.org/records/20738648
# DOI: 10.5281/zenodo.20738648 (data)
#   Felicia G, Wirawan EG, Inasius F (2026). Trust, Power, and Digital Tax Compliance Across Generations [Data set].
#   Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: one workbook, 555 registered Indonesian individual taxpayers (Millennials and Gen Z), English-language form.
#   Each item header begins with its code in brackets; item = that code. Every item observed within 1-5.
#   The "Full Name" column holds only "Respondent 1".."Respondent 555" (checked) and is dropped; id = row order.
# Tables: _system_quality (digital system quality, DSQ1-3); _digital_authority (the record's Perceived Digital
#   Authority: trust in the authority TR1-3 and its power PR1-3); _voluntary_compliance (VC1-3); _enforced_compliance
#   (EC1-3).
# Covariates: cov_age_group (bands as recorded), cov_gender, cov_occupation (as recorded; multi-selects kept as given).
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
URL = 'https://zenodo.org/api/records/20738648/files/Dataset_Trust%2C%20Power%2C%20and%20Digital%20Tax%20Compliance%20Across%20Generations.xlsx/content'
N_ROWS = 555
ID_COL = None
COVS = {'Age': 'cov_age_group', 'Gender': 'cov_gender', 'Occupation': 'cov_occupation'}
COV_MAPS = {'cov_gender': {'Male': 'male', 'Female': 'female'}}
RENAME = {'[DSQ1] The taxation website/application is easy to use': 'DSQ1', '[DSQ2]  This electronic tax system is accessible at any time': 'DSQ2', '[DSQ3] The electronic tax system provides reliable information': 'DSQ3', '[TR1] The tax authority treats taxpayers with respect': 'TR1', '[TR2] I believe that tax revenues are managed transparently for the public interest': 'TR2', '[TR3]  I consider the tax authority to be trustworthy': 'TR3', '[PR1] The tax authority has the power to enforce honest tax reporting': 'PR1', '[PR2] The tax authority has the expertise to detect tax avoidance due to its specialized knowledge': 'PR2', '[PR3] The tax authority takes firm action against tax crimes in Indonesia': 'PR3', '[VC1]  I am happy to pay taxes because the tax burden is not too high': 'VC1', '[VC2]  I would still report my taxes honestly, even if I knew that there would be no tax audits at all': 'VC2', '[VC3] Paying taxes is a contribution that makes me proud as a citizen': 'VC3', '[EC1]  I feel compelled to pay taxes': 'EC1', '[EC2] I pay taxes because the risk of being audited is high': 'EC2', '[EC3]  I pay taxes because the penalties for non-compliance are high': 'EC3'}
BLOCKS = {'felicia_2026_system_quality': ['DSQ1', 'DSQ2', 'DSQ3'], 'felicia_2026_digital_authority': ['TR1', 'TR2', 'TR3', 'PR1', 'PR2', 'PR3'], 'felicia_2026_voluntary_compliance': ['VC1', 'VC2', 'VC3'], 'felicia_2026_enforced_compliance': ['EC1', 'EC2', 'EC3']}
LO, HI = 1, 5
DROP_COLS = ['Full Name']


def load(content):
    return pd.read_excel(io.BytesIO(content))


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
