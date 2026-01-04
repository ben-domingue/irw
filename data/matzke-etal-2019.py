#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import glob
import pyreadr

def load_rdata_file(file_path):
    result = pyreadr.read_r(file_path)
    if result:
        df = list(result.values())[0]
        print(f"  Loaded via pyreadr: {df.shape}")
        return df

def convert_osari_to_irw(df, experiment_name):
    id_col = None
    for col in ['s', 'participant', 'subject', 'id']:
        if col in df.columns:
            id_col = col
            break
    
    if id_col is None:
        df['id'] = df.index + 1
        id_col = 'id'
    else:
        df = df.rename(columns={id_col: 'id'})
    
    item_parts = []
    if 'SS' in df.columns:
        item_parts.append('SS')
    if 'S' in df.columns:
        item_parts.append('S')
    if 'D' in df.columns:
        item_parts.append('D')
    
    if item_parts:
        df['item'] = df[item_parts].apply(lambda x: '_'.join([str(val) for val in x]), axis=1)
    else:
        df['item'] = df.groupby('id').cumcount() + 1
        df['item'] = 'trial_' + df['item'].astype(str)
    
    if 'R' in df.columns:
        def convert_response(r):
            if pd.isna(r):
                return 0
            r_str = str(r).upper()
            if r_str in ['R1', 'RIGHT', '1']:
                return 1
            elif r_str in ['NR', 'NO RESPONSE', '0']:
                return 0
            elif r_str in ['LEFT', '-1']:
                return -1
            else:
                try:
                    return float(r)
                except:
                    return 0
        
        df['resp'] = df['R'].apply(convert_response)
    else:
        df['resp'] = 0
    
    cov_cols = []
    for col in df.columns:
        if col not in ['id', 'item', 'resp', 'R']:
            cov_cols.append(col)
    
    cov_rename = {}
    for col in cov_cols:
        new_name = f'cov_{col.lower()}'
        cov_rename[col] = new_name
    
    df = df.rename(columns=cov_rename)
    
    irw_cols = ['id', 'item', 'resp']
    irw_cols.extend([c for c in df.columns if c.startswith('cov_')])
    
    irw_df = df[irw_cols].copy()
    
    if 'cov_rt' in irw_df.columns:
        irw_df = irw_df.rename(columns={'cov_rt': 'rt'})
    
    if 'cov_ssd' in irw_df.columns:
        irw_df['cov_ssd'] = irw_df['cov_ssd'].replace([np.inf, -np.inf], np.nan)
    
    irw_df = irw_df.drop_duplicates()
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    
    return irw_df

def convert_all_osari_files(data_dir, output_dir):
    rdata_files = glob.glob(os.path.join(data_dir, "*.RData"))
    
    if not rdata_files:
        raise ValueError(f"No RData files found in {data_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for rdata_file in sorted(rdata_files):
        file_name = os.path.basename(rdata_file)
        experiment_name = os.path.splitext(file_name)[0]
        
        
        try:
            df = load_rdata_file(rdata_file)
            
            irw_df = convert_osari_to_irw(df, experiment_name)
            
            output_file = os.path.join(output_dir, f"{experiment_name}_irw_format.csv")
            irw_df.to_csv(output_file, index=False)
            print(f"  Saved to: {output_file}")
            
            irw_df['cov_experiment'] = experiment_name
            
        except Exception as e:
            print(f"  ERROR processing {file_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    import sys
    
    data_dir = "/Users/francesraphael/projects/research/irw/osari/data"
    output_dir = "/Users/francesraphael/projects/research/irw/osari"
    
    try:
        convert_all_osari_files(data_dir, output_dir)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

