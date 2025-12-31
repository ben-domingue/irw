#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
import os

def convert_to_irw_format(input_file, output_file):
    df = pd.read_excel(input_file)
    
    non_item_cols = ['Time', 'Gndr', 'Age', 'AgeCat', 'Reg', 'Size', 'Edu', 'SubInc', 
                     'Vote', 'Vote_13', 'Ident', 'Vote_last', 'Vote_last_14', 'Ident_last',
                     'carelessLong', 'carelessMahal', 'careless', 'Tech', 'IntPol', 'IntSc',
                     'TrustPol', 'TrustPP', 'TrustGov', 'Relig']  # Relig is single item, treat as covariate
    
    item_cols = [c for c in df.columns if c not in non_item_cols]
    
    cov_cols = non_item_cols.copy()
    
    long_data = []
    
    for idx, row in df.iterrows():
        person_id = idx + 1
        
        covs = {}
        for col in cov_cols:
            if col in row:
                cov_name = f'cov_{col.lower()}'
                covs[cov_name] = row[col] if pd.notna(row[col]) else None
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                long_data.append({
                    'id': person_id,
                    'item': item_col,
                    'resp': row[item_col],
                    **covs
                })
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/science-related-populism/datacleaned_2023 ANONYM.xlsx"
    output_file = "/Users/francesraphael/projects/research/irw/science-related-populism/datacleaned_2023_irw_format.csv"
    
    irw_data = convert_to_irw_format(input_file, output_file)

