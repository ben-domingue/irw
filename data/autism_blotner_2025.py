import pandas as pd
import re
import os

def convert_to_irw_separate(file1, file2, output_base_name):
    
    def process_single_study(filename, wave_num, suffix, exclude_families=None):
        if exclude_families is None:
            exclude_families = []
            
        print(f"\n--- Processing {suffix.upper()} (Wave {wave_num}) from {filename} ---")
        
        try:
            df = pd.read_csv(filename)
            print(f"Loaded data: {df.shape}")
        except FileNotFoundError:
            print(f"Error: Could not find {filename}")
            return

        cov_map = {
            'age': 'cov_age',
            'sex': 'cov_sex',
            'edu': 'cov_education',
            'student': 'cov_student_status',
            'integrity': 'cov_integrity_check'
        }
        df.rename(columns=cov_map, inplace=True)

        if 'Unnamed: 0' in df.columns:
            df['id'] = df['Unnamed: 0'].astype(str)
        else:
            df['id'] = (df.index + 1).astype(str)
            
        df['wave'] = wave_num

        exclude_cols = ['id', 'wave', 'Unnamed: 0', 'Check', 'Check1', 'Check2', 'Check4', 
                        'seriousness_check', 'commi'] + list(cov_map.values())
 
        item_cols = [c for c in df.columns if c not in exclude_cols]

        id_vars = ['id', 'wave'] + [c for c in df.columns if c.startswith('cov_')]

        df_long = df.melt(
            id_vars=id_vars,
            value_vars=item_cols,
            var_name='original_item',
            value_name='resp'
        )

        def get_family(item_name):
            if not isinstance(item_name, str): return 'OTHER'
            match = re.match(r'^([A-Za-z]+)', item_name)
            if match:
                return match.group(1).upper()
            return 'OTHER'

        df_long['item_family'] = df_long['original_item'].apply(get_family)
        df_long['item'] = df_long['original_item']

        df_long.dropna(subset=['resp'], inplace=True)

        if exclude_families:
            print(f"Excluding families: {exclude_families}")
            df_long = df_long[~df_long['item_family'].isin(exclude_families)]

        base_cols = ['id', 'wave', 'item', 'resp', 'item_family']
        cov_cols = [c for c in df_long.columns if c.startswith('cov_')]
        final_cols = base_cols + [c for c in cov_cols if c not in base_cols]
        
        df_final = df_long[final_cols]

        base_name, ext = os.path.splitext(output_base_name)
        unique_families = df_final['item_family'].unique()
        print(f"Found families: {unique_families}")
        
        for family in unique_families:
            df_subset = df_final[df_final['item_family'] == family].copy()
            df_subset.drop(columns=['item_family'], inplace=True)
            
            fname = f"{base_name}_{suffix}_{family.lower()}{ext}"
            
            df_subset.to_csv(fname, index=False)
            print(f"Saved: {fname}")

    process_single_study(
        file1, 
        wave_num=1, 
        suffix='s1', 
        exclude_families=['APP', 'AV'] 
    )

    process_single_study(
        file2, 
        wave_num=2, 
        suffix='s2', 
        exclude_families=[] 
    )

    print("\nDone processing separately.")

if __name__ == "__main__":
    convert_to_irw_separate(
        'data_Mach_autism.csv', 
        'data_Mach_autism_S2.csv', 
        'autism_blotner_2025.csv'
    )