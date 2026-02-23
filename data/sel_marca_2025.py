import pandas as pd
import re
import os

def convert_to_irw(file_paths):
    potential_covs = [
        'Estado', 'Município', 'Escola', 'Programa', 
        'Ano escolar', 'Perfil', 'Parentesco'
    ]

    master_data = {}

    for file_path in file_paths:
        survey_group = "unknown"
        if "estudantes" in file_path: survey_group = "estudantes"
        elif "familiares" in file_path: survey_group = "familiares"
        elif "professores" in file_path: survey_group = "professores"
            
        if '173808' in file_path:
            cohort_label = 't2_cohort'
        else:
            cohort_label = 't1_cohort'
        
        try:
            df = pd.read_csv(file_path, sep=';', encoding='latin1')
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

        if 'IDUsuario' in df.columns:
            df.rename(columns={'IDUsuario': 'id'}, inplace=True)
        else:
            df['id'] = (df.index + 1).astype(str)
        df['id'] = df['id'].astype(str)

        df['cov_cohort'] = cohort_label

        cov_map = {}
        for c in df.columns:
            if c in potential_covs:
                clean_name = f"cov_{c.lower().replace(' ', '_').replace('í', 'i')}"
                cov_map[c] = clean_name
        df.rename(columns=cov_map, inplace=True)

        id_vars = ['id', 'cov_cohort'] + [c for c in df.columns if c.startswith('cov_') and c != 'cov_cohort']

        item_cols = [c for c in df.columns if re.match(r'^(A9|A12)_Q\d+_P\d+$', str(c))]
        
        if not item_cols:
            print("No valid item columns found. Skipping file.")
            continue

        df_subset = df[id_vars + item_cols].copy()
        df_subset = df_subset.loc[:, ~df_subset.columns.duplicated()]

        df_long = df_subset.melt(
            id_vars=id_vars,
            value_vars=item_cols,
            var_name='raw_item',
            value_name='resp'
        )

        df_long.dropna(subset=['resp'], inplace=True)
        df_long[['wave', 'item']] = df_long['raw_item'].str.split('_', n=1, expand=True)
        
        if df_long['resp'].dtype == 'object':
            df_long['resp'] = df_long['resp'].astype(str).str.strip()
            
        try:
            df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
            if survey_group == 'estudantes':
                df_long.loc[(df_long['resp'] < 1) | (df_long['resp'] > 5), 'resp'] = pd.NA
            elif survey_group == 'familiares':
                df_long.loc[(df_long['resp'] < 0) | (df_long['resp'] > 5), 'resp'] = pd.NA
            elif survey_group == 'professores':
                df_long.loc[(df_long['resp'] < 0) | (df_long['resp'] > 10), 'resp'] = pd.NA

            df_long.dropna(subset=['resp'], inplace=True)
            
            if (df_long['resp'] % 1 == 0).all():
                df_long['resp'] = df_long['resp'].astype('Int64')
        except:
            pass 
        base_cols = ['id', 'wave', 'item', 'resp']
        cov_cols = list(dict.fromkeys([c for c in df_long.columns if c.startswith('cov_')]))
        df_final_subset = df_long[base_cols + cov_cols].copy()
        
        if survey_group not in master_data:
            master_data[survey_group] = []
        master_data[survey_group].append(df_final_subset)
    
    for survey_group, df_list in master_data.items():
        df_combined = pd.concat(df_list, ignore_index=True)
        base_cols = ['id', 'item', 'resp', 'wave']
        cov_cols = sorted([c for c in df_combined.columns if c.startswith('cov_')])
        df_combined = df_combined[base_cols + cov_cols]
        
        output_name = f"raw_data/sel_marca_2025_{survey_group}.csv"
        df_combined.to_csv(output_name, index=False)
        

if __name__ == "__main__":
    files_to_process = [
        "raw_data/pesquisa_4_estudantes_1733083208226.csv",    
        "raw_data/pesquisa_4_familiares_1733083353172.csv",    
        "raw_data/pesquisa_4_professores_1733083488620.csv",   
        "raw_data/pesquisa_4_estudantes_1738086324819.csv",     
        "raw_data/pesquisa_4_familiares_1738086444228.csv",     
        "raw_data/pesquisa_4_professores_1738086513968.csv"     
    ]
    
    convert_to_irw(files_to_process)