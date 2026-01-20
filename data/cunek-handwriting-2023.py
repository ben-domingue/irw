import pandas as pd
import os

def convert_handwriting_to_irw():
    input_file = 'handwriting/Data_BHK_HLS_HPSQ-C.xlsx'
    df = pd.read_excel(input_file, sheet_name='data')
    
    id_col = 'ID'
    df = df.rename(columns={id_col: 'id'})
    
    bhk_items = [col for col in df.columns if col.startswith('BHK_P')]
    hls_items = [col for col in df.columns if col.startswith('HLS_P') and col != 'HLS_P_total']
    hpsq_items = [col for col in df.columns if col.startswith('HPSQC') and not col.startswith('SUM')]
    
    item_cols = bhk_items + hls_items + hpsq_items
    
    
    total_cols = ['BHK_Short', 'BHK_Total', 'HLS_P_total', 'SUM_HPSQC']
    
    subscale_cols = ['Organization', 'Letter formation', 'Fine motor', 'legibility', 'performance time', 'well-being']
    
    exclude_cols = item_cols + ['id', 'ID.1']  # Exclude ID.1 as it's a duplicate
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
    
    df_long = df_long.sort_values(['id', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp']
    other_cols = [col for col in df_long.columns if col not in core_cols]
    df_long = df_long[core_cols + sorted(other_cols)]
    
    output_file = 'handwriting/Data_BHK_HLS_HPSQ-C_irw_format.csv'
    df_long.to_csv(output_file, index=False)
    
    return df_long

if __name__ == '__main__':
    convert_handwriting_to_irw()
