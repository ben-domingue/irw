import pandas as pd
import pyreadstat
import numpy as np
import os
import re

def load_data(input_file):
    """Dynamically load data based on file extension."""
    ext = os.path.splitext(input_file)[-1].lower()
    if ext == '.sav':
        df, meta = pyreadstat.read_sav(input_file, apply_value_formats=False)
    elif ext == '.dta':
        df = pd.read_stata(input_file)
    elif ext == '.csv':
        df = pd.read_csv(input_file)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    return df

def process_to_irw_constructs(input_file, output_dir='irw_processed_tables'):
    print(f"Starting processing for: {input_file}")
    
    try:
        df = load_data(input_file)
        print(f"Successfully loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    # --- 1. Map Core Variables Safely ---
    id_col = next((c for c in ['ResponseId', 'ResponseID', 'Participant ID', 'PID', 'MID'] if c in df.columns), None)
    if id_col:
        df.rename(columns={id_col: 'id'}, inplace=True)

    date_col = next((c for c in ['RecordedDate', 'recorded_date', 'StartDate'] if c in df.columns), None)
    if date_col:
        df.rename(columns={date_col: 'date'}, inplace=True)

    rt_col = next((c for c in ['Duration__in_seconds_', 'Durationinseconds', 'duration_in_seconds', 'totalduration'] if c in df.columns), None)
    if rt_col:
        df.rename(columns={rt_col: 'rt'}, inplace=True)

    cov_map = {
        'Age': 'cov_age', 'age': 'cov_age',
        'Gender': 'cov_gender', 'gender': 'cov_gender',
        'Group': 'cov_group'
    }
    df.rename(columns={k: v for k, v in cov_map.items() if k in df.columns}, inplace=True)

    # --- 1.5 Study-Specific Pre-Mappings ---
    if 'Study 3' in input_file:
        study3_map = {
            'Q3.1_1': 'moral1', 'Q3.3_1': 'moral2', 'Q3.5_1': 'moral3',
            'Q4.1_1': 'moral4', 'Q4.3_1': 'moral5', 'Q4.5_1': 'moral6',
            'Q5.1_1': 'moral7', 'Q5.3_1': 'moral8', 'Q5.5_1': 'moral9',
            'Q212': 'cov_age', 'Q213': 'cov_gender', 'Q206': 'cov_socialclass'
        }
        for i in range(1, 42):
            study3_map[f'Q{i}'] = f'nfc{i}'
            study3_map[f'Q{i}.0'] = f'nfc{i}' 
        df.rename(columns=study3_map, inplace=True)

    if 'Study 4' in input_file:
        study4_map = {
            'Ideology': 'cov_ideology', 'leftright': 'cov_leftright', 'party': 'cov_party',
            'condname': 'cov_condition', 
            'manip': 'cov_manipcheck', 'accuracy': 'cov_accuracycheck',
            
            # Timed Condition
            'Q129': 'moral1_timed', 'Q130': 'moral2_timed', 'Q131': 'moral3_timed',
            'Q132': 'moral4_timed', 'Q133': 'moral5_timed', 'Q134': 'moral6_timed',
            'Q137': 'moral7_timed', 'Q138': 'moral8_timed', 'Q139': 'moral9_timed',
            
            # Control Condition (Corrected & Verified)
            'Q141': 'moral1_ctrl', 'Q142': 'moral2_ctrl', 'Q143': 'moral3_ctrl',
            'Q144': 'moral4_ctrl', 'Q145': 'moral5_ctrl', 'Q146': 'moral6_ctrl',
            'Q3.1': 'moral7_ctrl', 'Q127': 'moral8_ctrl', 'Q128': 'moral9_ctrl'
        }
        df.rename(columns=study4_map, inplace=True)

    if 'Study 5' in input_file:
        study5_map = {
            'political1': 'cov_ideology1', 'political2': 'cov_ideology2', 'political3': 'cov_ideology3',
            'abortion': 'moral_abortion', 'death': 'moral_deathpenalty', 'euth': 'moral_euthanasia',
            'hunt': 'moral_hunting', 'marij': 'moral_marijuana', 'homosex': 'moral_homosexual',
            'gun': 'moral_guncontrol', 'bribes': 'moral_bribes', 'pesticide': 'moral_pesticide',
            'refusecharity': 'moral_charity', 'oldagehomes': 'moral_oldage',
            'dv': 'ban_support'
        }
        for i in range(1, 21):
            study5_map[f'filler{i}'] = f'cov_mathfiller{i}'
        df.rename(columns=study5_map, inplace=True)

    if 'Study 6' in input_file:
        study6_map = {
            'affiliation': 'cov_affiliation', 'politicalavg': 'cov_ideology_avg',
            'political1': 'cov_ideology1', 'political2': 'cov_ideology2', 'political3': 'cov_ideology3',
            'ideoextreme': 'cov_ideoextreme', 'class': 'cov_socialclass', 'edu': 'cov_education',
            'abortion': 'stance_abortion', 'deathpenalty': 'stance_deathpenalty',
            'guncontrol': 'stance_guncontrol', 'weed': 'stance_marijuana',
            'hunting': 'stance_hunting', 'euthanasia': 'stance_euthanasia',
            'ban': 'ban_support', 
            'math': 'cov_mathcheck', 'gibberishchk': 'cov_gibberishcheck',
            'rc1': 'cov_readingcheck1', 'rc2': 'cov_readingcheck2'
        }
        df.rename(columns=study6_map, inplace=True)

    if 'Study 7' in input_file:
        study7_map = {
            'politicalavg': 'cov_ideology_avg',
            'political1': 'cov_ideology1', 'political2': 'cov_ideology2', 'political3': 'cov_ideology3',
            'class': 'cov_socialclass', 'edu': 'cov_education',
            'abortion': 'stance_abortion', 'deathpenalty': 'stance_deathpenalty',
            'guncontrol': 'stance_guncontrol', 'marijuana': 'stance_marijuana',
            'hunting': 'stance_hunting', 'euthanasia': 'stance_euthanasia',
            'ban': 'ban_support', 'gibberish2chk': 'cov_gibberishcheck'
        }
        df.rename(columns=study7_map, inplace=True)

    if 'Study 8' in input_file:
        study8_map = {
            'cond': 'cov_condition', 'condition': 'cov_condition_num', 'filter__': 'cov_filter',
            'ideology': 'cov_ideology_avg', 'polid': 'cov_polid',
            'distance': 'cov_ideology_distance', 'polidxcondition': 'cov_interaction_term',
            'interaction': 'cov_interaction', 'mc': 'cov_check_mc',
            'bans': 'ban_support', 'Ban': 'ban_raw', 
            'Q1_1': 'cov_screener', 'Q2_2': 'stance_1', 'Q108': 'stance_2', 
            'Q2_3': 'stance_3', 'Q2_4': 'stance_4', 'Q2_5': 'stance_5', 
            'Q2_6': 'stance_6', 'Q2_7': 'stance_7',
            'Q5_2_1': 'cov_check_raw1', 'Q5_3_1': 'cov_check_raw2', 
            'Q106_1': 'cov_check_raw3', 'Q107_1': 'cov_check_raw4'
        }
        df.rename(columns=study8_map, inplace=True)
        
    if 'Study 9' in input_file:
        study9_map = {
            'condname': 'cov_condition', 'condnum': 'cov_condnum',
            'excl': 'cov_exclusion_flag', 'filter_$': 'cov_filter',
            'affiliation': 'cov_affiliation', 'democratclick': 'cov_democratclick',
            'republicanclick': 'cov_republicanclick',
            'Q212': 'cov_age', 'Q213': 'cov_gender', 'Q206': 'cov_socialclass',
            'mc1': 'cov_check_mc1', 'mc2': 'cov_check_mc2', 'manichck': 'cov_check_mindset',
            'antihunting': 'petition_support', 'antihuntingav': 'cov_antihunting_avg'
        }
        df.rename(columns=study9_map, inplace=True)

    # --- 1.6 Format Coercion ---
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['date'] = df['date'].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else pd.NA)

    if 'rt' in df.columns:
        df['rt'] = pd.to_numeric(df['rt'], errors='coerce')

    if 'id' not in df.columns:
        df['id'] = (df.index + 1).astype(str)
    else:
        df['id'] = df['id'].astype(str)

    # Prevent ID duplicates in Long-Format experiments
    for long_col in ['issue', 'Issue', 'practice', 'trial', 'Trial']:
        if long_col in df.columns:
            df['id'] = df['id'] + f"_{long_col}" + df[long_col].astype(str)

    # --- 2. Filter Columns ---
    id_vars = ['id'] + [c for c in df.columns if c.startswith('cov_') or c in ['rt', 'date']]
    
    system_vars = [
        'EndDate', 'Status', 'IPAddress', 'Progress', 'Finished', 
        'LocationLatitude', 'LocationLongitude', 'issue', 'Issue', 
        'practice', 'trial', 'Trial', 'Exclusons', 'ipfreq', 'pidfreq', 'midfreq',
        'RecipientLastName', 'RecipientFirstName', 'RecipientEmail', 
        'ExternalReference', 'DistributionChannel', 'UserLanguage', 
        'StartDate', 'RecordedDate', 'PROLIFIC_PID', 'condname'
    ]
    
    # Isolate valid items and actively reject Qualtrics timing/text artifacts
    item_cols = [
        c for c in df.columns 
        if c not in id_vars 
        and c not in system_vars 
        and not any(artifact in c for artifact in ['_Click', '_Submit', '_TEXT', 'FL_'])
    ]

    # --- 3. Melt to Long Format ---
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=item_cols,
        var_name='original_item',
        value_name='resp'
    )

    # --- 4. Clean up the Responses (Text to Numeric) ---
    likert_mapping = {
        'strongly disagree': 1, 'moderately disagree': 2, 'slightly disagree': 3,
        'somewhat disagree': 3, 'neither agree nor disagree': 4, 'neutral': 4,
        'neither': 4, 'slightly agree': 5, 'somewhat agree': 5,
        'moderately agree': 6, 'strongly agree': 7,
        'strongly oppose': 1, 'somewhat oppose': 2, 'oppose': 2,
        'neither support nor oppose': 3, 'somewhat support': 4,
        'support': 4, 'strongly support': 5
    }

    def convert_likert(val):
        if pd.isna(val):
            return val
        if isinstance(val, str):
            clean_val = val.lower().strip()
            if clean_val in likert_mapping:
                return likert_mapping[clean_val]
        return val

    df_long['resp'] = df_long['resp'].apply(convert_likert)
    
    # Force coercion to numeric and safely bypass pandas object memory retention
    df_long['resp'] = pd.to_numeric(df_long['resp'], errors='coerce')
    df_long = df_long.dropna(subset=['resp']).copy()
    
    # Strict numpy array cast to Int64
    float_array = np.array(df_long['resp'].values, dtype=float)
    df_long['resp'] = pd.Series(float_array, index=df_long.index).round().astype('Int64')
    df_long['item'] = df_long['original_item']

    # --- 5. Extract Constructs via Strict Whitelist ---
    # Pure psychometric whitelist only
    valid_prefixes = ['mfq', 'nfc', 'dt', 'pp', 'mr', 'moral', 'stance', 'ban', 'petition']

    def extract_construct(item_name):
        clean_name = item_name.lower()
        for prefix in valid_prefixes:
            if re.match(rf'^{prefix}[_\d\.]', clean_name):
                return prefix.upper()
                
        if clean_name in ['intensity', 'certainty', 'centrality', 'importance', 'harmpercep']:
            return 'ATTITUDE_STRENGTH'
            
        return 'Discard'

    df_long['construct'] = df_long['item'].apply(extract_construct)
    
    # Remove junk columns
    df_long = df_long[df_long['construct'] != 'Discard']
    
    constructs = df_long['construct'].unique()
    print(f"Found {len(constructs)} valid constructs. Generating separate tables...")

    # --- 6. Export to Files ---
    base_cols = ['id', 'item', 'resp']
    cov_cols = [c for c in df_long.columns if c.startswith('cov_') or c in ['rt', 'date']]
    final_cols = base_cols + [c for c in cov_cols if c not in base_cols]
    
    os.makedirs(output_dir, exist_ok=True)

    # Extract Study number for dynamic file naming
    study_match = re.search(r'study\s*(\d+)', input_file, re.IGNORECASE)
    study_id = f"study{study_match.group(1)}" if study_match else "study_unknown"

    for construct in constructs:
        df_construct = df_long[df_long['construct'] == construct].copy()
        
        # Avoid creating tables for empty or nearly empty constructs
        if len(df_construct) < 10:
            continue
            
        df_final = df_construct[final_cols]
        df_final = df_final.drop_duplicates(subset=['id', 'item'])
        
        # Standardized IRW filename
        filename = f"moral_absolutism_goyal_2025_{study_id}_{construct.lower()}.csv"
        output_name = os.path.join(output_dir, filename)
        
        df_final.to_csv(output_name, index=False)
        print(f" -> Saved {output_name} ({len(df_final)} valid responses)")
        
    print(f"Processing complete for {input_file}!\n" + "-"*40 + "\n")

if __name__ == "__main__":

    files_to_process = [
        'raw_data/Study 3 Data.sav',
        'raw_data/Study 4 Data Experimental NFC.sav',
        'raw_data/Study 5 Data Long Format Support for Bans.dta',
        'raw_data/Study 6 Data Long Format .dta',
        'raw_data/Study 7 Data Long Format.dta',
        'raw_data/Study 8 data long format.dta',
        'raw_data/Study 9 Data.sav'
    ]
    
    for file in files_to_process:
        if os.path.exists(file):
            process_to_irw_constructs(file)
        else:
            print(f"File '{file}' not found.")