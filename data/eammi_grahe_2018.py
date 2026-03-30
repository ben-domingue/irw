import pandas as pd
import numpy as np
import os
import re

def convert_to_irw(input_file, output_dir='eammi_grahe_2018'):
    try:
        df = pd.read_excel(input_file, sheet_name='EAMMi2_Data')
        dups_df = pd.read_excel(input_file, sheet_name='suspicious duplicate Ps', 
                                skiprows=1, names=['Pair', 'ResponseId', 'Date', 'Action'])
    except Exception as e:
        print(f"Error loading file {input_file}: {e}")
        return

    # remove duplicates
    bad_ids = dups_df[dups_df['Action'].str.contains('delete', case=False, na=False)]['ResponseId'].tolist()
    df = df[~df['ResponseId'].isin(bad_ids)].copy()

    core_map = {
        'ResponseId': 'id',
        'Duration (in seconds)': 'rt',
        'RecordedDate': 'date'
    }
    df.rename(columns=core_map, inplace=True)
    
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = df['date'].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA)
    df['rt'] = pd.to_numeric(df['rt'], errors='coerce')

    covariate_map = {
        'age': 'cov_age', 'sex': 'cov_gender', 'Gender': 'cov_gender', 
        'race': 'cov_race', 'edu': 'cov_education', 'income': 'cov_income', 
        'sibling': 'cov_siblings', 'school': 'cov_school',
        'place2': 'cov_us_resident', 'place': 'cov_childhood_state',
        'Q80': 'cov_years_in_us', 'Q81': 'cov_current_country', 
        'Q82': 'cov_armed_forces_status', 'Q83': 'cov_armed_forces_years',
        'politics': 'cov_political_ideology', 'party': 'cov_political_party',
        'president': 'cov_president_support', 'adult_Q': 'cov_adult_status_percep'
    }
    existing_covs = {k: v for k, v in covariate_map.items() if k in df.columns}
    df.rename(columns=existing_covs, inplace=True)

    # Added str(c) to safely avoid TypeErrors on non-string column names
    cols_to_keep = [
        c for c in df.columns 
        if not re.search(r'(Click|Submit|Count|TEXT|StartDate|EndDate|Status|Progress|Finished|Recipient|External|Distribution|informedconsent|comments)', str(c), re.IGNORECASE)
    ]
    df = df[cols_to_keep]
    id_vars = ['id', 'rt', 'date'] + [c for c in df.columns if str(c).startswith('cov_')]
    item_cols = [c for c in df.columns if c not in id_vars]

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='original_item',
        value_name='resp'
    )

    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    float_array = np.array(df_long['resp'].values, dtype=float)
    df_long['resp'] = pd.Series(float_array, index=df_long.index).round().astype('Int64')
    df_long['item'] = df_long['original_item'].astype(str)

    def extract_construct(col_name):
        clean_name = col_name.lower()
        
        if clean_name.startswith('moa1#'): return 'moa1'
        if clean_name.startswith('moa2#'): return 'moa2'
        if clean_name.startswith('idea_'): return 'idea'
        if clean_name.startswith('swb_'): return 'swb'
        if clean_name.startswith('stress_'): return 'stress'
        if clean_name.startswith('mindful_'): return 'mindful'
        if clean_name.startswith('belong_'): return 'belong'
        if clean_name.startswith('support_'): return 'support'
        if clean_name.startswith('socmedia_'): return 'socmedia'
        if re.match(r'^npi\d+', clean_name): return 'npi' 
        if clean_name.startswith('exploit_'): return 'exploit'
        if clean_name.startswith('efficacy_'): return 'efficacy'
        if clean_name.startswith('physsx_'): return 'physsx'
        if clean_name.startswith('q10_'): return 'disability_identity' 
        if clean_name.startswith('transgres_'): return 'transgressions'
        if clean_name.startswith('usdream_'): return 'american_dream'
        if clean_name in ['marriage2', 'marriage4']: return 'marriage_attitudes'
        if clean_name == 'marriage3': return 'marriage_timing'
        if clean_name.startswith('marriage1_'): return 'marriage_identity_allocation'
        if clean_name == 'marriage5': return 'None'
        
        return 'None'

    df_long['construct'] = df_long['item'].apply(extract_construct)
    df_long = df_long[df_long['construct'] != 'None']
    valid_constructs = df_long['construct'].unique()

    valid_ranges = {
        'moa1': (1, 4),         
        'moa2': (1, 4),         
        'idea': (1, 4),         
        'swb': (1, 7),          
        'stress': (0, 4),       
        'mindful': (1, 6),      
        'belong': (1, 5),      
        'support': (1, 7),    
        'socmedia': (1, 7),   
        'npi': (0, 2),         
        'exploit': (1, 7),    
        'efficacy': (1, 4),   
        'physsx': (0, 2),      
        'disability_identity': (1, 6), 
        'marriage_attitudes': (1, 5), 
        'marriage_timing': (10, 100), 
        'marriage_identity_allocation': (0, 100), 
        'american_dream': (1, 5)
    }
    
    print(f"Found {len(valid_constructs)} valid constructs based on the codebook.")
    os.makedirs(output_dir, exist_ok=True)
    base_cols = ['id', 'item', 'resp', 'rt', 'date']
    final_cols = base_cols + [c for c in id_vars if str(c).startswith('cov_')]

    for construct in valid_constructs:
        df_construct = df_long[df_long['construct'] == construct].copy()
        if construct in valid_ranges:
            min_val, max_val = valid_ranges[construct]
            valid_mask = (df_construct['resp'] >= min_val) & (df_construct['resp'] <= max_val) 
            df_construct = df_construct[valid_mask]
            
        df_final = df_construct[final_cols]
        df_final = df_final.sort_values(by=['id', 'item'])
        
        output_name = os.path.join(output_dir, f"eammi_grahe_2018_{construct}.csv")
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with ({len(df_final)} rows)")

    print("Processing complete.")

if __name__ == "__main__":    
    convert_to_irw('raw_data/EAMMi2-Data1.2.xlsx')