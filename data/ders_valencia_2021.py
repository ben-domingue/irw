import pandas as pd
import numpy as np

def convert_ders_to_irw(input_file, output_file):
    try:
        df = pd.read_spss(input_file)
    except Exception as e:
        print(f"Error reading file. Make sure 'pyreadstat' is installed.\nError: {e}")
        return
    
    translation_map = {
        'id': 'id',
        'edad': 'cov_age',
        'sexo': 'cov_sex',
        'tipouni': 'cov_university_type',
        'semestre': 'cov_semester',
        'pareja': 'cov_partner',
        'trabaja': 'cov_employment'
    }

    df = df.rename(columns=translation_map)
    
    int_covs = ['id', 'cov_age', 'cov_partner', 'cov_employment', 'cov_semester']

    for col in int_covs:
        if col in df.columns:   
            # Convert to numeric, coercing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].astype('Int64')
    
    sex_map = {
        'mujer': 'female', 'hombre': 'male', 
    }
    uni_map = {
        'privada': 'private', 'publica': 'public',
    }
    if 'cov_sex' in df.columns:
        df['cov_sex'] = df['cov_sex'].astype(str).str.lower().map(sex_map).fillna(df['cov_sex'])
    
    if 'cov_university_type' in df.columns:
        df['cov_university_type'] = df['cov_university_type'].astype(str).str.lower().map(uni_map).fillna(df['cov_university_type'])
        
    cov_cols_english = [v for k, v in translation_map.items() if v != 'id']

    item_cols = [c for c in df.columns if c.startswith('ders') and c[4:].isdigit()]

    id_vars = ['id'] + cov_cols_english

    irw_df = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )

    irw_df['resp'] = pd.to_numeric(irw_df['resp'], errors='coerce')

    irw_df = irw_df.dropna(subset=['resp'])

    irw_df = irw_df[irw_df['resp'] >= 0]
    irw_df = irw_df[irw_df['resp'] % 1 == 0]

    irw_df['resp'] = irw_df['resp'].astype(int)

    final_cols = ['id', 'item', 'resp'] + cov_cols_english
    irw_df = irw_df[final_cols]
    irw_df = irw_df.sort_values(by=['id', 'item'])

    irw_df.to_csv(output_file, index=False)

    print(f"Done processing. Data saved to {output_file}")

if __name__ == "__main__":
    
    input_file = 'DERS Data.sav'
    output_file = 'ders_valencia_2025.csv'

    convert_ders_to_irw(input_file, output_file)