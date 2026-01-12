import pandas as pd
import numpy as np


def convert_to_irw(input_file, output_file):
    df = pd.read_excel(input_file)

    # Items
    phq_cols = [f'PHQ9.{i}' for i in range(1, 10)]
    gad_cols = [f'GAD7.{i}' for i in range(1, 8)]
    item_cols = phq_cols + gad_cols

    # Response table
    responses_df = df[['serial_no', 'time_taken_in_seconds', 'date_time'] + item_cols].copy()

    responses_df['date'] = pd.to_datetime(responses_df['date_time']).dt.tz_localize('Asia/Shanghai').dt.tz_convert('UTC').apply(lambda x: int(x.timestamp()))

    responses_df = responses_df.rename(columns={'serial_no': 'id', 'time_taken_in_seconds': 'rt'})

    irw_responses = responses_df.melt(
        id_vars=['id', 'rt', 'date'],
        value_vars=item_cols,
        var_name='item',
        value_name='resp'
    )

    irw_responses = irw_responses[['id', 'item', 'resp', 'rt', 'date']]

    # Columns to filter out
    items_and_timing = item_cols + ['date_time', 'time_taken_in_seconds']
    redundant_text_cols = [col for col in df.columns if col[0].isdigit() and col[1] == '.']

    cov_cols = [col for col in df.columns if col not in items_and_timing + redundant_text_cols and col != 'serial_no']

    irw_covariates = df[['serial_no'] + cov_cols].copy()
    irw_covariates = irw_covariates.rename(columns={'serial_no': 'id'})
    irw_covariates.columns = [f'cov_{col}' if col != 'id' else col for col in irw_covariates.columns]

    final_dataset = irw_responses.merge(irw_covariates, on='id', how='left')

    final_dataset.to_csv(output_file, index=False)

if __name__ == "__main__":
    
    input_file = 'COVID_mental_health_survey_data.xlsx'
    output_file = 'chinese_college_adolescent.csv'
    
    convert_to_irw(input_file, output_file)