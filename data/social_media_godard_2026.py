import pandas as pd
import os

def convert_to_irw(input_file):
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    df['id'] = df['id'].astype(str)
    item_cols = [c for c in df.columns if c != 'id']

    df_long = df.melt(
        id_vars=['id'],
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )

    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce').astype('Int64')
    df_long.dropna(subset=['resp'], inplace=True)
    df_long['construct'] = df_long['item'].apply(lambda x: x.split('_')[0] if '_' in x else 'Unknown')
    
    constructs = df_long['construct'].unique()
    print(f"\nFound {len(constructs)} constructs: {list(constructs)}")

    base_cols = ['id', 'item', 'resp']
    
    for construct in constructs:
        df_construct = df_long[df_long['construct'] == construct].copy()
        df_final = df_construct[base_cols]
        output_name = f"processed/social_media_godard_2026_{construct.lower()}.csv"
        
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with {len(df_final)} responses.")
        
    print("\nDone processing.")

if __name__ == "__main__": 
    convert_to_irw("raw_data/IRW_data.csv")
