#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8759353
# DOI: 10.7717/peerj.12809
#   "Medical cannabis use in Thailand after its legalization: a respondent-driven
#   sample survey" (Assanangkornchai, Thaikla, Talek, Saingam, 2022), PeerJ
#   10:e12809. PMC8759353.
# Data: PeerJ supplementary Raw Data peerj-10-12809-s003.xlsx (sheet data_P1,
#       485 x 54; sheet Code = codebook), fetched from the Europe PMC
#       supplementaryFiles zip.
# License: CC BY 4.0 (PeerJ article licence; the data are a PeerJ supplement).
#
# Item text: not shipped. The Code sheet gives English item labels for 25 of the
#   32 perception items (e.g. v501 "Treatment of chronic pain in adults",
#   v521 "Palpitations"); Table 3 of the paper lists 26 of them. V506, V510,
#   V511, V514, V516, V518 have no label in either place. The questionnaire was
#   administered in Thai by face-to-face interview; the Thai wording is not
#   deposited.
#
# Tables (section 3 of the questionnaire, "perception of benefits and harms of
# medical cannabis"; each item 1 = Yes, 2 = No in the file, recoded 1/0):
#   assanangkornchai_2022_cannabis_benefits  V501-V520, 20 perceived benefits
#   assanangkornchai_2022_cannabis_harms     V521-V532, 12 perceived harms
# The split follows the paper's Table 3 (benefits column / harms column);
# V520 (chronic cough) is a benefit there.
#
# Sample: 485 adult medical-cannabis users recruited by respondent-driven
# sampling in four regions of Thailand. `no` is a row number, used as id.
# No PII: coupon numbers are RDS recruitment codes, not personal identifiers
# (skipped anyway). No fractional values, no exact-duplicate rows. Repeated
# response patterns (e.g. every benefit yes / every harm no, 45 rows) are the
# block structure of the checklist, not copied rows.

import io
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
ZIP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8759353/supplementaryFiles"
FNAME = "peerj-10-12809-s003.xlsx"


def load() -> pd.DataFrame:
    r = requests.get(ZIP_URL, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(FNAME)), sheet_name="data_P1")


def main() -> None:
    d = load()
    assert d.shape == (485, 54), d.shape
    assert d["no"].is_unique

    benefits = [f"V{i}" for i in range(501, 521)]
    harms = [f"V{i}" for i in range(521, 533)]
    covs = {
        "region": "cov_region", "gender": "cov_gender", "age": "cov_age",
        "education": "cov_education", "occupation": "cov_occupation",
        "network": "cov_network_size", "con_use1": "cov_condition_for_use",
        "con_use2": "cov_condition_moph_class", "source1": "cov_cannabis_source",
    }
    skipped = {
        "coupon": "RDS coupon code (recruitment linkage, not a respondent attribute)",
        "c1": "RDS coupon code issued to recruit", "c2": "RDS coupon code issued to recruit",
        "c3": "RDS coupon code issued to recruit",
        **{f"V{i}": "source-of-information checklist (where the respondent heard "
                    "about cannabis), not a scale" for i in range(431, 439)},
    }
    used = {"no"} | set(benefits) | set(harms) | set(covs)
    assert used.isdisjoint(skipped)
    assert set(d.columns) == used | set(skipped), set(d.columns) ^ (used | set(skipped))
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")

    d = d.rename(columns={"no": "id", **covs})
    cov_cols = list(covs.values())

    tables = {
        "assanangkornchai_2022_cannabis_benefits": benefits,
        "assanangkornchai_2022_cannabis_harms": harms,
    }
    assert len(tables) == len(set(tables))
    for name, items in tables.items():
        vals = pd.unique(d[items].values.ravel())
        assert set(pd.Series(vals).dropna()) <= {1, 2}, vals
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = (t["resp"] == 1).astype(int)   # 1 = yes, 2 = no -> 1/0
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: {0, 1} for i in items}
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
