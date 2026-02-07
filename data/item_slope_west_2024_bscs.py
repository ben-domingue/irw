import pandas as pd
import os

def convert_to_irw(input_file, output_name):

    try:
        df = pd.read_spss(input_file, convert_categoricals=True)
        print(f"Loaded {len(df)} rows from {input_file}")
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    column_mapping = {
        'subject': 'id',
        'score': 'resp',
        'Item': 'item',
        'PhysAgg': 'cov_physagg',
        'VerbAgg': 'cov_verbagg',
        'Anger': 'cov_anger',
        'Hostility': 'cov_hostility'
    }

    existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
    df.rename(columns=existing_cols, inplace=True)

    likert_map = {
        'Completely disagree': 1,
        'Disagree': 2,
        'Neither agree nor disagree': 3,
        'Agree': 4,
        'Completely Agree': 5
    }

    if df['resp'].dtype.name == 'category' or df['resp'].dtype == 'object':
        original_resp = df['resp'].copy()
        df['resp'] = df['resp'].map(likert_map)
        
        missing_after_map = df['resp'].isna().sum()
        if missing_after_map > 0:
            print(f"Warning: {missing_after_map} responses could not be mapped to numbers.")
            print("Unmapped values sample:", original_resp[df['resp'].isna()].unique())
    else:
        print("Resp column are numeric already.")

    df['resp'] = pd.to_numeric(df['resp'], errors='coerce')
    df.dropna(subset=['resp'], inplace=True)
    df['resp'] = df['resp'].astype(int)
    df['item'] = df['item'].astype(int)

    base_cols = ['id', 'item', 'resp']
    cov_cols = [c for c in df.columns if c.startswith('cov_')]
    final_cols = base_cols + cov_cols
    
    final_cols = [c for c in final_cols if c in df.columns]
    
    df_final = df[final_cols]

    df_final.to_csv(output_name, index=False)


if __name__ == "__main__":
    convert_to_irw(
        'raw_data/RISRdat.sav', 
        'raw_data/item_slope_west_2024_bscs.csv'
    )