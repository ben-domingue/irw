import pandas as pd

def convert_to_irw(file_path):

    df = pd.read_csv(file_path, header=None, skiprows=1)
    
    df.columns = ['id', 'var1', 'var2', 'var3', 'var4', 'var5', 'var6']

    df_long = df.melt(id_vars=['id'], var_name='item', value_name='resp')

    df_long = df_long[['id', 'item', 'resp']]
    df_long.sort_values(by=['id', 'item'], inplace=True)
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce').astype('Int64')

    output_filename = 'presenteeism_golz_2024.csv'
    df_long.to_csv(output_filename, index=False)
    print("Done processing data.")

if __name__ == "__main__":
    convert_to_irw('data.csv')