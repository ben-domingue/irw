#!/usr/bin/env python3
"""
1. Golleretal2020.csv - 36 items (T1-T36)
2. Kaneetal2016.csv - 112 items across multiple scales
3. Zanescoetal2020.csv - 28 items (Probe1-Probe28)
"""

import pandas as pd
import numpy as np
import os

def convert_to_irw_format(input_file, output_file):
    df = pd.read_csv(input_file, encoding='utf-8')
    
    id_col = None
    for col in df.columns:
        if col.lower() in ['id', 'subject']:
            id_col = col
            break
    
    if id_col is None:
        raise ValueError(f"Could not find ID column in {input_file}")
    
    exclude_cols = [c for c in df.columns if c.lower() in ['exclude', 'exclusions']]
    
    item_cols = [c for c in df.columns if c not in [id_col] + exclude_cols]
    
    if exclude_cols:
        print(f"  Exclusion columns: {exclude_cols}")
    
    long_data = []
    
    for _, row in df.iterrows():
        person_id = row[id_col]
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                long_data.append({
                    'id': person_id,
                    'item': item_col,
                    'resp': row[item_col]
                })
    
    irw_df = pd.DataFrame(long_data)
    irw_df = irw_df.drop_duplicates().sort_values(['id', 'item']).reset_index(drop=True)
    irw_df.to_csv(output_file, index=False)
    
    print(f"  Output: {os.path.basename(output_file)}")
    
    return irw_df

if __name__ == "__main__":
    base_dir = "/Users/francesraphael/projects/research/irw/mind_wandering"
    
    
    files_to_convert = [
        ('Golleretal2020.csv', 'Golleretal2020_irw_format.csv'),
        ('Kaneetal2016.csv', 'Kaneetal2016_irw_format.csv'),
        ('Zanescoetal2020.csv', 'Zanescoetal2020_irw_format.csv')
    ]
    
    for input_name, output_name in files_to_convert:
        input_file = f"{base_dir}/{input_name}"
        output_file = f"{base_dir}/{output_name}"
        
        if os.path.exists(input_file):
            print(f"Converting {input_name}...")
            convert_to_irw_format(input_file, output_file)
            print()
        else:
            print(f"Warning: {input_file} not found\n")
    



