import pandas as pd
import os

def remove_imputed_values(df, valid_range):
    min_val, max_val = valid_range
    df_clean = df.copy()
    
    resp_rounded = df_clean['resp'].round()
    
    df_clean = df_clean[
        (resp_rounded >= min_val) & 
        (resp_rounded <= max_val) &
        (abs(df_clean['resp'] - resp_rounded) < 0.001)  # Very close to integer
    ]
    
    df_clean['resp'] = df_clean['resp'].round().astype(int)
    
    return df_clean

def convert_interview_to_irw():
    input_file = 'interview/DB_MASI_PortugueseValidation2021.csv'
    df = pd.read_csv(input_file)
    
    id_col = 'ID'
    df = df.rename(columns={id_col: 'id'})
    
    masi_items = [col for col in df.columns 
                 if col.startswith('MASI') and col[4:].isdigit() 
                 and not col.endswith('_r')]
    
    masi_rep_items = [col for col in df.columns 
                     if col.startswith('MASI') and '_Rep' in col 
                     and col[4:].split('_')[0].isdigit()
                     and not col.endswith('_Rep_r')]
    
    lsas_items = [col for col in df.columns if 'LSAS' in col and '_Anxiety' in col]
    
    exclude_cov_cols = [
        'MASI4_r', 'MASI6_r', 'MASI4_Rep_r', 'MASI6_Rep_r',
        'MASI_Communication', 'MASI_Appearance', 'MASI_Social', 'MASI_Performance', 
        'MASI_Behavioural', 'MASI_Total',
        'MASI_Communication_Rep', 'MASI_Appearance_Rep', 'MASI_Social_Rep', 
        'MASI_Performance_Rep', 'MASI_Behavioural_Rep', 'MASI_Total_Rep',
        'TraitSocialAnxietyFear'  # This is a total score
    ]
    
    exclude_from_cov = masi_items + masi_rep_items + lsas_items + exclude_cov_cols + ['id']
    cov_cols = [col for col in df.columns if col not in exclude_from_cov]
    
    # Process MASI wave 1
    df_masi1 = df[['id'] + masi_items + cov_cols].copy()
    df_masi1_long = pd.melt(
        df_masi1,
        id_vars=['id'] + cov_cols,
        value_vars=masi_items,
        var_name='item',
        value_name='resp'
    )
    df_masi1_long['wave'] = 1
    
    # Process MASI wave 2 (retest)
    df_masi2 = df[['id'] + masi_rep_items + cov_cols].copy()
    df_masi2_long = pd.melt(
        df_masi2,
        id_vars=['id'] + cov_cols,
        value_vars=masi_rep_items,
        var_name='item',
        value_name='resp'
    )
    df_masi2_long['wave'] = 2
    df_masi2_long['item'] = df_masi2_long['item'].str.replace('_Rep', '', regex=False)
    
    # Combine MASI waves
    df_masi = pd.concat([df_masi1_long, df_masi2_long], ignore_index=True)
    
    df_masi['resp'] = pd.to_numeric(df_masi['resp'], errors='coerce')
    
    df_masi = remove_imputed_values(df_masi, (1, 5))
    
    df_masi = df_masi.dropna(subset=['resp'])
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_masi.columns}
    df_masi = df_masi.rename(columns=rename_dict)
    
    df_masi = df_masi.sort_values(['id', 'wave', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp', 'wave']
    other_cols = [col for col in df_masi.columns if col not in core_cols]
    df_masi = df_masi[core_cols + sorted(other_cols)]
    
    output_masi = 'interview/MASI_irw_format.csv'
    df_masi.to_csv(output_masi, index=False)
    
    # Process LSAS
    df_lsas = df[['id'] + lsas_items + cov_cols].copy()
    df_lsas_long = pd.melt(
        df_lsas,
        id_vars=['id'] + cov_cols,
        value_vars=lsas_items,
        var_name='item',
        value_name='resp'
    )
    df_lsas_long['wave'] = 1
    
    df_lsas_long['resp'] = pd.to_numeric(df_lsas_long['resp'], errors='coerce')
    
    df_lsas_clean = remove_imputed_values(df_lsas_long, (0, 3))
    df_lsas = df_lsas_clean
    
    df_lsas = df_lsas.dropna(subset=['resp'])
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_lsas.columns}
    df_lsas = df_lsas.rename(columns=rename_dict)
    
    df_lsas = df_lsas.sort_values(['id', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp', 'wave']
    other_cols = [col for col in df_lsas.columns if col not in core_cols]
    df_lsas = df_lsas[core_cols + sorted(other_cols)]
    
    output_lsas = 'interview/LSAS_irw_format.csv'
    df_lsas.to_csv(output_lsas, index=False)
    
    return df_masi, df_lsas

if __name__ == '__main__':
    convert_interview_to_irw()
