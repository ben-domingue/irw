#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import re

def convert_inperson_to_irw(input_file, output_file):
    
    df = pd.read_excel(input_file)
    
    id_col = 'Participant number'
    df = df.rename(columns={id_col: 'id'})
    
    item_score_cols = [col for col in df.columns if 'item' in col.lower() and 'score' in col.lower() and 'rater' in col.lower()]
    
    exclude_cols = ['id'] + item_score_cols
    exclude_cols.extend([col for col in df.columns if 'total' in col.lower() and 'score' in col.lower()])
    exclude_cols.extend([col for col in df.columns if 'first score' in col.lower() or 'highest score' in col.lower()])
    
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    metadata_cols = ['Date of intervention', 'Date of outcome assessment']
    time_cols = [col for col in cov_cols if 'time' in col.lower() or 'spent' in col.lower() or 'start time' in col.lower() or 'duration' in col.lower()]
    cov_cols = [col for col in cov_cols if col not in time_cols and col not in metadata_cols]
    
    long_data = []
    
    for idx, row in df.iterrows():
        person_id = row['id']
        
        covs = {}
        for col in cov_cols:
            if col in row and pd.notna(row[col]):
                cov_name = f'cov_{col.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").replace("?", "").replace("/", "_")}'
                cov_name = re.sub('_+', '_', cov_name)
                covs[cov_name] = row[col]
        
        for col in item_score_cols:
            match = re.search(r'scenario\s+(\d+).*item\s+(\d+).*rater\s+(\d+)', col, re.IGNORECASE)
            if match:
                scenario = int(match.group(1))
                item_num = int(match.group(2))
                rater = int(match.group(3))
                
                item_id = f'scenario{scenario}_item{item_num}'
                
                resp = row[col]
                
                if pd.isna(resp):
                    continue
                
                row_data = {
                    'id': person_id,
                    'item': item_id,
                    'resp': float(resp) if pd.notna(resp) else np.nan,
                    'rater': rater,
                    **covs
                }
                
                long_data.append(row_data)
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item', 'rater']).reset_index(drop=True)
    
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

if __name__ == "__main__":
    import sys
    
    input_file = "/Users/francesraphael/projects/research/irw/inperson/Dataset 1. The data file contains de-identified outcome assessment data of study participants"
    output_file = "/Users/francesraphael/projects/research/irw/inperson/inperson_irw_format.csv"
    
    try:
        convert_inperson_to_irw(input_file, output_file)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

