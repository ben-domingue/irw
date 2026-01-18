import pandas as pd
import re
import numpy as np

def convert_to_irw(input_file, output_file):
    try:
        df = pd.read_csv(input_file, na_values=[' ', '', 'NA', 'nan'])
    except Exception as e:
        print(f"Error: {e}")
        return

    rename_map = {
        'PptId': 'id',  # Primary ID
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
    id_vars = ['id'] + cov_cols
    id_vars = [c for c in id_vars if c in df.columns]

    # Identify item columns 
    pattern = re.compile(r'^([a-zA-Z]+)(\d+)[_](.+)$')
    
    item_cols = []
    metadata = {} 
    
    for col in df.columns:
        if col in id_vars: continue
        
        match = pattern.match(col)
        if match:
            family, wave, suffix = match.groups()
            item_cols.append(col)
            
            # Standardize names
            # item: family + "_" + suffix (e.g. phq_1, rutiiq_a1)
            standard_item = f"{family}_{suffix}"
            
            metadata[col] = {
                'item_family': family.upper(), # e.g. PHQ, GAD
                'wave': int(wave),
                'item': standard_item
            }
            
    if not item_cols:
        print("Error: No item columns found matching the pattern 'NameWave_Item'.")
        return

    # Long format
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='original_col',
        value_name='resp'
    )
    
    meta_df = pd.DataFrame.from_dict(metadata, orient='index').reset_index()
    meta_df.columns = ['original_col', 'item_family', 'wave', 'item']
    
    df_long = pd.merge(df_long, meta_df, on='original_col', how='left')
    
    df_long.dropna(subset=['resp'], inplace=True)
    
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True) 
    
    non_int_rows = df_long[df_long['resp'] % 1 != 0]

    print(f"Found {len(non_int_rows)} non-integer rows.")
    print(non_int_rows[['id', 'item', 'resp']].head(10))
    breakpoint()
    if (df_long['resp'] % 1 == 0).all():
        df_long['resp'] = df_long['resp'].astype(int)

    base_cols = ['id', 'item', 'resp', 'wave', 'item_family']
    final_cols = base_cols + [c for c in cov_cols if c in df_long.columns]
    
    df_long = df_long[final_cols]
    
    df_long.to_csv(output_file, index=False)
    print("Done processing the data.")

if __name__ == "__main__":
    convert_to_irw('Raw data pre-exploratory factor analysis.csv', 'uti_newlands_2023.csv')