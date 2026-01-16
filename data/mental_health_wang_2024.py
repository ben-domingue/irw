import pandas as pd
import numpy as np
import re
from pathlib import Path


def convert_to_irw(input_file, output_file):
    df = pd.read_excel(input_file)

    # Items
    phq_cols = [f'PHQ9.{i}' for i in range(1, 10)]
    gad_cols = [f'GAD7.{i}' for i in range(1, 8)]
    item_cols = phq_cols + gad_cols

    # Response table
    responses_df = df[['serial_no', 'time_taken_in_seconds', 'date_time'] + item_cols].copy()

    # parse as UTC 
    _ts = pd.to_datetime(responses_df['date_time'], utc=True, errors='coerce')
    responses_df['date'] = ((_ts.astype('int64') // 10**9).where(_ts.notna())).astype('Int64')

    responses_df = responses_df.rename(columns={'serial_no': 'id', 'time_taken_in_seconds': 'rt'})

    # create separate tables
    irw_responses_phq = responses_df.melt(
        id_vars=['id', 'rt', 'date'],
        value_vars=phq_cols,
        var_name='item',
        value_name='resp'
    )
    irw_responses_phq = irw_responses_phq[['id', 'item', 'resp', 'rt', 'date']]

    irw_responses_gad = responses_df.melt(
        id_vars=['id', 'rt', 'date'],
        value_vars=gad_cols,
        var_name='item',
        value_name='resp'
    )
    irw_responses_gad = irw_responses_gad[['id', 'item', 'resp', 'rt', 'date']]

    items_and_timing = item_cols + ['date_time', 'time_taken_in_seconds']
    _leading_num_dot = re.compile(r'^\s*\d+\.\s*')
    redundant_text_cols = [col for col in df.columns if isinstance(col, str) and _leading_num_dot.match(col)]

    cov_cols = [col for col in df.columns if col not in items_and_timing + redundant_text_cols and col != 'serial_no']

    irw_covariates = df[['serial_no'] + cov_cols].copy()
    irw_covariates = irw_covariates.rename(columns={'serial_no': 'id'})
    irw_covariates.columns = [f'cov_{col}' if col != 'id' else col for col in irw_covariates.columns]

    base = Path(output_file)
    phq_out = base.with_name(base.stem + '_phq' + base.suffix)
    gad_out = base.with_name(base.stem + '_gad' + base.suffix)

    final_phq = irw_responses_phq.merge(irw_covariates, on='id', how='left')
    final_gad = irw_responses_gad.merge(irw_covariates, on='id', how='left')

    final_phq.to_csv(phq_out, index=False)
    final_gad.to_csv(gad_out, index=False)
    
    print(f"Done processing the data.")


if __name__ == "__main__":
    input_file = 'COVID_mental_health_survey_data.xlsx'
    output_file = 'mental_health_wang_2024.csv'

    convert_to_irw(input_file, output_file)