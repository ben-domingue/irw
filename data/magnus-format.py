import pandas as pd
import os

def convert_study1_to_irw():
    input_file = 'format/Study1.csv'
    df = pd.read_csv(input_file)
    
    df['id'] = df.index + 1
    
    exclude_cols = ['Duration', 'GeneralPhysical', 'GeneralMental', 'ChronicIllness', 
                     'Gender', 'Age', 'Ethnicity', 'Race', 'Education', 'Condition', 'Format']
    
    item_cols = [col for col in df.columns if col not in exclude_cols and col != 'id']
    
    cov_cols = ['Duration', 'GeneralPhysical', 'GeneralMental', 'ChronicIllness',
                 'Gender', 'Age', 'Ethnicity', 'Race', 'Education', 'Condition', 'Format']
    cov_cols = [col for col in cov_cols if col in df.columns]
    
    id_vars = ['id'] + cov_cols
    id_vars = [col for col in id_vars if col in df.columns]
    
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
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

def convert_study2_to_irw():
    
    input_file = 'format/Study2.csv'
    df = pd.read_csv(input_file)
    
    
    df['id'] = df.index + 1
    
    exclude_cols = ['Duration', 'GeneralPhysical', 'GeneralMental', 'ChronicIllness',
                     'Gender', 'Age', 'Ethnicity', 'Race', 'Education', 'Condition',
                     'Preference', 'PreferenceOpen']
    
    item_cols = [col for col in df.columns if col not in exclude_cols and col != 'id']
    
    cov_cols = ['Duration', 'GeneralPhysical', 'GeneralMental', 'ChronicIllness',
                'Gender', 'Age', 'Ethnicity', 'Race', 'Education', 'Condition',
                'Preference']
    cov_cols = [col for col in cov_cols if col in df.columns]
    
    id_vars = ['id'] + cov_cols
    id_vars = [col for col in id_vars if col in df.columns]
    
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
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

def convert_format_to_irw():
    
    # Convert each study
    df1 = convert_study1_to_irw()
    df2 = convert_study2_to_irw()
    
    output_file1 = 'format/Study1_irw_format.csv'
    output_file2 = 'format/Study2_irw_format.csv'
    
    df1.to_csv(output_file1, index=False)
    df2.to_csv(output_file2, index=False)
    
    return df1, df2

if __name__ == '__main__':
    convert_format_to_irw()
