import pandas as pd
import re

def convert_to_irw(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    df.insert(0, 'id', range(1, len(df) + 1))
    rename_map = {
        'W3Xage': 'cov_age',
        'W3XGENDER': 'cov_gender'
    }
    df = df.rename(columns=rename_map)
    
    df['cov_age'] = pd.to_numeric(df['cov_age'], errors='coerce').astype('Int64')
    df['cov_gender'] = pd.to_numeric(df['cov_gender'], errors='coerce').astype('Int64')

    item_pattern = r'^W\d+Q\d+'
    item_cols = [col for col in df.columns if re.match(item_pattern, col)]
    cov_cols = [col for col in df.columns if col not in item_cols and col != 'id']
    
    df_long = pd.melt(
        df,
        id_vars=['id'] + cov_cols,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )

    df_long = df_long.dropna(subset=['resp'])
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp'])
    df_long['resp'] = df_long['resp'].astype(int)
    
    final_cols = ['id', 'item', 'resp'] + cov_cols
    df_long = df_long[final_cols]
    
    df_long = df_long.sort_values(
        by=['id', 'item'],
        key=lambda x: x.str.extract(r'(\d+)')[0].fillna(999).astype(int) if x.name == 'item' else x
    )
    
    # Output to CSV
    df_long.to_csv(output_csv, index=False)
    print(f"Data saved to {output_csv} with shape: {df_long.shape}")
    

if __name__ == "__main__":  
    convert_to_irw('anes0809offwaves.csv', 'processed/dmirt_forsberg_2024.csv')