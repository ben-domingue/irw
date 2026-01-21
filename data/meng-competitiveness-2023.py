import pandas as pd
import os

def convert_competitive_to_irw():
    input_file = 'competitive/ICN_data.csv'
    df = pd.read_csv(input_file)
    
    
    id_col = 'SubID'
    df = df.rename(columns={id_col: 'id'})
    
    ccps_items = [f'CCPS_{i}' for i in range(1, 24)]  # CCPS_1 to CCPS_23
    sco_items = [f'SCO_{i}' for i in range(1, 12)]     # SCO_1 to SCO_11
    item_cols = ccps_items + sco_items
    
    total_scores = ['SCO', 'COM', 'COO']
    subscales = ['SCO_ab', 'SCO_op', 'COM_hy', 'COM_sd', 'COM_su', 'COO_wi', 'COO_re', 'COO_in']
    
    cov_cols = ['gender', 'age', 'study'] + total_scores + subscales
    
    
    
    id_vars = ['id'] + cov_cols
    
    id_vars = [col for col in id_vars if col in df.columns]
    item_cols = [col for col in item_cols if col in df.columns]
    
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    df_long = df_long.dropna(subset=['resp'])
    cov_cols_to_prefix = [col for col in cov_cols if col in df_long.columns]
    rename_dict = {col: f'cov_{col}' for col in cov_cols_to_prefix}
    df_long = df_long.rename(columns=rename_dict)
    
    df_long = df_long.sort_values(['id', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp']
    other_cols = [col for col in df_long.columns if col not in core_cols]
    df_long = df_long[core_cols + sorted(other_cols)]
    
    output_file = 'competitive/ICN_data_irw_format.csv'
    df_long.to_csv(output_file, index=False)
    
    return df_long

if __name__ == '__main__':
    convert_competitive_to_irw()
