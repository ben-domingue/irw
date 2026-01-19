import pandas as pd
import numpy as np

def convert_to_irw(input_file, output_file):
    df = pd.read_csv(input_file)
    
    item_cols = df.columns[8:].tolist()
    
    irw_df = df.rename(columns={'kh_id': 'id'})
    
    cov_cols = irw_df.iloc[:, :8]
    cov_cols_renamed = cov_cols.rename(columns={col: f'cov_{col}' for col in cov_cols.columns if col != 'id'})
    
    irw_df = pd.melt(
        irw_df,
        id_vars=['id'],
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    
    def standardize_resp(val):
        if pd.isna(val):
            return np.nan
        if isinstance(val, str):
            val_clean = val.lower().strip()
            if val_clean == 'yes': return 1.0
            if val_clean == 'no': return 0.0
        # non-numeric strings -> NaN
        return pd.to_numeric(val, errors='coerce')

    irw_df['resp'] = irw_df['resp'].apply(standardize_resp)
    
    irw_df = irw_df.dropna(subset=['resp'])
    
    irw_df = irw_df[['id', 'item', 'resp']]
    
    final_df = irw_df.merge(
        cov_cols_renamed,
        on='id',
        how='left'
    )
    
    # 9. Save result
    final_df.to_csv(output_file, index=False)
    print("Done processing the data.")

if __name__ == "__main__":
    # Test with the teachers dataset
    input_file = 'ds_pred_mets_teachers_sa.csv'
    output_file = 'mets_teachers_joubert_2025.csv'

    convert_to_irw(input_file, output_file)