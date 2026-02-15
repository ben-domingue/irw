import pandas as pd
import re
import os

def convert_to_irw(input_file, output_prefix):
    
    try:
        df = pd.read_csv(input_file, sep=';')
        if df.shape[1] == 1:
             df = pd.read_csv(input_file, sep=',')
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    all_cols = df.columns.tolist()

    if 'id_unique' in df.columns:
        df.rename(columns={'id_unique': 'id'}, inplace=True)

    item_cols = []
    
    survey_prefixes = ('AMAS', 'GAD', 'STAI', 'TAI', 'SDQ', 'PISA', 'BFI', 'FSMAS')
    
    survey_items = [c for c in all_cols if c.startswith(survey_prefixes) 
                    and c[-1].isdigit() 
                    and not c.startswith('score_')]
    
    arith_items = [c for c in all_cols if c.startswith('arith_perf') and c.endswith('_acc')]
    
    item_cols = survey_items + arith_items

    exclude_cols = ['id'] + item_cols + [c for c in all_cols if c.endswith('_resp')]
    
    cov_cols = [c for c in df.columns if c not in exclude_cols]

    cov_rename_map = {c: f"cov_{c}" for c in cov_cols}
    df.rename(columns=cov_rename_map, inplace=True)
    
    arith_clean_map = {c: c.replace('_acc', '') for c in arith_items}
    df.rename(columns=arith_clean_map, inplace=True)

    cols_to_drop = ['cov_age_range', 'cov_id_sample']
    score_cols = [c for c in df.columns if (c.startswith('cov_score_') or c.startswith('cov_sum_'))]
    
    df.drop(columns=cols_to_drop + score_cols, inplace=True, errors='ignore')

    final_item_cols = survey_items + list(arith_clean_map.values())
    
    final_cov_cols = [c for c in df.columns if c.startswith('cov_')]
    
    df_long = df.melt(
        id_vars=['id'] + final_cov_cols,
        value_vars=final_item_cols,
        var_name='item',
        value_name='resp'
    )

    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = df_long['resp'].astype(int)

    def get_construct(item_name):
        match = re.match(r"([a-zA-Z_]+)\d+", item_name)
        if match:
            if 'arith' in match.group(1):
                return 'arithmetic'
            return match.group(1).rstrip('_') 
        return 'other'

    df_long['construct'] = df_long['item'].apply(get_construct)

    unique_constructs = df_long['construct'].unique()

    for construct in unique_constructs:
        df_subset = df_long[df_long['construct'] == construct].copy()
        df_subset.drop(columns=['construct'], inplace=True)
        
        cols = ['id', 'item', 'resp'] + sorted(final_cov_cols)
        df_subset = df_subset[cols]
        df_subset.sort_values(by=['id', 'item'], inplace=True)

        filename = f"{output_prefix}_{construct.lower()}.csv"
        df_subset.to_csv(filename, index=False)
        print(f"Saved: {filename} ({len(df_subset)} rows)")

if __name__ == "__main__":
    convert_to_irw('raw_data/AMATUS_dataset.csv', 'raw_data/amatus_cipora_2024')