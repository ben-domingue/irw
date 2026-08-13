#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13156951
# DOI: 10.7717/peerj.21098
#
# Khattak O, Ehsan A, Khalid AA, Iqbal A, Chaudhary FA, Baig MN, Alsharari T,
# Memon MR (2026), "Assessment of clinical readiness, knowledge and attitude,
# regarding Basic Life Support (BLS) and cardiopulmonary resuscitation (CPR)
# skill among dentists practicing in Saudi Arabia." PeerJ. CC BY 4.0.
#
# Supplementary file peerj-14-21098-s001.sav is a survey of N=400 practicing
# dentists. `knowledge` is a pre-computed composite (low/moderate/high) and
# excluded as an aggregate per datastandard.md. Three raw binary-item
# instruments are extracted as separate IRW files:
#   - attitude1/2/3/5 (4 items, 1=agree, 2=disagree) -> khattak_2026_attitude
#   - cr1..cr4 (4 items, clinical readiness, 1=yes, 2=no) -> khattak_2026_cr
#   - confidence1..confidence4 (4 items, 1=very confident, 2=not confident)
#     -> khattak_2026_confidence
# (attitude4 does not exist in the source file -- only attitude1/2/3/5 were
# retained by the original authors.)

import io
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13156951/supplementaryFiles"
MEMBER = "peerj-14-21098-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "khattak_2026_attitude": ["attitude1", "attitude2", "attitude3", "attitude5"],
    "khattak_2026_cr": ["cr1", "cr2", "cr3", "cr4"],
    "khattak_2026_confidence": ["confidence1", "confidence2", "confidence3", "confidence4"],
}


def load_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        data = f.read()
    tmp = Path("/tmp") / MEMBER
    tmp.write_bytes(data)
    df, _meta = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def make_scale(df: pd.DataFrame, items: list[str], out_name: str):
    items = [c for c in items if c in df.columns]
    long = df[["id"] + items].melt(id_vars=["id"], value_vars=items,
                                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_raw()
    for out_name, items in SCALES.items():
        make_scale(df, items, out_name)


if __name__ == "__main__":
    convert()
