import pandas as pd
import re

def process_rapm_data(input_file, output_file):
    df = pd.read_csv(input_file)

    waves = [
        (1, 'RAPMq', 'RAPMt'),       # wave 1
        (2, 'RetestQ', 'RetestT')    # wave 2
    ]

    id_vars = ['ID', 'Age', 'Gender', 'YearsEducation', 'WorkStatus']
    df_clean = df[id_vars].copy()
    df_clean.rename(columns={
        'ID': 'id',
        'Age': 'cov_age',
        'Gender': 'cov_gender',
        'YearsEducation': 'cov_years_education',
        'WorkStatus': 'cov_work_status'
    }, inplace=True)

    long_dfs = []

    for wave_num, q_prefix, t_prefix in waves:
        q_cols = [c for c in df.columns if c.startswith(q_prefix) and c[len(q_prefix):].isdigit()]
        
        df_q = df[['ID'] + q_cols].melt(
            id_vars=['ID'], 
            value_vars=q_cols, 
            var_name='item_col', 
            value_name='resp'
        )
        
        df_q['item_num'] = df_q['item_col'].apply(lambda x: int(re.search(r'\d+$', x).group()))

        t_cols = [c for c in df.columns if c.startswith(t_prefix) and c[len(t_prefix):].isdigit()]
        
        df_t = df[['ID'] + t_cols].melt(
            id_vars=['ID'], 
            value_vars=t_cols, 
            var_name='time_col', 
            value_name='rt'
        )
        
        df_t['item_num'] = df_t['time_col'].apply(lambda x: int(re.search(r'\d+$', x).group()))

        df_wave = pd.merge(df_q, df_t, on=['ID', 'item_num'], how='left')
        
        df_wave['wave'] = wave_num
        df_wave['item'] = 'RAPM_' + df_wave['item_num'].astype(str) 
        
        long_dfs.append(df_wave)


    df_long = pd.concat(long_dfs, ignore_index=True)

    final_df = pd.merge(df_clean, df_long, left_on='id', right_on='ID', how='right')
    
    final_df.drop(columns=['ID', 'item_col', 'time_col', 'item_num'], inplace=True)

    cols_order = ['id', 'item', 'resp', 'wave', 'rt'] 
    cov_cols = [c for c in final_df.columns if c not in cols_order]
    final_df = final_df[cols_order + cov_cols]

    final_df.to_csv(output_file, index=False)
    print("Done processing the data.")

if __name__ == "__main__":
    process_rapm_data('RAPM12untimed.csv', 'rapm_poulton_2022_untimed.csv')