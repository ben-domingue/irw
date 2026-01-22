import pandas as pd

def convert_to_irw(input_file, output_file):
    print(f"Loading '{input_file}'...")
    df = pd.read_csv(input_file)

    rename_map = {
        'student': 'id',
        'section': 'item',
        'grademark': 'resp',
        'marker': 'rater',      
        'first_second': 'wave'  
    }
    df.rename(columns=rename_map, inplace=True)

    wave_map = {
        'first': 1, 
        'second': 2
    }

    df['wave'] = df['wave'].astype(str).str.lower().map(wave_map)

    df.dropna(subset=['resp'], inplace=True)

    if (df['resp'] % 1 == 0).all():
        df['resp'] = df['resp'].astype(int)
    
    target_cols = ['id', 'item', 'resp', 'wave', 'rater']
    
    final_cols = [c for c in target_cols if c in df.columns]
    
    df_final = df[final_cols]
    
    df_final.to_csv(output_file, index=False)
    print("Done processing the data.")

if __name__ == "__main__":
    convert_to_irw('clean_data.csv', 'double_marking_steele_2022.csv')