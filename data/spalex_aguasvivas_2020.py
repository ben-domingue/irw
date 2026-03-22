import pandas as pd
import os

def convert_to_irw(input_file, output_name):   
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    irw_map = {
        'trial_id': 'id',               
        'exp_id': 'cov_exp_id',         
        'spelling': 'item',              
        'accuracy': 'resp',              
        'lexicality': 'cov_lexicality',  
        'trial_order': 'cov_trial_order' 
    }
    
    df.rename(columns=irw_map, inplace=True)

    df['resp'] = pd.to_numeric(df['resp'], errors='coerce')
    df.dropna(subset=['resp'], inplace=True)
    
    df['id'] = df['id'].astype(str)
    df['item'] = df['item'].astype(str)
    if 'rt' in df.columns:
        df['rt'] = pd.to_numeric(df['rt'], errors='coerce')
    base_cols = ['id', 'item', 'resp', 'rt']
    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    final_cols = [c for c in (base_cols + cov_cols) if c in df.columns]
    df_final = df[final_cols]

    os.makedirs(os.path.dirname(output_name), exist_ok=True)
    
    df_final.to_csv(output_name, index=False)

if __name__ == "__main__":
    convert_to_irw(
        input_file='raw_data/lexical.csv', 
        output_name='processed/spalex_aguasvivas_2020.csv'
    )