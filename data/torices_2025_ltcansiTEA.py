#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/28188872
# DOI: 10.6084/m9.figshare.28188872.v1
# Title: LTCAnsiTEA: Unrude data of article: Mediating effect of cognitive rigidity
#        on the relationship between autism and anxiety in adults
# Author: Lucía Torices Callejo
# License: CC BY 4.0
# N=108 participants, 4 scales (BAPQ, ISRA-b, ISRA-b-SIT, D'Flex)
#
# The dataset contains 4 scales — one output file per scale:
#   torices_2025_bapq.csv         — BAPQ (Broad Autism Phenotype Questionnaire), 36 items, 1-6
#   torices_2025_isra_b.csv       — ISRA(b) anxiety symptoms, 24 items, 0-4
#   torices_2025_isra_b_sit.csv   — ISRA(b)-SIT situational anxiety, 22 items, 0-4
#   torices_2025_dflex.csv        — D'Flex cognitive flexibility, 24 items, 1-6
#
# Codebook (Sexo): 1=Hombre (male), 2=Mujer (female), 3=Prefiero no decirlo (prefer not to say)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

FIGSHARE_FILE_URL = "https://ndownloader.figshare.com/files/51612044"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Scale definitions: (prefix_or_cols, valid_min, valid_max, out_name)
SCALES = [
    ('BAPQ',        1, 6, 'torices_2025_bapq'),
    ('ISRA_b',      0, 4, 'torices_2025_isra_b'),
    ('ISRA_b_SIT',  0, 4, 'torices_2025_isra_b_sit'),
    ('DFlex',       1, 6, 'torices_2025_dflex'),
]


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Download file
    resp = requests.get(FIGSHARE_FILE_URL, headers=HEADERS)
    resp.raise_for_status()
    df = pd.read_excel(io.BytesIO(resp.content), sheet_name='Respuestas de formulario 1')

    # Person ID
    df = df.rename(columns={'ID': 'id'})
    df['id'] = pd.to_numeric(df['id'], errors='coerce')
    df = df.dropna(subset=['id']).reset_index(drop=True)

    # Covariates
    df = df.rename(columns={'Sexo': 'cov_gender', 'Edad': 'cov_age'})
    cov_cols = ['cov_gender', 'cov_age']

    # Normalise column names for matching: strip whitespace, replace special chars
    # Original: 'ISRA(b) - 1', 'ISRA(b) - SIT - 1', "D´Flex - 1"
    # We match by checking original column names directly
    all_cols = list(df.columns)

    bapq_cols = [c for c in all_cols if c.startswith('BAPQ')]
    isra_b_cols = [c for c in all_cols
                   if c.startswith('ISRA(b)') and 'SIT' not in c]
    isra_b_sit_cols = [c for c in all_cols
                       if c.startswith('ISRA(b)') and 'SIT' in c]
    dflex_cols = [c for c in all_cols if c.startswith("D´Flex")]

    scale_col_map = {
        'BAPQ':       bapq_cols,
        'ISRA_b':     isra_b_cols,
        'ISRA_b_SIT': isra_b_sit_cols,
        'DFlex':      dflex_cols,
    }

    # Generic label maps  (original col -> item_NN)
    def make_label_map(cols, prefix):
        return {c: f"{prefix}_{i+1:02d}" for i, c in enumerate(cols)}

    label_maps = {
        'BAPQ':       make_label_map(bapq_cols, 'BAPQ'),
        'ISRA_b':     make_label_map(isra_b_cols, 'ISRA_b'),
        'ISRA_b_SIT': make_label_map(isra_b_sit_cols, 'ISRA_b_SIT'),
        'DFlex':      make_label_map(dflex_cols, 'DFlex'),
    }

    for scale_key, valid_min, valid_max, out_name in SCALES:
        item_cols_orig = scale_col_map[scale_key]
        lmap = label_maps[scale_key]

        sub = df[['id'] + cov_cols + item_cols_orig].copy()
        sub = sub.rename(columns=lmap)
        item_cols_renamed = list(lmap.values())

        long = sub.melt(
            id_vars=['id'] + cov_cols,
            value_vars=item_cols_renamed,
            var_name='item',
            value_name='resp'
        )

        long['resp'] = pd.to_numeric(long['resp'], errors='coerce')
        long = long.dropna(subset=['resp']).reset_index(drop=True)
        long = long[(long['resp'] >= valid_min) & (long['resp'] <= valid_max)].reset_index(drop=True)

        # Enforce column order
        long = long[['id', 'item', 'resp'] + cov_cols]

        out_path = os.path.join(OUT_DIR, out_name + '.csv')
        long.to_csv(out_path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
