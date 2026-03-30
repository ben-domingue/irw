import pandas as pd
import numpy as np

def convert_to_irw(input_csv):
    df = pd.read_csv(input_csv)

    true_covariates = [
        'Age', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 
        'female', 'eyesight_problems', 'glasses_lenses', 'drugs', 'coffee',
        'Group1', 'Group2'
    ]
    rename_map = {'ID': 'id'}
    cov_cols_to_keep = []
    for c in true_covariates:
        if c in df.columns:
            new_name = f"cov_{c.lower()}"
            rename_map[c] = new_name
            cov_cols_to_keep.append(new_name)
            
    df.rename(columns=rename_map, inplace=True)
    scale_prefixes = ['PWICONTROL', 'PWIEXP', 'TBZSGCONTR', 'TBZSGEXP', 
                      'STOMPCONTR', 'STOMPEXP', 'MASRQ', 'MLQControl', 'MLQExp', 
                      'Paas', 'Know']
    
    item_cols = []
    for col in df.columns:
        if any(col.startswith(prefix) for prefix in scale_prefixes):
            if not any(x in col for x in ['_sum', '_extrs', '_reversed', 'extreme_rs']):
                item_cols.append(col)

    # clean missing values
    for col in item_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df.loc[df[col] < 0, col] = np.nan

    id_vars = ['id'] + cov_cols_to_keep
    df_long = pd.melt(df, id_vars=id_vars, value_vars=item_cols, 
                      var_name='item', value_name='resp')
    df_long.dropna(subset=['resp'], inplace=True)
    final_cols = ['id', 'item', 'resp'] + id_vars[1:]
    df_final = df_long[final_cols]
    construct_masks = {
        'MASR': df_final['item'].str.contains('MASR'),
        'MLQ': df_final['item'].str.contains('MLQ'),
        'PWI': df_final['item'].str.startswith('PWI'),
        'TBZSG': df_final['item'].str.startswith('TBZSG'),
        'STOMP': df_final['item'].str.startswith('STOMP'),
        'Paas': df_final['item'].str.startswith('Paas'),
        'Know': df_final['item'].str.startswith('Know')
    }
    for name, mask in construct_masks.items():
        df_subset = df_final[mask]
        filename = f'cognitive_load_klimova_2023/cognitive_load_klimova_2023_{name.lower()}.csv'
        df_subset.to_csv(filename, index=False)
        print(f"{filename} saved.")

if __name__ == "__main__":
    convert_to_irw('raw_data/Final_data.csv')