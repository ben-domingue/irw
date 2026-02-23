import pandas as pd

def convert_to_irw(file_path):
    try:
        df = pd.read_spss(file_path)
        print(f"Loaded data: {df.shape}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    if 'record.number' in df.columns:
        df.rename(columns={'record.number': 'id'}, inplace=True)
        
    if 'id' not in df.columns:
        df['id'] = (df.index + 1).astype(str)
    else:
        df['id'] = df['id'].astype(str)

    potential_covs = [
        'mono.or.bi.or.multi.SELFREPORT', 'tabriz.tehran', 'gender', 
        'age.group', 'age', 'occupation.stu', 'handedness'
    ]
    
    cov_map = {}
    for c in df.columns:
        c_lower = c.lower().strip()
        matched = False
        for pc in potential_covs:
            if pc.lower() == c_lower:
                cov_map[c] = f"cov_{pc.replace('.', '_').lower()}"
                matched = True
                break
        if not matched:
            for pc in potential_covs:
                if pc.lower() in c_lower and not c.startswith('cov_'):
                    cov_map[c] = f"cov_{pc.replace('.', '_').lower()}"
                    break
    
    explicit_mappings = {
        '18.1': 'cov_infancy',
        '18.2': 'cov_preschool_age',
        '18.3': 'cov_primary_school_age',
        '18.4': 'cov_high_school_age'
    }
    for code, clean_name in explicit_mappings.items():
        for col in df.columns:
            if code in col:
                cov_map[col] = clean_name
                
    df.rename(columns=cov_map, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]

    id_vars = list(dict.fromkeys(['id'] + [c for c in df.columns if c.startswith('cov_')]))

    construct_mappings = {
        'persian_comprehension': [
            '16.1.S', '16.1.L', '16.1.R', '16.1.W'
        ],
        'non_persian_proficiency': [
            '17.1.S', '17.1.L', '17.1.R', '17.1.W'
        ],
        'dominant_language_home_community': [
            '19.1', '19.2', '19.3', '19.4', '19.5', '19.6', '19.7',
            '20.1', '20.2', '20.3', '20.4', '20.5', '20.6', '20.7', '20.8'
        ],
        'non_persian_use': [
            '17.2.S', '17.2.L', '17.2.R', '17.2.W',
            '21.1', '21.2', '21.3', '21.4', '21.5', '21.6', '21.7', '21.8', '21.9'
        ],
        'switching': [
            '22.1', '22.2', '22.3'
        ]
    }

    def find_column(item_code, columns):
        search_str = item_code.lower()
        for col in columns:
            if search_str in col.lower():
                return col
        return None

    def process_construct(df, construct_name, item_codes, output_name):
        valid_cols = []
        rename_map = {}
        for code in item_codes:
            actual_col = find_column(code, df.columns)
            if actual_col and actual_col not in valid_cols:
                valid_cols.append(actual_col)
                rename_map[actual_col] = code 

        if not valid_cols:
            print(f"No valid columns found for {construct_name}. Skipping...")
            return

        df_subset = df[id_vars + valid_cols].copy()
        df_subset = df_subset.loc[:, ~df_subset.columns.duplicated()]
        df_subset.rename(columns=rename_map, inplace=True)

        df_long = df_subset.melt(
            id_vars=[v for v in id_vars if v in df_subset.columns],
            value_vars=list(rename_map.values()),
            var_name='item',
            value_name='resp'
        )

        df_long.dropna(subset=['resp'], inplace=True)
   
        scale_map = {
            '1all persin': 1,
            'most persian': 2,
            'half persian.half other language': 3,
            'most other language': 4,
            'only other language': 5,
            'never': 1,
            'rarely': 2,
            'sometimes': 3,
            'frequently': 4,
            'always': 5
        }

        if df_long['resp'].dtype == 'object' or pd.api.types.is_categorical_dtype(df_long['resp']):
            clean_resp = df_long['resp'].astype(str).str.strip().str.lower()
            df_long['resp'] = clean_resp.map(scale_map).fillna(df_long['resp'])

        try:
            df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
            
            if construct_name in ['dominant_language_home_community', 'non_persian_use', 'switching']:
                df_long.loc[(df_long['resp'] < 1) | (df_long['resp'] > 5), 'resp'] = pd.NA
                
            df_long.dropna(subset=['resp'], inplace=True)

            if (df_long['resp'].dropna() % 1 == 0).all():
                df_long['resp'] = df_long['resp'].astype('Int64')
                
        except Exception as e:
            pass

        base_cols = ['id', 'item', 'resp']
        cov_cols = list(dict.fromkeys([c for c in df_long.columns if c.startswith('cov_')]))
        final_cols = base_cols + cov_cols
        
        df_final = df_long[final_cols]
        
        df_final.to_csv(output_name, index=False)
        print(f"Saved {output_name} with shape {df_final.shape}")

    # Process all constructs
    for construct, codes in construct_mappings.items():
        if codes: 
            output_filename = f"raw_data/lsbq_maleki_2025_{construct}.csv"
            process_construct(df, construct, codes, output_filename)

    print("\nDone processing data.")

if __name__ == "__main__":
    convert_to_irw("raw_data/RAW Data.LSBQ.sav")