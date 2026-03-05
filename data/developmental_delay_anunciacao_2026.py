import pandas as pd
import numpy as np
import re

def convert_to_irw(input_csv):
    df = pd.read_csv(input_csv, low_memory=False)
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.replace('.', pd.NA)
    
    score_cols = [c for c in df.columns if re.match(r'^asqse\d+$', c, re.IGNORECASE)]
    concern_cols = [c for c in df.columns if re.match(r'^con\d+$', c, re.IGNORECASE)]
    
    special_maps = {'datcom': 'date'}
    
    covariates = [c for c in df.columns if c not in score_cols and c not in concern_cols and c != 'id' and c not in special_maps.keys()]
    
    df = df.rename(columns=special_maps)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        df['date'] = df['date'].apply(
            lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA
        ).astype('Int64')
      
    rename_map = {c: f'cov_{c.lower()}' for c in covariates}
    df = df.rename(columns=rename_map)
    
    id_vars = ['id']
    if 'date' in df.columns:
        id_vars.append('date')
    id_vars.extend(list(rename_map.values()))
    
    final_cols = ['id', 'item', 'resp']
    if 'date' in df.columns:
        final_cols.append('date')
    final_cols.extend(list(rename_map.values()))

    df_scores = pd.melt(df, id_vars=id_vars, value_vars=score_cols, var_name='item', value_name='resp')
    df_scores = df_scores.dropna(subset=['resp'])
    df_scores['resp'] = pd.to_numeric(df_scores['resp'], errors='coerce')
    df_scores = df_scores.dropna(subset=['resp'])
    df_scores['resp'] = df_scores['resp'].astype(int)
    
    df_scores = df_scores[final_cols]
    df_scores = df_scores.sort_values(
        by=['id', 'item'],
        key=lambda x: x.str.extract(r'(\d+)')[0].fillna(999).astype(int) if x.name == 'item' else x
    )
    df_scores.to_csv('processed/development_delay_anunciacao_2026_asqse.csv', index=False)

    df_concerns = pd.melt(df, id_vars=id_vars, value_vars=concern_cols, var_name='item', value_name='resp')
    df_concerns = df_concerns.dropna(subset=['resp'])
    df_concerns['resp'] = pd.to_numeric(df_concerns['resp'], errors='coerce')
    df_concerns = df_concerns.dropna(subset=['resp'])
    df_concerns['resp'] = df_concerns['resp'].astype(int)
    
    df_concerns = df_concerns[final_cols]
    df_concerns = df_concerns.sort_values(
        by=['id', 'item'],
        key=lambda x: x.str.extract(r'(\d+)')[0].fillna(999).astype(int) if x.name == 'item' else x
    )
    df_concerns.to_csv('processed/development_delay_anunciacao_2026_asqse_concerns.csv', index=False)
    print("Done.")
    
if __name__ == "__main__":
    convert_to_irw('raw_data/asqse_results.csv')