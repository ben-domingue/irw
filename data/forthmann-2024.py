#!/usr/bin/env python3
"""
1. cleverness_ratings.csv - ratings from multiple raters for objects
2. creative_quality_ratings.csv - creative quality ratings from multiple raters
3. prediciton_modeling.csv - similar to creative_quality_ratings with additional features
4. response_frequency_data.csv - response frequency data for ideas
"""

import pandas as pd
import numpy as np
import os

def convert_cleverness_ratings(input_file, output_file):
    df = pd.read_csv(input_file, encoding='latin-1')
    
    long_data = []
    
    objects = ['paperclip', 'garbagebag', 'rope']
    
    for _, row in df.iterrows():
        subject_id = row['subject_id']
        
        for obj in objects:
            for rater_num in range(1, 6):
                col_name = f'cleverness.rater{rater_num}.{obj}'
                if col_name in row and pd.notna(row[col_name]):
                    long_data.append({
                        'id': subject_id,
                        'item': obj,
                        'resp': row[col_name],
                        'rater': f'rater{rater_num}'
                    })
    
    irw_df = pd.DataFrame(long_data)
    irw_df = irw_df.drop_duplicates().sort_values(['id', 'item', 'rater']).reset_index(drop=True)
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

def convert_creative_quality_ratings(input_file, output_file, frequency_file=None):
    df = pd.read_csv(input_file, encoding='latin-1')
    
    freq_data = None
    if frequency_file and os.path.exists(frequency_file):
        freq_df = pd.read_csv(frequency_file, encoding='latin-1')
        freq_data = {}
        for _, row in freq_df.iterrows():
            key = (row['subject_id'], row['idea'])
            freq_data[key] = {
                'freq': row['Freq'] if pd.notna(row['Freq']) else None,
                'idea_type': row['idea_type'] if pd.notna(row['idea_type']) else None
            }
        print(f"  Loaded frequency data for {len(freq_data)} idea-subject combinations")
    
    long_data = []
    
    # Rater columns
    rater_cols = ['creativeq.rater4', 'creativeq.rater6', 'creativeq.rater7']
    
    for _, row in df.iterrows():
        subject_id = row['subject_id']
        idea = row['idea'] if pd.notna(row['idea']) else None
        obj = row['object'] if pd.notna(row['object']) else None
        obj_engl = row['obj_engl'] if pd.notna(row['obj_engl']) else None
        
        item_id = idea if idea else f"{subject_id}_{obj}"
        
        item_freq = None
        item_idea_type = None
        if freq_data and idea:
            key = (subject_id, idea)
            if key in freq_data:
                item_freq = freq_data[key]['freq']
                item_idea_type = freq_data[key]['idea_type']
        
        for rater_col in rater_cols:
            if rater_col in row and pd.notna(row[rater_col]):
                rater_name = rater_col.replace('creativeq.', '')
                row_data = {
                    'id': subject_id,
                    'item': item_id,
                    'resp': row[rater_col],
                    'rater': rater_name,
                    'cov_object': obj_engl if obj_engl else obj
                }
                
                if item_freq is not None:
                    row_data['itemcov_frequency'] = item_freq
                if item_idea_type is not None:
                    row_data['itemcov_idea_type'] = item_idea_type
                
                long_data.append(row_data)
    
    irw_df = pd.DataFrame(long_data)
    irw_df = irw_df.drop_duplicates().sort_values(['id', 'item', 'rater']).reset_index(drop=True)
    irw_df.to_csv(output_file, index=False)
    
    if 'itemcov_frequency' in irw_df.columns:
        print(f"  Added itemcov_frequency and itemcov_idea_type from frequency data")
    
    return irw_df

def convert_prediction_modeling(input_file, output_file):
    df = pd.read_csv(input_file, encoding='latin-1')
    
    long_data = []
    
    rater_cols = ['creativeq.rater4', 'creativeq.rater6', 'creativeq.rater7']
    
    for _, row in df.iterrows():
        subject_id = row['subject_id']
        idea = row['idea'] if pd.notna(row['idea']) else None
        obj = row['object'] if pd.notna(row['object']) else None
        obj_engl = row['obj_engl'] if pd.notna(row['obj_engl']) else None
        
        item_id = idea if idea else f"{subject_id}_{obj}"
        
        for rater_col in rater_cols:
            if rater_col in row and pd.notna(row[rater_col]):
                rater_name = rater_col.replace('creativeq.', '')
                
                row_data = {
                    'id': subject_id,
                    'item': item_id,
                    'resp': row[rater_col],
                    'rater': rater_name,
                    'cov_object': obj_engl if obj_engl else obj
                }
                
                
                long_data.append(row_data)
    
    irw_df = pd.DataFrame(long_data)
    irw_df = irw_df.drop_duplicates().sort_values(['id', 'item', 'rater']).reset_index(drop=True)
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

def convert_response_frequency_data(input_file, output_file):
    df = pd.read_csv(input_file, encoding='latin-1')
    
    long_data = []
    
    for _, row in df.iterrows():
        subject_id = row['subject_id']
        idea = row['idea'] if pd.notna(row['idea']) else None
        obj = row['object'] if pd.notna(row['object']) else None
        idea_type = row['idea_type'] if pd.notna(row['idea_type']) else None
        freq = row['Freq'] if pd.notna(row['Freq']) else None
        
        if idea and pd.notna(freq):
            item_id = idea
            
            long_data.append({
                'id': subject_id,
                'item': item_id,
                'resp': freq,
                'cov_object': obj,
                'cov_idea_type': idea_type
            })
    
    irw_df = pd.DataFrame(long_data)
    irw_df = irw_df.drop_duplicates().sort_values(['id', 'item']).reset_index(drop=True)
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

def convert_covariates_to_irw(input_file, output_file):
    df = pd.read_csv(input_file, encoding='latin-1')
    
    # Rename subject_id to id
    df = df.rename(columns={'subject_id': 'id'})
    
    # Add cov_ prefix to all columns except id
    covariate_cols = [col for col in df.columns if col != 'id']
    cov_rename = {col: f'cov_{col}' for col in covariate_cols}
    df = df.rename(columns=cov_rename)
    
    # Sort by id for consistency
    df = df.sort_values('id').reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    return df

def merge_covariates_into_irw_files(base_dir, covariates_file):
    covariates_converted = covariates_file.replace('.csv', '_irw_format.csv')
    if os.path.exists(covariates_converted):
        # Load the already-converted covariates file
        cov = pd.read_csv(covariates_converted, encoding='latin-1')
        cov_cols = [col for col in cov.columns if col.startswith('cov_')]
    else:
        # Load and convert covariates
        cov = pd.read_csv(covariates_file, encoding='latin-1')
        cov = cov.rename(columns={'subject_id': 'id'})
        cov_cols = [col for col in cov.columns if col != 'id']
        cov_rename = {col: f'cov_{col}' for col in cov_cols}
        cov = cov.rename(columns=cov_rename)
    
    irw_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('_irw_format.csv') and 'covariates' not in file:
                irw_files.append(os.path.join(root, file))
    
    
    for irw_file in irw_files:
        df = pd.read_csv(irw_file)
        
        # Merge covariates
        df_merged = df.merge(cov, on='id', how='left')
        
        # Save back to file
        df_merged.to_csv(irw_file, index=False)
    
    return cov

if __name__ == "__main__":
    base_dir = "/Users/francesraphael/projects/research/irw/diverge"
    
    
    # Convert cleverness_ratings
    cleverness_input = f"{base_dir}/Rating data/cleverness_ratings.csv"
    cleverness_output = f"{base_dir}/Rating data/cleverness_ratings_irw_format.csv"
    if os.path.exists(cleverness_input):
        convert_cleverness_ratings(cleverness_input, cleverness_output)
        print()
    
    # Convert creative_quality_ratings (incorporate frequency data as itemcov_)
    creative_input = f"{base_dir}/Rating data/creative_quality_ratings.csv"
    creative_output = f"{base_dir}/Rating data/creative_quality_ratings_irw_format.csv"
    freq_input = f"{base_dir}/Response frequency data/response_frequency_data.csv"
    if os.path.exists(creative_input):
        # Pass frequency file to incorporate as itemcov_ columns
        convert_creative_quality_ratings(creative_input, creative_output, frequency_file=freq_input if os.path.exists(freq_input) else None)
        print()
    
    covariates_file = f"{base_dir}/Person-level covariates/covariates.csv"
    if os.path.exists(covariates_file):
        merge_covariates_into_irw_files(base_dir, covariates_file)
        print()
    
