#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import zipfile
from pathlib import Path

STUDY_COLUMN_RANGES = {
    1: {
        'vocab': (4, 104),
        'nd': (105, 185),
        'art': (186, 276),
        'gk': (277, 357),
        'rf': (358, 391),
        'bfi': (391, 451),
    },
    2: {
        'vocab': (6, 246),
        'comp': (247, 271),
    },
    3: {
        'lextale': (6, 66),
        'vocab_general': (69, 119),
        'vocab_academic': (120, 170),
        'gk': (171, 236),
        'nd': (237, 317),
        'comp': (318, 354),
        'art': (355, 445),
        'rf': (446, 470),
        'bfi': (470, 530),
    },
    4: {
        'vocab': (7, 207),
        'comp_academic1': (208, 226),
        'comp_academic2': (227, 246),
        'comp': (247, 287),
        'afoqt': (289, 309),
    },
    5: {
        'bfi': (7, 67),
        'comp1': (67, 91),
        'comp2': (91, 133),
        'afoqt': (133, 153),
        'comp4': (154, 204),
        'art': (307, 397),
        'vocab_general': (397, 447),
        'vocab_academic': (447, 497),
        'nd': (497, 577),
        'gk': (577, 642),
    },
}

CONSTRUCT_COMBINE_MAP = {
    'vocab': 'vocab',
    'lextale': 'vocab',
    'vocab_general': 'vocab',
    'vocab_academic': 'vocab',
    'comp': 'comp',
    'comp_academic1': 'comp',
    'comp_academic2': 'comp',
    'comp1': 'comp',
    'comp2': 'comp',
    'comp4': 'comp',
    'afoqt': 'comp',
}

def is_binary_column(series):
    unique_vals = series.dropna().unique()
    return set(unique_vals).issubset({0, 1, 0.0, 1.0})


def is_0_to_5_scale(series):
    unique_vals = series.dropna().unique()
    return all(v in [0, 1, 2, 3, 4, 5, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0] for v in unique_vals)


def is_1_to_5_scale(series):
    unique_vals = series.dropna().unique()
    return all(v in [1, 2, 3, 4, 5, 1.0, 2.0, 3.0, 4.0, 5.0] for v in unique_vals)


def convert_wide_to_long(df, id_col_idx=0, construct_ranges=None, study_num=None):
    if construct_ranges is None:
        construct_ranges = {}
    
    id_col = df.columns[id_col_idx]
    cov_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if col_lower in ['age', 'gender', 'status', 'education', 'country', 'workstatus'] or \
           str(col).startswith('cov_'):
            cov_cols.append(col)

    construct_cols_map = {}
    if construct_ranges:
        for construct, (start_idx, end_idx) in construct_ranges.items():
            if start_idx < len(df.columns) and end_idx < len(df.columns):
                construct_cols = df.columns[start_idx:end_idx+1].tolist()
                construct_cols_map[construct] = construct_cols

    aggregate_patterns = ['total', 'sum_', 'sum ', 'mean', 'totaal', 'tijd', 'time', 'score',
                         'bftime', 'lextale_total', 'wpm', 'wpm_', 'iceagewpm']
    cols_to_drop = []
    for col in df.columns:
        col_str = str(col)
        col_lower = col_str.lower()
        if any(col_lower.startswith(pattern) or pattern in col_lower for pattern in aggregate_patterns):
            cols_to_drop.append(col)
        if col_lower.startswith('sum_') or col_lower.startswith('sum '):
            cols_to_drop.append(col)

    df = df.drop(columns=cols_to_drop, errors='ignore')
    item_cols = [col for col in df.columns if col != id_col and col not in cov_cols]
    construct_cols_set = set()
    if construct_cols_map:
        for cols in construct_cols_map.values():
            construct_cols_set.update(cols)
    
    if study_num in [2, 3, 4, 5]:
        valid_items = []
        for col in item_cols:
            is_construct_col = col in construct_cols_set
            if study_num == 5:
                if is_binary_column(df[col]) or is_0_to_5_scale(df[col]) or is_1_to_5_scale(df[col]):
                    valid_items.append(col)
            elif study_num == 3:
                if is_binary_column(df[col]) or is_1_to_5_scale(df[col]):
                    valid_items.append(col)
            else:
                if is_binary_column(df[col]):
                    valid_items.append(col)
        item_cols = valid_items

    long_df = df.melt(
        id_vars=[id_col] + cov_cols,
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )
    long_df = long_df.rename(columns={id_col: 'id'})

    if construct_cols_map:
        long_df['construct'] = None
        for construct, construct_cols in construct_cols_map.items():
            valid_construct_cols = [col for col in construct_cols if col in item_cols]
            if valid_construct_cols:
                mask = long_df['item'].isin(valid_construct_cols)
                long_df.loc[mask, 'construct'] = construct
        long_df = long_df[long_df['construct'].notna()]

    for col in long_df.columns:
        if col not in ['id', 'item', 'resp', 'construct'] and not col.startswith('cov_'):
            col_lower = str(col).lower()
            if col_lower in ['age', 'gender', 'status', 'education', 'country', 'workstatus']:
                long_df = long_df.rename(columns={col: f'cov_{col_lower}'})
    long_df = long_df.dropna(subset=['resp'])
    col_order = ['id', 'item', 'resp'] + [col for col in long_df.columns
                                          if col not in ['id', 'item', 'resp']]
    long_df = long_df[col_order]
    
    return long_df


def process_study_from_excel(excel_file, output_dir, study_num):
    print(f"Processing Study {study_num}: {excel_file}")
    df = pd.read_excel(excel_file)
    construct_ranges = STUDY_COLUMN_RANGES.get(study_num, {})
    long_df = convert_wide_to_long(df, construct_ranges=construct_ranges, study_num=study_num)
    long_df.columns = [col.lower() for col in long_df.columns]

    if study_num == 1:
        meta_items = ['period', 'included']
        long_df = long_df[~long_df['item'].str.lower().isin(meta_items)]
    elif study_num == 4:
        cols_to_drop = [col for col in long_df.columns if 'gender' in col.lower() and 'other' in col.lower()]
        long_df = long_df.drop(columns=cols_to_drop, errors='ignore')

    aggregated_patterns = ['total', 'tijd', 'time', 'mean', 'sum', 'score', 'bftime',
                          'sum_', 'lextale_total', 'wpm', 'wpm_', 'iceagewpm']
    long_df = long_df[~long_df['item'].str.lower().isin([p.lower() for p in aggregated_patterns])]

    if 'construct' in long_df.columns:
        constructs = {}
        for construct in long_df['construct'].unique():
            construct_df = long_df[long_df['construct'] == construct].copy()
            construct_df = construct_df.drop(columns=['construct'])
            constructs[construct] = construct_df
    else:
        constructs = {'other': long_df}

    output_files = []
    for construct, construct_df in constructs.items():
        construct_df['cov_study'] = study_num
        filename = f"vermeiren_study_{study_num}_2022_{construct}.csv"
        filepath = os.path.join(output_dir, filename)
        construct_df.to_csv(filepath, index=False)
        output_files.append((filepath, construct, construct_df))
        print(f"  Created: {filename} ({len(construct_df)} rows, {construct_df['item'].nunique()} unique items)")
    
    return output_files


def combine_constructs_across_studies(all_study_files, output_dir):
    constructs_dict = {}
    for filepath, construct, df in all_study_files:
        out_name = CONSTRUCT_COMBINE_MAP.get(construct, construct)
        if out_name not in constructs_dict:
            constructs_dict[out_name] = []
        constructs_dict[out_name].append(df)

    combined_files = []
    for out_name, dfs in constructs_dict.items():
        if len(dfs) > 1:
            combined_df = pd.concat(dfs, ignore_index=True)
            cols = [c for c in combined_df.columns if c != 'cov_study']
            cov_idx = next((i for i, c in enumerate(cols) if c.startswith('cov_')), len(cols))
            if 'cov_study' in combined_df.columns:
                cols.insert(cov_idx, 'cov_study')
            combined_df = combined_df[cols]

            filename = f"vermeiren_2022_{out_name}.csv"
            filepath = os.path.join(output_dir, filename)
            combined_df.to_csv(filepath, index=False)
            combined_files.append(filepath)
            n_studies = combined_df['cov_study'].nunique()
            print(f"  Combined: {filename} ({len(combined_df)} rows, {combined_df['item'].nunique()} unique items, {n_studies} studies)")
        else:
            df = dfs[0]
            cols = df.columns.tolist()
            if 'cov_study' in cols:
                cols = [c for c in cols if c != 'cov_study']
                cov_idx = next((i for i, c in enumerate(cols) if c.startswith('cov_')), len(cols))
                cols.insert(cov_idx, 'cov_study')
                df = df[cols]
            filename = f"vermeiren_2022_{out_name}.csv"
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False)
            combined_files.append(filepath)
            print(f"  Created: {filename} ({len(df)} rows, {df['item'].nunique()} unique items)")
    return combined_files


def main():
    base_dir = Path(__file__).parent
    vocab_dir = base_dir / 'vocab'
    output_dir = base_dir / 'vermeiren_vocab_study_irw'
    output_dir.mkdir(exist_ok=True)

    nested_output_dir = output_dir / output_dir.name
    if nested_output_dir.exists() and nested_output_dir.is_dir():
        import shutil
        try:
            shutil.rmtree(nested_output_dir)
        except OSError:
            pass
    for old_file in output_dir.glob("vermeiren_*.csv"):
        try:
            old_file.unlink()
        except OSError:
            pass
    for old_zip in output_dir.glob("*.zip"):
        try:
            old_zip.unlink()
        except OSError:
            pass

    study_files = {
        1: vocab_dir / 'Student vocabulary test study 1' / 'Data Study 1 for R analysis.xlsx',
        2: vocab_dir / 'Student vocabulary test study 2' / 'Student_vocabulary_test_study2.xlsx',
        3: vocab_dir / 'Student vocabulary test study 3' / 'student_vocabulary_test_study3.xlsx',
        4: vocab_dir / 'student vocabulary test study 4' / 'student vocabulary test study 4.xlsx',
        5: vocab_dir / 'Student vocabulary test study 5' / 'student_vocabulary_test_study5.xlsx',
    }
    all_study_files = []

    for study_num, excel_path in study_files.items():
        if not excel_path.exists():
            print(f"Warning: {excel_path} not found, skipping Study {study_num}")
            continue
        
        try:
            output_files = process_study_from_excel(str(excel_path), str(output_dir), study_num)
            all_study_files.extend(output_files)
        except Exception as e:
            print(f"Error processing Study {study_num}: {e}")
            import traceback
            traceback.print_exc()

    print("\nCombining constructs across studies...")
    combined_files = combine_constructs_across_studies(all_study_files, str(output_dir))

    for filepath, construct, df in all_study_files:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError:
            pass

    all_output_files = list(combined_files)
    if all_output_files:
        zip_path = os.path.join(str(output_dir), 'vermeiren_vocab_study_irw.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in all_output_files:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
        print(f"\nCreated zip file: {zip_path} ({len(all_output_files)} combined files)")
    
    print("\nConversion complete!")


if __name__ == '__main__':
    main()
