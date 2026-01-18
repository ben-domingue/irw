import pandas as pd

def convert_to_irw(input_file, output_file):
    # 1. Load Data
    try:
        df_phase2 = pd.read_excel(input_file, sheet_name='Phase2')
        df_phase3 = pd.read_excel(input_file, sheet_name='Phase3')
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'.")
        return

    df_phase2['cov_phase'] = 2
    df_phase3['cov_phase'] = 3

    df_all = pd.concat([df_phase2, df_phase3], ignore_index=True)

    # Item columns
    cols = df_all.columns.tolist()
    try:
        start_idx = cols.index('T_E_65')
        end_idx = cols.index('T_D_47')
        item_cols = cols[start_idx : end_idx+1]
    except ValueError:
        print("Error: Could not find item columns.")
        return

    rename_map = {
        'P_ID': 'id',
        'Age': 'cov_age',
        'Gender': 'cov_gender',
        'Education': 'cov_education',
        'Handedness': 'cov_handedness',
        'P_Group': 'cov_p_group',
        'EGEFACE_Group': 'cov_egeface_group'
    }
    df_all.rename(columns=rename_map, inplace=True)

    covariate_cols = [c for c in df_all.columns if c.startswith('cov_')]
    id_vars = ['id'] + covariate_cols
    
    df_subset = df_all[id_vars + item_cols].copy()

    df_long = df_subset.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',   
        value_name='resp'  
    )

    df_long.columns = [c.lower() for c in df_long.columns]

    first_cols = ['id', 'item', 'resp']
    rest_cols = [c for c in df_long.columns if c not in first_cols]
    final_order = first_cols + rest_cols
    df_long = df_long[final_order]

    df_long.to_csv(output_file, index=False)
    print("Done processing data.")

if __name__ == "__main__":
    input_file = 'EGEFACE_Data.xlsx'
    output_file = 'face_memory_amado_2024.csv'
    
    convert_to_irw(input_file, output_file)