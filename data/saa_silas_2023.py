import pandas as pd
import os

def process_spalex_to_irw(main_data_path, demographics_path, output_path):
    try:
        df_main = pd.read_csv(main_data_path)
        df_demo = pd.read_csv(demographics_path)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    main_rename_map = {
        'p_id': 'id',
        'item': 'item',
        'opti3_scores': 'resp', 
        'GMS.Musical.Training': 'cov_musical_training',
        'GMS.Singing.Abilities': 'cov_singing_abilities',
        'find_user_range': 'cov_user_range',
        'language': 'cov_language'
    }
    df_main.rename(columns=main_rename_map, inplace=True)

    base_cols = ['id', 'item', 'resp']
    cov_cols_main = [c for c in df_main.columns if c.startswith('cov_')]
    df_irw = df_main[base_cols + cov_cols_main].copy()

    df_irw['resp'] = pd.to_numeric(df_irw['resp'], errors='coerce')
    df_irw.dropna(subset=['resp'], inplace=True)

    demo_rename_map = {
        'p_id': 'id',
        'demographics.age': 'cov_age',
        'demographics.gender': 'cov_gender'
    }
    df_demo.rename(columns=demo_rename_map, inplace=True)
    df_demo = df_demo[['id', 'cov_age', 'cov_gender']]
    df_final = pd.merge(df_irw, df_demo, on='id', how='left')
    all_cov_cols = [c for c in df_final.columns if c.startswith('cov_')]
    final_cols = base_cols + all_cov_cols
    df_final = df_final[final_cols]
    df_final.to_csv(output_path, index=False)
    print(f"Saved to '{output_path}'.")

if __name__ == "__main__":
    process_spalex_to_irw('raw_data/main_data_2.csv', 'raw_data/full_age_gender_demographics.csv', 'processed/saa_silas_2023.csv')