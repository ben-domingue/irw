#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
import glob
import re
from datetime import datetime

def process_date_column(df, date_col='Date'):
    if date_col not in df.columns:
        return None, None
    
    dates = pd.to_datetime(df[date_col], errors='coerce')
    first_date = dates.min()
    
    if pd.isna(first_date):
        return None, None
    
    date_range = (dates.max() - dates.min()).total_seconds()
    
    if date_range < 86400:  # Less than 1 day difference
        # Treat as relative: use first date as 0
        df['date'] = (dates - first_date).dt.total_seconds()
        df['date'] = df['date'].fillna(0)
        print(f"Date: Using relative dates (first date as 0)")
    else:
        df['date'] = (dates - pd.Timestamp('1970-01-01')).dt.total_seconds()
    
    return df, first_date

# ARC's terms cover the RMET/MRMET test materials, including the four option words
# shown with each photo, so the tables must not reshare them (irw#2513, D13, 2026-09-28).
# resp_raw holds a per-item option code instead of the chosen word: "1" = the keyed
# answer (the word the source's accuracy column scores 1; normally also named in the
# header row just above the column names), "2"-"4" = the three
# distractors in alphabetical order of their English word. The codes are derived here
# from the source file at build time; do not write the word->code map anywhere public.
OPTION_WORD = re.compile(r'^[a-z\-]+$')


def code_options(irw_df, input_file, header_row, close_call=0.10):
    top = pd.read_excel(input_file, header=None, nrows=header_row + 1)
    keys = {}
    for i, name in enumerate(top.iloc[header_row]):
        m = re.fullmatch(r'response_(\d+)', str(name))
        if m:
            keys[int(m.group(1))] = str(top.iloc[header_row - 1, i]).strip()
    words = irw_df['resp_raw'].astype('string').str.strip()
    counts, options = {}, {}
    for k in keys:
        w = words[irw_df['item'] == f'item_{k}'].dropna()
        counts[k] = w[w.map(lambda x: bool(OPTION_WORD.match(x)) and x != 'none')].value_counts()
        options[k] = list(counts[k].index[:4])
    codes = pd.Series(pd.NA, index=irw_df.index, dtype='string')
    for k, key in keys.items():
        vc, opts = counts[k], options[k]
        # "1" is the word the source scores as correct. MRMET item_16's header row names
        # a different word than its accuracy column scores; resp follows accuracy.
        item_rows = irw_df['item'] == f'item_{k}'
        scored = set(words[item_rows & (irw_df['resp'] == 1)].dropna())
        if len(scored) != 1:
            raise ValueError(f'item_{k}: {len(scored)} words are scored correct, expected 1')
        if key != next(iter(scored)):
            print(f'item_{k}: header-row key differs from the scored answer; using the scored one')
            key = next(iter(scored))
        # The options are the item's four most frequent English words. MRMET also has a
        # few stray words (1-6 rows each), "none", and garbled HTML from translated
        # versions; all of those become NA. RMET has exactly four words per item.
        if len(opts) != 4 or key not in opts:
            raise ValueError(f'item_{k}: the key is not among the four most frequent words')
        if len(vc) > 4 and vc.iloc[4] >= close_call * vc.iloc[3]:
            # A close 5th word could be a real option. Accept it only as carry-over:
            # every extra word is an option of the neighbouring item (MRMET item_2).
            nearby = set(options.get(k - 1, [])) | set(options.get(k + 1, []))
            if not set(vc.index[4:]) <= nearby:
                raise ValueError(f'item_{k}: 5th word is close to the 4th '
                                 f'({vc.iloc[4]} vs {vc.iloc[3]}); decide before building')
        code = {key: '1'}
        code.update({w: str(j + 2) for j, w in enumerate(sorted(set(opts) - {key}))})
        rows = irw_df['item'] == f'item_{k}'
        codes[rows] = words[rows].map(code)
    # A keyed answer is exactly a correct response.
    coded = codes.notna()
    assert ((codes[coded] == '1') == (irw_df.loc[coded, 'resp'] == 1)).all()
    irw_df['resp_raw'] = codes
    return irw_df


def convert_mrmet_file(input_file, output_file, dataset_name):
    
    df = pd.read_excel(input_file, header=3)
    
    df, first_date = process_date_column(df)
    
    id_col = None
    for col in ['Count', 'count', 'ID', 'id', 'participant', 'subject']:
        if col in df.columns:
            id_col = col
            break
    
    if id_col is None:
        df['id'] = df.index + 1
        id_col = 'id'
    else:
        df = df.rename(columns={id_col: 'id'})
    
    
    accuracy_cols = [col for col in df.columns if col.startswith('accuracy_')]
    
    rt_cols = [col for col in df.columns if col.startswith('rt_')]
    
    response_cols = [col for col in df.columns if col.startswith('response_')]
    
    exclude_cols = ['id', 'date'] + accuracy_cols + rt_cols + response_cols
    exclude_cols.extend([col for col in df.columns if 'dsm_accuracy' in str(col).lower()])  # DSM items are NOT covariates
    exclude_cols.extend([col for col in df.columns if '_score' in str(col).lower()])  # Score columns are aggregated
    exclude_cols.extend([col for col in df.columns if 'total' in str(col).lower() and col != 'id'])  # Total scores
    
    cov_cols = [col for col in df.columns if col not in exclude_cols]
    
    metadata_cols = ['Date', 'date', 'Count', 'count', 'Trial number -->']
    cov_cols = [col for col in cov_cols if col not in metadata_cols]
    
    
    long_data = []
    
    for idx, row in df.iterrows():
        person_id = row['id']
        
        covs = {}
        for col in cov_cols:
            if col in row and pd.notna(row[col]):
                cov_name = f'cov_{col.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").replace("?", "")}'
                cov_name = re.sub('_+', '_', cov_name)
                covs[cov_name] = row[col]
        
        if 'date' in row and pd.notna(row['date']):
            covs['date'] = row['date']
        
        for acc_col in accuracy_cols:
            item_match = re.search(r'accuracy_(\d+)', acc_col)
            if item_match:
                item_num = item_match.group(1)
                item_id = f'item_{item_num}'
                
                resp = row[acc_col]
                
                if pd.isna(resp):
                    continue
                
                row_data = {
                    'id': person_id,
                    'item': item_id,
                    'resp': int(resp) if pd.notna(resp) else np.nan,
                    **covs
                }
                
                rt_col = f'rt_{item_num}'
                if rt_col in df.columns and pd.notna(row[rt_col]):
                    rt_val = row[rt_col]
                    if rt_val > 1000:  # Likely in milliseconds
                        rt_val = rt_val / 1000.0
                    row_data['rt'] = rt_val
                
                resp_col = f'response_{item_num}'
                if resp_col in df.columns and pd.notna(row[resp_col]):
                    row_data['resp_raw'] = row[resp_col]
                
                long_data.append(row_data)
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df = code_options(irw_df, input_file, header_row=3)
    
    irw_df['cov_dataset'] = dataset_name
    
    col_order = ['id', 'item', 'resp']
    if 'resp_raw' in irw_df.columns:
        col_order.append('resp_raw')
    if 'rt' in irw_df.columns:
        col_order.append('rt')
    if 'date' in irw_df.columns:
        col_order.append('date')
    
    remaining_cols = [c for c in irw_df.columns if c not in col_order]
    col_order.extend(sorted(remaining_cols))
    
    irw_df = irw_df[col_order]
    
    irw_df.to_csv(output_file, index=False)
    
    return irw_df

def convert_validation_file(input_file, output_file):
    df = pd.read_excel(input_file, header=4)
    
    df, first_date = process_date_column(df)
    
    id_col = None
    for col in ['Count', 'count', 'ID', 'id', 'participant', 'subject']:
        if col in df.columns:
            id_col = col
            break
    
    if id_col is None:
        df['id'] = df.index + 1
        id_col = 'id'
    else:
        df = df.rename(columns={id_col: 'id'})
    
    
    mrmet_acc_cols = [col for col in df.columns if 'accuracy_mrmet' in str(col).lower()]
    rmet_acc_cols = [col for col in df.columns if 'accuracy_rmet' in str(col).lower() and 'mrmet' not in str(col).lower()]
    
    
    mrmet_response_cols = [col for col in df.columns if 'response' in str(col).lower() and 'mrmet' in str(col).lower() and 'accuracy' not in str(col).lower() and 'time' not in str(col).lower()]
    rmet_response_cols = [col for col in df.columns if 'response' in str(col).lower() and 'rmet' in str(col).lower() and 'mrmet' not in str(col).lower() and 'accuracy' not in str(col).lower() and 'time' not in str(col).lower()]
    
    
    exclude_cols = ['id', 'date'] + mrmet_acc_cols + rmet_acc_cols
    exclude_cols.extend([col for col in df.columns if 'response' in str(col).lower()])  # Exclude all response word columns
    exclude_cols.extend([col for col in df.columns if 'dsm_accuracy' in str(col).lower()])  # DSM items are NOT covariates
    exclude_cols.extend([col for col in df.columns if '_score' in str(col).lower()])  # Score columns
    exclude_cols.extend([col for col in df.columns if col.startswith('rt_')])  # RT columns
    exclude_cols.extend([col for col in df.columns if 'total' in str(col).lower() and col != 'id' and 'dsm_total' not in str(col).lower()])  # Total scores (but keep DSM_total if it's a person-level measure)
    exclude_cols.extend([col for col in df.columns if col.startswith('accuracy_') and 'mrmet' not in str(col).lower() and 'rmet' not in str(col).lower()])
    
    metadata_cols = ['Date', 'date', 'Count', 'count', 'Trial number -->']
    cov_cols = [col for col in df.columns if col not in exclude_cols and col not in metadata_cols]
    
    long_data = []
    
    for idx, row in df.iterrows():
        person_id = row['id']
        
        covs = {}
        for col in cov_cols:
            if col in row and pd.notna(row[col]):
                cov_name = f'cov_{col.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").replace("?", "")}'
                cov_name = re.sub('_+', '_', cov_name)
                covs[cov_name] = row[col]
        
        if 'date' in row and pd.notna(row['date']):
            covs['date'] = row['date']
        
        for acc_col in mrmet_acc_cols:
            item_match = re.search(r'accuracy_mrmet_(\d+)', acc_col)
            if item_match:
                item_num = item_match.group(1)
                item_id = f'mrmet_item_{item_num}'
                
                resp = row[acc_col]
                if pd.isna(resp):
                    continue
                
                row_data = {
                    'id': person_id,
                    'item': item_id,
                    'resp': int(resp) if pd.notna(resp) else np.nan,
                    **covs
                }
                
                resp_col = f'response_mrmet_{item_num}'
                if resp_col in df.columns and pd.notna(row[resp_col]):
                    row_data['raw_resp'] = row[resp_col]
                else:
                    resp_col_alt = f'response_{item_num}'
                    if resp_col_alt in df.columns and pd.notna(row[resp_col_alt]):
                        row_data['raw_resp'] = row[resp_col_alt]
                
                long_data.append(row_data)
        
        for acc_col in rmet_acc_cols:
            item_match = re.search(r'accuracy_rmet_(\d+)', acc_col)
            if item_match:
                item_num = item_match.group(1)
                item_id = f'rmet_item_{item_num}'
                
                resp = row[acc_col]
                if pd.isna(resp):
                    continue
                
                row_data = {
                    'id': person_id,
                    'item': item_id,
                    'resp': int(resp) if pd.notna(resp) else np.nan,
                    **covs
                }
                
                resp_col = f'response_rmet_{item_num}'
                if resp_col in df.columns and pd.notna(row[resp_col]):
                    row_data['raw_resp'] = row[resp_col]
                else:
                    resp_col_alt = f'response_{item_num}'
                    if resp_col_alt in df.columns and pd.notna(row[resp_col_alt]):
                        row_data['raw_resp'] = row[resp_col_alt]
                
                long_data.append(row_data)
    
    irw_df = pd.DataFrame(long_data)
    
    irw_df = irw_df.drop_duplicates()
    
    irw_df = irw_df.sort_values(['id', 'item']).reset_index(drop=True)
    
    irw_df['cov_dataset'] = 'mrmet_rmet_validation'
    
    col_order = ['id', 'item', 'resp']
    if 'raw_resp' in irw_df.columns:
        col_order.append('raw_resp')
    if 'rt' in irw_df.columns:
        col_order.append('rt')
    if 'date' in irw_df.columns:
        col_order.append('date')
    
    remaining_cols = [c for c in irw_df.columns if c not in col_order]
    col_order.extend(sorted(remaining_cols))
    
    irw_df = irw_df[col_order]
    
    # Save to CSV
    irw_df.to_csv(output_file, index=False)
    
    
    return irw_df

def convert_all_mrmet_files(data_dir, output_dir):
    excel_files = glob.glob(os.path.join(data_dir, "*.xlsx"))
    
    if not excel_files:
        raise ValueError(f"No Excel files found in {data_dir}")
    
    for f in excel_files:
        print(f"  - {os.path.basename(f)}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for excel_file in sorted(excel_files):
        file_name = os.path.basename(excel_file)
        dataset_name = os.path.splitext(file_name)[0].lower().replace(" ", "_").replace("&", "and")
        
        output_file = os.path.join(output_dir, f"{dataset_name}_irw_format.csv")
        
        try:
            if 'validation' in file_name.lower():
                convert_validation_file(excel_file, output_file)
            else:
                convert_mrmet_file(excel_file, output_file, dataset_name)
        except Exception as e:
            print(f"ERROR processing {file_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    

if __name__ == "__main__":
    import sys
    
    data_dir = "/Users/francesraphael/projects/research/irw/mrmet/MRMET & RMET Open Normative and Validation Data"
    output_dir = "/Users/francesraphael/projects/research/irw/mrmet"
    
    try:
        convert_all_mrmet_files(data_dir, output_dir)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
