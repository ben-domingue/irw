import pandas as pd
import os


def _irw_columns(df):
    return df.rename(columns=lambda c: c.lower().replace(' ', '_').replace('.', '_'))


def convert_sheet1_to_irw(df):
    df = df.copy()
    df['id'] = df['ID.No']
    
    item_cols = [col for col in df.columns 
                 if col.endswith('_1') 
                 and col not in ['ID.No', 'Age Category']
                 and col not in ('Corrected_TS1', 'TS_1')]
    
    exclude_cols = item_cols + ['id', 'ID.No', 'TS_1', 'Corrected_TS1', 'EF_Fin']
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    id_vars = ['id'] + cov_cols
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
    df_long = _irw_columns(df_long)
    return df_long


def convert_sheet2_to_irw(df, sheet1_ids):
    df = df.copy()
    df['id'] = sheet1_ids.values
    
    item_cols = [col for col in df.columns if 'MCI_' in col]
    
    exclude_cols = item_cols + ['id', 'TS_1', 'Corrected_TS1']
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    id_vars = ['id'] + cov_cols
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    df_long['resp'] = df_long['resp'].map({'Yes': 1, 'No': 0})
    
    df_long = df_long.dropna(subset=['resp'])
    
    if 'Group_Code' in df_long.columns:
        df_long['Group_Code'] = df_long['Group_Code'].map({'Yes': 1, 'No': 0})
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_long.columns}
    df_long = df_long.rename(columns=rename_dict)
    df_long = _irw_columns(df_long)
    return df_long


def convert_sheet3_to_irw(df):
    df = df.copy()
    df['id'] = df['ID.No']
    
    subscales_1 = [col for col in df.columns 
                   if col.endswith('_1') 
                   and col not in ['ID.No', 'Age Category']
                   and col not in ('Corrected_TS1', 'TS_1')]
    subscales_2 = [col for col in df.columns 
                   if col.endswith('_2')
                   and col not in ('Corrected_TS2', 'TS_2')]
    
    base_subscales = set([col.replace('_1', '').replace('_2', '') for col in subscales_1 + subscales_2])
    
    exclude_cols = subscales_1 + subscales_2 + ['id', 'ID.No', 'Corrected_TS1', 'Corrected_TS2', 'TS_1', 'TS_2']
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    df1 = df[['id'] + subscales_1 + cov_cols].copy()
    df1_long = pd.melt(
        df1,
        id_vars=['id'] + cov_cols,
        value_vars=subscales_1,
        var_name='item',
        value_name='resp'
    )
    df1_long['wave'] = 1
    df1_long['item'] = df1_long['item'].str.replace(r'_1$', '', regex=True)

    df2 = df[['id'] + subscales_2 + cov_cols].copy()
    df2_long = pd.melt(
        df2,
        id_vars=['id'] + cov_cols,
        value_vars=subscales_2,
        var_name='item',
        value_name='resp'
    )
    df2_long['wave'] = 2
    df2_long['item'] = df2_long['item'].str.replace(r'_2$', '', regex=True)

    df_long = pd.concat([df1_long, df2_long], ignore_index=True)
    
    df_long = df_long.dropna(subset=['resp'])
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_long.columns}
    df_long = df_long.rename(columns=rename_dict)
    df_long = _irw_columns(df_long)
    return df_long


def convert_tmoca_to_irw():
    input_file = 'tmoca/Dataset_Karim.xlsx'
    
    df1 = pd.read_excel(input_file, sheet_name='Sheet1')
    df2 = pd.read_excel(input_file, sheet_name='Sheet2')
    df3 = pd.read_excel(input_file, sheet_name='Sheet3')
    
    df1_long = convert_sheet1_to_irw(df1)
    df2_long = convert_sheet2_to_irw(df2, df1['ID.No'])
    df3_long = convert_sheet3_to_irw(df3)
    
    output1 = 'tmoca/Karim2022_tmoca_subscales_single.csv'
    output2 = 'tmoca/Karim2022_tmoca_mci.csv'
    output3 = 'tmoca/Karim2022_tmoca_subscales_longitudinal.csv'

    df1_long.to_csv(output1, index=False)
    df2_long.to_csv(output2, index=False)
    df3_long.to_csv(output3, index=False)
    
    return df1_long, df2_long, df3_long

if __name__ == '__main__':
    convert_tmoca_to_irw()
