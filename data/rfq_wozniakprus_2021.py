import pandas as pd
import numpy as np

def convert_to_irw(input_file, output_file):
    try:
        df_all = pd.read_spss(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    scale_mapper = {
        'strongly disagree': 1, 'disagree': 2, 'somewhat disagree': 3,
        'neutral': 4, 'somewhat agree': 5, 'agree': 6, 'strongly agree': 7,
        'false': 0, 'true': 1,
        'no': 0, 'yes': 1
    }

    exclude_cols = ['Gender', 'Age', 'Area_of_study', 'Nationality', 'id']
    cols_to_map = [c for c in df_all.columns if c not in exclude_cols]

    for col in cols_to_map:

        if df_all[col].dtype == 'object' or hasattr(df_all[col], 'cat'):
            df_all[col] = df_all[col].astype(str).str.lower().str.strip()
            df_all[col] = df_all[col].replace(scale_mapper)
            df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

    target_prefixes = ['RFQ', 'GHQ', 'DERS', 'ECR', 'BPI']
    exclude_terms = ['_IRT', '_irt', 'Total', 'total', 'Sum', 'sum', 'Score', 'score', 'Scale', 'scale']

    item_cols = []
    for c in df_all.columns:
        if any(c.startswith(p) for p in target_prefixes) and not any(t in c for t in exclude_terms):
            item_cols.append(c)

    if 'id' not in df_all.columns:
        df_all['id'] = df_all.index + 1

    rename_map = {
        'Age': 'cov_age',
        'Gender': 'cov_gender',
        'Area_of_study': 'cov_area_of_study',
        'Nationality': 'cov_nationality',
    }
    df_all.rename(columns=rename_map, inplace=True)

    covariate_cols = [c for c in df_all.columns if c.startswith('cov_')]
    keep_cols = ['id'] + covariate_cols + item_cols
    keep_cols = [c for c in keep_cols if c in df_all.columns]
    
    df_subset = df_all[keep_cols].copy()

    # Long format
    df_long = df_subset.melt(
        id_vars=['id'] + covariate_cols,
        value_vars=item_cols,
        var_name='item',   
        value_name='resp'  
    )

    df_long.columns = [c.lower() for c in df_long.columns]

    df_long.dropna(subset=['resp'], inplace=True)

    # Remove imputed values
    df_long = df_long[df_long['resp'] % 1 == 0]

    df_long['resp'] = df_long['resp'].astype(int)

    first_cols = ['id', 'item', 'resp']
    rest_cols = [c for c in df_long.columns if c not in first_cols]
    df_long = df_long[first_cols + rest_cols]

    df_long.to_csv(output_file, index=False)

if __name__ == "__main__":
    input_file = 'Wozniak-Prus_et_al_RFQ-8_study.sav' 
    output_file = 'rfq_wozniakprus_2021.csv'
    
    convert_to_irw(input_file, output_file)