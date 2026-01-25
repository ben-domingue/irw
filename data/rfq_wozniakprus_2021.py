import pandas as pd
import numpy as np
import re
import os

def convert_to_irw_split(input_file):
    print(f"Loading {input_file}...")
    try:
        df_all = pd.read_spss(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    scale_mapper = {
        'strongly disagree': 1, 'disagree': 2, 'somewhat disagree': 3,
        'neutral': 4, 'somewhat agree': 5, 'agree': 6, 'strongly agree': 7,
        'false': 0, 'true': 1,
        'no': 0, 'yes': 1
    }

    exclude_cols = ['Gender', 'Age', 'Area_of_study', 'Nationality', 'id']
    cols_to_map = [c for c in df_all.columns if c not in exclude_cols]

    for col in cols_to_map:
        if df_all[col].dtype == 'object' or hasattr(df_all[col], 'cat'):
            df_all[col] = df_all[col].astype(str).str.lower().str.strip()
            df_all[col] = df_all[col].replace(scale_mapper)
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

    if 'id' not in df_all.columns:
        df_all['id'] = df_all.index + 1

    rename_map = {
        'Age': 'cov_age',
        'Gender': 'cov_gender',
        'Area_of_study': 'cov_area_of_study',
        'Nationality': 'cov_nationality',
    }
    df_all.rename(columns=rename_map, inplace=True)
    
    covariate_cols = [c for c in df_all.columns if c.startswith('cov_')]
    
    target_prefixes = ['RFQ', 'GHQ', 'DERS', 'ECR', 'BPI']
 
    exclude_terms = [
        'Total', 'Sum', 'Score', 'Scale', 'Strategies', 'Goals', 
        'Impulse', 'Awareness', 'Clarity', 'Nonacceptance', '_IRT'
    ]

    for prefix in target_prefixes:
        print(f"Processing {prefix}...")

        current_item_cols = []
        for c in df_all.columns:
            if not c.startswith(prefix):
                continue
            if any(term in c for term in exclude_terms):
                continue
            pattern = rf"^{prefix}_?\d+$"
        
            if re.match(pattern, c):
                current_item_cols.append(c)
        
        if not current_item_cols:
            print(f"  No valid items found for {prefix}. Skipping.")
            continue
        
        keep_cols = ['id'] + covariate_cols + current_item_cols
        keep_cols = [c for c in keep_cols if c in df_all.columns]
        df_subset = df_all[keep_cols].copy()

        df_long = df_subset.melt(
            id_vars=['id'] + covariate_cols,
            value_vars=current_item_cols,
            var_name='item',   
            value_name='resp'  
        )

        df_long.columns = [c.lower() for c in df_long.columns]

        df_long.dropna(subset=['resp'], inplace=True)

        df_long = df_long[df_long['resp'] % 1 == 0]
        df_long['resp'] = df_long['resp'].astype(int)

        first_cols = ['id', 'item', 'resp']
        rest_cols = [c for c in df_long.columns if c not in first_cols]
        df_long = df_long[first_cols + rest_cols]

        output_filename = f"{prefix.lower()}_wozniakprus_2021.csv"
        df_long.to_csv(output_filename, index=False)
        print(f"Saved {len(df_long)} rows to '{output_filename}'")

if __name__ == "__main__":
    input_file = 'Wozniak-Prus_et_al_RFQ-8_study.sav' 
    convert_to_irw_split(input_file)