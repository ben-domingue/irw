import pyreadstat, pandas as pd, numpy as np

SAV = 'Data_main experiment_13 countries_July 2 2024.sav'
df, meta = pyreadstat.read_sav(SAV, apply_value_formats=False)
df.columns = [c.lower() for c in df.columns]
vl = {k.lower(): v for k, v in meta.variable_value_labels.items()}

# .do lines 16-27: year, ceil(age), decode country
df['cov_year'] = pd.to_datetime(df['recordeddate']).dt.year
df['cov_age']  = np.ceil(df['age'])
df['cov_country'] = df['country'].map(vl['country'])

# .do lines 30-36: rename covariates
df = df.rename(columns={'human_development_index': 'cov_hdi',
                        'national_individualism': 'cov_individualism',
                        'national_powerdistance': 'cov_powerdistance',
                        'gender': 'cov_gender'})
# Stata's `export delimited` writes value LABELS: gender is labelled, so decode it.
# resp is deliberately de-labelled by the .do's `gen resp2 = resp` step -> stays numeric.
df['cov_gender'] = df['cov_gender'].map(vl['gender'])

# .do line 42: clean age; line 47: drop unfinished; line 50: id = _n
df.loc[df['cov_age'].isin([1986,1990,1996,2000,2001,2002,2003,2004]), 'cov_age'] = np.nan
df = df[~((df['finished'] == 0) | df['finished'].isna())].copy()
df['id'] = np.arange(1, len(df) + 1)

# Bookmark #10: Big 5 scale, South Korea
d = df[df['cov_country'] == 'South Korea'].copy()
d = d.rename(columns={'koean_big5_art': 'korean_big5_art'})   # source typo

items = ['korean_big5_conservative','korean_big5_trustworthy','korean_big5_lazy',
         'korean_big5_sociable','korean_big5_faults','korean_big5_nervous',
         'korean_big5_imaginative','korean_big5_thorough','korean_big5_laidback',
         'korean_big5_art']
covs = [c for c in d.columns if c.startswith('cov_')]

long = d.melt(id_vars=['id'] + covs, value_vars=items, var_name='item', value_name='resp')
long = long[['id','item','resp'] + covs].sort_values(['id','item'], kind='mergesort')
long['resp'] = long['resp'].astype('Int64')
long['cov_year'] = long['cov_year'].astype('Int64')
long['cov_age'] = long['cov_age'].astype('Int64')

long.to_csv('pezzuti_2025_coolpeople_main_big5_SouthKorea.csv', index=False)
print('rows', len(long), '| items', long['item'].nunique(), '| ids', long['id'].nunique())
print(long.head(11).to_string(index=False))
