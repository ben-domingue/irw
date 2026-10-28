"""alamer_2025_arabic_vlt.

Source: Alamer, A., et al. (2025). The Creation and Validation of the Arabic
Vocabulary Levels Test (Arabic-VLT). Language Assessment Quarterly,
doi:10.1080/15434303.2025.2477445.
Data: "Alamer et al 2025 ArabicVLT data.csv", sent to Ben Domingue by the first
author on 2026-10-26 offering it to the IRW. Archived with the paper and the
email at data/donated/alamer_2025_arabic_vlt/ (outside this repo).

Licence: no public deposit exists. The author contributed the file by email, so
Original License = Permission via Email; permission on file at
licenseinfo/emails/alamer_2025_arabic_vlt.md.

The Arabic-VLT is a matching-format vocabulary levels test modelled on the
English VLT of Schmitt et al. (2001): words are presented in clusters of six
with three definitions, over five word-frequency bands drawn from the Makkah
List for Frequent Arabic Vocabulary. Level 1 is the most frequent band, Level 5
the least. The published test has 30 scored items per level, 150 in all.

217 male undergraduates studying Arabic at Saudi universities, from Kenya,
Nigeria, South Korea, India and the UK, took it online in Google Forms. The
paper reports 259 responses received; 217 is the analysed sample, confirmed by
its RM-ANOVA residual df of 864 = 4 x (217 - 1).

Two things the file does not carry, both asked of the author 2026-10-28:

1. Four Level 2 item columns are absent. The header runs g31..g56 and then
   jumps to g61, so Level 2 has 26 columns where every other level has 30, and
   146 items ship instead of 150. The gap is not misfit-item deletion: the
   paper names g20, g21, g28 and g30 as the misfitting items and keeps them.
   It is visible in the paper's own numbers -- Level 2 mean 19.93 here against
   Level 3's 22.53, reversing the frequency ordering the test is built on,
   and the RM-ANOVA residual SS is 16896.7 against the published 26083.1.
   Four more Level 2 items would put its mean near 23 and make Level 2 and
   Level 3 indistinguishable, which is exactly the one post-hoc comparison the
   paper reports as non-significant (t = 2.23, p = .10).
2. No person covariates. The five countries and the age distribution are
   reported in the paper but are not columns in the file.

Mapping
- id            = row number (the file has no id column)
- item          = g1..g150 as the file and the paper label them, 146 of 150
- resp          = 0/1 as scored
- itemcov_level = 1..5, the word-frequency band the item belongs to

Blank cells are dropped, not scored 0. The file's own Lv1..Lv5 total columns
count a blank as incorrect -- they equal the count of 1s exactly -- but the
source documents no separate code for an item skipped versus one never
reached, so datastandard's default applies and the cell is filtered out. 4.5%
of item-responses are blank. The Lv* columns are level sums and do not ship.

Item text: not shipped. The paper's appendix prints one example cluster per
level; the other 145 items are not published. Asked of the author 2026-10-28.
"""
import hashlib
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

RAW = Path.home() / "Dropbox/projects/irw/data/donated/alamer_2025_arabic_vlt/arabic_vlt_data.csv"
SHA256 = "316ae7efd7bf3a737e426467393705c30d8d4001d53b798cb158299e305eff37"

assert RAW.exists(), f"donated file not found at {RAW}"
assert hashlib.sha256(RAW.read_bytes()).hexdigest() == SHA256

w = pd.read_csv(RAW)
assert w.shape == (217, 151)

## the five word-frequency bands, in the file's column order. Level 2 is short
## by four columns (g57-g60); see the docstring.
LEVELS = {1: range(1, 31), 2: range(31, 57), 3: range(61, 91),
          4: range(91, 121), 5: range(121, 151)}
LEVEL_OF = {f"g{i}": lv for lv, rng in LEVELS.items() for i in rng}
ITEMS = list(LEVEL_OF)
assert list(w.columns) == [c for lv in LEVELS
                           for c in [f"g{i}" for i in LEVELS[lv]] + [f"Lv{lv}"]]
assert len(ITEMS) == 146

## Lv1..Lv5 are level sums that score a blank as incorrect, so they are
## redundant with the item columns and do not ship
for lv, rng in LEVELS.items():
    cols = [f"g{i}" for i in rng]
    assert (w[cols].eq(1).sum(axis=1) == w[f"Lv{lv}"]).all()

wide = w[ITEMS].copy()
wide["id"] = range(1, len(wide) + 1)

df = wide.melt(id_vars=["id"], var_name="item", value_name="resp")
df = df.dropna(subset=["resp"])
df["resp"] = df["resp"].astype(int)
df["itemcov_level"] = df["item"].map(LEVEL_OF)
assert set(df["resp"]) == {0, 1}
assert len(df) == 30271  ## 31682 person-item cells, 1411 (4.5%) left blank

## the paper's analysed sample, and its item ordering by frequency band
assert df["id"].nunique() == 217 and df["item"].nunique() == 146
band = df.groupby("itemcov_level")["resp"].mean()
assert band[1] > band[2] and band[3] > band[4] > band[5]

df = df[["id", "item", "resp", "itemcov_level"]].sort_values(
    ["id", "item"], kind="stable")

checks = run_qc(df, permitted_values={i: {0, 1} for i in ITEMS})
fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
assert not fails, fails
df.to_csv("alamer_2025_arabic_vlt.csv", index=False)
print(f"alamer_2025_arabic_vlt: rows={len(df)} ids={df['id'].nunique()} "
      f"items={df['item'].nunique()}")
