"""
IRW processing script
Source: Gyurkovics, Stafford & Levita (2019/2020) - Cognitive Control Across Adolescence
Data: https://osf.io/7vbtr/  (flanker_merge.csv, simon_merge.csv, sart_merge.csv,
                             ppt_info.csv, readme.txt)

Produces four IRW-standard tables:
  cogcontrol_gyurkovics_2019_flanker
  cogcontrol_gyurkovics_2019_simon
  cogcontrol_gyurkovics_2019_sart
  cogcontrol_gyurkovics_2019_mwprobe
"""
import pandas as pd, numpy as np, os

HERE = os.path.dirname(os.path.abspath(__file__))
UP   = os.environ.get('IRW_IN',  HERE)                      # where the source CSVs live
OUT  = os.environ.get('IRW_OUT', os.path.join(HERE, 'output'))
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- person covariates
# ppt_info.csv is authoritative for demographics: the readme warns that the age /
# gender / group values stored in the trial files were typed in by the experimenter
# at the start of each session and contain errors.
GROUPS = {0: 'adult', 1: 'early_adolescent', 2: 'mid_adolescent', 3: 'late_adolescent'}

def person_covariates():
    p = pd.read_csv(f'{UP}/ppt_info.csv', skipinitialspace=True)
    cov = pd.DataFrame({
        'id'                    : p['subid'],
        'cov_age'               : p['age_c'].round(2),        # exact age at testing
        'cov_gender'            : p['sex'].map({0: 'M', 1: 'F'}),
        'cov_agegroup'          : p['grs'].map(GROUPS),
        'cov_puberty'           : p['pub_score'],             # under-18s only
        'cov_iq'                : p['IQ'].astype('Int64'),
        'cov_analysis_include'  : p['filter'].astype('Int64'),    # trait MW, MWQ subscales
        'cov_mwq_spontaneous'   : p['mwSpont'],
        'cov_stai_state'        : p['state_score'],
        'cov_stai_trait'        : p['trait_score'],
        'cov_panas_pos_pre'     : p['panas_pos1'],
        'cov_panas_neg_pre'     : p['panas_neg1'],
        'cov_panas_pos_post'    : p['panas_pos2'],
        'cov_panas_neg_post'    : p['panas_neg2'],
        'cov_analysis_include'  : p['filter'],                # authors' analytic sample
    })
    assert cov['cov_agegroup'].notna().all() and cov['cov_gender'].notna().all()
    assert cov['id'].is_unique
    return cov

COV = person_covariates()

def attach(df):
    out = df.merge(COV, on='id', how='left', validate='many_to_one')
    assert out['cov_agegroup'].notna().all()
    return out

# ---------------------------------------------------------------- trial files
def load(name):
    df = pd.read_csv(f'{UP}/{name}.csv', skipinitialspace=True)
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]          # trailing empty cols
    df = df.drop(columns=[c for c in ['unknown', 'ts_RT', 'diff', 'subage',
                                      'gender', 'group'] if c in df.columns])
    for c in df.columns[df.dtypes == object]:
        df[c] = df[c].str.strip()
    return df.sort_values(['subid', 'block', 'trial']).reset_index(drop=True)

def rt_seconds(ms):
    """ms -> s; RT of exactly 0 means no response was registered -> missing."""
    return (ms.replace(0, np.nan) / 1000).round(4)

# ---------------------------------------------------------------- conflict tasks
def conflict_table(name):
    df = load(name)
    df['prevcong'] = df.groupby(['subid', 'block'])['cong'].shift(1)   # NA on 1st trial
    out = pd.DataFrame({
        'id'             : df['subid'],
        'item'           : 'targ_' + df['targ'].astype(str),
        'resp'           : df['Acc'],                    # 1 = correct
        'rt'             : rt_seconds(df['RT']),
        'itemcov_cong'   : df['cong'],                   # 0 congruent, 1 incongruent
        'trial_block'    : df['block'],
        'trial_num'      : df['trial'],
        'trial_prevcong' : df['prevcong'].astype('Int64'),
        'trial_code'     : df['code'],
        'trial_pausetime': rt_seconds(df['pause_time']),
    })
    # congruency must be invariant within item for it to be an itemcov_
    assert out.groupby('item')['itemcov_cong'].nunique().max() == 1
    return attach(out)

flanker = conflict_table('flanker_merge')
simon   = conflict_table('simon_merge')

# ---------------------------------------------------------------- SART go/no-go
sart_raw = load('sart_merge')
gn = sart_raw[sart_raw['code'] != 3].copy()              # drop thought-probe trials
sart = attach(pd.DataFrame({
    'id'            : gn['subid'],
    'item'          : 'digit_' + gn['targ'].astype(str),
    'resp'          : gn['Acc'],                         # 1 = correct hit / correct withhold
    'rt'            : rt_seconds(gn['RT']),
    'itemcov_nogo'  : (gn['code'] == 2).astype(int),     # digit 3 is the only No-Go stimulus
    'trial_block'   : gn['block'],
    'trial_num'     : gn['trial'],
}))
assert sart.groupby('item')['itemcov_nogo'].nunique().max() == 1

# ---------------------------------------------------------------- MW thought probes
PROBE = {97: 'on_task', 98: 'space_out', 99: 'zone_out', 100: 'tune_out'}
MW    = {'on_task': 0, 'space_out': 0, 'zone_out': 1, 'tune_out': 1}   # "overall MW"
pb = sart_raw[sart_raw['code'] == 3].copy()
pb['report'] = pb['resp'].map(PROBE)
assert pb['report'].notna().all()
pb['probe_i'] = pb.groupby('subid').cumcount() + 1
mw = attach(pd.DataFrame({
    'id'          : pb['subid'],
    'item'        : 'probe_' + pb['probe_i'].astype(str).str.zfill(2),
    'resp'        : pb['report'].map(MW),                # 1 = mind-wandering reported
    'rt'          : rt_seconds(pb['RT']),                # time taken to answer the probe
    'trial_report': pb['report'],
    'trial_block' : pb['block'],
    'trial_num'   : pb['trial'],
}))

# ---------------------------------------------------------------- write + report
tables = {'cogcontrol_gyurkovics_2019_flanker': flanker,
          'cogcontrol_gyurkovics_2019_simon'  : simon,
          'cogcontrol_gyurkovics_2019_sart'   : sart,
          'cogcontrol_gyurkovics_2019_mwprobe': mw}
for name, t in tables.items():
    t.to_csv(f'{OUT}/{name}.csv', index=False)
    print(f'{name}: {len(t):,} rows | {t.id.nunique()} ids | {t.item.nunique()} items '
          f'| mean resp {t.resp.mean():.3f} | rt missing {t.rt.isna().sum()}')