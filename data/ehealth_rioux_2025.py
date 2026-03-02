import pandas as pd
import numpy as np
import re


def convert_to_irw(input_csv):
    df = pd.read_csv(input_csv)
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    
    df = df.rename(columns={'Random_ID': 'id'})
    
    rse_cols = [c for c in df.columns if re.match(r'^RSE(\d+|_noanswer)$', c)]
    answered_rse = df[rse_cols].notna().any(axis=1) # check at least 1 box?
    df.loc[answered_rse, rse_cols] = df.loc[answered_rse, rse_cols].fillna(0)
    
    item_patterns = {
        'Abiliti': r'^Abiliti_\d+$',
        'BEAM': r'^BEAM_\d+$',
        'TripleP': r'^TripleP_\d+$',
        'PSI': r'^PSI\d+$',
        'GAD': r'^GAD\d+$',
        'PHQ': r'^PHQ\d+$',
        'MSSPS': r'^MSSPS_\d+$',
        'RSE': r'^RSE(\d+|_noanswer)$',
        'RSES': r'^RSES\d+$'
    }
    
    all_items = []
    for pattern in item_patterns.values():
        all_items.extend([c for c in df.columns if re.match(pattern, c)])
    
    special_maps = {
        'RecordedDate': 'date',
        'Duration__in_seconds_': 'rt'
    }
    covariates = [c for c in df.columns if c not in all_items and c != 'id' and c not in special_maps.keys()]
    df = df.rename(columns=special_maps)
    
    # Convert 'date' to Unix time
    df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
    df['date'] = df['date'].apply(
        lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA
    ).astype('Int64')

    rename_map = {c: f'cov_{c.lower()}' for c in covariates}
    df = df.rename(columns=rename_map)
    
    for construct_name, pattern in item_patterns.items():
        c_items = [c for c in all_items if re.match(pattern, c)]
        
        if not c_items: 
            continue
        id_vars = ['id', 'date', 'rt'] + list(rename_map.values())
        df_long = pd.melt(
            df,
            id_vars=id_vars,
            value_vars=c_items,
            var_name='item',
            value_name='resp'
        )
        
        df_long = df_long.dropna(subset=['resp'])
        df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
        df_long = df_long.dropna(subset=['resp'])
        df_long['resp'] = df_long['resp'].astype(int)
        
        final_cols = ['id', 'item', 'resp', 'rt', 'date'] + list(rename_map.values())
        df_long = df_long[final_cols]
        
        df_long = df_long.sort_values(
            by=['id', 'item'],
            key=lambda x: x.str.extract(r'(\d+)')[0].fillna(999).astype(int) if x.name == 'item' else x
        )
        print(f"Construct: {construct_name}, Items: {len(c_items)}, resp type: {df_long['resp'].value_counts().sort_index()}")
        output_filename = f'processed/ehealth_rioux_2025_{construct_name.lower()}.csv'
        df_long.to_csv(output_filename, index=False)
        print(f"Generated {output_filename} with shape: {df_long.shape}")

if __name__ == "__main__":
    convert_to_irw('raw_data/ParentPref_OriginalData.csv')