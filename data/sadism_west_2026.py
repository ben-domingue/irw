import pandas as pd

def convert_to_irw(input_file, output_prefix):
    try:
        df = pd.read_spss(input_file, convert_categoricals=False)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    if 'subject' in df.columns:
        df.rename(columns={'subject': 'id'}, inplace=True)

    all_cols = df.columns.tolist()

    cast_items = [c for c in all_cols if c.startswith('CAST')]
    print(f"CAST items: {cast_items}")
    srp_items = [c for c in all_cols if c.startswith('SRP')]
    all_items = cast_items + srp_items
    df.rename(columns={'ATTCHK5e': 'cov_attchk5e'}, inplace=True)

    df_filtered = df[['id', 'cov_attchk5e'] + all_items].copy()

    df_long = df_filtered.melt(
        id_vars=['id', 'cov_attchk5e'],
        value_vars=all_items,
        var_name='item',
        value_name='resp'
    )

    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long.dropna(subset=['resp'], inplace=True)
    df_long['resp'] = df_long['resp'].astype(int)

    def get_construct(item_name):
        if item_name.startswith('CAST'):
            return 'cast'
        elif item_name.startswith('SRP'):
            return 'srp'
        return 'other'

    df_long['construct'] = df_long['item'].apply(get_construct)
    unique_constructs = df_long['construct'].unique()

    for construct in unique_constructs:
        df_subset = df_long[df_long['construct'] == construct].copy()
        df_subset.drop(columns=['construct'], inplace=True)
        df_subset = df_subset[['id', 'item', 'resp']]
        df_subset.sort_values(by=['id', 'item'], inplace=True)

        filename = f"{output_prefix}_{construct.lower()}.csv"
        df_subset.to_csv(filename, index=False)
        print(f"Saved: {filename} ({len(df_subset)} rows)")

if __name__ == "__main__":
    convert_to_irw('raw_data/SadismLR.sav', 'raw_data/sadism_west_2026')