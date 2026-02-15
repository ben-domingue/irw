import pandas as pd
import re

def save_to_irw(df, id_cols, item_cols, construct_name, output_prefix):
    df_long = df.melt(id_vars=id_cols, value_vars=item_cols, var_name='item', value_name='resp')
    df_long['item'] = df_long['item'].str.lower()
    
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = df_long['resp'].astype(int)
    
    cols_order = ['id', 'item', 'resp'] + [c for c in id_cols if c != 'id']
    df_long = df_long[cols_order].sort_values(by=['id', 'item'])
    
    filename = f"raw_data/lexical_difficulty_altgassen_2025_{output_prefix}_{construct_name}.csv"
    df_long.to_csv(filename, index=False)
    print(f"Saved {filename} ({len(df_long)} rows)")

def convert_to_irw():

    # study 1
    df_s01 = pd.read_csv('raw_data/_analyses_submission3_osf/_data/s01 - data_clean.csv', encoding='latin-1', dtype={'REF': str})
    df_s01.dropna(subset=['REF'], inplace=True)
    df_s01.rename(columns={'REF': 'id'}, inplace=True)
    if 'id' not in df_s01.columns: df_s01.rename(columns={df_s01.columns[0]: 'id'}, inplace=True)

    s01_covs = [c for c in df_s01.columns if c.startswith('DEM_') or c in ['attention_1', 'attention_2', 'TIME_SUM']]
    s01_rename = {c: f"cov_{c.lower()}" for c in s01_covs}
    df_s01.rename(columns=s01_rename, inplace=True)
    s01_final_covs = ['id'] + list(s01_rename.values())

    knowledge_items = [c for c in df_s01.columns if re.match(r'^A\d+$', c)]

    personality_items = []
    for c in df_s01.columns:
        if c.startswith('PR'):
            s = pd.to_numeric(df_s01[c], errors='coerce')
            # Look for PR columns that actually have valid data AND are Likert (max > 1.0)
            if s.notna().sum() > 0 and s.max() > 1.0:
                personality_items.append(c)

    print(f"Personality items: {len(personality_items)}")
    print(f"Knowledge items: {len(knowledge_items)}")

    save_to_irw(df_s01, s01_final_covs, knowledge_items, "knowledge", "s01")
    save_to_irw(df_s01, s01_final_covs, personality_items, "personality", "s01")

    # study 2
    df_s02 = pd.read_csv('raw_data/_analyses_submission3_osf/_data/s02 - data_clean.csv', encoding='latin-1')
    df_s02.rename(columns={'REF': 'id'}, inplace=True)

    s02_covs = [c for c in df_s02.columns if c.startswith('SD_') or c == 'demgroup']
    s02_rename = {c: f"cov_{c.lower()}" for c in s02_covs}
    df_s02.rename(columns=s02_rename, inplace=True)
    s02_final_covs = ['id'] + list(s02_rename.values())

    gc_items = [c for c in df_s02.columns if c.startswith('gc_') and 'score' not in c and 'mean' not in c]
    ws_items = [c for c in df_s02.columns if c.startswith('ws_') and 'score' not in c and 'mean' not in c]

    save_to_irw(df_s02, s02_final_covs, gc_items, "gc", "s02")
    save_to_irw(df_s02, s02_final_covs, ws_items, "ws", "s02")

    # study 3
    df_s03 = pd.read_csv('raw_data/_analyses_submission3_osf/_data/s03 - data_clean1_v1.csv', encoding='latin-1')
    df_s03.rename(columns={'REF': 'id'}, inplace=True)

    s03_covs = [c for c in df_s03.columns if c.startswith('SD_') or c == 'longstring_adj']
    s03_rename = {c: f"cov_{c.lower()}" for c in s03_covs}
    df_s03.rename(columns=s03_rename, inplace=True)
    s03_final_covs = ['id'] + list(s03_rename.values())
    
    per_items = [c for c in df_s03.columns if c.startswith('per_') and not c.startswith('para_')]

    save_to_irw(df_s03, s03_final_covs, per_items, "per", "s03")

if __name__ == "__main__":
    convert_to_irw()