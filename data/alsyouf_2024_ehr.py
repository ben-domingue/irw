from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300657
# DOI: 10.1371/journal.pone.0300657
# Legend (paper Sec. 3): A=Agreeableness, C=Conscientiousness, CI=Continuance
# intention, E=Extraversion, EE=Effort expectancy, EUS=End user support,
# FC=Facilitating conditions, MS=Management support, N=Neuroticism,
# O=Openness to experience, PE=Performance expectancy, SI=Social influence.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0300657.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "gender": "cov_gender",
    "age": "cov_age",
    "edu": "cov_education",
    "prof.exp": "cov_professional_experience",
    "hos.Name": "cov_hospital",
    "dep.Name": "cov_department",
}

SCALES = {
    "alsyouf_2024_continuance_intention": r"CI\d+$",
    "alsyouf_2024_performance_expectancy": r"PE\d+$",
    "alsyouf_2024_effort_expectancy": r"EE\d+$",
    "alsyouf_2024_social_influence": r"SI\d+$",
    "alsyouf_2024_facilitating_conditions": r"FC\d+$",
    "alsyouf_2024_management_support": r"MS\d+$",
    "alsyouf_2024_end_user_support": r"EUS\d+$",
    "alsyouf_2024_neuroticism": r"N\d+$",
    "alsyouf_2024_extraversion": r"E\d+$",
    "alsyouf_2024_openness": r"O\d+$",
    "alsyouf_2024_agreeableness": r"A\d+$",
    "alsyouf_2024_conscientiousness": r"C\d+$",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    df = fetch()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, pattern in SCALES.items():
        pat = re.compile(pattern)
        item_cols = [c for c in df.columns if pat.fullmatch(c)]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
