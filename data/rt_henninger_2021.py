import pandas as pd
import os

def convert_to_irw():
    studies = {
        'MI': {'file': 'raw_data/MI_RT_Mplus.dat', 'name': 'Study 1 (Pfister, 2018)'},
        'HJP': {'file': 'raw_data/HJP_RT_Mplus.dat', 'name': 'Study 2 (Plieninger, 2019)'},
        'MUC': {'file': 'raw_data/MUC_RT_Mplus.dat', 'name': 'Study 3 (Fladerer, 2019)'}
    }
    
    for prefix, info in studies.items():
        filename = info['file']
        
        if not os.path.exists(filename):
            print(f"File {filename} not found in directory. Skipping...")
            continue
            
        print(f"\n--- Processing {prefix}: {info['name']} ---")
        
        temp = pd.read_csv(filename, sep=r'\s+', header=None, nrows=1)
        num_cols = len(temp.columns)
        
        if prefix == 'HJP' or num_cols == 5:
            # HJP does not have the MRS column
            col_names = ['id', 'item', 'rt', 'ERS', 'ARS']
        else:
            col_names = ['id', 'item', 'rt', 'ERS', 'ARS', 'MRS']
            
        if num_cols > len(col_names):
            extra_cols = [f'cov_contrast_{i}' for i in range(1, num_cols - len(col_names) + 1)]
            col_names.extend(extra_cols)

        df = pd.read_csv(filename, sep=r'\s+', header=None, names=col_names)
        
        def export_construct(df_source, target_construct):
            if target_construct not in df_source.columns:
                return
        
            other_constructs = [c for c in ['ERS', 'ARS', 'MRS'] if c != target_construct and c in df_source.columns]
            
            df_out = df_source.drop(columns=other_constructs).copy()
            df_out = df_out.rename(columns={target_construct: 'resp'})
            df_out = df_out.dropna(subset=['resp'])
            df_out['resp'] = df_out['resp'].astype(int)

            covs = [c for c in df_out.columns if c.startswith('cov_')]
            final_cols = ['id', 'item', 'resp', 'rt'] + covs
            df_out = df_out[final_cols]
            
            out_filename = f"rt_henninger_2021_{prefix.lower()}_{target_construct.lower()}.csv"
            df_out.to_csv(out_filename, index=False)
            print(f" -> Generated {out_filename} | Shape: {df_out.shape}")
            
        export_construct(df, 'ERS')
        export_construct(df, 'ARS')
        export_construct(df, 'MRS')


if __name__ == "__main__":
    convert_to_irw()