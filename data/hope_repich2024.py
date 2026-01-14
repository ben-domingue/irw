#!/usr/bin/env python3
"""
Convert hope_n106.xlsx.xlsx to IRW data standard.

- id: person identifier
- item: item identifier (the 42 items from various scales)
- resp: response value
- cov_sex: covariate for sex
- cov_age: covariate for age
"""

import pandas as pd
import numpy as np

def convert_to_irw_format(input_file, output_file):

    df = pd.read_excel(input_file)
    
    item_cols = [col for col in df.columns if col not in ['id', ' sex', 'age']]
    
    long_data = []
    
    for _, row in df.iterrows():
        person_id = row['id']
        sex = row[' sex'] if pd.notna(row[' sex']) else None
        age = row['age'] if pd.notna(row['age']) else None
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                long_data.append({
                    'id': person_id,
                    'item': item_col,
                    'resp': row[item_col],
                    'cov_sex': sex,
                    'cov_age': age
                })
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/hope/hope_n106.xlsx.xlsx"
    output_file = "/Users/francesraphael/projects/research/irw/hope/hope_n106_irw_format.csv"
    
    irw_data = convert_to_irw_format(input_file, output_file)
