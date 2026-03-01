import pandas as pd

def convert_to_irw(input_file, output_file):
    df = pd.read_csv(input_file)

    df = df[df['exclude'] != 1]
    df = df.drop(columns=['exclude'])
    
    item_cols = [col for col in df.columns if str(col).startswith('BICB_')]
    cov_cols = [col for col in df.columns if col not in item_cols and col != 'id']

    cov_mapping = {col: f"cov_{col.lower()}" for col in cov_cols}
    df = df.rename(columns=cov_mapping)
    renamed_cov_cols = list(cov_mapping.values())
    
    df_long = pd.melt(
        df,
        id_vars=['id'] + renamed_cov_cols,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    df_long = df_long.dropna(subset=['resp'])
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp'])  
    df_long['resp'] = df_long['resp'].astype(int)

    final_cols = ['id', 'item', 'resp'] + renamed_cov_cols
    df_long = df_long[final_cols]
    df_long = df_long.sort_values(['id', 'item'])
    
    df_long.to_csv(output_file, index=False)
    print(f"File saved to {output_file} with shape: {df_long.shape}")
    


if __name__ == "__main__":
    convert_to_irw('raw_data/BICB-J250126.csv', 'processed/bicb-j_ishiguro_2025.csv')