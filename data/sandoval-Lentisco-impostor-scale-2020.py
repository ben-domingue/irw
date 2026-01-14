#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os

def convert_to_irw_format(input_file, output_file):
    df = pd.read_excel(input_file)
    
    id_col = 'ID'
    cov_cols = ['Edad', 'Genero', 'Estudios', 'Curso']
    
    item_cols = [c for c in df.columns if c not in [id_col] + cov_cols 
                 and not c.endswith('_total') and not c.endswith('_Total') 
                 and not c.endswith('_xtotal') and not c.endswith('_Xtotal')
                 and 'total' not in c.lower()]
    
    
    scales = {}
    for col in item_cols:
        col_clean = col.strip()
        scale_name = col_clean.split('_')[0]
        if scale_name not in scales:
            scales[scale_name] = []
        scales[scale_name].append(col)
    
    long_data = []
    
    for _, row in df.iterrows():
        person_id = row[id_col]
        
        covs = {}
        for col in cov_cols:
            if col in row and pd.notna(row[col]):
                cov_name = f'cov_{col.lower()}'
                covs[cov_name] = row[col]
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                item_name = item_col.strip()
                
                long_data.append({
                    'id': person_id,
                    'item': item_name,
                    'resp': row[item_col],
                    **covs
                })
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/impostor/Final_database.xlsx"
    output_file = "/Users/francesraphael/projects/research/irw/impostor/Final_database_irw_format.csv"
    
    irw_data = convert_to_irw_format(input_file, output_file)

