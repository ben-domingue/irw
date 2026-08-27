"""Academic Motivation Scale, Portuguese validity study -- two independent
samples of the same instrument.

DOI: 10.17632/6n78w5pz74
Source: https://data.mendeley.com/datasets/6n78w5pz74
License: CC BY 4.0
Contributor (deposit record): Ribeiro, Saraiva, Pereira

The deposit splits its data across two files, MotAcademica_AmostraA.sav
(568 respondents) and MotAcademica_AmostraB.sav (589). Both carry the same
29 items (Item1-Item29) on the same 1-7 scale, so this is one instrument
administered to two independently-recruited samples, not two instruments.
Per IRW practice that ships as ONE table with a `cov_study` covariate
distinguishing the samples, rather than two files.

Sample B's ids are offset past sample A's observed maximum id so the two
never collide.

The six bare columns DESM, MI, MERInte, MERIden, MERIntro and MERExter are
subscale means (their values are fractional) and are dropped.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/6n78w5pz74"
KEY = "6n78w5pz74"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SAMPLES = {"A": "MotAcademica_AmostraA.sav", "B": "MotAcademica_AmostraB.sav"}
COMPOSITES = ["DESM", "MI", "MERInte", "MERIden", "MERIntro", "MERExter"]
SCALE = (1, 7)


def fetch(filename: str) -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    match = [f for f in r.json()["files"] if f["filename"] == filename]
    assert len(match) == 1, filename
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    import pyreadstat
    fh = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
    fh.write(rr.content); fh.close()
    return pyreadstat.read_sav(fh.name)[0]


def build() -> None:
    frames, id_offset = [], 0
    item_cols = None

    for sample, filename in SAMPLES.items():
        df = fetch(filename)
        df.columns = [str(c).strip() for c in df.columns]
        items = [c for c in df.columns
                 if c.startswith("Item") and c[len("Item"):].isdigit()]
        assert items, sample

        if item_cols is None:
            item_cols = sorted(items)
        else:
            assert sorted(items) == item_cols, \
                f"sample {sample} item set differs -- not the same instrument"

        unused = [c for c in df.columns if c not in items and c not in COMPOSITES]
        assert not unused, f"sample {sample}: unaccounted columns {unused}"

        df["id"] = range(id_offset + 1, id_offset + len(df) + 1)
        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"]))
        long["cov_study"] = f"sample_{sample}"
        frames.append(long)
        # offset past this sample's ACTUAL observed max id, not a round number
        id_offset = int(df["id"].max())
        print(f"  sample {sample}: {len(df)} respondents, "
              f"ids {int(df['id'].min())}-{id_offset}")

    for c in COMPOSITES:
        print(f"    dropped '{c}': subscale mean (fractional), not a raw item")

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(*SCALE).all(), sorted(long["resp"].unique())
    long = long[["id", "item", "resp", "cov_study"]]

    checks = run_qc(long)
    fails = [c for c in checks if c.status == "fail"]
    assert not fails, [(c.name, c.detail) for c in fails]
    for c in checks:
        if c.status == "warn":
            print(f"    NOTE {c.name}: {c.detail}")

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() > 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "ribeiro_2019_academic_motivation.csv", index=False)
    print(f"  ribeiro_2019_academic_motivation: {long['id'].nunique()} ids x "
          f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    build()
