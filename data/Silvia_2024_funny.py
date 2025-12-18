#!/usr/bin/env python3
"""
- id: person identifier
- item: item identifier (the 8 items: hid1-hid4, hef1-hef4)
- resp: response value
- cov_identity: covariate for identity
- cov_efficacy: covariate for efficacy
- cov_age: covariate for age
- cov_gender: covariate for gender
"""

import pandas as pd
import numpy as np

def convert_to_irw_format(input_file, output_file):
    df = pd.read_csv(input_file)
    
    item_cols = [col for col in df.columns if col not in ['id', 'identity', 'efficacy', 'age', 'gender']]
    
    
    long_data = []
    
    for _, row in df.iterrows():
        person_id = row['id']  # This becomes our 'id'
        identity = row['identity'] if pd.notna(row['identity']) else None  # Covariate
        efficacy = row['efficacy'] if pd.notna(row['efficacy']) else None  # Covariate
        age = row['age'] if pd.notna(row['age']) else None  # Covariate
        gender = row['gender'] if pd.notna(row['gender']) else None  # Covariate
        
        for item_col in item_cols:
            if pd.notna(row[item_col]):
                long_data.append({
                    'id': person_id,
                    'item': item_col,
                    'resp': row[item_col],
                    'cov_identity': identity,
                    'cov_efficacy': efficacy,
                    'cov_age': age,
                    'cov_gender': gender
                })
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/funny/data.csv"
    output_file = "/Users/francesraphael/projects/research/irw/funny/data_irw_format.csv"
    
    irw_data = convert_to_irw_format(input_file, output_file)

##exported as silvia_2024_funny
