import pandas as pd
import numpy as np

def convert_to_irw(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return
    
    df = df[df['seriousness_check'] == 1].copy()
    df.insert(0, 'id', range(1, len(df) + 1))
    df['last_math_grade'] = df['last_math_grade'].replace(6, np.nan)
    
    # account for reverse scoring
    df['NCS3'] = 6 - df['NCS3']
    df['NCS4'] = 6 - df['NCS4']
    df['conscientiousness1'] = 6 - df['conscientiousness1']
    
    covariates = [
        'age', 'gender', 'education_level', 'last_math_grade',
        'stochastics_in_school', 'stochastics_in_uni', 'science_student', 'knows_entropy'
    ]
    cov_map = {c: f'cov_{c}' for c in covariates}
    df.rename(columns=cov_map, inplace=True)
    cov_cols = list(cov_map.values())
    
    constructs = {
        'ncs': ['NCS1', 'NCS2', 'NCS3', 'NCS4', 'NCS5', 'NCS6'],
        'conscientiousness': ['conscientiousness1', 'conscientiousness2']
    }
    
    for construct_name, items in constructs.items():
        id_vars = ['id'] + cov_cols
        
        df_long = df.melt(
            id_vars=id_vars,
            value_vars=items,
            var_name='item',
            value_name='resp'
        )
  
        df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
        df_long.dropna(subset=['resp'], inplace=True)
        
        base_cols = ['id', 'item', 'resp']
        final_cols = base_cols + cov_cols
        df_final = df_long[final_cols]
        
        # Save to separate file
        output_file = f"processed/randomness_angelike_2024_{construct_name}.csv"
        df_final.to_csv(output_file, index=False)
        
        print(f"Processed {construct_name} with {len(df_final)} rows to {output_file}.")

if __name__ == "__main__":
    convert_to_irw('raw_data/data.csv')