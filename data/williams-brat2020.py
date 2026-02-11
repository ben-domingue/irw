import pandas as pd
import os

def convert_beck_file(file_path, study_name):
    
    df = pd.read_excel(file_path, sheet_name=0)
    
    df['id'] = df.index + 1
    
    bdi_items = [col for col in df.columns if col.startswith('BDI')]
    
    exclude_cols = bdi_items + ['id']
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    id_vars = ['id'] + cov_cols
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=bdi_items,
        var_name='item',
        value_name='resp'
    )
    
    df_long = df_long.dropna(subset=['resp'])
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_long.columns}
    df_long = df_long.rename(columns=rename_dict)
    
    df_long = df_long.sort_values(['id', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp']
    other_cols = [col for col in df_long.columns if col not in core_cols]
    df_long = df_long[core_cols + sorted(other_cols)]
    
    return df_long

def convert_beck_to_irw():
    
    files = {
        'BRAT2020_study1': 'beck/BRAT2020_study1_osf.xlsx',
        'BRAT2020_study2': 'beck/BRAT2020_study2_osf.xlsx',
        'CPS2018': 'beck/CPS2018_study_osf.xlsx',
        'CPS2019': 'beck/CPS2019_study_osf.xlsx'
    }
    
    for study_name, file_path in files.items():
        df_long = convert_beck_file(file_path, study_name)
        
        output_file = f'beck/{study_name}_irw_format.csv'
        df_long.to_csv(output_file, index=False)

if __name__ == '__main__':
    convert_beck_to_irw()
