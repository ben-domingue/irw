import pandas as pd

def convert_to_irw(input_file):
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'], inplace=True)

    # 2. cov cols based on codebook
    rename_map = {
        'age': 'cov_age',
        'age_gp': 'cov_age_gp',
        'location': 'cov_location',
        'race_cat': 'cov_race_cat',
        'main': 'cov_main',
        'nvs_cat': 'cov_nvs_cat',
        'realm_cat': 'cov_realm_cat',
        'quest_61': 'cov_gender',
        'quest_65a': 'cov_born_in_us',
        'quest_65b': 'cov_country_of_origin',
        'quest_68': 'cov_education_level',
        'quest_69': 'cov_country_of_schooling',
        'quest_70': 'cov_hs_in_stl',
        'quest_70a': 'cov_hs_name',
        'quest_70a_clean': 'cov_hs_name_clean',
        'quest_72': 'cov_employment',
        'quest_74': 'cov_income'
    }
    
    df.rename(columns=rename_map, inplace=True)
    cov_cols = list(rename_map.values())
    id_vars = ['id'] + [col for col in cov_cols if col in df.columns]
    item_cols = [c for c in df.columns if c not in id_vars]
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    final_cols = ['id', 'item', 'resp'] + id_vars[1:]
    df_irw = df_long[final_cols]
    print(f"Total valid item-response pairs generated: {df_irw.shape[0]}\n")
    mask_health_lit = df_irw['item'].isin(['nvs_score', 'realm_score'])
    mask_racial_comp = df_irw['item'].str.startswith('quest_rc')
    mask_causal_beliefs = df_irw['item'].str.startswith('quest_105')
    mask_general_knowledge = (~mask_health_lit) & (~mask_racial_comp) & (~mask_causal_beliefs)

    df_hl = df_irw[mask_health_lit]
    df_rc = df_irw[mask_racial_comp]
    df_cb = df_irw[mask_causal_beliefs]
    df_gk = df_irw[mask_general_knowledge]
    df_hl.to_csv('coh_goodman_2023_health_literacy.csv', index=False)
    df_rc.to_csv('coh_goodman_2023_racial_comp.csv', index=False)
    df_cb.to_csv('coh_goodman_2023_causal_beliefs.csv', index=False)
    df_gk.to_csv('coh_goodman_2023_general_survey.csv', index=False)
    print("Done.")


if __name__ == "__main__":
    convert_to_irw('raw_data/COH_racial_comp_data.xlsx')