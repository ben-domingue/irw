import pandas as pd

def convert_to_irw(input_file):
    try:
        df = pd.read_csv(input_file, na_values=[' ', '', 'NA', 'nan'])
    except Exception as e:
        print(f"Error: {e}")
        return

    rename_map = {
        'AGE': 'cov_age',
        'GENDER': 'cov_gender',
        'COUNTRY': 'cov_country'
    }
    
    df.rename(columns=rename_map, inplace=True)
    
    if 'id' not in df.columns:
        df['id'] = df.index + 1

    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    base_vars = ['id'] + cov_cols
    base_vars = [c for c in base_vars if c in df.columns]
    
    items_by_construct = {}
    
    exclude_keywords = ['check', 'other', 'timeexclude']

    for col in df.columns:
        if col in base_vars: 
            continue
        
        if any(k in col.lower() for k in exclude_keywords):
            continue
        
        if '_' in col:
            parts = col.rsplit('_', 1)
            # Check if the suffix is a number (the item number)
            if len(parts) == 2 and parts[1].isdigit():
                family_raw = parts[0]
                item_suffix = parts[1]
                
                family = family_raw.lower()
                
                standard_item = f"{family}_{item_suffix}"
                
                if family not in items_by_construct:
                    items_by_construct[family] = []
                
                items_by_construct[family].append({
                    'original_col': col,
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

        final_cols = ['id', 'item', 'resp'] + [c for c in cov_cols if c in df_long.columns]
        df_final = df_long[final_cols]

        filename_part = construct.split('.')[0]
        output_filename = f"assessment_time_fournier_2026_{filename_part}.csv"
        df_final.to_csv(output_filename, index=False)
        print(f"Created: {output_filename}")

    print("Done processing data.")

if __name__ == "__main__":
    convert_to_irw('Anonymized processed non-pilot data_eval.csv')