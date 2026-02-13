import pandas as pd
import re
import os

def convert_swedish_stress_to_irw():
    input_file = 'swedish_stress/Swedish_PSS_Rasch_analysis.xlsx'
    df = pd.read_excel(input_file, sheet_name='Data_MagnusPJohansson_BBQ')
    
    df['id'] = df.index + 1
    
    pss_cols = [col for col in df.columns if 'PSS[' in col]
    print(f"\nPSS items found: {len(pss_cols)}")
    
    item_mapping = {}
    for col in pss_cols:
        match = re.search(r'PSS\[(\d+)\]', col)
        if match:
            item_num = match.group(1)
            item_name = f'PSS{item_num}'
            item_mapping[col] = item_name
    
    exclude_cols = pss_cols + ['id']
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    
    id_vars = ['id'] + cov_cols
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=pss_cols,
        var_name='item_col',
        value_name='resp'
    )
    
    df_long['item'] = df_long['item_col'].map(item_mapping)
    df_long = df_long.drop(columns=['item_col'])
    
    df_long = df_long.dropna(subset=['resp'])
    
    rename_dict = {col: f'cov_{col}' for col in cov_cols if col in df_long.columns}
    df_long = df_long.rename(columns=rename_dict)
    
    df_long = df_long.sort_values(['id', 'item']).reset_index(drop=True)
    
    core_cols = ['id', 'item', 'resp']
    other_cols = [col for col in df_long.columns if col not in core_cols]
    df_long = df_long[core_cols + sorted(other_cols)]
    
    output_file = 'swedish_stress/Swedish_PSS_Rasch_analysis_irw_format.csv'
    df_long.to_csv(output_file, index=False)
    
    return df_long

if __name__ == '__main__':
    convert_swedish_stress_to_irw()
