"""Turkish adaptation study: social identity, locus of control, entrepreneurial
self-efficacy, uncertainty avoidance, risk perception and entrepreneurial
orientation.

DOI: 10.17632/826gmw6ypw
Source: https://data.mendeley.com/datasets/826gmw6ypw
License: CC BY 4.0
Contributor (deposit record): Avci

216 respondents, all items on a 1-7 scale, across 25 short instrument blocks
that each ship as their own table.

Two clean-up problems in the source column names, both handled explicitly
rather than by a loose prefix match:

1. The 39 `*ORT` columns are subscale means ("ortalama") and are dropped.
2. Several blocks carry typo'd variants of their own name, which a naive
   prefix match would split into spurious one-item blocks:
       IcKontol_odak7        -> IcKontrol_odak
       TmlAmacOz_yeterlık2   -> TmlAmacOz_yeterlk
       YenCevOlsOz_yeterlık15-> YenCevOlsOz_yeterlk
   and the `_ek` ("ek" = additional) items belong to the identity blocks they
   are named after. `canonical()` below folds these together, and the expected
   size of every block is asserted so a future rename cannot silently drop
   items.
"""
from __future__ import annotations

import re
import sys
import tempfile
from collections import OrderedDict
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/826gmw6ypw"
KEY = "826gmw6ypw"
FILENAME = "öLÇEK Murat_UYARLAMA_HALİ SON.sav"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

COVS = {"Yas": "cov_age", "Cinsiyet": "cov_gender",
        "Eğitim_durumu": "cov_education", "Uzmanlık_alanı": "cov_expertise",
        "Sektör": "cov_sector", "Ortak_sayısı": "cov_n_partners",
        "Kuruluş_yılı": "cov_founding_year", "Çalışan_sayısı": "cov_n_employees"}
SCALE = (1, 7)

# canonical block name -> expected item count
EXPECTED = {
    "kımlık_Dar": 7, "kımlık_Com": 6, "kımlık_Miss": 6,
    "IcKontrol_odak": 8, "BskDayKontrol_odak": 6, "SansDayKontrol_odak": 5,
    "TmlAmacOz_yeterlk": 6, "ZorBasEtOz_yeterlk": 6, "YenCevOlsOz_yeterlk": 5,
    "UrunPazGelOz_yeterlk": 8, "YatrmcIlıskOz_yeterlk": 3, "IKYOz_yeterlk": 5,
    "Belırsız_kac": 5, "Rısk_algı": 5, "Oz_norm": 3,
    "Statu_Gır_yonel": 6, "Bagmsz_Gır_yonel": 6, "Kazanc_Gır_yonel": 5,
    "IsSahp_Gır_yonel": 4, "BasrmaArzu_Gır_yonel": 4, "Zorunluluk_Gır_yonel": 3,
    "ToplmFayd_Gır_yonel": 4, "Gecmıs_Gır_yonel": 3, "SureklGel_Gır_yonel": 3,
    "Guc_Gır_yonel": 2, "Rısk_Gır_yonel": 2, "Aktıf_Gır_yonel": 2,
}


def canonical(col: str) -> str:
    """Fold a raw column name onto its block name, repairing the typo'd
    variants documented in the module docstring."""
    c = col
    c = c.replace("IcKontol", "IcKontrol")
    c = c.replace("yeterlık", "yeterlk")
    c = re.sub(r"_?\d*ek$", "", c)      # the "_ek" additional items
    c = re.sub(r"_?\d+$", "", c)        # trailing item number
    return c


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    match = [f for f in r.json()["files"] if f["filename"] == FILENAME]
    assert len(match) == 1
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    import pyreadstat
    fh = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
    fh.write(rr.content); fh.close()
    return pyreadstat.read_sav(fh.name)[0]


def build() -> None:
    df = fetch()
    df.columns = [str(c).strip() for c in df.columns]
    df["id"] = range(1, len(df) + 1)
    cov = df[["id"] + list(COVS)].rename(columns=COVS)

    means = [c for c in df.columns if c.endswith("ORT")]
    print(f"    dropped {len(means)} '*ORT' subscale-mean columns")
    used = set(COVS) | set(means) | {"id"}

    blocks: "OrderedDict[str, list]" = OrderedDict()
    for c in df.columns:
        if c in used:
            continue
        blocks.setdefault(canonical(c), []).append(c)

    assert set(blocks) == set(EXPECTED), \
        f"block set changed: {sorted(set(blocks) ^ set(EXPECTED))}"
    for name, cols in blocks.items():
        assert len(cols) == EXPECTED[name], \
            f"{name}: {len(cols)} items, expected {EXPECTED[name]}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for block, items in blocks.items():
        used.update(items)
        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"])
                .merge(cov, on="id"))
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(*SCALE).all(), \
            f"{block}: {sorted(long['resp'].unique())}"
        long = long[["id", "item", "resp"] + list(COVS.values())]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        assert not fails, f"{block}: {[(c.name, c.detail) for c in fails]}"

        assert long["id"].nunique() >= 100, block
        assert long["item"].nunique() > 1, block

        slug = re.sub(r"[^a-z0-9]+", "_",
                      block.lower().replace("ı", "i").replace("ğ", "g")
                      .replace("ş", "s").replace("ç", "c").replace("ö", "o")
                      .replace("ü", "u")).strip("_")
        name = f"avci_2024_{slug}"
        assert name not in written, f"duplicate table name {name}"
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written[name] = len(long)
        print(f"  {name}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")

    leftover = [c for c in df.columns if c not in used]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"  total: {sum(written.values())} responses across {len(written)} tables")


if __name__ == "__main__":
    build()
