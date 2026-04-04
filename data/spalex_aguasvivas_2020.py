import pandas as pd
import os

def convert_to_irw(input_file, session_file, users_file, output_name):   
    try:
        df_lexical = pd.read_csv(input_file)
        df_session = pd.read_csv(session_file)
        df_users = pd.read_csv(users_file)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    df = df_lexical.merge(df_session, on='exp_id', how='left')
    df = df.merge(df_users, on='profile_id', how='left')
    
    df = df.sort_values(by=['profile_id', 'date'])
    first_sessions = df.drop_duplicates(subset=['profile_id'])[['profile_id', 'exp_id']]
    df = df.merge(first_sessions, on=['profile_id', 'exp_id'], how='inner')

    irw_map = {
        'profile_id': 'id',             
        'trial_id': 'cov_trial_id',      
        'exp_id': 'cov_exp_id',         
        'spelling': 'item',              
        'accuracy': 'resp',              
        'lexicality': 'cov_lexicality',  
        'trial_order': 'cov_trial_order',
        'gender': 'cov_gender',
        'age': 'cov_age',
        'country': 'cov_country',
        'education': 'cov_education',
        'no_foreign_lang': 'cov_no_foreign_lang',
        'best_foreign': 'cov_best_foreign',
        'handedness': 'cov_handedness',
        'gender_rec': 'cov_gender_rec',
        'education_rec': 'cov_education_rec',
        'location_rec': 'cov_location_rec',
        'handedness_rec': 'cov_handedness_rec'
    }
    
    df.rename(columns=irw_map, inplace=True)

    df['resp'] = pd.to_numeric(df['resp'], errors='coerce')
    df.dropna(subset=['resp'], inplace=True)
    df['id'] = df['id'].astype(str)
    df['item'] = df['item'].astype(str)
    
    if 'rt' in df.columns:
        df['rt'] = pd.to_numeric(df['rt'], errors='coerce')
        
    base_cols = ['id', 'item', 'resp', 'rt', 'date']
    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    final_cols = [c for c in (base_cols + cov_cols) if c in df.columns]
    df_final = df[final_cols]

    os.makedirs(os.path.dirname(output_name), exist_ok=True)
    df_final.to_csv(output_name, index=False)
    
    print(f"Successfully processed and saved {len(df_final)} rows to {output_name}.")

if __name__ == "__main__":
    convert_to_irw(
        input_file='raw_data/lexical.csv', 
        session_file='raw_data/sessions.csv',  
        users_file='raw_data/users.csv',     
        output_name='processed/spalex_aguasvivas_2020.csv'
    )