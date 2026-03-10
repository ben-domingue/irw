import pandas as pd
import re

def convert_to_irw():
    files = {
        'raw_data/data_sets_Study1/GerFFNI_data_HSNSonly_VersionMorf.csv': 'study1_morf',
        'raw_data/data_sets_Study1/HSNS_FEU_VersionKoeberl_NEU.csv': 'study1_koeberl',
        'raw_data/data_sets_Study1/Jauk_Nonlinear-Paper_Data_SPSS.csv': 'study1_jauk',
        'raw_data/Study2_data.csv': 'study2'
    }
    
    covs_to_include = {
        # Study 2
        'einverst_bedingungen', 'study_pref', 'biosex', 'gender', 'gender_else', 
        'age', 'lang_level', 'country_orig', 'country_curr', 'edu', 'job', 
        'job_else', 'fam', 'fam_pos', 'ment_dis',
        # Study 1 
        'sample', 'sex', 'mothertongue', 'diagnosis', 'work', 'education', 
        'criminal', 'strafe_d3', 'vorstrafen_d3', 'study', 'bio_sex', 
        'civil_status', 'civil_status_other', 'prof', 'valid', 'studie', 
        'geschlecht', 'alter',
        'datetime'
    }

    def get_construct(col):
        m = re.match(r'^([A-Za-z]+)(?:\d|_|$)', col)
        if not m: return None
        pref = m.group(1).lower()
        
        covariate_prefixes = ['c', 'p', 'v', 'kontroll', 'study', 'dispcode', 'id', 'sample', 'age', 'sex', 'valid', 'filter']
        if pref in covariate_prefixes:
            return None
        return pref

    for f, prefix in files.items():
        df = pd.read_csv(f, sep=';', low_memory=False)
        
        if 'Study_ID' in df.columns:
            df = df.rename(columns={'Study_ID': 'id'})
        elif 'dispcode' in df.columns:
            df = df.rename(columns={'dispcode': 'id'})
        else:
            df.insert(0, 'id', df.index + 1)
            
        df['id'] = df['id'].astype(str)
            
        construct_cols = {}
        for col in df.columns:
            if col == 'id': continue
            
            c = get_construct(col)
            if c and c not in ['c', 'p', 'v', 'kontroll', 'study', 'dispcode', 'id', 'sample', 'age', 'sex', 'valid', 'filter']:
                    if 'mean' in col.lower() or 'sum' in col.lower() or 'break' in col.lower():
                        continue
                    if re.search(r'\d+', col) or 'PNI_Example' in col:
                        if c not in construct_cols:
                            construct_cols[c] = []
                        construct_cols[c].append(col)

        construct_cols = {k: v for k, v in construct_cols.items() if len(v) >= 3}
        
        print(f"\nProcessing {f} -> Prefix: {prefix}")
        
        for construct, items in construct_cols.items():
            covariates = [c for c in df.columns if c.lower() in covs_to_include and c != 'id']
            rename_map = {c: f"cov_{c.lower()}" for c in covariates}
            
            df_melt = pd.melt(df, id_vars=['id'] + covariates, value_vars=items, var_name='item', value_name='resp')   
            df_melt = df_melt.rename(columns=rename_map)
            df_melt['resp'] = pd.to_numeric(df_melt['resp'], errors='coerce')
            df_melt = df_melt.dropna(subset=['resp'])
            df_melt = df_melt[df_melt['resp'] > 0]
            df_melt['resp'] = df_melt['resp'].astype(int)
            
            if 'cov_datetime' in df_melt.columns:
                df_melt['date'] = pd.to_datetime(df_melt['cov_datetime'], errors='coerce', utc=True)
                df_melt['date'] = df_melt['date'].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA).astype('Int64')
                df_melt = df_melt.drop(columns=['cov_datetime'])
            
            covs = [c for c in df_melt.columns if c.startswith('cov_')]
            final_cols = ['id', 'item', 'resp']
            if 'date' in df_melt.columns:
                final_cols.append('date')
            final_cols.extend(covs)
            df_melt = df_melt[final_cols]
            df_melt = df_melt.sort_values(by=['id', 'item'])

            out_name = f"processed/narcissism_schneider_2025_{prefix}_{construct}.csv"
            df_melt.to_csv(out_name, index=False)
            print(f"Generated {out_name} with shape: {df_melt.shape}")

if __name__ == "__main__":
    convert_to_irw()