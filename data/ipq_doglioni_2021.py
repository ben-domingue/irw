import pandas as pd
import os

def convert_ipq_excel(file_path, output_name):
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Loaded data: {df.shape}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    # irw#2255, 2026-09-19: this table was withdrawn because it published `cov_dob`, the exact
    # date of birth of 408 sickle-cell patients, beside their genotype. Date of birth is now
    # reduced to whole years of age at STUDY_DATE and the exact date is never emitted. The
    # source's `Dossier` (the hospital file number) is no longer used as `id` either: it
    # identifies the patient's record. Ids are sequential in source-row order instead.
    STUDY_DATE = pd.Timestamp('2021-01-01')  # the study year; the deposit gives no survey date

    cov_map = {
        'Sexe': 'cov_sex',
        'DateNaiss': '_dob_raw',
        'Genotype': 'cov_genotype',
        'Naissance': 'cov_birth_type',
    }
    
    existing_covs = {k: v for k, v in cov_map.items() if k in df.columns}
    df.rename(columns=existing_covs, inplace=True)

    df['id'] = (df.index + 1).astype(str)

    item_cols = [c for c in df.columns if c.startswith('IPQ')]

    print(f"Identified {len(item_cols)} items.")

    # Convert the integers to Datetime assuming SAS format (1960 epoch), then keep only whole
    # years of age. The exact date never reaches the output.
    if '_dob_raw' in df.columns:
        dob = pd.to_datetime(df['_dob_raw'], unit='D', origin='1960-01-01')
        df['cov_age'] = ((STUDY_DATE - dob).dt.days // 365.25).astype('Int64')
        df.drop(columns=['_dob_raw'], inplace=True)

    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]
    

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
    
    df_long = df_long[df_long['resp'] != 6]
    
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