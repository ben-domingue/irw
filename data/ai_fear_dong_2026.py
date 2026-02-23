import pandas as pd

def convert_to_irw(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    if 'id' in df.columns:
        df['id'] = df['id'].astype(str)
        df.rename(columns={'id': 'rater'}, inplace=True)

    cov_cols = ['country', 'age', 'age_group', 'gender', 'education', 'income', 'social_class']
    cov_map = {c: f"cov_{c}" for c in cov_cols if c in df.columns}
    df.rename(columns=cov_map, inplace=True)

    if 'occupation' in df.columns:
        df['occupation'] = df['occupation'].astype(str)
        df.rename(columns={'occupation': 'id'}, inplace=True)
    
    if 'trait' in df.columns:
        df['trait'] = df['trait'].astype(str)
        df.rename(columns={'trait': 'item'}, inplace=True)
        
    base_id_vars = ['id', 'item', 'rater']
    cov_vars = [c for c in df.columns if c.startswith('cov_')]
    id_vars = base_id_vars + cov_vars

    response_vars = ['requirement', 'ai', 'own.fear', 'other.fear', 'incentive']

    for resp_var in response_vars:
        if resp_var not in df.columns:
            continue
            
        cols_to_keep = [c for c in id_vars if c in df.columns] + [resp_var]
        df_construct = df[cols_to_keep].copy()
        
        df_construct.rename(columns={resp_var: 'resp'}, inplace=True)
        
        df_construct.dropna(subset=['resp'], inplace=True)
        
        if df_construct.empty:
            print(f"No data for {resp_var}, skipping...")
            continue
            
        try:
            df_construct['resp'] = pd.to_numeric(df_construct['resp'], errors='coerce')
            df_construct.dropna(subset=['resp'], inplace=True)
            if (df_construct['resp'] % 1 == 0).all():
                df_construct['resp'] = df_construct['resp'].astype('Int64')
        except ValueError:
            pass 
        
        final_cols_ordered = ['id', 'item', 'resp', 'rater'] + cov_vars
        final_cols = [c for c in final_cols_ordered if c in df_construct.columns]
        
        df_final = df_construct[final_cols]
        
        output_name = f"raw_data/ai_fear_dong_2026_{resp_var.replace('.', '_')}.csv"
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with shape {df_final.shape}")

if __name__ == "__main__":
    convert_to_irw("raw_data/long-format data for analysis.csv")