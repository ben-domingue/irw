import pandas as pd
import numpy as np


def convert_to_irw(input_file, output_file):
    df = pd.read_csv(input_file)

    # Items
    item_cols = df.iloc[:, 8:-1].columns.tolist()
    
    # Rater
    rater_name = df.columns[-1]

    # Response table
    irw_df = df.rename(columns={'ID' : 'id', rater_name : 'rater'})
    
    irw_df = pd.melt(
        irw_df,
        id_vars=['id', 'rater'],
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    irw_df['resp'] = pd.to_numeric(irw_df['resp'], errors='coerce')
    irw_df = irw_df.dropna(subset=['resp'])
    
    irw_df = irw_df[['id', 'item', 'resp', 'rater']]
    irw_df.to_csv(output_file, index=False)
    
    print("Done processing the data.")

if __name__ == "__main__":
    
    input_file = 'tte_data.csv'
    output_file = 'test_taking_much_2025.csv'

    convert_to_irw(input_file, output_file)