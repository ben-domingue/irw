from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0276665
# DOI: 10.1371/journal.pone.0276665
# Gerber et al. (2022), "The effects of Swiss summer camp on the
# development of socio-emotional abilities in children". S1 Data. CC BY
# 4.0. N=256 children, pre/post camp (wave=1/2).
# Two clean scale blocks shipped: ALT (altruism, 14 items, 0-4) and EST
# (self-esteem, 9 items, -2 to 2). A third 20-item block (TIM/EMO/SOC/ACT
# dimensions, several reverse-worded "R" items, unclear construct name and
# reverse-coding not yet applied) is NOT shipped -- needs the source paper
# before it can be split/scored safely.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0276665.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ALT_PRE = [f"PREALT{i}" for i in range(1, 15)]
ALT_POST = [f"POSTALT{i}" for i in range(1, 15)]
EST_PRE = [f"PREEST{i}" for i in range(1, 10)]
EST_POST = [f"POSTEST{i}" for i in range(1, 10)]
ALT_ITEMS = [f"alt{i}" for i in range(1, 15)]
EST_ITEMS = [f"est{i}" for i in range(1, 10)]

COV_MAP = {"Q4SEX": "cov_sex", "Q1AGE": "cov_age", "Condition": "cov_condition"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "Participant": "id"})


def _wave_long(df, pre_cols, post_cols, items, cov_cols):
    pre = df[["id"] + cov_cols + pre_cols].rename(columns=dict(zip(pre_cols, items)))
    pre_long = pre.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    pre_long["wave"] = 1
    post = df[["id"] + cov_cols + post_cols].rename(columns=dict(zip(post_cols, items)))
    post_long = post.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    post_long["wave"] = 2
    return pd.concat([pre_long, post_long], ignore_index=True)


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    alt = _wave_long(df, ALT_PRE, ALT_POST, ALT_ITEMS, cov_cols)
    alt["resp"] = pd.to_numeric(alt["resp"], errors="coerce")
    alt = alt.dropna(subset=["resp"]).reset_index(drop=True)
    alt = alt[["id", "item", "resp", "wave"] + cov_cols]
    alt.to_csv(OUT_DIR / "gerber_2022_altruism.csv", index=False)
    print(f"gerber_2022_altruism: rows={len(alt)} ids={alt['id'].nunique()} "
          f"items={alt['item'].nunique()} resp={alt['resp'].min():.0f}-{alt['resp'].max():.0f}")

    est = _wave_long(df, EST_PRE, EST_POST, EST_ITEMS, cov_cols)
    est["resp"] = pd.to_numeric(est["resp"], errors="coerce")
    est = est.dropna(subset=["resp"]).reset_index(drop=True)
    est = est[["id", "item", "resp", "wave"] + cov_cols]
    est.to_csv(OUT_DIR / "gerber_2022_self_esteem.csv", index=False)
    print(f"gerber_2022_self_esteem: rows={len(est)} ids={est['id'].nunique()} "
          f"items={est['item'].nunique()} resp={est['resp'].min():.0f}-{est['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
