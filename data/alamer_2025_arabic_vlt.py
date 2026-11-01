"""alamer_2025_arabic_vlt.

Source: Alamer, A., et al. (2025). The Creation and Validation of the Arabic
Vocabulary Levels Test (Arabic-VLT). Language Assessment Quarterly,
doi:10.1080/15434303.2025.2477445.
Data: "Alamer et al 2025 ArabicVLT data V2.xlsx", posted by the first author on
issue #3295 on 2026-11-01. It supersedes the CSV he emailed Ben Domingue on
2026-10-26 offering the data to the IRW, which lacked four Level 2 items. Both
files, the paper and the permission email are archived at
data/donated/alamer_2025_arabic_vlt/ (Dropbox, outside this repo).

Licence: no public deposit exists. The author contributed the file by email, so
Original License = Permission via Email; the email is archived as
permission_email_2026-10-26.pdf beside the data.

The Arabic-VLT is a matching-format vocabulary levels test modelled on the
English VLT of Schmitt et al. (2001): words are presented in clusters of six
with three definitions, over five word-frequency bands drawn from the Makkah
List for Frequent Arabic Vocabulary. Level 1 is the most frequent band, Level 5
the least. The published test has 30 scored items per level, 150 in all.

217 male undergraduates studying Arabic at Saudi universities, from Kenya,
Nigeria, South Korea, India and the UK, took it online in Google Forms. The
paper reports 259 responses received; 217 is the analysed sample, confirmed by
its RM-ANOVA residual df of 864 = 4 x (217 - 1).

Two versions of the file. The 2026-10-26 CSV labelled items g1..g150 but its
header jumped from g56 to g61, so Level 2 had 26 columns and 146 items. The
2026-11-01 V2 workbook labels items i1..i150 and carries all 150. On the 146
items both files share, every cell agrees, row for row, blanks included, so V2
is a strict superset and the i-numbers are the g-numbers. Items keep the g
labels, which are the paper's; i57..i60 become g57..g60. With the four items
restored the level means run 24.97 > 23.04 > 22.53 > 19.42 > 18.51 and the
Level 2 vs Level 3 paired t is 2.26 against the paper's 2.23. The paper's
RM-ANOVA residual SS (26,083.1) is still not reproduced (17,867.2 here).

The file carries no person covariates; the five countries and the age
distribution are reported in the paper only. Asked of the author in #3295.

Mapping
- id            = row number (the file has no id column)
- item          = g1..g150, the paper's labels (V2's i1..i150, same numbers)
- resp          = 0/1 as scored
- itemcov_level = 1..5, the word-frequency band the item belongs to

Blank cells are dropped, not scored 0. The earlier CSV's Lv1..Lv5 totals
counted a blank as incorrect, but the source documents no separate code for an
item skipped versus one never reached, so datastandard's default applies and
the cell is filtered out. 4.4% of item-responses are blank.

Item text: not shipped. The paper's appendix prints one example cluster per
level; the other 145 items are not published. Asked of the author in #3295.
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

DONATED = Path.home() / "Dropbox/projects/irw/data/donated/alamer_2025_arabic_vlt"
RAW = DONATED / "arabic_vlt_data_v2.xlsx"
SHA256 = "5c6f8200dd853ee86d52d58f233f97940bb0bb284eff78cb0749e73450ec36d5"
V1 = DONATED / "arabic_vlt_data.csv"
V1_SHA256 = "316ae7efd7bf3a737e426467393705c30d8d4001d53b798cb158299e305eff37"

assert RAW.exists(), f"donated file not found at {RAW}"
assert hashlib.sha256(RAW.read_bytes()).hexdigest() == SHA256

w = pd.read_excel(RAW)
assert w.shape == (217, 150)
assert list(w.columns) == [f"i{i}" for i in range(1, 151)]
w.columns = [f"g{i}" for i in range(1, 151)]

## the superseded CSV, when present: V2 must agree with it on every shared cell
if V1.exists():
    assert hashlib.sha256(V1.read_bytes()).hexdigest() == V1_SHA256
    v1 = pd.read_csv(V1)
    shared = [c for c in v1.columns if c.startswith("g")]
    assert len(shared) == 146 and set(shared) <= set(w.columns)
    a, b = v1[shared].reset_index(drop=True), w[shared].reset_index(drop=True)
    assert ((a == b) | (a.isna() & b.isna())).all().all()

## the five word-frequency bands, 30 items each
LEVELS = {lv: range((lv - 1) * 30 + 1, lv * 30 + 1) for lv in range(1, 6)}
LEVEL_OF = {f"g{i}": lv for lv, rng in LEVELS.items() for i in rng}
ITEMS = list(LEVEL_OF)
assert len(ITEMS) == 150

wide = w[ITEMS].copy()
wide["id"] = range(1, len(wide) + 1)

df = wide.melt(id_vars=["id"], var_name="item", value_name="resp")
df = df.dropna(subset=["resp"])
df["resp"] = df["resp"].astype(int)
df["itemcov_level"] = df["item"].map(LEVEL_OF)
assert set(df["resp"]) == {0, 1}
assert len(df) == 31131  ## 32550 person-item cells, 1419 (4.4%) left blank

## the paper's analysed sample, and its item ordering by frequency band
assert df["id"].nunique() == 217 and df["item"].nunique() == 150
band = df.groupby("itemcov_level")["resp"].mean()
assert band[1] > band[2] > band[3] > band[4] > band[5]

df = df[["id", "item", "resp", "itemcov_level"]].sort_values(
    ["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1} for i in ITEMS})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("alamer_2025_arabic_vlt.csv", index=False)
print(f"alamer_2025_arabic_vlt: rows={len(df)} ids={df['id'].nunique()} "
      f"items={df['item'].nunique()}")
