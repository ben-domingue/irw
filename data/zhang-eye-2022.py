#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import re

def convert_eye_to_irw(input_file, output_file):
    
    df = pd.read_excel(input_file, sheet_name='Sheet1')
    
    df_filtered = df[df['IA_ID'] == 1].copy()
    
    id_col = 'subject'
    df_filtered = df_filtered.rename(columns={id_col: 'id'})
    
    item_col = 'trial'
    df_filtered = df_filtered.rename(columns={item_col: 'item'})
    resp_col = 'RA'
    df_filtered = df_filtered.rename(columns={resp_col: 'resp'})
    
    if 'RT' in df_filtered.columns:
        # Convert RT from milliseconds to seconds
        df_filtered['rt'] = df_filtered['RT'] / 1000.0
        df_filtered = df_filtered.drop(columns=['RT'])
    
    eye_measure_cols = [
        'IA_DWELL_TIME', 'IA_DWELL_TIME_%', 'IA_FIRST_RUN_DWELL_TIME',
        'TRIAL_DWELL_TIME', 'toggle', 'toggle_rate'
    ]
    
    # Rename eye movement measures with itemcov_ prefix
    itemcov_rename = {}
    for col in eye_measure_cols:
        if col in df_filtered.columns:
            new_name = f'itemcov_{col.lower().replace("_", "_").replace("%", "pct")}'
            itemcov_rename[col] = new_name
    
    df_filtered = df_filtered.rename(columns=itemcov_rename)
    
    if 'IA_ID' in df_filtered.columns:
        df_filtered = df_filtered.drop(columns=['IA_ID'])
    
    keep_cols = ['id', 'item', 'resp']
    if 'rt' in df_filtered.columns:
        keep_cols.append('rt')
    keep_cols.extend([col for col in df_filtered.columns if col.startswith('itemcov_')])
    
    irw_df = df_filtered[keep_cols].copy()
    
    irw_df = irw_df.dropna(subset=['resp'])
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    # Save to CSV
    irw_df.to_csv(output_file, index=False)
    return irw_df

if __name__ == "__main__":
    import sys
    
    input_file = "/Users/francesraphael/projects/research/irw/eye/eye-data.xlsx"
    output_file = "/Users/francesraphael/projects/research/irw/eye/eye_irw_format.csv"
    
    try:
        convert_eye_to_irw(input_file, output_file)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

