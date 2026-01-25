import pandas as pd
import re
import os

def convert_to_irw(input_file):
    try:
        df = pd.read_spss(input_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    rename_map = {
        'PIN': 'id',
        'Age': 'cov_age',
        'Male': 'cov_gender',     
        'Language': 'cov_language',
        'Lang': 'cov_language_code',
        'Group': 'cov_group'
    }
    
    df.rename(columns=rename_map, inplace=True)
    
    df['cov_age'] = pd.to_numeric(df['cov_age'], errors='coerce')
    df['cov_age'] = df['cov_age'].astype('Int64')   
             
    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    base_vars = ['id'] + cov_cols
    base_vars = [c for c in base_vars if c in df.columns]
    
    all_srsi_items = []
    
    pattern = re.compile(r'^([a-zA-Z]+)(\d+)$')

    for col in df.columns:
        if col in base_vars: 
            continue
        
        match = pattern.match(col)
        if match:
            family_raw, item_suffix = match.groups()
            
            family = family_raw.lower()
            standard_item = f"{family}_{item_suffix}"
            
            all_srsi_items.append({
                'original_col': col,
                'item': standard_item
            })

    if not all_srsi_items:
        print("No items found matching the pattern.")
        return
    
    construct_cols = [x['original_col'] for x in all_srsi_items]

    df_subset = df[base_vars + construct_cols].copy()

    df_long = df_subset.melt(
        id_vars=base_vars,
        value_vars=construct_cols,
        var_name='original_col',
        value_name='resp'
    )

    meta_df = pd.DataFrame(all_srsi_items)
    df_long = pd.merge(df_long, meta_df, on='original_col', how='left')

    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)

    if (df_long['resp'] % 1 == 0).all():
        df_long['resp'] = df_long['resp'].astype(int)
    
    final_cols = ['id', 'item', 'resp'] + [c for c in cov_cols if c in df_long.columns]
    df_final = df_long[final_cols]

    output_filename = "srsi_dandachifitzgerald_2023.csv"
    df_final.to_csv(output_filename, index=False)
    print("Done processing data.")

if __name__ == "__main__":
    convert_to_irw('SRSI_Project1_Dutch_French_Equivalence.sav')