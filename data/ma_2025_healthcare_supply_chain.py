#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/29235896
# DOI: 10.6084/m9.figshare.29235896.v1 (data; no paper DOI on the record)
#   Ma, J.-Y. (2025). "Digital Intelligence and Decision Optimization in
#   Healthcare Supply Chain Management." figshare.
# Data: data.xlsx, 360 rows of a Chinese healthcare supply-chain survey (SEM
#   study), item columns I1-5, IC1-5, AC1-3, RPC1-3, RTC1-3, DO1-5, all 1-5.
#   The construct for each prefix is named in the record description:
#   digital intelligence, innovation capability, and supply-chain resilience
#   as absorptive, response and restorative capability, then strategic
#   decision optimization.
# License: CC BY 4.0 (figshare record).
# Codebook: none (constructs named in the record description only).
#
# Item text: not shipped -- codes only.
#
# Tables (one per construct, items as deposited):
#   ma_2025_digital_intelligence  I1-I5
#   ma_2025_innovation_capability IC1-IC5
#   ma_2025_absorptive_capability AC1-AC3
#   ma_2025_response_capability   RPC1-RPC3
#   ma_2025_restorative_capability RTC1-RTC3
#   ma_2025_decision_optimization DO1-DO5
# Serial number 序号 76 appears on two rows identical in every column (one
#   entry recorded twice); the copy is dropped, leaving 359 respondents.
#   id = 序号. No covariates in the file.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/55112222"
ALLOWED = {1, 2, 3, 4, 5}
SPEC = {"ma_2025_digital_intelligence": ("I", 5),
        "ma_2025_innovation_capability": ("IC", 5),
        "ma_2025_absorptive_capability": ("AC", 3),
        "ma_2025_response_capability": ("RPC", 3),
        "ma_2025_restorative_capability": ("RTC", 3),
        "ma_2025_decision_optimization": ("DO", 5)}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (360, 25), d.shape
    # serial 76 appears on two rows identical in every column: one entry
    # recorded twice; keep the first
    dup = d.duplicated(keep="first")
    assert dup.sum() == 1 and d.loc[dup, "序号"].tolist() == [76]
    d = d[~dup].reset_index(drop=True)
    d["id"] = d["序号"].astype(int)
    assert d["id"].is_unique
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (p, n) in SPEC.items():
        items = [f"{p}{i}" for i in range(1, n + 1)]
        long = d.melt(id_vars=["id"], value_vars=items, var_name="item",
                      value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: ALLOWED for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
