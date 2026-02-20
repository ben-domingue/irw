import pandas as pd

def process_fomo_negative_affect(file_path):
    df = pd.read_excel(file_path)

    # Rename id and demographic columns to IRW standard
    demo_map = {
        'idcareless': 'id',
        'age': 'cov_age',
        'sex': 'cov_sex',
    }
    df.rename(columns=demo_map, inplace=True)

    cov_cols = ['cov_age', 'cov_sex']

    # Define item columns for each scale
    constructs = {
        'fomo':  [f'fomo{i}_m'  for i in range(1, 11)],
        'phq':   [f'phq{i}_m'   for i in range(1, 10)],
        'panas': [f'panas{i}_m' for i in range(1, 21)],
        'rrs':   [f'rrs{i}_m'   for i in range(1, 11)],
    }

    output_files = []

    for name, cols in constructs.items():
        valid_cols = [c for c in cols if c in df.columns]
        existing_covs = [c for c in cov_cols if c in df.columns]

        melted = df.melt(
            id_vars=['id'] + existing_covs,
            value_vars=valid_cols,
            var_name='item',
            value_name='resp'
        )

        melted.dropna(subset=['resp'], inplace=True)
        melted['resp'] = melted['resp'].astype(int)

        cols_order = ['id', 'item', 'resp'] + existing_covs
        final_df = melted[cols_order]
        final_df['item_num'] = final_df['item'].str.extract(r'(\d+)').astype(int)
        final_df.sort_values(by=['id', 'item_num'], inplace=True)
        final_df.drop(columns=['item_num'], inplace=True)

        filename = f"FomoNegativeAffect_cremer_2026_{name}.csv"
        final_df.to_csv(filename, index=False)
        output_files.append(filename)
        print(f"Saved: {filename} — {final_df.shape}")

    return output_files

process_fomo_negative_affect("FomoNegativeAffect.xlsx")