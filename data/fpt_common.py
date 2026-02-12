import pandas as pd
import os

def load_session_metadata():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_file = os.path.join(script_dir, 'metadata_tables', 'session.csv')
    if os.path.exists(metadata_file):
        df = pd.read_csv(metadata_file)
        if 'session_id' in df.columns:
            df['session_id'] = df['session_id'].astype(str).str.strip()
            df = df.drop_duplicates(subset=['session_id'], keep='first').reset_index(drop=True)
        return df
    return None

def load_aig_version_metadata():
    """Load AIG/anchor version metadata."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    metadata_file = os.path.join(script_dir, 'metadata_tables', 'task_aig_version.csv')
    if os.path.exists(metadata_file):
        df = pd.read_csv(metadata_file)
        task_mapping = {
            'denominator_neglect_version_A': 'denominator_neglect',
            'denominator_neglect_version_B': 'denominator_neglect',
            'time_series': 'time_series',
            'leapfrog': 'leapfrog',
            'impossible_question': 'impossible_question',
            'bayesian_update_easy': 'bayesian_update',
            'bayesian_update_hard': 'bayesian_update',
        }
        df['irw_task_name'] = df['task'].map(task_mapping)
        lookup = {}
        for _, row in df.iterrows():
            if pd.notna(row['irw_task_name']):
                key = (row['session_id'], row['irw_task_name'])
                if key in lookup:
                    if lookup[key] != row['AIG_version']:
                        lookup[key] = f"{lookup[key]},{row['AIG_version']}"
                else:
                    lookup[key] = row['AIG_version']
        return lookup
    return None


def convert_berlin_numeracy(df, session_meta, aig_meta=None):
    df = df.copy()
    df = df.rename(columns={
        'subject_id': 'id', 'item_id': 'item',
        'correct': 'resp', 'response': 'resp_raw'
    })
    df = df.drop(columns=['correct_response'], errors='ignore')
    if session_meta is not None and 'subject_id' in session_meta.columns:
        if 'session_id' in df.columns:
            df = df.merge(session_meta[['session_id', 'wave', 'form', 'completed']],
                         on='session_id', how='left')
            df['cov_session_id'] = df['session_id']
            df = df.drop(columns=['session_id'])
    df['cov_task'] = 'berlin_numeracy'
    cov_cols = [col for col in df.columns if col not in ['id', 'item', 'resp', 'resp_raw', 'wave']]
    rename_dict = {col: f'cov_{col}' for col in cov_cols if not col.startswith('cov_')}
    df = df.rename(columns=rename_dict)
    return df


def convert_trial_based_task(df, session_meta, task_name, item_col='trial', resp_col='response', aig_meta=None):
    import ast
    df = df.copy()
    if 'id' in df.columns:
        df = df.rename(columns={'id': 'item_id_temp'})
        if item_col == 'id':
            item_col = 'item_id_temp'
    if 'session_id' not in df.columns:
        print(f"Warning: Could not find session_id column for {task_name}")
        return None
    if item_col in df.columns:
        def convert_to_string(val):
            if pd.isna(val):
                return 'NA'
            if isinstance(val, list):
                return str(val[0]) if len(val) > 0 else 'NA'
            return str(val)
        df['item'] = df[item_col].apply(convert_to_string)
    elif 'trial_index' in df.columns:
        df['item'] = 'trial_' + df['trial_index'].astype(str)
    else:
        item_cols = [col for col in df.columns if 'item' in col.lower() or 'trial' in col.lower()]
        if item_cols:
            df['item'] = df[item_cols[0]].astype(str)
        else:
            df['item'] = df.index.astype(str)
    if resp_col in df.columns:
        df['resp'] = df[resp_col]
    elif 'correct' in df.columns:
        df['resp'] = df['correct']
    elif 'score' in df.columns:
        df['resp'] = df['score']
    else:
        resp_cols = [col for col in df.columns if 'response' in col.lower() or 'answer' in col.lower()]
        if resp_cols:
            df['resp'] = df[resp_cols[0]]
        else:
            print(f"Warning: Could not find response column for {task_name}")
            return None

    def convert_to_numeric(val):
        if pd.isna(val):
            return pd.NA
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, (list, dict)):
                    return pd.NA
            except Exception:
                pass
            try:
                return float(val)
            except Exception:
                return pd.NA
        return pd.NA

    df['resp'] = df['resp'].apply(convert_to_numeric)
    rows_before = len(df)
    df = df.dropna(subset=['resp'])
    rows_removed = rows_before - len(df)
    if rows_removed > 0 and task_name == 'admc_raw':
        print(f"  Removed {rows_removed} rows with non-numeric responses (lists/dicts)")

    if session_meta is not None:
        original_session_id = df['session_id'].copy()
        sm = session_meta[['session_id', 'subject_id', 'wave']].copy()
        sm['session_id'] = sm['session_id'].astype(str).str.strip()
        sm = sm.drop_duplicates(subset=['session_id'], keep='first')
        session_to_subject = sm.set_index('session_id')['subject_id'].to_dict()
        session_to_wave = sm.set_index('session_id')['wave'].to_dict()
        session_id_stripped = df['session_id'].astype(str).str.strip()
        df['id'] = session_id_stripped.map(session_to_subject)
        df['cov_session_id'] = original_session_id
        df['wave'] = session_id_stripped.map(session_to_wave)
        df = df.drop(columns=['session_id'], errors='ignore')
        unmapped = df['id'].isna()
        if unmapped.any():
            df.loc[unmapped, 'id'] = original_session_id[unmapped].values
    else:
        print(f"Warning: No session metadata available for {task_name}, using session_id as id")
        df['cov_session_id'] = df['session_id'].copy()
        df['id'] = df['session_id']
        df = df.drop(columns=['session_id'], errors='ignore')

    df['cov_task'] = task_name
    if aig_meta is not None:
        df['cov_aig_version'] = df['cov_session_id'].apply(
            lambda sid: aig_meta.get((sid, task_name), None) if pd.notna(sid) else None
        )
    if 'aig_version' in df.columns:
        df = df.drop(columns=['aig_version'], errors='ignore')
    if 'rt' in df.columns:
        df['rt'] = df['rt'] / 1000
    core_cols = ['id', 'item', 'resp', 'rt', 'wave']
    cov_cols = [col for col in df.columns if col not in core_cols and not col.startswith('cov_')]
    df = df.rename(columns={col: f'cov_{col}' for col in cov_cols})
    return df


def convert_scores_dataset(df, session_meta, task_name, id_col='session_id', aig_meta=None):
    df = df.copy()
    if id_col == 'subject_id' and 'subject_id' in df.columns:
        df['id'] = df['subject_id']
    elif id_col == 'session_id' and 'session_id' in df.columns:
        if session_meta is not None:
            sm = session_meta[['session_id', 'subject_id', 'wave']].copy()
            sm['session_id'] = sm['session_id'].astype(str).str.strip()
            sm = sm.drop_duplicates(subset=['session_id'], keep='first')
            session_to_subject = sm.set_index('session_id')['subject_id'].to_dict()
            session_to_wave = sm.set_index('session_id')['wave'].to_dict()
            original_session_id = df['session_id'].copy()
            session_id_stripped = df['session_id'].astype(str).str.strip()
            df['id'] = session_id_stripped.map(session_to_subject)
            df['cov_session_id'] = original_session_id
            df['wave'] = session_id_stripped.map(session_to_wave)
            df = df.drop(columns=['session_id'], errors='ignore')
            unmapped = df['id'].isna()
            if unmapped.any():
                df.loc[unmapped, 'id'] = original_session_id[unmapped].values
        else:
            df['cov_session_id'] = df['session_id'].copy()
            df['id'] = df['session_id']
            df = df.drop(columns=['session_id'], errors='ignore')
    else:
        print(f"Warning: Could not find {id_col} column for {task_name}")
        return None

    exclude_cols = ['id', 'session_id', 'subject_id', 'cov_session_id', 'wave']
    score_cols = [col for col in df.columns
                  if col not in exclude_cols
                  and not any(x in col.lower() for x in ['mean', 'total', 'sum', '_score'])
                  and not col.endswith('_score')
                  and not col.startswith('cov_')]
    CFS_TESTLET_ITEMS = [
        'tri1_abc', 'tri1_ab', 'tri1_bc', 'bin1', 'bin2', 'bin3',
        't1', 't2', 's1', 's2', 'ci1',
    ]
    if task_name == 'coherence_forecasting_scores':
        score_cols = [c for c in CFS_TESTLET_ITEMS if c in df.columns]
    if not score_cols:
        print(f"Warning: Could not find score columns for {task_name}")
        return None
    id_vars = ['id'] + [col for col in df.columns if col not in score_cols and col != 'id']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=score_cols, var_name='item', value_name='resp')
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp'])
    df_long['cov_task'] = task_name
    core_cols = ['id', 'item', 'resp', 'wave']
    cov_cols = [col for col in df_long.columns if col not in core_cols and not col.startswith('cov_')]
    df_long = df_long.rename(columns={col: f'cov_{col}' for col in cov_cols})
    return df_long


ADMC_RF_ITEMS = [
    'rc1_1_vs_rc2_5', 'rc1_2_vs_rc2_4', 'rc1_3_vs_rc2_7', 'rc1_4_vs_rc2_2', 'rc1_5_vs_rc2_6', 'rc1_6_vs_rc2_3', 'rc1_7_vs_rc2_1',
    'a1_1_vs_a2_6', 'a1_2_vs_a2_5', 'a1_3_vs_a2_3', 'a1_4_vs_a2_1', 'a1_5_vs_a2_7', 'a1_6_vs_a2_2', 'a1_7_vs_a2_4'
]
ADMC_DR_ITEMS = [
    'dr1_C', 'dr2_D', 'dr3_C', 'dr4_None', 'dr5_A', 'dr6_E', 'dr7_E', 'dr8_A', 'dr8_C', 'dr9_A', 'dr9_D', 'dr9_E', 'dr10_C', 'dr10_D', 'dr10_E'
]
ADMC_RP_ITEMS = [
    'rp_a1_vs_rp_b1', 'rp_a2_vs_rp_b2', 'rp_a3_vs_rp_b3', 'rp_a4_vs_rp_b4', 'rp_a5_vs_rp_b5', 'rp_a6_vs_rp_b6', 'rp_a7_vs_rp_b7', 'rp_a8_vs_rp_b8', 'rp_a9_vs_rp_b9', 'rp_a10_vs_rp_b10',
    'rp_a3_vs_rp_a6', 'rp_b3_vs_rp_b6', 'rp_a4_vs_rp_a7', 'rp_b4_vs_rp_b7', 'rp_a2_vs_rp_a9', 'rp_b2_vs_rp_b9',
    'rp_a1_plus_rp_a10_equals_1', 'rp_b1_plus_rp_b10_equals_1', 'rp_a5_plus_rp_a8_equals_1', 'rp_b5_plus_rp_b8_equals_1'
]


def convert_admc_scores(df, session_meta, aig_meta=None):
    df = df.copy()
    if 'subject_id' not in df.columns:
        return None
    df['id'] = df['subject_id']
    out = []
    for subscale, item_cols in [('admc_rf', ADMC_RF_ITEMS), ('admc_dr', ADMC_DR_ITEMS), ('admc_rp', ADMC_RP_ITEMS)]:
        item_cols = [c for c in item_cols if c in df.columns]
        if len(item_cols) == 0:
            continue
        df_long = pd.melt(df, id_vars=['id'], value_vars=item_cols, var_name='item', value_name='resp')
        df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
        df_long = df_long.dropna(subset=['resp'])
        df_long['cov_subscale'] = subscale
        out.append(df_long)
    if not out:
        return None
    merged = pd.concat(out, ignore_index=True)
    merged['cov_task'] = 'admc_raw'
    return merged


def convert_item_based_task(df, session_meta, task_name, item_prefix='', use_correct=False, item_list=None, aig_meta=None):
    import ast
    df = df.copy()
    if 'session_id' not in df.columns:
        print(f"Warning: Could not find session_id column for {task_name}")
        return None
    exclude_cols = ['session_id', 'session_restart_id', 'time_elapsed', 'trial_index',
                    'custom_timer_ended_trial', 'rt', 'correct', 'score', 'response']
    if use_correct:
        item_cols = [col for col in df.columns
                     if col not in exclude_cols and not col.startswith('cov_')
                     and 'correct' in col.lower()
                     and not any(x in col.lower() for x in ['mean', 'total', 'sum', '_total'])]
    else:
        item_cols = [col for col in df.columns
                     if col not in exclude_cols and not col.startswith('cov_')
                     and not any(x in col.lower() for x in ['correct', 'mean', 'total', 'sum', '_total'])]
    if item_prefix:
        item_cols = [col for col in item_cols if col.startswith(item_prefix)]
    if item_list is not None:
        item_cols = [col for col in item_cols if col in item_list]
    if not item_cols:
        print(f"Warning: Could not find item columns for {task_name}")
        return None
    id_vars = ['session_id'] + [col for col in df.columns if col not in item_cols and col != 'session_id']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=item_cols, var_name='item', value_name='resp')
    if use_correct:
        df_long['item'] = df_long['item'].str.replace('_correct', '', regex=False)

    def convert_to_numeric(val):
        if pd.isna(val):
            return pd.NA
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, list):
                    return float(parsed[0]) if len(parsed) > 0 else pd.NA
            except Exception:
                pass
            try:
                return float(val)
            except Exception:
                return pd.NA
        return pd.NA

    df_long['resp'] = df_long['resp'].apply(convert_to_numeric)
    df_long = df_long.dropna(subset=['resp'])
    if session_meta is not None:
        sm = session_meta[['session_id', 'subject_id', 'wave']].copy()
        sm['session_id'] = sm['session_id'].astype(str).str.strip()
        sm = sm.drop_duplicates(subset=['session_id'], keep='first')
        session_to_subject = sm.set_index('session_id')['subject_id'].to_dict()
        session_to_wave = sm.set_index('session_id')['wave'].to_dict()
        original_session_id = df_long['session_id'].copy()
        session_id_stripped = df_long['session_id'].astype(str).str.strip()
        df_long['id'] = session_id_stripped.map(session_to_subject)
        df_long['cov_session_id'] = original_session_id
        df_long['wave'] = session_id_stripped.map(session_to_wave)
        df_long = df_long.drop(columns=['session_id'], errors='ignore')
        unmapped = df_long['id'].isna()
        if unmapped.any():
            df_long.loc[unmapped, 'id'] = original_session_id[unmapped].values
    else:
        df_long['cov_session_id'] = df_long['session_id'].copy()
        df_long['id'] = df_long['session_id']
        df_long = df_long.drop(columns=['session_id'], errors='ignore')
    df_long['cov_task'] = task_name
    core_cols = ['id', 'item', 'resp', 'wave']
    cov_cols = [col for col in df_long.columns if col not in core_cols and not col.startswith('cov_')]
    df_long = df_long.rename(columns={col: f'cov_{col}' for col in cov_cols})
    return df_long


def post_process_and_save(df_task, output_dir):
    if df_task is None or len(df_task) == 0:
        return None, 0
    task_name = df_task['cov_task'].iloc[0]
    required_cols = ['id', 'item', 'resp']
    missing_cols = [col for col in required_cols if col not in df_task.columns]
    if missing_cols:
        print(f"\n  Skipping {task_name} - missing required columns: {missing_cols}")
        return None, 0
    df_task = df_task.drop(columns=['cov_task'])
    empty_cols = []
    for col in df_task.columns:
        col_series = df_task[col]
        if isinstance(col_series, pd.DataFrame):
            continue
        na_count = col_series.isna().sum()
        na_count = na_count.iloc[0] if isinstance(na_count, pd.Series) else na_count
        if na_count == len(col_series):
            empty_cols.append(col)
        elif hasattr(col_series, 'dtype') and col_series.dtype == 'object':
            non_null = col_series.dropna()
            if len(non_null) > 0:
                empty_sum = (non_null == '').sum()
                empty_count = empty_sum.iloc[0] if isinstance(empty_sum, pd.Series) else empty_sum
                if empty_count == len(non_null):
                    empty_cols.append(col)
    if empty_cols:
        df_task = df_task.drop(columns=empty_cols)
    if task_name == 'cognitive_reflection' and 'cov_rt' in df_task.columns:
        if 'rt' not in df_task.columns:
            df_task['rt'] = df_task['cov_rt'] / 1000.0
        df_task = df_task.drop(columns=['cov_rt'])
    if task_name == 'cognitive_reflection':
        crt_drop = [c for c in df_task.columns if c in ('cov_session_restart_id', 'cov_trial_index')
                    or (c.startswith('cov_crt_') and c != 'cov_session_id')]
        if crt_drop:
            df_task = df_task.drop(columns=crt_drop)
    drop_cols = [
        'cov_admc_id', 'cov_admc_response', 'cov_completed', 'cov_custom_timer_ended_trial', 'cov_form', 'cov_time_elapsed',
        'cov_response', 'cov_response_slider', 'cov_score', 'cov_correct', 'cov_crt_correct_mean', 'cov_crt', 'cov_rt', 'cov_correct_response'
    ]
    if task_name != 'berlin_numeracy':
        drop_cols.append('resp_raw')
    drop_cols = [c for c in drop_cols if c in df_task.columns]
    if drop_cols:
        df_task = df_task.drop(columns=drop_cols)
    if task_name == 'coherence_forecasting_scores':
        extra_drop = [c for c in df_task.columns if c.startswith('cov_') and c not in ('cov_session_id', 'cov_task')
                      and (c.startswith('cov_time') or c.startswith('cov_space') or c.startswith('cov_confidence_interval')
                           or c.startswith('cov_trinary') or c.startswith('cov_binary') or c == 'cov_score_mean')]
        if extra_drop:
            df_task = df_task.drop(columns=extra_drop)
    if task_name == 'impossible_question':
        iqc_drop = [c for c in df_task.columns if c in (
            'cov_question_type', 'cov_confidence_scaled', 'cov_question_text', 'cov_answer_1', 'cov_answer_2', 'cov_item_id_temp',
            'cov_response_choice', 'cov_session_restart_id', 'cov_trial', 'cov_trial_index', 'cov_correct_answer')]
        if iqc_drop:
            df_task = df_task.drop(columns=iqc_drop)
    if task_name == 'leapfrog':
        lf_drop = [c for c in df_task.columns if c in (
            'cov_block', 'cov_optimal_choice', 'cov_optionA_reward', 'cov_optionB_reward', 'cov_option_selected', 'cov_points_won',
            'cov_session_restart_id', 'cov_trial', 'cov_trial_index', 'cov_trial_type')]
        if lf_drop:
            df_task = df_task.drop(columns=lf_drop)
    if task_name == 'number_series':
        ns_drop = [c for c in df_task.columns if c in ('cov_correct_answer', 'cov_ns_id', 'cov_ns_response', 'cov_session_restart_id', 'cov_trial_index', 'cov_trial_name')]
        if ns_drop:
            df_task = df_task.drop(columns=ns_drop)
    if task_name == 'raven':
        raven_drop = [c for c in df_task.columns if c in ('cov_correct_answer', 'cov_list_id', 'cov_session_restart_id', 'cov_stimulus', 'cov_trial', 'cov_trial_index')]
        if raven_drop:
            df_task = df_task.drop(columns=raven_drop)
    if task_name in ('shipley_vocabulary', 'shipley_abstraction'):
        shipley_drop = [c for c in df_task.columns if c in ('cov_shipley_vocab_total', 'cov_shipley_abstraction_total', 'cov_trial_index')]
        if shipley_drop:
            df_task = df_task.drop(columns=shipley_drop)
    if task_name == 'time_series':
        ts_drop = [c for c in df_task.columns if c in (
            'cov_chart_height', 'cov_displayed_values', 'cov_mse', 'cov_session_restart_id', 'cov_trial', 'cov_trial_index', 'cov_y_axis_values')
            or c.startswith('cov_ground_truth_prediction_') or c.startswith('cov_prediction_') or c.startswith('cov_squared_error_')]
        if ts_drop:
            df_task = df_task.drop(columns=ts_drop)
    if task_name == 'bayesian_update':
        bu_drop = [c for c in df_task.columns if c in (
            'cov_ball_split', 'cov_current_draw', 'cov_left_box_majority_color', 'cov_past_draws', 'cov_right_box_majority_color',
            'cov_selected_box_majority_color', 'cov_session_restart_id', 'cov_trial', 'cov_trial_index', 'cov_unique_trial', 'cov_unique_trial_draw_number')]
        if bu_drop:
            df_task = df_task.drop(columns=bu_drop)
    df_task = df_task.loc[:, ~df_task.columns.duplicated()]
    df_task = df_task.sort_values(['id', 'item']).reset_index(drop=True)
    core_cols = ['id', 'item', 'resp']
    optional_cols = [c for c in ['resp_raw', 'rt', 'wave'] if c in df_task.columns]
    cov_cols = sorted([col for col in df_task.columns if col not in core_cols + optional_cols])
    df_task = df_task[[c for c in core_cols + optional_cols + cov_cols if c in df_task.columns]]
    output_file = os.path.join(output_dir, f'himmelstein-{task_name}-2025.csv')
    df_task.to_csv(output_file, index=False)
    print(f"\n  Saved: {output_file}")
    print(f"    Shape: {df_task.shape}")
    print(f"    Participants: {df_task['id'].nunique()}")
    print(f"    Items: {df_task['item'].nunique()}")
    if empty_cols:
        print(f"    Removed {len(empty_cols)} empty columns")
    return output_file, len(empty_cols)
