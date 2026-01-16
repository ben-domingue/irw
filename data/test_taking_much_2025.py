import pandas as pd
import numpy as np


def convert_to_irw(input_file, output_file):
    df = pd.read_csv(input_file)
    
    # cov_ columns
    cov_cols_raw = df.columns[1:8].tolist()
    mapping = {col: f'cov_{col.lower()}' for col in cov_cols_raw}
    mapping['ID'] = 'id'
    mapping[df.columns[-1]] = 'rater'

    # Items
    item_cols = [c for c in df.columns[8:-1] if not c.startswith('X_')]
    
    irw_df = df.rename(columns=mapping)
    lower_cov_cols = [f'cov_{col.lower()}' for col in cov_cols_raw]
    id_vars = ['id', 'rater'] + lower_cov_cols

    irw_df = pd.melt(
        irw_df,
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    irw_df['resp'] = pd.to_numeric(irw_df['resp'], errors='coerce')
    irw_df = irw_df.dropna(subset=['resp'])
    
    # Filter -8 values
    irw_df = irw_df[irw_df['resp'] >= 0]
    
    # Filter non-integral values
    irw_df = irw_df[irw_df['resp'] % 1 == 0]

    irw_df['resp'] = irw_df['resp'].astype(int)
    final_cols = ['id', 'item', 'resp', 'rater'] + lower_cov_cols
    irw_df = irw_df[final_cols]
    irw_df.to_csv(output_file, index=False)
    
    print("Done processing the data.")

if __name__ == "__main__":
    
    input_file = 'tte_data.csv'
    output_file = 'test_taking_much_2025.csv'

    convert_to_irw(input_file, output_file)