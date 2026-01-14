#!/usr/bin/env python3
"""
This dataset contains:
- 43 items across multiple scales (IB, IH, PSY, EC, BC)
- 3 covariates (Age, Gender, Education)
- 552 participants
"""

import pandas as pd
import numpy as np

def convert_to_irw_format(input_file, output_file):
    df = pd.read_csv(input_file, sep=';', encoding='utf-8')
    
    covariate_cols = ['Age', 'Gender', 'Education']
    
    item_cols = [col for col in df.columns if col not in covariate_cols]
    
    long_data = []
    
    for idx, row in df.iterrows():
        person_id = idx + 1
        age = row['Age'] if pd.notna(row['Age']) else None
        gender = row['Gender'] if pd.notna(row['Gender']) else None
        education = row['Education'] if pd.notna(row['Education']) else None
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                long_data.append({
                    'id': person_id,
                    'item': item_col,
                    'resp': row[item_col],
                    'cov_age': age,
                    'cov_gender': gender,
                    'cov_education': education
                })
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    print(f"\nConversion complete! Output saved to {output_file}")
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/util/OUS-FR.csv"
    output_file = "/Users/francesraphael/projects/research/irw/util/OUS-FR_irw_format.csv"
    irw_data = convert_to_irw_format(input_file, output_file)


