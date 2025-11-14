#!/usr/bin/env python3
"""
Convert les_expert_level_long_hh.csv to IRW data standard format.

This script transforms the wide format data into the IRW standard with:
- id: party identifier
- item: item identifier
- resp: response value
- rater: expert identifier
- date: timestamp of response
"""

import pandas as pd
import numpy as np
from datetime import datetime

def convert_to_irw_format(input_file, output_file):
    df = pd.read_csv(input_file, sep=';')
    
    items = [
        "leftrightgeneral", "lrecon", "galtan", "genderlanguage", "genderroles",
        "childcare", "communityschool", "antielitism", "peoplecentrism", "publicdebt",
        "migrantbenefit", "assimilation", "liberalism", "climatepolicy", "immigration",
        "lawandorder", "missiles", "rentcontrol", "ukraine", "publicbroadcast", "asylum"
    ]
    
    long_data = []
    
    for _, row in df.iterrows():
        party = row['party']  
        expert_id = row['expert_id']  
        datestamp = row['datestamp']  
        context = row['bl']  
        
        
        party_id = f"{party}_{context}"
        
        
        for item in items:
            if item in row and pd.notna(row[item]):
                long_data.append({
                    'id': party_id,
                    'item': item,
                    'resp': row[item],
                    'rater': expert_id,
                    'date': datestamp
                })
    
    
    irw_df = pd.DataFrame(long_data)
    
    
    
    irw_df['date'] = pd.to_datetime(irw_df['date'])
    irw_df['date'] = irw_df['date'].astype('int64') // 10**9
    
    
    irw_df = irw_df.drop_duplicates()
    
    
    irw_df = irw_df.sort_values(['id', 'item', 'rater']).reset_index(drop=True)
    
    # Save to CSV
    irw_df.to_csv(output_file, index=False)
    
    
    # Debug confirm 
    context_counts = irw_df['id'].str.split('_').str[1].value_counts()
    print(context_counts)
    
    return irw_df

if __name__ == "__main__":
    input_file = "/Users/francesraphael/projects/research/irw/dataverse_files/les_expert_level_long_hh.csv"
    output_file = "/Users/francesraphael/projects/research/irw/les_expert_level_irw_format.csv"
    
    # Convert the data
    irw_data = convert_to_irw_format(input_file, output_file)
