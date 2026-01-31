import pandas as pd
import pyreadstat
import os
import re

def convert_to_irw(file1, output_name):
    
    try:
        df, meta = pyreadstat.read_sav(file1, apply_value_formats=True)
        print(f"Loaded data: {df.shape}")
    except Exception as e:
        print(f"Error loading {file1}: {e}")
        return

    cov_map = {
        'age': 'cov_age',
        'gender': 'cov_gender',
        'Grupo': 'cov_grupo',
        'fobcode': 'cov_fobcode',
        'fobgender': 'cov_fobgender',
        'subjectno': 'cov_subjectno'
    }
    
    existing_covs = {k: v for k, v in cov_map.items() if k in df.columns}
    df.rename(columns=existing_covs, inplace=True)

    if 'id' not in df.columns:
        df['id'] = (df.index + 1).astype(str)
    else:
        df['id'] = df['id'].astype(str)

    item_cols = [c for c in df.columns if c.startswith('cb')]

    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='original_item',
        value_name='resp'
    )
    
    to_int_cols = [
    'resp', 'cov_subjectno', 'cov_grupo', 'cov_age']
    
    for col in to_int_cols:
        if col in df_long.columns:
            df_long[col] = df_long[col].astype('Int64')

    df_long.dropna(subset=['resp'], inplace=True)
    df_long['item'] = df_long['original_item']

    base_cols = ['id', 'item', 'resp']
    cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
    final_cols = base_cols + [c for c in cov_cols if c not in base_cols]
    
    df_final = df_long[final_cols]

    df_final.to_csv(output_name, index=False)

    print("\nDone processing data.")

if __name__ == "__main__":
    convert_to_irw(
        'raw_data/BancoBPM-P_N=793_final_blind.sav', 'raw_data/ebp_tafla_2024.csv')