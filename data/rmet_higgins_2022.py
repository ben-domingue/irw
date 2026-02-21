import pandas as pd
import re

def convert_to_irw(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded data: {df.shape}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return
    
    cols_to_exclude = ['Dem_ethnicity_9_TEXT', 'Dem_gender_4_TEXT']
    df.drop(columns=[c for c in cols_to_exclude if c in df.columns], inplace=True)

    if 'ID' in df.columns:
        df.rename(columns={'ID': 'id'}, inplace=True)

    potential_covs = ['age', 'gender', 'ethnicity'] + [c for c in df.columns if c.startswith('Dem_')]
    cov_map = {c: f"cov_{c.lower()}" for c in potential_covs if c in df.columns and not c.startswith('cov_')}
    df.rename(columns=cov_map, inplace=True)

    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_')]

    def process_construct(df, construct_name, item_pattern, output_name, time_suffix=None):
        item_cols = [c for c in df.columns if re.match(item_pattern, c)]
        
        if not item_cols:
            print(f"No columns found for {construct_name}")
            return

        df_long = df.melt(
            id_vars=id_vars,
            value_vars=item_cols,
            var_name='original_item',
            value_name='resp'
        )

        has_time = False
        if time_suffix:
            valid_time_cols = [f"{item}{time_suffix}" for item in item_cols if f"{item}{time_suffix}" in df.columns]
            
            if valid_time_cols:
                has_time = True
                df_time = df.melt(
                    id_vars=['id'],
                    value_vars=valid_time_cols,
                    var_name='time_col',
                    value_name='rt'
                )
                
                df_time['original_item'] = df_time['time_col'].str.replace(time_suffix, '', regex=False)
                df_long = pd.merge(df_long, df_time[['id', 'original_item', 'rt']], on=['id', 'original_item'], how='left')

        df_long.dropna(subset=['resp'], inplace=True)
        df_long['item'] = df_long['original_item']

        try:
            df_long['resp'] = pd.to_numeric(df_long['resp']).astype('Int64')
        except ValueError:
            pass 

        base_cols = ['id', 'item', 'resp']
        if has_time:
            base_cols.append('rt')
            
        cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
        final_cols = base_cols + cov_cols
        
        df_final = df_long[final_cols]
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with shape {df_final.shape}")

    process_construct(df, "RMET", r'^(R\d+|RPrac)$', "raw_data/rmet_higgins_2022_rmet.csv", time_suffix="_T_Page Submit")
    process_construct(df, "AQ", r'^AQ\d+$', "raw_data/rmet_higgins_2022_aq.csv")
    process_construct(df, "TAS", r'^TAS\d+$', "raw_data/rmet_higgins_2022_tas.csv")
    process_construct(df, "TOM", r'^TOM\d+$', "raw_data/rmet_higgins_2022_tom.csv")

    print("\nDone processing data.")

if __name__ == "__main__":
    convert_to_irw("raw_data/RMET_Project_Data_OSF.csv")