import pandas as pd
import os

def convert_ipq_excel(file_path, output_name):
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Loaded data: {df.shape}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    cov_map = {
        'Sexe': 'cov_sex',
        'DateNaiss': 'cov_dob',
        'Genotype': 'cov_genotype',
        'Naissance': 'cov_birth_type',
        'Dossier': 'id'
    }
    
    existing_covs = {k: v for k, v in cov_map.items() if k in df.columns}
    df.rename(columns=existing_covs, inplace=True)

    if 'id' not in df.columns:
        df['id'] = (df.index + 1).astype(str)
    else:
        df['id'] = df['id'].astype(str).str.replace(r'\.0$', '', regex=True)

    item_cols = [c for c in df.columns if c.startswith('IPQ')]

    print(f"Identified {len(item_cols)} items.")

    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]
    
    # Convert the integers to Datetime assuming SAS format (1960 epoch)
    df['cov_dob'] = pd.to_datetime(df['cov_dob'], unit='D', origin='1960-01-01')

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',    
        value_name='resp'
    )

    numeric_targets = ['resp', 'cov_sex', 'cov_genotype', 'cov_birth_type'] 
    
    for col in numeric_targets:
        if col in df_long.columns:
            df_long[col] = pd.to_numeric(df_long[col], errors='coerce').astype('Int64')

    df_long.dropna(subset=['resp'], inplace=True)
    
    base_cols = ['id', 'item', 'resp']
    cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
    final_cols = base_cols + [c for c in cov_cols if c not in base_cols]
    
    df_final = df_long[final_cols]

    df_final.to_csv(output_name, index=False)
    print(f"\nSaved processed data to {output_name}")

if __name__ == "__main__":
    convert_ipq_excel(
        'raw_data/Psychometric proprieties IPQ_Data set_PH.xlsx', 
        'raw_data/ipq_doglioni_2021.csv'
    )