import pandas as pd

def convert_to_irw(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    df['id'] = df['id'].astype(str)

    cov_cols = ['country', 'age', 'age_group', 'gender', 'education', 'income', 'social_class']
    cov_map = {c: f"cov_{c}" for c in cov_cols if c in df.columns}
    df.rename(columns=cov_map, inplace=True)

    df['item'] = df['occupation'] + "_" + df['trait']

    id_vars = ['id', 'item'] + [c for c in df.columns if c.startswith('cov_')]

    response_vars = ['requirement', 'ai', 'own.fear', 'other.fear', 'incentive']

    for resp_var in response_vars:
        if resp_var not in df.columns:
            continue
            
        cols_to_keep = id_vars + [resp_var]
        df_construct = df[cols_to_keep].copy()
        
        df_construct.rename(columns={resp_var: 'resp'}, inplace=True)
        
        df_construct.dropna(subset=['resp'], inplace=True)
        
        if df_construct.empty:
            print(f"No data for {resp_var}, skipping...")
            continue
        try:
            df_construct['resp'] = pd.to_numeric(df_construct['resp']).astype('Int64')
        except ValueError:
            pass 
        
        base_cols = ['id', 'item', 'resp']
        covs = [c for c in df_construct.columns if c.startswith('cov_')]
        final_cols = base_cols + covs
        
        df_final = df_construct[final_cols]
        
        output_name = f"raw_data/ai_fear_dong_2026_{resp_var.replace('.', '_')}.csv"
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with shape {df_final.shape}")

if __name__ == "__main__":
    convert_to_irw("raw_data/long-format data for analysis.csv")