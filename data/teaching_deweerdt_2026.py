import pandas as pd
import numpy as np

def convert_to_irw(file1, output_name):

    df = pd.read_excel(file1)

    df = df.rename(columns={'ID': 'id'})
    
    treatment_map = {'Teamteaching': 1, 'Solo': 0}
    df['treat'] = df['Treatment'].map(treatment_map)

    wave_map = {'Pretest': 1, 'Posttest': 2, 'Delayed': 3}
    df['wave'] = df['Time_Cat'].map(wave_map)

    item_cols = [f'Item_{i}' for i in range(1, 9)]

    cov_mapping = {
        'Gender': 'cov_gender',
        'SchoolID': 'cov_schoolid',
        'ClassID': 'cov_classid',
        'Grade': 'cov_grade',
        'AbilityGroup': 'cov_abilitygroup',
        'StuTeaRat': 'cov_stutearat',
        'Content': 'itemcov_content' 
    }

    df = df.rename(columns=cov_mapping)

    id_vars = ['id', 'wave', 'treat'] + list(cov_mapping.values())

    # Melt to Long Format
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item_raw',
        value_name='resp'
    )

    df_long['item'] = df_long['itemcov_content'].astype(str) + "_" + df_long['item_raw'].astype(str)


    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp'])

    df_long['id'] = df_long['id'].astype(int)
    df_long['resp'] = df_long['resp'].astype(int)

    final_cols = ['id', 'item', 'resp', 'wave', 'treat'] + list(cov_mapping.values())
    df_irw = df_long[final_cols]

    df_irw = df_irw.sort_values(by=['id', 'wave', 'item']) 
    df_irw.to_csv(output_name, index=False)
    
if __name__ == "__main__":
    convert_to_irw(
        'raw_data/Data_MainStudy.xlsx', 'raw_data/teaching_deweerdt_2026.csv')