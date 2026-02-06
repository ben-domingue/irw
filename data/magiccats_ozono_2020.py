import pandas as pd
import os
import re

def convert_to_irw(file1, output_name):
    
    try:
        df = pd.read_csv(file1)
    except Exception as e:
        print(f"Error loading {file1}: {e}")
        return

    cov_map = {
        'Participant ID': 'id',
        'Age': 'cov_age',
        'Gender': 'cov_gender'
    }
    
    existing_covs = {k: v for k, v in cov_map.items() if k in df.columns}
    df.rename(columns=existing_covs, inplace=True)

    item_cols = df.columns[3:]

    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='original_item',
        value_name='resp'
    )

    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = df_long['resp'].astype(int)
    
    df_long['item'] = df_long['original_item']

    base_cols = ['id', 'item', 'resp']
    cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
    final_cols = base_cols + [c for c in cov_cols if c not in base_cols]
    
    df_final = df_long[final_cols]

    df_final.to_csv(output_name, index=False)

    print("\nDone processing data.")

if __name__ == "__main__":
    convert_to_irw(
        'raw_data/participants_data.csv', 'raw_data/magiccats_ozono_2020.csv')