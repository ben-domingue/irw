import pandas as pd
import re
import os

def convert_to_irw(input_file):
    try:
        df = pd.read_csv(input_file, na_values=[' ', '', 'NA', 'nan'])
    except Exception as e:
        print(f"Error: {e}")
        return

    # 1. Rename Covariates (Standard IRW naming)
    rename_map = {
        'PptId': 'id',
        'REDCap_id': 'cov_redcap_id',
        'gender': 'cov_gender',
        'age': 'cov_age',
        'country': 'cov_country',
        'ethnicity': 'cov_ethnicity',
        'ethnicity_gen': 'cov_ethnicity_gen',
        'english': 'cov_english',
        'relationship': 'cov_relationship',
        'ic': 'cov_ic',
        'antibiotics_currentUTI': 'cov_antibiotics_current_uti',
        'antibiotics_preventUTI': 'cov_antibiotics_prevent_uti',
        'antibiotics_nonUTI': 'cov_antibiotics_non_uti',
        'supplement': 'cov_supplement',
        'other_nonantibiotic': 'cov_other_nonantibiotic',
        'TimeExclude': 'cov_time_exclude'
    }
    
    df.rename(columns=rename_map, inplace=True)
    
    if 'id' not in df.columns:
        if 'cov_redcap_id' in df.columns:
             df['id'] = df['cov_redcap_id']
        else:
             df['id'] = df.index + 1
             
    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    base_vars = ['id'] + cov_cols
    base_vars = [c for c in base_vars if c in df.columns]
    
    pattern = re.compile(r'^([a-zA-Z]+)(\d+)[_]([a-z0-9]+).*$')
    
    items_by_construct = {}
    
    exclude_keywords = ['check', 'other', 'timeexclude']

    for col in df.columns:
        if col in base_vars: 
            continue
        
        if any(k in col.lower() for k in exclude_keywords):
            continue
        
        match = pattern.match(col)
        if match:
            family_raw, wave, item_suffix = match.groups()
            family = family_raw.lower()
            
            standard_item = f"{family}_{item_suffix}"
            
            if family not in items_by_construct:
                items_by_construct[family] = []
            
            items_by_construct[family].append({
                'original_col': col,
                'wave': int(wave),
                'item': standard_item
            })

    for construct, item_list in items_by_construct.items():
        
        construct_cols = [x['original_col'] for x in item_list]

        df_subset = df[base_vars + construct_cols].copy()

        df_long = df_subset.melt(
            id_vars=base_vars,
            value_vars=construct_cols,
            var_name='original_col',
            value_name='resp'
        )
        
        meta_df = pd.DataFrame(item_list)
        df_long = pd.merge(df_long, meta_df, on='original_col', how='left')
        
        df_long.dropna(subset=['resp'], inplace=True)
        df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
        df_long.dropna(subset=['resp'], inplace=True)
        
        if (df_long['resp'] % 1 == 0).all():
            df_long['resp'] = df_long['resp'].astype(int)
        
        final_cols = ['id', 'item', 'resp', 'wave'] + [c for c in cov_cols if c in df_long.columns]
        df_final = df_long[final_cols]

        output_filename = f"uti_newlands_2023_{construct}.csv"
        df_final.to_csv(output_filename, index=False)

    print("Done processing data.")

if __name__ == "__main__":
    convert_to_irw('Raw data pre-exploratory factor analysis.csv')