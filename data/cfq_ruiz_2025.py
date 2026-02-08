import pandas as pd
import os

def convert_to_irw(input_file, dass_output, cfq_output):

    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    df['id'] = df.index + 1

    cov_map = {
        'Country': 'cov_country',
        'Age': 'cov_age',
        'Gender': 'cov_gender'
    }
    df = df.rename(columns=cov_map)
    
    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]

    def process_item(full_df, item_prefix, output_filename):
        item_cols = [c for c in full_df.columns if c.startswith(item_prefix)]
        
        if not item_cols:
            print(f"No items found for {item_prefix}. Skipping.")
            return

        subset_df = full_df[id_vars + item_cols]

        df_long = subset_df.melt(
            id_vars=id_vars,
            value_vars=item_cols,
            var_name='original_item',  
            value_name='resp'
        )
        df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
        df_long = df_long.dropna(subset=['resp'])

        df_long['item'] = df_long['original_item']

        base_cols = ['id', 'item', 'resp']
        cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
        final_cols = base_cols + cov_cols
        
        df_final = df_long[final_cols]

        df_final = df_final.sort_values(by=['id', 'item'])

        df_final.to_csv(output_filename, index=False)
        print(f"Saved {output_filename}")

    
    process_item(df, 'DASS', dass_output)
    process_item(df, 'CFQ', cfq_output)

    print("\nDone processing data.")

if __name__ == "__main__":
    convert_to_irw(
        input_file='raw_data/Dataset.xlsx', 
        dass_output='raw_data/cfq_ruiz_2025_dass.csv',
        cfq_output='raw_data/cfq_ruiz_2025_cfq.csv'
    )