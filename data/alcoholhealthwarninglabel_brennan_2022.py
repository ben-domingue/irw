"""
Process Alcohol Health Warning Study Data_file.dta into IRW-format tables.

Source: Brennan et al. (2022). Testing the effectiveness of alcohol health
warning label formats. PLoS ONE 17(12): e0276189.

Produces:
  - alcoholhealthwarninglabel_brennan_2022_negative_arousal.csv
  - alcoholhealthwarninglabel_brennan_2022_positive_arousal.csv
  - alcoholhealthwarninglabel_brennan_2022_awareness_harms.csv
  - alcoholhealthwarninglabel_brennan_2022_intentions_postexposure.csv

Requires: pandas, pyreadstat  (pip install pyreadstat --break-system-packages)
"""

import pyreadstat
import pandas as pd
from pathlib import Path

# Resolve paths relative to this script's own folder, so it works wherever
# the folder is moved/cloned. Assumes the .dta file sits alongside this
# script — update SRC below if yours lives somewhere else.
BASE_DIR = Path(__file__).resolve().parent
SRC = BASE_DIR / 'Alcohol Health Warning Study_Data file.dta'
OUT_DIR = BASE_DIR

# ---------------------------------------------------------------------------
# Load raw Stata file (values + labels)
# ---------------------------------------------------------------------------
df, meta = pyreadstat.read_dta(SRC)
df = df.reset_index(drop=True)

# No participant id exists in the source file — generate a persistent
# sequential id (1 row = 1 participant in this file).
df['id'] = df.index + 1

# ---------------------------------------------------------------------------
# Covariates (person-invariant; attached to every IRW table via cov_ prefix)
# ---------------------------------------------------------------------------
condition_map = {
    1: 'No HWL control', 2: 'DrinkWise control', 3: 'Text-Only',
    4: 'Text + Pictogram', 5: 'Text + Photograph',
}
df['cov_condition'] = df['condition'].map(condition_map)
df['cov_age'] = df['A1']
df['cov_gender'] = df['gender_A2b'].map({0: 'not male', 1: 'male'})

COVS = ['cov_condition', 'cov_age', 'cov_gender']


def melt_construct(source_df, item_map, wave_label):
    """Reshape a set of wide item columns into id/item/resp long format."""
    cols = list(item_map.keys())
    long = source_df[['id'] + cols + COVS].melt(
        id_vars=['id'] + COVS,
        value_vars=cols,
        var_name='item',
        value_name='resp',
    )
    long['item'] = long['item'].map(item_map)
    long = long.dropna(subset=['resp'])
    long['wave'] = wave_label
    return long[['id', 'item', 'resp', 'wave'] + COVS]


# ---------------------------------------------------------------------------
# 1. Negative emotional arousal (follow-up, 7-point scale)
# ---------------------------------------------------------------------------
neg_items = {
    'FG1_FG6_1': 'disgusted',
    'FG1_FG6_2': 'afraid',
    'FG1_FG6_3': 'uncomfortable',
    'FG1_FG6_4': 'worried',
}
negative_arousal = melt_construct(df, neg_items, wave_label='follow_up')

# ---------------------------------------------------------------------------
# 2. Positive emotional arousal (follow-up, 7-point scale)
# ---------------------------------------------------------------------------
pos_items = {
    'FG1_FG6_5': 'excited',
    'FG1_FG6_6': 'pleased',
}
positive_arousal = melt_construct(df, pos_items, wave_label='follow_up')

# ---------------------------------------------------------------------------
# 3. Awareness of alcohol-related harms (follow-up, binary)
#    Note: there is no FD2_FD6_3_b in the source file — only 4 items
#    (cancer, liver damage, heart disease, pregnancy complications),
#    matching the paper's item list.
# ---------------------------------------------------------------------------
aware_items = {
    'FD2_FD6_1_b': 'increase_cancer_risk',
    'FD2_FD6_2_b': 'increase_liver_damage_risk',
    'FD2_FD6_4_b': 'increase_heart_disease_risk',
    'FD2_FD6_5_b': 'increase_pregnancy_complication_risk',
}
awareness_harms = melt_construct(df, aware_items, wave_label='follow_up')
awareness_harms['resp'] = awareness_harms['resp'].astype(int)

# ---------------------------------------------------------------------------
# 4. Drinking-reduction intentions, immediately post-exposure (raw 4-pt)
#    Note: "avoid drinking completely" (D2_D4_4) is only available in this
#    file already binarized (D2_D4_4_r), so it's excluded here to avoid
#    mixing response scales within one resp column.
# ---------------------------------------------------------------------------
intent_items = {
    'D2_D4_2': 'reduce_how_often',
    'D2_D4_3': 'reduce_amount_per_occasion',
}
intentions_postexposure = melt_construct(df, intent_items, wave_label='post_exposure')

# ---------------------------------------------------------------------------
# Write the four IRW tables
# ---------------------------------------------------------------------------
tables = {
    'negative_arousal': negative_arousal,
    'positive_arousal': positive_arousal,
    'awareness_harms': awareness_harms,
    'intentions_postexposure': intentions_postexposure,
}
for name, table in tables.items():
    fn = f'{OUT_DIR}/alcoholhealthwarninglabel_brennan_2022_{name}.csv'
    table.to_csv(fn, index=False)
    print(f'{name}: {table.shape} -> {fn}')