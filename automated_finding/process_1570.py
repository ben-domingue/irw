import pandas as pd
import os

os.chdir(os.path.expanduser("~/Desktop"))

excel_file = "DATA_MATRIX_ANONYMIZED.xlsx"

item_codes = [
    'att_1', 'att_2', 'att_3', 'att_4', 'att_5',
    'mem_1', 'mem_2', 'mem_3', 'mem_4', 'mem_5',
    'lang_1', 'lang_2', 'lang_3', 'lang_4',
    'log_1', 'log_2', 'log_3', 'log_4'
]

# 1. Save item text mapping
df_header = pd.read_excel(excel_file, sheet_name='Pre-Intervention', header=None)
item_texts = df_header.iloc[2, 4:].tolist()
item_text_df = pd.DataFrame({'item': item_codes, 'item_text': item_texts})
item_text_df.to_csv("cognitive_assessment_children_item_text.csv", index=False)
print("Saved: cognitive_assessment_children_item_text.csv")

# 2. Extract and format each wave
def process_sheet(sheet_name, wave_val):
    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    data_rows = df_raw.iloc[3:53].copy()
    ids = data_rows.iloc[:, 2].tolist()
    matrix = data_rows.iloc[:, 4:].copy()
    matrix.columns = item_codes
    matrix['id'] = ids
    
    df_long = pd.melt(matrix, id_vars=['id'], var_name='item', value_name='resp').dropna()
    df_long['resp'] = df_long['resp'].astype(int)
    df_long['wave'] = wave_val
    return df_long[['id', 'item', 'resp', 'wave']]

# 3. Combine Pre (wave=0) and Post (wave=1)
df_pre = process_sheet('Pre-Intervention', 0)
df_post = process_sheet('Post-Intervention', 1)
df_combined = pd.concat([df_pre, df_post], ignore_index=True)

output_name = "cognitive_children_2026.csv"
df_combined.to_csv(output_name, index=False)
print(f"Saved combined file: {output_name} ({len(df_combined)} rows)")