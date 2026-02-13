import pandas as pd
import numpy as np

def convert_to_irw(file_study1, file_study2, output_prefix):
    
    def process_single_study(filepath, study_label):
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None

        # item cols
        item_cols = [c for c in df.columns if c.startswith(('FNS', 'VAR', 'INVOL'))]
        
        cov_map = {
            'subject': 'id',
            'age': 'cov_age',
            'sex': 'cov_sex',
            'education': 'cov_education',
            'ethnicity': 'cov_ethnicity',
            'nationality': 'cov_nationality',
            'residency': 'cov_residency'
        }

        subset_cols = ['subject'] + [c for c in cov_map.keys() if c in df.columns and c != 'subject'] + item_cols
        subset_cols = [c for c in subset_cols if c in df.columns]
        
        df_flat = df[subset_cols].groupby('subject').first().reset_index()
        
        df_flat.rename(columns=cov_map, inplace=True)
        
        df_flat['wave'] = study_label

        id_vars = ['id', 'wave'] + [c for c in df_flat.columns if c.startswith('cov_')]

        df_long = df_flat.melt(
            id_vars=id_vars,
            value_vars=item_cols,
            var_name='item',
            value_name='resp'
        )
        
        return df_long

    df1 = process_single_study(file_study1, 1)
    df2 = process_single_study(file_study2, 2)
    df_combined = pd.concat([df1, df2], ignore_index=True)
    
    df_combined['resp'] = pd.to_numeric(df_combined['resp'], errors='coerce')
    df_combined.dropna(subset=['resp'], inplace=True)
    
    df_combined['resp'] = df_combined['resp'].astype(int)

    df_combined['item'] = df_combined['item'].str.upper()

    df_combined.sort_values(by=['wave', 'id', 'item'], inplace=True)
    base_cols = ['id', 'item', 'resp', 'wave']
    cov_cols = [c for c in df_combined.columns if c.startswith('cov_')]
    final_cols = base_cols + list(set(cov_cols)) 
    
    df_final = df_combined[final_cols]

    df_fns = df_final[df_final['item'].str.startswith('FNS')]
    if not df_fns.empty:
        fns_name = f"{output_prefix}_fns.csv"
        df_fns.to_csv(fns_name, index=False)
        print(f"Saved FNS data: {fns_name} ({len(df_fns)} rows)")

    df_var = df_final[df_final['item'].str.startswith('VAR')]
    if not df_var.empty:
        var_name = f"{output_prefix}_var.csv"
        df_var.to_csv(var_name, index=False)
        print(f"Saved VAR data: {var_name} ({len(df_var)} rows)")

    df_invol = df_final[df_final['item'].str.startswith('INVOL')]
    if not df_invol.empty:
        invol_name = f"{output_prefix}_invol.csv"
        df_invol.to_csv(invol_name, index=False)
        print(f"Saved INVOL data: {invol_name} ({len(df_invol)} rows)")

    print("Done processing data.")

if __name__ == "__main__":
    convert_to_irw('raw_data/Study_1_data.csv', 'raw_data/Study_2_data.csv', 'raw_data/curiosity_stone_2022')