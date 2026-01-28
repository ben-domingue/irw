import pandas as pd

def convert_to_irw(file_path):
    df = pd.read_csv(file_path)

    demo_cols_map = {
        'ID': 'id',
        'Group': 'cov_group',
        'Age': 'cov_age',
        'Gender': 'cov_gender',
        'Education': 'cov_education',
        'Language': 'cov_language',
        'Country': 'cov_country',
        'Device': 'cov_device',
        'AC': 'cov_ac',
        'Disruptions': 'cov_disruptions'
    }
    
    existing_demo_map = {k: v for k, v in demo_cols_map.items() if k in df.columns}
    demo_df = df[list(existing_demo_map.keys())].copy()
    demo_df.rename(columns=existing_demo_map, inplace=True)
    
    cov_cols = [c for c in demo_df.columns if c != 'id']
    
    constructs = {
        'mr': ['Y_MR', 'Y_MRt', 'Y_MRm'], 
        'ct': ['Y_CT', 'Y_CTt'],
        'cm': ['CM'], 
        'ef': ['EF'],
        'ao': ['AO'],
        'mrp': ['X_MRp']
    }
    
    totals = ['Y_MR_01', 'Y_MR_02', 'Y_MRt', 'Y_CTt', 'Y_CT_01', 'Y_CT_02', 'Y_CT_03', 'AO', 'CM_01', 'CM_02', 'CM_03', 'EF_01', 'EF_02']

    for name, prefixes in constructs.items():
        item_cols = []
        for col in df.columns:
            if col.startswith('T_') or col.startswith('cov_') or col.startswith('rt_') or col.startswith('CR_') or col in existing_demo_map:
                continue
            
            for p in prefixes:
                if col.startswith(p):
                    if col in totals:
                        continue
                    item_cols.append(col)
                    break
        
        dfs_to_concat = []
        for ic in item_cols:

            t_col = f"T_{ic[2:]}" if ic.startswith(('Y_', 'X_')) else f"T_{ic}"
            cr_col = f"CR_{ic[2:]}"

            sub = demo_df.copy()
            sub['item'] = ic
            sub['resp'] = df[ic] 
            print(f"Number of unique value for item '{ic}': {sub['resp'].nunique()}")
            
            if t_col in df.columns:
                sub['rt'] = df[t_col] / 1000.0
            else:
                sub['rt'] = None
            
            if cr_col in df.columns:
                sub['rater'] = df[cr_col]
            else:
                sub['rater'] = None
                
            dfs_to_concat.append(sub)
            
        if dfs_to_concat:
            final_df = pd.concat(dfs_to_concat, ignore_index=True)
            
            cols_order = ['id', 'item', 'resp', 'rt', 'rater'] + cov_cols
            cols_order = [c for c in cols_order if c in final_df.columns]
            final_df = final_df[cols_order]
            
            final_df.sort_values(by=['id', 'item'], inplace=True)
            
            filename = f"test_taking_much_{name}.csv"
            final_df.to_csv(filename, index=False)
            print(f"Saved: {filename}")

if __name__ == "__main__":
   convert_to_irw('tte_data.csv')