import pandas as pd
import re

def convert_to_irw(file1, file2, output_file):

    def process_study_wave(filename, id_prefix):
        df = pd.read_csv(filename)
        cov_map = {
            'age': 'cov_age',
            'sex': 'cov_sex',
            'edu': 'cov_education',
            'student': 'cov_student_status',
            'integrity': 'cov_integrity_check'
        }
        df.rename(columns=cov_map, inplace=True)

        if 'Unnamed: 0' in df.columns:
            df['original_id'] = df['Unnamed: 0'].astype(str)
        else:
            df['original_id'] = (df.index + 1).astype(str)
            
        df['id'] = id_prefix + df['original_id']
        
        exclude = ['id', 'original_id', 'Unnamed: 0', 'Check', 'Check1', 'Check2', 'Check4', 
                   'seriousness_check', 'commi'] + list(cov_map.values())
        
        item_cols = [c for c in df.columns if c not in exclude]
        
        df_long = df.melt(
            id_vars=['id'] + [c for c in df.columns if c.startswith('cov_')],
            value_vars=item_cols,
            var_name='original_item',
            value_name='resp'
        )
        
        def get_family(item_name):
            # Examples: BES_A1 -> BES, AQ10 -> AQ, ACME_COG -> ACME
            match = re.match(r'^([A-Za-z]+)', item_name)
            if match:
                return match.group(1).upper()
            return 'OTHER'

        df_long['item_family'] = df_long['original_item'].apply(get_family)
        
        df_long['item'] = df_long['original_item']
        
        return df_long

    df_s1 = process_study_wave(file1, id_prefix='S1_')
    df_s2 = process_study_wave(file2, id_prefix='S2_')
    
    # Combine
    df_final = pd.concat([df_s1, df_s2], ignore_index=True)
    
    df_final.dropna(subset=['resp'], inplace=True)
    
    base_cols = ['id', 'item', 'resp', 'item_family']
    cov_cols = [c for c in df_final.columns if c.startswith('cov_')]
    final_cols = base_cols + cov_cols
    
    df_final = df_final[final_cols]
    df_final.to_csv(output_file, index=False)
    print("Done processing the data.")

if __name__ == "__main__":
    convert_to_irw(
        'data_Mach_autism.csv', 
        'data_Mach_autism_S2.csv', 
        'autism_blotner_2025.csv'
    )