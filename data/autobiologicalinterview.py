"""
process_ai_to_irw.py

Reshapes the raw wide-format Autobiographical Interview (AI) dataset
(Lockrow et al., 2024) into three IRW-standard long tables:

    1. detailcounts   - internal/external detail tallies + wordcount, per
                         life period, per rater
    2. scorerratings  - scorer summary ratings (place/time/perceptual/
                         emotion/AMI/time-integration/episodic-richness),
                         per life period, per rater
    3. selfreport      - participant self-report ratings (vividness,
                         emotional change, significance now/then,
                         rehearsal), per life period

Rationale for the split and column choices (per the IRW data standard):
  - id/item/resp are the required columns for every table.
  - rater is used for the two double-scored tables (detailcounts,
    scorerratings), instead of baking rater-1/rater-2 into the item
    code, per the IRW field for "an identifier associated with the
    rater producing the rating."
  - item names are human-readable (life period + category), not the
    raw opaque variable codes, so they can be matched back to the
    original construct without the codebook.
  - cov_agegroup / cov_gender are person-invariant covariates, prefixed
    per the standard.
  - Rows are dropped (not imputed) where a participant did not complete
    a given life period (younger adults only did 3 of 5 periods).
  - The three tables are kept separate because they are conceptually
    distinct constructs (raw counts vs. scorer Likert ratings vs.
    self-report Likert ratings), per the "split into several tables if
    they have different constructs" guidance.

Usage:
    python process_ai_to_irw.py --input /path/to/aipsychometrics_ai_raw.csv --outdir /path/to/output
"""

import argparse
import pandas as pd

# Life period codes (m1-m5) -> readable labels
PERIOD_MAP = {
    1: 'childhood',
    2: 'teenage',
    3: 'youngadult',
    4: 'middleadult',
    5: 'lastyear',
}

# Raw detail-count category codes -> readable labels
DETAIL_CAT_MAP = {
    'int_ed': 'internal_event',       'ext_ed': 'external_event',
    'int_place': 'internal_place',    'ext_place': 'external_place',
    'int_time': 'internal_time',      'ext_time': 'external_time',
    'int_perc': 'internal_perceptual','ext_perc': 'external_perceptual',
    'int_emo': 'internal_emotion',    'ext_emo': 'external_emotion',
    'ext_sem': 'external_semantic',
    'ext_rep': 'external_repetition',
    'ext_other': 'external_other',
}

# Raw scorer-rating category codes -> readable labels
SCORER_CAT_MAP = {
    'scorer_place': 'scorer_place',
    'scorer_time': 'scorer_time',
    'scorer_perc': 'scorer_perceptual',
    'scorer_emo': 'scorer_emotion',
    'scorer_ami': 'scorer_ami',
    'scorer_ti': 'scorer_timeintegration',
    'scorer_er': 'scorer_episodicrichness',
}

# Raw self-report category codes -> readable labels
SR_CAT_MAP = {
    'sr_vividness': 'selfreport_vividness',
    'sr_emo': 'selfreport_emotionalchange',
    'sr_signow': 'selfreport_significancenow',
    'sr_sigthen': 'selfreport_significancethen',
    'sr_rehearse': 'selfreport_rehearsal',
}

COV_COLS = {'agegroup': 'cov_agegroup', 'gender': 'cov_gender'}


def base_frame(df):
    """id + person-level covariates, replicated for every long row."""
    out = df[['id']].copy()
    for src, dst in COV_COLS.items():
        out[dst] = df[src]
    return out


def build_detailcounts(df):
    rows = []
    for m, period in PERIOD_MAP.items():
        for rater in (1, 2):
            for code, label in DETAIL_CAT_MAP.items():
                col = f'ai_r{rater}_m{m}_{code}_frgp'
                if col not in df.columns:
                    continue
                tmp = base_frame(df)
                tmp['item'] = f'{period}_{label}'
                tmp['resp'] = df[col]
                tmp['rater'] = rater
                rows.append(tmp)
        # wordcount has no rater (it's counted once per memory, not per scorer)
        wc_col = f'ai_m{m}_wordcount_frgp'
        if wc_col in df.columns:
            tmp = base_frame(df)
            tmp['item'] = f'{period}_wordcount'
            tmp['resp'] = df[wc_col]
            tmp['rater'] = pd.NA
            rows.append(tmp)

    out = pd.concat(rows, ignore_index=True).dropna(subset=['resp'])
    return out[['id', 'item', 'resp', 'rater', 'cov_agegroup', 'cov_gender']]


def build_scorerratings(df):
    rows = []
    for m, period in PERIOD_MAP.items():
        for rater in (1, 2):
            for code, label in SCORER_CAT_MAP.items():
                col = f'ai_r{rater}_m{m}_{code}_frgp'
                if col not in df.columns:
                    continue
                tmp = base_frame(df)
                tmp['item'] = f'{period}_{label}'
                tmp['resp'] = df[col]
                tmp['rater'] = rater
                rows.append(tmp)

    out = pd.concat(rows, ignore_index=True).dropna(subset=['resp'])
    return out[['id', 'item', 'resp', 'rater', 'cov_agegroup', 'cov_gender']]


def build_selfreport(df):
    rows = []
    for m, period in PERIOD_MAP.items():
        for code, label in SR_CAT_MAP.items():
            col = f'ai_m{m}_{code}'
            if col not in df.columns:
                continue
            tmp = base_frame(df)
            tmp['item'] = f'{period}_{label}'
            tmp['resp'] = df[col]
            rows.append(tmp)

    out = pd.concat(rows, ignore_index=True).dropna(subset=['resp'])

    # Documented range for self-report items is 1-6; a resp of 0 is an
    # invalid/out-of-range value (data entry error), not a real "zero"
    # score, so it is recoded to missing rather than kept as-is.
    # (Unlike detailcounts/scorerratings, where 0 is a legitimate value
    # and must NOT be touched.)
    n_invalid = (out['resp'] == 0).sum()
    if n_invalid:
        print(f'  -> recoding {n_invalid} out-of-range selfreport value(s) of 0 to NA')
    out.loc[out['resp'] == 0, 'resp'] = pd.NA

    return out[['id', 'item', 'resp', 'cov_agegroup', 'cov_gender']]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to aipsychometrics_ai_raw.csv')
    parser.add_argument('--outdir', required=True, help='Directory to write the 3 output CSVs')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    print(f'Raw shape: {df.shape}')

    detailcounts = build_detailcounts(df)
    scorerratings = build_scorerratings(df)
    selfreport = build_selfreport(df)

    prefix = 'autobiographicalinterview_lockrow_2023'
    out_paths = {
        'detailcounts': f'{args.outdir}/{prefix}_detailcounts.csv',
        'scorerratings': f'{args.outdir}/{prefix}_scorerratings.csv',
        'selfreport': f'{args.outdir}/{prefix}_selfreport.csv',
    }

    detailcounts.to_csv(out_paths['detailcounts'], index=False)
    scorerratings.to_csv(out_paths['scorerratings'], index=False)
    selfreport.to_csv(out_paths['selfreport'], index=False)

    for name, table in [('detailcounts', detailcounts),
                         ('scorerratings', scorerratings),
                         ('selfreport', selfreport)]:
        print(f'{name}: {table.shape[0]} rows, {table["id"].nunique()} ids, '
              f'{table["item"].nunique()} unique items -> {out_paths[name]}')


if __name__ == '__main__':
    main()